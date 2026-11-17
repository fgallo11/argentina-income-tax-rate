# Metodología

Estimación de impuestos pagados como porcentaje del ingreso, por decil de ingreso per
cápita familiar, aglomerados urbanos de la EPH, 2004-2025.

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
- **Período:** 2004-2025. 2003 se descarta (sólo dos trimestres de EPH continua y sin
  Cuentas Nacionales base 2004). 2026 no se incluye: a noviembre de 2026 hay sólo dos
  trimestres de EPH y no hay recaudación, consumo ni Cuentas Nacionales anuales.
- **2025 (agregado el 16/11/2026):** Ganancias con la tabla anual del período fiscal 2025
  (PDF de la DNIAF, pág. 34; desde 2025 los montos se actualizan por IPC cada semestre y el
  modelo usa la tabla anual, como en 2024); tope de aportes con la cadena de movilidad,
  controlada contra las Res. ANSES 237/2025, 338/2025 y 359/2025 (coincide con las tres);
  contribuciones patronales iguales a 2020-2024 (Ley 27.541: no se encontró norma que las
  cambie en 2025; la reducción de la reforma laboral es de 2026; continuidad no contrastada
  con texto primario). La ENGHo sigue siendo la 2017/18.

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

**Medida principal: el ingreso declarado.** La pregunta del proyecto es qué parte de lo
que se gana va a impuestos, así que el denominador es el ingreso, no el gasto. La
encuesta subdeclara ingresos en todos los grupos salvo los asalariados registrados
(cuentapropia, rentas, evasión, activos no declarados en el exterior), y la subdeclaración
crece con el ingreso. Por eso la tasa medida del decil 10 está sobreestimada y la del
decil 1 algo sobreestimada; la corrección consistente es ajustar los ingresos de todos los
deciles a Cuentas Nacionales por fuente (sección 8, pendiente).

**Variante `recursos_gasto`** (era la principal hasta la auditoría). En los deciles más
bajos el gasto de consumo estimado supera al ingreso declarado (en el decil 1, entre 1,45 y
2,1 veces); la variante toma el gasto como medida de sus recursos donde lo supera. La
comparación es por decil, no por hogar: ningún hogar de la EPH declara gasto; el gasto del
decil es el cociente gasto/ingreso que la ENGHo muestra para hogares con el mismo ingreso
relativo. Dejó de ser la principal porque corrige la subdeclaración sólo abajo, lo que
aplanaba el perfil (`docs/auditoria.md`, 2.3). Opera en el decil 1 y, algunos años, en el
2 y el 3.

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
   - **Principal (`cobertura`, corregida el 16/11/2026)**: dos partes.
     a) A las personas del empalme se les suma el ingreso que la EPH no capta (resultado neto
        más rentas exentas declaradas) y la Ganancias que declaran y la EPH no simula
        (declarada − simulada sobre esas mismas personas), en pesos por habitante. Así ese
        grupo queda con el ingreso y el impuesto de sus declaraciones juradas.
     b) El resto de la Ganancias faltante (entre 28% y 60% según el año) lo pagan los demás
        declarantes, cuyo ingreso la EPH sí capta: se suma como impuesto, sin ingreso, en la
        escala de la encuesta (recaudación por peso de consumo privado), repartido según dónde
        viven las personas de la EPH entre el puesto del empalme y el total de declaraciones.
        Bienes Personales se divide igual, según la parte del patrimonio declarado que es de
        las personas del empalme.
     Antes toda la Ganancias faltante se sumaba a los de arriba sin su ingreso: el 1% de la
     encuesta quedaba con más Ganancias sobre su ingreso que el 1% de las declaraciones juradas
     (2016: 20,2% contra 12,4%), lo que es incoherente con un impuesto progresivo. Ahora coinciden
     (2004: 13,3% y 13,0%; 2024: 12,0% y 11,7%).
   - **Piso (`altos_sin_corregir`)**: Ganancias sólo simulada sobre la EPH. Incluye
     Bienes Personales imputado al decil 10; sin él, ver `sin_correcciones`.
   - **Techo (`altos_registros`)**: todo lo recaudado, por habitante, y al ingreso de la
     encuesta se le suma sólo el ingreso declarado al fisco que la EPH no capta (entre 1% y
     6% del ingreso total de la EPH). Es un techo porque ese ingreso faltante es una cota
     inferior: lo declarado al fisco también está subdeclarado y no incluye rentas exentas.

