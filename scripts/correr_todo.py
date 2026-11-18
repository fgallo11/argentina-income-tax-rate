#!/usr/bin/env python
"""Corre todo el pipeline en orden, de los datos crudos a las figuras, y los tests.

Uso:
  .venv/bin/python scripts/correr_todo.py            # todo, desde los datos ya descargados
  .venv/bin/python scripts/correr_todo.py --desde 05  # desde un paso (tras cambiar supuestos)

Cada figura depende de tablas que salen de pasos anteriores; correr sólo 07_graficos.py
después de cambiar un cálculo deja figuras con números viejos. Este script evita eso:
07_graficos.py borra todas las figuras y las vuelve a hacer al final. No descarga datos
(01_descargar_datos.py se corre aparte, una vez).
"""
import argparse
import subprocess
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
PASOS = [
    ("lmi", "aux_construir_lmi.py"),            # tope de aportes
    ("02", "02_procesar_engho.py"),             # canastas de consumo
    ("03", "03_recaudacion_macro.py"),          # recaudación y macro
    ("arca", "aux_anuarios_arca.py"),           # declaraciones juradas por tramo
    ("ipc", "aux_deflactor.py"),                # IPC empalmado
    ("04", "04_microsimulacion_eph.py"),        # impuestos directos sobre la EPH
    ("09", "09_ingresos_altos.py"),             # Ganancias y Bienes Personales faltantes
    ("cn", "aux_cuentas_nacionales.py"),        # Cuentas Nacionales y cobertura de la EPH
    ("05", "05_incidencia.py"),                 # tasas por decil, todas las variantes
    ("06", "06_validacion.py"),
    ("08", "08_poblacion_fija.py"),
    ("10", "10_top1.py"),                       # el 1% más rico
    ("11", "11_tramos_decil10.py"),             # el decil 10 partido en P90-95, P95-99 y 1%
    ("07", "07_graficos.py"),                   # todas las figuras
    ("12", "12_informe_graficos.py"),           # gráficos del informe (docs/informe.md)
    ("13", "13_brecha_recaudacion.py"),         # cuánta plata: proporcional y progresivo
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--desde", default=None, help="código del primer paso (lmi, 02, 03, arca, ipc, 04, ...)")
    args = ap.parse_args()
    codigos = [c for c, _ in PASOS]
    inicio = codigos.index(args.desde) if args.desde else 0
    py = sys.executable
    for codigo, script in PASOS[inicio:]:
        t0 = time.time()
        print(f"== {codigo}: {script}", flush=True)
        r = subprocess.run([py, "-W", "ignore", str(RAIZ / "scripts" / script)], cwd=RAIZ,
                           stdout=subprocess.DEVNULL)
        if r.returncode:
            sys.exit(f"falló {script}")
        print(f"   ok ({time.time() - t0:.0f}s)", flush=True)
    sys.exit(subprocess.run([py, "-m", "pytest", "-q"], cwd=RAIZ).returncode)


if __name__ == "__main__":
    main()
