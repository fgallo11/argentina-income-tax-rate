# Metodología

Estimación de impuestos pagados como porcentaje del ingreso, por decil de ingreso per
cápita familiar, aglomerados urbanos de la EPH, 2004-2024.

## 1. Qué se mide

- **Unidad:** hogar, en términos per cápita. Deciles de personas ordenadas por IPCF,
  ponderadas. Se calculan por trimestre y el dato anual es el promedio simple de los
  trimestres disponibles.
- **Impuestos incluidos:** Ganancias de personas humanas (4ta categoría), Bienes
  Personales, aportes personales (jubilación + INSSJP), contribuciones patronales, IVA,
  Internos e Ingresos Brutos. Son entre 56% y 71% de la recaudación total del país.
- **Excluidos:** derechos de exportación, combustibles, impuesto al cheque, Ganancias de
  sociedades, monotributo y autónomos, impuestos patrimoniales provinciales, sellos y
  tasas municipales. La obra social (3%) se descuenta del salario pero no se cuenta como
  impuesto porque no es recaudación del Estado.
- **Período:** 2004-2024. 2003 se descarta (sólo dos trimestres de EPH continua y sin
  Cuentas Nacionales base 2004).

## 2. Ingreso (denominador)

Ingreso antes de impuestos directos = IPCF (ingreso de bolsillo de la EPH) + aportes
personales + obra social + Ganancias + la parte de las contribuciones patronales que
recae en el trabajador.

**Aguinaldo (base devengada).** La EPH pregunta por el ingreso del mes anterior, así que
en el primer y el tercer trimestre el ingreso total incluye el aguinaldo cobrado en
diciembre o junio (`PP08J1` en la ocupación principal, `V21_M` en jubilaciones), que no
está en `P21` ni en `V2_M`. Se reemplaza el aguinaldo cobrado por el devengado: se resta
el declarado y se suma 1/12 del salario de los asalariados con descuento jubilatorio y de
la jubilación. Los impuestos directos se llevan a la misma base (×13/12). Los deciles se
arman con el IPCF así corregido (`src/incidencia/eph.py`). Supuesto: los asalariados sin
descuento jubilatorio no devengan aguinaldo.

**Corrección de recursos.** En los deciles más bajos el gasto de consumo estimado supera
al ingreso declarado (en el decil 1, entre 1,45 y 2,1 veces). Un hogar no puede gastar
de forma sostenida más de lo que tiene: la diferencia es ingreso no declarado, ingreso
transitoriamente bajo, ayuda de otros hogares o desahorro. En la estimación principal,
cuando el gasto de un decil supera a su ingreso se toma el gasto como medida de sus
recursos. **La comparación es por decil, no por hogar:** ningún hogar de la EPH declara
gasto; el gasto del decil es el cociente gasto/ingreso que la ENGHo muestra para hogares
con el mismo ingreso relativo, aplicado al ingreso del decil. No es el método CEQ, que
mide los impuestos indirectos contra el consumo en todos los deciles; aquí se corrige
sólo donde el gasto supera al ingreso (ver `docs/auditoria.md`, 2.3). La variante `ingreso_declarado` no corrige y se publica siempre al lado: las
dos juntas delimitan el rango del decil 1. La corrección sólo opera en el decil 1 y,
algunos años, en el 2 y el 3.

## 3. Impuestos directos: microsimulación sobre la EPH

Persona por persona, con las reglas vigentes en cada mes del trimestre.

- **Población alcanzada:** asalariados con descuento jubilatorio (PP07H = 1), excluido el
  servicio doméstico, y jubilados. Asalariados no registrados, cuentapropistas y patrones
  tienen tasa cero.
- **Bruto desde neto:** la EPH releva el ingreso de bolsillo. El bruto se obtiene
  invirtiendo numéricamente `neto = bruto − aportes − Ganancias`.
- **Aportes:** jubilación 11% (7% para el sector privado hasta 12/2007, afiliados a
  AFJP), INSSJP 3%, con tope de base (`params/lmi.csv`).
- **Contribuciones patronales:** sólo sector privado; alícuotas del Dto. 814/2001 y
  modificatorias, sin tope. Mitad al trabajador, mitad a precios. La mitad trasladada a
  precios se trata como los demás impuestos indirectos: recaudación de contribuciones por
  peso de consumo privado de Cuentas Nacionales, aplicada al consumo de cada decil.
- **Ganancias:** escalas, deducciones personales y cargas de familia de cada año
  (`params/ganancias.yaml`). El ingreso mensual se anualiza con la trayectoria del RIPTE
  del año. Incluye la reducción de deducciones vigente hasta 2008, el Dto. 1242/2013, los
  mínimos de la Ley 27.617 y el régimen cedular de 10/2023 a 06/2024.

