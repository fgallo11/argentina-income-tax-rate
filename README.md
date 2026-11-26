# Incidencia tributaria por decil de ingreso — Argentina 2004-2025

Estimación de la tasa impositiva efectiva (impuestos como % del ingreso) por decil de
ingreso per cápita familiar, aglomerados EPH, con serie anual 2004-2025.

**Estado: segunda versión.** Pipeline completo, con variantes de sensibilidad, contrafáctico
de población fija y documentación. Quedan supuestos abiertos (ver `docs/metodologia.md`,
secciones 7 y 14): el más importante es la cola alta de ingresos.

**Informe de resultados:** [`docs/informe.md`](docs/informe.md), con la evolución 2004-2025 en
gráficos (`outputs/figures/informe_v2/`, generados por `scripts/14_informe_v2_graficos.py`). Del
decil 1 al 9 y en las tres clases, cada grupo paga una parte de los impuestos casi igual a su parte
del ingreso; el que se aparta es el 1% más rico, que pagó menos de lo que le correspondería en un
sistema proporcional en 2016-2019 y 2024-2025. Con la misma recaudación y un sistema progresivo, el
1% pagaría unos US$8.900 millones más por año y la clase media unos US$8.800 millones menos (2025;
cuenta mecánica).

**Resultado 2025 (estimación principal, impuestos ÷ ingreso declarado):** tasa promedio
23,8%; decil 1, 28,7%; deciles 2 a 9 entre 23,0% y 23,8%; decil 10, 23,8%. En 2024: promedio
24,9%; decil 1, 31,4%; deciles 2 a 9 entre 23,7% y 25,1%; decil 10, 25,0%. El sistema no
es progresivo y es regresivo en la punta baja; dentro del decil 10 la tasa baja hacia la cima
(ver "El decil 10 partido"). La baja de 2025 viene sobre todo de los
impuestos al consumo: lo recaudado por IVA pasó de 10,9% a 10,2% del consumo privado y por
Ingresos Brutos de 6,0% a 5,5%, y eso pesa más abajo (indirectos del decil 1: de 28,5% a
26,8% de su ingreso). La encuesta subdeclara ingresos en todos
los grupos salvo los asalariados registrados, y mucho más arriba (rentas, cuentapropia,
evasión, activos no declarados en el exterior). Ajustar salarios e ingreso de cuentapropistas a
Cuentas Nacionales (INDEC) casi no cambia el perfil (decil 10: 25,3% en 2024 y 24,0% en 2025):
esa subdeclaración se reparte en toda la distribución. Lo que puede moverlo es el ingreso de
capital que la encuesta no capta (sin dato oficial; se estima con supuestos): con rentas ×7 y una
renta de 4% sobre la cartera externa atribuida al 1% más rico, el decil 10 baja a 23,7% (2024) y
22,4% (2025), debajo de todos los deciles; el 1%, a 18,5% en 2025 ([metodología](docs/metodologia.md),
sección 6). Las rentas
internas de los hogares no tienen dato oficial.

**Corrección del 16/11/2026 (ingresos altos).** Hasta esta versión, la Ganancias que la encuesta
no capta se sumaba a los de arriba sin el ingreso que la genera: el 1% de la encuesta quedaba con
más Ganancias sobre su ingreso que el 1% de las declaraciones juradas (2016: 20,2% contra 12,4%).
Ahora se suman juntos el ingreso faltante (con las rentas exentas declaradas) y la Ganancias que
le corresponde, los dos de las declaraciones juradas; la Ganancias del 1% de la encuesta coincide
con la de las declaraciones (2024: 12,0% contra 12,1%). El decil 10 bajó de 26,8% a 25,0% (2024)
y de 26,5% a 23,8% (2025); los deciles 1 a 8 no cambian.

**Auditoría externa:** `docs/auditoria.md` (13/11/2026). Ya se corrigieron el aguinaldo,
la escala de las contribuciones trasladadas a precios y dos parámetros (tope de aportes
09/2007 y edad de hijo deducible 2017). Tras la auditoría la medida principal pasó a ser
el ingreso declarado: la anterior reemplazaba el ingreso del decil 1 por su gasto y no
corregía la subdeclaración de los demás (queda como variante `recursos_gasto`). El
"techo" del decil 10 dejó de graficarse.

**El 1% más rico** (`outputs/figures/fig7_top1.png`). La medida es la del 1% de la encuesta,
completado con lo que declara al fisco: 21,7% en 2025, menos que el decil 1 (28,7%) y que el
decil 10 (23,8%). Como control, el 1% estimado sólo con las declaraciones juradas de Ganancias
(`scripts/10_top1.py`, medida C del informe, desde 2012): 22,8% en 2025. Usa lo que el 1% declara a
ARCA (ingreso, Ganancias, patrimonio, aportes y cuántos aportan como empleados) y estima el consumo
como el punto medio entre el "monto consumido" que calcula ARCA (35,0% del ingreso) y el de la
encuesta (18,5%). Con tres escenarios de ingreso no declarado (5%, 10% y 25% de su ingreso no
salarial) da 21,8%, 20,8% y 17,8%. Es un control y no la medida, porque sólo existe para el 1% y no
se puede combinar con los demás grupos. 2025 todavía es extrapolado (declaraciones de 2024 llevadas
a 2025 con el ingreso del decil 10 de la EPH).

**El decil 10 partido** (`outputs/figures/fig8_decil10_partido.png`, `scripts/11_tramos_decil10.py`):
percentiles 90-95, 95-99 y el 1% superior de la encuesta, con el mismo método que los deciles.
2025: 24,6%, 23,7% y 21,7%: en la cima la tasa baja, por debajo de los deciles medios. El 1% de
la encuesta, completado con el ingreso de las declaraciones juradas, tiene 24,5 canastas por
adulto equivalente; con la renta de activos externos paga 20,1%. El 1% medido sólo con las declaraciones
juradas (control de la figura 7) da 22,8%.

