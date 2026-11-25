# Quién paga impuestos en Argentina, 2004-2025

*Borrador de una nueva versión del informe, en paralelo a [informe.md](informe.md). Los gráficos se
generan con `scripts/14_informe_v2_graficos.py` y están en `outputs/figures/informe_v2/`.*

Este informe estima qué parte de su ingreso paga en impuestos cada grupo de la población argentina,
año por año entre 2004 y 2025. La medida es la **tasa efectiva**: lo que un grupo paga en
impuestos dividido por su ingreso. No es la alícuota que fija la ley, sino lo que efectivamente
pagan sus miembros sumando todos los impuestos que alcanzan.

El recorrido es el siguiente. Primero se compara el resultado con los dos estudios más citados
sobre el tema (sección 1). Después se presenta la tasa de cada decil con los datos más firmes del
proyecto (sección 2). La sección 3 muestra por qué los deciles no alcanzan para ver a quienes más
ganan, y la 4 parte el decil 10 y explica cómo se completa el ingreso que las encuestas no captan.
Con ese grupo separado, la sección 5 vuelve a mirar la evolución en el tiempo, la 6 compara el
sistema con uno proporcional y uno progresivo, y la 7 resume la distancia entre los de arriba y
los de abajo.

## 1. Lo que muestran otros estudios

![Figura 1](../outputs/figures/informe_v2/f01_comparacion.png)

**Figura 1.** El gráfico de siempre: tres estudios, el mismo perfil por deciles.

La forma habitual de mostrar quién paga impuestos es una barra por decil con la parte de su
ingreso que se va en impuestos. La figura 1 pone lado a lado los dos estudios más citados para
Argentina y este:

- **A. Argendata (Fundar)**, con datos de Pessino, Rasteletti, Artana y Lustig, para 2018: el decil 1
  paga 35,8% y el decil 10, 24,9%.
- **B. Este estudio**, mismo año: el decil 1 paga 33,6% y el decil 10, 24,0%.
- **C. International Tax Observatory (ITO)**, informe de abril de 2026. No usa deciles sino cuatro
  grupos: el 50% más pobre paga 37%, el 40% del medio 29%, el 10% más rico 25% y el 1% más rico
  alrededor de 30%. Al lado, este estudio con los mismos cuatro grupos en 2019: 25,3%, 23,6%, 23,3% y
  21,8%.

Los tres estudios coinciden en la forma de la parte de abajo: el 10% más pobre paga la proporción
más alta de su ingreso. Los niveles difieren porque cada estudio suma impuestos distintos y mide el
ingreso de otra forma:

| | Argendata | ITO | Este estudio |
|---|---|---|---|
| Año | 2018 | no lo dice (sus fuentes llegan a 2019) | 2004 a 2025, cada año |
| Unidad | personas | hogares | personas |
| Ingreso | encuesta | Cuentas Nacionales (más alto que la encuesta) | encuesta, completada arriba con las declaraciones juradas |
| Impuesto al cheque | sí (como impuesto "en cascada") | sí, dentro de "patrimonio", cargado arriba | como variante, cargado a precios (raya negra en B) |
| Ganancias de sociedades | sí | sí | no |
| Impuestos al patrimonio | no | sí | Bienes Personales |

Con el impuesto al cheque, este estudio queda casi igual a Argendata en las dos puntas (2018: decil
1, 37,1% contra 35,8%; decil 10, 25,0% contra 24,9%). En el IVA las dos estimaciones coinciden casi
decil por decil (decil 1: 16,7 contra 16,5 puntos; decil 5: 8,8 contra 8,8). Las diferencias que
quedan vienen de "otros impuestos indirectos" que Argendata suma (probablemente derechos de
importación y combustibles, entre otros) y de que reparte Ganancias de sociedades entre todos los
deciles.

Con el ITO, la diferencia está en las puntas. Abajo, el ITO le carga al 50% más pobre unos 30
puntos de impuestos al consumo, contra unos 18 de este estudio; no pudimos verificar de dónde sale
esa diferencia. Arriba, el 1% del ITO llega a 30% porque suma Ganancias de sociedades (unos 8
puntos) y bastante patrimonio (unos 9); este estudio no reparte el impuesto de sociedades.

El "patrimonio" del ITO no es sólo Bienes Personales. Sigue la clasificación internacional de la
OCDE, en la que "impuestos a la propiedad" incluye el impuesto al cheque. En 2019 esa categoría sumó
2,6% del PIB: cheque 1,6, sellos 0,4, inmobiliario 0,4 y Bienes Personales 0,14. El ITO la reparte
pesando más arriba; este estudio carga el cheque a los precios, donde pesa más abajo. Es la
diferencia de supuestos más importante en la cima y no está resuelta: parte del cheque la pagan
quienes consumen y parte quienes más mueven dinero en los bancos (`docs/metodologia.md`, sección 15).

## 2. Qué parte de su ingreso paga cada decil

### Qué se mide

**La población.** Las personas que viven en los aglomerados urbanos que releva la Encuesta
Permanente de Hogares (EPH) del INDEC: 65% de la población del país en 2025. La EPH es una encuesta
trimestral que pregunta a cada miembro del hogar cuánto ganó y de qué fuentes. El dato de cada año
es el promedio de sus trimestres.

**Cómo se ordena.** Cada persona tiene el ingreso per cápita familiar de su hogar: el ingreso de
todos sus miembros dividido por la cantidad de miembros. Se ordena a la población de menor a mayor
según ese ingreso y se la divide en diez grupos del mismo tamaño, los **deciles**. El decil 1 es el
10% de menores ingresos; el decil 10, el 10% de mayores ingresos.

**El ingreso (el denominador).** El que declara cada persona en la encuesta, llevado a antes de
impuestos directos: al ingreso de bolsillo se le suman los aportes personales, la Ganancias
retenida y la parte de las contribuciones patronales que recae sobre el trabajador. En la cima,
este ingreso se completa con el que se declara a ARCA y la encuesta no capta; cómo se hace se
explica en la sección 4.

**Los impuestos (el numerador).** Se incluyen siete, que suman entre 56% y 71% de todo lo que
recaudó el país según el año (70% en 2025). Para cada uno hay que decidir quién lo paga, y la
decisión no siempre es quien lo deposita:

- **Aportes personales** (jubilación y PAMI). Se calculan persona por persona para cada asalariado
  registrado de la encuesta, con las alícuotas y topes de cada mes.
- **Contribuciones patronales.** Las deposita el empleador, pero su costo se reparte: la mitad recae
  en el trabajador, que cobra un salario menor, y la mitad en los consumidores, a través de los
  precios. La primera mitad se carga a cada asalariado registrado; la segunda, a cada decil según
  su consumo.
