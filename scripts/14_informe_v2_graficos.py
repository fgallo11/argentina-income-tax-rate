#!/usr/bin/env python
"""Gráficos del informe nuevo (docs/informe_v2.md), numerados en el orden en que aparecen.

Salida: outputs/figures/informe_v2/f01_... a f18_... (PNG y SVG). Todo sale de las tablas de
outputs/tables/ (no corre la microsimulación). Reutiliza el estilo y varias figuras de
07_graficos.py, 12_informe_graficos.py y 13_brecha_recaudacion.py; las nuevas están acá.

Medida usada desde la sección 5: versión A (variante "principal": ingreso declarado en la
encuesta, completado arriba con lo que se declara al fisco). La versión B (ingreso completado
con estimaciones) se muestra sólo en la figura 9.

  f01  comparación con Argendata y el Tax Observatory (= c1 del informe actual)
  f02  2025: tasa de cada decil, por impuesto
  f03  lo mismo en los años de cambio de gobierno
  f04  composición en el tiempo: deciles 1, 4, 7 y 10
  f05  ingreso de cada grupo en canastas básicas, 2004 y 2025 (= c2)
  f06  ingreso de cada decil en canastas, 2004-2025, con la línea de pobreza y el límite de la clase alta
  f07  parte del ingreso total de cada grupo, 2025
  f08  versión A, 2025: deciles y el decil 10 partido
  f09  versión B, 2025: lo mismo con el ingreso completado
  f10  composición en el tiempo: deciles 1, 5 y 10 y el 1% (= i6)
  f11  años de cambio de gobierno, con el decil 10 partido
  f12  matrices frente a un sistema proporcional y uno progresivo (= i9)
  f13  índice de Kakwani, con el de un sistema progresivo de referencia
  f14  tasa de cada grupo menos el promedio (= i4)
  f15  cuánta plata: brecha de cada grupo, 2025 (versión A)
  f16  el 1% frente a las dos referencias, 2004-2025 (versión A)
  f17  2025: parte de los impuestos frente a las dos referencias, por grupo
  f18  cuántas veces más ingresan y cuántas veces más pagan los de arriba que el decil 1
"""
import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))


def _modulo(nombre, archivo):
    spec = importlib.util.spec_from_file_location(nombre, RAIZ / "scripts" / archivo)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


inf = _modulo("informe", "12_informe_graficos.py")
bre = _modulo("brecha", "13_brecha_recaudacion.py")
g, plt, matplotlib = inf.g, inf.plt, inf.matplotlib
from incidencia.config import ANIO_FIN, TABLES  # noqa: E402

OUT = g.FIGURES / "informe_v2"
pct, TINTA, TINTA2, MUDO, SUP = g.pct, g.TINTA, g.TINTA2, g.MUDO, g.SUP
ROJO, AZUL, OSCURO, GRIS, MEDIO = inf.ROJO, inf.AZUL, inf.OSCURO, inf.GRIS, inf.MEDIO
# años de cambio de gobierno: los mandatos empiezan el 10 de diciembre, así que el último año de
# uno es el punto de partida del siguiente. 2004: primer año de la serie; ANIO_FIN: último dato.
ANIOS_GOBIERNO = [2004, 2007, 2011, 2015, 2019, 2023, ANIO_FIN]
GOBIERNO = {2004: "inicio de la serie", 2007: "fin de N. Kirchner", 2011: "fin de C. Fernández (1)",
            2015: "fin de C. Fernández (2)", 2019: "fin de M. Macri", 2023: "fin de A. Fernández",
            ANIO_FIN: "último dato (J. Milei)"}
POB = {k: 0.1 for k in range(1, 10)} | {91: 0.05, 95: 0.04, 99: 0.01}
GRUPOS = list(range(1, 10)) + [91, 95, 99]
NOMBRES = {k: f"D{k}" for k in range(1, 10)} | {91: "P90-95", 95: "P95-99", 99: "1%"}
FUENTE = ("Fuente: elaboración propia con EPH y ENGHo (INDEC), recaudación DNIAF (Ministerio de Economía), anuarios "
          "de ARCA y normativa. Aglomerados urbanos de la EPH; personas ordenadas por ingreso per cápita familiar.")
VERSION_B = "ajuste_cn_rentas_cartera_ext"


def guardar(fig, nombre):
    g.guardar(fig, nombre, OUT)


def reusar(modulo, funcion, nombre, *args, **kw):
    """Corre una figura de otro script guardándola acá con otro nombre."""
    previo = modulo.guardar
    modulo.guardar = lambda fig, _n: guardar(fig, nombre)
    try:
        return funcion(*args, **kw)
    finally:
        modulo.guardar = previo


def leyenda_impuestos(destino, **kw):
    h = [g.Patch(facecolor=c, label=n.replace(" (imputado a ingresos altos)", ""),
                 hatch="////" if col == "bienes_personales" else None, edgecolor=SUP)
         for col, n, c in g.IMPUESTOS][::-1]
    return destino.legend(handles=h, frameon=False, **kw)


def tabla_deciles(largo, anio, variante="principal"):
    v = largo[(largo.anio == anio) & (largo.variante == variante)]
    return v.pivot(index="decil", columns="impuesto", values="tasa") * 100


def tabla_tramos(tramos, anio, variante="principal"):
    v = tramos[(tramos.anio == anio) & (tramos.variante == variante)]
    return v.set_index("grupo")


# ---------------------------------------------------------------- sección 2
def panel_deciles(ax, largo, anio, titulo=None, etiquetas=True, fs=9):
    t = tabla_deciles(largo, anio)
    g.barras(ax, t.loc[1:10, g.COLS], etiquetas=etiquetas)
    if not etiquetas:
        for xi, b in enumerate(t.loc[1:10, "total"]):
            ax.text(xi, b + 0.4, pct(b), ha="center", va="bottom", fontsize=fs, color=TINTA, zorder=5)
    prom = t.loc[0, "total"]
    ax.axhline(prom, color=TINTA2, linewidth=1.1, linestyle=(0, (4, 3)), zorder=0.5)
    ax.set_xlim(-0.6, 9.6)
    if titulo:
        ax.set_title(titulo, loc="left", fontsize=11.5, fontweight="bold")
    return prom


def f02_deciles(largo):
    a = ANIO_FIN
    fig, ax = plt.subplots(figsize=(12.5, 6.2))
    prom = panel_deciles(ax, largo, a)
    ax.set_ylim(0, 34)
    ax.set_ylabel("Impuestos, % del ingreso")
    ax.set_xticklabels([f"D{i}" for i in range(1, 11)])
    ax.set_xlabel("Deciles: la población ordenada por ingreso per cápita familiar y dividida en diez grupos iguales "
                  "(D1, el 10% de menores ingresos)", fontsize=9)
    leyenda_impuestos(fig, loc="center left", bbox_to_anchor=(0.86, 0.55), fontsize=9)
    fig.subplots_adjust(right=0.85)
    fig.suptitle(f"Qué parte de su ingreso pagó cada decil en impuestos, {a}", x=0.01, y=1.02, ha="left",
                 fontsize=14, fontweight="bold")
    fig.text(0.01, 0.965, "Cada barra es la tasa efectiva del decil: lo que pagó en impuestos dividido por su ingreso. "
             "Los colores separan los impuestos. Línea punteada: tasa de toda la población "
             f"({pct(prom)}%).", fontsize=9.4,
             color=TINTA2, va="top")
    fig.text(0.01, -0.03, FUENTE + "\nIngreso: declarado en la encuesta, antes de impuestos directos, completado en la "
             "cima con el ingreso declarado a ARCA que la encuesta no capta.", fontsize=7.3, color=MUDO, va="top")
    guardar(fig, "f02_deciles_2025")


