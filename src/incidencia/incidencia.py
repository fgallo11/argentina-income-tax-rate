"""Combina impuestos directos (microsimulados) e indirectos por decil para un trimestre."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .indirectos import perfil_consumo, tasas_indirectas

IMPUESTOS = ["ganancias", "bienes_personales", "aportes", "contrib_trabajador",
             "contrib_consumidor", "iva", "internos", "iibb"]
DIRECTOS = ["ganancias", "bienes_personales", "aportes", "contrib_trabajador"]
INDIRECTOS = ["contrib_consumidor", "iva", "internos", "iibb"]


@dataclass(frozen=True)
class Variante:
    """Conjunto de supuestos. Los valores por defecto definen la variante principal."""
    nombre: str = "principal"
    # Recursos del hogar: si el gasto de consumo estimado de un decil supera su ingreso
    # declarado, se toma el gasto como medida de sus recursos (ingreso = max(ingreso, gasto)).
    corregir_recursos: bool = True
    modo_engho: str = "interpolado"       # "interpolado" | "escalonado" | "2004" | "2012" | "2017"
    iva_nivel_legal: bool = False         # True: alícuota legal plena (sin evasión)
    fraccion_contrib_trabajador: float = 0.5
    incluir_afjp: bool = True             # aportes a AFJP 2004-2007 como impuesto
    incluir_bp: bool = True               # Bienes Personales imputado al decil 10
    calibrar_ganancias: bool = False      # reescalar Ganancias a la recaudación
    sobre_ipcf: bool = False              # denominador = ingreso de bolsillo
    # Corrección de ingresos altos con datos tributarios (scripts/09_ingresos_altos.py):
    #   "no"        sólo lo simulado sobre la EPH
    #   "cobertura" Ganancias y Bienes Personales faltantes, por peso de consumo privado
    #               (misma escala que los impuestos indirectos); no agrega ingreso
    #   "registros" Ganancias y Bienes Personales faltantes por habitante, y se suma al
    #               ingreso el ingreso declarado al fisco que la EPH no capta
    altos_ingresos: str = "cobertura"


VARIANTES = [
    Variante(),
    Variante("ingreso_declarado", corregir_recursos=False),
    Variante("sin_correcciones", corregir_recursos=False, altos_ingresos="no"),
    Variante("engho_escalonado", modo_engho="escalonado"),
    Variante("iva_legal", iva_nivel_legal=True),
    Variante("contrib_100_trabajador", fraccion_contrib_trabajador=1.0),
    Variante("contrib_100_consumidor", fraccion_contrib_trabajador=0.0),
    Variante("sin_afjp", incluir_afjp=False),
    Variante("sin_bienes_personales", incluir_bp=False),
    Variante("altos_sin_corregir", altos_ingresos="no"),
    Variante("altos_registros", altos_ingresos="registros"),
    Variante("ganancias_calibrada", calibrar_ganancias=True, altos_ingresos="no"),
    Variante("sobre_ipcf", sobre_ipcf=True),
    Variante("criterio_inicial", corregir_recursos=False, modo_engho="escalonado", altos_ingresos="no"),
]


def incidencia_trimestre(q: pd.DataFrame, anio: int, engho: pd.DataFrame, rec: pd.Series,
                         v: Variante = Variante()) -> pd.DataFrame:
    """q: una fila por decil con totales expandidos mensuales (salida de la microsimulación).

    Devuelve tasas (impuesto / ingreso) por decil; la fila 0 es el total de la población.
    """
    q = q.set_index("decil").sort_index()
    media = q.ipcf.sum() / q.personas.sum()
    rel = (q.ipcf / q.personas / media).values
    perfil = perfil_consumo(anio, rel, engho, v.modo_engho)
    perfil.index = q.index
    consumo = perfil.consumo_rel * media * q.personas
    ti = tasas_indirectas(perfil, consumo.values, rec, v.iva_nivel_legal)

    f = v.fraccion_contrib_trabajador
    afjp = q.ap_jub_afjp if "ap_jub_afjp" in q else 0.0
    t = pd.DataFrame(index=q.index)
    t["ganancias"] = q.ganancias
    t["aportes"] = q.ap_jub + q.ap_inssjp - (0.0 if v.incluir_afjp else afjp)
    t["contrib_trabajador"] = f * q.contrib
    # La parte trasladada a precios se trata como los demás impuestos trasladados:
    # recaudación por peso de consumo privado de Cuentas Nacionales × consumo de la encuesta.
    # (Antes se repartía lo simulado sobre la EPH entero sobre el consumo de la encuesta,
    # lo que daba ~2 veces la carga por peso de consumo; ver docs/auditoria.md, 4.2.)
    t["contrib_consumidor"] = (1 - f) * rec["ss_empleadores"] / rec["consumo_privado"] * consumo
    t["iva"] = ti.iva * consumo
    t["internos"] = ti.internos * consumo
    t["iibb"] = ti.iibb * consumo
    bp = pd.Series(0.0, index=q.index)
    if v.incluir_bp:
        # recaudación por peso de consumo privado, aplicada al consumo total de la encuesta
        # y asignada íntegramente al decil 10 (SUPUESTO; ver docs/metodologia.md)
        bp.loc[10] = rec["bienes_personales"] / rec["consumo_privado"] * consumo.sum()
    t["bienes_personales"] = bp
    if v.calibrar_ganancias and q.ganancias.sum() > 0:
        objetivo = rec["ganancias_pf"] / rec["consumo_privado"] * consumo.sum()
        t["ganancias"] = q.ganancias * objetivo / q.ganancias.sum()

    # ingreso antes de impuestos directos
    adic = q.ing_pre_adic - 0.5 * q.contrib + f * q.contrib + (t.ganancias - q.ganancias)
    if v.altos_ingresos != "no":
        partes = np.array([rec[f"parte_d{d}"] for d in q.index])
        if v.altos_ingresos == "registros":
            esc = 1e6 / 12 * q.personas.sum() / rec["poblacion"]    # millones anuales país -> pesos mensuales EPH
            adic = adic + rec["ingreso_faltante_mill"] * esc * partes
        else:
            esc = consumo.sum() / rec["consumo_privado"]
        t["ganancias"] = t.ganancias + rec["ganancias_faltante_mill"] * esc * partes
        if v.incluir_bp:
            t["bienes_personales"] = rec["bienes_personales"] * esc * partes
    base = np.maximum(q.ipcf, consumo) if v.corregir_recursos else q.ipcf
    den = q.ipcf if v.sobre_ipcf else base + adic

    tasas = t[IMPUESTOS].div(den, axis=0)
    tot = t[IMPUESTOS].sum() / den.sum()
    tasas.loc[0] = tot
    tasas["total"] = tasas[IMPUESTOS].sum(axis=1)
    tasas["directos"] = tasas[DIRECTOS].sum(axis=1)
    tasas["indirectos"] = tasas[INDIRECTOS].sum(axis=1)
    tasas["ingreso_rel"] = np.append(rel, 1.0)
    tasas["gasto_sobre_ingreso_declarado"] = np.append((consumo / q.ipcf).values, consumo.sum() / q.ipcf.sum())
    tasas["ajuste_recursos"] = np.append((base / q.ipcf - 1).values, base.sum() / q.ipcf.sum() - 1)
    return tasas


def promedio_anual(q_anio: pd.DataFrame, anio: int, engho, rec_anio, v: Variante) -> pd.DataFrame:
    """Promedio simple de los trimestres disponibles (indicador calculado por trimestre)."""
    trims = [incidencia_trimestre(qt, anio, engho, rec_anio, v) for _, qt in q_anio.groupby("trim")]
    prom = (sum(trims) / len(trims)).reset_index().rename(columns={"index": "decil"})
    prom["trimestres"] = len(trims)
    return prom
