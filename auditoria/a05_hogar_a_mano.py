"""Auditoría 05: un hogar de la EPH de punta a punta (2019T2), con cálculo independiente.
1) lee el .txt crudo de INDEC sin usar incidencia.eph; 2) elige un hogar con asalariado registrado
privado que paga Ganancias, cónyuge e hijos; 3) recalcula bruto, aportes, Ganancias y contribuciones
con fórmulas escritas aparte (bisección, no la iteración del proyecto) y parámetros leídos de la
norma (constantes abajo); 4) recalcula deciles con otro algoritmo; 5) compara con simular() y con la
fila publicada de data/processed/eph_trimestral_decil.csv; 6) rehace a mano la tasa del decil.
Sólo lee. Uso: .venv/bin/python auditoria/a05_hogar_a_mano.py"""
import sys
from pathlib import Path
import numpy as np, pandas as pd
R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R / "src"))
pd.set_option("display.width", 250)
ANIO, TRIM = 2019, 2

# ---------- 1) lectura cruda
f = R / "data/raw/eph/2019T2/USU_individual_t219.txt"
raw = pd.read_csv(f, sep=";", decimal=",", low_memory=False, encoding="latin-1")
raw.columns = [c.upper() for c in raw.columns]
print("filas crudas:", len(raw), " suma PONDERA:", raw.PONDERA.sum(), " suma PONDIH:", raw.PONDIH.sum(),
      " PONDIH=0:", (raw.PONDIH == 0).sum(), f"({raw.PONDERA[raw.PONDIH == 0].sum() / raw.PONDERA.sum():.1%} de la población)")
d = raw[raw.PONDIH > 0].copy()
d["hid"] = d.CODUSU.astype(str).str.strip() + "_" + d.NRO_HOGAR.astype(str)
print("IPCF<0:", (d.IPCF < 0).sum(), " IPCF=0 (personas pond.):", f"{d.PONDIH[d.IPCF == 0].sum() / d.PONDIH.sum():.2%}",
      " P21<0 con PONDIH>0:", (d.P21 < 0).sum())

# ---------- 4) deciles con algoritmo independiente (orden por IPCF, corte por masa acumulada de personas)
hog = d.groupby("hid").agg(ipcf=("IPCF", "first"), wp=("PONDIH", "sum")).reset_index().sort_values(["ipcf", "hid"])
cum = hog.wp.cumsum() - hog.wp / 2
hog["decil_mio"] = np.minimum((cum / hog.wp.sum() * 10).astype(int) + 1, 10)
d = d.merge(hog[["hid", "decil_mio"]], on="hid")

# ---------- proyecto
from incidencia.directos import Parametros, simular, resumir_por_decil
from incidencia.eph import cargar_trimestre
P = Parametros()
s = simular(cargar_trimestre(ANIO, TRIM), P, ANIO, TRIM)
chk = s.merge(d[["CODUSU", "NRO_HOGAR", "COMPONENTE", "decil_mio"]].assign(CODUSU=d.CODUSU.astype(str).str.strip()),
              on=["CODUSU", "NRO_HOGAR", "COMPONENTE"])
print("personas proyecto:", len(s), " mías:", len(d), " decil distinto:", int((chk.decil != chk.decil_mio).sum()))
print("personas por decil (proyecto, % del total):", (s.groupby("decil").w.sum() / s.w.sum() * 100).round(2).tolist())

# ---------- 2) elegir hogar
c = s[(s.registrado) & (s.privado_reg) & (s.ganancias > 0) & (s.CH03 == 1)]
hh = s[s.hid.isin(c.hid)].groupby("hid").agg(n=("CH03", "size"), cony=("CH03", lambda x: (x == 2).sum()), hijos=("CH03", lambda x: (x == 3).sum()))
hh = hh[(hh.cony == 1) & (hh.hijos == 2) & (hh.n == 4)]
hid = sorted(hh.index)[0]
H = s[s.hid == hid]
print("\nHOGAR", hid)
print(H[["COMPONENTE", "CH03", "CH04", "CH06", "ESTADO", "CAT_OCUP", "PP04A", "PP04B1", "PP04C", "PP07H", "P21", "V2_M", "P47T", "ITF", "IPCF", "w", "decil"]].to_string(index=False))

# ---------- 3) cálculo independiente (parámetros 2019 transcriptos a mano)
TOPE = {4: 117684.13, 5: 117684.13, 6: 130323.36}          # lmi.csv (Res. ANSES; ver auditoría de parámetros)
GNI, DE, CONY, HIJO = 103018.79, 494490.17, 80033.97, 40361.43   # RG AFIP 2019 + Dto. 561/2019 (+20% GNI y DE)
LIM = [33039.81, 66079.61, 99119.42, 132159.23, 198238.84, 264318.45, 396477.68, 528636.91]
ALI = [.05, .09, .12, .15, .19, .23, .27, .31, .35]
ripte = pd.read_csv(R / "data/raw/macro/ripte_mensual.csv"); ripte = pd.Series(ripte.iloc[:, 1].values, index=ripte.iloc[:, 0].str[:7])
def escala(b):
    imp, piso = 0.0, 0.0
    for lim, a in zip(LIM + [float("inf")], ALI):
        if b > piso: imp += a * (min(b, lim) - piso)
        piso = lim
    return imp
