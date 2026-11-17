#!/usr/bin/env python
"""Gráficos del informe (docs/informe.md): la tasa efectiva a lo largo de los años.

Salida: outputs/figures/informe/ (PNG y SVG). Todo sale de las tablas de outputs/tables/ (no
corre la microsimulación). Usa el estilo de 07_graficos.py.

  i1_serie                 deciles 1 y 10, promedio y 1% más rico; franja con los deciles 2 a 9.
  i2_anios                 barras por impuesto de cada decil y del 1% en 2004, 2013, 2019 y el último año.
  i3_distancia_promedio    decil 1 y decil 10 menos el promedio, en puntos, con banda de variantes.
  i4_mapa_calor            año × grupo (D1-D9, P90-95, P95-99, 1%): desvío contra el promedio del año.
  i5_supuestos             como fig5, en los mismos cuatro años, con el cheque y el ingreso no declarado.
  i6_composicion           impuesto por impuesto del decil 1, el 5, el 10 y el 1%, año por año.
  i7_ricos_pobres          fig6 de 07_graficos.py: distancia de ingresos antes y después de impuestos.
  i8_decil10_partido       fig8 de 07_graficos.py para el último año.
  i9_matriz_deltas         año × grupo: parte de los impuestos menos la de un reparto proporcional y uno progresivo.
  a1_progresividad         índice de Kakwani por año (anexo).
  a2_recaudado_consumo     IVA, Ingresos Brutos e Internos recaudados por peso de consumo (anexo).
  a3_cobertura             qué parte de la recaudación total cubre el estudio (anexo).
"""
import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("graficos", RAIZ / "scripts" / "07_graficos.py")
g = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(g)          # estilo, colores y utilidades (no corre su main)
plt, matplotlib = g.plt, g.matplotlib
from incidencia.config import ANIO_FIN, PROCESSED, TABLES  # noqa: E402

OUT = g.FIGURES / "informe"
ROJO, AZUL, OSCURO, GRIS = "#e34948", "#2a78d6", "#0b3d7a", "#9a998f"
CELESTE, MEDIO = "#a9cdf2", "#4f93dc"
# matrices (mapa de calor y deltas): azul = paga más, rojo = paga menos; extremos igual de oscuros
MAPA_DIV = matplotlib.colors.LinearSegmentedColormap.from_list("div", ["#8c1716", ROJO, "#f4f3ef", MEDIO, OSCURO])
ENGHO = [2005, 2012, 2018]           # anclas de las ediciones de la ENGHo (2004/05, 2012/13, 2017/18)
# variantes que miden otra cosa o no son válidas: fuera de las bandas (docs/metodologia.md)
OTRA_MEDIDA = {"sobre_consumo", "recursos_gasto", "altos_registros", "sobre_ipcf"}
NOTA = ("Fuente: elaboración propia con EPH, ENGHo e IPC (INDEC), recaudación DNIAF y anuarios de ARCA. "
        "Aglomerados urbanos de la EPH; personas ordenadas por ingreso per cápita familiar. Impuestos: Ganancias "
        "y Bienes Personales,\naportes y contribuciones, IVA, Internos e Ingresos Brutos. Ingreso declarado antes de "
        "impuestos directos, completado arriba con el ingreso que se declara al fisco y la encuesta no capta.")


def guardar(fig, nombre):
    g.guardar(fig, nombre, OUT)


def ejes_tiempo(ax, paso=3, indec=True, engho=False):
    """Eje de años con el período de intervención del INDEC sombreado y las ediciones de la ENGHo."""
    if indec:
        ax.axvspan(2006.5, 2015.5, color="#f0efec", zorder=0, linewidth=0)
    if engho:
        for a in ENGHO:
            ax.axvline(a, color=g.EJE, linewidth=0.9, linestyle=(0, (1, 2)), zorder=1)
    ax.set_xlim(2003.5, ANIO_FIN + 0.5)
    ax.set_xticks(range(2004, ANIO_FIN + 1, paso))
    ax.xaxis.grid(False)


def etiquetas_finales(ax, valores, sep, x=None, fmt=lambda v: f"{g.pct(v)}%"):
    """valores: {etiqueta: (y, color)}; las pone a la derecha sin superponerse."""
    x = ANIO_FIN + 0.4 if x is None else x
    pos, ult = {}, -1e9
    for k, (v, c) in sorted(valores.items(), key=lambda kv: kv[1][0]):
        pos[k] = max(v, ult + sep)
        ult = pos[k]
    for k, yy in pos.items():
        v, c = valores[k]
        ax.text(x, yy, f"{k}  {fmt(v)}", fontsize=8.6, va="center", color=c, fontweight="bold")


def cargar():
    largo = pd.read_csv(TABLES / "tasas_por_decil_anual.csv")
    tot = largo[largo.impuesto == "total"].pivot_table(index=["variante", "anio"], columns="decil", values="tasa") * 100
    ancho = pd.read_csv(TABLES / "tasas_por_decil_anual_ancho.csv")
    tramos = pd.read_csv(TABLES / "tasas_tramos_decil10.csv")
    trimestres = ancho[ancho.decil == 0].set_index("anio").trimestres
    return largo, tot, ancho, tramos, trimestres


