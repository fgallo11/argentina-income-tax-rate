"""Auditoría 07: cuánto mueven los hallazgos de implementación / coherencia (tasa total, pp).
(a) aguinaldo en el denominador sin impuestos en el numerador: T2+T4 vs. los cuatro trimestres;
(b) mitad 'consumidor' de contribuciones a la misma escala que el IVA;
(c) todos los impuestos con la misma cobertura respecto de la recaudación (composición macro);
(d) escenario combinado ilustrativo.
Sólo lee. Uso: .venv/bin/python auditoria/a07_efectos.py [anio]"""
import sys
from pathlib import Path
import numpy as np, pandas as pd
R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R / "src"))
from incidencia.incidencia import Variante, incidencia_trimestre, IMPUESTOS
from incidencia.indirectos import cargar_insumos
pd.set_option("display.width", 250)
A = int(sys.argv[1]) if len(sys.argv) > 1 else 2024
engho, rec = cargar_insumos(); r = rec.loc[A]
q = pd.read_csv(R / "data/processed/eph_trimestral_decil.csv"); q = q[q.anio == A]
COLS = [1, 2, 3, 5, 8, 9, 10, 0]

def trimestres(v):
    return {t: incidencia_trimestre(qt, A, engho, r, v) for t, qt in q.groupby("trim")}
def prom(d, ts=None, col="total"):
    ts = ts or list(d)
    return sum(d[t][col] for t in ts) / len(ts) * 100

out = {}
for nombre, v in [("principal", Variante()), ("ingreso_declarado", Variante("x", corregir_recursos=False)),
                  ("sin_correcciones", Variante("x", corregir_recursos=False, altos_ingresos="no"))]:
    d = trimestres(v)
    out[f"{nombre}: publicado (trimestres {sorted(d)})"] = prom(d)
    par = [t for t in d if t in (2, 4)]
    if par:
        out[f"{nombre}: (a) sólo T2 y T4 (sin aguinaldo)"] = prom(d, par)
    # (b) contribuciones-consumidor a escala macro
    alt = {}
    for t, x in d.items():
        qt = q[q.trim == t].set_index("decil").sort_index()
        C = (x.gasto_sobre_ingreso_declarado.drop(0) * qt.ipcf).sum()
        k = (0.5 * r.ss_empleadores / r.consumo_privado) / (0.5 * qt.contrib.sum() / C)
        y = x.copy(); y["total"] = x.total - x.contrib_consumidor * (1 - k); alt[t] = y
    out[f"{nombre}: (b) contrib. consumidor a escala del IVA"] = prom(alt)
    # (c) cobertura uniforme: cada impuesto reescalado para que lo asignado sea la misma fracción de lo recaudado
    qa = q.groupby("decil").mean(numeric_only=True)
    M = 12 * r.poblacion / qa.personas.sum() / 1e6
    tot = pd.DataFrame({c: sum(d[t][c] for t in d) / len(d) for c in IMPUESTOS + ["total"]})
    g = sum(d[t].gasto_sobre_ingreso_declarado for t in d) / len(d)
    base = (np.maximum(1, g.drop(0)) if v.corregir_recursos else 1) * qa.ipcf
    Y = (base.sum() + qa.ing_pre_adic.sum()) * M
    recd = {"ganancias": r.ganancias_pf, "bienes_personales": r.bienes_personales, "aportes": r.ss_empleados,
            "contrib_trabajador": 0.5 * r.ss_empleadores, "contrib_consumidor": 0.5 * r.ss_empleadores, "iva": r.iva,
            "internos": r.internos_modelados, "iibb": r.ingresos_brutos}
    cov = {c: tot.loc[0, c] * Y / recd[c] for c in IMPUESTOS}
    cu = tot.loc[0, "total"] * Y / sum(v_ for k_, v_ in recd.items() if k_ != "contrib_consumidor" or True) * 1.0
    cu = tot.loc[0, "total"] * Y / (sum(recd.values()))
    re = sum(tot[c] * cu / cov[c] for c in IMPUESTOS if cov[c] > 0) * 100
    out[f"{nombre}: (c) misma cobertura para todos los impuestos ({cu:.0%})"] = re
    if nombre == "principal":
        print("cobertura por impuesto (asignado / recaudado):", {k_: round(v_, 2) for k_, v_ in cov.items()})
        comp = pd.DataFrame({"modelo": {c: tot.loc[0, c] for c in IMPUESTOS}, "recaudación": {c: recd[c] / sum(recd.values()) * tot.loc[0, "total"] for c in IMPUESTOS}}) * 100
        print("composición de la tasa promedio, pp:"); print(comp.round(1).T.to_string())
t = pd.DataFrame(out).T
print(f"\n=== {A}: tasa total % ==="); print(t[COLS].round(1).to_string())
