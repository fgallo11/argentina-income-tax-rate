"""Impuestos indirectos (IVA, Internos, Ingresos Brutos) por decil.

1) NIVEL. Cada impuesto se expresa como "pesos de impuesto por peso de consumo privado"
   de Cuentas Nacionales (recaudación / consumo privado a precios corrientes). Así el
   nivel queda anclado a lo efectivamente recaudado y no a alícuotas "efectivas" supuestas.

2) DISTRIBUCIÓN. El consumo y la canasta de cada decil de la EPH se toman de la ENGHo
   según su INGRESO RELATIVO a la media (no según su número de decil):
     - en cada ENGHo se calcula, por veintil de ingreso per cápita, el consumo per cápita
       relativo al ingreso medio y la composición del gasto por tratamiento impositivo;
     - a cada decil EPH de cada trimestre se le asigna, interpolando, el valor que la
       ENGHo muestra para hogares con su mismo ingreso relativo.
   Esto evita suponer que "el decil 1 de la EPH consume como el decil 1 de la ENGHo"
   aunque su posición relativa haya cambiado (por ejemplo, cuando cae la desigualdad).

3) EDICIONES. Entre dos ENGHo se interpola linealmente en el tiempo (anclas: 2005, 2012
   y 2018, puntos medios del trabajo de campo); antes de 2005 y después de 2018 se usa
   la edición más cercana. Evita saltos artificiales en los años de cambio de edición.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .config import PROCESSED

RUBROS_INTERNOS = {
    "tabaco": "sel_tabaco", "alcohol": "sel_alcohol", "cerveza": "sel_cerveza",
    "analcoholicas": "sel_analcoholicas", "vehiculos": "sel_vehiculos", "telefonia": "sel_telefonia",
}
# Fracción de 2019 con alícuota 0% del Dto. 567/2019 (16/08 al 31/12 = 4,5 meses)
F_567_2019 = 4.5 / 12
ANCLAS_ENGHO = {"2004": 2005.0, "2012": 2012.0, "2017": 2018.0}


def pesos_ediciones(anio: int, modo: str = "interpolado") -> dict[str, float]:
    """Peso de cada edición de la ENGHo para `anio`.

    modo "interpolado" (principal) o "escalonado" (cada edición rige hasta la siguiente:
    criterio original del proyecto, se conserva como variante).
    """
    if modo == "escalonado":
        return {"2004" if anio <= 2011 else "2012" if anio <= 2016 else "2017": 1.0}
    if modo in ANCLAS_ENGHO:           # edición fija
        return {modo: 1.0}
    eds = sorted(ANCLAS_ENGHO, key=ANCLAS_ENGHO.get)
    if anio <= ANCLAS_ENGHO[eds[0]]:
        return {eds[0]: 1.0}
    if anio >= ANCLAS_ENGHO[eds[-1]]:
        return {eds[-1]: 1.0}
    for a, b in zip(eds[:-1], eds[1:]):
        ya, yb = ANCLAS_ENGHO[a], ANCLAS_ENGHO[b]
        if ya <= anio <= yb:
            w = (anio - ya) / (yb - ya)
            return {a: 1 - w, b: w}
    raise ValueError(anio)


def alicuota_iva(clase: str, anio: int, exento: float = 0.0) -> float:
    """Alícuota legal de IVA (sobre precio sin impuesto) por clase y año.

    exento: fracción de la alícuota general que se carga a los bienes exentos por el IVA de
    sus insumos (Pessino et al. 2023 usan 0,2; la medida principal, 0)."""
    f567 = F_567_2019 if anio == 2019 else 0.0
    if clase in ("G21", "MED"):
        return 0.21
    if clase == "G105":
        return 0.105
    if clase == "EX":
        return 0.21 * exento
    if clase == "AVPO":   # Ley 27.430: 10,5% desde 02/2018
        if anio <= 2017:
            return 0.21
        return (1 * 0.21 + 11 * 0.105) / 12 if anio == 2018 else 0.105
    if clase == "C567_21":
        return 0.21 * (1 - f567)
    if clase == "C567_105":
        return 0.105 * (1 - f567)
    raise KeyError(clase)


def perfil_consumo(anio: int, ingreso_rel: np.ndarray, engho: pd.DataFrame,
                   modo: str = "interpolado", exento: float = 0.0) -> pd.DataFrame:
    """Consumo y canasta que corresponden a hogares con `ingreso_rel` en `anio`.

    Devuelve DataFrame (una fila por elemento de ingreso_rel) con:
      consumo_rel : consumo per cápita / ingreso per cápita medio de la población
      iva_legal   : contenido legal de IVA por peso gastado, t/(1+t) ponderado
      s_<rubro>   : participación del gasto en cada rubro gravado por Internos
    Fuera del rango de ingresos de la ENGHo se usa el valor del extremo.
    """
    r = np.asarray(ingreso_rel, dtype=float)
    out = None
    for ed, w in pesos_ediciones(anio, modo).items():
        e = engho[engho.edicion.astype(str) == ed].sort_values("ingreso_rel")
        g = e.gasto_articulos
        x = e.ingreso_rel.values
        cols = {"consumo_rel": e.consumo_rel.values}
        legal = sum(e[c] / g * (alicuota_iva(c[4:], anio, exento) / (1 + alicuota_iva(c[4:], anio, exento)))
                    for c in e.columns if c.startswith("iva_"))
        cols["iva_legal"] = legal.values
        for rubro in RUBROS_INTERNOS:
            cols[f"s_{rubro}"] = (e[f"int_{rubro}"] / g).clip(lower=0.0).values
        p = pd.DataFrame({k: np.interp(r, x, v) for k, v in cols.items()})
        out = p * w if out is None else out + p * w
    return out


def tasas_indirectas(perfil: pd.DataFrame, consumo: np.ndarray, rec: pd.Series,
                     iva_nivel_legal: bool = False) -> pd.DataFrame:
    """Impuesto por peso de consumo para cada decil.

    `consumo` son los totales de consumo de cada decil (ponderadores para las medias).
    Con iva_nivel_legal=True el IVA usa la alícuota legal plena (sin evasión): cota superior.
    """
    cpriv = rec["consumo_privado"]
    tot = consumo.sum()
    out = pd.DataFrame(index=perfil.index)
    legal_medio = (perfil.iva_legal.values * consumo).sum() / tot
    out["iva"] = perfil.iva_legal if iva_nivel_legal else rec["iva"] / cpriv * perfil.iva_legal / legal_medio
    inter = 0.0
    for rubro, col in RUBROS_INTERNOS.items():
        s = perfil[f"s_{rubro}"].values
        s_medio = (s * consumo).sum() / tot
        inter = inter + rec[col] / cpriv * s / s_medio
    out["internos"] = inter
    out["iibb"] = rec["ingresos_brutos"] / cpriv
    out.attrs["iva_legal_medio"] = legal_medio
    return out


def cargar_insumos():
    engho = pd.read_csv(PROCESSED / "engho_grupos.csv")
    rec = pd.read_csv(PROCESSED / "recaudacion_macro.csv", index_col=0)
    altos = PROCESSED / "ajuste_altos_ingresos.csv"      # scripts/09_ingresos_altos.py
    if altos.exists():
        a = pd.read_csv(altos, index_col=0)
        rec = rec.join(a[[c for c in a.columns if c not in rec.columns]])
    cn = PROCESSED / "cn_ingresos.csv"                     # scripts/aux_cuentas_nacionales.py
    if cn.exists():
        c = pd.read_csv(cn, index_col=0)
        rec = rec.join(c[[x for x in c.columns if x not in rec.columns]])
    return engho, rec