def neto_de(bruto, m, cony, hijos):
    ap = 0.17 * min(bruto, TOPE[m])                              # 11% + 3% + 3%, mismo tope
    k = sum(ripte[f"2019-{i:02d}"] for i in range(1, 13)) / ripte[f"2019-{m:02d}"] * 13 / 12
    base = (bruto - ap) * k - (GNI + DE + CONY * cony + HIJO * hijos)
    gan = escala(max(base, 0)) / k
    return bruto - ap - gan, ap, gan
jefe = H[H.CH03 == 1].iloc[0]; cy = H[H.CH03 == 2].iloc[0]; hj = H[H.CH03 == 3]
ing = lambda r: r.P21 + r.V2_M
cony = int(ing(cy) <= GNI / 13 and ing(jefe) >= ing(cy))
hijos = int(((hj.CH06 < 18) & ((hj.P21 + hj.V2_M) <= GNI / 13)).sum())
print(f"cargas a mano: cónyuge a cargo={cony} hijos a cargo={hijos}")
res = []
for m in (4, 5, 6):
    lo, hi = jefe.P21, jefe.P21 * 3
    for _ in range(200):
        mid = (lo + hi) / 2
        if neto_de(mid, m, cony, hijos)[0] < jefe.P21: lo = mid
        else: hi = mid
    n, ap, gan = neto_de(mid, m, cony, hijos)
    grande = jefe.PP04C in (9, 10, 11, 12) or (jefe.PP04C == 99 and jefe.PP04C99 == 3)
    contrib = (0.204 if grande else 0.18) * max(mid - 7003.68, 0)
    res.append(dict(mes=m, bruto=mid, ap_jub=0.11 * min(mid, TOPE[m]), ap_inssjp=0.03 * min(mid, TOPE[m]), ap_os=0.03 * min(mid, TOPE[m]), ganancias=gan, contrib=contrib))
mio = pd.DataFrame(res).drop(columns="mes").mean()
cmp = pd.DataFrame({"a mano": mio, "proyecto": jefe[mio.index].astype(float)}); cmp["dif %"] = (cmp["proyecto"] / cmp["a mano"] - 1) * 100
print(cmp.round(3).to_string())
print(f"tasa directa del jefe sobre su bruto: aportes {(mio.ap_jub + mio.ap_inssjp) / mio.bruto:.2%}, Ganancias {mio.ganancias / mio.bruto:.2%}, contrib. {mio.contrib / mio.bruto:.2%}")

# ---------- 5) agregado del decil vs archivo publicado
q_pub = pd.read_csv(R / "data/processed/eph_trimestral_decil.csv"); q_pub = q_pub[(q_pub.anio == ANIO) & (q_pub.trim == TRIM)].set_index("decil")
dec = int(jefe.decil)
mia = {"personas": s.w[s.decil == dec].sum(), "ipcf": (s.w * s.IPCF)[s.decil == dec].sum(), "ganancias": (s.w * s.ganancias)[s.decil == dec].sum(),
       "ap_jub": (s.w * s.ap_jub)[s.decil == dec].sum(), "contrib": (s.w * s.contrib)[s.decil == dec].sum()}
print(f"\ndecil {dec}: recalculado vs publicado"); print(pd.DataFrame({"recalc": mia, "publicado": q_pub.loc[dec, list(mia)]}).assign(dif=lambda x: x.recalc / x.publicado - 1).to_string())
# control cruzado con lectura cruda: ipcf total del decil
print("ipcf del decil con lectura cruda independiente:", (d.PONDIH * d.IPCF)[d.decil_mio == dec].sum())

# ---------- 6) tasa del decil a mano (variante ingreso declarado, sin altos ni BP)
from incidencia.incidencia import Variante, incidencia_trimestre
from incidencia.indirectos import cargar_insumos
engho, rec = cargar_insumos(); r = rec.loc[ANIO]
qq = resumir_por_decil(s); qq["anio"], qq["trim"] = ANIO, TRIM
t = incidencia_trimestre(qq, ANIO, engho, r, Variante("x", corregir_recursos=False, altos_ingresos="no", incluir_bp=False))
Q = qq.set_index("decil")
media = Q.ipcf.sum() / Q.personas.sum(); rel = Q.ipcf / Q.personas / media
e = engho[engho.edicion.astype(str) == "2017"].sort_values("ingreso_rel")      # 2019 > ancla 2018: sólo ENGHo 2017/18
crel = np.interp(rel, e.ingreso_rel, e.consumo_rel); C = pd.Series(crel * media * Q.personas.values, index=Q.index)
den = Q.ipcf + Q.ing_pre_adic
iibb = r.ingresos_brutos / r.consumo_privado * C
cc = 0.5 * Q.contrib.sum() * C / C.sum()
print(f"\ndecil {dec} a mano: C/Y={C[dec] / Q.ipcf[dec]:.3f}  aportes={(Q.ap_jub + Q.ap_inssjp)[dec] / den[dec]:.2%} (proy {t.aportes[dec]:.2%})  "
      f"IIBB={iibb[dec] / den[dec]:.2%} (proy {t.iibb[dec]:.2%})  contrib_consumidor={cc[dec] / den[dec]:.2%} (proy {t.contrib_consumidor[dec]:.2%})  "
      f"Ganancias={Q.ganancias[dec] / den[dec]:.2%} (proy {t.ganancias[dec]:.2%})  total proy={t.total[dec]:.2%}")
print(f"IVA recaudado / consumo privado CN {ANIO} = {r.iva / r.consumo_privado:.4f};  IIBB = {r.ingresos_brutos / r.consumo_privado:.4f}")
