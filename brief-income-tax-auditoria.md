# Brief para Fable — Income Tax Argentina: auditoría adversaria

> Pegalo como primer mensaje de una sesión NUEVA (no continúes la sesión que construyó el
> proyecto) en `/home/fran/Income_tax_argentina`.

---

Sos un revisor externo, escéptico, de un estudio de incidencia tributaria por decil de ingreso
en Argentina (2004-2024). Lo construyó otra sesión; **tu trabajo no es mejorarlo sino intentar
romperlo**. Asumí que tiene errores hasta demostrar lo contrario.

Leé `README.md`, `docs/metodologia.md`, `docs/validacion.md`, `docs/preguntas_abiertas.md`,
`docs/respuestas_preguntas_abiertas.md`, `params/` y los scripts de `scripts/` y
`src/incidencia/`. Las tablas están en `outputs/tables/`.

**No modifiques el código, los parámetros ni los resultados del pipeline.** Podés escribir
scripts propios de verificación en `auditoria/` y correrlos. El entregable es
`docs/auditoria.md`.

## Resultado bajo revisión (2024)

Tasa promedio 26,2%. Deciles 2 a 9 entre 25% y 26%. Decil 1 entre 24,4% y 34,9% y decil 10
entre 24,1% y 31,2% (principal 27,3%), según cómo se mida el ingreso. Es decir, un perfil
**casi plano**.

## Lo que tengo que entender (en este orden)

1. **¿Por qué el perfil da plano si la literatura argentina suele dar regresivo** (decil 1
   bastante más alto que el promedio, decil 10 más bajo)? Buscá los estudios publicados
   comparables (Gómez Sabaini, Rossignolo, CEPAL, CEDLAS, CIPPEC, Ministerio de Economía u
   otros que encuentres) y armá una tabla: estudio, año, fuente, cifra D1 / D10 / promedio, y
   qué decisión de método explica cada diferencia con este proyecto. Cuantificá cuánto
   explica cada decisión usando las variantes ya calculadas, o corriendo variantes propias.

2. **La corrección del decil 1 por gasto.** Cuando el gasto declarado de un hogar supera su
   ingreso declarado, se toma el gasto como recurso. Explicame:
   - De dónde sale exactamente el gasto y de dónde el ingreso (qué encuesta, qué variable, qué
     años), y cómo se cruzan la ENGHo y la EPH.
   - Si es estadísticamente defendible, con referencias a cómo lo trata la literatura de
     incidencia internacional (consumo vs. ingreso como medida de bienestar).
   - Qué alternativa intermedia sería la más defendible y cuánto da.

3. **La lógica de la subdeclaración en el decil 10.** Mi intuición: si el decil 10 subdeclara
   ingresos, su ingreso real es mayor, así que la tasa real debería ser **menor** que la medida.
   Pero el proyecto agrega Ganancias y Bienes Personales que la simulación no capta, lo que la
   **sube**. Explicame con números qué efecto domina y si el tratamiento es coherente (¿se
   corrigió el numerador sin corregir el denominador, o al revés?).

4. **El tope de aportes.** Verificá que el tope de la base imponible de aportes
   (`params/lmi.csv`) esté bien aplicado año por año y que su efecto en los deciles altos sea
   el esperado.

5. **Parámetros legales.** Muestreá al menos 15 valores de `params/` (alícuotas, mínimos,
   escalas de Ganancias, topes) en años distintos y verificalos contra la norma original
   (InfoLEG, Boletín Oficial, ARCA). Listá los que no coinciden o no se pueden verificar.

6. **Errores de implementación.** Buscá bugs concretos: unidades, ponderadores, trimestres
   mal promediados, deciles mal armados, años desalineados entre fuentes, doble conteo.
   Verificá a mano un hogar de la EPH de punta a punta para un año.

## Formato de `docs/auditoria.md`

- Arriba, un veredicto en 5 líneas: ¿se puede publicar el resultado como está, con cambios o
  no?
- Hallazgos ordenados por cuánto mueven la conclusión, cada uno con: qué encontraste, cómo lo
  verificaste (script o fuente), cuántos puntos porcentuales mueve y qué recomendás.
- Separá claramente **errores** (algo está mal), **supuestos discutibles** (es una elección,
  hay alternativas) y **cosas verificadas que están bien**.
- Las explicaciones de los puntos 2 y 3 escritas para alguien que sabe economía pero no es
  especialista en incidencia: quiero poder defenderlas yo frente a un periodista o un
  economista.

Si algo no se puede verificar con los datos disponibles, decilo. No rellenes.