def i1_serie(tot, trimestres, tramos):
    p = tot.loc["principal"]
    top = tramos[(tramos.variante == "principal") & (tramos.grupo == 99)].set_index("anio").total * 100
    fig, ax = plt.subplots(figsize=(11, 5.8))
    ejes_tiempo(ax, engho=True)
    medios_min, medios_max = p[list(range(2, 10))].min(axis=1), p[list(range(2, 10))].max(axis=1)
    ax.fill_between(p.index, medios_min, medios_max, color=GRIS, alpha=0.35, linewidth=0)
    parc = trimestres < 4
    series = [(p[1], "Decil 1 (más pobre)", ROJO, 2.6), (p[10], "Decil 10 (más rico)", AZUL, 2.6),
              (p[0], "Promedio", g.TINTA, 2.0)]
    for y, nombre, color, lw in series:
        ax.plot(y.index, y, color=color, linewidth=lw, linestyle=(0, (5, 2)) if nombre == "Promedio" else "-")
        ax.scatter(y.index[parc.values], y[parc.values], s=40, facecolor=g.SUP, edgecolor=color, linewidth=1.5, zorder=3)
    ax.plot(top.index, top, color=OSCURO, linewidth=1.8, linestyle=(0, (1, 1.2)))
    fin = {n: (y.iloc[-1], c) for y, n, c, _ in series}
    fin["1% más rico"] = (top.iloc[-1], OSCURO)
    fin["Deciles 2 a 9"] = ((medios_min.iloc[-1] + medios_max.iloc[-1]) / 2, "#6f6e66")
    etiquetas_finales(ax, fin, 1.3)
    ax.set_ylim(15, 45)
    ax.set_ylabel("Impuestos, % del ingreso")
    ax.text(2011, 44.2, "INDEC intervenido (2007-2015)", ha="center", fontsize=8, color=g.MUDO)
    d1, pr = p[1], p[0]
    fig.suptitle(f"Qué parte de su ingreso pagó cada grupo en impuestos, 2004-{ANIO_FIN}", x=0.01, y=1.04, ha="left",
                 fontsize=14, fontweight="bold")
    ax.set_title(f"La carga promedio subió de {g.pct(pr.iloc[0])}% en 2004 a {g.pct(pr.max())}% en {int(pr.idxmax())} y "
                 f"bajó a {g.pct(pr.iloc[-1])}% en {ANIO_FIN}. El decil 1 pagó más que todos en "
                 f"{int((d1 > p[list(range(2, 11))].max(axis=1)).sum())} de {len(p)} años;\nlos deciles 2 a 9 (franja gris) "
                 f"pagan casi lo mismo entre sí. El 1% más rico (punteado) pagó entre {g.pct(top.min())}% y "
                 f"{g.pct(top.max())}%: más que el decil 10 en {int((top > p[10]).sum())} años y menos en "
                 f"{int((top < p[10]).sum())}.\nCírculos huecos: años con trimestres faltantes. Punteado vertical: "
                 "ediciones de la ENGHo.", loc="left", fontsize=9.3, color=g.TINTA2, pad=10)
    fig.subplots_adjust(right=0.8)
    fig.text(0.01, -0.02, NOTA, fontsize=7.2, color=g.MUDO, ha="left", va="top")
    guardar(fig, "i1_serie")


def bandas(tot, decil, excluir=OTRA_MEDIDA):
    v = tot[~tot.index.get_level_values(0).isin(excluir)]
    d = (v[decil] - v[0]).unstack(0)
    return d.min(axis=1), d.max(axis=1)


def i2_distancia(tot):
    p = tot.loc["principal"]
    fig, ax = plt.subplots(figsize=(11, 5.6))
    ejes_tiempo(ax, engho=True)
    ax.axhline(0, color=g.TINTA2, linewidth=1)
    fin = {}
    for dec, nombre, color in [(1, "Decil 1", ROJO), (10, "Decil 10", AZUL)]:
        lo, hi = bandas(tot, dec)
        ax.fill_between(lo.index, lo, hi, color=color, alpha=0.13, linewidth=0)
        y = p[dec] - p[0]
        ax.plot(y.index, y, color=color, linewidth=2.6)
        fin[nombre] = (y.iloc[-1], color)
    etiquetas_finales(ax, fin, 1.2, fmt=lambda v: f"{'+' if v >= 0 else '−'}{g.pct(abs(v))}")
    ax.set_ylabel("Puntos por encima (+) o por debajo (−) del promedio")
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:.0f}"))
    ax.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(2))
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:+.0f}".replace("-", "−") if v else "0"))
    y1 = p[1] - p[0]
    fig.suptitle("La distancia del decil más pobre al promedio se achicó; la del más rico oscila alrededor de cero",
                 x=0.01, y=1.04, ha="left", fontsize=13.5, fontweight="bold")
    ax.set_title(f"El decil 1 pagaba {g.pct(y1.iloc[0])} puntos más que el promedio en 2004 y {g.pct(y1.iloc[-1])} en "
                 f"{ANIO_FIN}. Franjas: rango entre supuestos. El valor de 2009 depende de cómo se\n"
                 "combinan las ediciones de la ENGHo (punteado vertical): con otra forma de combinarlas el decil 1 da 4,9 "
                 "puntos en vez de 12,9. Lo firme es la tendencia.", loc="left", fontsize=9.3, color=g.TINTA2, pad=10)
    fig.subplots_adjust(right=0.85)
    fig.text(0.01, -0.02, NOTA + "\nFranjas: mínimo y máximo entre las variantes de supuestos que miden lo mismo "
             "(excluye la lectura contra el consumo y la que usa el gasto como ingreso del decil 1).",
             fontsize=7.2, color=g.MUDO, ha="left", va="top")
    guardar(fig, "i3_distancia_promedio")


def i3_mapa(tramos):
    pr = tramos[tramos.variante == "principal"]
    m = pr.pivot(index="grupo", columns="anio", values="total") * 100
    d = m.drop(index=0) - m.loc[0]
    orden = [99, 95, 91] + list(range(9, 0, -1))
    d = d.loc[orden]
    nombres = {99: "1% superior", 95: "P95-99", 91: "P90-95"} | {k: f"Decil {k}" for k in range(1, 10)}
    fig, ax = plt.subplots(figsize=(13.5, 5.6))
    vmin, vmax = -5, 10                  # como la matriz de deltas: escala al rango de los datos, blanco en 0
    im = ax.imshow(d.values, cmap=MAPA_DIV, norm=matplotlib.colors.TwoSlopeNorm(vmin=vmin, vcenter=0, vmax=vmax),
                   aspect="auto")
    for i in range(d.shape[0]):
        for j in range(d.shape[1]):
            v = d.values[i, j]
            r = int(round(v))
            ax.text(j, i, "0" if r == 0 else f"{r:+d}".replace("-", "−"), ha="center", va="center", fontsize=7.6,
                    color="white" if (v < vmin * 0.6 or v > vmax * 0.6) else g.TINTA)
    ax.set_xticks(range(d.shape[1]))
    ax.set_xticklabels([str(a) for a in d.columns], fontsize=8.2)
    ax.set_yticks(range(d.shape[0]))
    ax.set_yticklabels([nombres[k] for k in d.index], fontsize=9)
    ax.axhline(2.5, color=g.TINTA, linewidth=1.2)
    ax.grid(False)
    for s_ in ax.spines.values():
        s_.set_visible(False)
    cb = fig.colorbar(im, ax=ax, fraction=0.025, pad=0.01)
    cb.set_ticks([vmin, vmin / 2, 0, vmax / 2, vmax])
    cb.ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(
        lambda v, _: f"{v:+.1f}".replace(".0", "").replace(".", ",").replace("-", "−") if v else "0"))
    cb.set_label("Puntos respecto del promedio del año", fontsize=8.5, color=g.TINTA2)
    cb.outline.set_visible(False)
    fig.suptitle("Quién paga más que el promedio, año por año", x=0.01, y=1.03, ha="left", fontsize=14,
                 fontweight="bold")
    fig.text(0.01, 0.975, "Cada celda: tasa del grupo menos la tasa promedio de ese año, en puntos. Azul: paga más que "
             "el promedio; rojo: menos. Arriba de la línea, el decil 10 partido en tres.\nEl decil 1 paga más que "
             "todos casi siempre; la cima alterna entre pagar más (2009-2015, 2020-2022) y menos (2016-2019, 2024-2025).",
             fontsize=9.3, color=g.TINTA2, va="top")
    fig.text(0.01, 0.02, NOTA + " Tramos del decil 10 con pocas observaciones: el 1% superior es ruidoso de un año a otro.",
             fontsize=7.2, color=g.MUDO, ha="left", va="top")
    fig.subplots_adjust(top=0.86, bottom=0.1)
    guardar(fig, "i4_mapa_calor")


