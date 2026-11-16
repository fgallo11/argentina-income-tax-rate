# Incidencia tributaria por decil de ingreso — Argentina 2004-2025

Estimación de la tasa impositiva efectiva (impuestos como % del ingreso) por decil de
ingreso per cápita familiar, aglomerados EPH, con serie anual 2004-2025.

**Estado: segunda versión.** Pipeline completo, con variantes de sensibilidad, contrafáctico
de población fija y documentación. Quedan supuestos abiertos (ver `docs/metodologia.md`,
secciones 6 y 8): el más importante es la cola alta de ingresos.

**Resultado 2025 (estimación principal, impuestos ÷ ingreso declarado):** tasa promedio
24,6%; decil 1, 28,7%; deciles 2 a 9 entre 23,0% y 23,8%; decil 10, 26,5%. En 2024: promedio
25,4%; decil 1, 31,4%; deciles 2 a 9 entre 23,7% y 25,0%; decil 10, 26,8%. El sistema no
es progresivo y es regresivo en la punta baja. La baja de 2025 viene sobre todo de los
impuestos al consumo: lo recaudado por IVA pasó de 10,9% a 10,2% del consumo privado y por
Ingresos Brutos de 6,0% a 5,5%, y eso pesa más abajo (indirectos del decil 1: de 28,5% a
26,8% de su ingreso). La encuesta subdeclara ingresos en todos
los grupos salvo los asalariados registrados, y mucho más arriba (rentas, cuentapropia,
evasión, activos no declarados en el exterior): la tasa real del decil 10 es menor que la
medida. Ajustar salarios e ingreso de cuentapropistas a Cuentas Nacionales (INDEC) casi no
cambia el perfil (decil 10: 26,0% en 2024 y en 2025): esa subdeclaración se reparte en toda la distribución.
Lo que puede moverlo es el ingreso de capital no declarado: si se suma la renta de los
activos externos privados (cota alta), el decil 10 baja a 24,5% (2024 y 2025): en 2024 queda
debajo de todos los deciles medios; en 2025, debajo de la mayoría (los deciles 3 y 9 quedan en
24,0%). Las rentas internas de los hogares no tienen dato oficial.

**Auditoría externa:** `docs/auditoria.md` (13/11/2026). Ya se corrigieron el aguinaldo,
la escala de las contribuciones trasladadas a precios y dos parámetros (tope de aportes
09/2007 y edad de hijo deducible 2017). Tras la auditoría la medida principal pasó a ser
el ingreso declarado: la anterior reemplazaba el ingreso del decil 1 por su gasto y no
corregía la subdeclaración de los demás (queda como variante `recursos_gasto`). El
"techo" del decil 10 dejó de graficarse.

**El 1% más rico** (`outputs/figures/fig7_top1.png`), estimado con las declaraciones juradas
de Ganancias y con todo lo que se le puede atribuir (la mitad de las ganancias de las empresas
y de su impuesto, y la renta de los activos externos privados): 28,1% en 2024 (26,6% a 29,5%
según cuánto consuma). Menos que el decil 1 (31,4%) y más que el decil 10 de la encuesta
(26,8%). Sólo con lo que declara al fisco serían 33,0%. Estas cifras de 2024 ya usan las
declaraciones juradas del año fiscal 2024 (anuario 2025 de ARCA); la versión anterior las
extrapolaba desde 2023 y daba 30,1% (35,8% sólo con lo declarado). La diferencia es sobre todo
Ganancias: con las declaraciones reales el impuesto determinado es 11,7% del ingreso del grupo,
contra 15,8% en la extrapolación (el ingreso declarado también resultó menor: $96 millones
anuales por persona, contra $112 millones extrapolados). 2025: 26,6% (25,1% a 28,1%),
prácticamente igual al decil 10 (26,5%); sólo con lo declarado, 30,2%. 2025 todavía es
extrapolado (declaraciones de 2024 llevadas a 2025 con el ingreso del decil 10 de la EPH).

**El decil 10 partido** (`outputs/figures/fig8_decil10_partido.png`, `scripts/11_tramos_decil10.py`):
percentiles 90-95, 95-99 y el 1% superior de la encuesta, con el mismo método que los deciles.
2025: 24,2%, 25,8% y 29,0%. Pero el 1% de la encuesta declara 12,4 canastas por persona y el de
las declaraciones juradas 35: la encuesta casi no lo capta. Con la renta de activos externos, el
1% de la encuesta paga 23,0%; el de las declaraciones juradas, 26,6%.