- **Ganancias de personas.** Se simula con la ley de cada año para asalariados registrados y
  jubilados. La encuesta no capta bien a quienes pagan Ganancias por otras rentas; la diferencia
  con lo recaudado se completa con las declaraciones juradas (sección 4).
- **Bienes Personales.** Se reparte según el patrimonio declarado en las declaraciones juradas, que
  se concentra en el decil 10.
- **IVA, Internos e Ingresos Brutos.** Se pagan al comprar, así que para saber cuánto paga cada
    decil hace falta saber cuánto consume. El cálculo tiene tres pasos.
    1. *Cuánto se cobra por cada peso que se consume.* Se toma lo que el Estado recaudó en el año con
    estos tres impuestos, según la Dirección Nacional de Investigaciones y Análisis Fiscal del
    Ministerio de Economía, y se lo divide por todo lo que consumieron los hogares del país, según
    las Cuentas Nacionales del INDEC. En 2025 se cobraron $16,2 por cada $100 de consumo ($10,2 de
    IVA, $5,5 de Ingresos Brutos y el resto de Internos).
    2. *Cuánto consume cada decil.* La EPH pregunta cuánto gana cada persona, pero no cuánto gasta.
    Ese dato sale de otra encuesta del INDEC, la Encuesta Nacional de Gastos de los Hogares (ENGHo,
    ediciones 2004/05, 2012/13 y 2017/18), que pregunta las dos cosas. De la ENGHo se toma cuánto
    consumen los hogares de cada nivel de ingreso, y eso se aplica al decil de la EPH que está en
    el mismo nivel.
    3. *Cuánto paga cada decil.* Su consumo multiplicado por lo que se cobra por peso. En el IVA se
    ajusta además según qué compra cada decil, porque unos productos pagan 21%, otros 10,5% y otros
    están exentos.

    Como el punto de partida es lo que efectivamente se recaudó y no la alícuota de la ley, no se
    cuenta como pagado el impuesto que se evade.

Quedan afuera Ganancias de sociedades, retenciones a la exportación, impuesto al cheque,
combustibles, monotributo, impuestos provinciales distintos de Ingresos Brutos y tasas municipales.
Ganancias de sociedades queda afuera porque no se sabe quién la paga (los dueños, los trabajadores
o los consumidores) ni hay datos de quién es dueño de qué empresa. El cheque, los combustibles y el
monotributo se calcularon como variantes y no cambian la forma de los resultados.

![Figura 2](../outputs/figures/informe_v2/f02_deciles_2025.png)

**Figura 2.** Qué parte de su ingreso pagó cada decil en impuestos, 2025.

La figura 2 muestra el resultado para 2025. Cada barra es un decil; su altura es la tasa efectiva y
los colores separan los impuestos. La línea punteada es la tasa de toda la población, 23,8%.

El decil 1 paga 28,7% de su ingreso, cinco puntos más que el promedio. Del decil 2 al 10 la tasa es
casi la misma: entre 23,0% y 23,8%. Lo que cambia entre deciles es con qué se paga. En el decil 1,
26,8 de los 28,7 puntos son impuestos al consumo: IVA, Ingresos Brutos, Internos y la mitad de las
contribuciones que pasa a precios. Ese peso se explica porque el consumo estimado del decil 1 es
1,4 veces el ingreso que declara en la EPH, y paga los impuestos al consumo sobre todo ese consumo
Hacia arriba el consumo pesa menos y los aportes y
contribuciones más. El decil 10 es el único con una parte importante de Ganancias y Bienes
Personales (7,9 puntos).

Ese resultado del decil 1 requiere una aclaración. En los deciles de menores ingresos, el consumo
que se estima con la ENGHo es mayor que el ingreso que los hogares declaran en la EPH. En 2025 ocurre
en los deciles 1 y 2: el consumo del decil 1 equivale a 1,43 veces su ingreso declarado y el del
decil 2, a 1,03 veces. En 2004 ocurría en los deciles 1 a 5. Es un rasgo conocido de las encuestas de
hogares en los sectores de menores ingresos, y responde a varias fuentes: la ayuda de familiares y de
la comunidad, el consumo financiado con deudas e ingresos que la encuesta no llega a registrar. Las
encuestas disponibles no permiten separar cuánto corresponde a cada una.

El estudio no trata esa diferencia como ingreso de los hogares. No hay forma de verificarla, y
atribuir a los hogares más vulnerables una capacidad económica que no declaran iría más allá de lo
que los datos sostienen. La tasa del decil 1 se expresa entonces sobre el ingreso que declara, y debe
leerse así: incluye los impuestos que se pagan al consumir bienes financiados con esos otros
recursos. Incluir esos recursos como ingreso podría alterar la lectura de la regresividad del
sistema en la base, porque la carga del decil 1 resultaría menor. Como no pueden medirse ni
verificarse por separado, el estudio no lo hace.

### Los años de cambio de gobierno

![Figura 3](../outputs/figures/informe_v2/f03_deciles_anios_gobierno.png)

**Figura 3.** Qué parte de su ingreso pagó cada decil, en los años de cambio de gobierno.

La figura 3 repite el cálculo en siete años. Los mandatos presidenciales empiezan el 10 de
diciembre, así que el último año de un gobierno es también el punto de partida del siguiente: 2007
(fin del mandato de Néstor Kirchner), 2011 y 2015 (fin de los dos mandatos de Cristina Fernández de
Kirchner), 2019 (Mauricio Macri) y 2023 (Alberto Fernández). Se agregan 2004, el primer año de la
serie, y 2025, el último dato disponible, en el segundo año de Javier Milei.

Tres rasgos se repiten en los siete años. El decil 1 paga más que todos los demás. Entre los
deciles 2 a 9 la tasa difiere en menos de 3,5 puntos (0,8 en 2025). Y el decil 10 queda cerca de los deciles medios, por encima de ellos
en los años en que Ganancias y Bienes Personales pesan más (2011, 2015 y 2023) y a la par en los
demás. Lo que cambia es el nivel: la tasa promedio pasó de 23,0% en 2004 a 28,8% en 2015, bajó a
24,0% en 2019, subió a 26,8% en 2023 y volvió a 23,8% en 2025. La distancia del decil 1 al resto se
achicó: pagaba 12,5 puntos más que el promedio en 2004 y 4,9 en 2025.

### Con qué impuestos paga cada decil

![Figura 4](../outputs/figures/informe_v2/f04_composicion_deciles.png)

**Figura 4.** Con qué impuestos paga cada decil, año por año.

La figura 4 sigue a cuatro deciles a lo largo de los 22 años: el 1, el 4, el 7 y el 10. Cada panel
apila, año por año, los puntos de ingreso que el decil paga en cada impuesto; la línea negra es el
total.

