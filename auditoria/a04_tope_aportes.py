"""Auditoría 04: tope de la base imponible de aportes (params/lmi.csv).
(a) relación tope / RIPTE por año; (b) por trimestre elegido: % de registrados sobre el tope por decil,
alícuota efectiva de aportes con y sin tope, efecto en la tasa total del decil 10.
Sólo lee. Uso: .venv/bin/python auditoria/a04_tope_aportes.py"""
import sys
from pathlib import Path
import numpy as np, pandas as pd
R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R / "src"))
from incidencia.directos import Parametros, simular, resumir_por_decil
from incidencia.eph import cargar_trimestre
from incidencia.incidencia import Variante, incidencia_trimestre
from incidencia.indirectos import cargar_insumos
pd.set_option("display.width", 250)
P = Parametros(); engho, rec = cargar_insumos()

print("(a) tope jubilatorio / RIPTE (promedio anual) y meses con cambio de tope por año")
lmi = pd.read_csv(R / "params/lmi.csv").set_index("mes")
x = pd.DataFrame({"tope": lmi.tope_jubilacion, "ripte": P.ripte.reindex(lmi.index)})
x["anio"] = x.index.str[:4]
print((x.groupby("anio").apply(lambda d: pd.Series({"tope_medio": d.tope.mean(), "tope/ripte": (d.tope / d.ripte).mean(),
      "cambios": (d.tope.diff().fillna(0) != 0).sum()}), include_groups=False)).round(2).T.to_string())

for anio, trim in [(2006, 2), (2008, 4), (2012, 2), (2019, 2), (2024, 3)]:
    df = cargar_trimestre(anio, trim)
    s = simular(df, P, anio, trim)
    m = P.mes(anio, {1: 2, 2: 5, 3: 8, 4: 11}[trim])
    tope = P.lmi_jub[m]
    reg = s[s.registrado]
    g = reg.groupby("decil")
    t = pd.DataFrame({
        "registrados_miles": g.w.sum() / 1e3,
        "%sobre tope": g.apply(lambda d: d.w[d.bruto > tope].sum() / d.w.sum(), include_groups=False) * 100,
        "aportes/bruto %": g.apply(lambda d: ((d.ap_jub + d.ap_inssjp) * d.w).sum() / (d.bruto * d.w).sum(), include_groups=False) * 100,
    })
    # sin tope: mismas alícuotas legales sobre todo el bruto
    tasa_leg = g.apply(lambda d: ((d.ap_jub + d.ap_inssjp) * d.w).sum() / (np.minimum(d.bruto, tope) * d.w).sum(), include_groups=False)
    t["sin tope %"] = tasa_leg * 100
    q = resumir_por_decil(s); q["anio"], q["trim"] = anio, trim
    base = incidencia_trimestre(q, anio, engho, rec.loc[anio], Variante("x", altos_ingresos="no", incluir_bp=False))
    # contrafáctico sin tope (aproximado: el bruto no se recalcula)
    s2 = s.copy()
    extra_j = np.where(s.registrado, s.ap_jub / np.minimum(s.bruto, tope).replace(0, np.nan) * (s.bruto - np.minimum(s.bruto, tope)), 0)
    extra_i = np.where(s.registrado, 0.03 * (s.bruto - np.minimum(s.bruto, P.lmi_otros[m])), 0)
    s2["ap_jub"] = s.ap_jub + np.nan_to_num(extra_j); s2["ap_inssjp"] = s.ap_inssjp + np.nan_to_num(extra_i)
    s2["ing_pre"] = s.ing_pre + np.nan_to_num(extra_j) + np.nan_to_num(extra_i) * 2
    q2 = resumir_por_decil(s2)
    alt = incidencia_trimestre(q2, anio, engho, rec.loc[anio], Variante("x", altos_ingresos="no", incluir_bp=False))
    t["aportes % ingreso decil"] = base.aportes.drop(0) * 100
    t["idem sin tope"] = alt.aportes.drop(0) * 100
    print(f"\n(b) {anio}T{trim}  tope del mes central {m}: {tope:,.2f}  (RIPTE {P.ripte[m]:,.0f})")
    print(t.round(2).T.to_string())
    print(f"   tasa total D10 (sin altos ni BP): con tope {base.total[10]:.2%}  sin tope {alt.total[10]:.2%}  -> efecto del tope {(base.total[10] - alt.total[10]) * 100:+.2f} pp;"
          f"  D9: {(base.total[9] - alt.total[9]) * 100:+.2f} pp")
    # control directo del tope: ningún aporte jubilatorio supera alícuota x tope
    mx_ok = (reg.ap_jub <= 0.11 * max(P.lmi_jub[P.mes(anio, mm)] for mm in {1: (1, 2, 3), 2: (4, 5, 6), 3: (7, 8, 9), 4: (10, 11, 12)}[trim]) + 1e-6).all()
    print("   control: ap_jub <= 11% x tope máximo del trimestre para todos:", bool(mx_ok))
