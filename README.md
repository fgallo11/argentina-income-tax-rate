# Incidencia tributaria por decil de ingreso — Argentina 2004-2024

Estimación de la tasa impositiva efectiva (impuestos como % del ingreso) por decil de
ingreso per cápita familiar, aglomerados EPH, con serie anual 2004-2024.

**Estado: segunda versión.** Pipeline completo, con variantes de sensibilidad, contrafáctico
de población fija y documentación. Quedan supuestos abiertos (ver `docs/metodologia.md`,
secciones 6 y 8): el más importante es la cola alta de ingresos.

**Resultado 2024 (estimación principal):** tasa promedio 25,2% del ingreso; deciles 2 a 9
entre 23,7% y 25,0%; decil 1 entre 22,0% y 31,4% y decil 10 entre 23,7% y 30,5% (principal
26,8%) según cómo se mida su ingreso.

**Auditoría externa:** `docs/auditoria.md` (13/11/2026). Ya se corrigieron el aguinaldo,
la escala de las contribuciones trasladadas a precios y dos parámetros (tope de aportes
09/2007 y edad de hijo deducible 2017); las cifras de arriba los incluyen. Quedan abiertas
las decisiones de presentación que plantea la auditoría (lecturas contra ingreso y contra
consumo, rango coherente del decil 10, cobertura de los impuestos al trabajo).

Figura central: `outputs/figures/fig0_dos_versiones_2024.png` muestra lado a lado la
lectura sin corregir (ingreso declarado, criterio habitual de la literatura) y la corregida.
Ninguna de las dos es "la" cifra: la carga real de los deciles 1 y 10 está entre ambas.

Documentación: [metodología](docs/metodologia.md) · [validación](docs/validacion.md) ·
[respuestas a preguntas abiertas](docs/respuestas_preguntas_abiertas.md) ·
[estudios previos](docs/literatura_previa.md)

## Cómo reproducir

```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt   # requiere bsdtar (libarchive)
.venv/bin/python scripts/01_descargar_datos.py     # EPH, ENGHo, recaudación, anuarios ARCA, normativa (~5 GB)
.venv/bin/python scripts/aux_construir_lmi.py      # tope de aportes (params/lmi.csv)
.venv/bin/python scripts/02_procesar_engho.py
.venv/bin/python scripts/03_recaudacion_macro.py
.venv/bin/python scripts/04_microsimulacion_eph.py
.venv/bin/python scripts/aux_anuarios_arca.py      # declaraciones juradas por tramo (anuarios ARCA)
.venv/bin/python scripts/09_ingresos_altos.py      # corrección de ingresos altos
.venv/bin/python scripts/05_incidencia.py
.venv/bin/python scripts/06_validacion.py
.venv/bin/python scripts/08_poblacion_fija.py
.venv/bin/python scripts/07_graficos.py
.venv/bin/python -m pytest -q
```

## Estructura

- `params/` parámetros legales con fuente y estado de verificación (`ganancias.yaml`,
  `seguridad_social.yaml`, `lmi.csv`).
- `src/incidencia/` código: lectura EPH, microsimulación de directos, clasificación fiscal
  de artículos ENGHo, impuestos indirectos.
- `scripts/` pipeline numerado. `data/raw` e `interim` no se versionan.
- `outputs/tables`, `outputs/figures` resultados. `legacy/` notebook original (borrador).

## Método en breve

- **Directos:** microsimulación legal sobre la EPH (aportes, contribuciones patronales,
  Ganancias 4ta categoría), sólo asalariados registrados y jubilados.
- **Indirectos:** recaudación oficial por peso de consumo privado, repartida según el
  consumo y la canasta que la ENGHo muestra para hogares del mismo ingreso relativo;
  ediciones de la ENGHo interpoladas en el tiempo.
- **Ingreso:** antes de impuestos directos, con el aguinaldo en base devengada; si el gasto
  que la ENGHo indica para el decil supera su ingreso declarado se toma el gasto como
  medida de sus recursos (comparación por decil, no por hogar; variante sin corregir publicada).
- **Ingresos altos:** lo recaudado por Ganancias que la simulación no capta y Bienes
  Personales se asignan a las personas de mayor ingreso (declaraciones juradas de ARCA),
  en la misma escala que los impuestos indirectos; piso y techo publicados.

## Limitaciones principales

- El decil 10 tiene un rango amplio (24% a 31% en 2024): su ingreso real no se observa.
- El consumo de encuesta es 37-55% del de Cuentas Nacionales.
- El decil 1 tiene un rango amplio (24% a 35% en 2024).
- No se estima el 1% superior. 2007-2015 con reservas (INDEC). 2007, 2015 y 2016 con
  trimestres faltantes.
