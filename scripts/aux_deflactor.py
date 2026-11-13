#!/usr/bin/env python
"""Índice de precios al consumidor empalmado, 2003-2024 (data/processed/deflactor.csv).

Tramos del empalme (variación mensual de cada fuente, encadenada):
  hasta 12/2006   IPC-GBA, INDEC (base abril 2008).
  01/2007-12/2016 IPC de la Provincia de San Luis. El IPC del INDEC de esos años está
                  cuestionado (intervención 2007-2015); San Luis es el reemplazo más usado
                  en la literatura para el período completo.
  desde 01/2017   IPC Nacional, INDEC (base diciembre 2016).
(Se probó el IPC de Mendoza como variante: la serie publicada tiene meses sin variación
en 2013-2015 y no es utilizable.)

Fuentes: API de Series de Tiempo (datos.gob.ar); ver scripts/01_descargar_datos.py.
Salida: año, índice promedio anual (2024 = 1) y canasta básica total (cbt): promedio anual
de la CBT del Gran Buenos Aires por adulto equivalente (INDEC) desde 2017; antes de 2017, la
de 2017 llevada hacia atrás con el IPC empalmado (las canastas oficiales de 2007-2015 están
intervenidas y la serie actual empieza en 04/2016).
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from incidencia.config import PROCESSED, RAW  # noqa: E402

M = RAW / "macro"


def serie(id_):
    s = pd.read_csv(M / f"ipc_{id_}.csv")
    return pd.Series(s.iloc[:, 1].values, index=pd.PeriodIndex(s.iloc[:, 0].str[:7], freq="M"))


def empalme(tramo_medio: pd.Series) -> pd.Series:
    gba = serie("97.2_ING_2008_M_17")
    nac = serie("148.3_INIVELNAL_DICI_M_26")
    var = pd.concat([
        gba.pct_change().loc[:"2006-12"],
        tramo_medio.pct_change().loc["2007-01":"2016-12"],
        nac.pct_change().loc["2017-01":],
    ])
    var = var[~var.index.duplicated()].sort_index().loc["2003-02":]
    nivel = (1 + var.fillna(0)).cumprod()
    return nivel.groupby(nivel.index.year).mean()


def main() -> None:
    central = empalme(serie("197.1_NIVEL_GENERAL_2014_0_13"))
    out = pd.DataFrame({"ipc": central / central.loc[2024]}).loc[2003:2024]
    cbt = pd.read_csv(M / "cbt_gba_mensual.csv")
    cbt = pd.Series(cbt.iloc[:, 1].values, index=cbt.iloc[:, 0].str[:4].astype(int)).groupby(level=0).mean()
    out["cbt"] = cbt.reindex(out.index)
    antes = out.index < 2017
    out.loc[antes, "cbt"] = cbt[2017] * out.ipc[antes] / out.ipc[2017]
    out["cbt_oficial"] = ~antes
    out.index.name = "anio"
    out.to_csv(PROCESSED / "deflactor.csv")
    print(out.assign(inflacion=out.ipc.pct_change() * 100).round(2).to_string())
    print("OK ->", PROCESSED / "deflactor.csv")


if __name__ == "__main__":
    main()