def grilla_anios(dibujar, nombre, titulo, sub, alto=10.5, ymax=45):
    """7 años de cambio de gobierno en una grilla de 2 × 4; la última celda lleva la leyenda."""
    fig, axs = plt.subplots(2, 4, figsize=(22, alto), sharey=True)
    for ax, a in zip(axs.flat, ANIOS_GOBIERNO):
        prom = dibujar(ax, a)
        ax.set_title(str(a), loc="left", fontsize=13, fontweight="bold")
        ax.set_title(f"{GOBIERNO[a]} · promedio {pct(prom)}%", loc="right", fontsize=8.6, color=TINTA2)
    ult = axs.flat[-1]
    ult.axis("off")
    leyenda_impuestos(ult, loc="center", fontsize=10)
    for ax in axs[:, 0]:
        ax.set_ylabel("Impuestos, % del ingreso")
    axs[0, 0].set_ylim(0, ymax)
    fig.suptitle(titulo, x=0.01, y=1.0, ha="left", fontsize=14, fontweight="bold")
    fig.text(0.01, 0.965, sub, fontsize=9.4, color=TINTA2, va="top")
    fig.subplots_adjust(left=0.04, right=0.995, wspace=0.06, hspace=0.32, top=0.89)
    fig.text(0.01, 0.02, FUENTE + " Línea punteada: tasa promedio de la población de ese año.", fontsize=7.3,
             color=MUDO, va="top")
    guardar(fig, nombre)


def f03_anios(largo):
    def dibujar(ax, a):
        prom = panel_deciles(ax, largo, a, etiquetas=False, fs=8.4)
        ax.set_xticklabels([f"D{i}" for i in range(1, 11)], fontsize=8.6)
        return prom
    grilla_anios(dibujar, "f03_deciles_anios_gobierno",
                 "Qué parte de su ingreso pagó cada decil, en los años de cambio de gobierno",
                 "Mismo cálculo que la figura anterior. Los mandatos empiezan el 10 de diciembre: el último año de un "
                 "gobierno es también el punto de partida del siguiente.")


def f04_composicion(ancho):
    pr = ancho.set_index(["anio", "decil"])
    paneles = [(f"Decil {k}" + (" (más pobre)" if k == 1 else " (más rico)" if k == 10 else ""),
                pr.xs(k, level="decil")) for k in (1, 4, 7, 10)]
    reusar(inf, inf.composicion, "f04_composicion_deciles", paneles, "f04",
           "Con qué impuestos paga cada decil, año por año",
           "Cada panel apila, año por año, los puntos de ingreso que el decil paga en cada impuesto. La línea negra "
           "es el total. Arriba de cada panel, el total en 2004 y en el último año.")


# ---------------------------------------------------------------- sección 3
def canastas_por_grupo(tramos):
    """Canastas por adulto equivalente: deciles 1-9, el decil 10 entero y sus tres tramos (versión A)."""
    pr = tramos[tramos.variante == "principal"]
    c = pr.pivot(index="anio", columns="grupo", values="canastas_por_adulto_eq")
    s = pr.pivot(index="anio", columns="grupo", values="part_ingreso")
    # decil 10 = ingreso total / adultos equivalentes totales de sus tres tramos (la canasta se cancela)
    c[10] = s[[91, 95, 99]].sum(axis=1) / (s[[91, 95, 99]] / c[[91, 95, 99]]).sum(axis=1)
    mediana = (c[5] + c[6]) / 2          # aproximada: entre el promedio del decil 5 y el del 6
    return c, mediana


def f06_canastas_tiempo(tramos):
    c, mediana = canastas_por_grupo(tramos)
    limite = 2 * mediana
    fig, ax = plt.subplots(figsize=(12.5, 6.8))
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list("dec", ["#e34948", "#eda100", "#2a78d6"])
    ax.fill_between(c.index, limite, 60, color="#e8f0fb", linewidth=0, zorder=0)
    ax.plot(c.index, limite, color="#5a2d82", linewidth=2.2)
    ax.axhline(1, color=TINTA, linewidth=1.2, linestyle=(0, (4, 3)))
    finales = {}
    for k in range(1, 11):
        ax.plot(c.index, c[k], color=cmap((k - 1) / 9), linewidth=2.6 if k in (1, 10) else 1.5)
        finales[f"D{k}  {pct(c[k].iloc[-1], 2)}"] = (c[k].iloc[-1], cmap((k - 1) / 9))
    ax.plot(c.index, c[99], color=OSCURO, linewidth=2.2, linestyle=(0, (4, 2)))
    finales[f"1% más rico  {pct(c[99].iloc[-1], 1)}"] = (c[99].iloc[-1], OSCURO)
    import math
    pos, ult = {}, -1e9
    for etq, (val, col) in sorted(finales.items(), key=lambda kv: kv[1][0]):
        lv = max(math.log10(val), ult + 0.07)
        pos[etq], ult = (lv, col), lv
    for etq, (lv, col) in pos.items():
        ax.text(ANIO_FIN + 0.5, 10 ** lv, etq, fontsize=8.4, va="center", color=TINTA)
    ax.text(2004.2, 1.06, "Línea de pobreza: 1 canasta por adulto equivalente", fontsize=8.6, color=TINTA,
            va="bottom")
    ax.text(2010.5, limite[2010] * 1.33, "Límite de la clase alta: el doble del ingreso mediano", fontsize=8.8,
            color="#5a2d82", va="bottom", ha="center", fontweight="bold",
            bbox=dict(boxstyle="square,pad=0.15", facecolor="#e8f0fb", edgecolor="none"))
    ax.text(2015.5, 40, "clase alta", fontsize=10, color=OSCURO, ha="center", fontweight="bold")
    ax.set_yscale("log")
    marcas = [0.1, 0.25, 0.5, 1, 2, 5, 10, 25, 50]
    ax.set_yticks(marcas)
    ax.set_yticklabels([pct(m, 2 if m < 1 else 0) for m in marcas])
    ax.minorticks_off()
    ax.set_ylim(0.1, 60)
    ax.set_xlim(2003.5, ANIO_FIN + 0.3)
    ax.set_xticks(range(2004, ANIO_FIN + 1, 3))
    ax.xaxis.grid(False)
    ax.set_ylabel("Canastas básicas por adulto equivalente, por mes (escala logarítmica)")
    fig.subplots_adjust(right=0.83)
    fig.suptitle(f"Ingreso de cada decil y del 1% más rico en canastas básicas, 2004-{ANIO_FIN}", x=0.01, y=1.02,
                 ha="left", fontsize=14, fontweight="bold")
    fig.text(0.01, 0.965, f"Debajo de la línea de pobreza, el grupo promedio es pobre. Por encima de la línea violeta, "
             f"clase alta según el criterio de la OCDE (más del doble del ingreso mediano; en {ANIO_FIN}, "
             f"{pct(limite.iloc[-1], 1)} canastas).\nEscala logarítmica: cada marca del eje multiplica a la anterior, "
             "para que entren en el mismo gráfico el decil 1 y el 1% más rico.", fontsize=9.4, color=TINTA2, va="top")
    fig.text(0.01, -0.03, FUENTE + "\nIngreso del grupo antes de impuestos directos (en la cima, completado con el "
             "ingreso declarado a ARCA que la encuesta no capta) ÷ sus adultos equivalentes (tabla del INDEC) ÷ la canasta "
             "básica total por adulto\nequivalente del Gran Buenos Aires (INDEC; antes de 2017, la de 2017 llevada hacia "
             "atrás con el IPC). Ingreso mediano aproximado como el promedio entre los deciles 5 y 6.",
             fontsize=7.3, color=MUDO, va="top")
    guardar(fig, "f06_canastas_tiempo")
    return c, mediana


