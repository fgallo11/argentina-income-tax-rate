#!/usr/bin/env python
"""Gráficos del informe (docs/informe.md): la tasa efectiva a lo largo de los años.

Salida: outputs/figures/informe/ (PNG y SVG). Todo sale de las tablas de outputs/tables/ (no
corre la microsimulación). Usa el estilo de 07_graficos.py.

  i1_serie                 decil 1, decil 10 y promedio; franja con los deciles 2 a 9.
  i2_distancia_promedio    decil 1 y decil 10 menos el promedio, en puntos, con banda de variantes.
  i3_mapa_calor            año × grupo (D1-D9, P90-95, P95-99, 1%): desvío contra el promedio del año.
  i4_composicion           qué impuestos paga el decil 1, el 5, el 10 y el 1% de la encuesta.
  i5_poblacion_fija        tasa observada contra la de una población fija (2004 y 2017).
  i6_cima                  el 1% menos los percentiles 90-95, en puntos.
  i7_robustez              decil 1, 5 y 10 con la banda de supuestos.
  i8_cheque                variante con el impuesto a los débitos y créditos bancarios.
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


def i1_serie(tot, trimestres):
    p = tot.loc["principal"]
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
    fin = {n: (y.iloc[-1], c) for y, n, c, _ in series}
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
                 "pagan casi lo mismo entre sí. Círculos huecos: años con trimestres faltantes. Punteado vertical: "
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
                 f"{ANIO_FIN}. Franjas: rango entre supuestos (ver robustez). El valor de 2009 depende de cómo se\n"
                 "combinan las ediciones de la ENGHo (punteado vertical): con otra forma de combinarlas el decil 1 da 4,9 "
                 "puntos en vez de 12,9. Lo firme es la tendencia.", loc="left", fontsize=9.3, color=g.TINTA2, pad=10)
    fig.subplots_adjust(right=0.85)
    fig.text(0.01, -0.02, NOTA + "\nFranjas: mínimo y máximo entre las variantes de supuestos que miden lo mismo "
             "(excluye la lectura contra el consumo y la que usa el gasto como ingreso del decil 1).",
             fontsize=7.2, color=g.MUDO, ha="left", va="top")
    guardar(fig, "i2_distancia_promedio")


def i3_mapa(tramos):
    pr = tramos[tramos.variante == "principal"]
    m = pr.pivot(index="grupo", columns="anio", values="total") * 100
    d = m.drop(index=0) - m.loc[0]
    orden = [99, 95, 91] + list(range(9, 0, -1))
    d = d.loc[orden]
    nombres = {99: "1% superior", 95: "P95-99", 91: "P90-95"} | {k: f"Decil {k}" for k in range(1, 10)}
    fig, ax = plt.subplots(figsize=(13.5, 5.6))
    lim = 8
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list("div", ["#2a78d6", "#f4f3ef", "#e34948"])
    im = ax.imshow(d.values, cmap=cmap, vmin=-lim, vmax=lim, aspect="auto")
    for i in range(d.shape[0]):
        for j in range(d.shape[1]):
            v = d.values[i, j]
            r = int(round(v))
            ax.text(j, i, "0" if r == 0 else f"{r:+d}".replace("-", "−"), ha="center", va="center", fontsize=7.6,
                    color="white" if abs(v) > 5.5 else g.TINTA)
    ax.set_xticks(range(d.shape[1]))
    ax.set_xticklabels([str(a) for a in d.columns], fontsize=8.2)
    ax.set_yticks(range(d.shape[0]))
    ax.set_yticklabels([nombres[k] for k in d.index], fontsize=9)
    ax.axhline(2.5, color=g.TINTA, linewidth=1.2)
    ax.grid(False)
    for s_ in ax.spines.values():
        s_.set_visible(False)
    cb = fig.colorbar(im, ax=ax, fraction=0.025, pad=0.01)
    cb.set_label("Puntos respecto del promedio del año", fontsize=8.5, color=g.TINTA2)
    cb.outline.set_visible(False)
    fig.suptitle("Quién paga más que el promedio, año por año", x=0.01, y=1.03, ha="left", fontsize=14,
                 fontweight="bold")
    fig.text(0.01, 0.975, "Cada celda: tasa del grupo menos la tasa promedio de ese año, en puntos. Rojo: paga más que "
             "el promedio; azul: menos. Arriba de la línea, el decil 10 partido en tres.\nEl decil 1 paga más que "
             "todos casi siempre; la cima alterna entre pagar más (2009-2015, 2020-2022) y menos (2016-2019, 2024-2025).",
             fontsize=9.3, color=g.TINTA2, va="top")
    fig.text(0.01, 0.02, NOTA + " Tramos del decil 10 con pocas observaciones: el 1% superior es ruidoso de un año a otro.",
             fontsize=7.2, color=g.MUDO, ha="left", va="top")
    fig.subplots_adjust(top=0.86, bottom=0.1)
    guardar(fig, "i3_mapa_calor")


def i4_composicion(ancho, tramos):
    grupos = [("Consumo (IVA, IIBB, Internos, contrib. a precios)", ["contrib_consumidor", "iva", "internos", "iibb"],
               "#9a998f"), ("Aportes personales", ["aportes"], "#1baf7a"),
              ("Contrib. patronales (mitad trabajador)", ["contrib_trabajador"], "#eda100"),
              ("Ganancias", ["ganancias"], AZUL), ("Bienes Personales", ["bienes_personales"], "#eb6834")]
    pr = ancho.set_index(["anio", "decil"])
    top = tramos[(tramos.variante == "principal") & (tramos.grupo == 99)].set_index("anio")
    paneles = [("Decil 1 (más pobre)", pr.xs(1, level="decil")), ("Decil 5", pr.xs(5, level="decil")),
               ("Decil 10 (más rico)", pr.xs(10, level="decil")), ("1% superior (encuesta completada)", top)]
    fig, axs = plt.subplots(1, 4, figsize=(15, 4.8), sharey=True)
    for ax, (titulo, d) in zip(axs, paneles):
        ejes_tiempo(ax, paso=7, indec=False)
        ax.set_xticks([2005, 2015, 2025])
        ys = [d[cols].sum(axis=1) * 100 for _, cols, _ in grupos]
        ax.stackplot(d.index, ys, colors=[c for _, _, c in grupos], linewidth=0)
        total = sum(ys)
        ax.plot(d.index, total, color=g.TINTA, linewidth=1)
        ax.set_title(f"{titulo}\n{g.pct(total.iloc[0])}% en 2004 → {g.pct(total.iloc[-1])}% en {ANIO_FIN}", loc="left",
                     fontsize=10, fontweight="bold")
    axs[0].set_ylabel("% del ingreso")
    axs[0].set_ylim(0, 45)
    handles = [g.Patch(color=c, label=n) for n, _, c in grupos]
    fig.legend(handles=handles, loc="lower center", ncol=5, fontsize=8.5, frameon=False, bbox_to_anchor=(0.5, -0.06))
    fig.suptitle("Qué impuestos paga cada grupo: abajo, consumo; arriba, Ganancias y Bienes Personales",
                 x=0.01, y=1.06, ha="left", fontsize=14, fontweight="bold")
    fig.text(0.01, 0.99, "Lo que mueve la tasa del decil 1 es el consumo (IVA e Ingresos Brutos); lo que mueve la del 1% es "
             "Ganancias y Bienes Personales. El decil 5 y el 10 pagan una tasa parecida, pero con impuestos distintos.",
             fontsize=9.3, color=g.TINTA2, va="top")
    fig.subplots_adjust(wspace=0.08, top=0.8, bottom=0.12)
    fig.text(0.01, -0.1, NOTA, fontsize=7.2, color=g.MUDO, ha="left", va="top")
    guardar(fig, "i4_composicion")


def i5_poblacion_fija(tot):
    pf = pd.read_csv(TABLES / "serie_poblacion_fija.csv")
    p = tot.loc["principal"]
    fig, axs = plt.subplots(1, 2, figsize=(13, 5.2), sharey=True)
    for ax, dec, nombre, color in [(axs[0], 1, "Decil 1 (más pobre)", ROJO), (axs[1], 10, "Decil 10 (más rico)", AZUL)]:
        ejes_tiempo(ax, paso=4)
        ax.plot(p.index, p[dec], color=color, linewidth=2.8, label="Observada")
        for base, estilo in [(2004, (0, (5, 2))), (2017, (0, (1, 1.5)))]:
            s = pf[(pf.anio_base == base) & (pf.decil == dec)].set_index("anio").total * 100
            ax.plot(s.index, s, color=color, linewidth=1.8, linestyle=estilo, alpha=0.8,
                    label=f"Con la población de {base}")
        ax.set_title(nombre, loc="left", fontsize=11, fontweight="bold")
        ax.legend(loc="lower center", fontsize=8.3, frameon=False)
    axs[0].set_ylabel("Impuestos, % del ingreso")
    axs[0].set_ylim(15, 48)
    s04 = pf[(pf.anio_base == 2004) & (pf.decil == 1)].set_index("anio").total * 100
    fig.suptitle("La baja del decil más pobre no vino de los impuestos: vino de cambios en su ingreso y su gasto",
                 x=0.01, y=1.06, ha="left", fontsize=13.5, fontweight="bold")
    fig.text(0.01, 1.0, f"Línea llena: la tasa observada. Punteadas: la que habría pagado la misma población del año base "
             f"(sus ingresos actualizados por salarios, su canasta fija) con los impuestos de cada año.\nCon la población "
             f"de 2004, el decil 1 habría pagado {g.pct(s04.loc[ANIO_FIN])}% en {ANIO_FIN}; pagó {g.pct(p[1].iloc[-1])}%. "
             "La diferencia es composición: quién está en el decil, cuánto gana respecto de los demás y cuánto gasta.",
             fontsize=9.3, color=g.TINTA2, va="top")
    fig.subplots_adjust(wspace=0.08, top=0.84)
    fig.text(0.01, -0.04, NOTA + " Población fija: scripts/08_poblacion_fija.py; el resultado depende del año base, por "
             "eso se muestran dos.", fontsize=7.2, color=g.MUDO, ha="left", va="top")
    guardar(fig, "i5_poblacion_fija")


def i6_cima(tramos):
    t = tramos.pivot_table(index=["variante", "anio"], columns="grupo", values="total") * 100
    dif = (t[99] - t[91]).unstack(0)
    pr = dif["principal"]
    fig, ax = plt.subplots(figsize=(11, 5.2))
    ejes_tiempo(ax)
    ax.axhline(0, color=g.TINTA2, linewidth=1)
    ax.fill_between(dif.index, dif.min(axis=1), dif.max(axis=1), color=OSCURO, alpha=0.13, linewidth=0)
    ax.bar(pr.index, pr, color=[OSCURO if v >= 0 else ROJO for v in pr], width=0.62)
    for a, v in pr.items():
        ax.text(a, v + (0.35 if v >= 0 else -0.35), ("+" if v >= 0 else "−") + g.pct(abs(v)), ha="center", va="bottom" if v >= 0 else "top",
                fontsize=7.4, color=g.TINTA2)
    ax.set_ylabel("Puntos: tasa del 1% superior − tasa de los percentiles 90-95")
    ax.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(2))
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:+.0f}".replace("-", "−") if v else "0"))
    n_pos, n_neg = int((pr > 0.5).sum()), int((pr < -0.5).sum())
    fig.suptitle("Dentro del 10% más rico, ¿la cima paga más o menos?", x=0.01, y=1.04, ha="left", fontsize=14,
                 fontweight="bold")
    ax.set_title(f"Azul: el 1% superior paga más que los percentiles 90-95 ({n_pos} años); rojo: paga menos ({n_neg} años). "
                 "Franja: rango entre cinco supuestos (consumo de la cima,\ningresos ajustados a Cuentas Nacionales, "
                 "renta de activos externos, sin Bienes Personales). Sigue a Ganancias y Bienes Personales; el 1% es "
                 "un grupo chico y ruidoso.", loc="left", fontsize=9.3, color=g.TINTA2, pad=10)
    fig.text(0.01, -0.02, NOTA, fontsize=7.2, color=g.MUDO, ha="left", va="top")
    guardar(fig, "i6_cima")


def i7_robustez(tot):
    nombres = {"recursos_gasto": "Gasto como ingreso del decil 1",
               "ajuste_cn_rentas_activos_ext": "Con rentas no declaradas y activos externos"}
    fig, axs = plt.subplots(1, 3, figsize=(15, 4.8), sharey=True)
    v = tot[~tot.index.get_level_values(0).isin(OTRA_MEDIDA)]
    for ax, (dec, nombre, color) in zip(axs, [(1, "Decil 1", ROJO), (5, "Decil 5", "#eda100"), (10, "Decil 10", AZUL)]):
        ejes_tiempo(ax, paso=7)
        d = v[dec].unstack(0)
        ax.fill_between(d.index, d.min(axis=1), d.max(axis=1), color=color, alpha=0.18, linewidth=0)
        ax.plot(d.index, d["principal"], color=color, linewidth=2.6)
        alt = "recursos_gasto" if dec == 1 else ("ajuste_cn_rentas_activos_ext" if dec == 10 else None)
        if alt:
            s = tot.loc[alt][dec]
            ax.plot(s.index, s, color=g.TINTA, linewidth=1.3, linestyle=(0, (4, 2)), label=nombres[alt])
            ax.legend(loc="lower center", fontsize=8, frameon=False)
        ax.set_title(nombre, loc="left", fontsize=11, fontweight="bold")
    axs[0].set_ylabel("Impuestos, % del ingreso")
    axs[0].set_ylim(10, 50)
    fig.suptitle("Qué tan firmes son los resultados", x=0.01, y=1.06, ha="left", fontsize=14, fontweight="bold")
    fig.text(0.01, 1.0, "Línea: medida principal. Franja: mínimo y máximo entre las variantes de supuestos que miden lo "
             "mismo (traslado de contribuciones, ediciones de la ENGHo, IVA, Bienes Personales, ingresos altos, Cuentas "
             "Nacionales,\nrentas, cheque y combustibles). Punteado: la variante que más cambia la conclusión en ese "
             "grupo. La franja del decil 1 es más ancha que su variación en el tiempo: su nivel es incierto, la "
             "tendencia no.", fontsize=9.3, color=g.TINTA2, va="top")
    fig.subplots_adjust(wspace=0.08, top=0.82)
    fig.text(0.01, -0.04, NOTA, fontsize=7.2, color=g.MUDO, ha="left", va="top")
    guardar(fig, "i7_robustez")


def i8_cheque(tot):
    """Medida principal contra la variante con el impuesto a los débitos y créditos bancarios."""
    p, c = tot.loc["principal"], tot.loc["con_cheque"]
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(14, 5.2), gridspec_kw={"width_ratios": [1.3, 1]})
    ejes_tiempo(ax)
    fin = {}
    for dec, nombre, color in [(1, "Decil 1", ROJO), (5, "Decil 5", "#eda100"), (10, "Decil 10", AZUL),
                               (0, "Promedio", g.TINTA)]:
        ax.plot(p.index, p[dec], color=color, linewidth=1.6, alpha=0.55)
        ax.plot(c.index, c[dec], color=color, linewidth=2.6, linestyle=(0, (5, 2)))
        fin[nombre] = (c[dec].iloc[-1], color)
    etiquetas_finales(ax, fin, 1.3)
    ax.set_ylabel("Impuestos, % del ingreso")
    ax.set_title("Línea fina: medida principal. Punteada: con el cheque", loc="left", fontsize=10.5,
                 fontweight="bold")
    dif = (c - p)[[1, 2, 3, 5, 8, 10, 0]]
    ejes_tiempo(ax2)
    colores = {1: ROJO, 2: "#e8836f", 3: "#eda100", 5: "#c9b25a", 8: "#7fb3ea", 10: AZUL, 0: g.TINTA}
    nombres = {0: "Promedio"} | {k: f"Decil {k}" for k in range(1, 11)}
    fin2 = {}
    for dec in dif.columns:
        ax2.plot(dif.index, dif[dec], color=colores[dec], linewidth=2.6 if dec in (1, 10) else 1.5,
                 linestyle=(0, (5, 2)) if dec == 0 else "-")
        fin2[nombres[dec]] = (dif[dec].iloc[-1], colores[dec])
    etiquetas_finales(ax2, fin2, 0.22, fmt=lambda v: f"+{g.pct(v)}")
    ax2.set_ylim(0, None)
    ax2.set_ylabel("Puntos que agrega el cheque")
    ax2.set_title("Cuánto le suma a cada grupo", loc="left", fontsize=10.5, fontweight="bold")
    fig.suptitle("Variante: con el impuesto a los débitos y créditos bancarios (\"cheque\")", x=0.01, y=1.06,
                 ha="left", fontsize=14, fontweight="bold")
    fig.text(0.01, 1.0, f"Lo recaudado por el cheque (2,3% a 2,6% del consumo privado) se supone trasladado entero a "
             f"precios y se reparte según el consumo, como Ingresos Brutos. Le suma {g.pct(dif[1].iloc[-1])} puntos al "
             f"decil 1 y {g.pct(dif[10].iloc[-1])} al decil 10 en {ANIO_FIN}:\nagranda la distancia entre ellos, pero no "
             "cambia la forma ni la tendencia. Es la lectura más regresiva posible: parte del cheque la pagan empresas y "
             "quienes más usan el sistema bancario.", fontsize=9.3, color=g.TINTA2, va="top")
    fig.subplots_adjust(wspace=0.42, top=0.84, right=0.9)
    fig.text(0.01, -0.03, NOTA, fontsize=7.2, color=g.MUDO, ha="left", va="top")
    guardar(fig, "i8_cheque")


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
    i1_serie(tot, trimestres)
    i2_distancia(tot)
    i3_mapa(tramos)
    i4_composicion(ancho, tramos)
    i5_poblacion_fija(tot)
    i6_cima(tramos)
    i7_robustez(tot)
    i8_cheque(tot)
    k = a1_progresividad(tramos)
    a2_recaudado_consumo()
    a3_cobertura()
    print("Gráficos del informe en", OUT)
    kp = k[k.variante == "principal"].set_index("anio")
    print("Kakwani principal:", kp.kakwani.round(3).to_dict())
