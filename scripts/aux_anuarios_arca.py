#!/usr/bin/env python
"""Extrae de los anuarios de ARCA las declaraciones juradas de Ganancias de personas
humanas por tramo de ingresos gravados (presentaciones con ingresos gravados), años fiscales 2002-2024.

Salida: data/processed/ddjj_ganancias_tramos.csv, una fila por (año fiscal, tramo), en
pesos corrientes:
  casos, ingresos_gravados (brutos), gnsi (ganancia neta sujeta a impuesto),
  impuesto (determinado), resultado_neto (beneficio - quebranto, antes de
  deducciones generales y personales), exentos (ganancias e ingresos exentos o no
  alcanzados declarados), exentos_ventas (la parte que es resultado por venta de bienes
  o moneda extranjera), bienes y patrimonio_neto al cierre; y, para reemplazar supuestos en
  la estimación del 1% por declaraciones juradas:
  cuarta_bruta y cuarta_gastos (4ta categoría: trabajo personal, incluye jubilaciones,
  honorarios y directores), aportes_deducidos (aportes obligatorios a jubilación, obra
  social, cajas provinciales y complementarias y autónomos, deducidos como deducciones
  generales) y monto_consumido (el consumo que surge de la justificación patrimonial).
Cada cuadro se ubica por su título, no por su número, y se controla contra su fila TOTAL.
En los cuadros de composición las columnas se ubican por una identidad contable (las
categorías suman el subtotal; los conceptos suman el total), porque en los .htm de
2009-2014 los encabezados quedan corridos respecto de los datos.
"""
import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from incidencia.anuarios import buscar, cuadros, importes, leer, por_tramo, titulo  # noqa: E402
from incidencia.config import PROCESSED  # noqa: E402


def rol(t: str) -> str | None:
    t = t.lower().replace(" / ", " ")
    if "tramo de ingresos gravados" not in t:
        return None
    if "ingresos gravados, ganancia neta sujeta a impuesto e impuesto determinado" in t:
        return "resumen"
    if "resultado neto total" in t:
        return "neto"
    if "patrimonio neto del per" in t and "corriente" in t:
        return "patrimonio"
    if "exentos" in t or "variaciones patrimoniales por tramo" in t:
        return "exentos"
    if "categor" in t and "ingresos gravados de" in t:
        return "categorias"
    if "gastos y deducciones de" in t and "categor" in t:
        return "gastos_categorias"
    if "deducciones generales por tramo" in t:
        return "deducciones"
    if "justificaci" in t and "erogaciones" in t:
        return "justificacion"
    return None


CATEGORIA = r"^\s*[1-4](RA|DA|TA)\.?\s*CATEGOR"
CUARTA = r"^\s*4TA\.?\s*CATEGOR"
APORTES = (r"OBRA SOCIAL|^(APORTES OBLIGAT\. A )?FONDOS DE JUBILACIONES|CAJAS PROVINCIALES|"
           r"CAJAS COMPLEMENTARIAS|FONDOS COMPENSADORES|TRABAJADORES AUT")


def id_categorias(tot):
    """Las cuatro categorías suman el subtotal de 1ra. a 4ta."""
    sub = [n for n in tot if not n.startswith("TOTAL")
           and ("1RA., 2DA" in n or n.startswith("INGRESOS GRAVADOS") or n.startswith("GASTOS Y DEDUCCIONES"))]
    return sum(tot[c] for c in buscar(tot, CATEGORIA, True)), tot[sub[-1]]


def id_deducciones(tot):
    """Los conceptos suman el total de deducciones generales."""
    t = buscar(tot, r"^TOTAL$")
    partes = [n for n in tot if n != t and not n.startswith(("DEDUCCIONES GENERALES", "TOTAL"))]
    return sum(tot[p] for p in partes), tot[t]


def id_justificacion(tot):
    """Los conceptos que no justifican erogaciones (consumo y otros) suman su total."""
    ns = list(tot)
    t = [n for n in ns if n.startswith("TOTAL")][-1]
    return sum(tot[p] for p in ns[ns.index(t) + 1:]), tot[t]


def id_exentos(tot):
    """El primer concepto es el total de ganancias e ingresos exentos."""
    ns = list(tot)
    return sum(tot[n] for n in ns[1:]), tot[ns[0]]


def composicion(hallados: dict, n_tramos: int) -> pd.DataFrame:
    """4ta categoría bruta y gastos, aportes deducidos y monto consumido, por tramo (fila 0 = TOTAL)."""
    out = {}
    v, _, _ = importes(leer(hallados["categorias"]), id_categorias)
    out["cuarta_bruta"] = v[buscar(v, CUARTA)]
    v, _, _ = importes(leer(hallados["gastos_categorias"]), id_categorias)
    out["cuarta_gastos"] = v[buscar(v, CUARTA)]
    v, _, _ = importes(leer(hallados["deducciones"]), id_deducciones)
    out["aportes_deducidos"] = [sum(x) for x in zip(*(v[n] for n in buscar(v, APORTES, True)))]
    v, _, _ = importes(leer(hallados["justificacion"]), id_justificacion)
    out["monto_consumido"] = v[buscar(v, r"MONTO CONSUMIDO")]
    for k, x in out.items():
        assert len(x) == n_tramos, (k, len(x), n_tramos)
    return pd.DataFrame(out)


def tabla(f) -> tuple[list[str], pd.DataFrame, float]:
    enc, filas, u = por_tramo(leer(f))
    return enc, pd.DataFrame(filas, columns=["desde", "hasta"] + [f"v{i}" for i in range(len(enc))]), u


