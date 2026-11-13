"""Utilidades numéricas compartidas."""
from __future__ import annotations

import numpy as np
import pandas as pd


def deciles_ponderados(valor: np.ndarray, peso: np.ndarray, desempate: np.ndarray | None = None,
                       n: int = 10) -> np.ndarray:
    """Asigna cuantiles ponderados (1..n) a unidades ordenadas por `valor`.

    Cada unidad (hogar) aporta `peso` (personas representadas). Una unidad pertenece al
    cuantil donde cae el punto medio de su masa acumulada, de modo que todos los miembros
    de un hogar quedan en el mismo decil. Los empates se rompen por `desempate` (id del
    hogar), para que el resultado sea determinístico.
    """
    valor = np.asarray(valor, dtype=float)
    peso = np.asarray(peso, dtype=float)
    if desempate is None:
        desempate = np.arange(len(valor))
    orden = np.lexsort((np.asarray(desempate).astype(str), valor))
    acum = np.cumsum(peso[orden])
    medio = (acum - peso[orden] / 2) / acum[-1]
    q = np.minimum(np.floor(medio * n).astype(int) + 1, n)
    out = np.empty(len(valor), dtype=int)
    out[orden] = q
    return out


def escala_progresiva(base: np.ndarray, limites: list[float], alicuotas: list[float]) -> np.ndarray:
    """Impuesto de una escala por tramos con alícuotas marginales."""
    base = np.maximum(np.asarray(base, dtype=float), 0.0)
    imp = np.zeros_like(base)
    piso = 0.0
    for lim, al in zip(list(limites) + [np.inf], alicuotas):
        imp += al * np.clip(base - piso, 0.0, lim - piso)
        piso = lim
    return imp


def leer_serie_mensual(path, col: str | None = None) -> pd.Series:
    """Lee un CSV (indice_tiempo, valor) y devuelve Series indexada por 'AAAA-MM'."""
    d = pd.read_csv(path)
    s = pd.Series(d.iloc[:, 1].values if col is None else d[col].values, index=d.iloc[:, 0].str[:7])
    return s[~s.index.duplicated()]
