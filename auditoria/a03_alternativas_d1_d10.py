"""Auditoría 03: (A) alternativas para los recursos del decil 1 (y simétricas para todos los deciles);
(B) coherencia numerador/denominador de la corrección del decil 10.
Sólo lee. Uso: .venv/bin/python auditoria/a03_alternativas_d1_d10.py [anio]"""
import sys
from pathlib import Path
import numpy as np, pandas as pd
R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R / "src"))
from incidencia.incidencia import Variante, incidencia_trimestre, DIRECTOS, INDIRECTOS
from incidencia.indirectos import cargar_insumos
from incidencia.util import deciles_ponderados
pd.set_option("display.width", 250)
ANIO = int(sys.argv[1]) if len(sys.argv) > 1 else 2024
engho, rec = cargar_insumos()
q = pd.read_csv(R / "data/processed/eph_trimestral_decil.csv"); q = q[q.anio == ANIO]

# --- ENGHo 2017/18: factores recursos/ingreso por decil según tratamiento
h = pd.read_csv(R / "data/raw/engho/2017/engho2018_hogares/engho2018_hogares.txt", sep="|", low_memory=False)
h = h[(h.pondera > 0) & (h.ingtoth >= 0)].copy()
h["wp"] = h.pondera * h.cantmiem
h["d"] = deciles_ponderados((h.ingtoth / h.cantmiem).values, h.wp.values, h.id.values)
g = h.assign(Y=h.ingtoth * h.pondera, C=h.gastot * h.pondera, MX=np.maximum(h.ingtoth, h.gastot) * h.pondera,
             sin2=np.where(h.gastot > 2 * h.ingtoth, 0, 1)).groupby("d")
E_ = g[["Y", "C", "MX"]].sum()
m_hog = (E_.MX / E_.Y)                      # max(Y,C) hogar por hogar, todos los deciles
m_perm = (1 + E_.C / E_.Y) / 2              # promedio de ingreso y gasto

V0 = Variante("x", corregir_recursos=False)                      # ingreso declarado + altos (cobertura)
res = {}
for trim, qt in q.groupby("trim"):
    t = incidencia_trimestre(qt, ANIO, engho, rec.loc[ANIO], V0)
    qq = qt.set_index("decil").sort_index()
    Y, adic = qq.ipcf, qq.ing_pre_adic
    gy = t.gasto_sobre_ingreso_declarado.drop(0)
    tot, dire, ind = t.total.drop(0), t.directos.drop(0), t.indirectos.drop(0)
    den0 = Y + adic
    def con_base(m):                       # m: recursos / ingreso declarado, por decil
        den = Y * m + adic
        r = tot * den0 / den
        r.loc[0] = (tot * den0).sum() / den.sum()
        return r
    alt = {
        "A ingreso declarado": con_base(pd.Series(1.0, index=Y.index)),
        "B proyecto: max(Y,C) por decil": con_base(np.maximum(1.0, gy)),
        "C max(Y,C) por hogar, todos los deciles": con_base(m_hog),
        "D max(Y,C) por hogar, sólo D1-D2": con_base(pd.Series(np.where(Y.index <= 2, m_hog, 1.0), index=Y.index)),
        "E (Y+C)/2, sólo si C>Y (decil)": con_base(np.maximum(1.0, (1 + gy) / 2)),
        "F (Y+C)/2, todos los deciles": con_base((1 + gy) / 2),
        "G D1 con el C/Y del 2do veintil (1,153)": con_base(pd.Series(1.0, index=Y.index)) * 1.0,
    }
    # G: recalcula sólo los indirectos del D1 como si su C/Y fuera el del segundo veintil ENGHo
    gG = alt["G D1 con el C/Y del 2do veintil (1,153)"].copy()
    gG.loc[1] = dire[1] + ind[1] * 1.153 / gy[1]
    alt["G D1 con el C/Y del 2do veintil (1,153)"] = gG
    # H: CEQ/BID simétrico: indirectos = (impuesto/consumo) x ingreso, para todos
    hH = dire + ind / gy
    hH.loc[0] = np.nan
    alt["H CEQ simétrico: indirectos como % del consumo, todos"] = hH
    # I: todo sobre consumo (bienestar = consumo), ordenamiento por ingreso
    alt["I impuestos / (consumo + adic), todos"] = con_base(gy)
    for k, v in alt.items():
        res.setdefault(k, []).append(v)
out = pd.DataFrame({k: sum(v) / len(v) for k, v in res.items()}).T * 100
print(f"=== (A) {ANIO}: tasa total % según cómo se midan los recursos (con corrección de altos 'cobertura') ===")
print(out[[1, 2, 3, 5, 8, 9, 10, 0]].round(1).to_string())
print("\nfactores recursos/ingreso ENGHo 17/18  max por hogar:", m_hog.round(3).tolist())