**Distancia entre deciles** (`outputs/figures/fig6_distancia_entre_deciles.png`, en canastas
básicas; `fig6b_distancia_en_pesos.png`, en pesos de hoy): el 10% más rico ingresaba por persona
46 veces lo del 10% más pobre en 2004 y 20 veces en 2024 y 2025; después de impuestos la distancia
es mayor (22 veces en 2024, 21 en 2025; mayor en 21 de los 22 años). En canastas básicas por
persona, el decil 1 pasó de 0,10 en 2004 a 0,28 en 2017, 0,22 en 2024 y 0,28 en 2025; el decil
10, de 4,0 a 5,3, 4,1 y 5,0.

**Impuesto al cheque y combustibles** (variantes `con_cheque`, `con_cheque_y_combustibles`): la
medida principal no los incluye; Pessino et al. sí. Con el cheque, 2025: D1 32,0%, D10 27,7%,
promedio 26,1% (2024: 34,7%, 28,1% y 27,0%); con ambos, 2025: D1 33,1%, D10 28,2%, promedio
26,7% (2024: 35,6%, 28,4% y 27,4%).

Comparación con Pessino et al. (~2018, publicado por Fundar en Argendata) y con el
International Tax Observatory (2026) en `docs/validacion.md`, sección 3.

La figura central de cada año 2004-2025 está en `outputs/figures/por_anio/`. Con el ingreso
no declarado, el decil 10 queda por debajo de todos los deciles en 2004, 2007-2008, 2018-2019,
2024 y 2025; en los demás años baja pero sigue por encima del promedio.

Los ingresos por decil de la EPH coinciden con los que publica el INDEC (validado contra el
cuarto trimestre de 2024, los diez deciles).

Figura central: `outputs/figures/fig0_dos_versiones_2025.png` (la de 2024, en `por_anio/`): la carga con el ingreso
declarado y con el ingreso ajustado a Cuentas Nacionales, con la sensibilidad de activos
externos. La lectura contra el consumo queda como variante (`sobre_consumo`): responde otra
pregunta y no registra la capacidad de ahorro de los deciles altos.

Documentación: [metodología](docs/metodologia.md) · [validación](docs/validacion.md) ·
[respuestas a preguntas abiertas](docs/respuestas_preguntas_abiertas.md) ·
[estudios previos](docs/literatura_previa.md)

## Cómo reproducir

```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt   # requiere bsdtar (libarchive) y unar
.venv/bin/python scripts/01_descargar_datos.py     # EPH, ENGHo, recaudación, ARCA, INDEC, IPC (~5 GB), una vez
.venv/bin/python scripts/correr_todo.py            # todo el pipeline en orden, todas las figuras y los tests
```

Después de cambiar un supuesto, `scripts/correr_todo.py --desde 05` rehace desde las tasas en
adelante. No corras `07_graficos.py` solo: las figuras quedarían con tablas viejas.

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
- **Ingreso:** el declarado en la EPH, antes de impuestos directos, con el aguinaldo en
  base devengada. Variantes: reemplazar el ingreso por el gasto donde éste lo supera
  (`recursos_gasto`) y medir contra el consumo (`sobre_consumo`).
- **Ingresos altos:** lo recaudado por Ganancias que la simulación no capta y Bienes
  Personales se asignan a las personas de mayor ingreso (declaraciones juradas de ARCA),
  en la misma escala que los impuestos indirectos; piso y techo publicados.

## Limitaciones principales

- El decil 10 tiene un rango amplio (24% a 31% en 2024): su ingreso real no se observa.
- El consumo de encuesta es 37-55% del de Cuentas Nacionales.
- El decil 1 declara gastar más de lo que gana: 31,4% contra el ingreso declarado y 22,0%
  si se reemplaza su ingreso por el gasto (2024).
- La encuesta casi no capta al 1% más rico: su carga no se estima por separado y queda
  incluida, de forma incompleta, en el decil 10.
- 2007-2015 con reservas (INDEC). 2007, 2015 y 2016 con trimestres faltantes.
