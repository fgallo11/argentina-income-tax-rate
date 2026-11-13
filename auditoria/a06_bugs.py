"""Auditoría 06: búsqueda de errores de implementación.
(1) aguinaldo: ¿está en P21? ¿está en el ingreso total (IPCF)?  (2) estacionalidad trimestral de las tasas;
(3) promedio simple de trimestres vs. cociente de sumas; (4) escala de la mitad 'consumidor' de las
contribuciones vs. escala del IVA; (5) qué fracción de cada impuesto recaudado asigna el modelo;
(6) hogares con ingreso cero en el decil 1; (7) frases del README vs tablas.
Sólo lee. Uso: .venv/bin/python auditoria/a06_bugs.py"""
import sys
from pathlib import Path
import numpy as np, pandas as pd
R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R / "src"))
from incidencia.incidencia import Variante, incidencia_trimestre, promedio_anual, IMPUESTOS
from incidencia.indirectos import cargar_insumos
pd.set_option("display.width", 250)
engho, rec = cargar_insumos()
q = pd.read_csv(R / "data/processed/eph_trimestral_decil.csv")

print("(1) aguinaldo en la EPH cruda")
for a, t, f in [(2019, 1, "data/raw/eph/2019T1"), (2019, 2, "data/raw/eph/2019T2"), (2019, 3, "data/raw/eph/2019T3")]:
    p = [x for x in (R / f).rglob("*") if "ndividual" in x.name][0]
    d = pd.read_csv(p, sep=";", decimal=",", low_memory=False, encoding="latin-1"); d.columns = [c.upper() for c in d.columns]
    d = d[(d.PONDIH > 0)]
    for c in ["PP08D1", "PP08D4", "PP08F1", "PP08F2", "PP08J1", "PP08J2", "PP08J3", "P21", "TOT_P12", "P47T", "V2_M", "V21_M", "T_VI"]:
        d[c] = pd.to_numeric(d[c], errors="coerce").fillna(0).clip(lower=0)
    r = d[(d.ESTADO == 1) & (d.CAT_OCUP == 3) & (d.PP07H == 1) & (d.P21 > 0)]
    comp = r.PP08D1 + r.PP08D4 + r.PP08F1 + r.PP08F2 + r.PP08J1 + r.PP08J2 + r.PP08J3
    sinag = comp - r.PP08J1
    w = r.PONDIH
    print(f"  {a}T{t}: registrados con aguinaldo declarado (PP08J1>0): {w[r.PP08J1 > 0].sum() / w.sum():.1%};  "
          f"aguinaldo / P21 (masa): {(w * r.PP08J1).sum() / (w * r.P21).sum():.1%};  "
          f"P21 == suma con aguinaldo: {np.isclose(r.P21, comp).mean():.1%};  P21 == suma sin aguinaldo: {np.isclose(r.P21, sinag).mean():.1%};  "
          f"aguinaldo jubilatorio V21_M / V2_M: {(d.PONDIH * d.V21_M).sum() / (d.PONDIH * d.V2_M).sum():.1%};  "
          f"P47T == P21+TOT_P12+T_VI: {np.isclose(d.P47T, d.P21 + d.TOT_P12 + d.T_VI).mean():.1%}")

print("\n(2) estacionalidad: tasa de aportes y total (ingreso declarado, sin altos) por trimestre, población total")
V = Variante("x", corregir_recursos=False, altos_ingresos="no", incluir_bp=False)
for a in (2012, 2017, 2019, 2022, 2024):
    out = []
    for t, qt in q[q.anio == a].groupby("trim"):
        x = incidencia_trimestre(qt, a, engho, rec.loc[a], V).loc[0]
        out.append(f"T{t}: aportes {x.aportes:.2%} contrib_trab {x.contrib_trabajador:.2%} gan {x.ganancias:.2%} total {x.total:.2%}")
    print(" ", a, " | ".join(out))

print("\n(3) 2024 principal: promedio simple de tasas trimestrales vs. cociente de sumas (trimestres en pesos corrientes)")
P0 = Variante()
tr = {t: incidencia_trimestre(qt, 2024, engho, rec.loc[2024], P0) for t, qt in q[q.anio == 2024].groupby("trim")}
simple = sum(x.total for x in tr.values()) / 4
print("  simple:", (simple * 100).round(2).to_dict())
print("  por trimestre D1:", [round(x.total[1] * 100, 1) for x in tr.values()], " D10:", [round(x.total[10] * 100, 1) for x in tr.values()], " prom:", [round(x.total[0] * 100, 1) for x in tr.values()])