def composicion(paneles, nombre, titulo, sub, ymax=48):
    """Stackplot impuesto por impuesto de varios grupos a lo largo de los años (colores de 07_graficos.py)."""
    fig, axs = plt.subplots(1, len(paneles), figsize=(4.75 * len(paneles), 5.6), sharey=True)
    for ax, (tit, d) in zip(axs, paneles):
        ejes_tiempo(ax, paso=7, indec=False)
        ax.set_xticks([2005, 2010, 2015, 2020, 2025])
        ys = [d[c] * 100 for c in g.COLS]
        ax.stackplot(d.index, ys, colors=[c for _, _, c in g.IMPUESTOS], linewidth=0.4, edgecolor=g.SUP)
        total = sum(ys)
        ax.plot(d.index, total, color=g.TINTA, linewidth=1)
        f = d.loc[ANIO_FIN] * 100
        consumo = f[["contrib_consumidor", "iva", "internos", "iibb"]].sum()
        directo = f[["ganancias", "bienes_personales"]].sum()
        ax.set_title(f"{tit}\n{g.pct(total.iloc[0])}% en 2004 → {g.pct(total.iloc[-1])}% en {ANIO_FIN}", loc="left",
                     fontsize=10.5, fontweight="bold")
        ax.text(0.02, 0.98, f"En {ANIO_FIN}, puntos de: consumo {g.pct(consumo)}; aportes y contrib. "
                f"{g.pct(f[['aportes', 'contrib_trabajador']].sum())};\nGanancias y Bienes Personales {g.pct(directo)}",
                transform=ax.transAxes, fontsize=7.8, color=g.TINTA2, va="top")
    axs[0].set_ylabel("% del ingreso")
    axs[0].set_ylim(0, ymax)
    handles = [g.Patch(facecolor=c, label=n.replace(" (imputado a ingresos altos)", ""))
               for col, n, c in g.IMPUESTOS][::-1]
    fig.legend(handles=handles, loc="lower center", ncol=8, fontsize=8.6, frameon=False, bbox_to_anchor=(0.5, -0.04))
    fig.suptitle(titulo, x=0.01, y=1.04, ha="left", fontsize=14, fontweight="bold")
    fig.text(0.01, 0.985, sub, fontsize=9.3, color=g.TINTA2, va="top")
    fig.subplots_adjust(wspace=0.07, top=0.8, bottom=0.14)
    fig.text(0.01, -0.07, NOTA, fontsize=7.2, color=g.MUDO, ha="left", va="top")
    guardar(fig, nombre)


def i6_composicion(ancho, tramos):
    pr = ancho.set_index(["anio", "decil"])
    top = tramos[(tramos.variante == "principal") & (tramos.grupo == 99)].set_index("anio")
    paneles = [("Decil 1 (más pobre)", pr.xs(1, level="decil")), ("Decil 5", pr.xs(5, level="decil")),
               ("Decil 10 (más rico)", pr.xs(10, level="decil")), ("1% más rico", top)]
    composicion(paneles, "i6_composicion", "Qué impuestos paga cada grupo, año por año",
                "Al decil 1 casi todo le llega por el consumo: IVA, Ingresos Brutos, Internos y la mitad de las "
                "contribuciones patronales que pasa a precios. Al decil 5, además, aportes y contribuciones de su salario. "
                "Al decil 10 y al 1%,\nGanancias y Bienes Personales. Por eso la carga de abajo sube y baja con lo que se "
                "recauda por peso de consumo, y la de arriba con Ganancias y Bienes Personales.")


def c3_composicion_tramos(ancho, tramos):
    """Lo mismo adentro del decil 10: el decil 9 de referencia y los tres tramos."""
    pr = ancho.set_index(["anio", "decil"])
    t = tramos[tramos.variante == "principal"].set_index(["anio", "grupo"])
    paneles = [("Decil 9 (referencia)", pr.xs(9, level="decil")), ("Percentiles 90-95", t.xs(91, level="grupo")),
               ("Percentiles 95-99", t.xs(95, level="grupo")), ("1% más rico", t.xs(99, level="grupo"))]
    composicion(paneles, "c3_composicion_tramos", "Adentro del 10% más rico, cada tramo paga con impuestos distintos",
                "Los percentiles 90-95 pagan como el decil 9: aportes, contribuciones y consumo, con algo de Ganancias. "
                "Cuanto más arriba, más pesa Ganancias y menos el resto. En el 1%, Ganancias y Bienes Personales son\n"
                "más de la mitad de lo que paga: por eso su tasa sube y baja con esos dos impuestos, mientras la de los "
                "percentiles 90-95 se mueve menos.")


ANIOS = [2004, 2013, 2019, ANIO_FIN]      # inicio, máximo del promedio, mínimo de 2019 y último año


