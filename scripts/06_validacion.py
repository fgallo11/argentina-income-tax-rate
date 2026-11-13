#!/usr/bin/env python
"""Validación contra agregados oficiales. Reporta las discrepancias tal como salen.

Tablas (outputs/tables/):
  validacion_directos.csv    impuestos directos simulados vs recaudación DNIAF.
  validacion_iva.csv         IVA legal teórico sobre el consumo vs IVA recaudado.
  validacion_cobertura.csv   consumo e ingreso de encuesta vs Cuentas Nacionales, y qué
                             parte de la recaudación total cubren los impuestos incluidos.

Lectura de los cocientes "simulado / recaudado":
  - *_eph: simulación sólo para la población de los aglomerados EPH (~60-65% del país).
  - *_nac: la misma simulación expandida a la población total del país suponiendo igual
    promedio per cápita fuera de los aglomerados (cota superior: el resto es más pobre e
    informal).
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from incidencia.config import PROCESSED, TABLES  # noqa: E402
from incidencia.indirectos import cargar_insumos, perfil_consumo, tasas_indirectas  # noqa: E402

M = 1e6

if __name__ == "__main__":
    engho, rec = cargar_insumos()
    q = pd.read_csv(PROCESSED / "eph_trimestral_decil.csv")
    # promedio anual de los totales mensuales por decil
    qa = q.groupby(["anio", "decil"]).mean(numeric_only=True).reset_index()
    a = qa.groupby("anio").sum(numeric_only=True)
    rec = rec.loc[a.index]
    f = rec.poblacion / a.personas

    d = pd.DataFrame(index=a.index)
    d["poblacion_eph_sobre_pais"] = 1 / f
    for nombre, sim, col in (
        ("aportes", (a.ap_jub + a.ap_inssjp) * 12 / M, "ss_empleados"),
        ("contribuciones", a.contrib * 12 / M, "ss_empleadores"),
        ("ganancias", a.ganancias * 12 / M, "ganancias_pf"),
    ):
        d[f"{nombre}_sim_eph_mill"] = sim
        d[f"{nombre}_recaudado_mill"] = rec[col]
        d[f"{nombre}_ratio_eph"] = sim / rec[col]
        d[f"{nombre}_ratio_nac"] = sim * f / rec[col]
    d["aportes_sin_afjp_ratio_nac"] = (a.ap_jub + a.ap_inssjp - a.ap_jub_afjp) * 12 / M * f / rec.ss_empleados
    d["contribuyentes_ganancias_eph_miles"] = a.n_ganancias / 1e3
    d["asalariados_registrados_eph_millones"] = a.n_registrados / 1e6
    d.round(4).to_csv(TABLES / "validacion_directos.csv")

    iva, cob = [], []
    for anio in a.index:
        r = rec.loc[anio]
        qd = qa[qa.anio == anio].set_index("decil")
        media = qd.ipcf.sum() / qd.personas.sum()
        perfil = perfil_consumo(anio, (qd.ipcf / qd.personas / media).values, engho)
        cons_d = perfil.consumo_rel.values * media * qd.personas.values
        legal = tasas_indirectas(perfil, cons_d, r).attrs["iva_legal_medio"]
        consumo = cons_d.sum() * 12 / M      # universo EPH, anual
        iva.append({"anio": anio,
                    "iva_legal_medio_sobre_gasto": legal,
                    "iva_recaudado_sobre_consumo_privado": r.iva / r.consumo_privado,
                    "recaudado_sobre_legal": r.iva / r.consumo_privado / legal})
        incl = (r.ganancias_pf + r.bienes_personales + r.iva + r.internos_modelados + r.ss_empleados
                + r.ss_empleadores + r.ingresos_brutos)
        cob.append({"anio": anio,
                    "consumo_encuesta_expandido_sobre_cn": consumo * f[anio] / r.consumo_privado,
                    "ingreso_eph_expandido_sobre_pib": a.loc[anio, "ipcf"] * 12 / M * f[anio] / r.pib,
                    "impuestos_incluidos_sobre_recaudacion_total": incl / r.recaudacion_neta_total,
                    "impuestos_incluidos_pct_pib": incl / r.pib,
                    "derechos_exportacion_pct_pib": r.derechos_exportacion / r.pib})
    iva = pd.DataFrame(iva).set_index("anio")
    cob = pd.DataFrame(cob).set_index("anio")
    iva.round(4).to_csv(TABLES / "validacion_iva.csv")
    cob.round(4).to_csv(TABLES / "validacion_cobertura.csv")

    pd.set_option("display.width", 250)
    print("== Directos: simulado / recaudado ==")
    print(d[[c for c in d.columns if "ratio" in c] + ["contribuyentes_ganancias_eph_miles"]].round(2).to_string())
    print("\n== IVA ==")
    print(iva.round(3).to_string())
    print("\n== Cobertura ==")
    print(cob.round(3).to_string())