def f07_parte_ingreso(tramos):
    a = ANIO_FIN
    t = tabla_tramos(tramos, a)
    orden = list(range(1, 10)) + [10, 91, 95, 99]
    parte = {k: t.part_ingreso[k] * 100 for k in GRUPOS}
    parte[10] = sum(parte[k] for k in (91, 95, 99))
    pob = {k: 10 for k in range(1, 11)} | {91: 5, 95: 4, 99: 1}
    x = list(range(10)) + [10.9, 11.9, 12.9]
    col = ["#b9b8b0"] * 9 + [AZUL, MEDIO, MEDIO, MEDIO]
    fig, ax = plt.subplots(figsize=(12.5, 6))
    ax.bar(x, [parte[k] for k in orden], color=col, width=0.72, zorder=3)
    for xi, k in zip(x, orden):
        ax.text(xi, max(parte[k], pob[k]) + 0.5, f"{pct(parte[k])}%", ha="center", va="bottom", fontsize=9,
                color=TINTA)
        ax.plot([xi - 0.36, xi + 0.36], [pob[k]] * 2, color=TINTA, linewidth=1.8, zorder=4)
    ax.axvspan(10.4, 13.4, color="#e8f0fb", zorder=0, linewidth=0)
    ax.text(11.9, 0.97, "el decil 10,\npartido", transform=ax.get_xaxis_transform(), ha="center", va="top",
            fontsize=8.8, color=TINTA2, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels([f"D{k}" for k in range(1, 11)] + ["P90-95", "P95-99", "1%"])
    ax.set_xlim(-0.6, 13.4)
    ax.set_ylim(0, 43)
    ax.xaxis.grid(False)
    ax.set_ylabel("% del ingreso total")
    ax.plot([], [], color=TINTA, linewidth=1.8, label="% de la población del grupo")
    ax.legend(loc="upper left", frameon=False, fontsize=9)
    fig.suptitle(f"Qué parte del ingreso total tiene cada grupo, {a}", x=0.01, y=1.02, ha="left", fontsize=14,
                 fontweight="bold")
    fig.text(0.01, 0.965, "Barras: parte del ingreso de toda la población que recibe el grupo. Raya negra: parte de la "
             "población que es el grupo (10% cada decil; 5%, 4% y 1% los tramos del decil 10).", fontsize=9.4,
             color=TINTA2, va="top")
    fig.text(0.01, -0.03, FUENTE + "\nIngreso antes de impuestos directos, completado en la cima con el ingreso "
             "declarado a ARCA que la encuesta no capta.", fontsize=7.3, color=MUDO, va="top")
    guardar(fig, "f07_parte_ingreso")


# ---------------------------------------------------------------- sección 4
X13 = list(range(10)) + [10.9, 11.9, 12.9]
NOMBRES13 = [f"D{i}" for i in range(1, 11)] + ["P90-\n95", "P95-\n99", "1%"]


def decil10(tr, cols):
    """El decil 10 entero a partir de sus tres tramos: tasas ponderadas por el ingreso de cada tramo."""
    peso = tr["part_ingreso"] if "part_ingreso" in tr else tr["ingreso_total"]
    w = peso.loc[[91, 95, 99]]
    return tr.loc[[91, 95, 99], cols].mul(w, axis=0).sum() / w.sum()


def datos13(largo, tramos_v, anio, variante):
    """Deciles 1-9, el decil 10 recombinado y sus tres tramos, todo de la misma tabla de tramos: así el
    decil 10 es exactamente la suma de sus partes (con el consumo de la cima estimado por tramo)."""
    tr = tramos_v[(tramos_v.anio == anio) & (tramos_v.variante == variante)].set_index("grupo")
    d10 = decil10(tr, g.COLS + ["total"])
    filas = pd.concat([tr.loc[list(range(1, 10)), g.COLS], d10[g.COLS].to_frame(10).T, tr.loc[[91, 95, 99], g.COLS]]) * 100
    tot = list(tr.loc[list(range(1, 10)), "total"] * 100) + [d10["total"] * 100] + list(tr.loc[[91, 95, 99], "total"] * 100)
    return filas, tot, tr.loc[0, "total"] * 100


def panel13(ax, filas, tot, prom, fs=9):
    g.barras(ax, filas, etiquetas=False, x=X13, nombres=NOMBRES13)
    for xi, b in zip(X13, tot):
        ax.text(xi, b + 0.4, pct(b), ha="center", va="bottom", fontsize=fs, color=TINTA, zorder=5,
                fontweight="bold" if xi >= 9 else None)
    ax.axvspan(10.4, 13.4, color="#e8f0fb", zorder=0, linewidth=0)
    ax.axhline(prom, color=TINTA2, linewidth=1.1, linestyle=(0, (4, 3)), zorder=0.5)
    ax.set_xlim(-0.6, 13.4)


def f08_version_a(largo, tramos):
    a = ANIO_FIN
    filas, tot, prom = datos13(largo, tramos, a, "principal")
    fig, ax = plt.subplots(figsize=(13.5, 6.4))
    panel13(ax, filas, tot, prom)
    ax.text(11.9, 0.97, "el decil 10, partido", transform=ax.get_xaxis_transform(), ha="center", va="top",
            fontsize=8.8, color=TINTA2, fontweight="bold")
    ax.set_ylim(0, 34)
    ax.set_ylabel("Impuestos, % del ingreso")
    leyenda_impuestos(fig, loc="center left", bbox_to_anchor=(0.86, 0.55), fontsize=9)
    fig.subplots_adjust(right=0.85)
    fig.suptitle(f"Versión A: el decil 10 partido en tres, con los mismos datos que los deciles, {a}", x=0.01,
                 y=1.02, ha="left", fontsize=14, fontweight="bold")
    fig.text(0.01, 0.965, f"A la izquierda, los diez deciles de la figura 2. A la derecha (fondo celeste), el decil 10 "
             "separado en los percentiles 90-95 (5% de la población), 95-99 (4%) y el 1% más rico.\nLínea punteada: promedio de la población ({pct(prom)}%). Ingreso: el declarado "
             "en la encuesta, completado en la cima con el ingreso y la Ganancias declarados a ARCA que la encuesta no capta.",
             fontsize=9.4, color=TINTA2, va="top")
    fig.text(0.01, -0.03, FUENTE + "\nDentro del decil 10 las personas se ordenan por ingreso per cápita familiar, igual "
             f"que en los deciles. Declaraciones juradas de {a - 1} actualizadas a {a} con la variación del ingreso del "
             "decil 10.", fontsize=7.3, color=MUDO, va="top")
    guardar(fig, "f08_version_a")


def f09_version_b(largo, f0):
    a = ANIO_FIN
    filas, tot, prom = datos13(largo, f0, a, VERSION_B)
    _, sin_ext, _ = datos13(largo, f0, a, "ajuste_cn_rentas")
    fig, ax = plt.subplots(figsize=(13.5, 6.4))
    panel13(ax, filas, tot, prom)
    for xi, v in zip(X13, sin_ext):
        ax.plot([xi - 0.36, xi + 0.36], [v, v], color="#6f6e66", linewidth=1.6, linestyle=(0, (2, 1.5)), zorder=6)
    raya = matplotlib.lines.Line2D([], [], color="#6f6e66", linewidth=1.6, linestyle=(0, (2, 1.5)),
                                   label="sin la renta de la cartera externa")
    ax.legend(handles=[raya], loc="upper left", frameon=False, fontsize=8.8)
    ax.text(11.9, 0.97, "el decil 10, partido", transform=ax.get_xaxis_transform(), ha="center", va="top",
            fontsize=8.8, color=TINTA2, fontweight="bold")
    ax.set_ylim(0, 36)
    ax.set_ylabel("Impuestos, % del ingreso")
    leyenda_impuestos(fig, loc="center left", bbox_to_anchor=(0.86, 0.55), fontsize=9)
    fig.subplots_adjust(right=0.85)
    fig.suptitle(f"Versión B: los mismos impuestos, con el ingreso que la encuesta no capta estimado, {a}", x=0.01,
                 y=1.02, ha="left", fontsize=14, fontweight="bold")
    fig.text(0.01, 0.965, "Los impuestos de cada grupo son los de la versión A; el ingreso se completa en tres partes: "
             "sueldos y cuentapropia llevados al total de las Cuentas Nacionales, rentas del capital\nmultiplicadas por 7 "
             "y 4% anual sobre la cartera de acciones y bonos del sector privado en el exterior, atribuido al 1% más "
             "rico. Rayas grises: la tasa sin esta última parte.", fontsize=9.4, color=TINTA2, va="top")
    fig.text(0.01, -0.03, FUENTE + "\nCuentas Nacionales: cuenta de generación del ingreso (INDEC). Rentas ×7: De Rosa, "
             "Flores y Morgan (2024). Cartera externa: Posición de inversión internacional (INDEC). La carga total de la "
             "población es la misma que en A.", fontsize=7.3, color=MUDO, va="top")
    guardar(fig, "f09_version_b")


# ---------------------------------------------------------------- sección 5
def f11_anios_partido(largo, tramos):
    def dibujar(ax, a):
        filas, tot, prom = datos13(largo, tramos, a, "principal")
        panel13(ax, filas, tot, prom, fs=7.6)
        ax.set_xticklabels(NOMBRES13, fontsize=7.8)
        return prom
    grilla_anios(dibujar, "f11_partido_anios_gobierno",
                 "Qué parte de su ingreso pagó cada grupo, con el decil 10 partido, en los años de cambio de gobierno",
                 "Como la figura 3, con el decil 10 separado en tres (fondo celeste). Versión A.")


# ---------------------------------------------------------------- sección 6
def kakwani_referencia(tramos, e):
    """Kakwani que tendría el sistema progresivo de referencia (misma recaudación, tasa ∝ ingreso^e)."""
    filas = []
    for a, d in tramos[tramos.variante == "principal"].groupby("anio"):
        d = d.set_index("grupo").loc[GRUPOS]
        w = np.array([POB[k] for k in GRUPOS])
        yrel = d.canastas_por_persona / tramos[(tramos.variante == "principal") & (tramos.anio == a) &
                                               (tramos.grupo == 0)].canastas_por_persona.iloc[0]
        peso = d.part_ingreso * yrel ** e
        ref = (peso / peso.sum()).values
        gi = inf.gini_agrupado(w, d.part_ingreso.values)
        filas.append({"anio": a, "kakwani": inf.gini_agrupado(w, ref) - gi})
    return pd.DataFrame(filas).set_index("anio").kakwani


def todas_variantes(tramos, f0):
    """Tramos con todos los supuestos: principal y los de la tabla de tramos, los de robustez y la versión B."""
    rob = pd.read_csv(TABLES / "tasas_tramos_decil10_robustez.csv")
    b = f0[f0.variante == VERSION_B].copy()
    tot = b[b.grupo == 0].set_index("anio")
    b["part_ingreso"] = b.ingreso_total / b.anio.map(tot.ingreso_total)
    b["part_impuestos"] = b.total * b.ingreso_total / b.anio.map(tot.total * tot.ingreso_total)
    b["variante"] = "version_b"
    base = tramos[~tramos.variante.isin(["ajuste_cn", "ajuste_cn_activos_ext"])]
    rob = rob[rob.variante != "recursos_gasto"]      # descartada: no se mide a los más pobres por su consumo
    return pd.concat([base, rob, b], ignore_index=True)


def f13_kakwani(tramos, todas):
    k = inf.kakwani(todas[["variante", "anio", "grupo", "part_ingreso", "part_impuestos"]])
    kk = k.pivot(index="anio", columns="variante", values="kakwani")
    ref = {e: kakwani_referencia(tramos, e) for e in (0.15, 0.25, 0.40)}
    fig, ax = plt.subplots(figsize=(12, 5.8))
    inf.ejes_tiempo(ax)
    ax.axhline(0, color=TINTA2, linewidth=1)
    ax.fill_between(ref[0.15].index, ref[0.15], ref[0.40], color=OSCURO, alpha=0.08, linewidth=0)
    ax.plot(ref[0.25].index, ref[0.25], color=OSCURO, linewidth=1.8, linestyle=(0, (5, 2)))
    ax.fill_between(kk.index, kk.min(axis=1), kk.max(axis=1), color=ROJO, alpha=0.15, linewidth=0)
    ax.plot(kk.index, kk["principal"], color=ROJO, linewidth=2.6, marker="o", markersize=3.5)
    a = ANIO_FIN
    ax.text(a + 0.4, ref[0.25][a], f"Sistema progresivo\nde referencia  {pct(ref[0.25][a], 3)}", fontsize=9,
            color=OSCURO, va="center", fontweight="bold")
    ax.text(a + 0.4, kk["principal"][a], f"Argentina  {pct(kk['principal'][a], 3)}", fontsize=9, color=ROJO,
            va="center", fontweight="bold")
    ax.text(2004.2, 0.004, "0: proporcional", fontsize=8.4, color=TINTA2, va="bottom")
    ax.set_ylabel("Índice de Kakwani")
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:.2f}".replace(".", ",")))
    ax.text(2011, ref[0.40].max() + 0.004, "INDEC intervenido (2007-2015)", ha="center", fontsize=8, color=MUDO)
    fig.subplots_adjust(right=0.82)
    fig.suptitle("Índice de Kakwani: qué tan progresivo es el sistema, año por año", x=0.01, y=1.02, ha="left",
                 fontsize=14, fontweight="bold")
    fig.text(0.01, 0.965, "Kakwani = concentración de los impuestos − concentración del ingreso (Gini). Mayor que 0: "
             "progresivo; 0: proporcional; menor que 0: regresivo. Rojo: Argentina (franja: todos los supuestos de la sección 8).\nAzul "
             "punteado: el valor que tendría el sistema progresivo de referencia de esta sección, con la misma recaudación "
             "(franja: con exponente 0,15 a 0,40 en lugar de 0,25).", fontsize=9.4, color=TINTA2, va="top")
    fig.text(0.01, -0.03, FUENTE + "\nCalculado con 12 grupos (deciles 1 a 9 y el decil 10 partido en tres): aproximado. "
             "Versión A.", fontsize=7.3, color=MUDO, va="top")
    guardar(fig, "f13_kakwani")
    return kk["principal"], ref