def i2_anios(largo, tramos):
    """Barras por impuesto de cada decil y del 1% más rico, en cuatro años, como el panel A de fig0."""
    fig, axs = plt.subplots(1, len(ANIOS), figsize=(24, 6.6), sharey=True)
    prom = {}
    for ax, a in zip(axs, ANIOS):
        v = largo[(largo.anio == a) & (largo.variante == "principal")].pivot(index="decil", columns="impuesto",
                                                                            values="tasa") * 100
        d = v.loc[1:10, g.COLS].copy()
        tr = tramos[(tramos.variante == "principal") & (tramos.anio == a)].set_index("grupo")
        for k, gr in zip((11, 12, 13), (91, 95, 99)):    # el decil 10 partido, separado por un hueco
            d.loc[k] = tr.loc[gr, g.COLS] * 100
        x = list(range(10)) + [10.9, 11.9, 12.9]
        base = pd.Series(0.0, index=d.index)
        for col, etq, color in g.IMPUESTOS:
            ax.bar(x, d[col], bottom=base, color=color, width=0.74, label=etq, edgecolor=g.SUP, linewidth=1,
                   hatch="////" if col == "bienes_personales" else None)
            base = base + d[col]
        for xi, b in zip(x, base):
            ax.text(xi, b + 0.5, g.pct(b), ha="center", va="bottom", fontsize=8.6,
                    fontweight="bold" if xi in (0, 9, 12.9) else None, color=g.TINTA)
        ax.axvspan(10.35, 13.5, color="#e8f0fb", zorder=0, linewidth=0)
        prom[a] = v.loc[0, "total"]
        ax.axhline(prom[a], color=g.TINTA2, linewidth=1, linestyle=(0, (4, 3)))
        ax.set_xticks(x)
        ax.set_xticklabels([f"D{i}" for i in range(1, 11)] + ["P90-\n95", "P95-\n99", "1%"], fontsize=8.2)
        ax.set_xlim(-0.6, 13.5)
        ax.xaxis.grid(False)
        ax.set_title(str(a), loc="left", fontsize=13, fontweight="bold")
        ax.set_title(f"promedio {g.pct(prom[a])}% (línea punteada)", loc="right", fontsize=9, color=g.TINTA2)
    axs[0].set_ylabel("% del ingreso")
    axs[0].set_ylim(0, 45)
    h, l = axs[0].get_legend_handles_labels()
    fig.legend(h[::-1], [x.replace(" (imputado a ingresos altos)", "") for x in l[::-1]], loc="lower center", ncol=8,
               frameon=False, fontsize=9, bbox_to_anchor=(0.5, -0.04))
    fig.suptitle("Qué parte de su ingreso pagó cada decil en impuestos, en cuatro años", x=0.01, y=1.04, ha="left",
                 fontsize=14, fontweight="bold")
    fig.text(0.01, 0.985, f"{ANIOS[0]}, el comienzo; {ANIOS[1]}, el año de carga promedio más alta; {ANIOS[2]}, el "
             f"punto bajo antes de la pandemia; {ANIOS[3]}, el último. En los cuatro el decil 1 paga más que todos, sobre "
             "todo por el consumo (rojo, violeta y verde),\ny del decil 2 al 10 la carga es pareja. Lo que cambia arriba "
             "es Ganancias y Bienes Personales (azul y naranja), que en 2013 pesaban mucho más que en 2019. A la derecha "
             "de cada año, el decil 10 partido: percentiles 90-95, 95-99 y el 1% más rico.", fontsize=9.3, color=g.TINTA2, va="top")
    fig.subplots_adjust(wspace=0.05, top=0.83, bottom=0.12)
    fig.text(0.01, -0.07, NOTA + " Ingreso declarado en la encuesta (medida principal); el gráfico de supuestos muestra "
             "cuánto cambia con el ingreso no declarado.", fontsize=7.2, color=g.MUDO, ha="left", va="top")
    guardar(fig, "i2_anios")


def i5_supuestos(largo):
    """Como fig5, en los cuatro años: rango por supuestos, medida principal, con cheque e ingreso no declarado."""
    incid = ["principal", "iva_legal", "contrib_100_trabajador", "contrib_100_consumidor", "altos_sin_corregir",
             "sin_bienes_personales"]
    fig, axs = plt.subplots(1, len(ANIOS), figsize=(22, 5.6), sharey=True)
    x = list(range(1, 11))
    for ax, a in zip(axs, ANIOS):
        v = largo[(largo.anio == a) & (largo.impuesto == "total") & (largo.decil > 0)]
        v = v.pivot(index="decil", columns="variante", values="tasa") * 100
        lo, hi = v[incid].min(axis=1), v[incid].max(axis=1)
        ax.bar(x, hi - lo, bottom=lo, width=0.56, color="#b9d4f4", edgecolor="none",
               label="Rango por supuestos de incidencia (traslado de contribuciones, IVA legal o recaudado,\n"
                     "sin corregir los ingresos altos, sin Bienes Personales)")
        ax.scatter(x, v["con_cheque"], s=46, marker="^", facecolor=g.SUP, edgecolor="#6f6e66", linewidth=1.5, zorder=3,
                   label="Con el impuesto al cheque (trasladado a precios)")
        ax.scatter(x, v["ajuste_cn_rentas_activos_ext"], s=40, marker="D", color=AZUL, zorder=3,
                   label="Con el ingreso no declarado: Cuentas Nacionales, rentas ×7 y activos externos")
        ax.scatter(x, v["principal"], s=56, color=g.TINTA, zorder=4, label="Medida principal")
        ax.text(1.42, v["principal"][1], g.pct(v["principal"][1]), va="center", ha="left", fontsize=8.4,
                color=g.TINTA, fontweight="bold")
        ax.text(10, hi[10] + 0.5, g.pct(v["principal"][10]), va="bottom", ha="center", fontsize=8.4, color=g.TINTA,
                fontweight="bold")
        ax.set_xticks(x)
        ax.set_xticklabels([f"D{i}" for i in x], fontsize=8.6)
        ax.xaxis.grid(False)
        ax.set_title(str(a), loc="left", fontsize=13, fontweight="bold")
    axs[0].set_ylim(15, 47)
    axs[0].set_ylabel("Impuestos, % del ingreso")
    h, l = axs[0].get_legend_handles_labels()
    orden = [3, 0, 1, 2]
    fig.legend([h[i] for i in orden], [l[i] for i in orden], loc="lower center", ncol=4, frameon=False, fontsize=8.8,
               bbox_to_anchor=(0.5, -0.07))
    fig.suptitle("Cuánto depende el resultado de los supuestos", x=0.01, y=1.04, ha="left", fontsize=14,
                 fontweight="bold")
    fig.text(0.01, 0.985, "En los cuatro años y con cualquier supuesto, el decil 1 paga más que los demás. El cheque "
             "(triángulos) suma más abajo que arriba: agranda la distancia. Lo que más mueve la punta de arriba es cómo "
             "se mide el ingreso:\ncon el ingreso que nadie declara (rombos) el decil 10 queda debajo del resto en 2004, 2019 y 2025. "
             "La punta de abajo depende sobre todo de a quién se le carga la contribución patronal.",
             fontsize=9.3, color=g.TINTA2, va="top")
    fig.subplots_adjust(wspace=0.05, top=0.83, bottom=0.12)
    fig.text(0.01, -0.12, NOTA, fontsize=7.2, color=g.MUDO, ha="left", va="top")
    guardar(fig, "i5_supuestos")


