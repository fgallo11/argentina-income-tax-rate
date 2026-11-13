# Preguntas abiertas para quien continúe el proyecto

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

- No es un repositorio git (`git init` pendiente).
- No hay tests; `pytest` está en `requirements.txt` pero `tests/` está vacío.
- Faltan `docs/metodologia.md`, `docs/validacion.md` y `docs/errores_notebook.md`.
- `PerformanceWarning` de pandas en `src/incidencia/eph.py:50` (DataFrame fragmentado).
- `requirements.txt` sin versiones fijadas.
- `data/processed` y `outputs` no están en `.gitignore`; confirmar si es intencional.
- El README no documenta el punto B3 (AFJP) ni destaca el A1 como la principal incertidumbre.
