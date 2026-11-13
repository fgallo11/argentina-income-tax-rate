#!/usr/bin/env python
"""Tasas efectivas por decil y año para la variante principal y las de sensibilidad.

Salidas (outputs/tables/):
  tasas_por_decil_anual.csv         formato largo: variante, año, decil, impuesto, tasa.
  tasas_por_decil_anual_ancho.csv   variante principal, una columna por impuesto.
  serie_total_anual.csv             total, directos e indirectos: promedio, D1, D5, D10.
  rango_por_decil_anual.csv         mínimo y máximo de la tasa total entre variantes.

Las variantes están definidas en src/incidencia/incidencia.py (VARIANTES).
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from incidencia.config import ANIOS_ADVERTENCIA_INDEC, PROCESSED, TABLES  # noqa: E402
from incidencia.incidencia import IMPUESTOS, VARIANTES, promedio_anual  # noqa: E402
from incidencia.indirectos import cargar_insumos  # noqa: E402

MEDIDAS = IMPUESTOS + ["total", "directos", "indirectos"]

if __name__ == "__main__":
    engho, rec = cargar_insumos()
    q = pd.read_csv(PROCESSED / "eph_trimestral_decil.csv")
    filas = []
    for v in VARIANTES:
        for anio, qa in q.groupby("anio"):
            p = promedio_anual(qa, anio, engho, rec.loc[anio], v)
            p.insert(0, "anio", anio)
            p.insert(0, "variante", v.nombre)
            p["advertencia_indec"] = anio in ANIOS_ADVERTENCIA_INDEC
            filas.append(p)
    ancho = pd.concat(filas, ignore_index=True)
    ancho["decil"] = ancho.decil.astype(int)

    ids = ["variante", "anio", "decil", "trimestres", "advertencia_indec"]
    ancho.melt(id_vars=ids, value_vars=MEDIDAS, var_name="impuesto", value_name="tasa").to_csv(
        TABLES / "tasas_por_decil_anual.csv", index=False)
    princ = ancho[ancho.variante == "principal"].drop(columns="variante")
    princ.to_csv(TABLES / "tasas_por_decil_anual_ancho.csv", index=False)

    serie = ancho[ancho.decil.isin([0, 1, 5, 10])].pivot_table(
        index=["variante", "anio", "trimestres"], columns="decil", values=["total", "directos", "indirectos"])
    serie.columns = [f"{m}_{'poblacion' if d == 0 else 'D' + str(d)}" for m, d in serie.columns]
    serie.reset_index().to_csv(TABLES / "serie_total_anual.csv", index=False)

    # El rango cubre supuestos sobre la misma medida de recursos. Se excluyen la lectura
    # contra consumo y las ajustadas a Cuentas Nacionales (otras medidas de ingreso) y el "techo" de ingresos altos, que implica
    # una alícuota de Ganancias imposible sobre el ingreso faltante (docs/auditoria.md, 3.4).
    fuera = {"sobre_consumo", "altos_registros", "ajuste_cn", "ajuste_cn_activos_ext", "ajuste_cn_rentas",
             "ajuste_cn_rentas_activos_ext", "con_cheque", "con_cheque_y_combustibles"}
    rango = ancho[~ancho.variante.isin(fuera)].groupby(["anio", "decil"]).total.agg(["min", "max"]).reset_index()
    rango = rango.merge(princ[["anio", "decil", "total"]], on=["anio", "decil"]).rename(
        columns={"total": "principal", "min": "minimo_variantes", "max": "maximo_variantes"})
    rango.to_csv(TABLES / "rango_por_decil_anual.csv", index=False)

    pd.set_option("display.width", 250)
    for a in (2004, 2014, 2024):
        print(f"\n=== {a} — principal (% del ingreso) ===")
        print((princ[princ.anio == a].set_index("decil")[IMPUESTOS + ["total", "gasto_sobre_ingreso_declarado"]]
               * [100] * 9 + [1]).round(1).to_string() if False else
              (princ[princ.anio == a].set_index("decil")[IMPUESTOS + ["total"]] * 100).round(1)
              .join(princ[princ.anio == a].set_index("decil").gasto_sobre_ingreso_declarado.round(2)).to_string())
    s = ancho[ancho.decil.isin([0, 1, 5, 10])].pivot_table(index=["variante", "decil"], columns="anio", values="total")
    print("\n=== Tasa total por variante ===")
    print((s * 100).round(1)[[2004, 2007, 2011, 2012, 2015, 2017, 2019, 2021, 2024]].to_string())