En el decil 1 casi todo es consumo. Su tasa bajó de 35,5% en 2004 a 28,7% en 2025, y la baja vino
sobre todo del IVA (de 20,4 a 14,5 puntos): en 2004 el decil gastaba 2,2 veces lo que declaraba
ganar y en 2025, 1,4 veces. En los deciles 4 y 7 se suman los aportes y contribuciones del salario
registrado, que crecen hacia arriba, y la tasa total se mantuvo entre 22% y 28% en toda la serie.
El decil 10 es el único en el que Ganancias y Bienes Personales tienen un peso propio, y su tasa sube
y baja con ellos: fue 23,8% en 2004 y en 2025, y llegó a 32,5% en 2013.

## 3. Por qué los deciles ocultan a quienes más ganan

Los deciles reparten a la población en diez grupos del mismo tamaño. Eso sirve para describir a la
mayoría, pero tiene una consecuencia: los grupos tienen la misma cantidad de personas, no el mismo
nivel de vida, y la distancia entre el primero y el último de cada grupo es muy distinta. Esta
sección mide esa distancia.

![Figura 5](../outputs/figures/informe_v2/f05_canastas.png)

**Figura 5.** Ingreso de cada grupo en canastas básicas por adulto equivalente, 2004 y 2025.

La figura 5 mide el ingreso de cada grupo con la misma unidad con que el INDEC mide la pobreza. La
**canasta básica total** es el valor de los bienes y servicios que el INDEC considera necesarios para
que un adulto no sea pobre; se publica todos los meses para el Gran Buenos Aires (antes de 2017,
este estudio usa la de 2017 llevada hacia atrás con el índice de precios). Las necesidades de cada
persona se ponderan con la tabla de **adultos equivalentes** del INDEC, que asigna a cada persona un
peso según su edad y sexo. El ingreso del grupo dividido por sus adultos equivalentes y por la
canasta dice cuántas canastas por mes puede cubrir el grupo promedio: debajo de 1 (línea
punteada), es pobre. Medir en canastas, además, permite comparar años distintos sin que la
inflación distorsione.

En 2025, los deciles 1 a 3 están debajo de la línea de pobreza (0,36, 0,69 y 0,93 canastas); en
2004 eran cinco deciles. El decil 5 tiene 1,45 canastas y el decil 9, 3,6. En el decil 10, en
cambio, conviven situaciones muy distintas: el decil entero promedia 8,8 canastas, pero los
percentiles 90 a 95 tienen 5,2, los percentiles 95 a 99, 9,1, y el 1% más rico, 24,5. Dentro de la
última barra hay casi cinco veces de distancia entre el primer tramo y el último; entre el decil 1
y el decil 5 hay cuatro.

![Figura 6](../outputs/figures/informe_v2/f06_canastas_tiempo.png)

**Figura 6.** Ingreso de cada decil y del 1% más rico en canastas básicas, 2004-2025.

La figura 6 sigue el mismo indicador para cada decil y para el 1% más rico en todos los años. El
eje vertical es logarítmico: cada marca multiplica a la anterior, lo que permite ver en el mismo
gráfico al decil 1 (menos de media canasta) y al 1% más rico (más de veinte).

Para marcar dónde empieza la clase alta hace falta un criterio, y no hay uno oficial en Argentina.
Se usa el de la OCDE (*Under Pressure: The Squeezed Middle Class*, 2019): clase alta es quien tiene
más del doble del ingreso mediano, es decir, del ingreso de la persona que está justo en el medio
de la distribución. Como este estudio trabaja con promedios por grupo, la mediana se aproxima con el
promedio de los deciles 5 y 6. En 2025 el límite queda en 3,2 canastas por adulto equivalente (1,9
en 2004). Es un límite relativo: se mueve con el ingreso del medio.

Con ese criterio, la clase alta incluye al decil 10 entero y a buena parte del decil 9, cuyo
promedio (3,6 canastas en 2025) está apenas por encima del límite. El decil 8 queda debajo. La
línea del 1% más rico, en cambio, está entre 17 y 31 canastas en toda la serie, muy lejos del resto
del decil 10 (entre 6 y 10).

![Figura 7](../outputs/figures/informe_v2/f07_parte_ingreso.png)

**Figura 7.** Qué parte del ingreso total tiene cada grupo, 2025.

La figura 7 muestra la misma desigualdad en términos de ingreso total. Cada barra es la parte del
ingreso de toda la población que recibe el grupo; la raya negra, la parte de la población que es el
grupo. Si el ingreso estuviera repartido en partes iguales, cada barra llegaría a su raya.

El decil 10 recibe 37,6% del ingreso total con el 10% de la población. Partido, los percentiles
90-95 (5% de la población) reciben 11,1%; los 95-99 (4%), 15,7%; y el 1% más rico, 10,8%, más que
los deciles 1, 2 y 3 juntos (8,2%).

Las tres figuras muestran lo mismo desde ángulos distintos. Un gráfico por deciles dedica nueve
barras a la mitad de abajo y a los sectores medios, y reúne en una sola al 10% de mayores ingresos,
que tiene más de un tercio del ingreso y adentro diferencias mayores que las que hay entre los
primeros cinco deciles. Para saber qué pagan quienes más ganan, hay que partir esa barra.

## 4. El decil 10, partido

### Cómo se parte

Dentro del decil 10, las personas se ordenan con el mismo criterio que en los deciles, por ingreso
per cápita familiar, y se cortan en los percentiles 95 y 99. Quedan tres grupos: los percentiles
90-95 (5% de la población), los 95-99 (4%) y el 1% de mayores ingresos.

Partir el decil 10 tiene un problema que en los deciles de abajo es menor. Sabemos bastante bien
cuánto se paga, porque los impuestos se pueden reconstruir con la recaudación y con las
declaraciones juradas. Lo que no sabemos bien es cuánto ganan los de arriba, porque la encuesta lo
subestima. Quienes más ganan declaran menos de lo que ganan o no responden, y la parte de su
ingreso que más se pierde (rentas del capital, ganancias de empresas, activos en el exterior) es la
más difícil de captar con una encuesta. Por eso el decil 10 partido se presenta en dos versiones.
La **versión A** completa el ingreso de la cima sólo con datos administrativos. La **versión B**
agrega estimaciones de lo que ninguna fuente registra persona por persona.

### Versión A: con los mismos datos que los deciles

![Figura 8](../outputs/figures/informe_v2/f08_version_a.png)

**Figura 8.** Versión A: el decil 10 partido en tres, con los mismos datos que los deciles, 2025.

