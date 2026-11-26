#!/usr/bin/env python
"""Medida de control del 1% más rico: el grupo armado sólo con las declaraciones juradas de Ganancias.

La EPH casi no capta a los más ricos. La medida del informe completa la encuesta con las
declaraciones juradas (11_tramos_decil10.py, versión A). Este script arma el 1% con los
anuarios de ARCA solos (declaraciones juradas de personas humanas por tramo de ingresos
gravados; scripts/aux_anuarios_arca.py), siguiendo a Alvaredo (2010). Es la "medida C" del
informe: un control, porque sólo existe para el 1% y no se puede combinar con los demás grupos.

Definiciones (supuestos marcados con *):
  Grupo        las N = 1% de la población total de mayores ingresos declarados al fisco*.
               Los tramos se acumulan de mayor a menor; en el tramo donde se llega a N se
               interpola linealmente.
  Ingreso      resultado neto (antes de deducciones personales) + ingresos exentos o no
               alcanzados, sin la venta de bienes o moneda extranjera; más la mitad de las
               contribuciones patronales sobre sus sueldos (como en los deciles).
  Ganancias    impuesto determinado del grupo (dato).
  B. Pers.     recaudación de Bienes Personales × participación del grupo en el patrimonio
               neto declarado en Ganancias*.
  Aportes      los aportes personales que el grupo descuenta en su declaración: jubilación,
               obra social, cajas provinciales y complementarias y autónomos (dato).
  Contrib.     la mitad del 20% sobre los sueldos del grupo. Sueldos = 4ta categoría neta ×
               (quienes descuentan aportes como empleados / quienes declaran 4ta categoría)*:
               se supone que los empleados del grupo ganan lo mismo, en promedio, que el resto
               de quienes declaran trabajo personal (jubilados, directores, independientes).
  Consumo      ninguna fuente lo mide. Dos aproximaciones que fallan en sentidos opuestos:
               - el "monto consumido" que ARCA calcula como saldo de la justificación
                 patrimonial (no lo declara el contribuyente; incluye el gasto en el exterior
                 y crece si el patrimonio se declara por debajo de su valor): alta;
               - el consumo del 1% en la versión A (lo mismo en pesos que el 5% más rico de la
                 ENGHo; columna consumo_sobre_ingreso de tasas_tramos_decil10.csv): baja.
               Se usa el punto medio*, año por año. Impuestos por peso de consumo:
               (IVA + Internos + Ingresos Brutos + ½ contribuciones) / consumo privado.
  Ingreso no declarado
               escenarios: el grupo no declara el 5%, el 10% o el 25% de su ingreso no
               salarial (todo lo que no es sueldo). Ese ingreso se suma al denominador y no
               paga impuestos. El 25% es del orden de lo que Alstadsæter, Johannesen y Zucman
               (2019) encuentran para el 0,01% más rico: un techo para el 1%.
Para que sea comparable con la versión A, no incluye Ganancias de sociedades ni la renta de
activos en el exterior.

Antes de 2012 pocos empleados descontaban sus aportes en la declaración jurada: dentro del 1%,
entre el 3% y el 25% de quienes declaraban 4ta categoría, contra 39% a 61% desde 2012. La
medida se informa desde 2012 (columna confiable).

Años sin declaraciones publicadas (hoy, 2025: el último anuario de ARCA, el de 2025, informa el
año fiscal 2024): se usan las del último año fiscal disponible llevadas al año con la variación
del ingreso del decil 10 de la EPH (como en 09_ingresos_altos.py).

Requiere outputs/tables/tasas_tramos_decil10.csv (11_tramos_decil10.py).
Salida: outputs/tables/top1.csv
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from incidencia.config import ANIO_FIN, PROCESSED, TABLES  # noqa: E402

FRACCION = 0.01
CONTRIB = 0.20            # contribución patronal aproximada (Dto. 814/2001 y modif.)
DESDE_CONFIABLE = 2012    # antes, pocos empleados declaraban sus aportes
NO_DECLARADO = {"oculta05": 0.05, "oculta10": 0.10, "oculta25": 0.25}
COLS = ["ingreso", "impuesto", "patrimonio_neto", "cuarta", "aportes_deducidos", "monto_consumido",
        "casos_cuarta", "casos_aportes_empleado"]


def acumular(d: pd.DataFrame, n: float) -> dict:
    """Totales de las n declaraciones de mayores ingresos (interpolación lineal en el corte)."""
    d = d.sort_values("desde", ascending=False)
    acc = {c: 0.0 for c in COLS}
    restante = n
    for _, f in d.iterrows():
        k = min(1.0, restante / f.casos)
        for c in COLS:
            acc[c] += k * f[c]
        restante -= k * f.casos
        if restante <= 1e-9:
            acc["umbral"] = f.desde + (1 - k) * ((f.hasta if np.isfinite(f.hasta) else f.desde * 2) - f.desde)
            break
    acc["n"] = n - max(restante, 0)
    return acc


def main() -> None:
    ddjj = pd.read_csv(PROCESSED / "ddjj_ganancias_tramos.csv")
    total = ddjj[ddjj.es_total].set_index("anio_fiscal")
    tramos = ddjj[~ddjj.es_total].copy()
    tramos["ingreso"] = tramos.resultado_neto + (tramos.exentos.fillna(0) - tramos.exentos_ventas.fillna(0))
    tramos["cuarta"] = tramos.cuarta_bruta - tramos.cuarta_gastos
    rec = pd.read_csv(PROCESSED / "recaudacion_macro.csv", index_col=0)
    q = pd.read_csv(PROCESSED / "eph_trimestral_decil.csv")
    d10 = q[q.decil == 10].groupby("anio").mean(numeric_only=True)
    crec = (d10.ipcf / d10.personas)
    tr = pd.read_csv(TABLES / "tasas_tramos_decil10.csv")
    cons_a = tr[(tr.variante == "principal") & (tr.grupo == 99)].set_index("anio").consumo_sobre_ingreso

    filas = []
    for anio in range(2004, ANIO_FIN + 1):
        fiscal = min(anio, int(total.index.max()))
        esc = crec[anio] / crec[fiscal]
        n = FRACCION * rec.poblacion[anio]
        a = acumular(tramos[tramos.anio_fiscal == fiscal], n)
        r = rec.loc[anio]
        ing = a["ingreso"] * esc
        parte_emp = a["casos_aportes_empleado"] / a["casos_cuarta"]
        sueldos = a["cuarta"] * esc * parte_emp
        contrib = 0.5 * CONTRIB * sueldos
        ing_total = ing + contrib
        ganancias = a["impuesto"] * esc
        bp = r.bienes_personales * 1e6 * a["patrimonio_neto"] / total.patrimonio_neto[fiscal]
        aportes = a["aportes_deducidos"] * esc
        por_peso = (r.iva + r.internos_modelados + r.ingresos_brutos + 0.5 * r.ss_empleadores) / r.consumo_privado
        c_arca = a["monto_consumido"] * esc / ing_total
        c_enc = float(cons_a[anio])
        c_usado = (c_arca + c_enc) / 2
        consumo = por_peso * c_usado * ing_total
        imp = ganancias + bp + aportes + contrib + consumo
        no_salarial = ing - sueldos
        fila = {
            "anio": anio, "anio_fiscal_ddjj": fiscal, "personas": n, "confiable": anio >= DESDE_CONFIABLE,
            "umbral_anual": a["umbral"] * esc, "ingreso_medio_anual": ing_total / n,
            "ganancias": ganancias / ing_total, "bienes_personales": bp / ing_total,
            "aportes_personales": aportes / ing_total, "contribuciones": contrib / ing_total,
            "aportes_contrib": (aportes + contrib) / ing_total, "consumo": consumo / ing_total,
            "parte_empleados": parte_emp, "no_salarial_sobre_ingreso": no_salarial / ing_total,
            "consumo_arca": c_arca, "consumo_encuesta": c_enc, "consumo_usado": c_usado,
            "impuesto_por_peso_consumido": por_peso,
            "total": imp / ing_total,
        }
        for k, x in NO_DECLARADO.items():
            # no declara la fracción x de su ingreso no salarial: lo declarado es (1 - x) del real
            fila[f"total_{k}"] = imp / (ing_total + no_salarial * x / (1 - x))
        filas.append(fila)
    out = pd.DataFrame(filas)
    out.to_csv(TABLES / "top1.csv", index=False)
    v = out[out.confiable].set_index("anio")
    print((v[["ganancias", "bienes_personales", "aportes_personales", "contribuciones", "consumo", "total",
              "total_oculta05", "total_oculta10", "total_oculta25", "consumo_arca", "consumo_encuesta",
              "parte_empleados"]] * 100).round(1).to_string())
    print("OK ->", TABLES / "top1.csv")


if __name__ == "__main__":
    main()
