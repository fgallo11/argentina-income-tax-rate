"""Lectura y armonización de los microdatos trimestrales de la EPH continua (INDEC)."""
from __future__ import annotations

import numpy as np
import pandas as pd

from .config import RAW
from .util import deciles_ponderados

COLS = [
    "CODUSU", "NRO_HOGAR", "COMPONENTE", "AGLOMERADO", "PONDERA", "PONDIH",
    "CH03", "CH04", "CH06", "ESTADO", "CAT_OCUP", "PP04A", "PP04B1", "PP04C", "PP04C99",
    "PP07H", "P21", "V2_M", "V21_M", "PP08J1", "P47T", "ITF", "IPCF",
    "TOT_P12", "V8_M", "V9_M", "V10_M",   # otras ocupaciones; alquileres, ganancias de negocios, intereses
]
NUMERICAS = [c for c in COLS if c != "CODUSU"]


def _aguinaldo_devengado(df: pd.DataFrame) -> pd.DataFrame:
    """Reemplaza el aguinaldo cobrado en el mes por el aguinaldo devengado (1/12 por mes).

    La EPH pregunta por el ingreso del mes anterior. En el primer y el tercer trimestre
    (encuestas que preguntan por diciembre y junio) el ingreso total (P47T, ITF, IPCF)
    incluye el aguinaldo cobrado: PP08J1 en la ocupación principal y V21_M en
    jubilaciones. P21 y V2_M no lo incluyen (verificado en los microdatos; ver
    docs/auditoria.md, 4.3). Los impuestos directos se simulan sobre P21 y V2_M, así que
    el aguinaldo quedaba en el denominador sin sus impuestos y las tasas oscilaban entre
    trimestres.

    Criterio: base devengada. Se resta el aguinaldo cobrado declarado y se suma 1/12 del
    salario (asalariados con descuento jubilatorio) y de la jubilación (jubilados), que es
    lo que devenga el aguinaldo cada mes. Los impuestos directos se llevan a la misma
    base en directos.simular. Supuesto: los asalariados sin descuento jubilatorio no
    devengan aguinaldo (si declaran uno cobrado, se resta igual).
    """
    df = df.copy()
    cobrado = df.PP08J1.where(df.PP08J1 > 0, 0.0).fillna(0.0) + df.V21_M.where(df.V21_M > 0, 0.0).fillna(0.0)
    con_sac = (df.ESTADO == 1) & (df.CAT_OCUP == 3) & (df.PP07H == 1)
    devengado = np.where(con_sac, df.P21, 0.0) / 12.0 + df.V2_M / 12.0
    delta = devengado - cobrado
    df["aguinaldo_cobrado"] = cobrado
    df["aguinaldo_devengado"] = devengado
    df["P47T"] = (df.P47T + delta).clip(lower=0.0)
    g = df.groupby("hid", sort=False)
    delta_hog = pd.Series(delta, index=df.index).groupby(df.hid, sort=False).transform("sum")
    # miembros del hogar = ITF / IPCF (incluye a quienes no figuran en la base de personas)
    miembros = np.where((df.IPCF > 0) & (df.ITF > 0), df.ITF / df.IPCF, g["hid"].transform("size"))
    df["IPCF_declarado"] = df.IPCF
    df["ITF"] = (df.ITF + delta_hog).clip(lower=0.0)
    df["IPCF"] = (df.IPCF + delta_hog / miembros).clip(lower=0.0)
    return df


def _archivo_individual(anio: int, trim: int):
    carpeta = RAW / "eph" / f"{anio}T{trim}"
    cand = [p for p in carpeta.rglob("*") if p.is_file() and ("ndividual" in p.name or "personas" in p.name.lower())
            and p.suffix.lower() in {".dta", ".txt"}]
    if not cand:
        raise FileNotFoundError(f"No hay base individual EPH en {carpeta}")
    return cand[0]


def cargar_trimestre(anio: int, trim: int) -> pd.DataFrame:
    """Base de personas de un trimestre con variables armonizadas.

    Decisiones:
    - Ponderador: desde 2016T2 INDEC no imputa ingresos y publica PONDIH (corrige la no
      respuesta de ingresos del hogar); se usa PONDIH y se descartan hogares con
      PONDIH = 0. Hasta 2015 los ingresos faltantes vienen imputados y se usa PONDERA.
    - Ingresos negativos (códigos de no respuesta, -9) se tratan como faltantes; con
      PONDIH > 0 no deberían aparecer en ITF/IPCF. En P21 y V2_M de hogares válidos se
      llevan a 0 (se informa la cantidad).
    """
    f = _archivo_individual(anio, trim)
    if f.suffix.lower() == ".dta":
        df = pd.read_stata(f, convert_categoricals=False)
    else:
        df = pd.read_csv(f, sep=";", decimal=",", low_memory=False, encoding="latin-1")
    df.columns = [c.upper().strip() for c in df.columns]

    # Desde 2023T4 la jubilación/pensión se abre en tres conceptos
    if "V2_M" not in df.columns:
        df = df.copy()
        partes = [c for c in ("V2_01_M", "V2_02_M", "V2_03_M") if c in df.columns]
        if partes:
            v = df[partes].apply(pd.to_numeric, errors="coerce")
            df["V2_M"] = v.where(v > 0, 0).sum(axis=1)
    if "V21_M" not in df.columns:
        partes = [c for c in ("V21_01_M", "V21_02_M", "V21_03_M") if c in df.columns]
        if partes:
            v = df[partes].apply(pd.to_numeric, errors="coerce")
            df["V21_M"] = v.where(v > 0, 0).sum(axis=1)
    for c in COLS:
        if c not in df.columns:
            df[c] = np.nan
    df = df[COLS].copy()
    for c in NUMERICAS:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["CODUSU"] = df["CODUSU"].astype(str).str.strip()
    df["hid"] = df["CODUSU"] + "_" + df["NRO_HOGAR"].astype("Int64").astype(str)

    usa_pondih = df["PONDIH"].notna().any() and (df["PONDIH"] > 0).any()
    df["w"] = df["PONDIH"] if usa_pondih else df["PONDERA"]
    df = df[(df.w > 0) & df.IPCF.notna() & (df.IPCF >= 0)].copy()
    neg_p21 = int((df.P21 < 0).sum())
    for c in ("P21", "V2_M", "P47T", "TOT_P12", "V8_M", "V9_M", "V10_M"):
        df[c] = df[c].where(df[c] > 0, 0.0).fillna(0.0)
    df["anio"], df["trim"] = anio, trim
    df = _aguinaldo_devengado(df)

    # deciles de personas según IPCF del hogar (con aguinaldo devengado)
    hog = df.groupby("hid", sort=False).agg(ipcf=("IPCF", "first"), wp=("w", "sum")).reset_index()
    hog["decil"] = deciles_ponderados(hog.ipcf.values, hog.wp.values, hog.hid.values)
    df = df.merge(hog[["hid", "decil"]], on="hid", how="left")
    df.attrs["ponderador"] = "PONDIH" if usa_pondih else "PONDERA"
    df.attrs["neg_p21"] = neg_p21
    return df
