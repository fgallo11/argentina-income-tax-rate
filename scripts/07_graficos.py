#!/usr/bin/env python
"""Genera los gráficos del proyecto (outputs/figures/, PNG y SVG).

  fig0_dos_versiones_<año>      la carga contra el ingreso declarado y contra el ingreso ajustado
                                a Cuentas Nacionales (con la sensibilidad de activos externos).
  fig1_tasa_por_decil_<año>     gráfico principal: tasa efectiva por decil y por impuesto,
                                contra el ingreso declarado.
  fig2_serie_historica          tasa total 2004-último año: promedio, D1, D5 y D10 (con la cota de
                                ingreso no declarado del decil 10).
  fig3_composicion_en_el_tiempo composición por impuesto en el tiempo, deciles 1, 5 y 10.
  fig4_deciles_anios_seleccionados
  fig5_sensibilidad             rango de la tasa por decil según los supuestos.
  fig6_distancia_entre_deciles  brecha decil 10 / decil 1 antes y después de impuestos; ingreso de cada
                                decil en canastas básicas (línea de pobreza).
  fig6b_distancia_en_pesos      la misma, con el ingreso en pesos constantes de hoy.
  fig7_top1                     el 1% más rico (declaraciones juradas) frente a los deciles 1, 5 y 10.
  fig8_decil10_partido          el decil 10 partido en percentiles 90-95, 95-99 y el 1% superior
                                (también uno por año en por_anio/).
  fig9_decil10_serie            la serie 2004-último año de esos tramos, y qué explica la del 1%.
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.ticker  # noqa: E402,F401
import pandas as pd  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from incidencia.config import ANIO_FIN, FIGURES, TABLES  # noqa: E402

SUP, TINTA, TINTA2, MUDO, GRILLA, EJE = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
IMPUESTOS = [  # (columna, etiqueta, color) — de abajo hacia arriba en las barras
    ("ganancias", "Ganancias (personas)", "#2a78d6"),
    ("bienes_personales", "Bienes Personales (imputado a ingresos altos)", "#eb6834"),
    ("aportes", "Aportes personales", "#1baf7a"),
    ("contrib_trabajador", "Contrib. patronales (mitad trabajador)", "#eda100"),
    ("contrib_consumidor", "Contrib. patronales (mitad consumidor)", "#e87ba4"),
    ("iva", "IVA", "#008300"),
    ("internos", "Internos", "#6250d6"),
    ("iibb", "Ingresos Brutos", "#e34948"),
]
COLS = [c for c, _, _ in IMPUESTOS]
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": EJE, "axes.labelcolor": TINTA2,
    "xtick.color": MUDO, "ytick.color": MUDO, "text.color": TINTA, "figure.facecolor": SUP,
    "axes.facecolor": SUP, "savefig.facecolor": SUP, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRILLA, "grid.linewidth": 0.8, "axes.axisbelow": True,
    "svg.fonttype": "none", "hatch.linewidth": 0.8, "text.parse_math": False,
})
NOTA = ("Fuente: elaboración propia con EPH y ENGHo (INDEC), recaudación DNIAF (Min. de Economía) y normativa. "
        "Aglomerados urbanos de la EPH. Deciles de personas por ingreso per cápita familiar.\n"
        "Ingreso: el declarado en la EPH, antes de impuestos directos. Los ingresos no declarados (rentas, "
        "cuentapropia, evasión) se concentran arriba: la tasa real de los deciles altos es menor. Ganancias:\nsimulada "
        "para asalariados registrados y jubilados; "
        "lo recaudado que la simulación no capta y Bienes Personales se asignan a los ingresos más altos con las "
        "declaraciones juradas de ARCA,\njunto con el ingreso que la encuesta no capta. El 1% más rico se ve aparte en "
        "las figuras 7 a 9. "
        "Excluye retenciones, combustibles, Ganancias de sociedades, monotributo e impuestos patrimoniales provinciales.")


def plata(x):
    """$ con 'mil' o 'millones', con coma decimal."""
    if x >= 1e6:
        m = x / 1e6
        if round(m, 1) == 1:
            return "$1 millón"
        return f"${m:.0f} millones" if abs(m - round(m)) < 0.05 else f"${pct(m)} millones"
    return f"${x / 1e3:.0f} mil"


def miles(x):
    return f"{x:,.0f}".replace(",", ".")


def pct(x, d=1):
    return f"{x:.{d}f}".replace(".", ",")


def guardar(fig, nombre, carpeta=None, formatos=("png", "svg")):
    carpeta = carpeta or FIGURES
    carpeta.mkdir(parents=True, exist_ok=True)
    for ext in formatos:
        fig.savefig(carpeta / f"{nombre}.{ext}", dpi=200, bbox_inches="tight")
    plt.close(fig)


def barras(ax, d, etiquetas=True):
    """d: tasas por impuesto (en %), índice = decil."""
    base = pd.Series(0.0, index=d.index)
    x = list(range(len(d)))
    for col, etq, color in IMPUESTOS:
        ax.bar(x, d[col], bottom=base, color=color, width=0.72, label=etq, edgecolor=SUP, linewidth=1.2,
               hatch="////" if col == "bienes_personales" else None)
        base = base + d[col]
    tope = base.copy()
    ax.set_xticks(x)
    ax.set_xticklabels([f"D{i}" for i in d.index])
    ax.xaxis.grid(False)
    if etiquetas:
        for xi, b, t in zip(x, base, tope):
            ax.text(xi, t + 0.5, pct(b), ha="center", va="bottom", fontsize=9, color=TINTA)
    return tope


def fig_principal(ancho, largo, anio):
    a = ancho[ancho.anio == anio]
    d = a[a.decil > 0].set_index("decil")[COLS] * 100
    prom = a[a.decil == 0].total.iloc[0] * 100
    fig, ax = plt.subplots(figsize=(11, 6.6))
    tope = barras(ax, d)
    ax.axhline(prom, color=TINTA2, linewidth=1, linestyle=(0, (4, 3)))
    ax.set_xlim(-0.6, 9.6)
    ax.text(9.68, prom, f"Promedio de la\npoblación: {pct(prom)}%", ha="left", va="center", fontsize=9,
            color=TINTA2, clip_on=False)
    ax.set_ylim(0, max(tope) * 1.1)
    ax.set_ylabel("% del ingreso")
    ax.set_xlabel("Decil de ingreso per cápita familiar (D1 = 10% más pobre)")
    fig.suptitle(f"Argentina {anio}: impuestos como porcentaje del ingreso, por decil", x=0.01, y=1.06,
                 ha="left", fontsize=14, fontweight="bold")
    lo, hi = d.loc[2:9].sum(axis=1).min(), d.loc[2:9].sum(axis=1).max()
    ax.set_title(f"Impuestos ÷ ingreso declarado. El decil 1 paga {pct(d.loc[1].sum())}%; entre el 2 y el 9, de "
                 f"{lo:.0f}% a {hi:.0f}%; el 10, {pct(d.loc[10].sum())}%, incluido lo recaudado\npor Ganancias (azul) "
                 "y Bienes Personales (rayado) que la encuesta no capta. Pero la encuesta tampoco capta buena parte "
                 "del ingreso de los\ndeciles altos (rentas, cuentapropia, evasión, activos no declarados): con su "
                 "ingreso real, su tasa sería menor que la que se muestra.", loc="left", fontsize=9.8, color=TINTA2,
                 pad=10)
    h, l = ax.get_legend_handles_labels()
    ax.legend(h[::-1], l[::-1], loc="lower left", bbox_to_anchor=(1.01, 0.0), frameon=False, fontsize=9)
    fig.text(0.01, -0.02, NOTA, fontsize=7.3, color=MUDO, ha="left", va="top")
    guardar(fig, f"fig1_tasa_por_decil_{anio}")


def fondo_serie(ax):
    ax.axvspan(2006.5, 2015.5, color="#f0efec", zorder=0)
    ax.text(2011, ax.get_ylim()[0] + 0.4, "2007-2015: estadísticas INDEC con reservas", ha="center", va="bottom",
            fontsize=8, color=MUDO)
    ax.set_xticks(range(2004, ANIO_FIN + 1, 2))
    ax.xaxis.grid(False)


def fig_serie(serie):
    s = serie[serie.variante == "principal"].set_index("anio")
    ext = serie[serie.variante == "ajuste_cn_rentas_activos_ext"].set_index("anio")
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.set_ylim(15, 45)
    fondo_serie(ax)
    ax.fill_between(s.index, ext.total_D10 * 100, s.total_D10 * 100, color="#2a78d6", alpha=0.14, linewidth=0)
    ax.plot(ext.index, ext.total_D10 * 100, color="#2a78d6", linewidth=1.2, linestyle=(0, (2, 2)))
    ax.text(2016.3, 19.0, "Franja azul: cuánto podría bajar el decil 10 si se suma su\ningreso no "
            "declarado (Cuentas Nacionales, rentas ×7 y renta de\nactivos externos privados; cota alta)",
            fontsize=8.5, color=TINTA2, ha="left", va="center")
    lineas = [("total_D1", "Decil 1 (más pobre)", "#e34948"), ("total_D5", "Decil 5", "#eda100"),
              ("total_D10", "Decil 10 (más rico)", "#2a78d6"), ("total_poblacion", "Promedio", TINTA)]
    fin = sorted((s[c].iloc[-1] * 100, c) for c, _, _ in lineas)
    pos, ult = {}, -1e9
    for y0, c in fin:
        ult = max(y0, ult + 1.3)
        pos[c] = ult
    parc = s.trimestres < 4
    for col, etq, color in lineas:
        y = s[col] * 100
        ax.plot(s.index, y, color=color, linewidth=2.6 if col == "total_poblacion" else 2, label=etq,
                linestyle=(0, (5, 2)) if col == "total_poblacion" else "-")
        ax.scatter(s.index[parc], y[parc], s=42, facecolor=SUP, edgecolor=color, linewidth=1.6, zorder=3)
        ax.text(ANIO_FIN + 0.25, pos[col], f"{etq}  {pct(y.iloc[-1])}%", va="center", fontsize=9, color=TINTA)
    ax.set_xlim(2003.5, ANIO_FIN + 0.2)
    ax.set_ylabel("% del ingreso")
    d1 = s.total_D1 * 100
    otros = s[["total_D5", "total_D10", "total_poblacion"]].max(axis=1) * 100
    siempre = bool((d1 > otros).all())
    p = s.total_poblacion * 100
    pico = int(p.idxmax())
    fig.suptitle(f"Tasa efectiva total por grupo de ingreso, 2004-{ANIO_FIN}", x=0.01, y=1.05, ha="left", fontsize=14,
                 fontweight="bold")
    ax.set_title(("El decil más pobre paga la mayor proporción de su ingreso en todos los años" if siempre else
                  "El decil más pobre suele pagar la mayor proporción de su ingreso") +
                 f" (entre {d1.min():.0f}% y {d1.max():.0f}%). La carga promedio subió de {pct(p.iloc[0])}% en "
                 f"{int(p.index[0])}\na {pct(p.max())}% en {pico} y fue {pct(p.iloc[-1])}% en {int(p.index[-1])}. "
                 "Impuestos ÷ ingreso declarado. Círculos huecos: años con trimestres EPH faltantes (2007, 2015, 2016).\n"
                 "Antes de 2016 el ajuste a Cuentas Nacionales usa la cobertura promedio de 2016-2018.",
                 loc="left", fontsize=9.3, color=TINTA2, pad=10)
    fig.text(0.01, -0.02, NOTA, fontsize=7.3, color=MUDO, ha="left", va="top")
    fig.subplots_adjust(right=0.8)
    guardar(fig, "fig2_serie_historica")


def fig_composicion(ancho):
    """Composición de la tasa en el tiempo para tres deciles, con el mismo eje."""
    grupos = [(1, "Decil 1 (10% más pobre)"), (5, "Decil 5 (medio)"), (10, "Decil 10 (10% más rico)")]
    fig, axes = plt.subplots(1, 3, figsize=(14, 5.6), sharey=True)
    tope = 0
    for ax, (dec, nombre) in zip(axes, grupos):
        d = ancho[ancho.decil == dec].set_index("anio")[COLS] * 100
        ax.stackplot(d.index, [d[c] for c in COLS], colors=[c for _, _, c in IMPUESTOS],
                     labels=[e for _, e, _ in IMPUESTOS], edgecolor=SUP, linewidth=0.8)
        tope = max(tope, d.sum(axis=1).max())
        ind = d[["contrib_consumidor", "iva", "internos", "iibb"]].sum(axis=1)
        ult = d.index.max()
        ax.set_title(nombre, loc="left", fontsize=11, fontweight="bold")
        ax.text(0.02, 0.97, f"{ult}: total {pct(d.loc[ult].sum())}%, de los cuales\n"
                f"{pct(ind[ult])} son impuestos al consumo", transform=ax.transAxes, fontsize=8.6,
                color=TINTA2, va="top")
        ax.set_xlim(2004, ANIO_FIN)
        ax.set_xticks(range(2005, ANIO_FIN + 1, 5))
        ax.xaxis.grid(False)
    axes[0].set_ylim(0, tope * 1.18)
    axes[0].set_ylabel("% del ingreso")
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h[::-1], l[::-1], loc="center left", bbox_to_anchor=(0.905, 0.5), frameon=False, fontsize=9)
    fig.subplots_adjust(right=0.9, wspace=0.1, top=0.8)
    fig.suptitle(f"Qué impuestos paga cada grupo, 2004-{ANIO_FIN}", x=0.01, y=0.98, ha="left", fontsize=14,
                 fontweight="bold")
    fig.text(0.01, 0.9, "Abajo pesan los impuestos al consumo (IVA, Ingresos Brutos); arriba, los aportes y "
             "Ganancias. Los impuestos al consumo se calculan como recaudación por peso\nde consumo de Cuentas "
             "Nacionales, aplicada a lo que consume cada decil: si la actividad crece, crecen recaudación y consumo "
             "juntos y la tasa no cambia por eso.", fontsize=9.6, color=TINTA2, va="top")
    fig.text(0.01, -0.02, NOTA, fontsize=7.3, color=MUDO, ha="left", va="top")
    guardar(fig, "fig3_composicion_en_el_tiempo")


def fig_anios(ancho, largo, anios):
    fig, axes = plt.subplots(1, len(anios), figsize=(3.3 * len(anios), 5), sharey=True)
    for ax, a in zip(axes, anios):
        d = ancho[(ancho.anio == a) & (ancho.decil > 0)].set_index("decil")[COLS] * 100
        barras(ax, d, etiquetas=False)
        ax.set_title(str(a), loc="left", fontsize=11, fontweight="bold")
        ax.set_xticks([0, 4, 9])
        ax.set_xticklabels(["D1", "D5", "D10"])
    axes[0].set_ylabel("% del ingreso")
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h[::-1], l[::-1], loc="lower center", ncol=3, frameon=False, fontsize=8.5,
               bbox_to_anchor=(0.5, -0.17))
    fig.suptitle("Tasa efectiva por decil en años seleccionados", x=0.01, ha="left", fontsize=14, fontweight="bold")
    fig.text(0.01, -0.19, NOTA, fontsize=7.3, color=MUDO, ha="left", va="top")
    guardar(fig, "fig4_deciles_anios_seleccionados")


def fig_dos_versiones(largo, anio, carpeta=None, formatos=("png", "svg")):
    """Ingreso declarado vs. ingreso ajustado a Cuentas Nacionales."""
    def tabla(variante):
        v = largo[(largo.anio == anio) & (largo.variante == variante)]
        return v.pivot(index="decil", columns="impuesto", values="tasa") * 100
    paneles = [
        ("principal", "A. Con el ingreso que declaran en la encuesta",
         "Impuestos ÷ ingreso declarado en la EPH. Todos los que no son\n"
         "asalariados registrados subdeclaran, y más arriba: rentas,\n"
         "cuentapropia, evasión y activos no declarados en el exterior."),
        ("ajuste_cn_rentas", "B. Con el ingreso no declarado",
         "Salarios y cuentapropia llevados a Cuentas Nacionales (INDEC); rentas\n"
         "(alquileres, intereses, ganancias) multiplicadas por 7, punto medio de\n"
         "lo que las encuestas latinoamericanas dejan afuera (De Rosa, Flores y\n"
         "Morgan 2024). Mismo nivel total que A: cambia el reparto. Marca negra\n"
         "en D10: si además se suma la renta (3%) de los activos externos\n"
         "privados (los demás deciles suben cerca de 1 punto)."),
    ]
    fig, axes = plt.subplots(1, 2, figsize=(13.5, 6.2), sharey=True)
    res = {}
    for ax, (variante, titulo, nota) in zip(axes, paneles):
        t = tabla(variante)
        d = t.loc[1:10, COLS]
        prom = t.loc[0, "total"]
        res[variante] = t.total
        barras(ax, d)
        ax.axhline(prom, color=TINTA2, linewidth=1, linestyle=(0, (4, 3)))
        ax.text(9.5, 0.97, f"Línea punteada: promedio de la población, {pct(prom)}%", ha="right", va="top",
                transform=ax.get_xaxis_transform(),
                fontsize=8.8, color=TINTA2)
        ax.set_title(titulo, loc="left", fontsize=11.5, fontweight="bold", pad=8)
        ax.text(0.0, -0.13, nota, transform=ax.transAxes, fontsize=8.3, color=TINTA2, ha="left", va="top",
                linespacing=1.35)
        ax.set_xlim(-0.6, 9.6)
    ext = tabla("ajuste_cn_rentas_activos_ext").total
    res["ext"] = ext
    axes[1].plot([9 - 0.36, 9 + 0.36], [ext[10]] * 2, color=TINTA, linewidth=2.4, zorder=4)
    axes[1].text(9 + 0.42, ext[10], pct(ext[10]), va="center", fontsize=8.5, color=TINTA)
    tope = max(max(res["principal"].loc[1:10]), max(res["ajuste_cn_rentas"].loc[1:10]))
    axes[0].set_ylim(0, max(40, (int(tope / 5) + 2) * 5))
    axes[0].set_ylabel("% del ingreso")
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h[::-1], l[::-1], loc="center left", bbox_to_anchor=(0.91, 0.55), frameon=False, fontsize=9)
    fig.suptitle(f"Argentina {anio}: qué parte de su ingreso paga cada decil en impuestos", x=0.01, y=1.04,
                 ha="left", fontsize=14, fontweight="bold")
    a, b = res["principal"], res["ajuste_cn_rentas"]
    medios = b.loc[2:9]
    if ext[10] < medios.min():
        cierre = f"a {pct(ext[10])}%:\npor debajo de todos los deciles. El sistema resulta regresivo de punta a punta."
    elif ext[10] < b.loc[0]:
        cierre = f"a {pct(ext[10])}%:\npor debajo del promedio, pero por encima de algunos deciles medios."
    else:
        cierre = f"a {pct(ext[10])}%:\nsigue por encima del promedio."
    fig.text(0.01, 0.975, f"El decil 1 paga {pct(a[1])}% de su ingreso; los deciles medios, alrededor de {pct(a[5])}%; el "
             f"decil 10, {pct(a[10])}%. El sistema no es progresivo y es regresivo en la punta baja. Si se suma el ingreso\n"
             f"que la encuesta no capta —sobre todo rentas del capital, concentradas arriba—, el decil 10 pasa a "
             f"{pct(b[10])}% y, con la renta de los activos externos, " + cierre, fontsize=9.6,
             color=TINTA2, ha="left", va="top")
    fig.subplots_adjust(wspace=0.06, right=0.9, top=0.8)
    fig.text(0.01, -0.2, "Fuente: elaboración propia con EPH y ENGHo (INDEC), recaudación DNIAF (Min. de Economía), "
             "anuarios estadísticos de ARCA y normativa. Aglomerados urbanos de la EPH. Deciles de personas por "
             "ingreso per cápita familiar.\nIncluye Ganancias de personas, Bienes Personales, aportes, contribuciones "
             "patronales, IVA, Internos e Ingresos Brutos. Excluye retenciones, combustibles, Ganancias de sociedades, "
             "monotributo e impuestos patrimoniales provinciales.\nLa encuesta casi no capta al 1% más rico: su carga no se "
             "estima por separado y queda incluida, de forma incompleta, en el decil 10 (ver figura 7).", fontsize=7.3,
             color=MUDO, ha="left", va="top")
    guardar(fig, f"fig0_dos_versiones_{anio}", carpeta, formatos)


def fig_sensibilidad(largo, anio):
    v = largo[(largo.anio == anio) & (largo.impuesto == "total") & (largo.decil > 0)]
    v = v.pivot(index="decil", columns="variante", values="tasa") * 100
    incid = ["principal", "iva_legal", "contrib_100_trabajador", "contrib_100_consumidor",
             "altos_sin_corregir", "sin_bienes_personales"]
    lo, hi = v[incid].min(axis=1), v[incid].max(axis=1)
    fig, ax = plt.subplots(figsize=(11, 5.6))
    x = list(range(1, 11))
    ax.bar(x, hi - lo, bottom=lo, width=0.5, color="#86b6ef", edgecolor="none",
           label="Rango por supuestos de incidencia (traslado de contribuciones,\nIVA legal o recaudado, "
                 "sin Ganancias faltante en el decil 10, sin Bienes Personales)")
    ax.scatter(x, v["principal"], s=70, color=TINTA, zorder=3, label="Estimación principal (contra el ingreso declarado)")
    dif = (v["recursos_gasto"] - v["principal"]).abs() > 0.3
    ax.scatter([xi for xi in x if dif[xi]], v["recursos_gasto"][dif], s=70, facecolor=SUP, edgecolor="#e34948", linewidth=1.8, zorder=3,
               label="Si el ingreso de los deciles donde el gasto lo supera se reemplaza por el gasto")
    ax.scatter(x, v["ajuste_cn_rentas_activos_ext"], s=60, marker="D", color="#2a78d6", zorder=3,
               label="Con el ingreso no declarado: Cuentas Nacionales, rentas ×7 y activos externos (cota alta)")
    for xi in x:
        ax.text(xi + 0.32, v["principal"][xi], pct(v["principal"][xi]), va="center", fontsize=8.5, color=TINTA)
    ax.set_xticks(x)
    ax.set_xticklabels([f"D{i}" for i in x])
    ax.set_ylim(0, None)
    ax.set_ylabel("Tasa efectiva total, % del ingreso")
    ax.xaxis.grid(False)
    ax.legend(frameon=False, fontsize=9, loc="lower right")
    fig.suptitle(f"Cuánto cambia el resultado según los supuestos, {anio}", x=0.01, ha="left", fontsize=14,
                 fontweight="bold")
    ax.set_title("Pesan sobre todo el reparto de la contribución patronal y, en los deciles 1 y 10, "
                 "cómo se mide el ingreso. Rombos: mismo nivel total, otro reparto.", loc="left", fontsize=10, color=TINTA2, pad=10)
    fig.text(0.01, -0.02, NOTA, fontsize=7.3, color=MUDO, ha="left", va="top")
    guardar(fig, "fig5_sensibilidad")


def fig_distancia(largo, unidad="canastas", carpeta=None, nombre=None):
    """Brecha decil 10 / decil 1 antes y después de impuestos, e ingreso de cada decil.

    unidad="canastas": en canastas básicas totales (línea de pobreza de un adulto, INDEC) de ese
    año: no la afecta la inflación y muestra si la torta crece. unidad="pesos": en pesos
    constantes del último mes publicado del IPC."""
    from incidencia.config import PROCESSED, RAW
    q = pd.read_csv(PROCESSED / "eph_trimestral_decil.csv")
    ipc = pd.read_csv(PROCESSED / "deflactor.csv", index_col=0).ipc
    nac = pd.read_csv(RAW / "macro" / "ipc_148.3_INIVELNAL_DICI_M_26.csv")
    nac = pd.Series(nac.iloc[:, 1].values, index=nac.iloc[:, 0].str[:7])
    a_hoy = nac.iloc[-1] / nac[[f"{ANIO_FIN}-{m:02d}" for m in range(1, 13)]].mean()
    meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre",
             "noviembre", "diciembre"]
    hoy = f"{meses[int(nac.index[-1][5:]) - 1]} de {nac.index[-1][:4]}"
    pesos = unidad == "pesos"
    a = q.groupby(["anio", "decil"]).mean(numeric_only=True)
    pre = ((a.ipcf + a.ing_pre_adic) / a.personas).unstack()          # antes de impuestos directos
    tasa = largo[(largo.variante == "principal") & (largo.impuesto == "total")].pivot(
        index="anio", columns="decil", values="tasa")[list(range(1, 11))]
    post = pre * (1 - tasa)
    b_pre, b_post = pre[10] / pre[1], post[10] / post[1]
    tot = a.groupby("anio").sum()
    media = tot.ipcf / tot.personas                                    # ingreso promedio por persona
    if pesos:
        rel = (a.ipcf / a.personas).unstack().div(ipc.reindex(media.index), axis=0) * a_hoy
    else:
        cbt = pd.read_csv(PROCESSED / "deflactor.csv", index_col=0).cbt
        rel = (a.ipcf / a.personas).unstack().div(cbt.reindex(media.index), axis=0)   # canastas
    fmt = (lambda v: plata(v)) if pesos else (lambda v: pct(v, 2))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.5, 5.8))
    ax1.fill_between(b_pre.index, b_pre, b_post, color="#e34948", alpha=0.15, linewidth=0)
    ax1.plot(b_pre.index, b_pre, color=TINTA2, linewidth=2.2)
    ax1.plot(b_post.index, b_post, color="#e34948", linewidth=2.6)
    ax1.text(2011, b_post[2011] + 2.5, "Después de impuestos", fontsize=9, color="#e34948", va="bottom")
    ax1.text(2011, b_pre[2011] - 2.5, "Antes de impuestos", fontsize=9, color=TINTA2, va="top")
    ax1.set_ylim(0, max(b_post.max(), b_pre.max()) * 1.08)
    ax1.set_ylabel("Veces")
    ax1.set_title("Cuántas veces más ingresa por persona el 10% más rico\nque el 10% más pobre", loc="left",
                  fontsize=11, fontweight="bold")
    # todos los deciles, de rojo (D1) a azul (D10), y el 1% más rico (declaraciones juradas) punteado
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list("dec", ["#e34948", "#eda100", "#2a78d6"])
    finales = {}
    for dec in range(1, 11):
        y = rel[dec]
        ax2.plot(y.index, y, color=cmap((dec - 1) / 9), linewidth=2.6 if dec in (1, 10) else 1.5)
        finales[f"D{dec}  {fmt(y.iloc[-1])}"] = y.iloc[-1]
    top = pd.read_csv(TABLES / "top1.csv").set_index("anio") if (TABLES / "top1.csv").exists() else None
    if top is not None:
        div = (ipc.reindex(top.index) / a_hoy) if pesos else cbt.reindex(top.index)
        y = top.ingreso_medio_anual / 12 / div
        ax2.plot(y.index, y, color="#0b3d7a", linewidth=2.2, linestyle=(0, (4, 2)))
        finales[f"1% más rico*  {plata(y.iloc[-1]) if pesos else pct(y.iloc[-1])}"] = y.iloc[-1]
    # etiquetas a la derecha sin superponerse (en escala logarítmica)
    import math
    pos, ult = {}, -1e9
    for etq, val in sorted(finales.items(), key=lambda kv: kv[1]):
        lv = max(math.log10(val), ult + 0.075)
        pos[etq], ult = lv, lv
    for etq, lv in pos.items():
        ax2.text(ANIO_FIN + 0.5, 10 ** lv, etq, fontsize=8, va="center", color=TINTA)
    ax2.text(ANIO_FIN + 0.5, 1.0, f"En {ANIO_FIN}:", fontsize=8.5, fontweight="bold", va="bottom", color=TINTA,
             transform=matplotlib.transforms.blended_transform_factory(ax2.transData, ax2.transAxes))
    ax2.set_yscale("log")
    if pesos:
        marcas = [50e3, 100e3, 250e3, 500e3, 1e6, 2.5e6, 10e6, 25e6]
        ax2.set_yticks(marcas)
        ax2.set_yticklabels([plata(m) for m in marcas])
        ax2.set_ylabel("Pesos por persona, por mes (escala log.)")
        ax2.set_title(f"Ingreso por persona de cada decil y del 1% más rico\n(en pesos de {hoy})", loc="left",
                      fontsize=11, fontweight="bold")
    else:
        marcas = [0.1, 0.25, 0.5, 1, 2, 5, 10, 25, 50]
        ax2.set_yticks(marcas)
        ax2.set_yticklabels([pct(m, 2 if m < 1 else 0) for m in marcas])
        ax2.axhline(1, color=TINTA2, linewidth=1, linestyle=(0, (4, 3)))
        ax2.text(2004, 1.05, "1 canasta básica: línea de pobreza de un adulto", fontsize=8, color=TINTA2,
                 va="bottom")
        ax2.set_ylabel("Canastas básicas totales por persona, por mes (escala log.)")
        ax2.set_title("Ingreso por persona de cada decil y del 1% más rico,\nen canastas básicas", loc="left",
                      fontsize=11, fontweight="bold")
    ax2.minorticks_off()
    for ax in (ax1, ax2):
        ax.set_xlim(2003.5, ANIO_FIN + 0.3)
        ax.set_xticks(range(2004, ANIO_FIN + 1, 4))
        ax.xaxis.grid(False)
    a0, a1 = int(b_pre.index[0]), int(b_pre.index[-1])
    minimo = int(b_pre.idxmin())
    n_agranda = int((b_post > b_pre + 0.05).sum())
    fig.suptitle(f"La distancia entre ricos y pobres se achicó a menos de la mitad desde {a0}, y los impuestos la "
                 "agrandan", x=0.01, y=1.08, ha="left", fontsize=14, fontweight="bold")
    fig.text(0.01, 1.02, f"En {a0} el 10% más rico ingresaba {b_pre.iloc[0]:.0f} veces lo del 10% más pobre; en {minimo}, "
             f"{b_pre[minimo]:.0f} veces; en {a1}, {b_pre.iloc[-1]:.0f}. Después de pagar impuestos la distancia es mayor "
             f"({b_post.iloc[-1]:.0f} veces en {a1}; mayor en {n_agranda} de {len(b_pre)} años), porque el decil 1\npaga una "
             "proporción más alta de su ingreso que el decil 10. Ingreso declarado en la encuesta: arriba está subdeclarado y el 1% más rico casi no aparece, "
             "así que la distancia real es mayor.", fontsize=9.6, color=TINTA2, va="top")
    fig.subplots_adjust(wspace=0.42, right=0.86, top=0.84)
    fig.text(0.01, -0.07, "* 1% más rico: ingreso declarado a ARCA por declarante (no por miembro del hogar), sin las "
             "utilidades de las empresas ni la renta de activos externos: no es estrictamente comparable con los deciles y está subestimado.\n"
             "Fuente: elaboración propia con EPH (INDEC) y anuarios de ARCA. Ingreso per cápita familiar (ingreso del hogar "
             "dividido por sus miembros), con el aguinaldo en base devengada. Brecha: antes de impuestos directos, y "
             "después de restar\ntodos los impuestos estimados (medida principal). " + ("Panel derecho: pesos constantes (IPC-GBA del INDEC hasta 2006, IPC de San Luis 2007-2016, IPC Nacional "
             "desde 2017)." if pesos else "Panel derecho: ingreso de bolsillo por persona dividido por la canasta básica "
             "total del Gran Buenos Aires por adulto equivalente (INDEC; antes de 2017, la de 2017 llevada hacia "
             "atrás con el IPC\nempalmado). La canasta es por adulto: un hogar con chicos necesita menos por "
             "persona, así que el umbral de pobreza por persona es algo menor que 1.") + " Aglomerados urbanos de la EPH.",
             fontsize=7.3, color=MUDO, ha="left", va="top")
    guardar(fig, nombre or ("fig6b_distancia_en_pesos" if pesos else "fig6_distancia_entre_deciles"), carpeta)


def fig_top1(largo):
    """Deciles 1, 5 y 10 de la EPH y el 1% más rico estimado con declaraciones juradas."""
    t = pd.read_csv(TABLES / "top1.csv").set_index("anio")
    anio = int(t.index.max())
    v = largo[(largo.anio == anio) & (largo.variante == "principal") & (largo.impuesto == "total")]
    v = v.set_index("decil").tasa * 100
    r = t.loc[anio]
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(13.5, 5.6), gridspec_kw={"width_ratios": [1.1, 1]})
    etiquetas = ["Decil 1", "Decil 5", "Decil 10", "1% más rico"]
    valores = [v[1], v[5], v[10], r.completo * 100]
    colores = ["#e34948", "#eda100", "#7fb3ea", "#0b3d7a"]
    x = range(4)
    ax.bar(x, valores, color=colores, width=0.62)
    ax.errorbar([3], [r.completo * 100], yerr=[[(r.completo - r.completo_bajo) * 100],
                                               [(r.completo_alto - r.completo) * 100]],
                color=TINTA, capsize=6, linewidth=1.4)
    for xi, val in zip(x, valores):
        ax.text(xi - 0.36, val + 0.6, pct(val), fontsize=10, color=TINTA, ha="left")
    for val, mk, lab, dy in [(r.total_central * 100, "o", "sólo con lo que\ndeclara al fisco", 1.4),
                             (r.con_sociedades * 100, "D", "sin los activos\nexternos", -1.4)]:
        ax.scatter([3.42], [val], marker=mk, s=50, facecolor=SUP, edgecolor=TINTA, linewidth=1.4, zorder=4)
        ax.text(3.55, val + dy, f"{pct(val)}: {lab}", fontsize=8.3, color=TINTA2, va="center")
    ax.axhline(v[0], color=TINTA2, linewidth=1, linestyle=(0, (4, 3)))
    ax.text(5.3, v[0] - 1.2, f"Promedio de la\npoblación: {pct(v[0])}%", fontsize=8.3, color=TINTA2, ha="right",
            va="top")
    ax.set_xticks(list(x))
    ax.set_xticklabels(etiquetas)
    ax.set_xlim(-0.6, 5.4)
    ax.set_ylim(0, max(valores + [r.total_central * 100]) * 1.25)
    ax.set_ylabel("Impuestos, % del ingreso")
    ax.xaxis.grid(False)
    ax.set_title(f"{anio}", loc="left", fontsize=11, fontweight="bold")
    s_ = largo[(largo.variante == "principal") & (largo.impuesto == "total")]
    finales, colores_fin, lineas = {}, {}, []
    for dec, color, nombre in [(1, "#e34948", "Decil 1"), (10, "#7fb3ea", "Decil 10")]:
        y = s_[s_.decil == dec].set_index("anio").tasa * 100
        lineas.append(ax2.plot(y.index, y, color=color, linewidth=2.2, label=nombre)[0])
        finales[nombre], colores_fin[nombre] = y.iloc[-1], color
    banda = ax2.fill_between(t.index, t.completo_bajo * 100, t.completo_alto * 100, color="#0b3d7a", alpha=0.15,
                             linewidth=0, label="1%: rango según cuánto consuma")
    lineas.append(ax2.plot(t.index, t.completo * 100, color="#0b3d7a", linewidth=2.4, linestyle=(0, (4, 2)),
                           label="1% más rico (declaraciones juradas)")[0])
    finales["1% más rico"], colores_fin["1% más rico"] = t.completo.iloc[-1] * 100, "#0b3d7a"
    # etiquetas al final de cada línea (con el color de la línea), separadas si quedan encimadas
    pos, sep = {}, 1.1
    for nombre, val in sorted(finales.items(), key=lambda kv: kv[1]):
        previo = max(pos.values()) if pos else -1e9
        pos[nombre] = max(val, previo + sep)
    for nombre, val in pos.items():
        ax2.text(t.index[-1] + 0.3, val, f"{nombre}  {pct(finales[nombre])}", fontsize=8.8, va="center",
                 color=colores_fin[nombre], fontweight="bold")
    bajo = min(s_[s_.decil.isin([1, 10])].tasa.min() * 100, t.completo_bajo.min() * 100)
    alto = max(s_[s_.decil.isin([1, 10])].tasa.max() * 100, t.completo_alto.max() * 100)
    ax2.set_ylim(bajo - (alto - bajo) * 0.32, alto + 1)
    ax2.legend(handles=[lineas[2], banda, lineas[0], lineas[1]], loc="lower center", ncol=2, fontsize=8.5,
               frameon=True, facecolor=SUP, edgecolor=GRILLA, framealpha=1)
    ax2.set_ylabel("Impuestos, % del ingreso")
    ax2.set_xlim(2003.5, ANIO_FIN + 0.3)
    ax2.set_xticks(range(2004, ANIO_FIN + 1, 4))
    ax2.xaxis.grid(False)
    ax2.set_title(f"2004-{ANIO_FIN} (franja del 1%: según cuánto consuma)", loc="left", fontsize=11, fontweight="bold")
    def comparar(a, b, quien):      # a menos de medio punto se lo da por igual
        if abs(a - b) < 0.5:
            return f"lo mismo que {quien}"
        return f"{'menos' if a < b else 'más'} que {quien}"
    fig.suptitle(f"En {anio} el 1% más rico pagó alrededor de {r.completo * 100:.0f}% de su ingreso: "
                 f"{comparar(r.completo * 100, v[1], 'el decil más pobre')} y "
                 f"{comparar(r.completo * 100, v[10], 'el decil 10 de la encuesta')}", x=0.01, y=1.06, ha="left",
                 fontsize=13, fontweight="bold")
    if int(r.anio_fiscal_ddjj) != anio:
        ax.set_title(f"{anio} (1%: declaraciones de {int(r.anio_fiscal_ddjj)} llevadas a {anio})", loc="left",
                     fontsize=11, fontweight="bold")
    fig.text(0.01, 1.0, "La encuesta casi no capta al 1% más rico; las declaraciones juradas de Ganancias sí. A su "
             "ingreso declarado al fisco se le suman la mitad de las ganancias de las empresas\n(son sus dueños) y la "
             "renta de los activos externos privados; a sus impuestos, la mitad del impuesto de las empresas. Con lo "
             f"que declara al fisco solamente, pagaría {pct(r.total_central * 100)}%.\nAun así es un techo: el "
             "ingreso del 1% sigue subdeclarado (rentas internas que no figuran en ninguna fuente).",
             fontsize=9.6, color=TINTA2, va="top")
    fig.subplots_adjust(wspace=0.22, top=0.82, right=0.93)
    fig.text(0.01, -0.04, "Fuente: elaboración propia con EPH (deciles) y anuarios de estadísticas tributarias de "
             "ARCA (1% más rico: el 1% de la población con mayores ingresos declarados en Ganancias). Supuestos del 1%: "
             "la mitad de su ingreso es salario\n(aportes con tope y contribuciones); consumo entre la mitad y el total "
             "del cociente gasto/ingreso del 5% más rico de la ENGHo; Bienes Personales según su patrimonio declarado; "
             "es dueño de la mitad\nde las empresas (utilidad = impuesto de sociedades / 30%); activos externos "
             "(cartera y depósitos, INDEC) al 3% anual, sin impuesto. Ver scripts/10_top1.py.", fontsize=7.3,
             color=MUDO, ha="left", va="top")
    guardar(fig, "fig7_top1")


ELAST_PROG = 0.25   # fig8: elasticidad de la tasa al ingreso en el sistema progresivo de referencia


def fig_decil10_partido(anio, carpeta=None, formatos=("png", "svg"), nombre=None):
    """El decil 10 partido en P90-95, P95-99 y el 1% superior (11_tramos_decil10.py)."""
    t = pd.read_csv(TABLES / "tasas_tramos_decil10.csv")
    top = pd.read_csv(TABLES / "top1.csv").set_index("anio").loc[anio]
    a = t[t.anio == anio]
    pr = a[a.variante == "principal"].set_index("grupo")
    cn = a[a.variante == "ajuste_cn_activos_ext"].set_index("grupo").total * 100
    grupos = [1, 3, 5, 7, 9, 91, 95, 99]
    etiquetas = ["D1", "D3", "D5", "D7", "D9", "P90-95", "P95-99", "1%", "1%"]
    rojo, gris, azul, oscuro = "#e34948", "#b9b8b0", "#7fb3ea", "#0b3d7a"
    colores = [rojo, gris, gris, gris, gris, azul, azul, azul, oscuro]
    vals = [pr.total[g] * 100 for g in grupos] + [top.completo * 100]
    x = list(range(len(grupos))) + [len(grupos) + 0.9]          # el 1% de las DDJJ, separado
    fig, (ax, ax2, ax3) = plt.subplots(1, 3, figsize=(19, 6.2), gridspec_kw={"width_ratios": [1.25, 0.85, 0.85]})
    ax.bar(x, vals, color=colores, width=0.66, label="Medida principal (ingreso declarado)")
    arriba = [max(v, cn[g]) for v, g in zip(vals, grupos)] + [vals[-1]]
    for xi, val, h in zip(x, vals, arriba):
        ax.text(xi, h + 1.0, pct(val), ha="center", fontsize=9, color=TINTA, fontweight="bold")
    ax.scatter(x[:-1], [cn[g] for g in grupos], marker="D", s=40, facecolor=SUP, edgecolor=TINTA, linewidth=1.3,
               zorder=5, label="Con ingresos ajustados a Cuentas Nacionales\ny renta de activos externos")
    ax.axhline(pr.total[0] * 100, color=TINTA2, linewidth=1, linestyle=(0, (4, 3)),
               label=f"Promedio de la población ({pct(pr.total[0] * 100)}%)")
    techo = max(vals + list(cn[grupos])) * 1.32
    ax.axvspan(4.5, 7.5, color="#e8f1fb", zorder=0, linewidth=0)
    ax.text(6, techo * 0.94, "decil 10, partido\n(encuesta)", ha="center", va="top", fontsize=8.5, color=TINTA2,
            fontweight="bold")
    ax.text(x[-1], techo * 0.94, "otra\nfuente:\nDDJJ*", ha="center", va="top", fontsize=8.5,
            color=oscuro, fontweight="bold")
    ax.axvline((7 + x[-1]) / 2, color=EJE, linewidth=1)
    ax.set_xticks(x)
    ax.set_xticklabels(etiquetas, fontsize=8.8)
    ax.set_xlim(-0.6, x[-1] + 0.6)
    ax.set_ylim(0, techo)
    ax.set_ylabel("Impuestos, % del ingreso")
    ax.xaxis.grid(False)
    h, l = ax.get_legend_handles_labels()
    h = [Patch(color=gris, label="Medida principal (ingreso declarado)") if lab.startswith("Medida") else x_
         for x_, lab in zip(h, l)]
    ax.legend(handles=h, loc="upper left", bbox_to_anchor=(0, -0.13), ncol=2, fontsize=8, frameon=False)
    ax.set_title(f"Qué parte de su ingreso paga cada grupo, {anio}", loc="left", fontsize=11, fontweight="bold")
    # paneles derechos: % de los impuestos que paga cada grupo frente a dos repartos de referencia
    # con la misma recaudación total. Proporcional: todos la misma tasa (su parte del ingreso).
    # Progresivo: tasa = promedio × (ingreso por persona / promedio)^ELAST_PROG, reescalada para
    # recaudar lo mismo (ELAST_PROG = 0,25: el decil 1 pagaría ~la mitad de la tasa promedio y el
    # 1% superior ~el doble).
    g2 = list(range(1, 10)) + [91, 95, 99]
    pob = {g: 10 for g in range(1, 10)} | {91: 5, 95: 4, 99: 1}
    nom = [f"D{g}" for g in range(1, 10)] + ["P90-95", "P95-99", "1% encuesta"]
    y = list(range(len(g2)))
    yrel = pr.canastas_por_persona[g2] / pr.canastas_por_persona[0]
    peso = pr.part_ingreso[g2] * yrel ** ELAST_PROG
    ref_prog = peso / peso.sum()                                   # parte de los impuestos, progresivo
    tasa_prog = pr.total[0] * yrel ** ELAST_PROG / peso.sum()
    d_prop = [(pr.part_impuestos[g] - pr.part_ingreso[g]) * 100 for g in g2]
    d_prog = [(pr.part_impuestos[g] - ref_prog[g]) * 100 for g in g2]
    def panel_delta(axx, delta, titulo, xlabel):
        lim = max(abs(d) for d in delta) * 1.45
        axx.barh(y, delta, height=0.62, color=[oscuro if d >= 0 else rojo for d in delta])
        axx.axvline(0, color=TINTA2, linewidth=1)
        bt = matplotlib.transforms.blended_transform_factory(axx.transData, axx.transAxes)
        for i, d in enumerate(delta):
            signo = "+" if d >= 0 else "−"
            axx.text(d + (0.03 if d >= 0 else -0.03) * lim, i, f"{signo}{pct(abs(d), 2)}", va="center",
                     ha="left" if d >= 0 else "right", fontsize=8.2, color=TINTA)
        axx.set_yticks(y)
        axx.set_xlim(-lim, lim)
        axx.set_ylim(-0.6, len(g2) - 0.1)
        axx.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: pct(v)))
        axx.set_xlabel(xlabel, fontsize=9)
        axx.yaxis.grid(False)
        axx.text(-0.04, 1.01, "← paga menos", transform=bt, fontsize=8, color=rojo, va="bottom", ha="right")
        axx.text(0.04, 1.01, "paga más →", transform=bt, fontsize=8, color=oscuro, va="bottom", ha="left")
        axx.set_title(titulo, loc="left", fontsize=10.5, fontweight="bold", pad=18)

    panel_delta(ax2, d_prop, "Frente a un sistema proporcional\n(todos la misma tasa)",
                "Puntos: % de los impuestos − % del ingreso")
    ax2.set_yticklabels(nom)
    panel_delta(ax3, d_prog, "Frente a un sistema progresivo\n(la tasa sube con el ingreso)",
                "Puntos: % de los impuestos − % en el progresivo")
    ax3.set_yticklabels([f"{pct(tasa_prog[g] * 100)}%" for g in g2], fontsize=8, color=TINTA2)
    ax3.text(-0.02, len(g2) - 0.35, "tasa en el\nprogresivo", transform=matplotlib.transforms.blended_transform_factory(
        ax3.transAxes, ax3.transData), ha="right", va="bottom", fontsize=7.4, color=MUDO)
    tr = matplotlib.transforms.blended_transform_factory(ax3.transAxes, ax3.transData)
    for i, g in enumerate(g2):
        ax3.text(1.04, i, f"{pob[g]}%  ·  {pct(pr.part_ingreso[g] * 100)}%  ·  {pct(pr.canastas_por_persona[g])}",
                 va="center", ha="left", fontsize=8, color=TINTA2, transform=tr)
    ax3.text(1.04, len(g2) - 0.35, "pobl. · ingreso · canastas", va="bottom", ha="left", fontsize=7.6,
             color=MUDO, transform=tr)
    p_alto = (pr.part_ingreso[[91, 95, 99]].sum()) * 100
    t91, t99 = pr.total[91] * 100, pr.total[99] * 100
    medios = pr.total[list(range(2, 10))].median() * 100
    if t99 < medios - 0.5:
        titulo = "En la cima la tasa baja: el 1% más rico de la encuesta paga menos que los deciles medios"
    elif t99 > t91 + 0.5:
        titulo = "Dentro del 10% más rico la tasa sube hacia la cima"
    else:
        titulo = "Dentro del 10% más rico la tasa es pareja"
    fig.suptitle(titulo, x=0.01, y=1.1, ha="left", fontsize=13.5, fontweight="bold")
    fig.text(0.01, 1.04, f"En {anio} el 10% más rico tiene {pct(p_alto, 0)}% del ingreso (encuesta más el ingreso que declara al fisco y "
             f"la encuesta no capta). Paga {pct(t91)}% en los percentiles 90-95,\n{pct(pr.total[95] * 100)}% en el 95-99 y "
             f"{pct(t99)}% en el 1% superior; los deciles medios, alrededor de {pct(medios)}%. Dos mediciones del 1%: la encuesta "
             f"completada con las declaraciones juradas\n({pct(pr.canastas_por_persona[99])} canastas por persona) y sólo las declaraciones "
             f"juradas, por declarante, con utilidades de empresas y renta de activos externos ({pct(top.completo * 100)}%). "
             f"Con esa renta, el de la encuesta paga {pct(a[(a.variante == 'ajuste_cn_activos_ext') & (a.grupo == 99)].total.iloc[0] * 100)}%.",
             fontsize=9.6, color=TINTA2, va="top")
    fig.subplots_adjust(wspace=0.32, top=0.84, right=0.87)
    fig.text(0.01, -0.12, "Fuente: elaboración propia con EPH, ENGHo (INDEC), recaudación DNIAF y anuarios de ARCA. "
             "Tramos ordenados por ingreso per cápita familiar, como los deciles. Ganancias que la encuesta no capta y "
             "Bienes Personales se reparten entre los tramos con las\ndeclaraciones juradas. Por encima del 5% más rico "
             "la ENGHo no informa consumo: se deja fijo. Rombo: ingresos de cada fuente llevados a\nCuentas Nacionales, "
             "más la renta de los activos externos privados. * 1% según las declaraciones juradas de Ganancias (ARCA), "
             "con utilidades de empresas y renta de activos externos; ingreso por declarante, ver fig7.\nPaneles derechos: misma "
             "recaudación total repartida de dos formas de referencia. Proporcional: todos pagan la tasa promedio. Progresivo: "
             f"tasa = promedio × (ingreso por persona del grupo / promedio)^{pct(ELAST_PROG, 2)}, reescalada para recaudar lo mismo. "
             "Ver scripts/11_tramos_decil10.py.", fontsize=7.3, color=MUDO, ha="left", va="top")
    nombre = nombre or ("fig8_decil10_partido" if carpeta is None else f"fig8_decil10_partido_{anio}")
    guardar(fig, nombre, carpeta, formatos)


def fig_decil10_serie():
    """Serie de los tramos del decil 10 (11_tramos_decil10.py) y composición de la tasa del 1%."""
    t = pd.read_csv(TABLES / "tasas_tramos_decil10.csv")
    pr = t[t.variante == "principal"]
    tasa = pr.pivot(index="anio", columns="grupo", values="total") * 100
    top = pd.read_csv(TABLES / "top1.csv").set_index("anio")
    medios = tasa[list(range(2, 10))].median(axis=1)
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(14, 5.8), gridspec_kw={"width_ratios": [1.15, 1]})
    series = [(tasa[1], "Decil 1", "#e34948", "-", 2.2), (medios, "D2-D9", "#9a998f", "-", 2.2),
              (tasa[91], "P90-95", "#a9cdf2", "-", 2.0), (tasa[95], "P95-99", "#4f93dc", "-", 2.0),
              (tasa[99], "1% encuesta", "#0b3d7a", "-", 2.8),
              (top.completo * 100, "1% DDJJ*", "#0b3d7a", (0, (4, 2)), 1.8)]
    finales = {}
    for y, nombre, color, estilo, lw in series:
        ax.plot(y.index, y, color=color, linestyle=estilo, linewidth=lw, label=nombre)
        finales[nombre] = (y.iloc[-1], color)
    pos, ult = {}, -1e9
    for nombre, (val, color) in sorted(finales.items(), key=lambda kv: kv[1][0]):
        pos[nombre] = max(val, ult + 1.05)
        ult = pos[nombre]
    for nombre, v in pos.items():
        ax.text(ANIO_FIN + 0.4, v, f"{nombre}  {pct(finales[nombre][0])}", fontsize=8.3, va="center",
                color=finales[nombre][1], fontweight="bold")
    ax.set_xlim(2003.5, ANIO_FIN + 0.3)
    ax.set_xticks(range(2004, ANIO_FIN + 1, 3))
    ax.xaxis.grid(False)
    ax.set_ylabel("Impuestos, % del ingreso")
    ax.set_title(f"Tasa efectiva total, 2004-{ANIO_FIN}", loc="left", fontsize=11, fontweight="bold")
    bajo, alto = min(s_[0].min() for s_ in series), max(s_[0].max() for s_ in series)
    ax.set_ylim(bajo - 1.5, alto + 1)
    # composición de la tasa del 1% de la encuesta
    c = pr[pr.grupo == 99].set_index("anio")
    partes = [("Ganancias", c.ganancias, "#2a78d6"), ("Bienes Personales", c.bienes_personales, "#eb6834"),
              ("Aportes y contribuciones", c.aportes + c.contrib_trabajador, "#1baf7a"),
              ("Impuestos al consumo", c.indirectos, "#9a998f")]
    base = pd.Series(0.0, index=c.index)
    for nombre, v, color in partes:
        ax2.bar(c.index, v * 100, bottom=base, color=color, width=0.72, label=nombre)
        base = base + v * 100
    for a_, tot in base.items():
        ax2.text(a_, tot + 0.4, pct(tot, 0), ha="center", fontsize=7.2, color=TINTA2)
    ax2.set_xticks(range(2004, ANIO_FIN + 1, 3))
    ax2.xaxis.grid(False)
    ax2.set_ylim(0, base.max() * 1.25)
    ax2.legend(loc="upper left", ncol=2, fontsize=8, frameon=False)
    ax2.set_title("Qué paga el 1% de la encuesta (% de su ingreso)", loc="left", fontsize=11, fontweight="bold")
    sube = [int(a_) for a_ in tasa.index if tasa.loc[a_, 99] > tasa.loc[a_, 91] + 0.5]
    baja = [int(a_) for a_ in tasa.index if tasa.loc[a_, 99] < tasa.loc[a_, 91] - 0.5]
    fig.suptitle("Dentro del 10% más rico, la carga del 1% sube y baja con Ganancias y Bienes Personales",
                 x=0.01, y=1.06, ha="left", fontsize=13.5, fontweight="bold")
    fig.text(0.01, 1.0, f"El 1% de la encuesta paga más que los percentiles 90-95 en {len(sube)} de {len(tasa)} años y menos "
             f"en {len(baja)} ({', '.join(str(a_) for a_ in baja)}). Lo que mueve su tasa es Ganancias y Bienes Personales; "
             "los impuestos al consumo\npesan poco arriba porque consumen una parte chica de su ingreso. Encuesta completada "
             "con el ingreso y la Ganancias que declaran al fisco y la encuesta no capta.", fontsize=9.6, color=TINTA2,
             va="top")
    fig.subplots_adjust(wspace=0.42, top=0.86, right=0.97)
    fig.text(0.01, -0.06, "Fuente: elaboración propia con EPH, ENGHo (INDEC), recaudación DNIAF y anuarios de ARCA. "
             "Tramos ordenados por ingreso per cápita familiar, como los deciles; medida principal. D2-D9: mediana de las "
             "tasas de los deciles 2 a 9.\n* 1% según las "
             "declaraciones juradas de Ganancias (ARCA), por declarante, con utilidades de empresas y renta de activos "
             f"externos (figura 7). {ANIO_FIN}: declaraciones del año anterior actualizadas. Ver scripts/11_tramos_decil10.py.",
             fontsize=7.3, color=MUDO, ha="left", va="top")
    guardar(fig, "fig9_decil10_serie")


if __name__ == "__main__":
    ancho = pd.read_csv(TABLES / "tasas_por_decil_anual_ancho.csv")
    largo = pd.read_csv(TABLES / "tasas_por_decil_anual.csv")
    serie = pd.read_csv(TABLES / "serie_total_anual.csv")
    ultimo = int(ancho.anio.max())
    for f in FIGURES.glob("fig*"):
        f.unlink()
    fig_dos_versiones(largo, ultimo)
    fig_dos_versiones(largo, 2004)
    for a in sorted(largo.anio.unique()):          # la figura central, un archivo por año
        fig_dos_versiones(largo, int(a), FIGURES / "por_anio", formatos=("png",))
    fig_principal(ancho, largo, ultimo)
    fig_principal(ancho, largo, 2004)
    fig_serie(serie)
    fig_composicion(ancho)
    fig_anios(ancho, largo, [2004, 2009, 2014, 2019, ANIO_FIN])
    fig_sensibilidad(largo, ultimo)
    fig_distancia(largo)
    fig_distancia(largo, unidad="pesos")
    if (TABLES / "top1.csv").exists():
        fig_top1(largo)
    if (TABLES / "tasas_tramos_decil10.csv").exists():
        fig_decil10_partido(ultimo)
        for a in sorted(largo.anio.unique()):      # un archivo por año
            fig_decil10_partido(int(a), FIGURES / "por_anio", formatos=("png",))
        fig_decil10_serie()
    print("Gráficos en", FIGURES)