# clases para marcar en las figuras 15 y 17: posiciones en GRUPOS (D1..D9, P90-95, P95-99, 1%)
CLASES_MARCA = [("Clase baja", 0, 2, "#f6dede", ROJO), ("Clase media", 3, 7, "#ecebe6", "#6f6e66"),
                ("Clase alta", 8, 10, "#e3eefb", MEDIO), ("1%", 11, 11, "#d3e0f0", OSCURO)]


def marcar_clases_x(ax, y_txt=-0.2, totales=None):
    """Fondo por clase y su nombre debajo del eje x (barras verticales); con totales, el monto debajo."""
    tr = matplotlib.transforms.blended_transform_factory(ax.transData, ax.transAxes)
    for nombre, i0, i1, fondo, color in CLASES_MARCA:
        ax.axvspan(i0 - 0.48, i1 + 0.48, color=fondo, zorder=0, linewidth=0)
        ax.plot([i0 - 0.4, i1 + 0.4], [y_txt + 0.035] * 2, color=color, linewidth=2, transform=tr, clip_on=False)
        ax.text((i0 + i1) / 2, y_txt, nombre, transform=tr, ha="center", va="top", fontsize=9.5, color=color,
                fontweight="bold", clip_on=False)
        if totales is not None:
            v = totales[nombre]
            ax.text((i0 + i1) / 2, y_txt - 0.05, f"{'+' if v >= 0 else '−'}US${pct(abs(v))} mil M",
                    transform=tr, ha="center", va="top", fontsize=8.6, color=color, clip_on=False)


