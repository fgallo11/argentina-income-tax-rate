# Preguntas abiertas para quien continúe el proyecto

> **Las secciones A a E son históricas** (primera revisión del proyecto, anterior a la auditoría
> del 13/11/2026); sus respuestas están en `docs/respuestas_preguntas_abiertas.md` y el estado
> actual, en `docs/metodologia.md` (sección 14) y `docs/informe.md`. La sección F y los
> "Pendientes de desarrollo" están al día.

Resultado de una primera revisión del proyecto (código, parámetros, tablas de validación y
log de la última corrida). **Nada de esto fue verificado con corridas nuevas**: son lecturas
del código y de las tablas existentes. Los pesos numéricos que se mencionan son aproximados.

Orden: primero lo que más condiciona las conclusiones.

---

## A. La conclusión de regresividad

**A1. ¿Qué parte de la regresividad es real y cuál es un artefacto de encuesta?**
La relación gasto/ingreso del decil 1 es 1,59 (ENGHo 2004), 1,68 (2012) y 1,45 (2017); en
D10 va de 0,63 a 0,70. Con `gasto_tope1` la brecha D10 − D1 pasa de unos −10 pp a un perfil
plano (+2,1 a −0,9 pp). Las variantes `sobre_ipcf` y `calibrada` reducen la brecha pero no la
eliminan.
- ¿Hay un escenario intermedio defendible entre `principal` y `gasto_tope1`? El tope en 1 es
  un extremo, no un caso central.
- ¿Se puede corregir el ingreso del D1 (subdeclaración, transferencias en especie, ingresos
  irregulares) en lugar de truncar el cociente?
- ¿Cómo debería presentarse el resultado principal: como un rango en lugar de un punto?

**A2. ¿Es válido aplicar el cociente gasto/ingreso de la ENGHo al IPCF de la EPH?**
`05_incidencia.py` hace `consumo = q.ipcf * cy`, con `cy` de la ENGHo y los deciles de la EPH.
Se supone que el decil 1 de una encuesta consume como el decil 1 de la otra.
- ¿Se puede validar esa equivalencia (por ejemplo, comparando distribuciones de ingreso
  ENGHo vs. EPH en años cercanos)?

**A3. ¿Las subcoberturas de consumo e ingreso son comparables?**
El consumo de la encuesta es 37-56% de Cuentas Nacionales y el ingreso EPH ronda 33% del PIB.
Los indirectos agregados quedan a menos de la mitad de lo recaudado
(`impuestos_incluidos_sobre_recaudacion_total` ~0,56).
- ¿Las tasas por decil son robustas a que ambas subcoberturas difieran? ¿Hay que reescalar
  consumo, ingreso o ambos?

---

## B. Serie temporal

**B1. ¿Cuánto de la trayectoria del D1 es artefacto?**
La tasa total del D1 pasa de 33,0% (2007) a 40,1% (2015) y cae a 35,6% (2017). Lectura
preliminar, sin descomposición formal:
- Saltos de edición ENGHo: +3,5 pp en 2012 y −3,7 pp en 2017.
- Ingresos Brutos: ~+3 pp (6,7% → ~10%) por el aumento de recaudación IIBB / consumo privado
  (4,3% → 6,2% → 5,5%), que es un movimiento macro y no distributivo.
- Contribuciones: 1 a 1,5 pp, mismo mecanismo (4,3% → 6,0% del consumo).
- Composición real (más registrados, más jubilados por la moratoria): ~1,5 pp.
- ¿Se puede armar una descomposición contrafáctica (fijar la edición ENGHo, fijar los
  cocientes macro) para tener los pesos exactos?
- ¿Por qué cae la recaudación de IIBB / consumo privado después de 2014? ¿Es real o un problema
  de la serie de consumo privado?

**B2. ¿Se puede suavizar el cambio de edición de ENGHo?**
La estructura de gasto es fija dentro de cada edición (2004-2011, 2012-2016, 2017-2024). El
README ya marca los saltos como artefactos, pero no hay una versión sin ellos.
- ¿Conviene interpolar entre ediciones, fijar una sola edición o presentar sólo
  comparaciones dentro de cada edición?

