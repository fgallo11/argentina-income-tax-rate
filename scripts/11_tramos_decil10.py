#!/usr/bin/env python
"""El decil 10 partido: percentiles 90-95, 95-99 y el 1% superior de la EPH.

Mismo orden (ingreso per cápita familiar), misma microsimulación y mismos supuestos que los
deciles; los deciles 1-9 no cambian. Ganancias faltante y Bienes Personales se reparten
entre los tramos con las declaraciones juradas (09_ingresos_altos.py). Es la versión A del
informe. El 1% se controla con el 1% armado sólo con las declaraciones juradas (10_top1.py, que
usa la columna consumo_sobre_ingreso de esta salida).

Variantes:
  principal               por encima del veintil más alto de la ENGHo el consumo queda fijo
  consumo_proporcional    por encima de ese veintil, consumo proporcional al ingreso
  ajuste_cn               ingresos ajustados a Cuentas Nacionales (como fig0)
  ajuste_cn_activos_ext   además, renta de activos externos (cota alta)
  sin_bienes_personales

Salidas (outputs/tables/):
  tasas_tramos_decil10_fig0.csv   los tramos con el ingreso completado (versión B del informe; panel B de fig0), con
                                  ingreso y personas (los usa 13_brecha_recaudacion.py).
  tasas_tramos_decil10_robustez.csv   los tramos con los demás supuestos (sección 8 del informe,
                                  "Qué tan firme es cada resultado").
  tasas_tramos_decil10.csv   variante, año, grupo (1-9, 91 = P90-95, 95 = P95-99, 99 = P99-100),
                             tasas por impuesto, participación en el ingreso y en los impuestos,
                             ingreso por persona en canastas básicas.
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from incidencia.config import PROCESSED, TABLES  # noqa: E402
from incidencia.incidencia import IMPUESTOS, Variante, promedio_anual  # noqa: E402
from incidencia.indirectos import cargar_insumos  # noqa: E402

VARIANTES = [
    Variante(),
    Variante("consumo_proporcional", extrapolar_consumo="proporcional"),
    Variante("ajuste_cn", ajuste_cn=True),
    Variante("ajuste_cn_activos_ext", ajuste_cn=True, renta_activos_ext=0.03),
    Variante("sin_bienes_personales", incluir_bp=False),
]
# Sólo para la versión B del informe y el panel B de fig0 (ingreso completado). Van a un archivo aparte para no cambiar
# los rangos que usan fig8, fig9 y el informe.
VARIANTES_FIG0 = [
    Variante("ajuste_cn_rentas", ajuste_cn=True, factor_rentas=7.0),
    Variante("ajuste_cn_rentas_activos_ext", ajuste_cn=True, factor_rentas=7.0, renta_activos_ext=0.03),
    Variante("ajuste_cn_rentas_cartera_ext", ajuste_cn=True, factor_rentas=7.0, renta_activos_ext=0.04,
             base_activos_ext="cartera"),
]
# Para la sección 8 del informe ("Qué tan firme es cada resultado"): los mismos supuestos que se prueban en los
# deciles, ahora también sobre los tramos. Archivo aparte para no cambiar las franjas de las
# figuras que usan tasas_tramos_decil10.csv.
VARIANTES_ROBUSTEZ = [
    Variante("contrib_100_trabajador", fraccion_contrib_trabajador=1.0),
    Variante("contrib_100_consumidor", fraccion_contrib_trabajador=0.0),
    Variante("iva_legal", iva_nivel_legal=True),
    Variante("con_cheque", incluir_cheque=True),
    Variante("con_cheque_y_combustibles", incluir_cheque=True, incluir_combustibles=True),
    Variante("con_monotributo", incluir_monotributo=True),
    Variante("altos_sin_corregir", altos_ingresos="no"),
    Variante("engho_escalonado", modo_engho="escalonado"),
    Variante("recursos_gasto", corregir_recursos=True),
]
NOMBRES = {0: "Población", 91: "P90-95", 95: "P95-99", 99: "1% (EPH)"} | {d: f"D{d}" for d in range(1, 10)}

if __name__ == "__main__":
    engho, rec = cargar_insumos()
    q = pd.read_csv(PROCESSED / "eph_trimestral_tramos.csv")
    cbt = pd.read_csv(PROCESSED / "deflactor.csv", index_col=0).cbt
    filas = []
    for v in VARIANTES:
        for anio, qa in q.groupby("anio"):
            p = promedio_anual(qa, anio, engho, rec.loc[anio], v)
            p.insert(0, "anio", anio)
            p.insert(0, "variante", v.nombre)
            filas.append(p)
    t = pd.concat(filas, ignore_index=True)
    t["grupo"] = t.pop("decil").astype(int)
    tot = t[t.grupo == 0].set_index(["variante", "anio"])
    imp = t.total * t.ingreso_total
    t["part_ingreso"] = t.ingreso_total / t.set_index(["variante", "anio"]).index.map(tot.ingreso_total)
    t["part_impuestos"] = imp / t.set_index(["variante", "anio"]).index.map(tot.total * tot.ingreso_total)
    t["canastas_por_persona"] = t.ingreso_total / t.personas / t.anio.map(cbt)
    # en la misma unidad que la canasta (por adulto equivalente, como mide el INDEC la pobreza)
    t["canastas_por_adulto_eq"] = t.ingreso_total / t.adulto_eq / t.anio.map(cbt)
    t["nombre"] = t.grupo.map(NOMBRES)
    cols = ["variante", "anio", "grupo", "nombre"] + IMPUESTOS + ["total", "directos", "indirectos", "part_ingreso",
                                                                   "part_impuestos", "canastas_por_persona", "canastas_por_adulto_eq",
                                                                   "gasto_sobre_ingreso_declarado", "consumo_sobre_ingreso",
                                                                   "trimestres"]
    t[cols].to_csv(TABLES / "tasas_tramos_decil10.csv", index=False)

    filas = []
    for v in VARIANTES_FIG0:
        for anio, qa in q.groupby("anio"):
            p = promedio_anual(qa, anio, engho, rec.loc[anio], v)
            p.insert(0, "anio", anio)
            p.insert(0, "variante", v.nombre)
            filas.append(p)
    f0 = pd.concat(filas, ignore_index=True)
    f0["grupo"] = f0.pop("decil").astype(int)
    f0[["variante", "anio", "grupo"] + IMPUESTOS + ["total", "ingreso_total", "personas"]].to_csv(TABLES / "tasas_tramos_decil10_fig0.csv",
                                                                      index=False)

    filas = []
    for v in VARIANTES_ROBUSTEZ:
        for anio, qa in q.groupby("anio"):
            p = promedio_anual(qa, anio, engho, rec.loc[anio], v)
            p.insert(0, "anio", anio)
            p.insert(0, "variante", v.nombre)
            filas.append(p)
    r = pd.concat(filas, ignore_index=True)
    r["grupo"] = r.pop("decil").astype(int)
    tot_r = r[r.grupo == 0].set_index(["variante", "anio"])
    clave = r.set_index(["variante", "anio"]).index
    r["part_ingreso"] = r.ingreso_total / clave.map(tot_r.ingreso_total)
    r["part_impuestos"] = r.total * r.ingreso_total / clave.map(tot_r.total * tot_r.ingreso_total)
    r["canastas_por_persona"] = r.ingreso_total / r.personas / r.anio.map(cbt)
    r[["variante", "anio", "grupo"] + IMPUESTOS + ["total", "part_ingreso", "part_impuestos", "canastas_por_persona",
                                                   "ingreso_total", "personas"]].to_csv(
        TABLES / "tasas_tramos_decil10_robustez.csv", index=False)

    pr = t[t.variante == "principal"].set_index(["anio", "grupo"])
    pd.set_option("display.width", 220)
    for a in (2017, 2024, 2025):
        x = pr.loc[a].copy()
        x.index = x.index.map(NOMBRES)
        print(f"\n=== {a}, principal ===")
        print(pd.DataFrame({"tasa %": x.total * 100, "directos": x.directos * 100, "indirectos": x.indirectos * 100,
                            "% ingreso": x.part_ingreso * 100, "% impuestos": x.part_impuestos * 100,
                            "canastas": x.canastas_por_persona, "gasto/ingreso": x.gasto_sobre_ingreso_declarado})
              .round(2).to_string())
    print("\n=== Tasa total por variante, tramos del decil 10 (%) ===")
    s = t[t.grupo.isin([1, 5, 91, 95, 99, 0])].pivot_table(index=["variante", "grupo"], columns="anio", values="total")
    print((s * 100).round(1)[[2004, 2008, 2012, 2016, 2020, 2024, 2025]].to_string())