La versión A usa exactamente la misma información que la figura 2. La diferencia es sólo que el
decil 10 se muestra también separado en sus tres tramos (fondo celeste).

El ingreso y la Ganancias de la cima se completan con las **declaraciones juradas de Ganancias**.
ARCA publica cada año, en sus anuarios de estadísticas tributarias, cuántos contribuyentes declaran
en cada tramo de ingresos, cuánto ingreso declaran y cuánto impuesto pagan. El procedimiento es el
siguiente:

1. Se ordenan las declaraciones juradas de mayor a menor ingreso y se comparan con las personas de
   mayor ingreso de la encuesta, expandida a la población del país.
2. Se busca el punto en que el ingreso declarado al fisco empieza a superar al de la encuesta.
   De ahí para arriba, a cada persona de la encuesta se le suma el ingreso que declara a ARCA y la
   encuesta no registra (incluidas sus rentas exentas) y la Ganancias que paga por ese ingreso.
   Se suman a la vez el ingreso y el impuesto; sumar sólo el impuesto inflaría la tasa.
3. La parte de la Ganancias recaudada que no corresponde a esas personas se reparte entre los
   demás que presentan declaración jurada. Bienes Personales se reparte según la parte del
   patrimonio declarado que tiene cada grupo.

El resultado se puede verificar: con esta corrección, la Ganancias que paga el 1% de la encuesta,
como parte de su ingreso, coincide con la que surge de las declaraciones juradas del 1% de mayores
ingresos (12,0% contra 11,7% en 2024). Para 2025 todavía no hay declaraciones publicadas y se usan
las de 2024, actualizadas con la variación del ingreso del decil 10 de la encuesta.

Partir el decil 10 cambia también un cálculo. En la figura 2 el consumo del decil 10 sale del
promedio de ese decil en la ENGHo. Partido, el consumo se estima tramo por tramo, y por encima del 5%
de mayores ingresos la ENGHo no tiene datos (ver la segunda limitación, más abajo). Con esa
estimación más detallada el decil 10 completo paga 23,4% en lugar de 23,8%, y el promedio de la
población, 23,6% en lugar de 23,8%. Desde aquí, todas las cifras usan este cálculo.

Con la versión A, en 2025 el decil 10 paga 23,4% y sus tramos 24,6% (percentiles 90-95), 23,7%
(95-99) y 21,7% (el 1%). La tasa baja hacia la cima: el 1% más rico paga menos que el promedio
(23,6%) y menos que cualquier decil. También cambia con qué paga cada tramo. Los percentiles 90-95
pagan sobre todo aportes, contribuciones y consumo, con poca Ganancias: su composición se parece a la
del decil 9. En el 1%, Ganancias y Bienes Personales son 14,2 de sus 21,7 puntos. Los aportes pesan
poco porque tienen tope, y el consumo pesa poco porque se supone que, por encima del 5% de mayores
ingresos, el consumo no sigue creciendo con el ingreso (ver la segunda limitación).

La versión A tiene tres limitaciones, todas en la cima:

- **El ingreso sigue incompleto.** Las declaraciones juradas sólo registran lo que se declara al
  fisco. Las Cuentas Nacionales del INDEC, que miden el ingreso total del país, muestran que en 2025
  la encuesta capta el 80% de los sueldos y el 66% del ingreso de los cuentapropistas y pequeños
  empleadores. Para las rentas del capital no hay un total oficial con qué comparar. Si el ingreso
  que falta está concentrado arriba, la tasa de la versión A sobreestima lo que paga la cima.
- **El consumo de arriba es un supuesto.** La ENGHo informa el consumo hasta el 5% de mayores
  ingresos, no más arriba. La versión A deja fijo el consumo en el nivel de ese 5%: quienes ganan
  más no consumen más. Con ese supuesto el 1% gasta 36% de su ingreso. Si en cambio se supone que
  gasta la misma proporción de su ingreso que ese 5% (58%), su tasa sube de 21,7% a 23,6%, la
  misma que los deciles medios.
- **Pocas observaciones.** El 1% de la encuesta son pocas personas por trimestre, y su tasa salta de
  un año a otro en parte por azar.

### Versión B: completando el ingreso que la encuesta no capta

![Figura 9](../outputs/figures/informe_v2/f09_version_b.png)

**Figura 9.** Versión B: los mismos impuestos, con el ingreso que la encuesta no capta estimado,
2025.

La versión B responde a la primera limitación. Mantiene los impuestos de la versión A y agrega al
ingreso una estimación de lo que la encuesta no registra. Esa estimación tiene tres partes, y cada
una se apoya en una fuente distinta:

| Qué se suma | De dónde sale | Qué es dato y qué es supuesto |
|---|---|---|
| Sueldos e ingreso de cuentapropistas que faltan en la encuesta | Cuenta de generación del ingreso de las Cuentas Nacionales (INDEC), que mide el total del país | El faltante total es un dato. Repartirlo en proporción a lo que cada persona ya declara es un supuesto |
| Rentas del capital (alquileres, intereses, utilidades) | Las rentas declaradas en la encuesta se multiplican por 7. Las encuestas latinoamericanas captan entre un quinto y un décimo de esas rentas (De Rosa, Flores y Morgan, 2024) | Supuesto: el INDEC no publica el total de rentas de los hogares |
| Renta de los activos financieros privados en el exterior | 4% anual sobre las acciones y bonos que el sector privado tiene afuera, según la Posición de inversión internacional del INDEC, atribuido al 1% más rico | Supuesto: que esa cartera es de la cima y que su renta no se declara |

La tercera parte necesita una justificación propia. De los US$378.000 millones que el sector privado
tiene afuera según el INDEC (2025), US$260.000 millones son moneda y depósitos, en su mayoría
dólares fuera del sistema que no generan renta y que están repartidos entre buena parte de la
población. Esos se dejan afuera. Las acciones y bonos (US$118.000 millones) sí generan renta, y es
plausible que pertenezcan a la cima: en Bienes Personales declaran tener bienes en el exterior unas
87.000 personas (ARCA, año fiscal 2023), alrededor del 0,2% de la población. El 4% combina
dividendos (alrededor de 2%) y cupones de bonos (3% a 4%); con 3% o 5% el resultado casi no cambia.

La carga total de la población se mantiene igual que en la versión A. Lo que cambia es quién la
soporta en proporción a su ingreso: los grupos cuyo ingreso crece más con la estimación pasan a
tener una tasa menor, y los demás una mayor.

Con la versión B, en 2025 el decil 10 baja de 23,4% a 22,0% y queda por debajo de todos los demás
deciles. Partido, los percentiles 90-95 pagan 24,0%, los 95-99, 23,4%, y el 1% más rico, 18,5% (20,0%
sin la renta de la cartera externa, rayas grises). El decil 1 sube de 28,7% a 31,5%: su ingreso
crece menos que el del resto con la estimación y, como la carga total es la misma, le toca una
parte mayor.

