#!/usr/bin/env python
"""Procesa los microdatos de la ENGHo 2004/05, 2012/13 y 2017/18.

Para cada edición y cada decil de ingreso per cápita familiar (deciles de PERSONAS,
ordenadas por ingreso per cápita del hogar, ponderadas) calcula:
  - ingreso total y gasto de consumo total  ->  relación gasto/ingreso;
  - gasto de consumo por clase de IVA y por rubro de Impuestos Internos.

Salidas:
  data/processed/engho_grupos.csv              (una fila por edición y veintil)
  data/processed/clasificacion_articulos_<ed>.csv  (auditoría de la clasificación)
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from incidencia.clasificador import clase_internos, clase_iva, sector_coicop  # noqa: E402
from incidencia.config import PROCESSED, RAW  # noqa: E402
from incidencia.util import deciles_ponderados  # noqa: E402

E = RAW / "engho"
# Grupos de ingreso per cápita (veintiles): se usan para estimar, por interpolación, el
# consumo y la canasta que corresponden a cada nivel de ingreso RELATIVO a la media.
N_GRUPOS = 20


def _num(s: pd.Series) -> pd.Series:
    if s.dtype == object or str(s.dtype).startswith("str"):
        s = s.astype(str).str.replace(",", ".", regex=False)
    return pd.to_numeric(s, errors="coerce")


# ----------------------------------------------------------------------------- lectura
def leer_2017():
    h = pd.read_csv(E / "2017/engho2018_hogares/engho2018_hogares.txt", sep="|", low_memory=False)
    h = h.rename(columns={"id": "hid", "pondera": "w", "cantmiem": "miembros",
                          "ingtoth": "ingreso", "gastot": "gasto_total"})[
        ["hid", "w", "miembros", "ingreso", "gasto_total"]]
    g = pd.read_csv(E / "2017/engho2018_gastos/engho2018_gastos.txt", sep="|", low_memory=False,
                    usecols=["id", "articulo", "monto"]).rename(columns={"id": "hid"})
    cat = pd.read_csv(E / "2017/engho2018_articulos/engho2018_articulos.txt", sep="|", encoding="utf-8")
    cat = cat.rename(columns={"articulo_desc": "desc", "subclase_desc": "subdesc"})[["articulo", "desc", "subdesc"]]
    return h, g, cat


def _catalogo_9cap(path: Path, col_clave: str, enc: str) -> pd.DataFrame:
    c = pd.read_csv(path, sep="|", encoding=enc, dtype=str, index_col=False)
    c.columns = [x.strip().upper() for x in c.columns]
    c = c.rename(columns={col_clave: "CLAVE"})
    sub = c[c.ARTICULO.isna() & c.SUBCLASE.notna()].set_index("CLAVE")["DESCRIPCION"]
    art = c[c.ARTICULO.notna()].copy()
    art["subdesc"] = art.SUBCLASE.map(sub).fillna("")
    return art.rename(columns={"ARTICULO": "articulo", "DESCRIPCION": "desc"})[["articulo", "desc", "subdesc"]]


def _es_consumo_9cap(art: pd.Series) -> pd.Series:
    """Artículos de gasto de consumo en el nomenclador de 9 capítulos.

    Se excluyen: registros de ingresos y movimientos financieros (25x-27x), capítulo
    98x-99x (transferencias, inversiones, gastos de la actividad económica) y alquileres
    imputados (3112, 3115, 3116).
    """
    a = art.astype(str)
    return ~(a.str.match(r"^(25|26|27|98|99)") | a.str.match(r"^(3112|3115|3116|3121|3122)"))


def leer_2012():
    base = next((E / "2012/bases_datos_engho2012").glob("*/"))
    h = pd.read_csv(base / "ENGHo - Hogares.txt", sep="|", encoding="latin-1", low_memory=False)
    h.columns = [c.upper() for c in h.columns]
    h = h.rename(columns={"CLAVE": "hid", "EXPAN": "w", "CANTMIEM": "miembros",
                          "INGTOTH": "ingreso", "GASTOT": "gasto_total"})[
        ["hid", "w", "miembros", "ingreso", "gasto_total"]]
    g = pd.read_csv(base / "ENGHo - Gastos.txt", sep="|", encoding="latin-1", low_memory=False,
                    usecols=["CLAVE", "ARTICULO", "MONTO"], dtype={"ARTICULO": str})
    g = g.rename(columns={"CLAVE": "hid", "ARTICULO": "articulo", "MONTO": "monto"})
    cat = _catalogo_9cap(E / "2012/codigos_engho2012/ENGHo_Codigos_de_bienes_y_servicios.txt", "CLAVE", "utf-8")
    return h, g[_es_consumo_9cap(g.articulo)], cat


def leer_2004():
    h = pd.read_csv(E / "2004/ENGH0405_hogar/ENGH0405_hogar.txt", sep="|", encoding="latin-1",
                    low_memory=False, index_col=False)
    h = h.rename(columns={"CLAVE": "hid", "EXPAN": "w", "CANTMIEM": "miembros",
                          "INGTOTH": "ingreso", "GASTOT": "gasto_total"})[
        ["hid", "w", "miembros", "ingreso", "gasto_total"]]
    g = pd.read_csv(E / "2004/ENGH0405_gastos/ENGH0405_gastos.txt", sep="|", encoding="latin-1",
                    low_memory=False, index_col=False, usecols=["CLAVE", "ARTICULO", "MONTO"],
                    dtype={"ARTICULO": str})
    g = g.rename(columns={"CLAVE": "hid", "ARTICULO": "articulo", "MONTO": "monto"})
    cat = _catalogo_9cap(E / "2004/ENGH0405_codigos_bienes_servicios/ENGH0405_codigos_bienes_servicios.txt",
                         "CLAVEAGRP", "latin-1")
    return h, g[_es_consumo_9cap(g.articulo)], cat


LECTORES = {"2004": leer_2004, "2012": leer_2012, "2017": leer_2017}


# ----------------------------------------------------------------------------- proceso
def procesar(ed: str) -> pd.DataFrame:
    h, g, cat = LECTORES[ed]()
    for c in ("w", "miembros", "ingreso", "gasto_total"):
        h[c] = _num(h[c])
    g["monto"] = _num(g["monto"]).fillna(0.0)
    g["articulo"] = g["articulo"].astype(str).str.strip()
    cat["articulo"] = cat["articulo"].astype(str).str.strip()
    cat = cat.drop_duplicates("articulo")

    # clasificación de artículos
    cat["sector"] = [sector_coicop(ed, a) for a in cat.articulo]
    res = [clase_iva(s, d, sd) for s, d, sd in zip(cat.sector, cat.desc, cat.subdesc)]
    cat["clase_iva"] = [r[0] for r in res]
    cat["regla_iva"] = [r[1] for r in res]
    cat["clase_internos"] = [clase_internos(s, d, sd) for s, d, sd in zip(cat.sector, cat.desc, cat.subdesc)]

    g = g.merge(cat[["articulo", "sector", "clase_iva", "clase_internos"]], on="articulo", how="left")
    sin = g.clase_iva.isna()
    if sin.any():
        g.loc[sin, "sector"] = [sector_coicop(ed, a) for a in g.loc[sin, "articulo"]]
        g.loc[sin, "clase_iva"] = "G21"
        g.loc[sin, "clase_internos"] = ""

    # hogares válidos e ingreso per cápita
    h = h[(h.w > 0) & (h.miembros > 0) & h.ingreso.notna() & (h.ingreso >= 0) & h.gasto_total.notna()].copy()
    h["ipc"] = h.ingreso / h.miembros
    h["wp"] = h.w * h.miembros
    h["decil"] = deciles_ponderados(h.ipc.values, h.wp.values, h.hid.values, n=N_GRUPOS)
    g = g.merge(h[["hid", "w", "decil"]], on="hid", how="inner")
    g["mw"] = g.monto * g.w

    # control: suma de artículos vs gasto total del archivo de hogares
    tot_art = g.mw.sum()
    tot_hog = (h.gasto_total * h.w).sum()
    print(f"ENGHo {ed}: hogares={len(h):,}  gasto artículos/gasto_total hogares = {tot_art / tot_hog:.4f}  "
          f"artículos sin catálogo = {sin.mean():.2%} de registros")

    peso = g.groupby("articulo").mw.sum() / tot_art
    cat["participacion_gasto"] = cat.articulo.map(peso).fillna(0.0)
    cat.sort_values("articulo").to_csv(PROCESSED / f"clasificacion_articulos_{ed}.csv", index=False)

    base = h.groupby("decil").apply(
        lambda x: pd.Series({
            "personas": x.wp.sum(),
            "ingreso": (x.ingreso * x.w).sum(),
            "gasto_hogares": (x.gasto_total * x.w).sum(),
        }), include_groups=False)
    base["gasto_articulos"] = g.groupby("decil").mw.sum()
    iva = g.pivot_table(index="decil", columns="clase_iva", values="mw", aggfunc="sum", fill_value=0.0)
    iva.columns = [f"iva_{c}" for c in iva.columns]
    gi = g[g.clase_internos != ""]
    inter = gi.pivot_table(index="decil", columns="clase_internos", values="mw", aggfunc="sum", fill_value=0.0)
    inter.columns = [f"int_{c}" for c in inter.columns]
    out = base.join(iva).join(inter).fillna(0.0).reset_index()
    out.insert(0, "edicion", ed)
    return out


if __name__ == "__main__":
    tabla = pd.concat([procesar(e) for e in ("2004", "2012", "2017")], ignore_index=True).fillna(0.0)
    tabla = tabla.rename(columns={"decil": "grupo"})
    media = tabla.groupby("edicion").apply(lambda x: x.ingreso.sum() / x.personas.sum(), include_groups=False)
    m = tabla.edicion.map(media)
    # ingreso y consumo per cápita del grupo, relativos al ingreso per cápita medio de la encuesta
    tabla["ingreso_rel"] = tabla.ingreso / tabla.personas / m
    tabla["consumo_rel"] = tabla.gasto_articulos / tabla.personas / m
    tabla["gasto_sobre_ingreso"] = tabla.gasto_articulos / tabla.ingreso
    tabla.to_csv(PROCESSED / "engho_grupos.csv", index=False)
    pd.set_option("display.width", 250)
    cols = [c for c in tabla.columns if c.startswith("iva_")]
    v = tabla.copy()
    for c in cols + [c for c in tabla.columns if c.startswith("int_")]:
        v[c] = (v[c] / v.gasto_articulos * 100).round(1)
    print(v[["edicion", "grupo", "ingreso_rel", "consumo_rel", "gasto_sobre_ingreso"] + cols +
            [c for c in tabla.columns if c.startswith("int_")]].round(3).to_string(index=False))
