#!/usr/bin/env python
"""Arma la tabla anual de recaudación y agregados macro usada para calibrar y validar.

Fuente de recaudación: DNIAF (Ministerio de Economía), "Recaudación tributaria -
Clasificación internacional", en millones de pesos corrientes, 1991-2025. Es una única
fuente oficial que separa Ganancias de personas físicas, Bienes Personales, IVA, los
impuestos selectivos por producto, aportes de empleados / empleadores e impuestos
provinciales generales sobre bienes y servicios (Ingresos Brutos).

Reemplaza las tablas hardcodeadas de la notebook original (que tenían, entre otros
errores, 2013 = copia de 2012 y Bienes Personales 2004-2010 muy subestimado).

Salida: data/processed/recaudacion_macro.csv
"""
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from incidencia.config import ANIO_FIN, PROCESSED, RAW  # noqa: E402

# índice DNIAF -> nombre de columna
FILAS = {
    "1.1.1": "ganancias_pf",
    "1.2.1": "ganancias_sociedades",
    "2.6.1": "bienes_personales",
    "3.1.1": "iva",
    "3.2.1": "sel_tabaco",
    "3.2.2": "sel_alcohol",
    "3.2.3": "sel_cerveza",
    "3.2.4": "sel_analcoholicas",
    "3.2.5": "sel_vehiculos",
    "3.2.6": "sel_combustibles",
    "3.2.9": "sel_otros",
    "3.3.2": "sel_telefonia",
    "3.1.2.2": "creditos_debitos",
    "4.2": "derechos_exportacion",
    "5.2": "monotributo",
    "6.1": "ss_empleados",
    "6.2": "ss_empleadores",
    "6.3": "ss_autonomos",
    "9": "recaudacion_neta_nacional",
    "10": "provinciales_total",
    "10.2.1": "ingresos_brutos",
    "12": "recaudacion_neta_total",
}


def leer_dniaf() -> pd.DataFrame:
    d = pd.read_excel(RAW / "recaudacion" / "dniaf_recaudacion_nominal_clasif_internacional.xlsx", header=None)
    fila_hdr = d.index[d[0].astype(str).str.strip().eq("Índice")][0]
    anios = d.loc[fila_hdr, 2:].astype(float).astype(int)
    d = d.loc[fila_hdr + 1:]
    d[0] = d[0].astype(str).str.strip()
    out = {}
    for idx, nombre in FILAS.items():
        fila = d[d[0] == idx]
        if len(fila) != 1:
            raise SystemExit(f"Fila DNIAF {idx} ({nombre}) no encontrada de forma única")
        out[nombre] = pd.to_numeric(fila.iloc[0, 2:], errors="coerce").values
    return pd.DataFrame(out, index=anios.values).rename_axis("anio")


def serie_anual(nombre: str) -> pd.Series:
    s = pd.read_csv(RAW / "macro" / nombre)
    return pd.Series(s.iloc[:, 1].values, index=s.iloc[:, 0].str[:4].astype(int))


if __name__ == "__main__":
    t = leer_dniaf()
    t["consumo_privado"] = serie_anual("consumo_privado_corriente_anual.csv")
    t["pib"] = serie_anual("pib_corriente_anual.csv")
    wb = json.load(open(RAW / "macro" / "poblacion_total_wb.json"))[1]
    t["poblacion"] = pd.Series({int(r["date"]): r["value"] for r in wb})
    # Internos sobre consumo modelados (Ley 24.674): tabaco, alcohol, cerveza,
    # analcohólicas, vehículos y telefonía celular.
    rub = ["sel_tabaco", "sel_alcohol", "sel_cerveza", "sel_analcoholicas", "sel_vehiculos", "sel_telefonia"]
    t["internos_modelados"] = t[rub].sum(axis=1)
    t = t.loc[2003:ANIO_FIN]
    t.to_csv(PROCESSED / "recaudacion_macro.csv")
    pd.set_option("display.width", 250)
    v = t.copy()
    for c in ["ganancias_pf", "bienes_personales", "iva", "internos_modelados", "ss_empleados",
              "ss_empleadores", "ingresos_brutos", "derechos_exportacion", "recaudacion_neta_total"]:
        v[c + "_%pib"] = (v[c] / v.pib * 100).round(2)
    print(v[[c for c in v.columns if c.endswith("%pib")]].to_string())
    print((t[["iva", "ingresos_brutos", "internos_modelados"]].div(t.consumo_privado, axis=0) * 100).round(2)
          .add_suffix("_%consumo").to_string())
