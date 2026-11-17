"""Microsimulación de impuestos directos sobre la EPH.

Impuestos simulados persona por persona:
  - aportes personales (jubilación + INSSJP; obra social se calcula pero no es impuesto),
  - contribuciones patronales (Dto. 814/2001) de asalariados registrados privados,
  - Impuesto a las Ganancias de 4ta categoría (asalariados registrados y jubilados).

Reglas generales:
  * Población alcanzada: asalariados (CAT_OCUP = 3) ocupados con descuento jubilatorio
    (PP07H = 1), excluido el servicio doméstico (régimen especial, no modelado).
    Informales, cuentapropistas y patrones: tasa cero (decisión del proyecto; la EPH no
    informa su situación registral).
  * La EPH releva el ingreso "de bolsillo" (neto de aportes y de retención de Ganancias).
    El bruto se obtiene invirtiendo numéricamente:  neto = bruto - aportes - ganancias.
  * Todo se calcula con los parámetros vigentes en cada MES del trimestre y se promedia.
  * Ganancias es anual: el ingreso del mes se anualiza con la trayectoria del RIPTE del
    año (13 pagos, incluye SAC) y el impuesto anual se reexpresa por mes.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import yaml

from .config import PARAMS, RAW
from .util import escala_progresiva, leer_serie_mensual

MESES_TRIM = {1: (1, 2, 3), 2: (4, 5, 6), 3: (7, 8, 9), 4: (10, 11, 12)}
SAC = 13.0 / 12.0   # salario o haber mensual + 1/12 de aguinaldo


class Parametros:
    def __init__(self):
        self.gan = yaml.safe_load(open(PARAMS / "ganancias.yaml", encoding="utf-8"))
        self.ss = yaml.safe_load(open(PARAMS / "seguridad_social.yaml", encoding="utf-8"))
        lmi = pd.read_csv(PARAMS / "lmi.csv").set_index("mes")
        self.lmi_jub = lmi.tope_jubilacion
        self.lmi_otros = lmi.tope_otros_subsistemas
        self.ripte = leer_serie_mensual(RAW / "macro" / "ripte_mensual.csv")
        self.haber_min = leer_serie_mensual(RAW / "macro" / "haber_minimo_mensual.csv")
        self.smvm = leer_serie_mensual(RAW / "macro" / "smvm_mensual.csv")
        # Referencia Dto. 1242/2013: mayor RIPTE de enero-agosto 2013
        self.mono = yaml.safe_load(open(PARAMS / "monotributo.yaml", encoding="utf-8"))
        self.ripte_ref_2013 = max(self.ripte[f"2013-{m:02d}"] for m in range(1, 9))

    @staticmethod
    def mes(anio: int, m: int) -> str:
        return f"{anio}-{m:02d}"

    def k_anual(self, anio: int, m: int) -> float:
        """Meses-equivalentes del año a valores del mes m (incluye SAC)."""
        tot = sum(self.ripte[self.mes(anio, i)] for i in range(1, 13))
        return tot / self.ripte[self.mes(anio, m)] * 13.0 / 12.0

    def haber_min_anual(self, anio: int) -> float:
        return float(sum(self.haber_min[self.mes(anio, i)] for i in range(1, 13)))

    def contribuciones(self, anio: int, m: int) -> dict:
        mes = self.mes(anio, m)
        for p in self.ss["contribuciones_patronales"]["periodos"]:
            if p["desde"] <= mes <= p["hasta"]:
                return p
        raise KeyError(mes)


# ------------------------------------------------------------------ aportes personales
def aportes_mes(P: Parametros, anio: int, m: int, bruto: np.ndarray, privado: np.ndarray):
    """Aportes mensuales: (jubilación, INSSJP, obra social)."""
    mes = P.mes(anio, m)
    ap = P.ss["aportes_personales"]
    tj = np.full(bruto.shape, ap["jubilacion"]["tasa_general"])
    if mes <= ap["jubilacion"]["capitalizacion_hasta"]:
        tj = np.where(privado, ap["jubilacion"]["tasa_capitalizacion"], tj)
    base_j = np.minimum(bruto, P.lmi_jub[mes])
    base_o = np.minimum(bruto, P.lmi_otros[mes])
    return tj * base_j, ap["inssjp"]["tasa"] * base_o, ap["obra_social"]["tasa"] * base_o


# ---------------------------------------------------------------------------- Ganancias
def _reduccion(tabla, neta: np.ndarray) -> np.ndarray:
    pct = np.zeros_like(neta)
    piso = -np.inf
    for tope, p in tabla:
        pct = np.where((neta > piso) & (neta <= tope), p, pct)
        piso = tope
    return pct


def ganancias_mes(P: Parametros, anio: int, m: int, salario: np.ndarray, jubilacion: np.ndarray,
                  aportes: np.ndarray, conyuge: np.ndarray, hijos: np.ndarray) -> np.ndarray:
    """Impuesto a las Ganancias devengado en el mes (pesos del mes)."""
    G = P.gan
    mes = P.mes(anio, m)
    bruto = salario + jubilacion
    neto_mes = bruto - aportes

    # --- régimen cedular (10/2023 - 06/2024)
    ced = G["cedular"]
    if ced["desde"] <= mes <= ced["hasta"]:
        esc = G["escalas"]["cedular_oct2023_mensual"]
        f = 1.0 if anio == 2023 else float(P.smvm[mes]) / ced["smvm_base"]
        return escala_progresiva(neto_mes, [x * f for x in esc["limites"]], esc["alicuotas"])

    d = G["deducciones"][str(anio)]
    esc = G["escalas"][str(d["escala"])]
    k = P.k_anual(anio, m)
    neta = neto_mes * k

    n = bruto.shape
    gni = np.full(n, float(d["gni"]))
    cony = np.full(n, float(d["conyuge"]))
    hijo = np.full(n, float(d["hijo"]))
    de = np.full(n, float(d["de_dep"]))
    exento = np.zeros(n, dtype=bool)

    # --- Decreto 1242/2013
    dto = G["dto_1242"]
    if dto["desde"] <= mes <= dto["hasta"]:
        w13 = bruto * P.ripte_ref_2013 / P.ripte[mes]   # remuneración llevada a ene-ago 2013
        exento |= w13 <= dto["umbral_exento"]
        piso = dto["umbral_exento"]
        for t in (dto["tramos_2015"] if anio == 2015 else dto["tramos_2013_2014"]):
            msk = (w13 > piso) & (w13 <= t["hasta"])
            gni[msk], cony[msk], hijo[msk], de[msk] = t["gni"], t["conyuge"], t["hijo"], t["de_dep"]
            piso = t["hasta"]

    cargas = cony * conyuge + hijo * hijos
    ded_base = gni + de
    veces = G["jubilados_veces_haber_minimo"].get(str(anio))
    if veces:
        puro = (jubilacion > 0) & (salario <= 0)
        ded_base = np.where(puro, np.maximum(ded_base, veces * P.haber_min_anual(anio)), ded_base)
    ded = ded_base + cargas
    red = G["reduccion_deducciones"].get(str(anio))
    if red:
        ded = ded * (1.0 - _reduccion(red, neta))

    imp = escala_progresiva(neta - ded, esc["limites"], esc["alicuotas"]) / k
    imp[exento] = 0.0

    # --- Ley 27.617: mínimo por remuneración bruta mensual, con tramo de transición
    for u in G["umbrales_ley_27617"]:
        if u["desde"] <= mes <= u["hasta"]:
            ex, tr = u["exento"], u["transicion"]
            frac = np.clip((bruto - ex) / (tr - ex), 0.0, 1.0)
            imp = imp * frac
    return imp


# ------------------------------------------------------------------------ monotributo
def monotributo_mes(P: Parametros, anio: int, m: int, facturacion_anual: np.ndarray, bienes: np.ndarray):
    """Cuota mensual del monotributo (impuesto integrado, aporte jubilatorio) de la categoría que
    corresponde a la facturación anual. La obra social no se cuenta como impuesto. Quien supera la
    última categoría admitida para su actividad queda fuera del régimen (0: régimen general, no
    simulado)."""
    mes = P.mes(anio, m)
    per = next(p for p in P.mono["periodos"] if p["desde"] <= mes <= p["hasta"])
    imp = np.zeros_like(facturacion_anual)
    sipa = np.zeros_like(facturacion_anual)
    hecho = np.zeros(facturacion_anual.shape, dtype=bool)
    for c in per["categorias"]:
        if "actividad" in c:                       # 2004-2009: escalas separadas por actividad
            permitido = bienes if c["actividad"] == "bienes" else ~bienes
            monto = c["impuesto"]
        else:                                      # 2010 en adelante: una escala, dos columnas
            mb, ms = c["impuesto_bienes"], c["impuesto_servicios"]
            permitido = np.where(bienes, mb is not None, ms is not None)
            monto = np.where(bienes, mb or 0.0, ms or 0.0)
        cae = permitido & ~hecho & (facturacion_anual <= c["tope_anual"])
        imp = np.where(cae, monto, imp)
        sipa = np.where(cae, c["sipa"], sipa)
        hecho |= cae
    return imp, sipa


# ----------------------------------------------------------------- cargas de familia
def cargas_familia(df: pd.DataFrame, P: Parametros, anio: int) -> tuple[np.ndarray, np.ndarray]:
    """Indicador de cónyuge a cargo y cantidad de hijos a cargo por persona.

    Las cargas se asignan al jefe o cónyuge de mayor ingreso. Cónyuge e hijos cuentan
    si su ingreso anualizado no supera la ganancia no imponible. (Aproximación con la
    información de parentesco de la EPH; hijos = CH03 == 3 dentro del límite de edad.)
    """
    d = P.gan["deducciones"][str(anio)]
    tope = d["gni"] / 13.0
    ing = (df.P21 + df.V2_M).values
    jefe, cony, hijo = (df.CH03 == 1).values, (df.CH03 == 2).values, (df.CH03 == 3).values
    g = df.groupby("hid", sort=False)
    t = pd.DataFrame({
        "hid": df.hid.values,
        "ing_j": ing * jefe, "ing_c": ing * cony, "hay_c": cony.astype(float),
        "nh": (hijo & (df.CH06.values < d["hijo_edad_max"]) & (ing <= tope)).astype(float),
    }).groupby("hid", sort=False).transform("sum")
    del g
    jefe_principal = t.ing_j.values >= t.ing_c.values
    principal = (jefe & jefe_principal) | (cony & ~jefe_principal)
    ing_pareja = np.where(jefe, t.ing_c.values, t.ing_j.values)
    conyuge = principal & (t.hay_c.values > 0) & (ing_pareja <= tope)
    hijos = np.where(principal, t.nh.values, 0.0)
    return conyuge.astype(float), hijos


# ------------------------------------------------------------------------- simulación
def simular(df: pd.DataFrame, P: Parametros, anio: int, trim: int, iteraciones: int = 60) -> pd.DataFrame:
    """Agrega a `df` (personas de un trimestre) los impuestos directos mensuales."""
    registrado = ((df.ESTADO == 1) & (df.CAT_OCUP == 3) & (df.PP07H == 1) & (df.P21 > 0)
                  & ~(df.PP04B1 == 1)).values
    privado = registrado & (df.PP04A != 1).values
    grande = (df.PP04C.isin([9, 10, 11, 12]) | ((df.PP04C == 99) & (df.PP04C99 == 3))).values
    neto = np.where(registrado, df.P21.values, 0.0)
    jub = df.V2_M.values.astype(float)
    conyuge, hijos = cargas_familia(df, P, anio)
    frac_trab = P.ss["contribuciones_patronales"]["fraccion_trabajador"]

    activos = (neto > 0) | (jub > 0)
    idx = np.where(activos)[0]
    acc = {k: np.zeros(len(df)) for k in ("bruto", "ap_jub", "ap_jub_afjp", "ap_inssjp", "ap_os", "ganancias",
                                          "contrib")}
    cap_hasta = P.ss["aportes_personales"]["jubilacion"]["afjp_existen_hasta"]

    for m in MESES_TRIM[trim]:
        n_, j_, pr_, c_, h_ = neto[idx], jub[idx], privado[idx], conyuge[idx], hijos[idx]
        ap0 = P.ss["aportes_personales"]
        bruto = n_ / (1 - 0.11 - ap0["inssjp"]["tasa"] - ap0["obra_social"]["tasa"])
        bruto = np.where(n_ > 0, bruto, 0.0)
        for _ in range(iteraciones):
            aj, ai, ao = aportes_mes(P, anio, m, bruto, pr_)
            gan = ganancias_mes(P, anio, m, bruto, j_, aj + ai + ao, c_, h_)
            # la retención se reparte entre salario y jubilación en proporción al ingreso
            part = np.divide(bruto, bruto + j_, out=np.zeros_like(bruto), where=(bruto + j_) > 0)
            nuevo = np.where(n_ > 0, n_ + aj + ai + ao + gan * part, 0.0)
            bruto = 0.5 * bruto + 0.5 * nuevo
        aj, ai, ao = aportes_mes(P, anio, m, bruto, pr_)
        gan = ganancias_mes(P, anio, m, bruto, j_, aj + ai + ao, c_, h_)
        cp = P.contribuciones(anio, m)
        tasa = np.where(grande[idx], cp["inc_a"], cp["inc_b"])
        contrib = np.where(pr_, tasa * np.maximum(bruto - cp["detraccion"], 0.0), 0.0)
        # aportes jubilatorios que iban a una AFJP (no eran recaudación del Estado)
        afjp = np.where(pr_, aj, 0.0) if P.mes(anio, m) <= cap_hasta else np.zeros_like(aj)
        # Base devengada: el ingreso incluye 1/12 de aguinaldo por mes (eph._aguinaldo_devengado),
        # así que los impuestos del mes se llevan a 13/12 (el SAC paga aportes y contribuciones,
        # y Ganancias ya se calcula sobre 13 pagos y se reexpresa por pago).
        for k, v in (("bruto", bruto), ("ap_jub", aj), ("ap_jub_afjp", afjp), ("ap_inssjp", ai), ("ap_os", ao),
                     ("ganancias", gan), ("contrib", contrib)):
            acc[k][idx] += v * SAC / 3.0

    # Monotributo de los independientes (cuentapropistas y patrones). Quién paga: desde 2023T4 la
    # EPH lo pregunta (PP05I = 1); antes, la proporción de cada decil en 2023T4-2025T4 (valor
    # esperado). Se calcula sin calibrar; la variante con_monotributo lo lleva a lo recaudado.
    indep = ((df.ESTADO == 1) & df.CAT_OCUP.isin([1, 2]) & (df.P21 > 0)).values
    margen = P.mono["margen_ganancia"]
    fact = np.where(indep, df.P21.values * 12.0 / margen, 0.0)
    bienes = df.vende_bienes.values.astype(bool) if "vende_bienes" in df else np.zeros(len(df), dtype=bool)
    if "PP05I" in df and df.PP05I[indep].notna().any():
        paga = (df.PP05I.values == 1).astype(float)
    else:
        perfil = P.mono["inscripcion_por_decil"]["decil"]
        paga = df.decil.map(perfil).fillna(0.0).values if "decil" in df else np.zeros(len(df))
    paga = paga * indep
    mono_imp, mono_sipa = np.zeros(len(df)), np.zeros(len(df))
    for m in MESES_TRIM[trim]:
        i_, s_ = monotributo_mes(P, anio, m, fact, bienes)
        mono_imp += paga * i_ / 3.0
        mono_sipa += paga * s_ / 3.0

    out = df.copy()
    for k, v in acc.items():
        out[k] = v
    out["mono_imp"] = mono_imp
    out["mono_sipa"] = mono_sipa
    out["registrado"] = registrado
    out["privado_reg"] = privado
    out["contrib_trab"] = out.contrib * frac_trab
    # Ingreso antes de impuestos directos: ingreso de bolsillo + aportes + obra social +
    # Ganancias + parte de las contribuciones patronales que recae sobre el trabajador.
    out["directos"] = out.ap_jub + out.ap_inssjp + out.ganancias + out.contrib_trab
    out["ing_pre"] = out.ap_jub + out.ap_inssjp + out.ap_os + out.ganancias + out.contrib_trab
    return out


def resumir_por_decil(s: pd.DataFrame, clave: str = "decil") -> pd.DataFrame:
    """Totales expandidos mensuales por decil (impuestos, ingresos y composición).

    clave="grupo": deciles 1-9 y el decil 10 partido en 91 (P90-95), 95 (P95-99) y 99 (P99-100);
    la columna de salida se sigue llamando "decil"."""
    w = s.w
    ocup = (s.ESTADO == 1)
    asal = ocup & (s.CAT_OCUP == 3)
    indep = ocup & s.CAT_OCUP.isin([1, 2])
    t = pd.DataFrame({
        "decil": s[clave],
        "personas": w,
        "adulto_eq": w * s.ae,          # adultos equivalentes (tabla del INDEC), para medir en canastas
        "hogares": w * (s.CH03 == 1),
        "ipcf": w * s.IPCF,
        "ing_pre_adic": w * s.ing_pre,
        "ap_jub": w * s.ap_jub,
        "ap_jub_afjp": w * s.ap_jub_afjp,
        "ap_inssjp": w * s.ap_inssjp,
        "ap_os": w * s.ap_os,
        "ganancias": w * s.ganancias,
        "contrib": w * s.contrib,
        "mono_imp": w * s.mono_imp,
        "mono_sipa": w * s.mono_sipa,
        "masa_bruta_reg": w * s.bruto,
        "masa_bruta_reg_priv": w * s.bruto * s.privado_reg,
        "jubilaciones": w * s.V2_M,
        "ing_lab_registrado": w * s.P21 * s.registrado,
        "ing_lab_asal_no_reg": w * s.P21 * (asal & ~s.registrado),
        "ing_lab_independiente": w * s.P21 * indep,
        "ing_otras_ocup": w * s.TOT_P12,
        "rentas": w * (s.V8_M + s.V9_M + s.V10_M),
        "masa_bruta_reg_pub": w * s.bruto * (s.registrado & ~s.privado_reg),
        "n_registrados": w * s.registrado,
        "n_registrados_priv": w * s.privado_reg,
        "n_asal_no_registrados": w * (asal & ~s.registrado),
        "n_cuenta_propia": w * (ocup & (s.CAT_OCUP == 2)),
        "n_patrones": w * (ocup & (s.CAT_OCUP == 1)),
        "n_jubilados": w * (s.V2_M > 0),
        "n_ganancias": w * (s.ganancias > 0),
        "n_ocupados": w * ocup,
        "n_asalariados": w * asal,
    })
    return t.groupby("decil").sum().reset_index()