La versión B tiene sus propias limitaciones. El multiplicador de 7 sale de estudios sobre otros
países de la región. Lo que se declara en Bienes Personales como bienes en el exterior es alrededor
del 5% de lo que el INDEC estima que hay afuera, así que la atribución de la cartera al 1% no se
puede verificar persona por persona. Y la Posición de inversión internacional incluye también a
empresas, no sólo a hogares.

### Qué medida se usa en adelante

Para 2025, el 1% más rico paga 21,7% de su ingreso con la versión A y 18,5% con la versión B. Hay
una tercera forma de medirlo, que no usa la encuesta: armar el 1% sólo con las declaraciones
juradas de Ganancias. Las tres coinciden en lo que surge de un mismo dato, la Ganancias (12,4% del
ingreso en la encuesta completada y 11,7% en las declaraciones juradas), y se separan en lo demás:

| Medida | 1% más rico, 2025 | Qué sale de datos | Qué se supone |
|---|---|---|---|
| A. Encuesta completada con declaraciones juradas | 21,7% | Ingreso de la encuesta, ingreso y Ganancias declarados a ARCA, recaudación | El consumo por encima del percentil 95 |
| B. A más el ingreso estimado | 18,5% | Lo mismo que A y el total de sueldos de las Cuentas Nacionales | Rentas ×7, reparto del faltante, renta de la cartera externa |
| Sólo declaraciones juradas | 28,6% | Ingreso, Ganancias y patrimonio declarados | Que la mitad del ingreso es sueldo y que gasta como el 5% más rico de la ENGHo, de donde salen aportes y consumo |

La tercera medida queda más arriba porque no puede medir los aportes ni el consumo y los supone:
le asigna al 1% el doble de aportes y más del doble de impuestos al consumo que los que la encuesta
mide para el 1% que releva. Por eso se descarta.

De aquí en adelante se usa la **versión A**, por dos razones. La primera es que todos sus
componentes salvo el consumo de la cima salen de fuentes observadas, mientras que la versión B
depende de un multiplicador tomado de otros países y de la atribución de una cartera que no se
puede verificar. La segunda es que la versión A es la más prudente para las conclusiones que siguen:
si el ingreso que falta está arriba, la tasa real de la cima es menor que la de la versión A, no
mayor. Cuando la versión A muestra que la cima paga menos que el promedio o menos que un sistema
progresivo, la versión B refuerza ese resultado. La versión B queda como cota: indica cuánto más
baja podría ser la tasa de la cima.

## 5. El decil 10 partido a lo largo del tiempo

![Figura 10](../outputs/figures/informe_v2/f10_composicion_1pct.png)

**Figura 10.** Qué impuestos paga cada grupo, año por año: deciles 1, 5 y 10 y el 1% más rico.

La figura 10 repite el gráfico de la figura 4 con el 1% más rico como cuarto panel. Los deciles 1,
5 y 10 son los mismos de antes; el 1% es un tramo del decil 10, separado con la versión A.

El 1% es el grupo cuya tasa más se mueve: entre 21,6% (2016) y 34,9% (2013). La razón está en su
composición. Ganancias y Bienes Personales son entre 61% y 75% de lo que paga, según el año, y esos dos impuestos
cambiaron mucho en el período: el piso de Ganancias quedó atrás de los salarios en 2009-2013, las
alícuotas de Bienes Personales bajaron en 2016 (Ley 27.260, con blanqueo), subieron en 2020 (Ley
27.541) y volvieron a bajar en 2024 (Ley 27.743). Son coincidencias en el tiempo, no causas
demostradas; el estudio no aísla el efecto de cada ley.

![Figura 11](../outputs/figures/informe_v2/f11_partido_anios_gobierno.png)

**Figura 11.** Qué parte de su ingreso pagó cada grupo, con el decil 10 partido, en los años de cambio
de gobierno.

La figura 11 vuelve a los siete años de la figura 3 con el decil 10 partido. Muestra que el decil 10
entero esconde movimientos de signo contrario adentro:

| Año | Decil 10 | P90-95 | P95-99 | 1% | Promedio |
|---|---|---|---|---|---|
| 2004 | 23,1% | 21,7% | 22,6% | 25,1% | 22,7% |
| 2007 | 24,5% | 24,0% | 24,1% | 25,6% | 24,6% |
| 2011 | 29,6% | 27,6% | 29,4% | 32,5% | 27,7% |
| 2015 | 30,4% | 29,5% | 31,2% | 30,0% | 28,6% |
| 2019 | 23,3% | 24,4% | 23,7% | 21,8% | 23,8% |
| 2023 | 27,7% | 27,5% | 28,5% | 27,1% | 26,5% |
| 2025 | 23,4% | 24,6% | 23,7% | 21,7% | 23,6% |

Entre 2004 y 2011 la tasa sube dentro del decil 10: el 1% paga más que los otros dos tramos. Desde
2015 la relación se invierte y el 1% paga menos que los percentiles 95-99, y en 2019 y 2025 menos que
todos. En 2004 el decil 10 y el promedio de la población estaban casi a la par (23,1% y 22,7%), con el
1% por encima de ambos; en 2025 también están a la par (23,4% y 23,6%), pero con el 1% dos puntos por
debajo.

## 6. ¿Proporcional o progresivo?

### Dos sistemas de referencia

Un sistema tributario es **proporcional** si todos pagan la misma tasa, **progresivo** si la tasa
sube con el ingreso y **regresivo** si baja. Para ubicar al sistema argentino se lo compara con dos
sistemas de referencia que recaudan exactamente lo mismo que el real cada año:

- **Proporcional:** todos pagan la tasa promedio. En ese sistema, cada grupo paga una parte de los
  impuestos igual a su parte del ingreso: si tiene el 10% del ingreso, paga el 10% de la
  recaudación.
- **Progresivo:** la tasa de cada grupo es la tasa promedio multiplicada por su ingreso relativo
  elevado a 0,25, y después se ajusta para que la recaudación total sea la misma. El ingreso
  relativo es el ingreso por persona del grupo dividido por el de toda la población. Con esta regla,
  en 2025 el decil 1 pagaría 12,7% y el 1% más rico, 37,0%.

La referencia progresiva no es un hallazgo sino una regla de medición. El exponente 0,25 es una
elección: un valor mayor daría un sistema más progresivo y uno menor, uno más parecido al
proporcional. Sirve para medir cuán lejos está el sistema real de un sistema progresivo concreto.
Al final de la sección se muestra cuánto cambian los resultados con otros exponentes.