def deltas_referencia(tramos):
    """Por año y grupo: % de los impuestos que paga − % que pagaría con un reparto proporcional o progresivo
    de la misma recaudación (mismo cálculo que los paneles derechos de fig8)."""
    g2 = list(range(1, 10)) + [91, 95, 99]
    filas = []
    for a, d in tramos[tramos.variante == "principal"].groupby("anio"):
        d = d.set_index("grupo")
        yrel = d.canastas_por_persona[g2] / d.canastas_por_persona[0]
        peso = d.part_ingreso[g2] * yrel ** g.ELAST_PROG
        ref_prog = peso / peso.sum()
        for k in g2:
            filas.append({"anio": a, "grupo": k, "delta_proporcional": (d.part_impuestos[k] - d.part_ingreso[k]) * 100,
                          "delta_progresivo": (d.part_impuestos[k] - ref_prog[k]) * 100})
    return pd.DataFrame(filas)


PERIODOS_CIMA = [(2009, 2013, "la cima paga más", OSCURO), (2016, 2019, "la cima paga menos", "#8c1716"),
                 (2020, 2022, "paga más", OSCURO), (2024, 2025, "paga menos", "#8c1716")]


def i9_matriz_deltas(tramos):
    dl = deltas_referencia(tramos)
    dl.round(3).to_csv(TABLES / "deltas_proporcional_progresivo.csv", index=False)
    orden = [99, 95, 91] + list(range(9, 0, -1))
    nombres = {99: "1% superior", 95: "P95-99", 91: "P90-95"} | {k: f"Decil {k}" for k in range(1, 10)}
    cmap = MAPA_DIV
    fig, axs = plt.subplots(2, 1, figsize=(15, 11.8))
    paneles = [("delta_proporcional", (-1.0, 1.0), "Frente a un sistema proporcional (todos pagan la tasa promedio)",
                "Cada celda: % de los impuestos que paga el grupo − % del ingreso que tiene, en puntos."),
               ("delta_progresivo", (-10.0, 5.0), "Frente a un sistema progresivo (la tasa sube con el ingreso, misma recaudación)",
                "Cada celda: % de los impuestos que paga el grupo − % que pagaría si la tasa fuera el promedio × "
                "(ingreso relativo)^0,25.")]
    for ax, ((vmin, vmax), col, titulo, sub) in zip(axs, [(p_[1], p_[0], p_[2], p_[3]) for p_ in paneles]):
        m = dl.pivot(index="grupo", columns="anio", values=col).loc[orden]
        norma = matplotlib.colors.TwoSlopeNorm(vmin=vmin, vcenter=0, vmax=vmax)   # el blanco siempre en 0
        im = ax.imshow(m.values, cmap=cmap, norm=norma, aspect="auto")
        dec = 1 if vmax > 2 else 2
        for i in range(m.shape[0]):
            for j in range(m.shape[1]):
                v = m.values[i, j]
                txt = f"{v:+.{dec}f}".replace(".", ",").replace("-", "−")
                if round(v, dec) == 0:
                    txt = "0"
                ax.text(j, i, txt, ha="center", va="center", fontsize=6.9 if dec == 2 else 7.6,
                        color="white" if (v < vmin * 0.6 or v > vmax * 0.6) else g.TINTA)
        ax.set_xticks(range(m.shape[1]))
        ax.set_xticklabels([str(a) for a in m.columns], fontsize=8.2)
        ax.set_yticks(range(m.shape[0]))
        ax.set_yticklabels([nombres[k] for k in m.index], fontsize=9)
        ax.axhline(2.5, color=g.TINTA, linewidth=1.2)
        ax.grid(False)
        for s_ in ax.spines.values():
            s_.set_visible(False)
        if col == "delta_proporcional":            # períodos en que la cima se aleja de lo proporcional
            c0 = int(m.columns[0])
            for a0, a1, txt, color in PERIODOS_CIMA:
                ax.plot([a0 - c0 - 0.42, a1 - c0 + 0.42], [-0.85, -0.85], color=color, linewidth=3,
                        solid_capstyle="butt", clip_on=False)
                ax.text((a0 + a1) / 2 - c0, -1.05, txt, ha="center", va="bottom", fontsize=8.2, color=color,
                        fontweight="bold", clip_on=False)
            ax.set_ylim(m.shape[0] - 0.5, -0.5)
        cb = fig.colorbar(im, ax=ax, fraction=0.025, pad=0.01)
        cb.set_ticks(np.linspace(vmin, vmax, 5) if vmax == -vmin else [vmin, vmin / 2, 0, vmax / 2, vmax])
        cb.ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(
            lambda v, _: (f"{v:+.{dec}f}".replace(".", ",").replace("-", "−")) if v else "0"))
        cb.set_label("Puntos de la recaudación", fontsize=8.5, color=g.TINTA2)
        cb.outline.set_visible(False)
        ax.set_title(f"{titulo}\n\n" if col == "delta_proporcional" else f"{titulo}\n", loc="left", fontsize=11.5,
                     fontweight="bold")
        ax.text(0, 1.015 if col != "delta_proporcional" else 1.075, sub, transform=ax.transAxes, fontsize=8.8, color=g.TINTA2, va="bottom")
    fig.suptitle("Cuánto más o menos de los impuestos paga cada grupo que en un sistema proporcional o progresivo",
                 x=0.01, y=1.0, ha="left", fontsize=14, fontweight="bold")
    fig.text(0.01, 0.975, "Azul: paga una parte mayor de la recaudación que en el sistema de referencia; rojo: menor. "
             "Escalas distintas: frente al proporcional los desvíos son de décimas (el sistema real es casi proporcional);\n"
             "frente al progresivo, de varios puntos: los deciles 1 a 8 pagan más de lo que les tocaría y la cima, sobre "
             "todo el 1%, bastante menos. Arriba de la línea, el decil 10 partido en tres.",
             fontsize=9.3, color=g.TINTA2, va="top")
    fig.subplots_adjust(top=0.86, hspace=0.34)
    fig.text(0.01, 0.05, NOTA + " Tramos del decil 10 con pocas observaciones: el 1% superior es ruidoso de un año a "
             "otro. Tabla: outputs/tables/deltas_proporcional_progresivo.csv.",
             fontsize=7.2, color=g.MUDO, ha="left", va="top")
    guardar(fig, "i9_matriz_deltas")