## 4. Impuestos indirectos

**Nivel.** Cada impuesto se expresa como recaudación oficial por peso de consumo privado
de Cuentas Nacionales. Así el nivel refleja lo efectivamente recaudado. En IVA resulta
entre 73% y 87% del contenido legal teórico de la canasta.

**Distribución entre deciles.**

- A cada decil de la EPH se le asigna el consumo y la canasta que la ENGHo muestra para
  hogares con su mismo **ingreso relativo a la media** (interpolando entre veintiles de
  la ENGHo). No se supone que "el decil 1 de la EPH consume como el decil 1 de la ENGHo".
- IVA: según la alícuota legal de cada artículo (`src/incidencia/clasificador.py`; el
  detalle artículo por artículo queda en `data/processed/clasificacion_articulos_*.csv`).
- Internos: por rubro (tabaco, alcohol, cerveza, analcohólicas, vehículos, telefonía).
- Ingresos Brutos: uniforme sobre todo el consumo.

**Ediciones de la ENGHo.** Se interpola linealmente en el tiempo entre 2004/05, 2012/13 y
2017/18 (anclas 2005, 2012 y 2018). El criterio inicial ("cada edición rige hasta la
siguiente") generaba escalones artificiales en 2012 y 2017; se conserva como variante
`engho_escalonado`.

## 5. Ingresos altos: Ganancias y Bienes Personales

La EPH subdeclara los ingresos altos y la simulación de Ganancias sólo alcanza a
asalariados registrados y jubilados: reproduce entre 12% y 37% de lo recaudado. La
corrección usa dos fuentes administrativas (`scripts/aux_anuarios_arca.py` y
`scripts/09_ingresos_altos.py`):

- **Recaudación oficial** de Ganancias de personas humanas y de Bienes Personales (DNIAF).
- **Declaraciones juradas de Ganancias por tramo de ingresos** (anuarios de estadísticas
  tributarias de ARCA, años fiscales 2002-2023): casos, resultado neto e impuesto.

Pasos:

1. *Ganancias faltante* = recaudado − simulado (EPH expandida al país).
2. *Quién lo paga.* Se acumulan los tramos de las declaraciones de mayor a menor y se
   comparan con las personas de mayor ingreso individual de la EPH. En el punto donde lo
   declarado al fisco más supera a la encuesta (entre 0,2% y 1,5% de la población) se
   observa en qué decil viven esas personas: entre 84% y 99,9% en el decil 10, el resto en
   el 9 y el 8. Con esas proporciones se reparten Ganancias faltante y Bienes Personales.
3. *Escala.* Tres opciones, que delimitan el rango del decil 10:
   - **Principal (`cobertura`)**: los montos se llevan a la escala de la encuesta con el
     mismo factor que los impuestos indirectos (recaudación por peso de consumo privado).
     Supone que la EPH subcapta el ingreso del decil 10 en la misma proporción en que las
     encuestas subcaptan el consumo.
   - **Piso (`altos_sin_corregir`)**: Ganancias sólo simulada sobre la EPH. Incluye
     Bienes Personales imputado al decil 10; sin él, ver `sin_correcciones`.
   - **Techo (`altos_registros`)**: todo lo recaudado, por habitante, y al ingreso de la
     encuesta se le suma sólo el ingreso declarado al fisco que la EPH no capta (entre 1% y
     6% del ingreso total de la EPH). Es un techo porque ese ingreso faltante es una cota
     inferior: lo declarado al fisco también está subdeclarado y no incluye rentas exentas.

2024 usa las declaraciones del año fiscal 2023 (último publicado), llevadas a 2024 por el
ingreso medio de la EPH. Bienes Personales sigue siendo una imputación (la EPH no releva
patrimonio): se grafica rayado y existe la variante `sin_bienes_personales`.

## 5 bis. Las dos lecturas

Los resultados se presentan siempre en dos versiones (`fig0_dos_versiones_*`):

- **A. Sin corregir** (variante `sin_correcciones`): ingreso declarado en la EPH y
  Ganancias sólo simulada. Es el criterio habitual de los estudios de incidencia.
  Sobreestima el decil 1 y subestima el decil 10.
- **B. Corregida** (variante `principal`): corrección de recursos (sección 2) y de
  ingresos altos (sección 5). En el decil 1 equivale a medir impuesto sobre gasto, que es
  casi proporcional por construcción, y subestima la carga si esos hogares de verdad
  desahorran o se endeudan.

La carga real de los deciles 1 y 10 está entre A y B. En ninguna de las dos el sistema
resulta progresivo: en A es regresivo en la punta baja; en B es aproximadamente
proporcional, es decir, no redistribuye por el lado de los impuestos.

## 6. Tabla de supuestos

Efecto medido en puntos porcentuales de la tasa total de 2024, salvo indicación.

| Supuesto | Estado | Alternativa calculada | Efecto |
|---|---|---|---|
| Recursos del decil 1 = gasto cuando gasto > ingreso | Supuesto central | `ingreso_declarado` | D1: 22,0 → 31,4. D2: +1,2. Resto: 0 |
| Consumo por ingreso relativo e interpolación de ENGHo | Método | `criterio_inicial` | Elimina escalones de 2012 y 2017 |
| Contribuciones patronales 50% trabajador / 50% precios | Supuesto | `contrib_100_trabajador`, `contrib_100_consumidor` | D1: 20,2 a 23,7. D5: 24,6 a 25,3. D10: 25,1 a 28,3 |
| IVA al nivel recaudado (no al legal) | Anclado a datos | `iva_legal` | Promedio +1,6 |
| Ingresos altos: Ganancias y Bienes Personales faltantes en escala de encuesta | Supuesto central del decil 10 | `altos_sin_corregir` (piso), `altos_registros` (techo) | D10: 23,7 a 30,5 (principal 26,8). Promedio: 24,1 a 26,7. El techo no es válido: implica que el ingreso faltante pagó más Ganancias que la alícuota máxima (`docs/auditoria.md`, 3.4) |
| Lo faltante lo pagan las personas de mayor ingreso de la EPH | Anclado a datos (anuarios ARCA) | No calculada | Reparte entre D8, D9 y D10 |
| Bienes Personales con el mismo reparto que Ganancias faltante | Imputación | `sin_bienes_personales` | D10 −1,2 |
| Aportes a AFJP (hasta 11/2008) cuentan como impuesto | Definición | `sin_afjp` | 2004: promedio −2,0. Desde 2009: 0 |
| 7% de aporte para todo el sector privado hasta 2007 | Supuesto (EPH no informa régimen) | No calculada | Menor |
| Alícuota patronal mayor si el establecimiento tiene más de 40 personas | Supuesto | No calculada | Menor |
| Informales e independientes con tasa cero en directos | Decisión del proyecto | No calculada | Subestima D7-D10 |
| Traslado pleno de IVA, Internos e Ingresos Brutos al consumidor | Supuesto estándar | No calculada | Desconocido |
| Todo el IVA e Ingresos Brutos recae en consumo de hogares | Supuesto | No calculada | Sobreestima indirectos |
| Tramo de transición Ley 27.617 interpolado; cedular 2024 reescalado por SMVM | Aproximación | No calculada | Sólo D10, 2021-2024 |

## 7. Población fija

Los deciles no son las mismas personas a lo largo del tiempo. `scripts/08_poblacion_fija.py`
aplica las reglas y la presión tributaria de cada año a la población de 2017 con ingresos
llevados a cada año por RIPTE. La diferencia con la serie observada es el efecto de
composición. Entre 2004 y 2015 el decil 1 sube 6,3 puntos en la serie observada y 3,5 con
población fija: algo más de la mitad de la suba es presión tributaria y el resto es
composición (más asalariados registrados y jubilados en ese decil).

## 8. Qué falta para cerrar los supuestos abiertos

1. **Altos ingresos.** Hecho en parte (sección 5). Falta: una medida del ingreso real del
   decil 10 que no dependa de la encuesta ni de lo declarado al fisco (Argentina no
   publica cuentas del sector hogares), las rentas exentas (los anuarios las informan de
   forma irregular) y repartir Bienes Personales con las declaraciones de ese impuesto.
2. **Monotributo y autónomos.** La EPH no identifica la condición fiscal de los
   independientes. Se puede imputar la recaudación de monotributo entre cuentapropistas
   en proporción a su ingreso laboral, declarándolo como imputación.
3. **Base de los impuestos indirectos.** Con las matrices de insumo-producto se puede
   separar qué parte de IVA e Ingresos Brutos recae en consumo de hogares.
4. **Ingreso del decil 1.** Comparar la distribución de ingresos ENGHo y EPH en años
   cercanos, y evaluar excluir hogares con ingreso cero.
5. **Verificaciones de norma pendientes:** alícuotas patronales 2003-2019, INSSJP y obra
   social, y varias reglas de IVA marcadas "no verificado" en el clasificador.