2025 usa las declaraciones del año fiscal 2024 (último publicado: anuario 2025 de ARCA),
llevadas a 2025 por el ingreso medio de la EPH. 2024 ya usa sus propias declaraciones. Bienes Personales sigue siendo una imputación (la EPH no releva
patrimonio): se grafica rayado y existe la variante `sin_bienes_personales`.

## 5 bis. Ingreso declarado y ingreso ajustado a Cuentas Nacionales

La figura central (`fig0_dos_versiones_*`) muestra:

- **A. Ingreso declarado** (variante `principal`). 2024: D1 31,4%, deciles medios ~25%,
  D10 25,0%, promedio 24,9%. 2025: D1 28,7%, deciles medios ~23,5%, D10 23,8%, promedio 23,8%.
- **B. Ingreso ajustado a Cuentas Nacionales** (variante `ajuste_cn`,
  `scripts/aux_cuentas_nacionales.py`). Cada fuente de ingreso se lleva al total de la
  Cuenta de generación del ingreso del INDEC con un factor propio, aplicado a quien
  declara esa fuente:
  - salarios (bruto de registrados + no registrados) a la remuneración al trabajo
    asalariado. La EPH capta 68%-78%. Para comparar se suman a la EPH las contribuciones
    patronales simuladas, 18% del bruto de los registrados públicos y 6% de obra social
    patronal, que la remuneración incluye;
  - ingreso de cuentapropistas y patrones (más otras ocupaciones) al ingreso mixto bruto.
    La EPH capta 50%-72%, menos en los últimos años.

  Para 2004-2015 no hay Cuenta de generación del ingreso en base 2004: se usa la cobertura
  promedio 2016-2018. **Nivel neutro:** todos los impuestos se escalan por el mismo factor
  para que la carga total sobre el ingreso total quede como en A. Llevar los impuestos a la
  escala de lo recaudado (consumo de Cuentas Nacionales) sin tener el ingreso completo de
  los hogares inflaba las tasas: el decil 1 daba 67%. El ajuste muestra cómo cambia el
  reparto, no el nivel. 2024: D1 32,2%, D10 25,3%. 2025: D1 29,8%, D10 24,0%.
- **Sensibilidad de activos externos** (variante `ajuste_cn_activos_ext`): además, 3% anual
  sobre los activos externos de "otros sectores" (inversión de cartera + moneda y
  depósitos; Posición de inversión internacional, INDEC, cuadro 18; a pesos con el tipo de
  cambio A 3500 promedio) como ingreso no declarado, repartido como la Ganancias faltante
  (declaraciones juradas: casi todo al decil 10). Es una cota alta: supone que nada de eso
  se declara, que los billetes rinden como depósitos y que todo pertenece a hogares, aunque
  el sector incluye empresas. 2024: D10 24,1%, debajo de todos los deciles medios. 2025: D10
  22,9%, debajo de todos los deciles.

Resultado: la subdeclaración de salarios y de cuentapropia está repartida en toda la
distribución y casi no cambia el perfil. Lo que puede volver regresiva también la punta
alta es el ingreso de capital no declarado. Las rentas internas de los hogares
(intereses, alquileres, dividendos) no tienen dato oficial: el INDEC no publica la cuenta
del sector hogares. La EPH registra rentas por 0,4%-0,7% del PIB, una cifra inverosímil.

**Contra el consumo** (variante `sobre_consumo`): impuestos ÷ (gasto + impuestos
directos). 2024: D1 22,0%, D10 33,6%. 2025: D1 20,2%, D10 31,8%. Responde otra pregunta (qué parte de lo que se gasta
va a impuestos) y no registra que los deciles altos ahorran y subdeclaran. No se grafica.

La variante `altos_registros` ("techo" del decil 10) se sigue calculando pero no se
grafica ni entra en los rangos: implica que el ingreso faltante pagó más Ganancias que la
alícuota máxima (`docs/auditoria.md`, 3.4).

## 6. Tabla de supuestos

