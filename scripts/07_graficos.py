#!/usr/bin/env python
"""Genera los gráficos del proyecto (outputs/figures/, PNG y SVG).

  fig1_tasa_por_decil_<año>     gráfico principal: tasa efectiva por decil y por impuesto,
                                con el tramo adicional si se mide contra el ingreso declarado.
  fig2_serie_historica          tasa total 2004-2024: promedio, D1 (con rango), D5 y D10.
  fig3_composicion_en_el_tiempo composición de la tasa promedio por impuesto.
  fig4_deciles_anios_seleccionados
  fig5_sensibilidad             rango de la tasa por decil según los supuestos.
  fig6_poblacion_fija           serie observada vs. contrafáctico de población fija.
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from incidencia.config import FIGURES, TABLES  # noqa: E402

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
ETQ_TECHO = ("Techo de ingresos altos: Ganancias y Bienes Personales\nrecaudados por habitante, sobre ingreso de "
             "encuesta\nmás ingreso declarado al fisco")
ETQ_DECL = "Adicional si se divide por el ingreso declarado\n(deciles donde el gasto supera al ingreso)"
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": EJE, "axes.labelcolor": TINTA2,
    "xtick.color": MUDO, "ytick.color": MUDO, "text.color": TINTA, "figure.facecolor": SUP,
    "axes.facecolor": SUP, "savefig.facecolor": SUP, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRILLA, "grid.linewidth": 0.8, "axes.axisbelow": True,
    "svg.fonttype": "none", "hatch.linewidth": 0.8,
})
NOTA = ("Fuente: elaboración propia con EPH y ENGHo (INDEC), recaudación DNIAF (Min. de Economía) y normativa. "
        "Aglomerados urbanos de la EPH. Deciles de personas por ingreso per cápita familiar.\n"
        "Ingreso: antes de impuestos directos; si el gasto estimado de un decil supera su ingreso declarado, se "
        "toma el gasto como medida de sus recursos. Ganancias: simulada para asalariados registrados y jubilados;\n"
        "lo recaudado que la simulación no capta y Bienes Personales se asignan a los ingresos más altos (anuarios "
        "de ARCA), en la misma escala que los impuestos indirectos. No estima el 1% superior.\n"
        "Excluye retenciones, combustibles, Ganancias de sociedades, monotributo e impuestos patrimoniales provinciales.")


def pct(x, d=1):
    return f"{x:.{d}f}".replace(".", ",")


def guardar(fig, nombre):
    for ext in ("png", "svg"):
        fig.savefig(FIGURES / f"{nombre}.{ext}", dpi=200, bbox_inches="tight")
    plt.close(fig)


def barras(ax, d, extra=None, etiquetas=True, techo=None, piso=None):
    """d: tasas por impuesto (en %), índice = decil. extra: total con ingreso declarado.
    techo / piso: total con la corrección de ingresos altos por registros / sin corrección."""
    base = pd.Series(0.0, index=d.index)
    x = list(range(len(d)))
    for col, etq, color in IMPUESTOS:
        ax.bar(x, d[col], bottom=base, color=color, width=0.72, label=etq, edgecolor=SUP, linewidth=1.2,
               hatch="////" if col == "bienes_personales" else None)
        base = base + d[col]
    tope = base.copy()
    if extra is not None:
        ad = (extra - base).clip(lower=0)
        ad[ad < 0.3] = 0
        ax.bar(x, ad, bottom=base, color="#f0efec", width=0.72, edgecolor=MUDO, linewidth=0.8, hatch="....",
               label=ETQ_DECL)
        tope = base + ad
    if techo is not None:
        ad2 = (techo - base).clip(lower=0)
        ad2[(ad2 < 0.3) | (tope > base)] = 0
        ax.bar(x, ad2, bottom=base, color="#e6eef9", width=0.72, edgecolor="#2a78d6", linewidth=0.8, hatch="xxxx",
               label=ETQ_TECHO)
        tope = tope + ad2
    if piso is not None:
        for xi, b, pz in zip(x, base, piso):
            if b - pz > 0.3:
                ax.plot([xi - 0.36, xi + 0.36], [pz, pz], color=TINTA, linewidth=1.6, zorder=4)
                ax.text(xi + 0.4, pz, f"sólo\nEPH\n{pct(pz)}", fontsize=7.5, color=TINTA2, va="center", ha="left",
                        clip_on=False)
    ax.set_xticks(x)
    ax.set_xticklabels([f"D{i}" for i in d.index])
    ax.xaxis.grid(False)
    if etiquetas:
        for xi, b, t in zip(x, base, tope):
            txt = pct(b) if t - b < 0.3 else f"{pct(b)} a {pct(t)}"
            ax.text(xi, t + 0.5, txt, ha="center", va="bottom", fontsize=9, color=TINTA)
    return tope


def fig_principal(ancho, largo, anio):
    a = ancho[ancho.anio == anio]
    d = a[a.decil > 0].set_index("decil")[COLS] * 100
    decl = largo[(largo.anio == anio) & (largo.variante == "ingreso_declarado") & (largo.impuesto == "total")
                 & (largo.decil > 0)].set_index("decil").tasa * 100
    def var(nombre):
        return largo[(largo.anio == anio) & (largo.variante == nombre) & (largo.impuesto == "total")
                     & (largo.decil > 0)].set_index("decil").tasa * 100
    prom = a[a.decil == 0].total.iloc[0] * 100
    fig, ax = plt.subplots(figsize=(11, 6.6))
    tope = barras(ax, d, decl, techo=var("altos_registros"), piso=var("altos_sin_corregir"))
    ax.axhline(prom, color=TINTA2, linewidth=1, linestyle=(0, (4, 3)))
    ax.set_xlim(-0.6, 9.6)
    ax.text(9.68, prom, f"Promedio de la\npoblación: {pct(prom)}%", ha="left", va="center", fontsize=9,
            color=TINTA2, clip_on=False)
    ax.set_ylim(0, max(tope) * 1.1)
    ax.set_ylabel("% del ingreso")
    ax.set_xlabel("Decil de ingreso per cápita familiar (D1 = 10% más pobre)")
    fig.suptitle(f"Argentina {anio}: impuestos como porcentaje del ingreso, por decil", x=0.01, y=1.0,
                 ha="left", fontsize=14, fontweight="bold")
    lo, hi = d.loc[2:9].sum(axis=1).min(), d.loc[2:9].sum(axis=1).max()
    ax.set_title(f"Entre el decil 2 y el 9 la carga estimada va de {lo:.0f}% a {hi:.0f}%. En las puntas depende de "
                 "cómo se mida el ingreso: el decil 1 declara gastar más\nde lo que gana y el decil 10 subdeclara "
                 "sus ingresos en la encuesta, por lo que ambos se muestran como rango.", loc="left",
                 fontsize=10, color=TINTA2, pad=10)
    h, l = ax.get_legend_handles_labels()
    ax.legend(h[::-1], l[::-1], loc="lower left", bbox_to_anchor=(1.01, 0.0), frameon=False, fontsize=9)
    fig.text(0.01, -0.02, NOTA, fontsize=7.3, color=MUDO, ha="left", va="top")
    guardar(fig, f"fig1_tasa_por_decil_{anio}")


def fondo_serie(ax):
    ax.axvspan(2006.5, 2015.5, color="#f0efec", zorder=0)
    ax.text(2011, ax.get_ylim()[0] + 0.4, "2007-2015: estadísticas INDEC con reservas", ha="center", va="bottom",
            fontsize=8, color=MUDO)
    ax.set_xticks(range(2004, 2025, 2))
    ax.xaxis.grid(False)


def fig_serie(serie):
    s = serie[serie.variante == "principal"].set_index("anio")
    decl = serie[serie.variante == "ingreso_declarado"].set_index("anio")
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.set_ylim(10, 45)
    fondo_serie(ax)
    ax.fill_between(s.index, s.total_D1 * 100, decl.total_D1 * 100, color="#e34948", alpha=0.13, linewidth=0)
    ax.plot(decl.index, decl.total_D1 * 100, color="#e34948", linewidth=1.2, linestyle=(0, (2, 2)))
    ax.text(2019.6, 41.2, "Decil 1 si se divide por\nsu ingreso declarado", fontsize=8.5, color=TINTA2,
            ha="left", va="center")
    piso = serie[serie.variante == "altos_sin_corregir"].set_index("anio")
    techo = serie[serie.variante == "altos_registros"].set_index("anio")
    ax.fill_between(s.index, piso.total_D10 * 100, techo.total_D10 * 100, color="#2a78d6", alpha=0.12, linewidth=0)
    ax.text(2016.4, 14.5, "Franja azul: decil 10 entre «sólo EPH» (piso)\ny el techo con registros tributarios", fontsize=8.5,
            color=TINTA2, ha="left", va="center")
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
        ax.text(2024.25, pos[col], f"{etq}  {pct(y.iloc[-1])}%", va="center", fontsize=9, color=TINTA)
    ax.set_xlim(2003.5, 2024.2)
    ax.set_ylabel("% del ingreso")
    fig.suptitle("Tasa efectiva total por grupo de ingreso, 2004-2024", x=0.01, y=1.0, ha="left", fontsize=14,
                 fontweight="bold")
    ax.set_title("La carga subió para todos los grupos entre 2004 y 2015 y bajó en 2016-2019. Franjas: rango de los "
                 "deciles 1 y 10 según cómo se mida su ingreso.\nCírculos huecos: años con trimestres EPH faltantes "
                 "(2007, 2015, 2016).", loc="left", fontsize=9.5, color=TINTA2, pad=10)
    fig.text(0.01, -0.02, NOTA, fontsize=7.3, color=MUDO, ha="left", va="top")
    fig.subplots_adjust(right=0.8)
    guardar(fig, "fig2_serie_historica")


def fig_composicion(ancho):
    d = ancho[ancho.decil == 0].set_index("anio")[COLS] * 100
    fig, ax = plt.subplots(figsize=(11, 5.8))
    ax.stackplot(d.index, [d[c] for c in COLS], colors=[c for _, _, c in IMPUESTOS],
                 labels=[e for _, e, _ in IMPUESTOS], edgecolor=SUP, linewidth=1.0)
    ax.set_xlim(2004, 2024)
    ax.set_xticks(range(2004, 2025, 2))
    ax.set_ylabel("% del ingreso")
    ax.xaxis.grid(False)
    h, l = ax.get_legend_handles_labels()
    ax.legend(h[::-1], l[::-1], loc="center left", bbox_to_anchor=(1.01, 0.5), frameon=False, fontsize=9)
    fig.suptitle("Composición de la tasa efectiva promedio, 2004-2024", x=0.01, ha="left", fontsize=14,
                 fontweight="bold")
    ax.set_title("Total de la población de los aglomerados EPH. Hasta 2008 los aportes incluyen los destinados "
                 "a las AFJP.", loc="left", fontsize=10, color=TINTA2, pad=10)
    fig.text(0.01, -0.02, NOTA, fontsize=7.3, color=MUDO, ha="left", va="top")
    guardar(fig, "fig3_composicion_en_el_tiempo")


def fig_anios(ancho, largo, anios):
    fig, axes = plt.subplots(1, len(anios), figsize=(3.3 * len(anios), 5), sharey=True)
    for ax, a in zip(axes, anios):
        d = ancho[(ancho.anio == a) & (ancho.decil > 0)].set_index("decil")[COLS] * 100
        decl = largo[(largo.anio == a) & (largo.variante == "ingreso_declarado") & (largo.impuesto == "total")
                     & (largo.decil > 0)].set_index("decil").tasa * 100
        barras(ax, d, decl, etiquetas=False)
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


def fig_dos_versiones(largo, anio):
    """Las dos lecturas lado a lado: sin correcciones y con correcciones de ingreso."""
    def tabla(variante):
        v = largo[(largo.anio == anio) & (largo.variante == variante)]
        return v.pivot(index="decil", columns="impuesto", values="tasa") * 100
    paneles = [
        ("sin_correcciones", "A. Sin corregir: lo que declaran las encuestas",
         "Ingreso: el declarado en la EPH. Ganancias: sólo la simulada sobre los\n"
         "salarios y jubilaciones de la EPH (12% a 37% de lo recaudado).\n"
         "Es el criterio habitual de los estudios de incidencia. Sesgos conocidos:\n"
         "sobreestima el decil 1 (declara gastar más de lo que gana, así que su\n"
         "ingreso está mal medido) y subestima el decil 10 (falta la mayor parte\n"
         "de lo recaudado por Ganancias)."),
        ("principal", "B. Corregida: ingreso y recaudación ajustados",
         "Decil 1 a 3: si el gasto estimado (ENGHo) supera al ingreso declarado, se\n"
         "divide por el gasto. Decil 8 a 10: se agrega lo recaudado por Ganancias\n"
         "que la EPH no capta, repartido con las declaraciones juradas de ARCA.\n"
         "Sesgos conocidos: en el decil 1 mide impuesto sobre gasto, que es casi\n"
         "proporcional por construcción; si esos hogares de verdad se endeudan\n"
         "o desahorran, subestima su carga. El gasto es imputado, no observado."),
    ]
    fig, axes = plt.subplots(1, 2, figsize=(13.5, 6.2), sharey=True)
    for ax, (variante, titulo, nota) in zip(axes, paneles):
        t = tabla(variante)
        d = t.loc[1:10, COLS]
        prom = t.loc[0, "total"]
        tope = barras(ax, d)
        ax.axhline(prom, color=TINTA2, linewidth=1, linestyle=(0, (4, 3)))
        ax.text(9.5, 38.6, f"Línea punteada: promedio de la población, {pct(prom)}%", ha="right", va="center",
                fontsize=8.8, color=TINTA2)
        ax.set_title(titulo, loc="left", fontsize=11.5, fontweight="bold", pad=8)
        ax.text(0.0, -0.13, nota, transform=ax.transAxes, fontsize=8.3, color=TINTA2, ha="left", va="top",
                linespacing=1.35)
        ax.set_xlim(-0.6, 9.6)
    axes[0].set_ylim(0, 40)
    axes[0].set_ylabel("% del ingreso")
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h[::-1], l[::-1], loc="center left", bbox_to_anchor=(0.91, 0.55), frameon=False, fontsize=9)
    fig.suptitle(f"Argentina {anio}: impuestos como porcentaje del ingreso por decil, dos lecturas", x=0.01, y=1.03,
                 ha="left", fontsize=14, fontweight="bold")
    fig.text(0.01, 0.955, "Los deciles 3 a 9 casi no cambian. Las puntas dependen de cómo se mida el ingreso: la carga "
             "real del decil 1 y del decil 10 está entre los valores de A y B.\nEn ninguna de las dos lecturas el "
             "sistema es progresivo: en A los más pobres pagan la mayor proporción; en B todos pagan una proporción "
             "parecida de sus recursos.", fontsize=9.8, color=TINTA2, ha="left", va="top")
    fig.subplots_adjust(wspace=0.06, right=0.9, top=0.84)
    fig.text(0.01, -0.2, "Fuente: elaboración propia con EPH y ENGHo (INDEC), recaudación DNIAF (Min. de Economía), "
             "anuarios estadísticos de ARCA y normativa. Aglomerados urbanos de la EPH. Deciles de personas por "
             "ingreso per cápita familiar.\nIncluye Ganancias de personas, Bienes Personales, aportes, contribuciones "
             "patronales, IVA, Internos e Ingresos Brutos. Excluye retenciones, combustibles, Ganancias de sociedades, "
             "monotributo e impuestos patrimoniales provinciales. No estima el 1% superior.", fontsize=7.3,
             color=MUDO, ha="left", va="top")
    guardar(fig, f"fig0_dos_versiones_{anio}")


def fig_sensibilidad(largo, anio):
    v = largo[(largo.anio == anio) & (largo.impuesto == "total") & (largo.decil > 0)]
    v = v.pivot(index="decil", columns="variante", values="tasa") * 100
    incid = ["principal", "iva_legal", "contrib_100_trabajador", "contrib_100_consumidor",
             "altos_sin_corregir", "altos_registros", "sin_bienes_personales"]
    lo, hi = v[incid].min(axis=1), v[incid].max(axis=1)
    fig, ax = plt.subplots(figsize=(11, 5.6))
    x = list(range(1, 11))
    ax.bar(x, hi - lo, bottom=lo, width=0.5, color="#86b6ef", edgecolor="none",
           label="Rango por supuestos de incidencia (traslado de contribuciones,\nIVA legal o recaudado, "
                 "ingresos altos sin corregir o con registros tributarios, sin Bienes Personales)")
    ax.scatter(x, v["principal"], s=70, color=TINTA, zorder=3, label="Estimación principal")
    ax.scatter(x, v["ingreso_declarado"], s=70, facecolor=SUP, edgecolor="#e34948", linewidth=1.8, zorder=3,
               label="Dividiendo por el ingreso declarado (sin corregir gasto > ingreso)")
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
                 "cómo se mide el ingreso.", loc="left", fontsize=10, color=TINTA2, pad=10)
    fig.text(0.01, -0.02, NOTA, fontsize=7.3, color=MUDO, ha="left", va="top")
    guardar(fig, "fig5_sensibilidad")


def fig_poblacion_fija(serie, fija):
    s = serie[serie.variante == "principal"].set_index("anio")
    base = int(fija.anio_base.iloc[0])
    fig, axes = plt.subplots(1, 3, figsize=(12.5, 4.6), sharey=True)
    for ax, (dec, nombre, color) in zip(axes, [(1, "Decil 1", "#e34948"), (5, "Decil 5", "#eda100"),
                                                 (10, "Decil 10", "#2a78d6")]):
        f = fija[fija.decil == dec].set_index("anio").total * 100
        o = s[f"total_D{dec}"] * 100
        ax.plot(o.index, o, color=color, linewidth=2.2, label="Observada (población de cada año)")
        ax.plot(f.index, f, color=TINTA2, linewidth=1.8, linestyle=(0, (4, 2)),
                label=f"Población fija de {base}: sólo cambian las reglas\ny la presión tributaria agregada")
        ax.set_title(nombre, loc="left", fontsize=11, fontweight="bold")
        ax.set_xticks(range(2004, 2025, 4))
        ax.xaxis.grid(False)
    axes[0].set_ylabel("% del ingreso")
    axes[0].set_ylim(10, 32)
    axes[0].set_yticks(range(10, 33, 5))
    from matplotlib.lines import Line2D
    fig.legend([Line2D([], [], color=MUDO, linewidth=2.2), Line2D([], [], color=TINTA2, linewidth=1.8,
                                                                  linestyle=(0, (4, 2)))],
               ["Observada (línea de color): reglas y población de cada año",
                f"Población fija de {base}: sólo cambian las reglas y la presión tributaria agregada"],
               loc="lower center", ncol=2, frameon=False, fontsize=9, bbox_to_anchor=(0.5, -0.06))
    fig.suptitle("¿Cambiaron los impuestos o cambió la gente de cada decil?", x=0.01, ha="left", fontsize=14,
                 fontweight="bold")
    fig.text(0.01, 0.9, "La distancia entre ambas líneas es el efecto de composición: formalización laboral, "
             "estructura de ingresos y desigualdad.", fontsize=10, color=TINTA2)
    fig.subplots_adjust(top=0.8)
    fig.text(0.01, -0.08, NOTA, fontsize=7.3, color=MUDO, ha="left", va="top")
    guardar(fig, "fig6_poblacion_fija")


if __name__ == "__main__":
    ancho = pd.read_csv(TABLES / "tasas_por_decil_anual_ancho.csv")
    largo = pd.read_csv(TABLES / "tasas_por_decil_anual.csv")
    serie = pd.read_csv(TABLES / "serie_total_anual.csv")
    ultimo = int(ancho.anio.max())
    for f in FIGURES.glob("fig*"):
        f.unlink()
    fig_dos_versiones(largo, ultimo)
    fig_dos_versiones(largo, 2004)
    fig_principal(ancho, largo, ultimo)
    fig_principal(ancho, largo, 2004)
    fig_serie(serie)
    fig_composicion(ancho)
    fig_anios(ancho, largo, [2004, 2009, 2014, 2019, 2024])
    fig_sensibilidad(largo, ultimo)
    fija = TABLES / "serie_poblacion_fija.csv"
    if fija.exists():
        fig_poblacion_fija(serie, pd.read_csv(fija))
    print("Gráficos en", FIGURES)
