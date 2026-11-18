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
                recaudar lo mismo; e = 0,25 (como fig8 e i9), con 0,15 y 0,40 de sensibilidad.

Brecha positiva: el grupo pagaría más; negativa: pagaría menos. Suman cero en cada año: es el
mismo total repartido de otra manera. Como el sistema y la referencia recaudan lo mismo, la
brecha del 1% es también lo que se recaudaría de más si sólo el 1% pasara a la tasa de referencia
y nadie más cambiara.

Dos versiones, como en la sección 3 del informe: A (encuesta, variante principal) y B (ingreso
completado, ajuste_cn_rentas_cartera_ext). Cálculo mecánico: no supone cambios de comportamiento.

Salidas:
  outputs/tables/brecha_recaudacion.csv          versión, año, grupo: tasas, brechas en millones de
                                                 pesos, % del PIB, millones de US$ y US$ por persona.
  outputs/figures/informe/i10_brecha_grupos.png  2025 (B): brecha de cada grupo en US$.
  outputs/figures/informe/i11_brecha_1pct.png    el 1%: tasa que paga, promedio y progresiva, 2004-2025.
"""
import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
_spec = importlib.util.spec_from_file_location("informe", RAIZ / "scripts" / "12_informe_graficos.py")
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


def fig_grupos(b):
    """i10: 2025, versión B, cuánto más o menos pagaría cada grupo, en miles de millones de US$."""
    x = b[(b.version == "B") & (b.anio == ANIO_FIN)].set_index("grupo").loc[GRUPOS]
    fig, ax = plt.subplots(figsize=(13, 6))
    xs, w = np.arange(len(GRUPOS)), 0.38
    series = [(-w / 2, "proporcional", inf.GRIS, f"si fuera proporcional: todos pagan el promedio ({u(x.tasa_promedio.iloc[0] * 100)}%)"),
              (w / 2, "progresivo_e025", inf.OSCURO, "si fuera progresivo: la tasa sube con el ingreso")]
    for off, col, color, nombre in series:
        v = x[f"{col}_musd"] / 1000
        ax.bar(xs + off, v, w, color=color, label=nombre, zorder=3)
        for xi, vi in zip(xs + off, v):
            ax.text(xi, vi + (0.2 if vi >= 0 else -0.2), ("+" if vi >= 0 else "−") + u(abs(vi)), ha="center",
                    va="bottom" if vi >= 0 else "top", fontsize=8, color=color)
    ax.axhline(0, color=g.TINTA, lw=0.9, zorder=4)
    ax.set_xticks(xs, [f"{NOMBRES[k]}\n{u(x.tasa[k] * 100)}%" for k in GRUPOS])
    ax.set_ylabel("miles de millones de US$ por año")
    ax.xaxis.grid(False)
    ax.legend(frameon=False, loc="upper left", fontsize=9.5)
    ax.set_title(f"{ANIO_FIN}: cuánto más (+) o menos (−) pagaría cada grupo si el sistema fuera otro, recaudando lo mismo",
                 loc="left", fontsize=12, fontweight="bold", pad=30)
    ax.text(0, 1.02, "Abajo de cada grupo, la tasa que paga hoy. Ingreso completado (versión B). Lo que suben unos lo bajan "
            "otros: cada color suma cero.", transform=ax.transAxes, fontsize=9.3, color=g.TINTA2)
    fig.text(0.01, -0.03, inf.NOTA + "\nBrecha = recaudación real de esos impuestos × (parte que le tocaría − parte que paga). "
             "Dólares al tipo de cambio oficial promedio del año. Cálculo mecánico, sin cambios de comportamiento. "
             "Tabla: outputs/tables/brecha_recaudacion.csv.", fontsize=7.2, color=g.MUDO, va="top")
    inf.guardar(fig, "i10_brecha_grupos")


def fig_1pct(b):
    """i11: el 1% (versión B): tasa que paga, la promedio (proporcional) y la progresiva."""
    x = b[(b.version == "B") & (b.grupo == 99)].set_index("anio")
    t, p, q = x.tasa * 100, x.tasa_promedio * 100, x.tasa_progresiva * 100
    fig, ax = plt.subplots(figsize=(12, 6.4))
    ax.fill_between(x.index, np.maximum(t, p), q, color=inf.OSCURO, alpha=0.09, lw=0)
    ax.fill_between(x.index, t, p, where=t < p, interpolate=True, color=inf.ROJO, alpha=0.22, lw=0)
    ax.plot(x.index, q, color=inf.OSCURO, lw=2.2)
    ax.plot(x.index, p, color=inf.GRIS, lw=2.2)
    ax.plot(x.index, t, color=inf.ROJO, lw=3)
    a = ANIO_FIN
    ax.text(a + 0.25, q[a], "Lo que pagaría\ncon un sistema progresivo", color=inf.OSCURO, va="center", fontsize=10)
    ax.text(a + 0.25, p[a] + 0.9, "Lo que paga el promedio\n(= sistema proporcional)", color=inf.GRIS, va="center", fontsize=10)
    ax.text(a + 0.25, t[a] - 0.9, "Lo que paga hoy el 1%", color=inf.ROJO, va="center", fontsize=10.5, fontweight="bold")
    m_prop, m_prog = x.proporcional_musd[a] / 1000, x.progresivo_e025_musd[a] / 1000
    ax.annotate("", xy=(a, p[a]), xytext=(a, t[a]), arrowprops=dict(arrowstyle="<->", color=inf.ROJO, lw=1.4))
    ax.annotate("", xy=(a, q[a]), xytext=(a, p[a]), arrowprops=dict(arrowstyle="<->", color=inf.OSCURO, lw=1.4))
    caja = dict(fc="white", ec="none", pad=1.5)
    ax.text(a - 0.2, (t[a] + p[a]) / 2, f"+US${u(m_prop)} mil M/año", ha="right", va="center", fontsize=9.5,
            color=inf.ROJO, fontweight="bold", bbox=caja)
    ax.text(a - 0.2, (p[a] + q[a]) / 2 + 2.6, f"+US${u(m_prog - m_prop)} mil M/año más\n(US${u(m_prog)} mil M en total)",
            ha="right", va="center", fontsize=9.5, color=inf.OSCURO, fontweight="bold", bbox=caja)
    ax.text(2011, 35.0, "2009-2013: el 1% paga\nmás que el promedio", fontsize=9, color=g.TINTA2, ha="center")
    ax.text(2021, 37.3, "2020-2022:\ntambién", fontsize=9, color=g.TINTA2, ha="center")
    ax.text(2014.5, 17.3, "Zona roja: años en que el 1% paga menos que el promedio", fontsize=9, color=inf.ROJO, ha="center")
    ax.set_xlim(2003.5, a + 5.5)
    ax.set_ylim(16, 47)
    ax.set_xticks(range(2004, a + 1, 3))
    ax.xaxis.grid(False)
    ax.set_ylabel("impuestos como % del ingreso")
    ax.set_title("El 1% más rico: cuánto paga y cuánto pagaría con otro sistema", loc="left", fontsize=13,
                 fontweight="bold", pad=34)
    ax.text(0, 1.02, "Cada línea es una tasa: qué parte de su ingreso paga en impuestos. La distancia entre la roja y las "
            "otras es lo que el 1% paga de menos.\nLa recaudación total no cambia: lo que pagaría de más el 1% lo pagarían "
            "de menos los deciles 1 a 9.", transform=ax.transAxes, fontsize=9.5, color=g.TINTA2)
    xa = b[(b.version == "A") & (b.grupo == 99) & (b.anio == a)].iloc[0]
    fig.text(0.01, -0.02, f"Ingreso completado (versión B). Con la encuesta sola (A) el 1% paga {u(xa.tasa * 100)}% en {a} y las "
             f"brechas son US${u(xa.proporcional_musd / 1000)} y US${u(xa.progresivo_e025_musd / 1000)} mil millones. "
             f"Dólares al tipo de cambio oficial promedio del año.\nProgresivo: la tasa crece con el ingreso por persona "
             f"(elasticidad 0,25), con la misma recaudación. Cálculo mecánico: no supone cambios de comportamiento. "
             f"Tabla: outputs/tables/brecha_recaudacion.csv.", fontsize=7.6, color=g.MUDO, va="top")
    inf.guardar(fig, "i11_brecha_1pct")


if __name__ == "__main__":
    _, rec = cargar_insumos()
    b = brechas(cargar(), rec)
    b.to_csv(TABLES / "brecha_recaudacion.csv", index=False)
    fig_grupos(b)
    fig_1pct(b)
    pd.set_option("display.width", 220)
    for v in ("A", "B"):
        x = b[(b.version == v) & (b.anio == ANIO_FIN)].set_index("nombre")
        print(f"\n=== {ANIO_FIN}, versión {v} ===")
        print(pd.DataFrame({"tasa": x.tasa * 100, "tasa prog": x.tasa_progresiva * 100,
                            "prop %PIB": x.proporcional_pib * 100, "prop MUSD": x.proporcional_musd,
                            "prog %PIB": x.progresivo_e025_pib * 100, "prog MUSD": x.progresivo_e025_musd,
                            "prog USD/pers": x.progresivo_e025_usd_persona}).round(2).to_string())