Efecto medido en puntos porcentuales de la tasa total de 2024, salvo indicación.

| Supuesto | Estado | Alternativa calculada | Efecto |
|---|---|---|---|
| Recursos = ingreso declarado (no se reemplaza por gasto) | Medida principal | `recursos_gasto` | D1: 31,4 → 22,0. D2: −1,2. Resto: 0 |
| Consumo por ingreso relativo e interpolación de ENGHo | Método | `criterio_inicial` | Elimina escalones de 2012 y 2017 |
| Contribuciones patronales 50% trabajador / 50% precios | Supuesto | `contrib_100_trabajador`, `contrib_100_consumidor` | D1: 28,8 a 34,0. D5: 24,6 a 25,3. D10: 23,6 a 26,2 |
| IVA al nivel recaudado (no al legal) | Anclado a datos | `iva_legal` | Promedio +1,6 |
| Ingresos altos: Ganancias y Bienes Personales faltantes en escala de encuesta | Supuesto central del decil 10 | `altos_sin_corregir` (piso), `altos_registros` (techo) | D10: 23,7 a 31,5 (principal 25,0). Promedio: 24,3 a 27,2. El techo no es válido: implica que el ingreso faltante pagó más Ganancias que la alícuota máxima (`docs/auditoria.md`, 3.4) |
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
aplica las reglas y la presión tributaria de cada año a una población fija, con sus
ingresos llevados a cada año por RIPTE y la canasta de la ENGHo de su momento. Se calcula
con dos años base, porque el resultado depende de cuál se deja fijo (problema de números
índice): **2004**, el primero de la serie (ENGHo 2004/05), y **2017**, la ENGHo más reciente
(2017/18). Con base 2004 la serie coincide con la observada en 2004, como debe.

Variación 2004-2015, en puntos de la tasa total:

| | Observada | Población de 2004 | Población de 2017 |
|---|---|---|---|
| Decil 1 | +0,5 | +9,7 | +7,2 |
| Decil 5 | +5,2 | +5,5 | +5,1 |
| Decil 10 | +11,1 | +11,4 | +10,4 |

En los deciles 5 y 10 casi todo el cambio es presión tributaria: las tres columnas se
parecen. En el decil 1 las reglas habrían subido la carga entre 7 y 10 puntos, pero la
serie observada casi no se movió. La diferencia mezcla dos cosas: cambió quién está en el
decil (más asalariados registrados y jubilados) y cambió su gasto respecto de su ingreso
entre ediciones de la ENGHo (el cociente del decil 1 es 1,59 en la 2004/05, 1,68 en la 2012/13 y 1,45 en la
2017/18). Con estos datos no se pueden separar.

## 6 bis. Lo que se tomó de Pessino et al. (2023) y De Rosa, Flores y Morgan (2024)

Papers en `papers/`. Variantes nuevas (2024, total % del ingreso):

| Variante | Qué hace | D1 | D5 | D10 | Prom. |
|---|---|---|---|---|---|
| `principal` | ingreso declarado | 31,4 | 25,0 | 25,0 | 24,9 |
| `iva_exentos_20` | bienes exentos cargan 20% de la alícuota por insumos (Pessino et al.) | 31,2 | 24,9 | 25,1 | 24,9 |
| `con_cheque` | suma impuesto a créditos y débitos (Pessino et al. lo incluyen como "cascada") | 34,7 | 26,8 | 26,0 | 26,3 |
| `ajuste_cn_rentas` | Cuentas Nacionales + rentas de la EPH × 7 (las encuestas captan 1/5 a 1/10; De Rosa et al.) | 33,9 | 26,1 | 24,1 | 24,9 |
| `ajuste_cn_rentas_activos_ext` | lo anterior + renta de activos externos | 35,0 | 26,9 | 23,1 | 24,9 |

El panel B de la figura 0 usa `ajuste_cn_rentas` con la marca de `ajuste_cn_rentas_activos_ext`:
con el ingreso de capital no declarado el decil 10 queda por debajo de todos los demás.

