"""Auditoría 01: (a) reproduce outputs/tables desde data/processed sin escribir nada del pipeline;
(b) descompone 2024 de 'sin_correcciones' a 'principal'; (c) variantes propias.
Sólo lee. Uso: .venv/bin/python auditoria/a01_reproducir_y_variantes.py"""
import sys
from dataclasses import replace
from pathlib import Path
import numpy as np, pandas as pd
R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R / "src"))
from incidencia.incidencia import IMPUESTOS, VARIANTES, Variante, promedio_anual, incidencia_trimestre
from incidencia.indirectos import cargar_insumos, perfil_consumo, tasas_indirectas
pd.set_option("display.width", 250)

engho, rec = cargar_insumos()
q = pd.read_csv(R / "data/processed/eph_trimestral_decil.csv")
pub = pd.read_csv(R / "outputs/tables/tasas_por_decil_anual.csv")

# (a) reproducción
mx = 0
for v in VARIANTES:
    for anio, qa in q.groupby("anio"):
        p = promedio_anual(qa, anio, engho, rec.loc[anio], v).set_index("decil").total
        o = pub[(pub.variante == v.nombre) & (pub.anio == anio) & (pub.impuesto == "total")].set_index("decil").tasa
        mx = max(mx, (p - o).abs().max())
print("(a) desvío máximo recalculado vs publicado (todas las variantes y años):", mx)

def fila(v, anio=2024):
    p = promedio_anual(q[q.anio == anio], anio, engho, rec.loc[anio], v).set_index("decil")
    return (p.total * 100).round(1)

# (b) descomposición secuencial 2024
pasos = [
    ("0 sin nada: ingreso declarado, sin BP, Gan simulada", Variante("x", corregir_recursos=False, altos_ingresos="no", incluir_bp=False)),
    ("1 + Bienes Personales todo a D10", Variante("x", corregir_recursos=False, altos_ingresos="no")),
    ("2 + Ganancias faltante (cobertura)", Variante("x", corregir_recursos=False)),
    ("3 + corrección de recursos = principal", Variante()),
]
t = pd.DataFrame({n: fila(v) for n, v in pasos}).T
print("\n(b) 2024, tasa total %:"); print(t.to_string())
for a in (2004, 2010, 2017):
    print(a, pd.DataFrame({n: fila(v, a) for n, v in pasos}).T[[0, 1, 2, 5, 9, 10]].to_string())

# (c) variantes propias
print("\n(c) variantes propias 2024")
otras = {
    "contrib 75/25 (CEPAL), ingreso declarado, sin altos": Variante("x", corregir_recursos=False, altos_ingresos="no", fraccion_contrib_trabajador=0.75),
    "contrib 100% trab, ingreso declarado, sin altos": Variante("x", corregir_recursos=False, altos_ingresos="no", fraccion_contrib_trabajador=1.0),
    "principal con ENGHo 2004 fija": Variante("x", modo_engho="2004"),
    "principal con ENGHo 2012 fija": Variante("x", modo_engho="2012"),
    "ingreso declarado con ENGHo 2004 fija": Variante("x", corregir_recursos=False, modo_engho="2004"),
    "ingreso declarado con ENGHo 2012 fija": Variante("x", corregir_recursos=False, modo_engho="2012"),
}
print(pd.DataFrame({n: fila(v) for n, v in otras.items()}).T.to_string())

# serie D1/D10/prom sin correcciones vs principal
s = {}
for anio in sorted(q.anio.unique()):
    a = fila(Variante("x", corregir_recursos=False, altos_ingresos="no"), anio); b = fila(Variante(), anio)
    s[anio] = dict(sc_D1=a[1], sc_D10=a[10], sc_prom=a[0], pr_D1=b[1], pr_D10=b[10], pr_prom=b[0])
print(pd.DataFrame(s).T.to_string())
