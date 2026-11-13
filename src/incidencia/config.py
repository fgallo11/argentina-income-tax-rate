"""Rutas y constantes globales del proyecto."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

PARAMS = ROOT / "params"
RAW = ROOT / "data" / "raw"
INTERIM = ROOT / "data" / "interim"
PROCESSED = ROOT / "data" / "processed"
FIGURES = ROOT / "outputs" / "figures"
TABLES = ROOT / "outputs" / "tables"

for _p in (RAW, INTERIM, PROCESSED, FIGURES, TABLES):
    _p.mkdir(parents=True, exist_ok=True)

ANIO_INI = 2003
ANIO_FIN = 2024

# Trimestres de la EPH continua que INDEC nunca publicó.
# 2003 T1-T2: la EPH continua empieza en el 3er trimestre de 2003.
# 2007 T3: no relevado/publicado. 2015 T3-T4 y 2016 T1: emergencia estadística
# (Decretos 181/2015 y 55/2016).
TRIMESTRES_INEXISTENTES = {
    (2003, 1), (2003, 2), (2007, 3), (2015, 3), (2015, 4), (2016, 1),
}

# Período en que INDEC desaconseja el uso de sus series (IPC y, con reservas,
# EPH): enero 2007 - diciembre 2015.
ANIOS_ADVERTENCIA_INDEC = range(2007, 2016)


def trimestres_disponibles():
    """Lista (anio, trimestre) de la EPH continua publicados por INDEC."""
    return [
        (a, t)
        for a in range(ANIO_INI, ANIO_FIN + 1)
        for t in (1, 2, 3, 4)
        if (a, t) not in TRIMESTRES_INEXISTENTES
    ]
