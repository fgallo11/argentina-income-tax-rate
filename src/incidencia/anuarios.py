"""Lectura de cuadros de los anuarios de estadísticas tributarias de ARCA (ex AFIP).

Los anuarios vienen en tres formatos según el año de publicación: planillas .xls dentro
de un instalador (2003-2008), páginas .htm exportadas de Excel (2009-2014) y planillas
.xls sueltas (2015 en adelante). El anuario del año N informa el año fiscal N-1.
"""
from __future__ import annotations

import html
import re
from html.parser import HTMLParser
from pathlib import Path

import xlrd

from .config import RAW

RAIZ = RAW / "anuarios_arca"
_NOMBRE = re.compile(r"^\d+(\.\d+)+(_\d+)?$")


class _Tabla(HTMLParser):
    def __init__(self):
        super().__init__()
        self.filas, self._fila, self._celda, self._span = [], None, None, 1

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self._fila = []
        elif tag in ("td", "th") and self._fila is not None:
            self._celda = []
            self._span = int(dict(attrs).get("colspan", 1) or 1)

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self._celda is not None and self._fila is not None:
            self._fila.append(" ".join("".join(self._celda).split()))
            self._fila.extend([""] * (self._span - 1))
            self._celda = None
        elif tag == "tr" and self._fila is not None:
            self.filas.append(self._fila)
            self._fila = None

    def handle_data(self, data):
        if self._celda is not None:
            self._celda.append(data)


def _numero(v):
    """Convierte una celda a float si es un número (formato 1.234,5 en los .htm)."""
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip()
    if re.fullmatch(r"-?[\d.]+(,\d+)?", s) and any(ch.isdigit() for ch in s):
        return float(s.replace(".", "").replace(",", "."))
    return None


def cuadros(anuario: int) -> dict[str, Path]:
    """Mapa {número de cuadro: archivo} de un anuario."""
    out = {}
    for f in (RAIZ / str(anuario)).rglob("*"):
        suf = f.suffix.lower()
        if suf == ".xls" and _NOMBRE.match(f.stem):
            out[f.stem] = f
        elif suf == ".htm" and f.name == "sheet001.htm" and f.parent.name.endswith("_archivos"):
            n = f.parent.name[: -len("_archivos")]
            if _NOMBRE.match(n):
                out[n] = f
    return out


def leer(f: Path) -> list[list]:
    """Filas del cuadro como listas de celdas (texto o número)."""
    if f.suffix.lower() == ".xls":
        wb = xlrd.open_workbook(f)
        sh = wb.sheet_by_index(0)
        filas = [[sh.cell_value(r, c) for c in range(sh.ncols)] for r in range(sh.nrows)]
        # algunos cuadros anchos siguen en una segunda hoja ("2.2.2.1.4. (2)"), con las
        # mismas filas: sus columnas de valores se agregan a la derecha
        for extra in wb.sheets()[1:]:
            if extra.name.startswith(sh.name.strip()) and extra.nrows == sh.nrows:
                for r in range(sh.nrows):
                    filas[r] += [extra.cell_value(r, c) for c in range(3, extra.ncols)]
        return filas
    p = _Tabla()
    p.feed(html.unescape(f.read_bytes().decode("latin-1", "ignore")))
    return p.filas


def titulo(filas: list[list], n: int = 9) -> str:
    t = [" ".join(str(c).split()) for fila in filas[:n] for c in fila[:4] if isinstance(c, str) and len(c.strip()) > 3]
    return " / ".join(t)


def por_tramo(filas: list[list]) -> tuple[list[str], list[list[float]], float]:
    """Extrae el bloque de valores por tramo de un cuadro.

    Devuelve (encabezados de cada columna de valores, filas [desde, hasta, v1, v2...],
    factor de unidad en pesos). La primera fila devuelta es el TOTAL (desde = hasta = nan).
    """
    cab = " ".join(str(c) for fila in filas[:12] for c in fila).lower()
    unidad = 1e6 if "millones de pesos" in cab else 1e3 if "miles de pesos" in cab else 1.0
    i_tot, b = next((i, j) for i, fila in enumerate(filas) for j, c in enumerate(fila[:3])
                    if str(c).strip().upper() == "TOTAL")               # b: columna de la etiqueta
    cols = [j for j, v in enumerate(filas[i_tot]) if j > b and _numero(v) is not None]
    enc = []
    for j in cols:
        partes = [str(filas[i][j]).strip() for i in range(max(0, i_tot - 8), i_tot)
                  if j < len(filas[i]) and isinstance(filas[i][j], str) and filas[i][j].strip()]
        enc.append(" ".join(" ".join(partes).split()))
    # los encabezados combinados sólo figuran en la primera columna del grupo: se arrastran
    out = [[float("nan"), float("nan")] + [_numero(filas[i_tot][j]) for j in cols]]
    for fila in filas[i_tot + 1:]:
        if any(isinstance(c, str) and "structura porcentual" in c for c in fila):
            break
        desde = _numero(fila[b]) if len(fila) > b else None
        if desde is None:
            continue
        hasta = _numero(fila[b + 1]) if len(fila) > b + 1 else None
        vals = [(_numero(fila[j]) or 0.0) if j < len(fila) else 0.0 for j in cols]
        out.append([desde, hasta if hasta is not None else float("inf")] + vals)
    return enc, out, unidad