# ---------------------------------------------------------------- (B) decil 10
a = pd.read_csv(R / "data/processed/ajuste_altos_ingresos.csv", index_col=0).loc[ANIO]
dd = pd.read_csv(R / "data/processed/ddjj_ganancias_tramos.csv")
dd = dd[(dd.anio_fiscal == a.anio_fiscal_ddjj) & ~dd.es_total]
tasa_ddjj = dd.impuesto.sum() / dd.resultado_neto.sum()
top = dd.sort_values("desde", ascending=False)
qa = q.groupby("decil").mean(numeric_only=True)
f = rec.poblacion[ANIO] / qa.personas.sum()
M = 12 * f / 1e6                                             # pesos mensuales EPH -> millones anuales país
piso = None
tr = [incidencia_trimestre(qt, ANIO, engho, rec.loc[ANIO], Variante("x", altos_ingresos="no", incluir_bp=False)) for _, qt in q.groupby("trim")]
r0 = (sum(tr) / len(tr)).total[10]
Y10 = (qa.ipcf[10] + qa.ing_pre_adic[10]) * M                # ingreso antes de impuestos del D10 (EPH expandida)
T0 = r0 * Y10
G, BP, p10 = a.ganancias_faltante_mill, a.bienes_personales_mill, a.parte_d10
s = None
print(f"\n=== (B) {ANIO}: decil 10, millones de pesos anuales, EPH expandida al país (factor {f:.2f}) ===")
print(f"ingreso D10 antes de imp. (encuesta) Y0 = {Y10:,.0f}   impuestos simulados+indirectos T0 = {T0:,.0f}   tasa base r0 = {r0:.1%}")
print(f"Ganancias faltante G = {G:,.0f} ({G / Y10:.1%} de Y0)   Bienes Personales = {BP:,.0f} ({BP / Y10:.1%})   parte D10 = {p10:.3f}")
print(f"ingreso faltante según DDJJ (cota inf.) = {a.ingreso_faltante_mill:,.0f} ({a.ingreso_faltante_mill / Y10:.1%} de Y0);  G / ingreso faltante = {G / a.ingreso_faltante_mill:.0%}")
print(f"tasa efectiva DDJJ {int(a.anio_fiscal_ddjj)}: impuesto determinado / resultado neto = {tasa_ddjj:.1%}")
cs = (qa.ipcf.sum() * 0 + 1)
esc_cob = None
cob = pd.read_csv(R / "outputs/tables/validacion_cobertura.csv", index_col=0).loc[ANIO, "consumo_encuesta_expandido_sobre_cn"]
print(f"factor 'cobertura' (consumo encuesta expandido / consumo CN) = {cob:.3f}")
def tasa(dT, dY):
    return (T0 + dT) / (Y10 + dY)
filas = [("piso: sólo simulado, sin BP", 0, 0),
         ("piso publicado: + BP x cobertura", BP * cob * 1.0, 0),
         ("principal: (G+BP) x cobertura x parte, sin ingreso", (G + BP) * cob * p10, 0),
         ("numerador completo, sin ingreso (incoherente)", (G + BP) * p10, 0),
         ("techo publicado: completo + ingreso faltante DDJJ", (G + BP) * p10, a.ingreso_faltante_mill * p10)]
for tau in (0.35, 0.25, tasa_ddjj, 0.15, 0.10):
    filas.append((f"coherente: completo + ingreso = G/{tau:.0%}", (G + BP) * p10, G * p10 / tau))
for n, dT, dY in filas:
    print(f"  {n:55s} dT={dT:12,.0f} dY={dY:12,.0f} ({dY / Y10:5.1%} de Y0)  tasa D10 = {tasa(dT, dY):.1%}")
# ingreso faltante implícito en la principal
rp = tasa((G + BP) * cob * p10, 0)
dY_impl = (T0 + (G + BP) * p10) / rp - Y10
print(f"la principal ({rp:.1%}) equivale a sumar todo G+BP y un ingreso faltante de {dY_impl:,.0f} = {dY_impl / Y10:.0%} de Y0 "
      f"(tasa media implícita sobre ese ingreso: {(G + BP) * p10 / dY_impl:.0%})")
# con indirectos sobre el ingreso faltante (si se consume como el D10)
ti10 = (sum(tr) / len(tr)).indirectos[10]
for tau in (0.35, tasa_ddjj, 0.15):
    dY = G * p10 / tau
    print(f"  coherente + indirectos sobre el ingreso faltante (tasa D10 {ti10:.1%}), tau={tau:.0%}: {tasa((G + BP) * p10 + ti10 * dY, dY):.1%}")
print(f"umbral: sumar (dT, dY) sube la tasa sólo si dT/dY > {r0:.1%}")
