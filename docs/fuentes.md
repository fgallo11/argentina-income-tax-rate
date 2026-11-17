# Fuentes: qué son, qué aportan y cómo se usan

Glosario de todas las fuentes del proyecto. Para cada una se indica **qué es**, **qué
información aporta**, **cómo se usó** y **dónde** está en el repositorio. Las descargas las
hace `scripts/01_descargar_datos.py` (las URL exactas están ahí); lo transcrito a mano está en
`params/`; el control de cada número contra su fuente, en `docs/trazabilidad_datos.md`. Cómo se combinan, en diagramas: `docs/diagramas.md`.

## Resumen

| Fuente | Quién la produce | Para qué se usa | Entra en el cálculo |
|---|---|---|---|
| [EPH](#eph-encuesta-permanente-de-hogares) | INDEC | Ingresos de cada persona; deciles | Sí, es la base |
| [ENGHo](#engho-encuesta-nacional-de-gastos-de-los-hogares) | INDEC | Cuánto y qué consume cada nivel de ingreso | Sí |
| [Recaudación por impuesto](#recaudación-por-impuesto-dniaf) | DNIAF (Min. de Economía) | Cuánto se cobró de cada impuesto | Sí |
| [Anuarios de estadísticas tributarias](#anuarios-de-estadísticas-tributarias-arca) | ARCA (ex AFIP) | Ingreso, Ganancias y patrimonio declarados por tramo | Sí |
| [Normativa de Ganancias](#normativa-de-ganancias-dniaf) | DNIAF | Escalas y deducciones de cada año | Sí (`params/`) |
| [Normativa de seguridad social](#normativa-de-seguridad-social) | Leyes, decretos, Res. ANSES | Aportes, contribuciones y su tope | Sí (`params/`) |
| [Consumo privado y PIB](#consumo-privado-y-pib-cuentas-nacionales) | INDEC | Escala de los impuestos al consumo; validación | Sí |
| [Cuenta de generación del ingreso](#cuenta-de-generación-del-ingreso-cgi) | INDEC | Total de salarios e ingreso mixto del país | Variante |
| [Posición de inversión internacional](#posición-de-inversión-internacional-pii) | INDEC | Activos externos privados | Variante |
| [Tipo de cambio A 3500](#tipo-de-cambio-comunicación-a-3500) | BCRA | Pasar activos externos a pesos | Variante |
| [Población total](#población-total-banco-mundial) | Banco Mundial | Llevar la encuesta al total del país | Sí |
| [RIPTE](#ripte) | Secretaría de Trabajo | Anualizar sueldos; actualizar ingresos | Sí |
| [Haber mínimo jubilatorio](#haber-mínimo-jubilatorio) | ANSES | Tope de aportes; deducción de jubilados | Sí |
| [Salario mínimo (SMVM)](#salario-mínimo-vital-y-móvil-smvm) | Secretaría de Trabajo | Régimen cedular de Ganancias 2024 | Sí |
| [Índices de precios (IPC)](#índices-de-precios-al-consumidor-ipc) | INDEC y San Luis | Pesos constantes (figura 6b) | Sólo gráficos |
| [Canasta básica total](#canasta-básica-total-cbt) | INDEC | Ingreso medido en canastas | Sólo gráficos |
| [Distribución del ingreso (informe)](#evolución-de-la-distribución-del-ingreso-indec) | INDEC | Validar los deciles | Sólo validación |
| [Argendata / Pessino et al.](#argendata-fundar--pessino-rasteletti-artana-y-lustig) | Fundar; Oxford Open Economics | Comparar; dos supuestos tomados | Comparación |
| [International Tax Observatory](#international-tax-observatory-ito) | Paris School of Economics | Comparar | Comparación |
| [De Rosa, Flores y Morgan](#de-rosa-flores-y-morgan-2024) | World Development | Comparar; multiplicador de rentas | Comparación y variante |
| [Revenue Statistics (OCDE)](#revenue-statistics-in-latin-america-and-the-caribbean-ocde) | OCDE, CEPAL, CIAT, BID | Entender la comparación con el ITO | Comparación |
| [Estudios previos](#estudios-previos-de-incidencia-en-argentina) | CEPAL, CEQ y otros | Comparar | Comparación |

"Variante" quiere decir que sólo se usa en una medida alternativa, no en la principal.
"Comparación": no entra en ningún número del proyecto.

---

## 1. Encuestas a hogares

### EPH (Encuesta Permanente de Hogares)

- **Qué es.** La encuesta trimestral del INDEC sobre empleo e ingresos, en 31 aglomerados
  urbanos (65% de la población del país en 2025). Microdatos por persona y por hogar,
  2003T3-2025T4.
- **Qué aporta.** El ingreso de cada persona por fuente (sueldo, jubilación, cuentapropia,
  rentas, aguinaldo), si es asalariado registrado (tiene descuento jubilatorio), el tamaño del
  hogar y el ingreso per cápita familiar. Es la población del estudio.
- **Cómo se usó.**
  - Ordenar a las personas por ingreso per cápita familiar y armar deciles y percentiles.
  - Simular persona por persona aportes, contribuciones y Ganancias (de neto a bruto), con las
    reglas de cada mes.
  - Corregir el aguinaldo a base devengada.
  - Promediar los trimestres disponibles de cada año (faltan 2007T3, 2015T3-T4 y 2016T1).
- **Dónde.** `data/raw/eph/`, `src/incidencia/eph.py`, `src/incidencia/directos.py`,
  `scripts/04_microsimulacion_eph.py`.
- **Limitaciones.** Sólo aglomerados urbanos; los de más ingresos declaran menos de lo que
  ganan o no responden; 2007-2015 con el INDEC intervenido.

### ENGHo (Encuesta Nacional de Gastos de los Hogares)

- **Qué es.** La encuesta del INDEC sobre qué compra cada hogar, artículo por artículo.
  Ediciones 2004/05, 2012/13 y 2017/18.
- **Qué aporta.** Cuánto gasta cada nivel de ingreso respecto de lo que gana y en qué (alimentos
  exentos de IVA o con alícuota reducida, tabaco, alcohol, autos, telefonía, etc.).
- **Cómo se usó.**
  - A cada decil de la EPH se le asigna el gasto y la canasta de los hogares de la ENGHo con su
    mismo ingreso relativo a la media.
  - Cada artículo se clasifica por su alícuota de IVA y su impuesto interno.
  - Entre ediciones se interpola en el tiempo.
- **Dónde.** `data/raw/engho/`, `scripts/02_procesar_engho.py`, `src/incidencia/clasificador.py`,
  `src/incidencia/indirectos.py`.
- **Limitaciones.** Su veintil más alto es el techo de lo que se observa: por encima, el consumo
  del 1% se extrapola. La última edición es de 2017/18.

---

## 2. Impuestos y normativa

### Recaudación por impuesto (DNIAF)

- **Qué es.** La serie de recaudación nominal, nacional y provincial, de la Dirección Nacional de
  Investigaciones y Análisis Fiscal del Ministerio de Economía, desde 1991, con clasificación
  internacional.
- **Qué aporta.** Cuánto se cobró cada año de cada impuesto: Ganancias de personas y de
  sociedades, Bienes Personales, IVA, internos por rubro, cheque, combustibles, derechos de
  exportación, monotributo, aportes y contribuciones, Ingresos Brutos y el resto de los
  provinciales.
- **Cómo se usó.**
  - El nivel de los impuestos al consumo: lo recaudado por cada peso de consumo privado se
    aplica al consumo de cada decil. Así el estudio cobra lo que efectivamente se recaudó y no
    la alícuota de la ley.
  - La Ganancias que la simulación no capta (recaudado menos simulado) y Bienes Personales.
  - La cobertura del estudio (qué parte de todo lo recaudado entra) y la validación.
- **Dónde.** `data/raw/recaudacion/dniaf_recaudacion_nominal_clasif_internacional.xlsx`,
  `scripts/03_recaudacion_macro.py` → `data/processed/recaudacion_macro.csv`.
- **Nota.** El pipeline baja también otras planillas de la DNIAF y de ARCA (presión tributaria,
  series anuales por impuesto) que hoy no se usan.

### Anuarios de estadísticas tributarias (ARCA)

- **Qué es.** Los anuarios de ARCA (ex AFIP), 2003-2025, con las declaraciones juradas de
  Ganancias de personas humanas agrupadas por tramo de ingresos gravados (años fiscales
  2002-2024).
- **Qué aporta.** Por tramo: cuántas personas declaran, su ingreso (ingresos gravados,
  ganancia neta sujeta a impuesto, resultado neto, rentas exentas), el impuesto determinado y el
  patrimonio neto que declaran en esa misma presentación. Es la única fuente que ve bien a los de
  más ingresos. No se usan las declaraciones de Bienes Personales.
- **Cómo se usó.**
  - Completar la cima de la EPH: donde lo declarado al fisco más supera a la encuesta, se les
    suma a esas personas el ingreso que la encuesta no capta y la Ganancias que pagan por él.
  - Repartir el resto de la Ganancias no simulada y Bienes Personales (este último según el
    patrimonio declarado en Ganancias).
  - Estimar el 1% más rico sólo con declaraciones juradas (figura 7).
  - 2025 usa las declaraciones de 2024 actualizadas (las de 2025 todavía no se publicaron).
- **Dónde.** `data/raw/anuarios_arca/`, `scripts/aux_anuarios_arca.py`,
  `scripts/09_ingresos_altos.py`, `scripts/10_top1.py`.

### Normativa de Ganancias (DNIAF)

- **Qué es.** El documento de la DNIAF "Impuesto a las Ganancias desde el año 2000 al 2025", con
  las escalas, deducciones y regímenes especiales de cada período.
- **Qué aporta.** Las reglas para calcular la Ganancias de un asalariado o jubilado en cada mes:
  mínimo no imponible, cargas de familia, deducción especial, escala, reducción de deducciones
  hasta 2008, Dto. 1242/2013, Ley 27.617, régimen cedular de 10/2023 a 06/2024.
- **Cómo se usó.** Transcrita a `params/ganancias.yaml` y aplicada en la microsimulación. Cada
  número fue buscado en el PDF (`docs/trazabilidad_datos.md`, B).
- **Dónde.** `data/raw/normativa/`, `params/ganancias.yaml`, `src/incidencia/directos.py`.

### Normativa de seguridad social

- **Qué es.** Leyes, decretos y resoluciones de la ANSES: Dto. 814/2001 y modificatorias, Ley
  27.430, Ley 27.541, Dto. 390/2003, Ley 26.222, resoluciones de movilidad, entre otras.
- **Qué aporta.** Alícuotas de aportes (jubilación, INSSJP) y de contribuciones patronales, el
  aporte reducido a las AFJP hasta 2007 y el tope de la base de aportes.
- **Cómo se usó.** Transcrita a `params/seguridad_social.yaml` y `params/lmi.csv` (tope de
  aportes, armado por `scripts/aux_construir_lmi.py` con la serie del haber mínimo y anclas en
  resoluciones). Algunas alícuotas siguen marcadas como no verificadas.
- **Dónde.** `params/`, `src/incidencia/directos.py`.

---

## 3. Cuentas Nacionales y datos macroeconómicos

### Consumo privado y PIB (Cuentas Nacionales)

- **Qué es.** Consumo privado y PIB a precios corrientes, anuales, base 2004 (INDEC; series
  `4.3_DGCP_2004_A_27` y `4.3_OGP_2004_A_17` de datos.gob.ar).
- **Qué aporta.** El total de lo que consumen los hogares del país y el tamaño de la economía.
- **Cómo se usó.** El consumo privado es el denominador de "recaudado por peso de consumo",
  la tasa que se aplica al consumo de cada decil. El PIB, para expresar recaudación y
  cobertura como porcentaje del producto.
- **Dónde.** `data/raw/macro/`, `scripts/03_recaudacion_macro.py`.

### Cuenta de generación del ingreso (CGI)

- **Qué es.** La cuenta del INDEC que reparte el valor agregado entre trabajo asalariado,
  ingreso mixto (cuentapropistas) y excedente, desde 2016.
- **Qué aporta.** Cuánto suman en el país los salarios y el ingreso de los cuentapropistas.
- **Cómo se usó.** Sólo en la variante `ajuste_cn`: se llevan los salarios y el ingreso
  cuentapropista de la EPH al total de Cuentas Nacionales, cada uno con su factor. Para 2004-2015
  se usa la cobertura promedio de 2016-2018.
- **Dónde.** `data/raw/macro/serie_cgi_10_26.xls`, `scripts/aux_cuentas_nacionales.py`.

### Posición de inversión internacional (PII)

- **Qué es.** El cuadro del INDEC con los activos y pasivos externos del país (cuadro 18, "otros
  sectores").
- **Qué aporta.** Cuántos activos en el exterior tiene el sector privado: inversión de cartera,
  moneda y depósitos.
- **Cómo se usó.** Sólo en las variantes con activos externos: se les supone una renta del 3%
  anual no declarada y se reparte como la Ganancias faltante (casi todo arriba). Es una cota
  alta.
- **Dónde.** `data/raw/macro/cin_II_2026.xls`, `scripts/aux_cuentas_nacionales.py`.

### Tipo de cambio (Comunicación A 3500)

- **Qué es.** El tipo de cambio mayorista de referencia del BCRA (serie `168.1_T_CAMBI500_D_0_0_17`).
- **Qué aporta.** El promedio anual de pesos por dólar.
- **Cómo se usó.** Para pasar a pesos los activos externos de la PII.

### Población total (Banco Mundial)

- **Qué es.** La población total de Argentina por año (indicador `SP.POP.TOTL`).
- **Qué aporta.** Cuántas personas tiene el país, no sólo los aglomerados de la EPH.
- **Cómo se usó.** Para pasar lo recaudado en todo el país a la escala de la encuesta ("por
  habitante", en la corrección de ingresos altos) y para la validación. No es la proyección del
  INDEC; difieren poco.
- **Dónde.** `data/raw/macro/poblacion_total_wb.json`, `scripts/03_recaudacion_macro.py`.

---

## 4. Salarios, precios y canastas

### RIPTE

- **Qué es.** La remuneración imponible promedio de los trabajadores estables, mensual
  (Secretaría de Trabajo).
- **Qué aporta.** Cómo evolucionan los sueldos registrados mes a mes.
- **Cómo se usó.** Para anualizar el sueldo mensual de la EPH al calcular Ganancias (que es
  anual) y para actualizar ingresos en el contrafáctico de población fija.

### Haber mínimo jubilatorio

- **Qué es.** El haber mínimo de la ANSES, mensual (serie `58.1_MP_0_M_13`).
- **Qué aporta.** La referencia de la movilidad previsional.
- **Cómo se usó.** Para encadenar el tope de la base de aportes entre resoluciones y para la
  deducción de jubilados en Ganancias (6 u 8 veces el haber mínimo, según el año).

### Salario mínimo, vital y móvil (SMVM)

- **Qué es.** El salario mínimo mensual (serie `57.1_SMVMM_0_M_34`).
- **Qué aporta.** Su valor en cada mes.
- **Cómo se usó.** Para el régimen cedular de Ganancias de 2024, definido en múltiplos del SMVM.

### Índices de precios al consumidor (IPC)

- **Qué es.** El IPC-GBA del INDEC hasta 2006, el IPC de San Luis para 2007-2016 (por la
  intervención del INDEC) y el IPC Nacional del INDEC desde 2017.
- **Qué aporta.** Cuánto subieron los precios.
- **Cómo se usó.** Sólo para expresar ingresos en pesos de hoy (figura 6b) y para llevar hacia
  atrás la canasta básica antes de 2017.
- **Dónde.** `scripts/aux_deflactor.py`.

### Canasta básica total (CBT)

- **Qué es.** El costo mensual de la canasta básica total por adulto equivalente en el Gran
  Buenos Aires (INDEC; serie oficial desde 04/2016). Define la línea de pobreza.
- **Qué aporta.** Un umbral de "lo necesario para no ser pobre" que se actualiza solo con los
  precios.
- **Cómo se usó.** Para medir el ingreso de cada grupo en canastas (figura 6, gráfico de
  canastas del informe). Antes de 2017 se usa la de 2017 llevada hacia atrás con el IPC.

---

## 5. Validación

### Evolución de la distribución del ingreso (INDEC)

- **Qué es.** El informe trimestral del INDEC con los deciles de ingreso per cápita familiar.
- **Qué aporta.** Los ingresos medios y los límites de cada decil, la media y la población.
- **Cómo se usó.** Para controlar que los deciles del proyecto coinciden con los oficiales:
  coinciden los diez deciles del cuarto trimestre de 2024 (`docs/metodologia.md`, sección 10).

---

## 6. Estudios usados para comparar

Ninguno entra en los números del proyecto. Sus datos están en `data/externos/`, con su
README.

### Argendata (Fundar) / Pessino, Rasteletti, Artana y Lustig

- **Qué es.** *Distributional effects of taxation in Latin America* (Oxford Open Economics, vol.
  4), con datos de 2018 para Argentina, publicado por Fundar en su plataforma Argendata. El
  paper está en `papers/`.
- **Qué aporta.** La tasa efectiva de cada decil en 2018, abierta en cinco tipos de impuesto
  (seguridad social, en cascada, Ganancias de personas y sociedades, IVA, otros indirectos).
- **Cómo se usó.**
  - Comparación de la sección 1 del informe y de `docs/validacion.md`, sección 3.
  - Dos supuestos tomados como variantes: los bienes exentos de IVA cargan 20% de la alícuota
    por sus insumos (`iva_exentos_20`) y el cheque como impuesto en cascada (`con_cheque`).
- **Dónde.** `data/externos/argendata_presion_por_decil_2018.csv`.

### International Tax Observatory (ITO)

- **Qué es.** El informe n.° 10 del observatorio de la Paris School of Economics, *Tax
  Progressivity and Inequality: Minimum Taxation of High-Net-Worth Individuals in Latin America
  and the Caribbean* (abril 2026), y su nota sobre Argentina (con la Friedrich Ebert Stiftung).
- **Qué aporta.** La tasa efectiva de cuatro grupos (50% más pobre, 40% medio, 10% y 1% más
  ricos) por tipo de impuesto, por hogar y con ingreso de Cuentas Nacionales. No dice el año;
  sus fuentes llegan a 2019.
- **Cómo se usó.** Comparación de la sección 1 del informe. Su categoría "patrimonio" incluye el
  impuesto al cheque (ver la fuente de la OCDE más abajo).
- **Dónde.** `data/externos/ito_2026_argentina.csv` (totales del texto; composición leída del
  gráfico, aproximada).

### De Rosa, Flores y Morgan (2024)

- **Qué es.** *More unequal or not as rich? Revisiting the Latin American exception* (World
  Development, vol. 184). Distribución del ingreso nacional y de los impuestos en diez países de
  América Latina. Es la base de los números del ITO. El paper está en `papers/`.
- **Qué aporta.** Que las encuestas captan entre un quinto y un décimo de las rentas del capital
  de Cuentas Nacionales, y cómo se reparten los impuestos por tipo (Argentina 2019).
- **Cómo se usó.**
  - El multiplicador de rentas (×7, punto medio de su rango) de la variante
    `ajuste_cn_rentas`.
  - Entender de dónde salen las cifras del ITO.

### Revenue Statistics in Latin America and the Caribbean (OCDE)

- **Qué es.** La base de recaudación comparable entre países de la OCDE, la CEPAL, el CIAT y el
  BID, con clasificación internacional de impuestos. Consultada por DBnomics (serie
  `DSD_REV_LAC@DF_REVARG`).
- **Qué aporta.** Qué impuesto argentino cae en cada categoría internacional y cuánto recauda.
- **Cómo se usó.** Para verificar que el "patrimonio" del ITO incluye el cheque: en 2019,
  impuestos a la propiedad 2,61% del PIB, de los cuales cheque 1,62, sellos 0,41, inmobiliario
  0,41 y Bienes Personales 0,14 (`docs/metodologia.md`, sección 15).

### Estudios previos de incidencia en Argentina

- **Qué es.** Santiere, Gómez Sabaini y Rossignolo (CEPAL, datos 1997); Gómez Sabaini, Harriague
  y Rossignolo (2008); Gaggero y Rossignolo (CEFID-AR, 2010); Rossignolo (CEQ, 2012/13), entre
  otros.
- **Qué aporta.** Tasas por decil de otros años y métodos.
- **Cómo se usó.** Comparación en `docs/validacion.md`, sección 2. Detalle de cada uno, con
  página y lo que no se pudo verificar, en `docs/literatura_previa.md`.

---

## 7. Métodos tomados de la literatura

No son datos, sino formas de hacer la cuenta que vienen de otros trabajos:

| Qué | De dónde | Dónde se usa |
|---|---|---|
| Asignar impuestos al consumo según el ingreso relativo y comparar contra el ingreso | Manual del Commitment to Equity (CEQ), Lustig (ed.) | Toda la medida principal; variante `recursos_gasto` |
| Estimar el 1% más rico con declaraciones juradas por tramo | Alvaredo (2010) | `scripts/10_top1.py` |
| Rentas de encuesta × 7 | De Rosa, Flores y Morgan (2024) | Variante `ajuste_cn_rentas` |
| Bienes exentos cargan 20% del IVA; cheque en cascada | Pessino et al. | Variantes `iva_exentos_20`, `con_cheque` |
| Evasión de IVA según el lugar de compra | Bachas, Gadenne y Jensen | Pendiente (`docs/metodologia.md`, sección 14) |