def marcar_clases_y(ax, etiquetas=False):
    """Fondo por clase (barras horizontales); con etiquetas, el nombre a la derecha del panel."""
    tr = matplotlib.transforms.blended_transform_factory(ax.transAxes, ax.transData)
    for nombre, i0, i1, fondo, color in CLASES_MARCA:
        ax.axhspan(i0 - 0.48, i1 + 0.48, color=fondo, zorder=0, linewidth=0)
        if etiquetas:
            ax.plot([1.02, 1.02], [i0 - 0.35, i1 + 0.35], color=color, linewidth=2, transform=tr, clip_on=False)
            ax.text(1.04, (i0 + i1) / 2, nombre, transform=tr, ha="left", va="center", fontsize=9.5, color=color,
                    fontweight="bold", clip_on=False)


def f15_brecha_grupos(b):
    x = b[(b.version == "A") & (b.anio == ANIO_FIN)].set_index("grupo").loc[GRUPOS]
    fig, ax = plt.subplots(figsize=(13, 6.2))
    xs, w = np.arange(len(GRUPOS)), 0.38
    series = [(-w / 2, "proporcional", GRIS, f"si fuera proporcional: todos pagan la tasa promedio "
                                             f"({pct(x.tasa_promedio.iloc[0] * 100)}%)"),
              (w / 2, "progresivo_e025", OSCURO, "si fuera progresivo: la tasa sube con el ingreso")]
    for off, col, color, nombre in series:
        v = x[f"{col}_musd"] / 1000
        ax.bar(xs + off, v, w, color=color, label=nombre, zorder=3)
        for xi, vi in zip(xs + off, v):
            ax.text(xi, vi + (0.15 if vi >= 0 else -0.15), ("+" if vi >= 0 else "−") + pct(abs(vi)), ha="center",
                    va="bottom" if vi >= 0 else "top", fontsize=8, color=color)
    ax.axhline(0, color=TINTA, lw=0.9, zorder=4)
    bt = matplotlib.transforms.blended_transform_factory(ax.transAxes, ax.transData)
    ax.text(1.01, 0.4, "↑ pagaría más\nque hoy", transform=bt, fontsize=9, color=OSCURO, va="bottom",
            ha="left", fontweight="bold")
    ax.text(1.01, -0.4, "↓ pagaría menos\nque hoy", transform=bt, fontsize=9, color=ROJO, va="top", ha="left",
            fontweight="bold")
    ax.set_xticks(xs, [f"{NOMBRES[k]}\n{pct(x.tasa[k] * 100)}%" for k in GRUPOS])
    ax.set_xlim(-0.6, len(GRUPOS) - 0.4)
    totales = {n: x.progresivo_e025_musd.iloc[i0:i1 + 1].sum() / 1000 for n, i0, i1, _, _ in CLASES_MARCA}
    marcar_clases_x(ax, y_txt=-0.15, totales=totales)
    ax.set_ylabel("miles de millones de US$ por año")
    ax.xaxis.grid(False)
    ax.legend(frameon=False, loc="upper left", fontsize=9.5)
    fig.suptitle(f"Cuánto más (+) o menos (−) pagaría cada grupo con otro sistema que recaude lo mismo, {ANIO_FIN}",
                 x=0.01, y=1.02, ha="left", fontsize=14, fontweight="bold")
    fig.text(0.01, 0.965, "Debajo de cada grupo, la tasa que paga hoy. Gris: frente a un sistema proporcional; azul: "
             "frente al progresivo de referencia. En cada color, lo que suman unos lo restan otros: el total es cero.\n"
             "Debajo del nombre de cada clase, su total frente al sistema progresivo.",
             fontsize=9.4, color=TINTA2, va="top")
    fig.text(0.01, -0.13, FUENTE + "\nBrecha = recaudación real de los impuestos del estudio (DNIAF) × (parte de los "
             "impuestos que le tocaría − parte que paga). Dólares al tipo de cambio oficial promedio del año. Versión A. "
             "Cálculo mecánico, sin cambios de comportamiento.", fontsize=7.3, color=MUDO, va="top")
    guardar(fig, "f15_brecha_grupos")


def f16_brecha_1pct(b):
    x = b[(b.version == "A") & (b.grupo == 99)].set_index("anio")
    t, p, q = x.tasa * 100, x.tasa_promedio * 100, x.tasa_progresiva * 100
    fig, ax = plt.subplots(figsize=(12.5, 6.4))
    ax.fill_between(x.index, np.maximum(t, p), q, color=OSCURO, alpha=0.09, lw=0)
    ax.fill_between(x.index, t, p, where=t < p, interpolate=True, color=ROJO, alpha=0.22, lw=0)
    ax.fill_between(x.index, t, p, where=t >= p, interpolate=True, color=GRIS, alpha=0.25, lw=0)
    ax.plot(x.index, q, color=OSCURO, lw=2.2)
    ax.plot(x.index, p, color=GRIS, lw=2.2)
    ax.plot(x.index, t, color=ROJO, lw=3)
    a = ANIO_FIN
    ax.text(a + 0.3, q[a], f"Tasa en el sistema\nprogresivo  {pct(q[a])}%", color=OSCURO, va="center", fontsize=9.5)
    ax.text(a + 0.3, p[a] + 1.2, f"Tasa promedio (sistema\nproporcional)  {pct(p[a])}%", color="#6f6e66",
            va="center", fontsize=9.5)
    ax.text(a + 0.3, t[a] - 1.2, f"Tasa del 1%  {pct(t[a])}%", color=ROJO, va="center", fontsize=10,
            fontweight="bold")
    ax.set_xlim(2003.5, a + 0.2)
    ax.set_ylim(15, 47)
    ax.set_xticks(range(2004, a + 1, 3))
    ax.xaxis.grid(False)
    ax.set_ylabel("Impuestos, % del ingreso")
    fig.subplots_adjust(right=0.8)
    fig.suptitle(f"El 1% más rico: la tasa que paga y la que pagaría con cada sistema de referencia, 2004-{a}",
                 x=0.01, y=1.02, ha="left", fontsize=14, fontweight="bold")
    fig.text(0.01, 0.965, "Roja: la tasa del 1%. Gris: la tasa promedio, que es la que pagaría con un sistema "
             "proporcional. Azul: la que pagaría con el progresivo de referencia.\nSombreado rojo: años en que paga "
             "menos que el promedio; gris: años en que paga más. Celeste: la distancia hasta el progresivo.",
             fontsize=9.4, color=TINTA2, va="top")
    fig.text(0.01, -0.03, FUENTE + "\nVersión A. Progresivo: tasa = promedio × (ingreso por persona del grupo ÷ "
             "promedio)^0,25, reescalada para recaudar lo mismo.", fontsize=7.3, color=MUDO, va="top")
    guardar(fig, "f16_brecha_1pct")