# ---------- comparación con otros estudios (sección 1) y canastas (sección 2) ----------
EXT = RAIZ / "data" / "externos"
CATS = [("ganancias", "Ganancias de personas", AZUL), ("sociedades", "Ganancias de sociedades", OSCURO),
        ("patrimonio", "Bienes Personales y patrimonio", "#eb6834"), ("ss", "Aportes y contribuciones", "#1baf7a"),
        ("consumo", "Impuestos al consumo", "#d9a441")]


def a_categorias(d):
    """Tasas por impuesto del proyecto (en %) a las cinco categorías comunes de la comparación."""
    return pd.DataFrame({"ganancias": d.ganancias, "sociedades": 0.0, "patrimonio": d.bienes_personales,
                         "ss": d.aportes + d.contrib_trabajador + d.contrib_consumidor,
                         "consumo": d.iva + d.internos + d.iibb + d.cheque + d.combustibles}) * 100


def apilar(ax, x, d, ancho=0.72, etiquetas=True, alfa=1.0):
    base = np.zeros(len(d))
    for col, etq, color in CATS:
        v = d[col].values
        ax.bar(x, v, bottom=base, color=color, width=ancho, label=etq, edgecolor=g.SUP, linewidth=0.8, alpha=alfa)
        base = base + v
    if etiquetas:
        for xi, b in zip(x, base):
            ax.text(xi, b + 0.5, g.pct(b), ha="center", va="bottom", fontsize=8.4, color=g.TINTA)
    return base


def c1_comparacion(largo, tramos):
    arg = pd.read_csv(EXT / "argendata_presion_por_decil_2018.csv").pivot(index="decil", columns="categoria",
                                                                           values="valor")
    arg = pd.DataFrame({"ganancias": arg["Ganancias personales y corporativas"], "sociedades": 0.0, "patrimonio": 0.0,
                        "ss": arg["Aportes y contribuciones a la seguridad social"],
                        "consumo": arg["IVA"] + arg["En cascada"] + arg["Otros impuestos indirectos"]})
    ito = pd.read_csv(EXT / "ito_2026_argentina.csv").set_index("grupo")
    ito = ito.rename(columns={"ganancias_personas": "ganancias", "seguridad_social": "ss", "indirectos": "consumo"})
    def nuestro(anio, variante="principal"):
        v = largo[(largo.anio == anio) & (largo.variante == variante) & (largo.decil > 0)]
        return a_categorias(v.pivot(index="decil", columns="impuesto", values="tasa"))
    t = tramos[(tramos.variante == "principal") & (tramos.anio == 2019)].set_index("grupo")
    grupos = {"bottom50": [1, 2, 3, 4, 5], "middle40": [6, 7, 8, 9], "top10": [91, 95, 99], "top1": [99]}
    filas = {}
    for k, gr in grupos.items():
        w = t.part_ingreso[gr]
        filas[k] = (t.loc[gr, g.COLS + ["cheque", "combustibles"]].mul(w, axis=0).sum() / w.sum())
    nos_g = a_categorias(pd.DataFrame(filas).T)
    cheque18 = largo[(largo.anio == 2018) & (largo.variante == "con_cheque") & (largo.decil > 0) &
                     (largo.impuesto == "total")].set_index("decil").tasa * 100

    fig, axs = plt.subplots(1, 3, figsize=(22, 6.6), gridspec_kw={"width_ratios": [1, 1, 0.95]}, sharey=True)
    x = np.arange(10)
    apilar(axs[0], x, arg)
    axs[0].set_title("A. Argendata / Fundar (Pessino et al.), 2018", loc="left", fontsize=11.5, fontweight="bold")
    apilar(axs[1], x, nuestro(2018), etiquetas=False)
    tot18 = nuestro(2018).sum(axis=1)
    for xi, (b, c) in enumerate(zip(tot18, cheque18)):
        axs[1].text(xi, b - 0.3, g.pct(b), ha="center", va="top", fontsize=8.4, color=g.TINTA)   # dentro de la barra
        axs[1].text(xi, c + 0.35, g.pct(c), ha="center", va="bottom", fontsize=7.4, color=g.MUDO)    # el de la raya
    axs[1].scatter(x, cheque18, marker="_", s=260, color=g.TINTA, linewidth=2.2, zorder=5,
                   label="Con el impuesto al cheque")
    axs[1].set_title("B. Este estudio, 2018", loc="left", fontsize=11.5, fontweight="bold")
    for ax in axs[:2]:
        ax.set_xticks(x)
        ax.set_xticklabels([f"D{i}" for i in range(1, 11)], fontsize=9)
        ax.set_xlabel("Deciles de ingreso (del 10% más pobre al 10% más rico)", fontsize=8.8)
    orden = ["bottom50", "middle40", "top10", "top1"]
    xg = np.arange(4) * 1.0
    apilar(axs[2], xg - 0.2, ito.loc[orden], ancho=0.38)
    apilar(axs[2], xg + 0.2, nos_g.loc[orden], ancho=0.38, alfa=0.55)
    for xi in xg:
        axs[2].text(xi - 0.2, -1.2, "ITO", ha="center", va="top", fontsize=7.6, color=g.TINTA2)
        axs[2].text(xi + 0.2, -1.2, "este", ha="center", va="top", fontsize=7.6, color=g.TINTA2)
    axs[2].set_xticks(xg)
    axs[2].set_xticklabels(["50% más\npobre", "40%\nmedio", "10% más\nrico", "1% más\nrico"], fontsize=9)
    axs[2].tick_params(axis="x", pad=22)
    axs[2].set_title("C. Tax Observatory (~2019) y este estudio (2019)", loc="left", fontsize=11.5,
                     fontweight="bold")
    for ax in axs:
        ax.xaxis.grid(False)
    axs[0].set_ylim(0, 45)
    axs[0].set_ylabel("Impuestos, % del ingreso")
    h, l = axs[1].get_legend_handles_labels()
    fig.legend(h[::-1], l[::-1], loc="lower center", ncol=6, frameon=False, fontsize=9.2, bbox_to_anchor=(0.5, -0.05))
    fig.suptitle("El gráfico de siempre: qué parte de su ingreso paga cada grupo en impuestos, según tres estudios",
                 x=0.01, y=1.04, ha="left", fontsize=14, fontweight="bold")
    fig.text(0.01, 0.985, "Los tres muestran lo mismo: el 10% más pobre paga la proporción más alta y de ahí para arriba "
             "la carga es pareja o baja. Las diferencias de nivel vienen de qué impuestos suma cada uno: Argendata\nincluye "
             "el cheque y otros impuestos al consumo (con el cheque, la raya negra en B, los dos quedan casi iguales); el "
             "Tax Observatory suma Ganancias de sociedades y más impuestos al patrimonio arriba, y usa el ingreso de "
             "Cuentas Nacionales.", fontsize=9.3, color=g.TINTA2, va="top")
    fig.subplots_adjust(wspace=0.06, top=0.84, bottom=0.17)
    fig.text(0.01, -0.08, "Fuentes: A, Argendata (Fundar), CSV del tópico Sistema tributario, con datos de Pessino, "
             "Rasteletti, Artana y Lustig (Oxford Open Economics, vol. 4); su categoría de Ganancias incluye sociedades. "
             "C, International Tax Observatory, informe n.° 10 (abril 2026),\nfigura 5, y nota sobre Argentina: totales del "
             "texto, composición leída del gráfico (aproximada); hogares, ingreso de Cuentas Nacionales, año no informado "
             "(sus fuentes llegan a 2019). Este estudio: personas, ingreso declarado en la EPH completado con las "
             "declaraciones juradas;\nen C, sus deciles agrupados con el decil 10 partido. Datos en data/externos/.",
             fontsize=7.2, color=g.MUDO, ha="left", va="top")
    guardar(fig, "c1_comparacion")