**No vale para todos los años.** Con rentas ×7 y activos externos, el decil 10 queda por
debajo de todos los deciles medios sólo en 2004, 2007, 2008, 2018, 2019, 2024 y 2025. En 2009-2017 y
2020-2023 baja pero sigue por encima del promedio (Ganancias pesaba más en esos años). La
figura 0 para cada año está en `outputs/figures/por_anio/` y su texto se adapta al resultado.

Pendiente de Pessino et al. (no implementado):
- **Compras informales:** el IVA y Ingresos Brutos de lo que se compra en comercios informales
  se paga sólo en 20%. Los pobres compran más en la informalidad: hace menos regresivo el IVA.
  Requiere el lugar de compra de la ENGHo.
- **Cascada con matriz insumo-producto:** Ingresos Brutos y cheque acumulan distinto según el
  producto (usaron el código fiscal de Buenos Aires 2018 y la matriz INDEC 1997).
- **Derechos de importación** y **Ganancias de sociedades** repartida por deciles (100% al
  capital, o 50% capital / 50% trabajo).
- **Concepto de ingreso:** incluyen el alquiler imputado de la vivienda propia; la EPH no lo trae.
- **Contribuciones con mercado integrado:** 50% recae en salarios informales.

## 7 bis. Distancia entre deciles (figuras 6 y 6b)

Brecha de ingresos: ingreso por persona del decil 10 dividido por el del decil 1 (como la
"brecha de ingresos" que publica el INDEC), antes de impuestos directos y después de restar
todos los impuestos estimados con la medida principal.

Panel derecho: ingreso de bolsillo por persona de los diez deciles y, punteado, el ingreso
declarado a ARCA por declarante del 1% más rico (no estrictamente comparable: es por persona
que declara, no por miembro del hogar, y no incluye utilidades ni activos externos).
- **Figura 6, en canastas básicas:** ingreso por persona / canasta básica total del Gran Buenos
  Aires por adulto equivalente (INDEC). No depende de la inflación ni del tipo de cambio y,
  a diferencia de una medida relativa (veces el promedio), muestra si el ingreso real crece.
  La serie oficial empieza en 04/2016; antes de 2017 se usa la de 2017 llevada hacia atrás con
  el IPC empalmado (las canastas oficiales de 2007-2015 están intervenidas). La canasta es por
  adulto equivalente: el umbral de pobreza por persona es algo menor que 1.
- **Figura 6b, en pesos de hoy:** pesos constantes del último mes publicado del IPC. Deflactor
  (`scripts/aux_deflactor.py`): IPC-GBA del INDEC hasta 12/2006, IPC de San Luis 2007-2016 e
  IPC Nacional del INDEC desde 2017.

Los hogares del decil 1 tienen 3,9 personas en promedio; los del decil 10, 2,0. Es ingreso
declarado en la encuesta: el decil 10 está subestimado y no incluye al 1% más rico.

**Validación contra el INDEC.** Con los deciles armados sobre el ingreso tal como lo publica
el INDEC (sin el ajuste de aguinaldo), el ingreso medio por persona de los diez deciles, sus
límites, la media ($442.596) y la población (29.783.755) del cuarto trimestre de 2024 coinciden
con el informe "Evolución de la distribución del ingreso (EPH)" del INDEC (cuadro 1). El decil
10 promedia $1.430.619 por persona en pesos de ese trimestre: es por persona, no por hogar.

## 7 ter. El 1% más rico (figura 7)

`scripts/10_top1.py`, con las declaraciones juradas de Ganancias por tramo (anuarios de ARCA,
años fiscales 2002-2024; 2025 extrapolado), como Alvaredo (2010). Grupo: el 1% de la población con mayores
ingresos declarados (todo el grupo está dentro de las declaraciones). Ingreso, Ganancias y
patrimonio se acumulan de los tramos más altos hacia abajo, interpolando en el corte.

**Estimación principal ("completo"): todo lo que se le puede atribuir.** Ingreso = declarado
al fisco + la mitad de las utilidades de las empresas (impuesto de sociedades / 30%; es dueño
de la mitad) + renta del 3% de los activos externos privados (cartera y depósitos, INDEC).
Impuestos = Ganancias declarada + Bienes Personales según su patrimonio + la mitad de la
Ganancias de sociedades + aportes y contribuciones (la mitad del ingreso es salario, aportes
con tope) + impuestos al consumo (entre la mitad y el total del cociente gasto/ingreso del 5%
más rico de la ENGHo).