def f17_deltas_2025(tramos):
    a = ANIO_FIN
    pr = tabla_tramos(tramos, a)
    y = list(range(len(GRUPOS)))
    yrel = pr.canastas_por_persona[GRUPOS] / pr.canastas_por_persona[0]
    peso = pr.part_ingreso[GRUPOS] * yrel ** g.ELAST_PROG
    ref_prog = peso / peso.sum()
    tasa_prog = pr.total[0] * yrel ** g.ELAST_PROG / peso.sum()
    d_prop = [(pr.part_impuestos[k] - pr.part_ingreso[k]) * 100 for k in GRUPOS]
    d_prog = [(pr.part_impuestos[k] - ref_prog[k]) * 100 for k in GRUPOS]
    fig, (ax2, ax3) = plt.subplots(1, 2, figsize=(15, 6.4))

    def panel(axx, delta, titulo, xlabel):
        lim = max(abs(d) for d in delta) * 1.45
        axx.barh(y, delta, height=0.62, color=[OSCURO if d >= 0 else ROJO for d in delta])
        axx.axvline(0, color=TINTA2, linewidth=1)
        bt = matplotlib.transforms.blended_transform_factory(axx.transData, axx.transAxes)
        for i, d in enumerate(delta):
            axx.text(d + (0.03 if d >= 0 else -0.03) * lim, i, f"{'+' if d >= 0 else '−'}{pct(abs(d), 2)}",
                     va="center", ha="left" if d >= 0 else "right", fontsize=8.4, color=TINTA)
        axx.set_yticks(y)
        axx.set_xlim(-lim, lim)
        axx.set_ylim(-0.6, len(GRUPOS) - 0.1)
        axx.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: pct(v)))
        axx.set_xlabel(xlabel, fontsize=9)
        axx.yaxis.grid(False)
        axx.text(-0.04, 1.01, "← paga una parte menor", transform=bt, fontsize=8.2, color=ROJO, va="bottom",
                 ha="right")
        axx.text(0.04, 1.01, "paga una parte mayor →", transform=bt, fontsize=8.2, color=OSCURO, va="bottom",
                 ha="left")
        axx.set_title(titulo, loc="left", fontsize=11.5, fontweight="bold", pad=20)

    panel(ax2, d_prop, "Frente a un sistema proporcional", "Puntos: % de los impuestos que paga − % del ingreso que tiene")
    ax2.set_yticklabels([NOMBRES[k] for k in GRUPOS])
    marcar_clases_y(ax2)
    panel(ax3, d_prog, "Frente al sistema progresivo de referencia",
          "Puntos: % de los impuestos que paga − % que pagaría en el progresivo")
    ax3.set_yticklabels([f"{pct(tasa_prog[k] * 100)}%" for k in GRUPOS], fontsize=8.4, color=TINTA2)
    ax3.text(-0.02, len(GRUPOS) - 0.35, "tasa en el\nprogresivo", transform=matplotlib.transforms.
             blended_transform_factory(ax3.transAxes, ax3.transData), ha="right", va="bottom", fontsize=7.6, color=MUDO)
    marcar_clases_y(ax3, etiquetas=True)
    fig.subplots_adjust(wspace=0.3, top=0.8, right=0.9)
    fig.suptitle(f"Qué parte de los impuestos paga cada grupo frente a lo que pagaría con cada referencia, {a}",
                 x=0.01, y=1.0, ha="left", fontsize=14, fontweight="bold")
    fig.text(0.01, 0.945, "Cada barra: la parte de la recaudación total que paga el grupo menos la que pagaría con el "
             "sistema de referencia, en puntos. Azul: paga una parte mayor; rojo: menor.\nIzquierda: el grupo pagaría su "
             "parte del ingreso. Derecha: la tasa sube con el ingreso (a la izquierda de cada barra, la tasa que le tocaría).",
             fontsize=9.4, color=TINTA2, va="top")
    fig.text(0.01, -0.03, FUENTE + " Versión A.", fontsize=7.3, color=MUDO, va="top")
    guardar(fig, "f17_deltas_2025")


# ---------------------------------------------------------------- sección 7
def veces(tramos):
    """Por año: ingreso e impuestos por persona del decil 10 y del 1%, relativos al decil 1 (versión A)."""
    pr = tramos[tramos.variante == "principal"]
    ing = pr.pivot(index="anio", columns="grupo", values="canastas_por_persona")       # ∝ ingreso por persona
    imp = ing * pr.pivot(index="anio", columns="grupo", values="total")                # impuestos por persona
    w = pd.Series({91: 0.5, 95: 0.4, 99: 0.1})                                         # personas dentro del decil 10
    ing10, imp10 = (ing[w.index] * w).sum(axis=1), (imp[w.index] * w).sum(axis=1)
    return pd.DataFrame({
        "ingreso_d10": ing10 / ing[1], "ingreso_d10_despues": (ing10 - imp10) / (ing[1] - imp[1]),
        "impuestos_d10": imp10 / imp[1], "ingreso_1": ing[99] / ing[1], "impuestos_1": imp[99] / imp[1]})


def f18_veces(tramos):
    v = veces(tramos)
    fig, axs = plt.subplots(1, 3, figsize=(21, 6))
    paneles = [
        (axs[0], [("ingreso_d10", "antes de impuestos", TINTA2, "-"), ("ingreso_d10_despues", "después de impuestos",
                                                                         ROJO, "-")],
         "A. Cuántas veces más ingresa por persona\nel 10% más rico que el 10% más pobre"),
        (axs[1], [("ingreso_d10", "ingreso", TINTA2, (0, (4, 2))), ("impuestos_d10", "impuestos", AZUL, "-")],
         "B. Cuántas veces más ingresa y cuántas veces más\npaga por persona el 10% más rico que el 10% más pobre"),
        (axs[2], [("ingreso_1", "ingreso", TINTA2, (0, (4, 2))), ("impuestos_1", "impuestos", OSCURO, "-")],
         "C. Cuántas veces más ingresa y cuántas veces más\npaga por persona el 1% más rico que el 10% más pobre"),
    ]
    for ax, series, titulo in paneles:
        finales = sorted([(v[col].iloc[-1], col) for col, *_ in series])
        sep = (finales[-1][0] - finales[0][0])
        minimo = 0.09 * max(v[[c for c, *_ in series]].max())
        desp = {} if sep >= minimo else {finales[0][1]: -(minimo - sep) / 2, finales[-1][1]: (minimo - sep) / 2}
        for col, nombre, color, estilo in series:
            ax.plot(v.index, v[col], color=color, linewidth=2.6, linestyle=estilo)
            ax.text(ANIO_FIN + 0.4, v[col].iloc[-1] + desp.get(col, 0), f"{nombre}\n{pct(v[col].iloc[-1], 0)} veces",
                    fontsize=8.6, va="center", color=color, fontweight="bold")
        ax.set_ylim(0, None)
        ax.set_xlim(2003.5, ANIO_FIN + 0.3)
        ax.set_xticks(range(2004, ANIO_FIN + 1, 4))
        ax.xaxis.grid(False)
        ax.set_title(titulo, loc="left", fontsize=11, fontweight="bold")
        ax.set_ylabel("Veces")
    a = axs[0]
    a.fill_between(v.index, v.ingreso_d10, v.ingreso_d10_despues, color=ROJO, alpha=0.15, linewidth=0)
    fig.subplots_adjust(wspace=0.62, right=0.93, top=0.78)
    fig.suptitle("Cuántas veces más ingresan y cuántas veces más pagan los de arriba que el 10% más pobre", x=0.01,
                 y=1.0, ha="left", fontsize=14, fontweight="bold")
    fig.text(0.01, 0.945, "A: ingreso por persona del decil 10 dividido por el del decil 1, antes y después de pagar los "
             "impuestos del estudio. B y C: lo mismo con los impuestos que paga cada persona (línea llena),\njunto al "
             "ingreso (punteada). Si la línea de impuestos queda debajo de la de ingreso, el grupo de arriba paga una "
             "proporción de su ingreso menor que el decil 1.", fontsize=9.4, color=TINTA2, va="top")
    fig.text(0.01, -0.03, FUENTE + "\nIngreso antes de impuestos directos, completado en la cima con el ingreso declarado "
             "a ARCA que la encuesta no capta; por persona (ingreso del grupo ÷ sus miembros). Versión A.",
             fontsize=7.3, color=MUDO, va="top")
    guardar(fig, "f18_veces")
    return v


# ---------------------------------------------------------------- sección 8
OTROS = ["version_b"]                            # se muestra aparte, no dentro de la franja


def tasas_por_variante(todas):
    """Tasa total (%) por variante, año y grupo."""
    return todas.pivot_table(index=["variante", "anio"], columns="grupo", values="total") * 100