def c2_canastas(tramos):
    t = tramos[tramos.variante == "principal"].set_index(["anio", "grupo"]).canastas_por_persona
    orden = list(range(1, 10)) + [91, 95, 99]
    etq = [f"D{k}" for k in range(1, 10)] + ["P90-95", "P95-99", "1%"]
    fig, axs = plt.subplots(1, 2, figsize=(16, 6), sharey=True)
    for ax, a in zip(axs, (2004, ANIO_FIN)):
        v = t.loc[a].loc[orden]
        x = list(range(9)) + [9.6, 10.6, 11.6]
        col = [ROJO if y < 1 else ("#b9b8b0" if k < 10 else MEDIO) for k, y in zip(orden, v)]
        ax.bar(x, v, color=col, width=0.72)
        for xi, y in zip(x, v):
            ax.text(xi, y + 0.3, g.pct(y, 2 if y < 1 else 1), ha="center", va="bottom", fontsize=8.6, color=g.TINTA)
        ax.axhline(1, color=g.TINTA, linewidth=1.1, linestyle=(0, (4, 3)))
        ax.axvspan(9.1, 12.1, color="#e8f0fb", zorder=0, linewidth=0)
        ax.text(10.6, 0.97, "el decil 10,\npartido", transform=ax.get_xaxis_transform(), ha="center", va="top",
                fontsize=8.6, color=g.TINTA2, fontweight="bold")
        ax.set_xticks(x)
        ax.set_xticklabels(etq, fontsize=8.6)
        ax.xaxis.grid(False)
        ax.set_xlim(-0.6, 12.2)
        pobres = int((v.loc[list(range(1, 10))] < 1).sum())
        ax.set_title(f"{a}: {pobres} de los 9 primeros deciles, debajo de una canasta", loc="left", fontsize=11.5,
                     fontweight="bold")
    axs[0].set_ylabel("Ingreso por persona, en canastas básicas por mes")
    v = t.loc[ANIO_FIN]
    fig.suptitle("Los deciles muestran sobre todo a la mitad de abajo; los ricos están todos en la última barra",
                 x=0.01, y=1.04, ha="left", fontsize=14, fontweight="bold")
    fig.text(0.01, 0.985, f"Ingreso por persona de cada grupo, medido en canastas básicas (lo que necesita un adulto para "
             f"no ser pobre; línea punteada). En {ANIO_FIN} el decil 5 tiene {g.pct(v[5], 2)} canastas y el decil 9, {g.pct(v[9], 1)}; el 1% "
             f"más rico, {g.pct(v[99], 1)}.\nUn gráfico por deciles pone nueve barras para la mitad de abajo y la clase media, "
             "y mete en una sola a asalariados de clase media alta y a los ricos: por eso aquí el decil 10 se parte en tres.",
             fontsize=9.3, color=g.TINTA2, va="top")
    fig.subplots_adjust(wspace=0.05, top=0.83)
    fig.text(0.01, -0.03, "Fuente: elaboración propia con EPH (INDEC) y anuarios de ARCA. Ingreso per cápita familiar "
             "(antes de impuestos directos; en la cima, completado con el ingreso declarado a ARCA que la encuesta no "
             "capta) dividido por la canasta básica\ntotal por adulto equivalente del Gran Buenos Aires (INDEC; antes de "
             "2017, llevada hacia atrás con el IPC). Rojo: por debajo de una canasta. Aglomerados urbanos de la EPH.",
             fontsize=7.2, color=g.MUDO, ha="left", va="top")
    guardar(fig, "c2_canastas")


def gini_agrupado(pob, part):
    """Coeficiente de concentración con grupos ya ordenados por ingreso."""
    p = np.concatenate([[0], np.cumsum(pob)])
    l = np.concatenate([[0], np.cumsum(part)])
    return 1 - np.sum((p[1:] - p[:-1]) * (l[1:] + l[:-1]))