![Figura 12](../outputs/figures/informe_v2/f12_matriz_deltas.png)

**Figura 12.** Qué parte de los impuestos paga cada grupo frente a su parte del ingreso, año por año,
con los dos años extremos en detalle.

La figura 12 se lee de los costados hacia el centro. A los costados hay dos gráficos de flujo. Cada
franja es un grupo y tiene tres alturas: a la izquierda, la parte de la población que es (10% cada
decil); en el medio, la parte del ingreso total que recibe; a la derecha, la parte de todo lo que se
paga en impuestos que pone. Para calcular esa última, se suman los pesos que paga el grupo en los
siete impuestos y se dividen por lo que pagan todos los grupos juntos. Si una franja tiene la misma
altura en el medio y a la derecha, el grupo paga impuestos en proporción a su ingreso; si se
ensancha, paga una parte mayor; si se angosta, menor. Las partes suman siempre 100%: si un grupo
pone una parte mayor, los demás ponen una parte menor, aunque paguen los mismos pesos.

Los dos años elegidos son los extremos del período. En 2022, el más lejos de lo proporcional, el 1%
tiene el 10,8% del ingreso y pone el 12,9% de los impuestos, mientras la clase media pasa del 38,8%
al 35,7%. En 2025, el más cerca, las franjas casi no cambian de altura y la única que se angosta es
la del 1% (del 10,8% al 9,9%). La distancia de cada año a lo proporcional se mide con la parte de la
recaudación que tendría que cambiar de grupo para que todos pagaran la misma tasa: 4,4 puntos en
2022 y 1,0 en 2025.

La tabla del centro (A) muestra lo mismo para todos los grupos y todos los años. Cada fila es un
grupo y cada columna, un año; las líneas horizontales separan el 1%, la clase alta, la clase media y
la clase baja. Cada celda es la diferencia entre las dos columnas de la derecha de un gráfico de
flujo: la parte de los impuestos que paga el grupo menos su parte del ingreso, en puntos de la
recaudación. Las columnas de 2022 y 2025 están recuadradas. Azul significa que el grupo paga una
parte mayor que su parte del ingreso; rojo, una parte menor; blanco, la misma. La tabla de abajo (B)
hace la misma cuenta frente al sistema progresivo de referencia, con otra escala de colores.

En la tabla de arriba, frente al sistema proporcional, casi todas las celdas están cerca de cero:
las diferencias son de décimas de punto. El decil 1 paga una parte mayor que su parte del ingreso
los 22 años (entre 0,2 y 0,6 puntos). El único grupo que se aleja más de un punto es el 1%, y lo hace
en las dos direcciones: paga una parte mayor que su parte del ingreso en 2004-2015 y 2020-2023 (hasta
2,4 puntos) y una menor en 2016-2019 y 2024-2025 (hasta 1,9 puntos).

En la tabla de abajo, frente al sistema progresivo, las diferencias son de varios puntos y tienen
siempre el mismo signo. Los deciles 1 a 7 pagan una parte mayor que la que les tocaría todos los
años (entre 0,3 y 1,8 puntos), y el 1% una parte menor todos los años (entre 2,4 y 9,1 puntos). Esto
es lo esperable en un sistema casi proporcional: cualquier referencia progresiva le asigna más a la
cima y menos a la base que un sistema donde todos pagan parecido.

![Figura 13](../outputs/figures/informe_v2/f13_kakwani.png)

**Figura 13.** Índice de Kakwani: qué tan progresivo es el sistema, año por año.

La figura 13 resume cada año en un número, el **índice de Kakwani**. Compara dos repartos: cómo se
concentra la recaudación entre los grupos y cómo se concentra el ingreso. El segundo se mide con el
coeficiente de Gini, que vale 0 si todos tienen el mismo ingreso y 1 si una sola persona tiene todo;
el primero se calcula igual, con los impuestos en lugar del ingreso. El índice es la diferencia
entre los dos. Si los impuestos están más concentrados arriba que el ingreso, el índice es positivo
y el sistema es progresivo; si están igual de concentrados, es 0 y el sistema es proporcional; si
están menos concentrados, es negativo y el sistema es regresivo.

La línea roja es Argentina, con una franja que muestra cómo cambia el índice con todos los
supuestos que se prueban en la sección 8. Con la medida del informe va de −0,021 (2016) a +0,031
(2022), y con cualquier supuesto queda entre −0,039 y +0,040: prácticamente cero en todo el período, con cambios de
signo que siguen a los del 1% en la figura 12. La línea azul punteada es el índice que tendría el
sistema progresivo de referencia, con la misma recaudación: alrededor de 0,10 en todos los años
(0,109 en 2025). La franja azul muestra ese valor con exponentes entre 0,15 y 0,40: va de 0,06 a 0,18.
Incluso el más suave de esos sistemas progresivos queda lejos del sistema argentino.

![Figura 14](../outputs/figures/informe_v2/f14_mapa_calor.png)

**Figura 14.** Tasa de cada grupo menos la tasa promedio, año por año.

La figura 14 mira lo mismo con otra medida: la tasa de cada grupo menos la tasa promedio del año,
en puntos de ingreso. Azul significa que el grupo paga una tasa mayor que el promedio; rojo, menor.
Es la forma más directa de ver quién paga más de lo que pagaría con un sistema proporcional.

El decil 1 paga más que el promedio todos los años, entre 3,7 puntos (2022) y 13,1 (2009). Los
deciles 6 a 8 son los que más seguido pagan menos. El 1% alterna: pagó más que el promedio en
2004-2015 y 2020-2023 (hasta 6,4 puntos, en 2006) y menos en 2016-2019 y 2024-2025 (hasta 4,1
puntos, en 2016).

![Figura 15](../outputs/figures/informe_v2/f15_brecha_grupos.png)

**Figura 15.** Cuánto más o menos pagaría cada grupo con otro sistema que recaude lo mismo, 2025.

Las diferencias de la figura 12 se pueden pasar a dinero. Para cada grupo, la diferencia entre la
parte de la recaudación que le tocaría y la que paga se multiplica por lo que efectivamente se
recaudó en el año con los siete impuestos del estudio (18,7% del PIB en 2025, según la Dirección
Nacional de Investigaciones y Análisis Fiscal). Se usa lo recaudado y no lo que reconstruye el
modelo porque la encuesta capta menos ingreso y consumo que las Cuentas Nacionales: el modelo
reproduce bien cómo se reparte la carga, no cuánto suma. Los montos se pasan a dólares con el tipo
de cambio oficial promedio del año.