**B3. ¿Debería excluirse la serie 2004-2008 de la validación de aportes?**
El ratio simulado / recaudado de aportes es 1,4-2,9 hasta 2008 y 1,14-1,3 desde 2009. La serie
DNIAF `ss_empleados` salta de 0,79% del PIB (2007) a 2,31% (2009): coincide con la reestatización
de las AFJP, cuyos aportes la recaudación del Estado no incluía antes.
- Hipótesis consistente pero no verificada: la simulación cuenta aportes que van a AFJP y la
  recaudación no. ¿Se confirma revisando qué incluye `ss_empleados` en cada año?
- ¿Hay que documentarlo en `validacion.md` o ajustar la comparación?
- Después de 2009 queda un ratio ~1,2: ¿es evasión no modelada entre los "registrados"?

---

## C. Composición del trabajo y de la población

**C1. ¿Cómo tratar monotributistas, autónomos e informales?**
Tienen tasa cero en directos, y la recaudación de monotributo y autónomos está excluida. El
modelo ve la formalización asalariada pero no la monotributista, que en parte reemplazó al
empleo informal.
- ¿Se puede identificar a estos grupos con la EPH (categoría ocupacional, aportes) y simularles
  aportes y Ganancias?
- ¿Cómo cambia la lectura de la serie si se los incluye?

**C2. ¿Cuánto del cambio en el D1 es composición real?**
Entre 2007 y 2016 los registrados pasan de 1,2% a 2,7% de las personas del D1 y las
jubilaciones de 7,7% a 15,2% de su ingreso. Los aportes INSSJP sobre jubilaciones cuentan como
impuesto.
- ¿Es correcto tratar el INSSJP de jubilados como carga tributaria en el mismo sentido que los
  aportes de un trabajador?

---

## D. Definición del indicador

**D1. Denominador: ¿dos medidas de "ingreso" en el mismo decil?**
El denominador es el ingreso antes de impuestos directos: IPCF + aportes + obra social +
Ganancias + mitad de las contribuciones. Para asalariados registrados es mayor que lo que
cobran; para informales, monotributistas y desocupados es sólo el ingreso de bolsillo.
- ¿Introduce un sesgo entre deciles con distinta formalidad? ¿Es preferible `sobre_ipcf`?

**D2. ¿El numerador mezcla cosas incomparables?**
Suma directos (aportes, Ganancias, contribuciones) con indirectos (IVA, IIBB, internos) y
Bienes Personales. Los indirectos no se descuentan del ingreso: se pagan al consumir.
- ¿Conviene mostrar directos e indirectos por separado como resultado principal?

**D3. ¿La mitad de las contribuciones patronales "del trabajador" es un supuesto razonable?**
Se asume 50% al trabajador y 50% al consumidor. El README lo declara, pero no hay sensibilidad.

---

## E. Ganancias

**E1. Cobertura de 8-23% de la recaudación de personas físicas.**
El cálculo es determinístico (escala, deducciones, parámetros verificados contra el PDF de la
DNIAF), pero la EPH no capta los ingresos altos y no se simulan independientes ni capital. El
"D10" es un D10 de la EPH.
- ¿Qué hay que cambiar para que el D10 sea interpretable (por ejemplo, una corrección con
  datos tributarios o de ingresos altos)?
- La variante `calibrada` reescala Ganancias a la recaudación de personas físicas, suponiendo
  que lo que falta se distribuye como lo simulado. ¿Es defendible?

**E2. Deducciones generales no modeladas.**
Los aportes sí se deducen de la base (`neto_mes = bruto - aportes`). No hay deducción de
alquiler, intereses hipotecarios, gastos médicos, educación, seguros de vida ni servicio
doméstico (`params/ganancias.yaml` sólo tiene deducciones personales). Probablemente
sobreestima Ganancias por asalariado en el D10.
- ¿Qué variables de la EPH permiten aproximarlas (alquiler, servicio doméstico)?
- ¿Cuánto cambia el resultado? Ganancias pesa 0,4-1,1% del ingreso total, concentrado en D10.

**E3. Traslación de IIBB y contribuciones.**
Se asume traslación plena al consumidor, sin deducciones de empresas. No hay doble conteo en
lo modelado, pero la traslación podría ser parcial.
- ¿Hay evidencia para una traslación menor al 100% o distinta por decil?

---

## F. Higiene del proyecto

Estado al 26/11/2026 (la lista original, del inicio del proyecto, ya se resolvió en su mayor parte:
hay repositorio git, tests en `tests/`, `docs/metodologia.md` y `docs/validacion.md`).

- `requirements.txt` sigue sin versiones fijadas.
- `data/processed/` se versiona en parte (las tablas chicas que leen los scripts de gráficos);
  `data/raw/` e `interim/` no.
