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
        sh = xlrd.open_workbook(f).sheet_by_index(0)
        return [[sh.cell_value(r, c) for c in range(sh.ncols)] for r in range(sh.nrows)]
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
