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