_GENERICOS = re.compile(r"^(casos|importe|más de|mas de|hasta|\(pesos\)|tramo de ingresos.*|presentaciones con.*|\d+(\.\d+)+\.?)$", re.I)


def conceptos_por_columna(filas: list[list]) -> tuple[int, int, list[tuple[int, str, bool]]]:
    """Encabezados de concepto de un cuadro por tramo.

    Devuelve (fila del TOTAL, columna de la etiqueta de tramo, [(columna, concepto, es_par)]).
    Se toma la fila de encabezado con más conceptos. Un concepto ocupa un par de columnas
    (casos, importe) si el siguiente está dos columnas más allá, y una sola si está a una.
    En los .htm las etiquetas quedan corridas respecto de los datos; el corrimiento se
    resuelve aparte (ver `importes`).
    """
    i_tot, b = next((i, j) for i, fila in enumerate(filas) for j, c in enumerate(fila[:3])
                    if str(c).strip().upper() == "TOTAL" and any(_numero(v) is not None for v in fila[j + 1:]))
    i_casos = max(i for i in range(i_tot) if any(str(c).strip().lower() == "casos" for c in filas[i]))
    mejor = []
    for i in range(max(0, i_casos - 4), i_casos):
        et = [(j, " ".join(str(c).split())) for j, c in enumerate(filas[i])
              if isinstance(c, str) and len(c.strip()) > 2 and not _GENERICOS.match(" ".join(c.split()))]
        if len(et) > len(mejor):
            mejor = et
    out = []
    for k, (j, t) in enumerate(mejor):
        sig = mejor[k + 1][0] if k + 1 < len(mejor) else j + 2
        out.append((j, t.upper(), sig - j >= 2))
    return i_tot, b, out


def importes(filas: list[list], identidad, con_casos: bool = False):
    """Importe por tramo de cada concepto, con el corrimiento de columnas que cumple `identidad`.

    `identidad(tot)` recibe {concepto: importe de la fila TOTAL} (conceptos repetidos se
    numeran: 'TOTAL', 'TOTAL#2') y devuelve (a, b) que deben coincidir. Devuelve
    ({concepto: [TOTAL, tramo1, ...]}, desde por fila, unidad en pesos).
    """
    cab = " ".join(str(c) for fila in filas[:12] for c in fila).lower()
    unidad = 1e6 if "millones de pesos" in cab else 1e3 if "miles de pesos" in cab else 1.0
    i_tot, b, cc = conceptos_por_columna(filas)
    datos = [filas[i_tot]]
    for fila in filas[i_tot + 1:]:
        if any(isinstance(c, str) and "structura porcentual" in c for c in fila):
            break
        if len(fila) > b and _numero(fila[b]) is not None:
            datos.append(fila)
    desde = [float("nan")] + [_numero(f[b]) for f in datos[1:]]
    nombres, vistos = [], {}
    for _, t, _ in cc:
        vistos[t] = vistos.get(t, 0) + 1
        nombres.append(t if vistos[t] == 1 else f"{t}#{vistos[t]}")
    val = lambda f, j: (_numero(f[j]) or 0.0) if 0 <= j < len(f) else 0.0  # noqa: E731
    for d in (0, 1, 2, 3, 4, 5, 6, -1, -2):
        cols = {n: j + d + (1 if par else 0) for n, (j, _, par) in zip(nombres, cc)}
        tot = {n: val(datos[0], j) for n, j in cols.items()}
        try:
            x, y = identidad(tot)
        except (KeyError, StopIteration, ValueError):
            continue
        if y > 0 and abs(x / y - 1) < 0.02:
            imp = {n: [val(f, j) * unidad for f in datos] for n, j in cols.items()}
            if con_casos:
                cas = {n: [val(f, j - 1) for f in datos] for n, (j0, _, par) in zip(nombres, cc)
                       for j in [cols[n]] if par}
                return imp, cas, desde, unidad
            return imp, desde, unidad
    raise ValueError("ningún corrimiento cumple la identidad contable del cuadro")


def buscar(tot: dict, patron: str, todos: bool = False):
    """Concepto(s) cuyo nombre cumple la expresión regular."""
    hall = [n for n in tot if re.search(patron, n, re.I)]
    if not hall:
        raise KeyError(patron)
    return hall if todos else hall[0]
