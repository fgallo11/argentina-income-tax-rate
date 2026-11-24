# Observaciones sobre la narrativa del informe

Revisión de `docs/informe.md` (versión del commit `c911781`, 24/11/2026). No discute el método:
discute si lo que el informe **dice** está respaldado por lo que el proyecto **calcula**, y si el
texto es coherente consigo mismo. Cada punto cita la línea del informe y la fuente que lo contradice
o lo matiza.

## Veredicto

La prosa y el arco funcionan: "gráfico de siempre → por qué engaña → partir el decil 10 → contra
referencias → conclusión" se sigue bien, y separar el **Detalle técnico** sirve. El problema es que
**la tesis central sobre el 1% se presenta más firme de lo que permiten los propios datos del
proyecto**, y hay contradicciones internas.

## Problemas estructurales (de más a menos grave)

### 1. "El 1% paga menos que cualquier decil" depende de un supuesto no testeado en el informe

- `docs/metodologia.md` §13: con `consumo_proporcional` (cociente gasto/ingreso fijo arriba del
  P95) el 1% paga **23,6%**, igual a los deciles medios. Rango del 1% en 2025: **19,9–23,6%**.
- Es decir, "menos que cualquier decil" depende de dejar fijo el *nivel* de consumo por encima
  del P95.
- La sección 7 ("Qué tan firme es") se dedica casi solo al decil 1. La afirmación que encabeza el
  resumen no tiene su prueba de robustez.

### 2. La explicación de por qué el 1% de las declaraciones juradas queda arriba es incorrecta

- Informe, sección 3 (línea 278): la medida con declaraciones juradas da 26,6% y "queda por encima
  del promedio, sobre todo porque suma el impuesto de sociedades".
- `outputs/tables/top1.csv`, 2025: `total_central` 30,2% (sin sociedades), `con_sociedades` 30,1%,
  `completo` 26,6%. **Sumar sociedades no cambia nada**; lo que baja a 26,6% es la renta de los
  activos externos.
- La propia sección "Pendientes" (línea 631) dice que sociedades "casi no cambia su tasa", y
  contradice a la sección 3.
- La brecha real entre las dos medidas del 1% (~30% contra 21,7%) viene del **consumo** (~10% del
  ingreso con declaraciones juradas contra ~3,3 puntos en la encuesta) y del supuesto de que **la
  mitad del ingreso es salario** (aportes y contribuciones: 8,6% contra 4,3%). Esa es la discusión
  de fondo, y la atribución equivocada la tapa.

### 3. Las mediciones externas del 1% contradicen el titular, y el resumen dice que lo confirman

- Resumen, primer punto: Argendata y el ITO "lo encuentran también". Vale para el perfil por deciles.
- En el 1%, el ITO da ~30%, por encima del 10% más rico (25%): progresivo en la cima. La medida
  propia con declaraciones juradas da entre 26,6% y 30% según la variante, y por encima del promedio
  todos los años (`top1.csv`).
- El lector se queda con "tres estudios coinciden" cuando en el punto más importante no coinciden.

### 4. "Frente al progresivo, el 1% paga menos" da su resultado por construcción

- Si el Kakwani da cerca de cero (sistema casi proporcional), cualquier referencia progresiva va a
  mostrar que la cima paga de menos y la base de más, **todos los años**.
- "Falta arriba lo que sobra abajo" se presenta como hallazgo, pero es consecuencia del exponente
  elegido (0,25, justificado sólo como "una elección"). La tabla de sensibilidad muestra que la
  dirección se mantiene con 0,15 y 0,40: eso es lo que pasa con cualquier exponente positivo.
- Es útil como **medida de distancia**; no debería figurar como resultado en el resumen.

### 5. Se cambia de versión sin avisar, y el número más citable usa la menos firme

- Los cuatro primeros puntos del resumen y las secciones 1–3 y 5 usan la versión A (1% = 21,7%).
- "¿Cuánta plata es?" usa la versión B con renta externa (1% = 18,5%): **la estimación más baja de
  todo el rango**, la que la sección 3 llama "una estimación, no una medición" y que se apoya en un
  ×7 importado de otros países.
- Progresivo 2025: versión A, US$8.900 millones (1,31% del PIB); versión B, US$13.200 millones
  (1,94%). El resumen da el más grande.
- Que la cifra que va a circular sea la más dependiente de supuestos es un sesgo de presentación,
  aunque no sea intencional.

### 6. La tesis oscila entre "casi proporcional" y "regresivo"

- Resumen y sección 4: casi proporcional (Kakwani entre −0,021 y +0,031).
- Sección 3, cierre: con la versión B "el sistema es regresivo de punta a punta".
- Sección 6: el sistema "agranda" la distancia entre ricos y pobres.
- Hay que elegir una tesis y presentar la otra como variante condicionada.

### 7. La conclusión se apoya en el resultado más débil

- "Los impuestos agrandan la distancia" sale del cociente D10/D1 antes y después de impuestos, que
  depende del **nivel** del decil 1.
- La sección 7 dice que ese nivel es "el resultado menos firme" y que, medido por gasto, el decil 1
  paga por debajo del promedio, lo que daría vuelta la conclusión.
- En los años con Kakwani positivo (por ejemplo 2022), medido con el Gini el sistema reduce la
  desigualdad. La conclusión no lo menciona.

### 8. El punto 3 de la conclusión generaliza a todos los años

- Sección 6, punto 3: "Partiendo el decil 10, la cima paga menos que el resto", sin año.
- La propia sección 3 muestra que en 2004 y 2013 el 1% paga más que los percentiles 90-95, y la
  matriz de la sección 4 muestra que en 2009-2013 y 2020-2022 paga más que la tasa proporcional.

## Inconsistencias menores

- Decil 1 en la versión B, 2025: 31,6% con renta externa en la sección 3 y 31,5% en la tabla de
  "¿Cuánta plata es?".
- Tasa promedio de 2025: 23,8% (A) y 23,6% (B), sin aclarar cuál es cuál donde aparece.
- Brecha del 1% frente al proporcional: 0,52% del PIB y unas líneas después 0,55% ("subir a todos
  los que pagan de menos"). Es correcto, pero confunde sin explicación.
- Sumas de componentes que difieren por una décima (decil 1 consumo: 26,7 calculado contra 26,8
  escrito; 1% Ganancias + Bienes Personales: 14,2 contra 14,1). Es redondeo; conviene una nota.

## Propuestas

1. **Reformular el titular del 1%:** "con la encuesta, el 1% paga igual o menos que el promedio
   (19,9–23,6%); con declaraciones juradas, más (26,6–30%). La diferencia está en el consumo y en
   la composición del ingreso".
2. **Corregir la línea 278** con la atribución correcta (renta externa, consumo y salario; no
   sociedades).
3. **Agregar a la sección 7 una prueba de robustez para el 1%**, del mismo peso que la del decil 1.
4. **Usar la versión A para la cifra en dólares del resumen**, con la versión B como cota.
5. **Presentar la referencia progresiva como regla de medición**, no como hallazgo; sacarla del
   resumen o rebajarla.
6. **Tomar "casi proporcional" como tesis** y dar "regresivo" como resultado condicionado a la
   versión B.
7. **Agregar el año** a las afirmaciones de la conclusión que dependen del año, y matizar el
   "agranda la distancia" con el Kakwani.
