"""Pruebas mínimas de las piezas de cálculo. Correr con:  .venv/bin/python -m pytest -q"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from incidencia.config import PARAMS, RAW  # noqa: E402
from incidencia.indirectos import alicuota_iva, pesos_ediciones  # noqa: E402
from incidencia.util import deciles_ponderados, escala_progresiva  # noqa: E402

hay_datos = (RAW / "macro" / "ripte_mensual.csv").exists()


def test_escala_progresiva():
    lim, al = [10000, 20000], [0.09, 0.14, 0.19]
    assert escala_progresiva(np.array([0.0, 10000, 15000, 30000]), lim, al) == pytest.approx([0, 900, 1600, 4200])


def test_deciles_ponderados_reparten_la_poblacion():
    rng = np.random.default_rng(0)
    v, w = rng.lognormal(size=5000), rng.uniform(50, 500, size=5000)
    d = deciles_ponderados(v, w)
    partes = pd.Series(w).groupby(d).sum() / w.sum()
    assert set(d) == set(range(1, 11))
    assert partes.sub(0.1).abs().max() < 0.005
    assert pd.Series(v).groupby(d).max().is_monotonic_increasing


def test_alicuotas_iva_por_anio():
    assert alicuota_iva("AVPO", 2017) == 0.21 and alicuota_iva("AVPO", 2019) == 0.105
    assert alicuota_iva("C567_21", 2018) == 0.21
    assert alicuota_iva("C567_21", 2019) == pytest.approx(0.21 * (1 - 4.5 / 12))
    assert alicuota_iva("C567_21", 2020) == 0.21          # el Dto. 567/2019 venció el 31/12/2019


def test_pesos_ediciones_engho():
    assert pesos_ediciones(2004) == {"2004": 1.0}
    assert pesos_ediciones(2024) == {"2017": 1.0}
    assert pesos_ediciones(2025) == {"2017": 1.0}
    p = pesos_ediciones(2015)
    assert sum(p.values()) == pytest.approx(1.0) and p["2017"] == pytest.approx(0.5)


def test_lmi_anclas():
    lmi = pd.read_csv(PARAMS / "lmi.csv").set_index("mes").tope_jubilacion
    assert lmi["2004-06"] == 4800 and lmi["2010-03"] == 10119.08
    assert lmi["2013-03"] == 24473.92 and lmi["2024-12"] == 2841525.42
    assert lmi["2025-06"] == 3335458.18 and lmi["2025-12"] == 3731212.01
    assert lmi.is_monotonic_increasing or (lmi.diff().dropna() > -10).all()


@pytest.mark.skipif(not hay_datos, reason="requiere data/raw (correr scripts/01_descargar_datos.py)")
def test_ganancias_2019_caso_a_mano(monkeypatch):
    """Soltero sin hijos, sueldo bruto constante: cálculo a mano con la escala 2019."""
    from incidencia.directos import Parametros, ganancias_mes
    P = Parametros()
    monkeypatch.setattr(P, "k_anual", lambda anio, m: 13.0)      # sin inflación intraanual
    bruto = np.array([100000.0])
    aportes = bruto * 0.17
    imp = ganancias_mes(P, 2019, 6, bruto, np.zeros(1), aportes, np.zeros(1), np.zeros(1))
    neta = (100000 - 17000) * 13
    base = neta - (103018.79 + 494490.17)
    esperado = 76982.75 + 0.31 * (base - 396477.68)
    assert imp[0] * 13 == pytest.approx(esperado, rel=1e-6)


@pytest.mark.skipif(not (PARAMS.parent / "data/processed/ajuste_altos_ingresos.csv").exists(),
                    reason="requiere correr scripts/09_ingresos_altos.py")
def test_ajuste_altos_ingresos():
    a = pd.read_csv(PARAMS.parent / "data/processed/ajuste_altos_ingresos.csv", index_col=0)
    partes = a[[f"parte_d{d}" for d in range(1, 11)]]
    assert partes.sum(axis=1).sub(1).abs().max() < 1e-9
    assert (partes.parte_d10 > 0.8).all()                      # lo faltante recae en el decil 10
    assert (a.ingreso_faltante_mill >= 0).all() and (a.ganancias_faltante_mill > 0).all()
    # rango de sanidad; en base devengada (con aguinaldo) el máximo es 2016, ~0,40
    assert a.ganancias_simulada_mill.div(a.ganancias_recaudada_mill).between(0.1, 0.45).all()


def test_ganancias_2025_tabla_anual():
    """Período fiscal 2025, tabla anual del PDF de la DNIAF (pág. 34): el impuesto fijo de
    cada tramo debe coincidir con la escala acumulada."""
    import yaml
    g = yaml.safe_load(open(PARAMS / "ganancias.yaml", encoding="utf-8"))
    e = g["escalas"]["2025"]
    fijos, piso, acc = [], 0.0, 0.0
    for lim, t in zip(e["limites"], e["alicuotas"]):
        acc += (lim - piso) * t
        fijos.append(acc)
        piso = lim
    publicados = [87495.07, 244986.20, 454974.38, 848702.20, 2344867.94, 4156015.94, 7345211.33, 12837714.51]
    assert fijos == pytest.approx(publicados, abs=0.02)
    assert g["deducciones"]["2025"]["escala"] == "2025"


def test_adulto_equivalente_hogar_tipo():
    """Hogar tipo 2 del INDEC: varón de 35, mujer de 31, hijos de 6 y 8 años = 3,09."""
    from incidencia.eph import adulto_equivalente
    assert adulto_equivalente([1, 2, 1, 2], [35, 31, 6, 8]).sum() == pytest.approx(3.09)
    assert adulto_equivalente([1, 2], [-1, 80]).tolist() == pytest.approx([0.35, 0.63])


def test_monotributo_tablas_continuas():
    import yaml
    per = yaml.safe_load(open(PARAMS / "monotributo.yaml", encoding="utf-8"))["periodos"]
    assert per[0]["desde"] == "2004-01"
    for a, b in zip(per, per[1:]):
        y, m = map(int, a["hasta"].split("-"))
        assert b["desde"] == f"{y + (m == 12)}-{1 if m == 12 else m + 1:02d}"
    for p in per:
        topes = [c["tope_anual"] for c in p["categorias"] if c.get("actividad", "bienes") == "bienes"]
        assert topes == sorted(topes) and all(c["sipa"] > 0 for c in p["categorias"])


@pytest.mark.skipif(not hay_datos, reason="requiere data/raw (correr scripts/01_descargar_datos.py)")
def test_monotributo_categorias():
    from incidencia.directos import Parametros, monotributo_mes
    P = Parametros()
    imp, sipa = monotributo_mes(P, 2025, 5, np.array([1e6, 20e6, 90e6]), np.array([False, True, False]))
    assert imp.tolist() == pytest.approx([3633.98, 28829.60, 0.0])      # A; E bienes; fuera del régimen
    assert sipa.tolist() == pytest.approx([11871.01, 17380.35, 0.0])
    imp, sipa = monotributo_mes(P, 2006, 5, np.array([10000.0, 100000.0]), np.array([False, True]))
    assert imp.tolist() == [33, 405] and sipa.tolist() == [35, 35]   # Ley 25.865: A servicios, L bienes


@pytest.mark.skipif(not (PARAMS.parent / "data/processed/ddjj_ganancias_tramos.csv").exists(),
                    reason="requiere correr scripts/aux_anuarios_arca.py")
def test_ddjj_composicion():
    """Los tramos suman la fila TOTAL y los conteos son coherentes (anuarios de ARCA)."""
    d = pd.read_csv(PARAMS.parent / "data/processed/ddjj_ganancias_tramos.csv")
    cols = ["cuarta_bruta", "cuarta_gastos", "aportes_deducidos", "monto_consumido", "casos_cuarta",
            "casos_aportes_empleado"]
    s = d[~d.es_total].groupby("anio_fiscal")[cols].sum()
    t = d[d.es_total].set_index("anio_fiscal")[cols]
    assert (s / t - 1).abs().max().max() < 0.002
    assert (t.casos_aportes_empleado <= t.casos_cuarta).all()
    assert (t.cuarta_gastos < t.cuarta_bruta).all()
    assert d.exentos.notna().all()


@pytest.mark.skipif(not (PARAMS.parent / "outputs/tables/top1.csv").exists(),
                    reason="requiere correr scripts/10_top1.py")
def test_control_top1():
    """Medida de control del 1%: escenarios ordenados y consumo entre las dos aproximaciones."""
    t = pd.read_csv(PARAMS.parent / "outputs/tables/top1.csv")
    t = t[t.confiable]
    assert t.anio.min() == 2012
    assert ((t.total > t.total_oculta05) & (t.total_oculta05 > t.total_oculta10)
            & (t.total_oculta10 > t.total_oculta25)).all()
    lo, hi = t[["consumo_arca", "consumo_encuesta"]].min(axis=1), t[["consumo_arca", "consumo_encuesta"]].max(axis=1)
    assert t.consumo_usado.between(lo, hi).all()
    assert t.parte_empleados.between(0.2, 0.8).all()
    partes = t[["ganancias", "bienes_personales", "aportes_personales", "contribuciones", "consumo"]].sum(axis=1)
    assert (partes - t.total).abs().max() < 1e-9


def test_importes_identidad_contable():
    """importes() elige el corrimiento de columnas que cumple la identidad del cuadro (.htm corridos)."""
    from incidencia.anuarios import importes
    filas = [["", "TRAMO", "", "PRESENTACIONES", "", "", ""],
             ["", "", "", "TOTAL", "UNO", "", "DOS"],
             ["", "Más de", "Hasta", "Casos", "Importe", "Casos", "Importe"],
             ["", "TOTAL", "", 10, 30, 3, 10, 6, 20],      # datos corridos una columna
             ["", 0, 100, 10, 30, 3, 10, 6, 20]]
    v, c, desde, u = importes(filas, lambda tot: (tot["UNO"] + tot["DOS"], tot["TOTAL"]), con_casos=True)
    assert v["UNO"] == [10, 10] and v["DOS"] == [20, 20] and c["UNO"] == [3, 3]
