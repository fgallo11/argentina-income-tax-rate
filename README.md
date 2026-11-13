# Incidencia tributaria por decil de ingreso — Argentina 2004-2024

Estimación de la tasa impositiva efectiva (impuestos como % del ingreso) por decil de
ingreso per cápita familiar, aglomerados EPH, con serie anual 2004-2024.

**Estado: segunda versión.** Pipeline completo, con variantes de sensibilidad, contrafáctico
de población fija y documentación. Quedan supuestos abiertos (ver `docs/metodologia.md`,
secciones 6 y 8): el más importante es la cola alta de ingresos.

**Resultado 2024 (estimación principal, impuestos ÷ ingreso declarado):** tasa promedio
25,4%; decil 1, 31,4%; deciles 2 a 9 entre 23,7% y 25,0%; decil 10, 26,8%. El sistema no
es progresivo y es regresivo en la punta baja. La encuesta subdeclara ingresos en todos
los grupos salvo los asalariados registrados, y mucho más arriba (rentas, cuentapropia,
evasión, activos no declarados en el exterior): la tasa real del decil 10 es menor que la
medida. Ajustar salarios e ingreso de cuentapropistas a Cuentas Nacionales (INDEC) casi no
cambia el perfil (decil 10: 26,0%): esa subdeclaración se reparte en toda la distribución.
Lo que puede moverlo es el ingreso de capital no declarado: si se suma la renta de los
activos externos privados (cota alta), el decil 10 baja a 24,5%, debajo de todos los deciles
medios. Las rentas internas de los hogares no tienen dato oficial.

**Auditoría externa:** `docs/auditoria.md` (13/11/2026). Ya se corrigieron el aguinaldo,
la escala de las contribuciones trasladadas a precios y dos parámetros (tope de aportes
09/2007 y edad de hijo deducible 2017). Tras la auditoría la medida principal pasó a ser
el ingreso declarado: la anterior reemplazaba el ingreso del decil 1 por su gasto y no
corregía la subdeclaración de los demás (queda como variante `recursos_gasto`). El
"techo" del decil 10 dejó de graficarse.

**El 1% más rico** (`outputs/figures/fig7_top1.png`), estimado con las declaraciones juradas
de Ganancias y con todo lo que se le puede atribuir (la mitad de las ganancias de las empresas
y de su impuesto, y la renta de los activos externos privados): 30,1% en 2024 (28,5% a 31,7%
según cuánto consuma). Menos que el decil 1 (31,4%) y más que el decil 10 de la encuesta
(26,8%). Sólo con lo que declara al fisco serían 35,8%.

**Distancia entre deciles** (`outputs/figures/fig6_distancia_entre_deciles.png`, en canastas
básicas; `fig6b_distancia_en_pesos.png`, en pesos de hoy): el 10% más rico ingresaba por persona
46 veces lo del 10% más pobre en 2004 y 20 veces en 2024; después de impuestos la distancia es
mayor (22 veces en 2024; mayor en 20 de los 21 años). En canastas básicas por persona, el decil 1
pasó de 0,10 en 2004 a 0,28 en 2017 y 0,22 en 2024; el decil 10, de 4,0 a 5,3 y 4,1.

**Impuesto al cheque y combustibles** (variantes `con_cheque`, `con_cheque_y_combustibles`): la
medida principal no los incluye; Pessino et al. sí. Con el cheque, 2024: D1 34,7%, D10 28,1%,
promedio 27,0%; con ambos: D1 35,6%, D10 28,4%, promedio 27,4%.

Comparación con Pessino et al. (~2018, publicado por Fundar en Argendata) y con el
International Tax Observatory (2026) en `docs/validacion.md`, sección 3.

La figura central de cada año 2004-2024 está en `outputs/figures/por_anio/`. Con el ingreso
no declarado, el decil 10 queda por debajo de todos los deciles en 2004, 2007-2008, 2018-2019 y
2024; en los demás años baja pero sigue por encima del promedio.

Los ingresos por decil de la EPH coinciden con los que publica el INDEC (validado contra el
cuarto trimestre de 2024, los diez deciles).

Figura central: `outputs/figures/fig0_dos_versiones_2024.png`: la carga con el ingreso
declarado y con el ingreso ajustado a Cuentas Nacionales, con la sensibilidad de activos
externos. La lectura contra el consumo queda como variante (`sobre_consumo`): responde otra
pregunta y no registra la capacidad de ahorro de los deciles altos.

Documentación: [metodología](docs/metodologia.md) · [validación](docs/validacion.md) ·
[respuestas a preguntas abiertas](docs/respuestas_preguntas_abiertas.md) ·
[estudios previos](docs/literatura_previa.md)

## Cómo reproducir

```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt   # requiere bsdtar (libarchive)
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
