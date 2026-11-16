#!/usr/bin/env python
"""Corre la microsimulación de impuestos directos sobre cada trimestre de la EPH.

Salida: data/processed/eph_trimestral_tramos.csv: lo mismo con el decil 10 partido en
91 (percentiles 90-95), 95 (95-99) y 99 (el 1% superior), ordenados por el mismo IPCF.
data/processed/eph_trimestral_decil.csv, una fila por (año, trimestre, decil)
con totales expandidos MENSUALES (pesos corrientes del trimestre):
  personas, ipcf (ingreso de bolsillo), ing_pre (agregado para llegar al ingreso antes
  de impuestos directos), ap_jub, ap_inssjp, ap_os, ganancias, contrib (contribuciones
  patronales totales), masa salarial bruta registrada, cantidad de registrados y de
  contribuyentes de Ganancias.
"""
import sys
import time
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from incidencia.config import PROCESSED, trimestres_disponibles  # noqa: E402
from incidencia.directos import Parametros, resumir_por_decil, simular  # noqa: E402
from incidencia.eph import cargar_trimestre  # noqa: E402


FRACCION_COLA = 0.12   # parte superior de la población (personas) que se guarda


def cola_alta(s: pd.DataFrame, anio: int, trim: int) -> pd.DataFrame:
    """Personas de mayor ingreso individual, para comparar con las declaraciones juradas.

    ing_anual: ingreso individual total antes de impuestos directos, anualizado
    (12 meses de ingreso de bolsillo + aportes + obra social + Ganancias, todo en base
    devengada: ya incluye 1/12 de aguinaldo por mes). Se guarda el decil del hogar.
    """
    mensual = s.P47T + s.ap_jub + s.ap_inssjp + s.ap_os + s.ganancias
    d = pd.DataFrame({"anio": anio, "trim": trim, "decil": s.decil.values, "grupo": s.grupo.values, "w": s.w.values,
                      "ing_anual": (12 * mensual).values,
                      "ganancias_anual": (12 * s.ganancias).values})
    d = d.sort_values("ing_anual", ascending=False, kind="stable")   # estable: hay empates en el corte
    return d[d.w.cumsum() <= FRACCION_COLA * s.w.sum()].round(1)


if __name__ == "__main__":
    P = Parametros()
    filas, colas, tramos = [], [], []
    t0 = time.time()
    for anio, trim in trimestres_disponibles():
        if anio < 2004:
            continue  # sin Cuentas Nacionales base 2004 ni año completo
        df = cargar_trimestre(anio, trim)
        s = simular(df, P, anio, trim)
        r = resumir_por_decil(s)
        colas.append(cola_alta(s, anio, trim))
        g = resumir_por_decil(s, "grupo")
        g.insert(0, "trim", trim)
        g.insert(0, "anio", anio)
        tramos.append(g)
        r.insert(0, "trim", trim)
        r.insert(0, "anio", anio)
        r["ponderador"] = df.attrs["ponderador"]
        r["aglomerados"] = df.AGLOMERADO.nunique()
        filas.append(r)
        tot = r.sum(numeric_only=True)
        print(f"{anio}T{trim} n={len(df):>6,} pob={tot.personas / 1e6:5.1f}M "
              f"aportes/ipcf={(tot.ap_jub + tot.ap_inssjp) / tot.ipcf:6.2%} "
              f"gan/ipcf={tot.ganancias / tot.ipcf:6.2%} contrib/ipcf={tot.contrib / tot.ipcf:6.2%} "
              f"reg/asal={tot.n_registrados / tot.n_asalariados:5.1%} "
              f"contrib.Gan={tot.n_ganancias / 1e3:7.0f}k  [{time.time() - t0:5.0f}s]", flush=True)
    out = pd.concat(filas, ignore_index=True)
    out.to_csv(PROCESSED / "eph_trimestral_decil.csv", index=False)
    print("OK ->", PROCESSED / "eph_trimestral_decil.csv")
    pd.concat(tramos, ignore_index=True).to_csv(PROCESSED / "eph_trimestral_tramos.csv", index=False)
    print("OK ->", PROCESSED / "eph_trimestral_tramos.csv")
    pd.concat(colas, ignore_index=True).to_csv(PROCESSED / "eph_cola_alta.csv.gz", index=False)
    print("OK ->", PROCESSED / "eph_cola_alta.csv.gz")