def conceptos(enc: list[str]) -> list[str]:
    """Nombres de concepto en el orden en que aparecen (sin 'Casos', 'Importe' ni el número
    de cuadro). En los .htm el texto del encabezado queda corrido de columna, pero el orden
    se conserva: el concepto k ocupa el par de columnas (casos, importe) k-ésimo."""
    out = []
    for e in enc:
        e = re.sub(r"\b(Indice|Casos|Importe)\b|\d+(\.\d+)+\.?", " ", e, flags=re.I)
        e = " ".join(e.split())
        if e:
            out.append(e.upper())
    return out


def extraer(anuario: int) -> pd.DataFrame:
    cs = cuadros(anuario)
    hallados = {}
    for k in sorted(cs, key=lambda s: [int(x) for x in s.replace("_", ".").split(".")]):
        if not k.startswith("2.2.2.1."):
            continue
        filas = leer(cs[k])
        r = rol(titulo(filas))
        if r and r not in hallados:
            hallados[r] = cs[k]
        # el cuadro de justificación patrimonial puede tener también el rol "exentos"
        cab = " ".join(str(c) for f in filas[:14] for c in f).upper()
        if "justificacion" not in hallados and "MONTO CONSUMIDO" in cab:
            hallados["justificacion"] = cs[k]
        # en los .htm el título del cuadro de exentos no siempre se lee: se lo reconoce por sus conceptos
        if "exentos" not in hallados and "PREMIOS, SORTEOS" in " ".join(str(c) for f in filas[:16] for c in f).upper():
            hallados["exentos"] = cs[k]
    falta = {"resumen", "neto", "patrimonio", "categorias", "gastos_categorias",
             "deducciones", "justificacion"} - set(hallados)
    if falta:
        raise RuntimeError(f"anuario {anuario}: no se encontró {falta}")

    # resumen: casos, ingresos gravados, casos con GNSI, GNSI, impuesto determinado
    enc, t, u = tabla(hallados["resumen"])
    out = t[["desde", "hasta"]].copy()
    out["casos"] = t["v0"]
    out["ingresos_gravados"], out["gnsi"], out["impuesto"] = t["v1"] * u, t["v3"] * u, t["v4"] * u
    tot = out.iloc[0]
    assert t["v2"].iloc[0] <= tot.casos and 0.05 < tot.impuesto / tot.gnsi < 0.36 and tot.gnsi < tot.ingresos_gravados, anuario

    enc, t, u = tabla(hallados["neto"])            # presentaciones, (casos, importe) beneficio, quebranto
    assert len(t) == len(out), (anuario, "neto", len(t), len(out))
    hay_quebranto = any("QUEBRANTO" in c for c in conceptos(enc)) and "v4" in t
    out["resultado_neto"] = (t["v2"] - (t["v4"] if hay_quebranto else 0.0)) * u

    enc, t, u = tabla(hallados["patrimonio"])      # presentaciones, bienes, deudas, patrimonio neto
    assert len(t) == len(out), (anuario, "patrimonio")
    out["bienes"], out["patrimonio_neto"] = t["v2"] * u, t["v6"] * u

    out["exentos"] = float("nan")
    out["exentos_ventas"] = float("nan")
    if "exentos" in hallados:
        enc, t, u = tabla(hallados["exentos"])     # presentaciones, total, y un par por concepto
        cc = conceptos(enc)
        if len(t) == len(out) and len(enc) == 2 * len(cc) - 1 and "EXENT" in cc[1]:
            out["exentos"] = t["v2"] * u
            ventas = [f"v{2 * k}" for k, n in enumerate(cc) if "VENTA" in n or "VTA" in n]
            out["exentos_ventas"] = t[ventas].sum(axis=1) * u
    if out["exentos"].isna().all():
        # .htm con encabezados corridos: se ubican las columnas por identidad contable
        try:
            v, _, _ = importes(leer(hallados["exentos"]), id_exentos)
            ns = list(v)
            out["exentos"] = v[ns[0]]
            out["exentos_ventas"] = [sum(x) for x in zip(*(v[n] for n in ns[1:] if "VENT" in n or "VTA" in n))]
        except (KeyError, ValueError):
            # sin cuadro de exentos legible: el mismo concepto en la justificación patrimonial
            v, _, _ = importes(leer(hallados["justificacion"]), id_justificacion)
            out["exentos"] = v[buscar(v, r"EXENT")]
    comp = composicion(hallados, len(out))
    for c in comp:
        out[c] = comp[c].values
    out.insert(0, "anio_fiscal", anuario - 1)
    out.insert(1, "es_total", out.desde.isna())
    return out


if __name__ == "__main__":
    todo = pd.concat([extraer(a) for a in range(2003, 2026)], ignore_index=True)
    # control: la suma de tramos reproduce la fila TOTAL
    cols = ["casos", "gnsi", "impuesto", "resultado_neto", "patrimonio_neto",
            "cuarta_bruta", "cuarta_gastos", "aportes_deducidos", "monto_consumido"]
    s = todo[~todo.es_total].groupby("anio_fiscal")[cols].sum()
    tot = todo[todo.es_total].set_index("anio_fiscal")[cols]
    dif = (s / tot - 1).abs().max()
    print("desvío máximo suma de tramos vs TOTAL:", dif.round(5).to_dict())
    assert (dif < 0.002).all()
    todo.to_csv(PROCESSED / "ddjj_ganancias_tramos.csv", index=False)
    r = tot.join(todo[todo.es_total].set_index("anio_fiscal")[["exentos", "exentos_ventas"]])
    r["tramos"] = todo[~todo.es_total].groupby("anio_fiscal").size()
    print((r.assign(casos=r.casos / 1e3).div({c: 1e9 if c not in ("casos", "tramos") else 1 for c in r.columns})).round(1).to_string())
