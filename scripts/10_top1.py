#!/usr/bin/env python
"""Tasa efectiva del 1% más rico a partir de las declaraciones juradas de Ganancias.

La EPH casi no capta a los más ricos. Este script estima su ingreso y su carga con los
anuarios de ARCA (declaraciones juradas de personas humanas por tramo de ingresos
gravados; scripts/aux_anuarios_arca.py), siguiendo a Alvaredo (2010).

Definiciones (supuestos marcados con *):
  Grupo        las N = 1% de la población total de mayores ingresos declarados al fisco*.
               Con N menor que la cantidad de declarantes, el grupo entero está dentro de
               las declaraciones. (Con adultos como unidad el grupo sería algo más chico.)
  Corte        los tramos se acumulan de mayor a menor; en el tramo donde se llega a N se
               interpola linealmente (casos, ingreso, impuesto y patrimonio).
  Ingreso      resultado neto (antes de deducciones personales) + ingresos exentos o no
               alcanzados, sin la venta de bienes o moneda extranjera; más la mitad de las
               contribuciones patronales sobre su parte salarial (como en los deciles).
  Ganancias    impuesto determinado del grupo.
  B. Pers.     recaudación de Bienes Personales × participación del grupo en el patrimonio
               neto declarado en Ganancias*.
  Aportes      PARTE_SALARIAL* del ingreso es salario: aportes personales (14%, con tope)
               y la mitad de las contribuciones patronales (sin tope).
  Consumo      ingreso × gasto/ingreso del veintil más rico de la ENGHo (cota alta*; el
               1% gasta una proporción menor) y la mitad (cota baja*). Impuestos por peso de
               consumo: (IVA + Internos + Ingresos Brutos + ½ contribuciones) / consumo privado.
  Sociedades   sensibilidad: el grupo es dueño de PARTE_SOCIEDADES* de las empresas. Se le
               atribuyen esa parte de la Ganancias de sociedades y de las utilidades antes de
               impuesto que la generaron (impuesto / TASA_SOCIEDADES*), como hacen las cuentas
               nacionales distributivas: las ganancias retenidas en las empresas son ingreso de
               sus dueños. No hay datos de tenencia accionaria.
  Activos ext. renta de RENTA_EXTERIOR* sobre la inversión de cartera en el exterior del sector
               privado no financiero (acciones y bonos, PII del INDEC), toda atribuida al grupo y
               sin impuesto: el mismo supuesto que el panel B de la figura 0 (variante
               ajuste_cn_rentas_cartera_ext de incidencia.py). Moneda y depósitos (billetes
               fuera del sistema, que no rinden) quedan afuera; la versión con todo el stock al
               RENTA_EXTERIOR_TODO* queda como cota (columna completo_ext_todo_stock).
Estimación principal ("completo"): ingreso declarado + utilidades de las empresas + renta de
activos externos, y todos los impuestos atribuibles; el rango refleja el consumo. Aun así el
ingreso declarado al fisco sigue subdeclarado (rentas internas no declaradas): la tasa es
un techo.

Años sin declaraciones publicadas (hoy, 2025: el último anuario de ARCA, el de 2025, informa el
año fiscal 2024): se usan las del último año fiscal disponible llevadas al año con la variación
del ingreso del decil 10 de la EPH (como en 09_ingresos_altos.py).

Salida: outputs/tables/top1.csv
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from incidencia.config import ANIO_FIN, PARAMS, PROCESSED, TABLES  # noqa: E402

FRACCION = 0.01
PARTE_SALARIAL = 0.5
PARTE_SOCIEDADES = 0.5
TASA_SOCIEDADES = 0.30    # impuesto / utilidad antes de impuesto (alícuota legal 25%-35%)
RENTA_EXTERIOR = 0.04      # sobre la cartera, como incidencia.py
RENTA_EXTERIOR_TODO = 0.03 # cota: sobre cartera + moneda y depósitos
APORTES = 0.14            # jubilación 11% + INSSJP 3%
CONTRIB = 0.20            # contribución patronal aproximada (Dto. 814/2001 y modif.)


def acumular(d: pd.DataFrame, n: float) -> dict:
    """Totales de las n declaraciones de mayores ingresos (interpolación lineal en el corte)."""
    d = d.sort_values("desde", ascending=False)
    cols = ["ingreso", "impuesto", "patrimonio_neto"]
    acc = {c: 0.0 for c in cols}
    restante = n
    for _, f in d.iterrows():
        k = min(1.0, restante / f.casos)
        for c in cols:
            acc[c] += k * f[c]
        restante -= k * f.casos
        if restante <= 1e-9:
            acc["umbral"] = f.desde + (1 - k) * ((f.hasta if np.isfinite(f.hasta) else f.desde * 2) - f.desde)
            break
    acc["n"] = n - max(restante, 0)
    return acc


def gasto_top(engho: pd.DataFrame, anio: int) -> float:
    ed = 2004 if anio < 2009 else (2012 if anio < 2016 else 2017)
    return float(engho[(engho.edicion == ed) & (engho.grupo == engho.grupo.max())].gasto_sobre_ingreso.iloc[0])


def main() -> None:
    ddjj = pd.read_csv(PROCESSED / "ddjj_ganancias_tramos.csv")
    total = ddjj[ddjj.es_total].set_index("anio_fiscal")
    tramos = ddjj[~ddjj.es_total].copy()
    tramos["ingreso"] = tramos.resultado_neto + (tramos.exentos.fillna(0) - tramos.exentos_ventas.fillna(0))
    rec = pd.read_csv(PROCESSED / "recaudacion_macro.csv", index_col=0)
    engho = pd.read_csv(PROCESSED / "engho_grupos.csv")
    lmi = pd.read_csv(PARAMS / "lmi.csv")
    lmi["anio"] = lmi.mes.str[:4].astype(int)
    tope = lmi.groupby("anio").tope_jubilacion.mean() * 13
    q = pd.read_csv(PROCESSED / "eph_trimestral_decil.csv")
    d10 = q[q.decil == 10].groupby("anio").mean(numeric_only=True)
    crec = (d10.ipcf / d10.personas)

    filas = []
    for anio in range(2004, ANIO_FIN + 1):
        fiscal = min(anio, int(total.index.max()))
        esc = crec[anio] / crec[fiscal]
        n = FRACCION * rec.poblacion[anio]
        a = acumular(tramos[tramos.anio_fiscal == fiscal], n)
        r = rec.loc[anio]
        ing = a["ingreso"] * esc
        salario = PARTE_SALARIAL * ing
        ing_total = ing + 0.5 * CONTRIB * salario
        ganancias = a["impuesto"] * esc
        bp = r.bienes_personales * 1e6 * a["patrimonio_neto"] / total.patrimonio_neto[fiscal]
        aportes = APORTES * np.minimum(salario / n, tope[anio]) * n + 0.5 * CONTRIB * salario
        por_peso = (r.iva + r.internos_modelados + r.ingresos_brutos + 0.5 * r.ss_empleadores) / r.consumo_privado
        c_alto = gasto_top(engho, anio)
        consumo_alto = por_peso * c_alto * ing
        imp_soc = PARTE_SOCIEDADES * r.ganancias_sociedades * 1e6
        util_soc = imp_soc / TASA_SOCIEDADES
        cn = pd.read_csv(PROCESSED / "cn_ingresos.csv", index_col=0).loc[anio]
        renta_ext = RENTA_EXTERIOR * cn.pii_cartera_musd * cn.tc * 1e6
        renta_ext_todo = RENTA_EXTERIOR_TODO * (cn.pii_cartera_musd + cn.pii_mondep_musd) * cn.tc * 1e6
        base = ganancias + bp + aportes
        centro = base + 0.75 * consumo_alto
        filas.append({
            "anio": anio, "anio_fiscal_ddjj": fiscal, "personas": n,
            "umbral_anual": a["umbral"] * esc, "ingreso_medio_anual": ing_total / n,
            "ganancias": ganancias / ing_total, "bienes_personales": bp / ing_total,
            "aportes_contrib": aportes / ing_total,
            "consumo_cota_alta": consumo_alto / ing_total, "consumo_cota_baja": 0.5 * consumo_alto / ing_total,
            "total_bajo": (base + 0.5 * consumo_alto) / ing_total,
            "total_alto": (base + consumo_alto) / ing_total,
            "total_central": centro / ing_total,
            "con_sociedades": (centro + imp_soc) / (ing_total + util_soc),
            "con_sociedades_y_activos_ext": (centro + imp_soc) / (ing_total + util_soc + renta_ext),
            # estimación completa (principal): todo el ingreso y todos los impuestos que se pueden
            # atribuir; el rango es el del consumo
            "completo": (centro + imp_soc) / (ing_total + util_soc + renta_ext),
            "completo_bajo": (base + 0.5 * consumo_alto + imp_soc) / (ing_total + util_soc + renta_ext),
            "completo_alto": (base + consumo_alto + imp_soc) / (ing_total + util_soc + renta_ext),
            "completo_ext_todo_stock": (centro + imp_soc) / (ing_total + util_soc + renta_ext_todo),
            # composición comparable con el 1% de la encuesta (figura 7)
            "consumo_central": 0.75 * consumo_alto / ing_total,
            "utilidades_sobre_ingreso": util_soc / ing_total, "renta_ext_sobre_ingreso": renta_ext / ing_total,
            "gasto_sobre_ingreso_usado": c_alto,
        })
    out = pd.DataFrame(filas)
    out.to_csv(TABLES / "top1.csv", index=False)
    v = out.set_index("anio")
    print((v[["ganancias", "bienes_personales", "aportes_contrib", "consumo_cota_baja", "consumo_cota_alta",
              "total_bajo", "total_alto", "total_central", "con_sociedades", "completo_bajo", "completo",
              "completo_alto",
              "utilidades_sobre_ingreso", "renta_ext_sobre_ingreso"]] * 100).round(1).to_string())
    print("OK ->", TABLES / "top1.csv")


if __name__ == "__main__":
    main()