- La auditoría externa (`docs/auditoria.md`, `auditoria/`) y la trazabilidad
  (`docs/trazabilidad_datos.md`) describen el proyecto en la fecha en que se hicieron; sus cifras
  no se actualizan.

---

## Pendientes de desarrollo (antes en el informe)

**Ganancias de sociedades (2,4% del PIB en 2025; entre 2,4% y 3,1% en la serie).** No se suma a la
medida principal por tres razones:

1. **No se sabe bien quién lo paga.** Lo paga la empresa, pero el costo puede recaer en los dueños
   (menos ganancia), en los trabajadores (menos salario) o en los consumidores (más precio). La
   literatura usa escenarios (100% a los dueños del capital, o 50% capital y 50% trabajo) y el
   resultado de la cima depende de cuál se elija.
2. **Sumarlo bien exige sumar también las utilidades al ingreso de los dueños.** Si se suma sólo el
   impuesto, la tasa de la cima se infla (lo mismo pasaría con la Ganancias de personas: impuesto
   sin el ingreso que lo genera). Con las utilidades, esa parte paga cerca del
   30% y el efecto es mucho menor: en la versión anterior del 1% de las declaraciones juradas
   (hasta el 26/11/2026), sumar la mitad del impuesto y de las utilidades casi no cambiaba su tasa
   (30,2% sin sociedades, 30,1% con). La medida de control actual no lo incluye, para ser
   comparable con la versión A.
3. **No hay datos de quién es dueño de qué.** Ni la EPH ni las declaraciones juradas publicadas dicen
   cuántas acciones o participaciones tiene cada persona.

**Cómo se agregaría.** Como variantes, con una sola perilla: quién paga cada peso del impuesto. A
quien lo paga se le suman a la vez el impuesto y el ingreso que tendría sin el impuesto, como en la
corrección de la Ganancias de personas. Cuatro escenarios:

| Escenario | Capital | Trabajo | Consumidores |
|---|---|---|---|
| Todo al capital | 100% | | |
| Mitad capital, mitad trabajo | 50% | 50% | |
| Todo al trabajo | | 100% | |
| Todo a precios | | | 100% |

- **Parte del capital (los dueños).** Impuesto: su parte de la recaudación, menos la que corresponde
  a dueños del exterior (aproximada con la inversión extranjera directa de la Posición de inversión
  internacional del INDEC). Ingreso: las utilidades antes del impuesto (impuesto ÷ alícuota), que
  son ingreso de los dueños aunque la empresa no las reparta. La alícuota va año por año en
  `params/`: 35% hasta 2017, 30% en 2018-2020, escala de 25/30/35% desde 2021 (Ley 27.630). A quién:
  primero con las proporciones del empalme con las declaraciones juradas (como la Ganancias que la
  encuesta no capta); mejor, con las rentas de negocios por tramo de los anuarios de ARCA, si vienen
  separadas; las ganancias de negocios de la EPH pueden dar la forma en los deciles medios.
- **Parte del trabajo (salarios más bajos).** Se trata como un impuesto al salario: tasa = su parte
  de la recaudación ÷ la masa salarial privada registrada del país; a cada decil, esa tasa × su masa
  salarial privada registrada, como impuesto y también como ingreso (es salario que habría cobrado).
  No alcanza a informales, empleados públicos ni jubilados.
- **Parte de los consumidores (precios más altos).** Como la mitad de las contribuciones patronales
  que pasa a precios: recaudación por peso de consumo privado × el consumo de cada decil.

**Qué se espera.** El nivel sube unos 3 puntos en cualquier escenario (2,4% a 3,1% del PIB).

- Todo al capital: sube la cima; el 1% de la encuesta (21,7% en 2025) se acerca al 30%, porque esa
  parte paga más que su promedio, y su parte del ingreso crece mucho (las utilidades son del orden
  de 8% del PIB). Los deciles 1 a 8 casi no cambian.
- Todo al trabajo: recae en los deciles con empleo privado registrado (4 a 10) y sube varios puntos
  a los del medio; el decil 1 casi no cambia. El perfil queda con una joroba en el medio.
- Todo a precios: regresivo, como el IVA.
- Mitad y mitad: entre los dos primeros.