En la figura 15, cada grupo tiene dos barras: gris, frente al sistema proporcional; azul, frente al
progresivo. Debajo de cada grupo está la tasa que paga hoy. En cada color, lo que suman unos grupos
lo restan otros, porque la recaudación total no cambia.

Con un sistema proporcional, en 2025 el 1% más rico pagaría US$1.100 millones más por año (0,16% del
PIB), unos US$2.400 por persona. Con el progresivo de referencia pagaría US$8.900 millones más (1,31%
del PIB), unos US$19.500 por persona, y los percentiles 95-99, US$4.300 millones más. Los deciles 1 a
9 pagarían en conjunto US$13.500 millones menos (2,0% del PIB): entre US$150 y US$400 por persona y
por año. Los montos por persona cuentan a todos los miembros del grupo, incluidos chicos, jubilados
y desocupados.

La figura marca también las clases sociales, con el criterio de la OCDE de la figura 6 aproximado
con deciles: clase baja, por debajo del 75% del ingreso mediano (deciles 1 a 3); clase media, entre
el 75% y el doble (deciles 4 a 8); clase alta, por encima del doble (decil 9 y percentiles 90 a 99). El
1% más rico se muestra aparte. Debajo de cada clase está su total frente al sistema progresivo. Entre
2016 y 2025, lo que la clase media pagó de más frente a ese sistema suma US$65.700 millones, y lo que
el 1% pagó de menos, US$73.100 millones.

Es una cuenta mecánica, que supone que nadie cambia su comportamiento. No estima lo que se podría
recaudar con una reforma: una suba de impuestos en la cima traería más elusión, más evasión y más
activos afuera. Mide la distancia entre cómo se reparte hoy la carga y cómo se repartiría con cada
referencia.

![Figura 16](../outputs/figures/informe_v2/f16_brecha_1pct.png)

**Figura 16.** El 1% más rico: la tasa que paga y la que pagaría con cada sistema de referencia,
2004-2025.

La figura 16 sigue al 1% en el tiempo con tres tasas. La roja es la que paga. La gris es la tasa
promedio, que es la que pagaría con un sistema proporcional. La azul es la que pagaría con el
progresivo de referencia. El sombreado gris marca los años en que el 1% paga más que el promedio; el
rojo, los años en que paga menos; el celeste, la distancia hasta el progresivo.

Frente al sistema proporcional el resultado depende del período: el 1% pagó más que el promedio en
2004-2015 y 2020-2023 y menos en 2016-2019 y 2024-2025. Sumando 2016-2025, lo que pagó de menos y lo
que pagó de más se compensan casi exactamente. Frente al progresivo, pagó menos todos los años: la
distancia fue de entre 0,35% y 1,86% del PIB según el año, y sumó US$73.000 millones entre 2016 y
2025.

El monto frente al progresivo depende del exponente elegido. En 2025, con un exponente de 0,15 (un
sistema menos progresivo) el 1% pagaría US$5.500 millones más (0,81% del PIB); con 0,25, US$8.900
millones (1,31%); con 0,40, US$14.800 millones (2,17%). Cambia el monto, no la dirección.

![Figura 17](../outputs/figures/informe_v2/f17_deltas_2025.png)

**Figura 17.** Qué parte de los impuestos paga cada grupo frente a lo que pagaría con cada
referencia, 2025.

La figura 17 es la columna de 2025 de la figura 12, dibujada en barras para leer los valores. A la
izquierda, frente al sistema proporcional; a la derecha, frente al progresivo, con la tasa que le
tocaría a cada grupo al lado de su nombre.

Los fondos de color marcan las mismas clases que la figura 15. Frente al proporcional, en 2025 el 1% paga 0,86 puntos menos de la recaudación que su parte del
ingreso, y el decil 1 y los percentiles 90-95 pagan algo más (0,32 y 0,46 puntos). Los demás grupos
quedan a menos de una décima. Frente al progresivo, todos los deciles 1 a 9 pagan una parte mayor
que la que les tocaría (entre 0,5 y 1,5 puntos cada uno), los percentiles 90-95 casi la misma, los
95-99, 3,4 puntos menos, y el 1%, 7,0 puntos menos.

## 7. Cuántas veces más ingresan y cuántas veces más pagan

![Figura 18](../outputs/figures/informe_v2/f18_veces.png)

**Figura 18.** Cuántas veces más ingresan y cuántas veces más pagan los de arriba que el 10% más
pobre.

La figura 18 compara a los de arriba con el decil 1 dividiendo una cosa por otra. Todo está por
persona: el ingreso o los impuestos del grupo divididos por la cantidad de personas del grupo.

El panel A divide el ingreso por persona del decil 10 por el del decil 1, antes y después de pagar
los impuestos del estudio. En 2004 el decil 10 ingresaba 51 veces lo del decil 1; en 2025, 25 veces.
Después de impuestos la distancia es mayor todos los años (61 veces en 2004 y 27 en 2025), porque el
decil 1 paga una proporción más alta de su ingreso que el decil 10.

El panel B pone, junto a ese cociente de ingresos (línea punteada), el cociente de impuestos: cuántas
veces más paga por persona el decil 10 que el decil 1 (línea llena). Si los dos grupos pagaran la
misma tasa, las dos líneas coincidirían. En 2025 el decil 10 ingresa 25 veces más que el decil 1 y
paga 21 veces más; la línea de impuestos queda debajo de la de ingreso todos los años.

El panel C hace lo mismo con el 1% más rico. En 2025 ingresa 72 veces lo del decil 1 por persona y
paga 55 veces más en impuestos. La línea de impuestos queda debajo de la de ingreso todos los años
salvo 2022. La distancia entre las dos se achicó en los años en que el 1% pagó más (2009-2015 y
2020-2023) y se agrandó en 2016-2019 y desde 2024.

Los tres paneles comparan contra el decil 1 y usan su ingreso declarado, con la aclaración de la
sección 2: una parte de su consumo se financia con recursos que no son ese ingreso. En los paneles B
y C, que la línea de impuestos quede debajo de la de ingreso equivale a decir que el grupo de arriba
paga una tasa menor que el decil 1.

## 8. Qué tan firme es cada resultado

Cada resultado de las secciones anteriores depende de decisiones: a quién se le carga cada impuesto,
qué impuestos se incluyen, cómo se mide el ingreso. Esta sección repite el cálculo cambiando esas
decisiones una por una y revisa, para cada afirmación del informe, si se sostiene. El resultado de
cada prueba se resume con tres veredictos: **firme** (se sostiene con cualquier supuesto, todos los
años), **depende del año** o **depende de un supuesto**, en cuyo caso se dice cuál.

### Los supuestos que se prueban

Se agrupan en cuatro familias. Cada una reemplaza una decisión de la medida del informe por otra
que también es defendible:

1. **Quién paga.** Las contribuciones patronales cargadas enteras al trabajador o enteras a los
   consumidores, en lugar de mitad y mitad. Y el IVA cobrado con la alícuota legal, como si nadie lo
   evadiera, en lugar de lo que efectivamente se recaudó por peso de consumo.
2. **Qué impuestos entran.** Sumando el impuesto al cheque, cargado a los precios; el cheque y los
   impuestos a los combustibles; el monotributo. O sacando Bienes Personales.
3. **Cómo se mide el ingreso de la cima.** Sin completar la cima con las declaraciones juradas (sólo
   la encuesta), o con la versión B de la sección 4.
4. **Cuánto consume la cima.** Por encima del 5% de mayores ingresos, el consumo proporcional al
   ingreso en lugar de fijo.

Se agrega una prueba más, sobre la forma de combinar las tres ediciones de la ENGHo: por tramos de
años en lugar de interpolarlas. Con la medida del informe son 12 versiones del cálculo.

![Figura 19](../outputs/figures/informe_v2/f19_rangos_supuestos.png)

**Figura 19.** Cuánto cambia la tasa de cada grupo con cada supuesto, en los años de cambio de
gobierno.

La figura 19 muestra, para los mismos siete años de las figuras 3 y 11, entre qué valores queda la
tasa de cada grupo con los supuestos de las familias 1, 2 y 4, sin completar la cima y con la otra
forma de combinar la ENGHo (franja celeste). El punto negro es la medida del informe y el rombo
azul, la versión B. La línea punteada es el promedio de la población.

La franja del decil 1 es la más larga, porque el decil 1 paga sobre todo impuestos al consumo y las
contribuciones, y esos son los supuestos que más cambian: en 2025 su tasa va de 26% a 33%. Las
franjas mezclan supuestos distintos y por eso se tocan entre grupos, pero comparando con el mismo
supuesto el decil 1 paga más que cada uno de los deciles 2 a 9 en todos los años. Las franjas de los deciles 2 a 9 se superponen entre sí: con cualquier supuesto pagan parecido. En
la cima las franjas son anchas y la del 1% cruza el promedio en varios años.

![Figura 20](../outputs/figures/informe_v2/f20_distancias_supuestos.png)

**Figura 20.** Las tres comparaciones centrales del informe, con todos los supuestos, 2004-2025.

La figura 20 sigue las tres comparaciones en las que se apoya el informe, año por año. Cada panel es
una diferencia de tasas en puntos de ingreso: por encima de cero, el primer grupo paga una
proporción de su ingreso mayor que el segundo. La línea llena es la medida del informe; la franja,
el rango con los demás supuestos; la línea azul punteada, la versión B. Cuando toda la franja queda
de un lado del cero, ese año el resultado no depende de los supuestos.

En el panel A, la franja del decil 1 queda por encima de cero los 22 años, y baja: la distancia del
decil 1 al promedio se redujo entre 7 y 11 puntos de 2004 a 2025 con cualquier supuesto.

En el panel B, la franja del 1% cruza el cero en la mayoría de los años. Queda entera por debajo en
2018, 2019 y 2025, años en que el 1% paga menos que el promedio con cualquier supuesto, y entera por
encima en 2012, 2013 y 2020-2022. En 2016, 2017 y 2024 el 1% paga menos que el promedio con todos los
supuestos salvo uno.

En el panel C, el 1% paga menos que los percentiles 90-95 con cualquier supuesto en 2018, 2019 y 2025,
y más con cualquier supuesto en 2011-2013, 2020 y 2022. En el resto de los años depende del supuesto.

### Veredicto por afirmación

| Afirmación | Dónde | Veredicto | Detalle |
|---|---|---|---|
| El decil 1 paga la tasa más alta entre los deciles | Sección 2 | Firme sobre el ingreso declarado | Con el decil 10 partido, algún tramo de la cima lo supera en 13 de las 264 combinaciones de año y supuesto; en la medida del informe, sólo el 1% en 2022 |
| Los deciles 2 a 9 pagan casi lo mismo | Sección 2 | Firme | La diferencia entre el que más paga y el que menos es de hasta 3,9 puntos en la medida del informe y de hasta 5,6 con contribuciones cargadas enteras a los consumidores (2012) |
| La distancia del decil 1 al promedio se achicó | Secciones 2 y 8 | Firme sobre el ingreso declarado | Baja entre 7 y 11 puntos de 2004 a 2025 con todos los supuestos. El valor de 2009 depende de cómo se combinan las ediciones de la ENGHo |
| El decil 10 esconde mucha diferencia adentro | Sección 3 | Firme | No depende de los supuestos sobre impuestos; con la versión B la diferencia es mayor |
| La tasa baja hacia la cima (el 1% paga menos que los percentiles 90-95) | Secciones 4 y 5 | Depende del año | Con cualquier supuesto en 2018, 2019 y 2025; nunca en 2011-2013, 2020 y 2022 |
| El 1% paga menos que el promedio | Secciones 5 y 6 | Depende del año | Con cualquier supuesto en 2018, 2019 y 2025, y con todos salvo uno en 2016, 2017 y 2024. Paga más con cualquier supuesto en 2012, 2013 y 2020-2022 |
| En 2025 el 1% paga menos que cualquier decil | Sección 4 | Depende de un supuesto | Se sostiene con 10 de las 12 versiones. No se sostiene si la cima consume en proporción a su ingreso o si las contribuciones se cargan enteras al trabajador |
| El sistema es casi proporcional | Sección 6 | Firme | El índice de Kakwani queda entre −0,039 y +0,040 con todos los supuestos, lejos del 0,06 del sistema progresivo más suave de la figura 13 |
| El 1% paga menos y el decil 1 más que en un sistema progresivo | Sección 6 | Firme en la dirección | Con todos los supuestos y todos los años. El monto depende del exponente de la referencia y de la versión (sección 6) |
| Los de arriba pagan, en proporción a su ingreso, menos que el decil 1 | Sección 7 | Firme sobre el ingreso declarado | Salvo el 1% en 2022 |

Los resultados se ordenan entonces en dos grupos. Son firmes la forma del sistema para la gran
mayoría de la población (los deciles 2 a 9 pagan parecido y el sistema, en conjunto, es casi
proporcional), la distancia frente a un sistema progresivo y que la carga relativa del decil 1 bajó.
Dependen del año los resultados sobre el 1%: en 2018, 2019 y 2025 paga menos que el promedio y que los
percentiles 90-95 con cualquier supuesto, y en 2012, 2013 y 2020-2022 paga más. La carga más alta
del decil 1 es firme frente a todos los supuestos; se mide sobre el ingreso que declara, con la
aclaración de la sección 2.

