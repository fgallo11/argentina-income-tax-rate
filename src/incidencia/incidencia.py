"""Combina impuestos directos (microsimulados) e indirectos por decil para un trimestre."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .indirectos import perfil_consumo, tasas_indirectas

IMPUESTOS = ["ganancias", "bienes_personales", "aportes", "contrib_trabajador", "monotributo",
             "contrib_consumidor", "iva", "internos", "iibb", "cheque", "combustibles"]
DIRECTOS = ["ganancias", "bienes_personales", "aportes", "contrib_trabajador", "monotributo"]
INDIRECTOS = ["contrib_consumidor", "iva", "internos", "iibb", "cheque", "combustibles"]


@dataclass(frozen=True)
class Variante:
    """Conjunto de supuestos. Los valores por defecto definen la variante principal."""
    nombre: str = "principal"
    # Recursos del hogar. Principal: el ingreso declarado (la pregunta es qué parte de lo
    # que se gana va a impuestos). Con True, si el gasto de consumo estimado de un decil
    # supera su ingreso declarado se toma el gasto (variante `recursos_gasto`; era la
    # principal hasta la auditoría de 11/2026, que la objetó por corregir sólo abajo).
    corregir_recursos: bool = False
    modo_engho: str = "interpolado"       # "interpolado" | "escalonado" | "2004" | "2012" | "2017"
    iva_nivel_legal: bool = False         # True: alícuota legal plena (sin evasión)
    fraccion_contrib_trabajador: float = 0.5
    incluir_afjp: bool = True             # aportes a AFJP 2004-2007 como impuesto
    incluir_bp: bool = True               # Bienes Personales imputado al decil 10
    calibrar_ganancias: bool = False      # reescalar Ganancias a la recaudación
    sobre_ipcf: bool = False              # denominador = ingreso de bolsillo
    # Lectura "contra consumo": en TODOS los deciles los recursos son el gasto de consumo
    # (ENGHo, por ingreso relativo) más los impuestos directos; los deciles siguen
    # ordenados por ingreso. Es la medida de bienestar alternativa al ingreso corriente.
    sobre_consumo: bool = False
    # Corrección de ingresos altos con datos tributarios (scripts/09_ingresos_altos.py):
    #   "no"        sólo lo simulado sobre la EPH
    #   "cobertura" Ganancias y Bienes Personales faltantes, por peso de consumo privado
    #               (misma escala que los impuestos indirectos); no agrega ingreso
    #   "registros" Ganancias y Bienes Personales faltantes por habitante, y se suma al
    #               ingreso el ingreso declarado al fisco que la EPH no capta
    altos_ingresos: str = "cobertura"
    # Ajuste a Cuentas Nacionales (scripts/aux_cuentas_nacionales.py). El ingreso de cada
    # fuente se lleva al total de Cuentas Nacionales con un factor por fuente, aplicado a
    # quien declara esa fuente: salarios a la remuneración al trabajo asalariado, ingreso
    # de independientes al ingreso mixto bruto. El nivel de la carga total se mantiene igual
    # al de la medida principal (todos los impuestos se escalan por el mismo factor): el
    # ajuste muestra cómo cambia el reparto. Llevar los impuestos a la escala de lo
    # recaudado no es coherente mientras falten las rentas de los hogares en el ingreso.
    ajuste_cn: bool = False
    # Sensibilidad: renta anual de los activos externos del sector privado no financiero
    # (inversión de cartera + moneda y depósitos, PII del INDEC) a esta tasa, sumada al
    # ingreso de los deciles altos con el reparto de las declaraciones juradas. Cota alta:
    # supone que nada de eso se declara y que los billetes rinden como depósitos.
    renta_activos_ext: float = 0.0
    # Base y reparto de esa renta. "todo": inversión de cartera + moneda y depósitos (incluye los
    # billetes fuera del sistema, muy repartidos: cota alta), repartido como la Ganancias faltante.
    # "cartera": sólo inversión de cartera (acciones, fondos y bonos), asignada entera a la cima
    # (1% superior; decil 10 en la medida por deciles): quienes declaran bienes en el exterior en
    # Bienes Personales son ~87.000 personas (anuario ARCA, cuadro 2.5.1.2.3), dentro del 1%.
    base_activos_ext: str = "todo"
    # Impuestos que la medida principal excluye y que Pessino et al. (2023) incluyen: el
    # impuesto a los créditos y débitos bancarios ("cheque") y el de combustibles. Se
    # trasladan a precios y se reparten según el consumo de cada decil (supuesto: el
    # cheque actúa en cascada como Ingresos Brutos; combustibles, sin canasta propia).
    incluir_cheque: bool = False
    incluir_combustibles: bool = False
    # Pessino et al. (2023): los bienes exentos de IVA cargan el 20% de la alícuota por el IVA
    # de sus insumos. Cambia el reparto del IVA entre deciles (el nivel sigue en lo recaudado).
    iva_exentos: float = 0.0
    # De Rosa, Flores y Morgan (2024): las encuestas captan entre 1/5 y 1/10 de las rentas de
    # la propiedad. Con ajuste_cn, multiplica las rentas declaradas en la EPH (alquileres,
    # intereses, ganancias de negocios) por este factor. 1 = sin ajuste.
    factor_rentas: float = 1.0
    # Consumo por encima del veintil más alto de la ENGHo (sólo afecta a los tramos del decil 10):
    # "nivel" (fijo) o "proporcional" (mismo cociente gasto/ingreso que ese veintil).
    extrapolar_consumo: str = "nivel"
    # Monotributo de los independientes (directos.monotributo_mes): cuota de su categoría
    # (impuesto integrado + aporte jubilatorio, sin obra social), escalada para que el impuesto
    # integrado sume lo recaudado (DNIAF 5.2) por habitante. Se suma también al ingreso antes
    # de impuestos (el ingreso de la EPH de los independientes se supone neto de la cuota).
    incluir_monotributo: bool = False


VARIANTES = [
    Variante(),
    Variante("recursos_gasto", corregir_recursos=True),
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
    Variante("sobre_consumo", sobre_consumo=True),
    Variante("ajuste_cn", ajuste_cn=True),
    Variante("ajuste_cn_activos_ext", ajuste_cn=True, renta_activos_ext=0.03),
    Variante("con_cheque", incluir_cheque=True),
    Variante("con_cheque_y_combustibles", incluir_cheque=True, incluir_combustibles=True),
    Variante("con_monotributo", incluir_monotributo=True),
    Variante("iva_exentos_20", iva_exentos=0.2),
    Variante("ajuste_cn_rentas", ajuste_cn=True, factor_rentas=7.0),
    Variante("ajuste_cn_rentas_activos_ext", ajuste_cn=True, factor_rentas=7.0, renta_activos_ext=0.03),
    Variante("ajuste_cn_rentas_cartera_ext", ajuste_cn=True, factor_rentas=7.0, renta_activos_ext=0.04,
             base_activos_ext="cartera"),
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
    perfil = perfil_consumo(anio, rel, engho, v.modo_engho, v.iva_exentos, v.extrapolar_consumo)
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
    t["cheque"] = (rec["creditos_debitos"] / rec["consumo_privado"] * consumo) if v.incluir_cheque else 0.0 * consumo
    t["combustibles"] = ((rec["sel_combustibles"] / rec["consumo_privado"] * consumo) if v.incluir_combustibles
                         else 0.0 * consumo)
    esc_pais = 1e6 / 12 * q.personas.sum() / rec["poblacion"]   # millones anuales país -> pesos mensuales EPH
    t["monotributo"] = 0.0
    if v.incluir_monotributo and "mono_imp" in q and q.mono_imp.sum() > 0:
        k_mono = rec["monotributo"] * esc_pais / q.mono_imp.sum()
        t["monotributo"] = k_mono * (q.mono_imp + q.mono_sipa)
    bp = pd.Series(0.0, index=q.index)
    if v.incluir_bp:
        # recaudación por peso de consumo privado, aplicada al consumo total de la encuesta
        # y asignada íntegramente al decil 10 (SUPUESTO; ver docs/metodologia.md)
        arriba = 10 if 10 in q.index else 99     # con el decil 10 partido, al 1% superior
        bp.loc[arriba] = rec["bienes_personales"] / rec["consumo_privado"] * consumo.sum()
    t["bienes_personales"] = bp
    if v.calibrar_ganancias and q.ganancias.sum() > 0:
        objetivo = rec["ganancias_pf"] / rec["consumo_privado"] * consumo.sum()
        t["ganancias"] = q.ganancias * objetivo / q.ganancias.sum()

    # ingreso antes de impuestos directos
    adic = q.ing_pre_adic - 0.5 * q.contrib + f * q.contrib + (t.ganancias - q.ganancias) + t.monotributo
    if v.altos_ingresos == "registros":
        partes = np.array([rec[f"parte_d{d}"] for d in q.index])
        adic = adic + rec["ingreso_faltante_mill"] * esc_pais * partes
        t["ganancias"] = t.ganancias + rec["ganancias_faltante_mill"] * esc_pais * partes
        if v.incluir_bp:
            t["bienes_personales"] = rec["bienes_personales"] * esc_pais * partes
    elif v.altos_ingresos != "no":
        # Medida principal (corregida el 16/11/2026). Dos partes:
        #  a) Las n* personas de arriba (empalme EPH-declaraciones juradas): se les suma el ingreso
        #     que la EPH no capta y la Ganancias que declaran y la EPH no simula, los dos de las
        #     declaraciones juradas y en pesos reales por habitante. Así ese grupo queda con el
        #     ingreso y el impuesto de sus declaraciones.
        #  b) El resto de la Ganancias faltante lo pagan los demás declarantes, cuyo ingreso la
        #     EPH sí capta: impuesto sin ingreso adicional, en la escala de la encuesta
        #     (recaudación por peso de consumo privado), repartido según dónde viven.
        # Antes toda la Ganancias faltante iba a las personas de arriba sin su ingreso: el 1% de la
        # encuesta quedaba con más Ganancias sobre su ingreso que el 1% de las declaraciones.
        partes = np.array([rec[f"parte_d{d}"] for d in q.index])
        resto = np.array([rec[f"resto_d{d}"] for d in q.index])
        esc_c = consumo.sum() / rec["consumo_privado"]
        g_emp = rec["ganancias_faltante_empalme_mill"]
        g_resto = rec["ganancias_faltante_mill"] - g_emp
        adic = adic + rec["ingreso_faltante_completo_mill"] * esc_pais * partes   # con rentas exentas
        t["ganancias"] = t.ganancias + g_emp * esc_pais * partes + g_resto * esc_c * resto
        if v.incluir_bp:
            sh = rec["patrimonio_ddjj_empalme_sobre_total"]
            t["bienes_personales"] = rec["bienes_personales"] * (sh * esc_pais * partes + (1 - sh) * esc_c * resto)
    if v.sobre_consumo:
        base = consumo
    else:
        base = np.maximum(q.ipcf, consumo) if v.corregir_recursos else q.ipcf
    if v.ajuste_cn:
        den_sin_ajuste = (base + adic).sum()
        adic = adic + (1 / rec["cob_asal"] - 1) * (q.masa_bruta_reg + q.ing_lab_asal_no_reg)
        adic = adic + (1 / rec["cob_imb"] - 1) * (q.ing_lab_independiente + q.ing_otras_ocup)
        adic = adic + (v.factor_rentas - 1) * q.rentas
        if v.renta_activos_ext and v.base_activos_ext == "cartera":
            cima = 99 if 99 in q.index else 10
            partes_c = np.array([1.0 if d == cima else 0.0 for d in q.index])
            adic = adic + v.renta_activos_ext * rec["pii_cartera_musd"] * rec["tc"] * esc_pais * partes_c
        elif v.renta_activos_ext:
            partes = np.array([rec[f"parte_d{d}"] for d in q.index])
            activos = (rec["pii_cartera_musd"] + rec["pii_mondep_musd"]) * rec["tc"]   # millones de pesos
            adic = adic + v.renta_activos_ext * activos * esc_pais * partes
    den = q.ipcf if v.sobre_ipcf else base + adic
    if v.ajuste_cn:
        # Nivel neutro: la carga total sobre el ingreso total queda como en la medida
        # principal (el nivel con ingresos completos no se puede medir: faltan las rentas de
        # los hogares en Cuentas Nacionales). El ajuste sólo cambia el reparto entre deciles.
        t[IMPUESTOS] = t[IMPUESTOS] * den.sum() / den_sin_ajuste

    tasas = t[IMPUESTOS].div(den, axis=0)
    tot = t[IMPUESTOS].sum() / den.sum()
    tasas.loc[0] = tot
    tasas["total"] = tasas[IMPUESTOS].sum(axis=1)
    tasas["directos"] = tasas[DIRECTOS].sum(axis=1)
    tasas["indirectos"] = tasas[INDIRECTOS].sum(axis=1)
    tasas["ingreso_rel"] = np.append(rel, 1.0)
    tasas["gasto_sobre_ingreso_declarado"] = np.append((consumo / q.ipcf).values, consumo.sum() / q.ipcf.sum())
    tasas["ajuste_recursos"] = np.append((base / q.ipcf - 1).values, base.sum() / q.ipcf.sum() - 1)
    # totales mensuales del grupo (pesos corrientes, población EPH): para participaciones
    tasas["ingreso_total"] = np.append(den.values, den.sum())
    tasas["personas"] = np.append(q.personas.values, q.personas.sum())
    if "adulto_eq" in q:
        tasas["adulto_eq"] = np.append(q.adulto_eq.values, q.adulto_eq.sum())
    return tasas


def promedio_anual(q_anio: pd.DataFrame, anio: int, engho, rec_anio, v: Variante) -> pd.DataFrame:
    """Promedio simple de los trimestres disponibles (indicador calculado por trimestre)."""
    trims = [incidencia_trimestre(qt, anio, engho, rec_anio, v) for _, qt in q_anio.groupby("trim")]
    prom = (sum(trims) / len(trims)).reset_index().rename(columns={"index": "decil"})
    prom["trimestres"] = len(trims)
    return prom