**Dónde se toca el código.** `params/` (alícuota por año); `src/incidencia/incidencia.py` (un campo
de `Variante` con el reparto entre capital, trabajo y precios; un impuesto `sociedades`; el cálculo
de cada parte); `scripts/09_ingresos_altos.py` (el reparto de la parte del capital si se usan las
rentas de negocios); `scripts/05_incidencia.py` y `scripts/11_tramos_decil10.py` (las cuatro
variantes); el informe (un apartado en la sección 8, "Qué tan firme es cada resultado"). No hace falta volver a correr la
microsimulación de la EPH.

**Evasión de IVA distinta por decil (posible pendiente).** Hoy el IVA que no se cobra se reparte
parejo: si en un año se recauda el 80% del IVA que correspondería por ley, se supone que cada decil
paga el 80% del IVA legal de su canasta (informe, sección 2). Pero es probable que los
hogares más pobres compren una parte mayor en negro (ferias, almacenes de barrio, venta ambulante),
donde el Estado no cobra IVA. Si es así, su carga real es menor que la medida.

- **Qué importa y qué no.** Para la tasa efectiva sólo cuenta qué parte de lo que compra cada decil
  es en negro: esa compra no deja IVA al Estado. Cómo se reparten la evasión comprador y vendedor
  (por ejemplo, un descuento de 10% para el comprador y 10% de ganancia extra para el vendedor, en vez
  del 21% entero) no cambia el IVA pagado: cambia quién se beneficia de la evasión. La ganancia del
  vendedor es ingreso suyo (cuentapropistas y pequeños comercios), ya incluido en la encuesta si lo
  declara.
- **Cómo se haría.** Con el lugar de compra de la ENGHo (supermercado, almacén, feria, etc.), si la
  encuesta lo trae con detalle suficiente: calcular por decil la parte del gasto hecha en comercios
  probablemente informales, cargarle menos IVA a esa parte y reescalar para que el total siga siendo
  lo recaudado. Es el método de Bachas, Gadenne y Jensen (*Informality, Consumption Taxes and
  Redistribution*), que en varios países encuentra que la parte informal del consumo cae con el
  ingreso y que eso vuelve al IVA menos regresivo. Hay que verificar que la ENGHo tenga la variable
  en las tres ediciones.
- **Qué se espera.** Baja la tasa del decil 1 y sube un poco la de los de arriba; el total no cambia.
  Sería una variante, no la medida principal, porque el traslado de "comercio informal" a "no paga
  IVA" es un supuesto.
- **Dónde se toca el código.** `src/incidencia/indirectos.py` (perfil de IVA por decil) y la lectura
  de la ENGHo.

**Otros impuestos que quedan afuera:**

- **Combustibles (0,6% del PIB en 2025)** está como variante: se reparte según el consumo total de
  cada decil. Le llega a los hogares por dos vías: directa (la nafta del auto propio, que crece con
  el ingreso) e indirecta (el gasoil del transporte de carga y de pasajeros, de la producción
  agropecuaria y de la industria, que encarece casi todo lo que se compra). Repartirlo según el
  consumo total representa bien la vía indirecta y exagera algo lo regresivo de la directa. Le suma
  1,1 puntos al decil 1 y 0,3 al decil 10 en 2025 (3,7 y 0,9 en 2004, cuando el impuesto pesaba el
  doble). Para separar las dos vías haría falta el gasto en combustible de la ENGHo y una matriz
  insumo-producto.
- **Impuestos provinciales distintos de Ingresos Brutos** (inmobiliario, automotor, sellos; 1,0% a
  1,4% del PIB): habría que conseguir la recaudación separada por impuesto y repartir el inmobiliario
  según la propiedad de la vivienda, el automotor según la tenencia de autos y sellos a precios.
  Sumaría entre 1 y 2 puntos, bastante parejo.
- **Tasas municipales:** no hay una serie nacional de recaudación.
- **Retenciones a la exportación:** no está claro si las pagan los productores o los consumidores
  internos, con precios de alimentos más bajos.
- **Monotributo:** está como variante (`con_monotributo`): cuota por categoría, quién paga según la
  propia encuesta y nivel ajustado a lo recaudado. Sube la tasa total entre 0,1 y 0,7 puntos por decil y no
  cambia la forma ([el simulador](microsimulacion.md), sección 8). Faltan los aportes de autónomos del
  régimen general y los asalariados que aportan por su cuenta (monotributistas que facturan a un solo
  empleador: de 2,2% de los ocupados en 2016 a 4,4% en 2025), que el modelo trata como no registrados.