2024: 28,1% (26,6-29,5 según el consumo). Sólo con lo declarado al fisco: 33,0%; sin los
activos externos: 31,8%. (Hasta el 16/11/2026, con las declaraciones de 2023 extrapoladas,
daba 30,1%, 35,8% y 33,7%: la Ganancias determinada real del grupo es 11,7% de su ingreso,
contra 15,8% extrapolado.) 2025 (extrapolado): 26,6% (25,1-28,1); sólo con lo declarado,
30,2%; sin los activos externos, 30,1%. Sigue siendo un techo: las rentas internas no declaradas no figuran
en ninguna fuente. Pesa el supuesto de que la mitad del ingreso es salario (aportes y
contribuciones: 8,2% del ingreso declarado).

## 7 quater. Impuesto al cheque y combustibles

La medida principal excluye el impuesto a los créditos y débitos bancarios y el de
combustibles. Pessino et al. (2023) los incluyen ("en cascada" y "otros"). Variantes
`con_cheque` y `con_cheque_y_combustibles`: recaudación por peso de consumo privado aplicada
al consumo de cada decil, como Ingresos Brutos. Supuestos: el cheque se traslada entero a
precios; combustibles se reparte como el consumo total (falta la canasta de combustibles por
decil de la ENGHo). 2018 con cheque: D1 37,1%, D2 27,6%, D10 28,4% (Pessino et al.: 35,8%,
30,8%, 24,9%).

## 7 quinquies. El decil 10 partido (figura 8)

`scripts/11_tramos_decil10.py` (agregado el 16/11/2026). El decil 10 se parte en percentiles
90-95, 95-99 y el 1% superior, con el mismo orden (ingreso per cápita familiar), la misma regla
de corte y la misma microsimulación que los deciles (`src/incidencia/eph.py`, columna `grupo`;
`data/processed/eph_trimestral_tramos.csv`). Los deciles 1-9 no cambian. Motivo: el promedio
del decil 10 mezcla a la clase media alta asalariada con los ricos.

- **Ganancias faltante y Bienes Personales:** la parte del decil 10 se reparte entre los tramos
  según el tramo del hogar de las personas que empalman con las declaraciones juradas
  (`parte_d91`, `parte_d95`, `parte_d99` en `ajuste_altos_ingresos.csv`; 2025: 4%, 37% y 59%),
  y el resto de la Ganancias faltante según los demás declarantes (`resto_d91`, etc.).
- **Consumo:** la ENGHo sólo llega al promedio del 5% más rico (su veintil más alto). Por encima,
  la medida principal deja fijo el consumo; la variante `consumo_proporcional` deja fijo el
  cociente gasto/ingreso. Sólo cambia el 1% superior (2025: 21,7% contra 23,6%).
- **Rango:** principal, `consumo_proporcional`, `ajuste_cn`, `ajuste_cn_activos_ext` y
  `sin_bienes_personales`.

Resultado 2025 (principal): P90-95 24,6%, P95-99 23,7%, 1% de la encuesta 21,7% (rango 19,9-23,6).
En la cima la tasa baja, por debajo de los deciles medios (~23,6%). El 10% más rico tiene 37,6% del
ingreso (encuesta más el ingreso declarado al fisco que la encuesta no capta) y el 1% 10,8% (9,9%
de los impuestos). El 1% de la encuesta, completado, tiene 20,9 canastas por persona; el de las
declaraciones juradas, 35 por declarante. Con la renta de activos externos, el 1% de la encuesta
paga 20,1%. El 1% de la sección 7 ter da 26,6% porque además suma la mitad del impuesto de
sociedades (y la mitad de las utilidades al ingreso) y supone que la mitad de su ingreso es salario.

(Hasta la corrección del 16/11/2026 este tramo daba 29,0%: la Ganancias faltante se le sumaba sin
su ingreso.)

