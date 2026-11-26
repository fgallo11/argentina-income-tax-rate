#!/usr/bin/env python
"""Cuánta plata está en juego: lo que cada grupo pagaría de más o de menos con un sistema
proporcional o uno progresivo que recaude lo mismo.

Para cada año y grupo (deciles 1-9, P90-95, P95-99 y el 1%):

  brecha del grupo = R × (parte que le tocaría de los impuestos − parte que paga hoy)

R es lo que se recaudó de verdad de los impuestos del estudio (Ganancias de personas, Bienes
Personales, aportes y contribuciones, IVA, Internos e Ingresos Brutos; DNIAF). Se usa R y no la
recaudación que reconstruye el modelo porque la encuesta capta menos ingreso y menos consumo que
Cuentas Nacionales: el modelo reproduce bien el reparto (las partes), no el nivel.

  proporcional: la parte que le tocaría es su parte del ingreso (todos pagan la tasa promedio).
  progresivo:   tasa = promedio × (ingreso por persona del grupo / promedio)^e, reescalada para
                recaudar lo mismo; e = 0,25 (como el informe y fig8), con 0,15 y 0,40 de sensibilidad.

Brecha positiva: el grupo pagaría más; negativa: pagaría menos. Suman cero en cada año: es el
mismo total repartido de otra manera. Como el sistema y la referencia recaudan lo mismo, la
brecha del 1% es también lo que se recaudaría de más si sólo el 1% pasara a la tasa de referencia
y nadie más cambiara.

Dos versiones, como en la sección 4 del informe: A (encuesta, variante principal) y B (ingreso
completado, ajuste_cn_rentas_cartera_ext). Cálculo mecánico: no supone cambios de comportamiento.

Salidas:
  outputs/tables/brecha_recaudacion.csv          versión, año, grupo: tasas, brechas en millones de
                                                 pesos, % del PIB, millones de US$ y US$ por persona.
Las figuras de los montos (16 y 17 del informe) las hace 14_informe_graficos.py con brechas().
"""
import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
_spec = importlib.util.spec_from_file_location("graficos_comunes", RAIZ / "scripts" / "12_graficos_comunes.py")
inf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(inf)       # estilo y colores del informe (no corre su main)
g, plt = inf.g, inf.plt
from incidencia.config import ANIO_FIN, TABLES  # noqa: E402
from incidencia.indirectos import cargar_insumos  # noqa: E402

GRUPOS = list(range(1, 10)) + [91, 95, 99]
NOMBRES = {d: f"D{d}" for d in range(1, 10)} | {91: "P90-95", 95: "P95-99", 99: "1%"}
VERSION_B = "ajuste_cn_rentas_cartera_ext"
ELASTICIDADES = (0.15, 0.25, 0.40)
# impuestos del estudio, recaudación real (millones de pesos)
RECAUDACION = ["ganancias_pf", "bienes_personales", "ss_empleados", "ss_empleadores", "iva",
               "internos_modelados", "ingresos_brutos"]


def cargar():
    """Ingreso, personas y tasa total por versión, año y grupo (0 = población)."""
    tr = pd.read_csv(TABLES / "tasas_tramos_decil10.csv")
    a = tr[tr.variante == "principal"].copy()
    # ingreso relativo: la tabla trae partes y canastas por persona; con eso alcanza
    a["ingreso"] = a.part_ingreso
    a["personas"] = a.part_ingreso / a.canastas_por_persona
    a["version"] = "A"
    f0 = pd.read_csv(TABLES / "tasas_tramos_decil10_fig0.csv")
    b = f0[f0.variante == VERSION_B].copy()
    b["ingreso"], b["version"] = b.ingreso_total, "B"
    cols = ["version", "anio", "grupo", "total", "ingreso", "personas"]
    return pd.concat([a[cols], b[cols]], ignore_index=True)


def brechas(d, rec):
    R = rec[RECAUDACION].sum(axis=1)
    filas = []
    for (ver, anio), x in d.groupby(["version", "anio"]):
        x = x.set_index("grupo")
        # partes sobre la suma de los grupos (el promedio anual de la población, grupo 0, es un
        # promedio de trimestres y difiere de la suma en milésimas)
        imp = x.total[GRUPOS] * x.ingreso[GRUPOS]
        sy = x.ingreso[GRUPOS] / x.ingreso[GRUPOS].sum()             # parte del ingreso
        st = imp / imp.sum()                                          # parte de los impuestos
        prom = imp.sum() / x.ingreso[GRUPOS].sum()
        yrel = sy / (x.personas[GRUPOS] / x.personas[GRUPOS].sum())   # ingreso por persona / promedio
        pers = x.personas[GRUPOS] / x.personas[GRUPOS].sum() * rec.loc[anio, "poblacion"]
        pib, tc = rec.loc[anio, "pib"], rec.loc[anio, "tc"]
        ref = {}
        for e in ELASTICIDADES:
            w = sy * yrel ** e
            ref[e] = w / w.sum()
        for k in GRUPOS:
            f = {"version": ver, "anio": anio, "grupo": k, "nombre": NOMBRES[k], "personas": pers[k],
                 "tasa": x.total[k], "tasa_promedio": prom, "tasa_progresiva": ref[0.25][k] / sy[k] * prom,
                 "recaudacion_pib": R[anio] / pib}
            for nom, parte in [("proporcional", sy[k])] + [(f"progresivo_e{int(e * 100):03d}", ref[e][k])
                                                           for e in ELASTICIDADES]:
                m = R[anio] * (parte - st[k])                             # millones de pesos
                f[f"{nom}_mill"] = m
                f[f"{nom}_pib"] = m / pib
                f[f"{nom}_musd"] = m / tc
                f[f"{nom}_usd_persona"] = m * 1e6 / tc / pers[k]
            filas.append(f)
    return pd.DataFrame(filas)


def u(v, d=1):
    return g.pct(v, d)



if __name__ == "__main__":
    _, rec = cargar_insumos()
    b = brechas(cargar(), rec)
    b.to_csv(TABLES / "brecha_recaudacion.csv", index=False)
    pd.set_option("display.width", 220)
    for v in ("A", "B"):
        x = b[(b.version == v) & (b.anio == ANIO_FIN)].set_index("nombre")
        print(f"\n=== {ANIO_FIN}, versión {v} ===")
        print(pd.DataFrame({"tasa": x.tasa * 100, "tasa prog": x.tasa_progresiva * 100,
                            "prop %PIB": x.proporcional_pib * 100, "prop MUSD": x.proporcional_musd,
                            "prog %PIB": x.progresivo_e025_pib * 100, "prog MUSD": x.progresivo_e025_musd,
                            "prog USD/pers": x.progresivo_e025_usd_persona}).round(2).to_string())
