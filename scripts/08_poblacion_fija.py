#!/usr/bin/env python
"""Contrafáctico de población fija: separa cambios de reglas de cambios de composición.

Los deciles no son las mismas personas a lo largo del tiempo: cambia quién es asalariado
registrado, cuentapropista o jubilado, y cuánto gana cada uno en relación con los demás.
Para aislar el efecto de la POLÍTICA TRIBUTARIA se toma una población fija (los cuatro
trimestres de la EPH del año base), se llevan sus ingresos nominales al nivel de cada año
con el RIPTE (todos los ingresos se mueven igual: la distribución relativa no cambia) y
se le aplican las reglas y la presión tributaria agregada de cada año. La canasta de
consumo también queda fija: la ENGHo contemporánea del año base (2004/05 para 2004,
2017/18 para 2017).

Se calcula con dos años base, 2004 (el primero de la serie) y 2017 (la ENGHo más reciente).
El resultado depende del año base (problema de números índice): se publican los dos.

  serie observada   = reglas del año + población del año
  serie contrafáctica = reglas del año + población de AÑO_BASE
  diferencia        = efecto de composición (formalización, estructura de ingresos, desigualdad)

Salida: outputs/tables/serie_poblacion_fija.csv
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from incidencia.config import TABLES  # noqa: E402
from incidencia.directos import MESES_TRIM, Parametros, resumir_por_decil, simular  # noqa: E402
from incidencia.eph import cargar_trimestre  # noqa: E402
from incidencia.incidencia import IMPUESTOS, Variante, incidencia_trimestre  # noqa: E402
from incidencia.indirectos import cargar_insumos  # noqa: E402

BASES = {2004: "2004", 2017: "2017"}   # año base -> edición de la ENGHo


def ripte_trim(P, anio, trim):
    return sum(P.ripte[P.mes(anio, m)] for m in MESES_TRIM[trim]) / 3


if __name__ == "__main__":
    P = Parametros()
    engho, rec = cargar_insumos()
    filas = []
    for anio_base, edicion in BASES.items():
        base = {t: cargar_trimestre(anio_base, t) for t in (1, 2, 3, 4)}
        v = Variante("poblacion_fija", modo_engho=edicion)
        for anio in range(2004, 2025):
            trims = []
            for t, df0 in base.items():
                k = ripte_trim(P, anio, t) / ripte_trim(P, anio_base, t)
                df = df0.copy()
                for c in ("P21", "V2_M", "IPCF", "ITF", "P47T", "TOT_P12", "V8_M", "V9_M", "V10_M"):
                    df[c] = df[c] * k
                q = resumir_por_decil(simular(df, P, anio, t))
                trims.append(incidencia_trimestre(q, anio, engho, rec.loc[anio], v))
            p = (sum(trims) / 4).reset_index().rename(columns={"index": "decil"})
            p.insert(0, "anio", anio)
            p.insert(0, "anio_base", anio_base)
            filas.append(p)
            print(anio_base, anio, (p.set_index("decil").total.loc[[0, 1, 5, 10]] * 100).round(1).to_dict(),
                  flush=True)
    out = pd.concat(filas, ignore_index=True)
    out[["anio_base", "anio", "decil"] + IMPUESTOS + ["total", "directos", "indirectos"]].to_csv(
        TABLES / "serie_poblacion_fija.csv", index=False)