**Comparación con repartos de referencia (figura 8, paneles derechos).** Misma recaudación total,
repartida de dos formas: proporcional (todos pagan la tasa promedio, es decir, cada grupo aporta su
parte del ingreso) y progresiva (tasa = promedio × (ingreso por persona / promedio)^0,25, reescalada
para recaudar lo mismo; con ese exponente el decil 1 pagaría 12,7% y el 1% superior 37,0% en 2025).
El exponente es una elección para ilustrar, no una norma (`ELAST_PROG` en `scripts/07_graficos.py`).
Frente al proporcional los desvíos son menores a 1 punto; frente al progresivo, los deciles 1 a 9
pagan entre 0,5 y 1,5 puntos más de su parte y el 1% superior 7 puntos menos.

**Serie (figura 9) y figura 8 por año** (`outputs/figures/por_anio/fig8_decil10_partido_<año>.png`).
El 1% de la encuesta paga más que los percentiles 90-95 en 14 de 22 años y menos en 2016-2019, 2024
y 2025. Lo que mueve su tasa es Ganancias y Bienes Personales; el consumo pesa poco arriba. El salto
de 2006 (31%, contra 24-26% en 2005 y 2007) y los vaivenes de 2016-2019 reflejan en parte el ruido
del tramo (pocas observaciones).

**Limitación:** el 1% de la encuesta tiene pocas observaciones por trimestre y es ruidoso año a
año. Un trimestre (2011T1) de la base cruda local difiere en 0,1% de la usada para los deciles
publicados; los tramos se calcularon con la local.

## 8. Qué falta para cerrar los supuestos abiertos

0. **Subdeclaración de ingresos en todos los deciles.** Hecho para salarios e ingreso mixto
   (sección 5 bis). Falta lo que no tiene dato oficial: rentas de la propiedad de los hogares
   y la Cuenta de generación del ingreso de 2004-2015. Plan original: ajustar el ingreso de la
   EPH a Cuentas Nacionales por fuente, como Gómez Sabaini y Rossignolo: salarios,
   ingreso de cuentapropistas (ingreso mixto), rentas de la propiedad y jubilaciones, cada
   una con su propio factor, aplicado a quien declara esa fuente. Fuente: Cuenta de
   Generación del Ingreso del INDEC (base 2004, publicada desde 2016; para 2004-2015 hay
   que empalmar con series anteriores). Como la subdeclaración de rentas e ingreso mixto es
   mucho mayor que la de salarios registrados y se concentra arriba, se espera que baje la
   tasa de los deciles altos. Sensibilidad adicional para el decil 10: renta de los activos
   externos no declarados del sector privado (Posición de Inversión Internacional, INDEC).
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
5. **Ganancias de sociedades** (2,4% a 3,1% del PIB). No se reparte por deciles: su incidencia es
   incierta (capital, trabajo o precios), sumarlo bien exige sumar también las utilidades al
   ingreso de los dueños (si no, se infla la cima, como pasaba con la Ganancias de personas antes
   de la corrección del 16/11/2026) y no hay datos de propiedad de empresas. Hoy sólo entra en el
   1% de las declaraciones juradas (sección 7 ter). Plan: cuatro variantes (100% capital; 50%
   capital y 50% trabajo; 100% trabajo; 100% precios). Capital: impuesto menos la parte de dueños
   del exterior (inversión extranjera directa, PII del INDEC), más las utilidades (impuesto ÷
   alícuota del año, en `params/`) como ingreso, repartido con el empalme de declaraciones juradas o
   con las rentas de negocios de los anuarios. Trabajo: tasa = recaudación ÷ masa salarial privada
   registrada del país, aplicada a la masa de cada decil como impuesto e ingreso. Precios: por peso
   de consumo privado, como las contribuciones trasladadas. Detalle en `docs/informe.md`,
   "Pendientes".
6. **Evasión de IVA por decil (posible).** Hoy la parte no cobrada del IVA es la misma proporción
   del IVA legal en todos los deciles. Con el lugar de compra de la ENGHo (si lo trae) se puede
   cargar menos IVA a lo comprado en comercios probablemente informales, reescalando a lo recaudado
   (método de Bachas, Gadenne y Jensen). Detalle en `docs/informe.md`, "Pendientes".
7. **Verificaciones de norma pendientes:** alícuotas patronales 2003-2019, INSSJP y obra
   social, y varias reglas de IVA marcadas "no verificado" en el clasificador.
