# Respuestas a `preguntas_abiertas.md`

> **Documento histórico (anterior a la auditoría del 13/11/2026).** Varias decisiones cambiaron
> después: la medida principal es el ingreso declarado (no el gasto), los ingresos altos se
> corrigieron el 16/11/2026 y las cifras de abajo son de ese momento. El estado actual está en
> `docs/metodologia.md` y los resultados en `docs/informe.md`.

Cada punto fue contrastado con corridas nuevas. Las cifras salen de `outputs/tables/`.

## A. Regresividad

**A1. Correcta, y era el problema central.** La regresividad del criterio inicial salía
casi entera del cociente gasto/ingreso del decil 1. Ahora la estimación principal toma el
gasto como medida de recursos cuando supera al ingreso declarado, y la variante
`ingreso_declarado` se muestra siempre al lado. Resultado 2024: decil 1 entre 24,4% y
34,9%; deciles 3 a 10 entre 24% y 27% en ambas. El resultado se presenta como rango.

**A2. Correcta: no era válido.** El decil 1 de la EPH tenía un ingreso relativo de 0,09
de la media en 2004 y 0,18 en 2015; el de la ENGHo 2004/05, 0,13. Aplicar el cociente por
número de decil ignoraba ese cambio. Ahora el consumo se asigna por ingreso relativo.

**A3. Parcialmente resuelta.** El consumo de encuesta sigue siendo 37% a 55% del de
Cuentas Nacionales. Las tasas por decil son válidas si la subcobertura es proporcional
entre deciles; no hay forma de verificarlo sin ajustar ingresos a Cuentas Nacionales por
fuente. Queda como limitación declarada.

## B. Serie temporal

**B1. Correcta.** Descomposición del decil 1 entre 2004 y 2015:

| Serie | 2004 | 2015 | Cambio |
|---|---|---|---|
| Criterio inicial (escalonado, ingreso declarado) | 39,0 | 40,6 | con saltos de +9,6 en 2012 |
| Ingreso declarado, método nuevo | 39,0 | 38,6 | −0,4 |
| Principal | 18,6 | 24,9 | +6,3 |
| Principal con población fija de 2017 | 21,2 | 24,7 | +3,5 |

La suba de Ingresos Brutos sobre consumo privado (3,7% → 6,1%) es real: es recaudación
provincial creciente, no un problema de la serie de consumo.

**B2. Resuelta:** interpolación lineal entre ediciones.

**B3. Hipótesis confirmada.** Excluyendo los aportes a AFJP, el cociente simulado /
recaudado de 2008 baja de 2,35 a 1,18, igual que 2009-2024 (1,0 a 1,3). El exceso
restante se explica porque la expansión al total país supone la misma formalidad fuera
de los aglomerados y porque los empleados públicos provinciales aportan a cajas que no
están en la recaudación nacional. En 2004-2007 queda en 1,4 a 1,7: no explicado del todo.

## C. Composición

**C1. Correcta; sin resolver.** La EPH no identifica monotributistas. La proporción de
cuentapropistas por decil está en `composicion_por_decil_anual.csv` (decil 1: 5,6% de las
personas en 2004, 9,6% en 2024).

**C2. Una corrección:** el modelo NO cobra INSSJP sobre jubilaciones; los aportes sólo se
calculan sobre salarios registrados. Los registrados pasan de 0,6% a 2,9% de las personas
del decil 1 entre 2004 y 2024, y eso explica la suba de sus impuestos directos (0,5% a
2,1% del ingreso).

## D. Definición

**D1.** El denominador antes de impuestos es el correcto para una tasa; `sobre_ipcf` se
publica como variante y da entre 3 y 5 puntos más.

**D2. Atendida:** las tablas traen `directos` e `indirectos` por separado. 2024: decil 1,
2,1% directos y 22,3% indirectos; decil 10, 12,3% y 11,8%.

**D3. Atendida:** variantes 100% trabajador y 100% consumidor.

## E. Ganancias

**E1. Atendida con datos tributarios** (`metodologia.md`, sección 5). La simulación
reproduce entre 12% y 37% de lo recaudado; lo faltante se asigna ahora a las personas de
mayor ingreso según las declaraciones juradas de ARCA. Decil 10 en 2024: 24,1% sin
corregir, 27,3% en la estimación principal, 31,2% como techo.

**E2. Correcta:** las deducciones generales no están modeladas. Sesga hacia arriba el
impuesto por contribuyente, en sentido contrario al sesgo dominante.

**E3.** Sin evidencia propia; es el supuesto estándar y queda declarado.

## F. Higiene

Tests agregados (`tests/`), advertencia de pandas corregida, documentación escrita.
Pendiente: `git init`, fijar versiones en `requirements.txt`.
