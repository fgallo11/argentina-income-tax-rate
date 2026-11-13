"""Auditoría 02: ¿de dónde sale el gasto > ingreso del decil 1? Microdatos ENGHo 2017/18 (hogares).
Compara tratamientos del cociente gasto/ingreso por decil de ingreso per cápita.
Sólo lee data/raw. Uso: .venv/bin/python auditoria/a02_engho_decil1.py"""
import sys
from pathlib import Path
import numpy as np, pandas as pd
R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R / "src"))
from incidencia.util import deciles_ponderados
pd.set_option("display.width", 250)

h = pd.read_csv(R / "data/raw/engho/2017/engho2018_hogares/engho2018_hogares.txt", sep="|", low_memory=False)
for c in ["pondera", "cantmiem", "gastot", "ingtoth", "fp_especie", "fp_prodprop", "gasto_imputado", "ingtoth_imp", "gc_04"]:
    h[c] = pd.to_numeric(h[c].astype(str).str.replace(",", "."), errors="coerce")
print("hogares:", len(h), " ingtoth nulo:", h.ingtoth.isna().sum(), " ingtoth==0:", (h.ingtoth == 0).sum(),
      " m_ingtoth:", h.m_ingtoth.value_counts(dropna=False).to_dict())
h = h[(h.pondera > 0) & h.ingtoth.notna() & (h.ingtoth >= 0) & h.gastot.notna()].copy()
h["wp"] = h.pondera * h.cantmiem
h["ipc"] = h.ingtoth / h.cantmiem
h["cpc"] = h.gastot / h.cantmiem
h["d"] = deciles_ponderados(h.ipc.values, h.wp.values, h.id.values)
h["dc"] = deciles_ponderados(h.cpc.values, h.wp.values, h.id.values)
h["v"] = deciles_ponderados(h.ipc.values, h.wp.values, h.id.values, n=20)
W = lambda x, c: (x[c] * x.pondera).sum()

def tabla(g):
    out = {}
    for k, x in g:
        Y, C = W(x, "ingtoth"), W(x, "gastot")
        x2 = x.assign(mx=np.maximum(x.ingtoth, x.gastot), perm=(x.ingtoth + x.gastot) / 2)
        out[k] = {
            "C/Y declarado": C / Y,
            "C/max(Y,C) decil (proyecto)": C / max(Y, C),
            "C/max(Y,C) hogar": C / W(x2, "mx"),
            "C/((Y+C)/2) hogar": C / W(x2, "perm"),
            "%pers. en hogares C>Y": x.wp[x.gastot > x.ingtoth].sum() / x.wp.sum(),
            "%pers. C>2Y": x.wp[x.gastot > 2 * x.ingtoth].sum() / x.wp.sum(),
            "%pers. Y=0": x.wp[x.ingtoth == 0].sum() / x.wp.sum(),
            "mediana C/Y hogar": np.nan,
            "%gasto en especie": W(x, "fp_especie") / C if x.fp_especie.max() > 1.5 else (x.fp_especie * x.gastot * x.pondera).sum() / C,
            "%gasto prod.propia": W(x, "fp_prodprop") / C if x.fp_prodprop.max() > 1.5 else (x.fp_prodprop * x.gastot * x.pondera).sum() / C,
            "ingreso imputado %hog": (x.pondera[x.m_ingtoth != 0].sum() / x.pondera.sum()) if "m_ingtoth" in x else np.nan,
        }
        r = (x.gastot / x.ingtoth.replace(0, np.nan)).dropna()
        o = np.argsort(r.values); cw = np.cumsum(x.loc[r.index, "wp"].values[o]); out[k]["mediana C/Y hogar"] = r.values[o][np.searchsorted(cw, cw[-1] / 2)]
    return pd.DataFrame(out).round(3)

print("\nPor decil de ingreso per cápita (ENGHo 2017/18):"); print(tabla(h.groupby("d")).to_string())
print("\nVeintiles 1-4:"); print(tabla(h[h.v <= 4].groupby("v")).to_string())
print("\nTotal:"); print(tabla([(0, h)]).to_string())

# sensibilidad: D1 excluyendo hogares con ingreso cero / cociente extremo
d1 = h[h.d == 1]
for nombre, m in [("todos", d1.ingtoth >= 0), ("sin Y=0", d1.ingtoth > 0), ("sin C>3Y", d1.gastot <= 3 * d1.ingtoth),
                  ("sin C>2Y", d1.gastot <= 2 * d1.ingtoth)]:
    x = d1[m]; print(f"D1 {nombre:10s} personas={x.wp.sum() / d1.wp.sum():.3f}  C/Y={W(x, 'gastot') / W(x, 'ingtoth'):.3f}")

# reordenamiento: dónde están (por consumo) las personas del decil 1 de ingreso
print("\nDecil de CONSUMO per cápita de las personas del decil 1 de INGRESO (%):")
print((d1.groupby("dc").wp.sum() / d1.wp.sum() * 100).round(1).to_string())
print("\nC/Y por decil de consumo per cápita:")
print(pd.Series({k: W(x, "gastot") / W(x, "ingtoth") for k, x in h.groupby("dc")}).round(3).to_string())
print("participación en el ingreso por decil de ingreso (%):", (pd.Series({k: W(x, 'ingtoth') for k, x in h.groupby('d')}) / W(h, 'ingtoth') * 100).round(2).tolist())
print("media ingreso pc mensual ENGHo 17/18:", round(W(h, "ingtoth") / h.wp.sum(), 1), " gasto pc:", round(W(h, "gastot") / h.wp.sum(), 1))
print("vivienda (gc_04) / gasto total:", round(W(h, "gc_04") / W(h, "gastot"), 3))
print(h[["fp_especie", "fp_prodprop", "gasto_imputado", "ingtoth_imp"]].describe().T.to_string())