def f19_rangos(w):
    sup = w.drop(OTROS, level=0)
    orden = list(range(1, 10)) + [91, 95, 99]
    x = list(range(9)) + [9.9, 10.9, 11.9]
    fig, axs = plt.subplots(2, 4, figsize=(22, 10.5), sharey=True)
    for ax, a in zip(axs.flat, ANIOS_GOBIERNO):
        s_ = sup.xs(a, level=1)[orden]
        lo, hi = s_.min(), s_.max()
        ax.bar(x, hi - lo, bottom=lo, width=0.62, color="#b9d4f4", zorder=2)
        pr = w.loc[("principal", a), orden]
        ax.scatter(x, w.loc[("version_b", a), orden], marker="D", s=30, color=AZUL, zorder=4)
        ax.scatter(x, pr, s=42, color=TINTA, zorder=5)
        ax.axhline(w.loc[("principal", a), 0], color=TINTA2, linewidth=1, linestyle=(0, (4, 3)), zorder=1)
        ax.axvspan(9.45, 12.35, color="#e8f0fb", zorder=0, linewidth=0)
        ax.set_xticks(x)
        ax.set_xticklabels([f"D{k}" for k in range(1, 10)] + ["P90-\n95", "P95-\n99", "1%"], fontsize=8.2)
        ax.set_xlim(-0.6, 12.4)
        ax.xaxis.grid(False)
        ax.set_title(str(a), loc="left", fontsize=13, fontweight="bold")
        ax.set_title(GOBIERNO[a], loc="right", fontsize=8.6, color=TINTA2)
    ult = axs.flat[-1]
    ult.axis("off")
    h = [g.Patch(facecolor="#b9d4f4", label="Rango entre los supuestos de las\nfamilias 1, 2 y 4 y sin completar la cima"),
         matplotlib.lines.Line2D([], [], marker="o", color=TINTA, linestyle="", label="Versión A (medida del informe)"),
         matplotlib.lines.Line2D([], [], marker="D", color=AZUL, linestyle="", label="Versión B (ingreso completado)"),
         matplotlib.lines.Line2D([], [], color=TINTA2, linestyle=(0, (4, 3)), label="Promedio (versión A)")]
    ult.legend(handles=h, loc="center", fontsize=10, frameon=False)
    for ax in axs[:, 0]:
        ax.set_ylabel("Impuestos, % del ingreso")
    axs[0, 0].set_ylim(10, 46)
    fig.suptitle("Cuánto cambia la tasa de cada grupo con cada supuesto, en los años de cambio de gobierno", x=0.01,
                 y=1.0, ha="left", fontsize=14, fontweight="bold")
    fig.text(0.01, 0.965, "Franja celeste: entre qué valores queda la tasa del grupo con los distintos supuestos sobre quién "
             "paga, qué impuestos entran y cuánto consume la cima. Puntos negros: la medida del informe.\nRombos azules: "
             "con el ingreso que la encuesta no capta estimado.", fontsize=9.4, color=TINTA2, va="top")
    fig.subplots_adjust(left=0.04, right=0.995, wspace=0.06, hspace=0.32, top=0.89)
    fig.text(0.01, 0.02, FUENTE, fontsize=7.3, color=MUDO, va="top")
    guardar(fig, "f19_rangos_supuestos")


def f20_distancias(w):
    sup = w.drop(OTROS, level=0)
    paneles = [
        ("A. Decil 1 menos el promedio", lambda d: d[1] - d[0], ROJO),
        ("B. El 1% más rico menos el promedio", lambda d: d[99] - d[0], OSCURO),
        ("C. El 1% más rico menos los percentiles 90-95", lambda d: d[99] - d[91], MEDIO),
    ]
    fig, axs = plt.subplots(1, 3, figsize=(21, 6))
    for ax, (titulo, f, color) in zip(axs, paneles):
        banda = f(sup).unstack(0)
        inf.ejes_tiempo(ax, paso=4)
        ax.axhline(0, color=TINTA, linewidth=1)
        ax.fill_between(banda.index, banda.min(axis=1), banda.max(axis=1), color=color, alpha=0.16, linewidth=0)
        ax.plot(banda.index, banda["principal"], color=color, linewidth=2.6)
        vb = f(w.loc["version_b"])
        ax.plot(vb.index, vb, color=AZUL, linewidth=1.6, linestyle=(0, (4, 2)))
        ax.set_title(titulo, loc="left", fontsize=11.5, fontweight="bold")
        ax.set_ylabel("Puntos de ingreso")
        ax.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(5 if color == ROJO else 2))
        ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(
            lambda v, _: f"{v:+.0f}".replace("-", "−") if v else "0"))
    h = [g.Patch(facecolor=TINTA2, alpha=0.25, label="rango entre supuestos"),
         matplotlib.lines.Line2D([], [], color=TINTA, linewidth=2.6, label="versión A (medida del informe)"),
         matplotlib.lines.Line2D([], [], color=AZUL, linewidth=1.6, linestyle=(0, (4, 2)), label="versión B")]
    fig.legend(handles=h, loc="lower center", ncol=3, frameon=False, fontsize=9.5, bbox_to_anchor=(0.5, -0.04))
    fig.subplots_adjust(wspace=0.22, top=0.78, bottom=0.14)
    fig.suptitle("Las tres comparaciones centrales del informe, con todos los supuestos, 2004-" + str(ANIO_FIN), x=0.01,
                 y=1.0, ha="left", fontsize=14, fontweight="bold")
    fig.text(0.01, 0.945, "Cada panel es una diferencia de tasas, en puntos: por encima de 0, el primer grupo paga una "
             "proporción de su ingreso mayor que el segundo; por debajo, menor. La línea llena es la medida del informe;\n"
             "la franja, entre qué valores queda la diferencia con los demás supuestos. Si la franja entera está de un "
             "lado del 0, el resultado de ese año no depende de los supuestos.", fontsize=9.4, color=TINTA2, va="top")
    fig.text(0.01, -0.07, FUENTE + " Sombreado gris: INDEC intervenido (2007-2015).", fontsize=7.3, color=MUDO, va="top")
    guardar(fig, "f20_distancias_supuestos")


# ---------------------------------------------------------------- sección 9
CLASES = [("Clase baja\n(deciles 1 a 3)", [1, 2, 3], ROJO), ("Clase media\n(deciles 4 a 8)", [4, 5, 6, 7, 8], GRIS),
          ("Clase alta sin el 1%\n(decil 9 a percentil 99)", [9, 91, 95], MEDIO), ("1% más rico", [99], OSCURO)]


def por_clase(tramos):
    """Por año y clase: parte del ingreso, parte de los impuestos, tasa y composición (versión A)."""
    pr = tramos[tramos.variante == "principal"]
    filas = []
    for a, d in pr.groupby("anio"):
        d = d.set_index("grupo")
        for nombre, gr, _ in CLASES:
            w = d.part_ingreso[gr]
            f = {"anio": a, "clase": nombre, "part_ingreso": w.sum() * 100, "part_impuestos": d.part_impuestos[gr].sum() * 100,
                 "tasa": (d.total[gr] * w).sum() / w.sum() * 100}
            for c in g.COLS:
                f[c] = (d[c][gr] * w).sum() / w.sum()
            filas.append(f)
    return pd.DataFrame(filas)


def brecha_por_clase(b):
    filas = []
    x = b[b.version == "A"]
    for (a,), d in x.groupby(["anio"]):
        d = d.set_index("grupo")
        for n, gr, _ in CLASES:
            filas.append({"anio": a, "clase": n, "personas": d.personas[gr].sum(),
                          "prop_musd": d.proporcional_musd[gr].sum(), "prog_musd": d.progresivo_e025_musd[gr].sum(),
                          "prog_pib": d.progresivo_e025_pib[gr].sum() * 100, "prop_pib": d.proporcional_pib[gr].sum() * 100})
    r = pd.DataFrame(filas)
    r["prop_pp"] = r.prop_musd * 1e6 / r.personas
    r["prog_pp"] = r.prog_musd * 1e6 / r.personas
    return r