print("\n(4) mitad 'consumidor' de las contribuciones: escala usada vs. escala del IVA (recaudación / consumo privado CN)")
for a in (2004, 2010, 2017, 2024):
    qa = q[q.anio == a].groupby("decil").mean(numeric_only=True)
    r = rec.loc[a]
    t = promedio_anual(q[q.anio == a], a, engho, r, Variante("x", corregir_recursos=False)).set_index("decil")
    C = t.gasto_sobre_ingreso_declarado * qa.ipcf.reindex(t.index).fillna(qa.ipcf.sum())
    C.loc[0] = (t.gasto_sobre_ingreso_declarado.drop(0) * qa.ipcf).sum()
    usada = 0.5 * qa.contrib.sum() / C[0]
    macro = 0.5 * r.ss_empleadores / r.consumo_privado
    print(f"  {a}: por peso de consumo -> usada {usada:.2%} vs macro {macro:.2%} (x{usada / macro:.2f}).  "
          f"contrib_consumidor publicada (ingreso declarado) D1 {t.contrib_consumidor[1]:.1%}, D10 {t.contrib_consumidor[10]:.1%}, prom {t.contrib_consumidor[0]:.1%}; "
          f"a escala macro: D1 {t.contrib_consumidor[1] * macro / usada:.1%}, D10 {t.contrib_consumidor[10] * macro / usada:.1%}, prom {t.contrib_consumidor[0] * macro / usada:.1%}")

print("\n(5) fracción de la recaudación nacional que el modelo asigna a hogares (principal; EPH expandida al país)")
filas = {}
for a in (2004, 2010, 2017, 2024):
    qa = q[q.anio == a].groupby("decil").mean(numeric_only=True); r = rec.loc[a]
    f = r.poblacion / qa.personas.sum(); M = 12 * f / 1e6
    t = promedio_anual(q[q.anio == a], a, engho, r, Variante()).set_index("decil").loc[0]
    den = None
    base = (np.maximum(1, promedio_anual(q[q.anio == a], a, engho, r, Variante()).set_index("decil").gasto_sobre_ingreso_declarado.drop(0)) * qa.ipcf).sum() + qa.ing_pre_adic.sum()
    Y = base * M
    filas[a] = {"aportes": t.aportes * Y / r.ss_empleados, "contribuciones": (t.contrib_trabajador + t.contrib_consumidor) * Y / r.ss_empleadores,
                "ganancias_pf": t.ganancias * Y / r.ganancias_pf, "bienes_pers": t.bienes_personales * Y / r.bienes_personales,
                "iva": t.iva * Y / r.iva, "iibb": t.iibb * Y / r.ingresos_brutos, "internos": t.internos * Y / r.internos_modelados,
                "TOTAL asignado / recaudado incluido": t.total * Y / (r.ss_empleados + r.ss_empleadores + r.ganancias_pf + r.bienes_personales + r.iva + r.ingresos_brutos + r.internos_modelados),
                "ingreso denominador / PIB": Y / r.pib, "impuestos incluidos / PIB": (r.ss_empleados + r.ss_empleadores + r.ganancias_pf + r.bienes_personales + r.iva + r.ingresos_brutos + r.internos_modelados) / r.pib,
                "directos % del total asignado": t.directos / t.total,
                "directos % de lo recaudado incluido": (r.ss_empleados + 0.5 * r.ss_empleadores + r.ganancias_pf + r.bienes_personales) / (r.ss_empleados + r.ss_empleadores + r.ganancias_pf + r.bienes_personales + r.iva + r.ingresos_brutos + r.internos_modelados)}
print(pd.DataFrame(filas).round(3).to_string())

print("\n(7) README: 'deciles 2 a 9 entre 25% y 26%' -> principal 2024:")
print("  ", (promedio_anual(q[q.anio == 2024], 2024, engho, rec.loc[2024], Variante()).set_index("decil").total * 100).round(2).to_dict())