def kakwani(tramos):
    pob = {k: 0.1 for k in range(1, 10)} | {91: 0.05, 95: 0.04, 99: 0.01}
    orden = list(range(1, 10)) + [91, 95, 99]
    filas = []
    for (v, a), d in tramos[tramos.grupo != 0].groupby(["variante", "anio"]):
        d = d.set_index("grupo").loc[orden]
        w = np.array([pob[k] for k in orden])
        gi = gini_agrupado(w, d.part_ingreso.values)
        ci = gini_agrupado(w, d.part_impuestos.values)
        filas.append({"variante": v, "anio": a, "gini_ingreso": gi, "concentracion_impuestos": ci, "kakwani": ci - gi})
    return pd.DataFrame(filas)


def a1_progresividad(tramos):
    k = kakwani(tramos)
    k.round(4).to_csv(TABLES / "progresividad_anual.csv", index=False)
    kk = k.pivot(index="anio", columns="variante", values="kakwani")
    fig, ax = plt.subplots(figsize=(10, 4.6))
    ejes_tiempo(ax)
    ax.axhline(0, color=g.TINTA2, linewidth=1)
    ax.fill_between(kk.index, kk.min(axis=1), kk.max(axis=1), color=OSCURO, alpha=0.13, linewidth=0)
    ax.plot(kk.index, kk["principal"], color=OSCURO, linewidth=2.4, marker="o", markersize=3.5)
    ax.set_ylabel("Índice de Kakwani")
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:.2f}".replace(".", ",")))
    fig.suptitle("Progresividad del sistema, año por año: prácticamente cero", x=0.01, y=1.04, ha="left", fontsize=13.5,
                 fontweight="bold")
    ax.set_title("Kakwani = concentración de los impuestos − Gini del ingreso. Positivo: progresivo (los de arriba pagan "
                 "una parte mayor que su parte del ingreso);\nnegativo: regresivo. Calculado con 12 grupos (deciles 1-9 y "
                 "el decil 10 partido en tres): aproximado. Franja: cinco supuestos.", loc="left", fontsize=9,
                 color=g.TINTA2, pad=10)
    fig.text(0.01, -0.02, NOTA, fontsize=7.2, color=g.MUDO, ha="left", va="top")
    guardar(fig, "a1_progresividad")
    return k


def a2_recaudado_consumo():
    rec = pd.read_csv(PROCESSED / "recaudacion_macro.csv", index_col=0).loc[2004:ANIO_FIN]
    fig, ax = plt.subplots(figsize=(10, 4.6))
    ejes_tiempo(ax)
    for col, nombre, color in [("iva", "IVA", "#008300"), ("ingresos_brutos", "Ingresos Brutos", ROJO),
                               ("internos_modelados", "Internos", "#6250d6")]:
        y = rec[col] / rec.consumo_privado * 100
        ax.plot(y.index, y, color=color, linewidth=2.3)
        ax.text(ANIO_FIN + 0.4, y.iloc[-1], f"{nombre}  {g.pct(y.iloc[-1])}%", fontsize=8.6, va="center", color=color,
                fontweight="bold")
    ax.set_ylim(0, None)
    ax.set_ylabel("Recaudado, % del consumo privado")
    fig.suptitle("Cuánto se recauda por cada peso que consumen los hogares", x=0.01, y=1.04, ha="left", fontsize=13.5,
                 fontweight="bold")
    ax.set_title("Es la tasa que el estudio aplica al consumo de cada decil. Cuando baja, baja más la carga de los deciles "
                 "de abajo, que consumen todo su ingreso.", loc="left", fontsize=9, color=g.TINTA2, pad=10)
    fig.subplots_adjust(right=0.82)
    fig.text(0.01, -0.02, "Fuente: recaudación DNIAF (Ministerio de Economía) y consumo privado de Cuentas Nacionales "
             "(INDEC).", fontsize=7.2, color=g.MUDO, ha="left", va="top")
    guardar(fig, "a2_recaudado_consumo")


def a3_cobertura():
    c = pd.read_csv(TABLES / "validacion_cobertura.csv", index_col=0).loc[2004:ANIO_FIN]
    fig, ax = plt.subplots(figsize=(10, 4.4))
    ejes_tiempo(ax)
    y = c.impuestos_incluidos_sobre_recaudacion_total * 100
    ax.plot(y.index, y, color=OSCURO, linewidth=2.4, marker="o", markersize=3.5)
    ax.set_ylim(0, 100)
    ax.set_ylabel("% de la recaudación total")
    fig.suptitle("Qué parte de todo lo recaudado cubre el estudio", x=0.01, y=1.04, ha="left", fontsize=13.5,
                 fontweight="bold")
    ax.set_title(f"Entre {g.pct(y.min(), 0)}% y {g.pct(y.max(), 0)}%. Quedan afuera retenciones a la exportación, "
                 "Ganancias de sociedades, cheque, combustibles, monotributo e impuestos provinciales\ny municipales "
                 "distintos de Ingresos Brutos. Hasta 2015 los impuestos incluidos ganaron peso en la recaudación.",
                 loc="left", fontsize=9, color=g.TINTA2, pad=10)
    fig.text(0.01, -0.02, "Fuente: recaudación DNIAF; outputs/tables/validacion_cobertura.csv.", fontsize=7.2,
             color=g.MUDO, ha="left", va="top")
    guardar(fig, "a3_cobertura")


if __name__ == "__main__":
    largo, tot, ancho, tramos, trimestres = cargar()
    for f in OUT.glob("*"):
        f.unlink()
    i1_serie(tot, trimestres, tramos)
    i2_anios(largo, tramos)
    i2_distancia(tot)
    i3_mapa(tramos)
    i5_supuestos(largo)
    i6_composicion(ancho, tramos)
    g.fig_distancia(largo, carpeta=OUT, nombre="i7_ricos_pobres")
    g.fig_decil10_partido(ANIO_FIN, OUT, nombre="i8_decil10_partido")
    i9_matriz_deltas(tramos)
    c1_comparacion(largo, tramos)
    c2_canastas(tramos)
    c3_composicion_tramos(ancho, tramos)
    k = a1_progresividad(tramos)
    a2_recaudado_consumo()
    a3_cobertura()
    print("Gráficos del informe en", OUT)
    kp = k[k.variante == "principal"].set_index("anio")
    print("Kakwani principal:", kp.kakwani.round(3).to_dict())