def f_flujo(tramos, a=ANIO_FIN, archivo="fXX_flujo", carpeta=None):
    """Población → ingreso → impuestos, por grupo (versión A), al estilo de un diagrama de flujo."""
    d = tabla_tramos(tramos, a)
    orden = list(range(1, 10)) + [91, 95, 99]              # de abajo (D1) hacia arriba (1%)
    pob = np.array([POB[k] * 100 for k in orden])
    ing = np.array([d.part_ingreso[k] * 100 for k in orden])
    imp = np.array([d.part_impuestos[k] * 100 for k in orden])
    clase = {k: c for c, ks in [("baja", [1, 2, 3]), ("media", [4, 5, 6, 7, 8]), ("alta", [9, 91, 95]), ("1", [99])] for k in ks}
    tonos = {"baja": ["#f2b8b5", "#ec9a97", "#e57b78"], "media": ["#dcdbd4", "#cfcec6", "#c2c1b8", "#b5b4aa", "#a8a79c"],
             "alta": ["#b9d4f4", "#8fbaec", "#5f9ae0"], "1": [OSCURO]}
    usados = {c: 0 for c in tonos}
    colores = []
    for k in orden:
        c = clase[k]
        colores.append(tonos[c][usados[c]])
        usados[c] += 1
    cols_x = [0.0, 1.0, 2.0]
    ancho = 0.10
    def tramos_y(v):
        hi = np.cumsum(v)
        return hi - v, hi
    yp, yi, yt = tramos_y(pob), tramos_y(ing), tramos_y(imp)
    fig, ax = plt.subplots(figsize=(13, 8.6))
    t = np.linspace(0, 1, 60)
    suave = 3 * t ** 2 - 2 * t ** 3
    for i, col in enumerate(colores):
        for (x0, (a0, b0)), (x1, (a1, b1)) in [((cols_x[0], (yp[0][i], yp[1][i])), (cols_x[1], (yi[0][i], yi[1][i]))),
                                              ((cols_x[1], (yi[0][i], yi[1][i])), (cols_x[2], (yt[0][i], yt[1][i])))]:
            xs = x0 + ancho / 2 + (x1 - x0 - ancho) * t
            ax.fill_between(xs, a0 + (a1 - a0) * suave, b0 + (b1 - b0) * suave, color=col, alpha=0.55, linewidth=0)
        for x, (lo, hi) in zip(cols_x, [(yp[0][i], yp[1][i]), (yi[0][i], yi[1][i]), (yt[0][i], yt[1][i])]):
            ax.add_patch(matplotlib.patches.Rectangle((x - ancho / 2, lo), ancho, hi - lo, color=col, linewidth=0.6,
                                                      edgecolor=SUP))
    nombres = [f"D{k}" for k in range(1, 10)] + ["P90-95", "P95-99", "1% más rico"]
    for i, n in enumerate(nombres):
        ax.text(cols_x[0] - ancho / 2 - 0.03, (yp[0][i] + yp[1][i]) / 2, f"{n}  {pct(pob[i], 0)}%", ha="right",
                va="center", fontsize=9, color=TINTA)
        ax.text(cols_x[2] + ancho / 2 + 0.03, (yt[0][i] + yt[1][i]) / 2, f"{pct(imp[i])}%", ha="left", va="center",
                fontsize=9, color=TINTA, fontweight="bold" if orden[i] == 99 else None)
        if ing[i] > 2.2:
            ax.text(cols_x[1], (yi[0][i] + yi[1][i]) / 2, f"{pct(ing[i])}%", ha="center", va="center", fontsize=8,
                    color="white" if orden[i] in (95, 99) else TINTA)
    for x, t_ in zip(cols_x, ["Parte de la\npoblación", "Parte del\ningreso", "Parte de los\nimpuestos"]):
        ax.text(x, 103, t_, ha="center", va="bottom", fontsize=11, fontweight="bold", color=TINTA)
    # nombres de clase a la izquierda de todo
    for nombre, ks, color in [("Clase baja", [1, 2, 3], ROJO), ("Clase media", [4, 5, 6, 7, 8], "#6f6e66"),
                              ("Clase alta", [9, 91, 95], MEDIO), ("1%", [99], OSCURO)]:
        idx = [orden.index(k) for k in ks]
        lo, hi = yp[0][idx[0]], yp[1][idx[-1]]
        ax.plot([-0.52, -0.52], [lo + 0.4, hi - 0.4], color=color, linewidth=2.5)
        ax.text(-0.56, (lo + hi) / 2, nombre, ha="right", va="center", fontsize=10, color=color, fontweight="bold")
    ax.set_xlim(-0.85, 2.35)
    ax.set_ylim(-1, 110)
    ax.axis("off")
    fig.suptitle(f"De cada 100 personas, cuánto del ingreso tienen y cuánto de los impuestos pagan, {a}", x=0.01, y=1.0,
                 ha="left", fontsize=14, fontweight="bold")
    fig.text(0.01, 0.955, "Cada franja es un grupo: los deciles 1 a 9 y el decil 10 partido en tres. A la izquierda, qué parte "
             "de la población es; en el medio, qué parte del ingreso total recibe; a la derecha, qué parte de lo\n"
             "recaudado paga. Si una franja tiene el mismo ancho en el medio y a la derecha, el grupo paga impuestos en "
             "proporción a su ingreso.", fontsize=9.4, color=TINTA2, va="top")
    fig.text(0.01, 0.02, FUENTE + " Versión A.", fontsize=7.3, color=MUDO, va="top")
    g.guardar(fig, archivo, carpeta or OUT)


if __name__ == "__main__":
    largo, tot, ancho, tramos, trimestres = inf.cargar()
    f0 = pd.read_csv(TABLES / "tasas_tramos_decil10_fig0.csv")
    OUT.mkdir(parents=True, exist_ok=True)
    for f in OUT.glob("*"):
        f.unlink()
    reusar(inf, inf.c1_comparacion, "f01_comparacion", largo, tramos)
    f02_deciles(largo)
    f03_anios(largo)
    f04_composicion(ancho)
    reusar(inf, inf.c2_canastas, "f05_canastas", tramos)
    c, mediana = f06_canastas_tiempo(tramos)
    f07_parte_ingreso(tramos)
    f08_version_a(largo, tramos)
    f09_version_b(largo, f0)
    reusar(inf, inf.i6_composicion, "f10_composicion_1pct", ancho, tramos)
    f11_anios_partido(largo, tramos)
    reusar(inf, inf.i9_matriz_deltas, "f12_matriz_deltas", tramos)
    todas = todas_variantes(tramos, f0)
    kp, ref = f13_kakwani(tramos, todas)
    reusar(inf, inf.i3_mapa, "f14_mapa_calor", tramos)
    from incidencia.indirectos import cargar_insumos  # noqa: E402
    _, rec = cargar_insumos()
    b = bre.brechas(bre.cargar(), rec)
    f15_brecha_grupos(b)
    f16_brecha_1pct(b)
    f17_deltas_2025(tramos)
    v = f18_veces(tramos)
    w = tasas_por_variante(todas)
    f19_rangos(w)
    f20_distancias(w)
    f_flujo(tramos)
    cl = por_clase(tramos)
    bc = brecha_por_clase(b)
    pd.set_option("display.width", 200)
    print(cl[cl.anio.isin([2004, 2013, 2019, ANIO_FIN])].round(1)[["anio", "clase", "part_ingreso", "part_impuestos", "tasa"]].to_string())
    print(bc[bc.anio == ANIO_FIN].round(2).to_string())
    print(bc[bc.anio >= 2016].groupby("clase")[["prop_musd", "prog_musd"]].sum().round(0))
    print("Gráficos en", OUT)
    print("límite clase alta (canastas):", (2 * mediana).round(2).loc[[2004, 2015, 2019, ANIO_FIN]].to_dict(),
          "75% mediana:", (0.75 * mediana).round(2).loc[[2004, ANIO_FIN]].to_dict())
    print("D9, D10 canastas:", c[[9, 10]].round(2).loc[[2004, ANIO_FIN]].to_dict())
    print("Kakwani referencia 0,25:", ref[0.25].round(3).loc[[2004, 2016, 2022, ANIO_FIN]].to_dict(),
          "rango", round(ref[0.15].min(), 3), round(ref[0.40].max(), 3))
    print(v.round(1).loc[[2004, 2007, 2011, 2015, 2019, 2023, ANIO_FIN]].to_string())
