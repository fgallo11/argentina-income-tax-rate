#!/usr/bin/env python
"""Extrae de los anuarios de ARCA las declaraciones juradas de Ganancias de personas
humanas por tramo de ingresos gravados (presentaciones con ingresos gravados), años fiscales 2002-2024.

Salida: data/processed/ddjj_ganancias_tramos.csv, una fila por (año fiscal, tramo), en
pesos corrientes:
  casos, ingresos_gravados (brutos), gnsi (ganancia neta sujeta a impuesto),
  impuesto (determinado), resultado_neto (beneficio - quebranto, antes de
  deducciones generales y personales), exentos (ganancias e ingresos exentos o no
  alcanzados declarados), exentos_ventas (la parte que es resultado por venta de bienes
  o moneda extranjera), bienes y patrimonio_neto al cierre.
Cada cuadro se ubica por su título, no por su número, y se controla contra su fila TOTAL.
"""
import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from incidencia.anuarios import cuadros, leer, por_tramo, titulo  # noqa: E402
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
    return None


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
        r = rol(titulo(leer(cs[k])))
        if r and r not in hallados:
            hallados[r] = cs[k]
    falta = {"resumen", "neto", "patrimonio"} - set(hallados)
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
    out.insert(0, "anio_fiscal", anuario - 1)
    out.insert(1, "es_total", out.desde.isna())
    return out


if __name__ == "__main__":
    todo = pd.concat([extraer(a) for a in range(2003, 2026)], ignore_index=True)
    # control: la suma de tramos reproduce la fila TOTAL
    cols = ["casos", "gnsi", "impuesto", "resultado_neto", "patrimonio_neto"]
    s = todo[~todo.es_total].groupby("anio_fiscal")[cols].sum()
    tot = todo[todo.es_total].set_index("anio_fiscal")[cols]
    dif = (s / tot - 1).abs().max()
    print("desvío máximo suma de tramos vs TOTAL:", dif.round(5).to_dict())
    assert (dif < 0.002).all()
    todo.to_csv(PROCESSED / "ddjj_ganancias_tramos.csv", index=False)
    r = tot.join(todo[todo.es_total].set_index("anio_fiscal")[["exentos", "exentos_ventas"]])
    r["tramos"] = todo[~todo.es_total].groupby("anio_fiscal").size()
    print((r.assign(casos=r.casos / 1e3).div({c: 1e9 if c not in ("casos", "tramos") else 1 for c in r.columns})).round(1).to_string())
