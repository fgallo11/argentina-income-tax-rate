#!/usr/bin/env python
"""Corrección de ingresos altos: compara la cola superior de la EPH con las declaraciones
juradas de Ganancias de personas humanas (anuarios de ARCA) y con la recaudación oficial.

Para cada año:
  1. Ingreso faltante. Se ordenan los tramos de las declaraciones de mayor a menor y se
     acumulan casos (n) e ingreso declarado (resultado neto: ingresos gravados menos gastos,
     antes de deducciones personales). Para cada n se calcula el ingreso de las n personas
     de mayor ingreso de la EPH expandida al total del país. El ingreso faltante es la
     mayor diferencia positiva entre ambas curvas (punto de empalme n*).
     Es una cota inferior: los tramos están ordenados por ingresos brutos, no por ingreso
     neto, y lo declarado al fisco también puede estar subdeclarado.
  2. Ganancias faltante = recaudación oficial de Ganancias de personas humanas menos la
     simulada sobre la EPH expandida al país.
  3. Reparto entre deciles: según el decil del hogar de las n* personas de mayor ingreso
     individual de la EPH (ponderado por su ingreso).
  4. Bienes Personales: recaudación oficial, repartida con las mismas proporciones.
  También se reparte la parte del decil 10 entre sus tramos (parte_d91: percentiles 90-95,
  parte_d95: 95-99, parte_d99: el 1% superior), según el tramo del hogar de esas personas.

El año fiscal 2025 todavía no está publicado (el anuario 2025 de ARCA informa el año fiscal
2024): se usan las declaraciones de 2024 llevadas a 2025 por la variación del ingreso medio de
la EPH (marcado como extrapolado).

Salida: data/processed/ajuste_altos_ingresos.csv (millones de pesos anuales, total país).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from incidencia.config import PROCESSED, TABLES  # noqa: E402

M = 1e6
GRUPOS_D10 = [91, 95, 99]   # tramos del decil 10 (04_microsimulacion_eph.py)


def curva_ddjj(d: pd.DataFrame, col: str, escala: float = 1.0) -> pd.DataFrame:
    d = d.sort_values("desde", ascending=False)
    return pd.DataFrame({"n": d.casos.cumsum().values, "ingreso": d[col].cumsum().values * escala,
                         "impuesto": d.impuesto.cumsum().values * escala,
                         "patrimonio": d.patrimonio_neto.cumsum().values * escala})


if __name__ == "__main__":
    rec = pd.read_csv(PROCESSED / "recaudacion_macro.csv", index_col=0)
    q = pd.read_csv(PROCESSED / "eph_trimestral_decil.csv")
    cola = pd.read_csv(PROCESSED / "eph_cola_alta.csv.gz")
    ddjj = pd.read_csv(PROCESSED / "ddjj_ganancias_tramos.csv")
    ddjj = ddjj[~ddjj.es_total]
    qt = q.groupby(["anio", "trim"]).sum(numeric_only=True)
    qa = q.groupby(["anio", "decil"]).mean(numeric_only=True).groupby("anio").sum()
    media_eph = qa.ipcf / qa.personas

    filas = []
    for anio in sorted(q.anio.unique()):
        fiscal = min(anio, int(ddjj.anio_fiscal.max()))
        escala = media_eph[anio] / media_eph[fiscal]                 # 1 salvo año extrapolado
        c = curva_ddjj(ddjj[ddjj.anio_fiscal == fiscal], "resultado_neto", escala)
        ca = cola[cola.anio == anio]
        eph_ing, eph_dec, eph_grp = [], [], []
        for trim, t in ca.groupby("trim"):
            f = rec.poblacion[anio] / qt.personas[(anio, trim)]      # expansión al total del país
            t = t.sort_values("ing_anual", ascending=False, kind="stable")
            n_ac, y = (t.w * f).cumsum().values, (t.w * f * t.ing_anual).values
            eph_ing.append(np.interp(c.n, n_ac, y.cumsum(), right=np.nan))
            # ingreso acumulado por decil del hogar en cada punto n
            eph_dec.append(np.column_stack([np.interp(c.n, n_ac, np.where(t.decil == d, y, 0).cumsum(), right=np.nan)
                                            for d in range(1, 11)]))
            # lo mismo con el decil 10 partido en tramos (91: P90-95, 95: P95-99, 99: P99-100)
            eph_grp.append(np.column_stack([np.interp(c.n, n_ac, np.where(t.grupo == g, y, 0).cumsum(), right=np.nan)
                                            for g in GRUPOS_D10]))
        c["eph"] = np.mean(eph_ing, axis=0)
        c["dif"] = c.ingreso - c.eph
        dec = np.mean(eph_dec, axis=0)
        k = int(c.dif.idxmax()) if c.dif.notna().any() else 0
        faltante = max(float(c.dif[k]), 0.0) if c.dif.notna().any() else 0.0
        partes = dec[k] / dec[k].sum()
        grp = np.mean(eph_grp, axis=0)[k]
        partes_grp = grp / grp.sum() * partes[9]          # el decil 10 repartido entre sus tramos
        f_anual = rec.poblacion[anio] / qa.personas[anio]
        gan_sim = qa.ganancias[anio] * 12 * f_anual
        fila = {
            "anio": anio, "anio_fiscal_ddjj": fiscal, "extrapolado": fiscal != anio,
            "n_empalme": c.n[k], "n_empalme_sobre_poblacion": c.n[k] / rec.poblacion[anio],
            "ingreso_ddjj_empalme_mill": c.ingreso[k] / M, "ingreso_eph_empalme_mill": c.eph[k] / M,
            "ingreso_faltante_mill": faltante / M,
            "ingreso_eph_total_mill": qa.ipcf[anio] * 12 * f_anual / M,
            "ganancias_recaudada_mill": rec.ganancias_pf[anio], "ganancias_simulada_mill": gan_sim / M,
            "ganancias_faltante_mill": max(rec.ganancias_pf[anio] - gan_sim / M, 0.0),
            "impuesto_ddjj_total_mill": c.impuesto.iloc[-1] / M,
            "impuesto_ddjj_empalme_sobre_total": c.impuesto[k] / c.impuesto.iloc[-1],
            "patrimonio_ddjj_empalme_sobre_total": c.patrimonio[k] / c.patrimonio.iloc[-1],
            "bienes_personales_mill": rec.bienes_personales[anio],
        }
        fila |= {f"parte_d{d}": partes[d - 1] for d in range(1, 11)}
        fila |= {f"parte_d{g}": partes_grp[i] for i, g in enumerate(GRUPOS_D10)}
        filas.append(fila)
    out = pd.DataFrame(filas).set_index("anio")
    out.to_csv(PROCESSED / "ajuste_altos_ingresos.csv")
    out.round(4).to_csv(TABLES / "ajuste_altos_ingresos.csv")
    r = out.assign(falt_sobre_eph=out.ingreso_faltante_mill / out.ingreso_eph_total_mill,
                   gan_sim_sobre_rec=out.ganancias_simulada_mill / out.ganancias_recaudada_mill,
                   tasa_marginal=out.ganancias_faltante_mill / out.ingreso_faltante_mill,
                   ddjj_sobre_eph=out.ingreso_ddjj_empalme_mill / out.ingreso_eph_empalme_mill)
    print(r[["n_empalme", "n_empalme_sobre_poblacion", "ddjj_sobre_eph", "falt_sobre_eph", "gan_sim_sobre_rec",
             "tasa_marginal", "impuesto_ddjj_empalme_sobre_total", "parte_d8", "parte_d9", "parte_d10"]].round(3).to_string())