**El decil 10 a lo largo del tiempo** (`outputs/figures/fig9_decil10_serie.png`; la figura 8 de cada
año en `outputs/figures/por_anio/`): el 1% de la encuesta paga más que los percentiles 90-95 en 14
de 22 años y menos en 8 (2014, 2016-2019 y 2023-2025). Lo que mueve su tasa es Ganancias y Bienes
Personales: en 2012-2013 llegó a 34-35%; en 2016, 2018 y 2019, a 22%.

**Distancia entre deciles** (`outputs/figures/fig6_distancia_entre_deciles.png`, en canastas
básicas; `fig6b_distancia_en_pesos.png`, en pesos de hoy): el 10% más rico ingresaba por persona
46 veces lo del 10% más pobre en 2004 y 20 veces en 2024 y 2025; después de impuestos la distancia
es mayor (22 veces en 2024 y en 2025; mayor en los 22 años). En canastas básicas por
adulto equivalente (como mide el INDEC la pobreza), el decil 1 pasó de 0,13 en 2004 a 0,36 en 2017,
0,28 en 2024 y 0,35 en 2025; el decil 10, de 4,8 a 6,4, 4,8 y 6,0.

**Monotributo** (variante `con_monotributo`, [cómo se simula](docs/microsimulacion.md)): cuota por
categoría con las tablas de cada período, quién paga según la EPH y nivel ajustado a lo recaudado.
Sube la tasa total entre 0,1 y 0,7 puntos por decil; no cambia la forma.

**Impuesto al cheque y combustibles** (variantes `con_cheque`, `con_cheque_y_combustibles`): la
medida principal no los incluye; Pessino et al. sí. Con el cheque, 2025: D1 32,0%, D10 24,8%,
promedio 25,2% (2024: 34,7%, 26,0% y 26,3%); con ambos, 2025: D1 33,1%, D10 25,1%, promedio
25,7% (2024: 35,6%, 26,3% y 26,7%).

Comparación con Pessino et al. (2018, publicado por Fundar en Argendata) y con el
International Tax Observatory (2026) en `docs/validacion.md`, sección 3, y en la sección 1 del
informe; sus datos están en `data/externos/`. El "patrimonio" del ITO incluye el impuesto al cheque
(clasificación de la OCDE): ver `docs/metodologia.md`, sección 15.

La figura central de cada año 2004-2025 está en `outputs/figures/por_anio/`. Completando (con una estimación) el
ingreso que la encuesta no capta, el decil 10 queda por debajo de todos los deciles en 2004-2005, 2007-2008,
2016, 2018-2019, 2024 y 2025; en 2006, 2009-2015 y 2020-2023 baja pero sigue por encima del promedio.

Los ingresos por decil de la EPH coinciden con los que publica el INDEC (validado contra el
cuarto trimestre de 2024, los diez deciles).

Figura central: `outputs/figures/fig0_dos_versiones_2025.png` (la de 2024, en `por_anio/`): la carga con el ingreso
declarado y con el ingreso ajustado a Cuentas Nacionales, con la sensibilidad de activos
externos. La lectura contra el consumo queda como variante (`sobre_consumo`): responde otra
pregunta y no registra la capacidad de ahorro de los deciles altos.

Documentación: [metodología](docs/metodologia.md) · [glosario de fuentes](docs/fuentes.md) · [diagramas](docs/diagramas.md) · [simulador de impuestos directos](docs/microsimulacion.md) · [qué mide el informe](docs/informe.md#qué-se-mide) · [validación](docs/validacion.md) ·
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
  Ganancias 4ta categoría), sólo asalariados registrados y jubilados
  ([cómo funciona](docs/microsimulacion.md)). El monotributo de los independientes, como variante.
- **Indirectos:** recaudación oficial por peso de consumo privado, repartida según el
  consumo y la canasta que la ENGHo muestra para hogares del mismo ingreso relativo;
  ediciones de la ENGHo interpoladas en el tiempo.
- **Ingreso:** el declarado en la EPH, antes de impuestos directos, con el aguinaldo en
  base devengada. Variantes: reemplazar el ingreso por el gasto donde éste lo supera
  (`recursos_gasto`) y medir contra el consumo (`sobre_consumo`).
- **Ingresos altos:** a las personas de mayor ingreso de la EPH se les suma el ingreso que
  declaran a ARCA y la encuesta no capta, junto con la Ganancias que pagan por él (declaraciones
  juradas por tramo); el resto de la Ganancias no simulada y Bienes Personales se reparten con
  las mismas declaraciones. El decil 10 se parte además en percentiles 90-95, 95-99 y el 1%.

## Limitaciones principales

- El decil 10 depende de supuestos: entre 21,8% y 25,1% en 2025 según la variante (el piso es el
  ingreso completado con la cota alta de activos externos), porque su ingreso real no se observa.
- El consumo de encuesta es 37-55% del de Cuentas Nacionales.
- El decil 1 declara gastar más de lo que gana: 31,4% contra el ingreso declarado y 22,0%
  si se reemplaza su ingreso por el gasto (2024).
- La encuesta casi no capta al 1% más rico: se completa con las declaraciones juradas de ARCA
  (figuras 8 y 9) y se estima aparte sólo con ellas (figura 7). El 1% de la encuesta tiene pocas
  observaciones y es ruidoso de un año a otro.
- 2007-2015 con reservas (INDEC). 2007, 2015 y 2016 con trimestres faltantes.
