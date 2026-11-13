# Auditoría externa — incidencia tributaria por decil, Argentina 2004-2024

Revisión hecha el 13/11/2026 sobre el estado del repositorio a esa fecha. No se modificó código,
parámetros ni resultados. Los scripts de verificación están en `auditoria/` (sólo leen) y cada
hallazgo indica cuál lo respalda. Cifras de 2024 salvo indicación; "pp" = puntos porcentuales de la
tasa total.

## Veredicto

1. **No publicar como está; sí con cambios.** El código hace lo que la documentación dice (las 14
   variantes × 21 años se reproducen con diferencia cero y un hogar verificado a mano coincide al
   centavo), pero el titular "perfil casi plano" no es un resultado robusto.
2. El perfil plano sale de **dos correcciones que actúan en un solo sentido** (decil 1: −10,5 pp;
   decil 10: +4,4 pp) más **una inconsistencia de escala** entre impuestos al trabajo e impuestos al
   consumo que aplana los deciles 2 a 9. Sin ellas el mismo modelo da regresivo abajo.
3. Hay dos errores concretos de cálculo (aguinaldo en el denominador sin impuestos en el numerador;
   mitad "consumidor" de las contribuciones al doble de escala que el IVA) y dos errores menores de
   parámetros. Ninguno, solo, cambia el signo; juntos mueven 1 a 3 pp.
4. Lo que sí se sostiene: tasa promedio de 25-27% sobre este conjunto de impuestos; deciles 3 a 8
   entre 24% y 29% en casi cualquier variante; el sistema **no es progresivo** medido contra el ingreso.
5. Cifras defendibles hoy: decil 1 ≈ 28-30% (rango 24-35), decil 10 ≈ 26% (rango 22-30). Es decir,
   **levemente regresivo en la punta baja y cercano al promedio en la alta**, igual que la literatura.

## Resumen de hallazgos, por cuánto mueven la conclusión

| # | Hallazgo | Tipo | Efecto 2024 | Script |
|---|---|---|---|---|
| 1 | Recursos del decil 1 = gasto: corrección unilateral | Supuesto discutible (decisivo) | D1 −10,5; D2 −1,4 | `a01`, `a02`, `a03` |
| 2 | Impuestos al trabajo al 75-123% de lo recaudado e indirectos al 37% | Error de coherencia | Con cobertura pareja: D1 +5,2; D5 +1,1; D9 −1,5 (pendiente D1-D9 pasa de −1 a +6 pp) | `a06`, `a07` |
| 3 | Decil 10: se corrige el numerador y no el denominador | Supuesto discutible; el "techo" es inválido | D10 +3,2 (Ganancias) y +1,2 (Bienes Personales); coherente: 22 a 28 | `a03` |
| 4 | Mitad "consumidor" de contribuciones a 2,0× la escala del IVA | Error | D1 −2,3; promedio −1,6; D10 −1,3 (si se corrige sola) | `a06`, `a07` |
| 5 | Reparto 50/50 de contribuciones patronales | Supuesto discutible | D1 entre 20,3 y 28,4 (ya publicado) | tablas del proyecto |
| 6 | Aguinaldo: está en el ingreso de T1 y T3, sin impuestos | Error | Promedio +0,6; D8-D10 +0,6 a +0,7 | `a06`, `a07` |
| 7 | Edición de la ENGHo usada para 2024 (2017/18, 6 años antes) | Supuesto no verificable | D1 declarado entre 31,7 y 38,8 según edición | `a01` |
| 8 | Aporte de jubilados al INSSJP (3%-6% del haber) no modelado | Omisión | +0,3 a +0,6 por decil (piso) | cálculo en sección 6 |
| 9 | Tope de aportes: falta el escalón de $6.750 (09/2007-02/2008) | Error de parámetro | < 0,05 en D10, sólo 2007-08 | `a04`, norma |
| 10 | Edad de hijo deducible 2017: 24 en vez de 18 | Error de parámetro | Despreciable | norma |
| 11 | Frases de README/metodología que no coinciden con las tablas | Error de documentación | — | `a06` |

---

## 1. ¿Por qué da plano si la literatura da regresivo?

### 1.1 Qué dice realmente la literatura

Verifiqué las cifras contra los PDF originales (no contra `docs/literatura_previa.md`). La premisa
"decil 1 bastante más alto, decil 10 más bajo" sólo describe el estudio de 1997. Desde 2008 los
estudios encuentran una **U**: decil 1 entre 8% y 22% por encima del promedio y decil 10 *también*
por encima.

| Estudio | Año datos | Fuente | D1 | D10 | Prom. | D1/prom | D10/prom | Decisión de método que explica la diferencia con este proyecto |
|---|---|---|---|---|---|---|---|---|
| Santiere, Gómez Sabaini y Rossignolo (CEPAL, Gestión Pública 20), Cuadro C p. 81 | 1997 | ENGH 96/97 | 58,7 | 39,8 | 42,4 | 1,38 | 0,94 | Todos los impuestos; ingreso ajustado a Cuentas Nacionales (+60%); adulto equivalente; seg. social 75/25. Los autores advierten que el D1 "responde en parte" a gasto > ingreso |
| Gómez Sabaini, Harriague y Rossignolo (UNC, 2011), diap. 38 | 2008 | ENGH 96/97 ajustada | 38,3 | 35,5 | 34,6 | 1,11 | 1,03 | Incluye retenciones y sociedades; ingresos corregidos por fuente |
| Gaggero y Rossignolo (CEFID-AR DT 40), Cuadro 44 | 2010 | EPH + ENGH 96/97 | 49,7 | 47,0 | 45,4 | 1,09 | 1,04 | Ídem. Sólo con los impuestos de este proyecto (suma propia): 31,7 / 28,0 / 29,4 |
| Rossignolo (CEQ WP 45), Tabla 11-5, suma propia | 2012 | ENGHo 12/13 | 44,6 | 45,5 | 39,6 | 1,13 | 1,15 | Ingreso de mercado sin ajustar; aportes jubilatorios no cuentan como impuesto |
| Gaskín (tesis UNLP, 2022), Cuadro 3.13 | 2017/18 | ENGHo 17/18 | — | — | — | 1,22 | 1,09 | Sólo IVA, selectivos, Ganancias y seg. social; ingreso declarado. Sólo publica presión relativa |
| Fernández Felices, Guardarucci y Puig (Estudios Económicos 2016) | 2004/05 | ENGH 04/05 | — | — | — | >1 | >1 | Sólo gráfico. Por ingreso: U. Por consumo: plano y sube en D10 |
| **Proyecto, sin correcciones** | 2024 | EPH + ENGHo 17/18 | 34,9 | 24,1 | 25,4 | 1,37 | 0,95 | |
| **Proyecto, principal** | 2024 | | 24,4 | 27,3 | 26,2 | 0,93 | 1,04 | |
| Proyecto, sin correcciones / principal | 2010 | | 40,4 / 22,1 | 25,0 / 29,0 | 26,4 / 27,2 | 1,53 / 0,81 | 0,95 / 1,07 | |

Dos lecturas:

- **Sin corregir, el proyecto es *más* regresivo abajo que la literatura reciente** (1,37-1,53 contra
  1,09-1,22). La causa es que usa ingreso declarado crudo; los estudios de Rossignolo corrigen
  subdeclaración por fuente en todos los deciles.
- **Con la corrección, el decil 1 queda por *debajo* del promedio (0,81-0,93)**, algo que ningún
  estudio publicado encuentra ordenando por ingreso. Para 2010, sobre los mismos impuestos,
  Gaggero-Rossignolo dan D1 = 31,7%: cae entre las dos versiones del proyecto (22,1 y 40,4).

En el decil 10 el proyecto (1,04-1,08) coincide con la literatura. La discrepancia está abajo.

### 1.2 Cuánto explica cada decisión (2024)

Descomposición secuencial (`auditoria/a01_reproducir_y_variantes.py`):

| Paso | D1 | D5 | D10 | Prom. |
|---|---|---|---|---|
| Ingreso declarado, Ganancias simulada, sin Bienes Personales | 34,9 | 26,3 | 22,9 | 25,0 |
| + Bienes Personales imputado al D10 | 34,9 | 26,3 | 24,1 | 25,4 |
| + Ganancias "faltante" en escala de encuesta | 34,9 | 26,3 | 27,3 | 26,5 |
| + recursos = gasto si gasto > ingreso (**principal**) | 24,4 | 26,3 | 27,3 | 26,2 |

Brecha D10 − D1: de −12,0 a +2,9 pp. De esos 14,9 pp, **10,5 son la corrección del decil 1 y 4,4
las dos imputaciones al decil 10**.

Otras decisiones, medidas con variantes propias sobre la versión de ingreso declarado:

| Decisión | Efecto en D1 | Efecto en D10 |
|---|---|---|
| Contribuciones 75% trabajador (criterio CEPAL) en vez de 50% | −3,0 | 0,0 |
| Contribuciones 100% trabajador (Fernández Felices, Gaskín) | −5,9 | +0,1 |
| ENGHo 2012/13 fija en vez de 2017/18 | +3,9 | +1,4 |
| ENGHo 2004/05 fija | −3,2 | +2,1 |
| Impuestos no incluidos (sociedades, cheque, combustibles, retenciones) | No calculable aquí. En Gaggero-Rossignolo suman 18,0 pp en D1, 19,0 en D10 y 16,0 en promedio: suben el nivel, casi no cambian la forma | |
| Ajuste de ingresos a Cuentas Nacionales por fuente | No replicable con los datos disponibles | |

---

## 2. La corrección del decil 1 por gasto

### 2.1 De dónde sale cada número

- **Ingreso:** EPH (INDEC), base de personas de cada trimestre 2004-2024, variable `IPCF` (ingreso per
  cápita familiar, de bolsillo), ponderada con `PONDERA` hasta 2015 y `PONDIH` desde 2016T2. Los
  deciles se arman con esa variable (`src/incidencia/eph.py`).
- **Gasto:** ENGHo (INDEC), tres ediciones: 2004/05, 2012/13 y 2017/18. Gasto de consumo = suma de
  `monto` del archivo de gastos (coincide con `gastot` del archivo de hogares); ingreso = `ingtoth`
  (`scripts/02_procesar_engho.py`).
- **Cómo se cruzan:** no se cruzan hogares. En cada ENGHo se calcula, para 20 grupos de ingreso per
  cápita, el consumo per cápita dividido por el ingreso medio de la encuesta. A cada decil de la EPH
  se le asigna, interpolando, el consumo que la ENGHo muestra para un grupo con el mismo ingreso
  *relativo a la media*. Entre ediciones se interpola en el tiempo; 2019-2024 usa sólo 2017/18.
- **La corrección** (`src/incidencia/incidencia.py`, `base = max(ipcf, consumo)`) se aplica **al total
  del decil**, no hogar por hogar. En 2024 el consumo imputado al decil 1 es 1,45 veces su ingreso y
  al decil 2, 1,06 veces.

Consecuencia que hay que tener clara: la frase "cuando el gasto declarado de un hogar supera su
ingreso declarado" no describe lo que se hace. Ningún hogar de la EPH declara gasto. Es un cociente
de 2017/18 trasladado al decil 1 de 2024.

### 2.2 Qué muestra la ENGHo 2017/18 hogar por hogar (`auditoria/a02_engho_decil1.py`)

| Decil de ingreso | 1 | 2 | 3 | 5 | 8 | 10 | Total |
|---|---|---|---|---|---|---|---|
| Gasto / ingreso declarado | 1,45 | 1,07 | 0,95 | 0,88 | 0,77 | 0,63 | 0,77 |
| Mediana del cociente por hogar | 1,20 | 0,89 | 0,83 | 0,75 | 0,68 | 0,62 | 0,75 |
| % de personas en hogares con gasto > ingreso | 58 | 42 | 36 | 29 | 22 | 16 | 30 |
| % con gasto > 2 × ingreso | 24 | 8 | 5 | 4 | 2 | 1 | 5 |
| Gasto / max(ingreso, gasto) hogar por hogar | 0,90 | 0,83 | 0,79 | 0,75 | 0,71 | 0,60 | 0,69 |

- Gasto mayor que ingreso **no es un fenómeno del decil 1**: le pasa al 30% de la población y al 16%
  del decil 10.
- El exceso del decil 1 lo produce una minoría: sin el 24% de personas con gasto mayor al doble del
  ingreso, el cociente del decil baja de 1,45 a 0,98.
- Ordenando por *consumo*, el decil 1 gasta 0,34 de su ingreso. Es la imagen espejo: quien queda
  último en una variable medida con ruido tiene, en promedio, la otra variable más alta. Sólo 41% de
  las personas del decil 1 de ingreso están en el decil 1 de consumo.
- No es consumo en especie (0,6% del gasto del decil) ni hogares con ingreso cero (0,5% del decil).

### 2.3 ¿Es defendible?

**La idea de fondo sí; la forma en que se aplicó, no del todo.**

La literatura internacional acepta que el ingreso corriente de los más pobres subestima su nivel de
vida y que el consumo es mejor medida de bienestar de largo plazo (Poterba 1989; Meyer y Sullivan
2003; Deaton 1997; Caspersen y Metcalf 1994 muestran que el IVA parece mucho menos regresivo contra
ingreso permanente). El manual CEQ (Enami, Higgins y Lustig, 2ª ed., vol. 1, p. 273, que leí
directamente) propone, siguiendo al BID (2009), calcular los impuestos indirectos como proporción del
consumo y aplicar esa proporción al ingreso, precisamente para que no aparezca una regresividad
espuria.

Pero hay tres objeciones que un economista va a hacer:

1. **Es unilateral.** El método CEQ se aplica a *todos* los hogares; el proyecto, sólo donde el gasto
   del decil supera al ingreso. Aplicado a todos, el decil 10 pasa a pagar 34% y el sistema resulta
   progresivo (fila H abajo). Corregir sólo abajo fabrica el perfil plano. `docs/validacion.md` cita
   el manual como respaldo sin mencionar esta diferencia.
2. **Es por construcción.** Si recursos = gasto, la tasa del decil 1 es el impuesto por peso de
   consumo (22,3%) más sus impuestos directos (2,1%). No puede dar otra cosa que algo cercano al
   promedio. `docs/metodologia.md` (sección 5 bis) lo admite; el README, no.
3. **Mezcla dos medidas de bienestar.** El decil 1 se mide contra consumo y los otros nueve contra
   ingreso, con hogares ordenados por ingreso.

### 2.4 Alternativas y cuánto dan (`auditoria/a03_alternativas_d1_d10.py`)

| Tratamiento de los recursos | D1 | D2 | D5 | D9 | D10 | Prom. |
|---|---|---|---|---|---|---|
| A. Ingreso declarado | 34,9 | 27,5 | 26,3 | 25,5 | 27,3 | 26,5 |
| B. Proyecto: max(ingreso, gasto) por decil | 24,4 | 26,1 | 26,3 | 25,5 | 27,3 | 26,2 |
| C. max(ingreso, gasto) hogar por hogar, todos los deciles | 21,9 | 21,6 | 22,9 | 24,1 | 26,3 | 24,2 |
| E. Promedio de ingreso y gasto, sólo donde gasto > ingreso | 28,6 | 26,8 | 26,3 | 25,5 | 27,3 | 26,3 |
| F. Promedio de ingreso y gasto, todos los deciles | 28,6 | 26,8 | 27,9 | 28,8 | 32,6 | 29,6 |
| G. D1 con el cociente del segundo veintil (1,15) | 28,4 | 27,5 | 26,3 | 25,5 | 27,3 | 26,5 |
| H. CEQ simétrico: indirectos como % del consumo, todos | 25,0 | 26,3 | 28,9 | 30,6 | 34,3 | — |
| I. Todo sobre consumo | 24,4 | 26,1 | 29,6 | 33,0 | 40,6 | 33,5 |

Con la mediana del cociente (1,20) en lugar de la media, el decil 1 da 29,4%.

**La alternativa intermedia más defendible es D1 ≈ 28-29,5%** (E, G o mediana): trata ingreso y gasto
como dos mediciones ruidosas del mismo recurso en vez de elegir siempre la mayor, y no depende del
24% de hogares con cocientes extremos. Queda 2 a 3 pp sobre el promedio, que es lo que encuentra la
literatura reciente (D1/promedio entre 1,09 y 1,22 equivaldría a 29-32%).

**Recomendación.** No presentar B como "principal". Publicar dos lecturas completas y coherentes:
contra ingreso (A: regresivo abajo) y contra consumo (I: progresivo), como hacen Fernández Felices et
al. y Gaskín. Si hace falta una sola cifra para el decil 1: 28-30%, con rango 24-35.

---

## 3. La subdeclaración en el decil 10

### 3.1 La intuición es correcta

Si falta ingreso, corregirlo baja la tasa; si faltan impuestos, corregirlos la sube. Agregar un
impuesto ΔT junto con el ingreso ΔY que lo genera **sube la tasa sólo si ΔT/ΔY supera la tasa que
el decil ya tenía** (22,9% antes de imputaciones). Todo depende de qué tasa media pagó el ingreso
que la encuesta no ve.

### 3.2 Qué hace el proyecto

- **Principal (27,3%):** suma al numerador Ganancias faltante y Bienes Personales, multiplicados por
  0,37 (consumo de encuesta / consumo de Cuentas Nacionales). **Al denominador no le suma nada.** La
  justificación es que el factor 0,37 "equivale" a suponer que el ingreso del decil 10 está subcaptado
  en la misma proporción. Es una hipótesis sobre el denominador, no una corrección.
- **Techo (31,2%):** suma todo lo recaudado y, al denominador, el ingreso que las declaraciones
  juradas muestran por encima de la EPH.
- **Piso (24,1%):** la documentación dice "sólo lo simulado", pero incluye 1,2 pp de Bienes Personales
  imputado. El piso sin imputaciones es 22,9%.

### 3.3 Los números (millones de pesos anuales, EPH expandida al país)

| Concepto | Monto | % del ingreso D10 |
|---|---|---|
| Ingreso del decil 10 antes de impuestos, según encuesta (Y0) | 71.583.719 | 100 |
| Impuestos ya asignados (T0) | 16.402.927 | 22,9 |
| Ganancias recaudada que la simulación no capta (G) | 6.267.471 | 8,8 |
| Bienes Personales | 2.288.113 | 3,2 |
| Ingreso faltante según declaraciones juradas (cota inferior) | 9.234.936 | 12,9 |

| Tratamiento | Impuesto agregado | Ingreso agregado | Tasa D10 |
|---|---|---|---|
| Nada | 0 | 0 | 22,9 |
| Principal: 37% de (G + BP), sin ingreso | 3.120.789 | 0 | 27,3 |
| Todo (G + BP), sin ingreso | 8.512.790 | 0 | 34,8 |
| Techo publicado | 8.512.790 | 9.188.744 | 30,8 (31,2 con promedio trimestral) |
| Coherente, ingreso faltante gravado al 35% (máximo legal) | 8.512.790 | 17.817.490 | 27,9 |
| Coherente, gravado al 24,4% (tasa efectiva de las DDJJ 2023) | 8.512.790 | 25.541.349 | 25,7 |
| Coherente, gravado al 15% | 8.512.790 | 41.574.144 | 22,0 |

"Coherente" = sumar todo el impuesto y el ingreso mínimo necesario para generarlo, G / tasa.

### 3.4 Qué efecto domina

- **Ganancias, sola, es casi neutra.** La tasa efectiva de quienes presentan declaración jurada
  (impuesto determinado / resultado neto) fue 24,4% en 2023 y 19,2% en 2017: muy cerca de la tasa
  que el decil ya tenía. Sumar el impuesto con su ingreso deja al decil 10 donde estaba.
- **Lo que sube la tasa es Bienes Personales** (+3,2% del ingreso sin ingreso asociado) y, si ese
  ingreso se consume, los impuestos indirectos que paga (lleva 25,7 a 28,7).
- **La principal equivale a suponer** que al decil 10 le falta 28% de ingreso y que ese ingreso pagó
  43% entre Ganancias y Bienes Personales. Es alto: el máximo legal de Ganancias es 35%.
- **El techo no es un techo válido.** Implica que el ingreso faltante pagó 68% sólo de Ganancias (94%
  en 2017). Eso prueba que el ingreso faltante está subestimado al menos a la mitad; la propia
  metodología lo llama "cota inferior". Usar una cota inferior del denominador da una cifra
  imposible, no un extremo plausible.

**Respuesta corta:** se corrigió el numerador sin corregir el denominador. Con tratamiento coherente
el decil 10 queda entre 22% y 28% (hasta 30% si se suman indirectos sobre el ingreso faltante), con
centro en 26%. La principal (27,3%) está dentro del rango pero en su mitad alta; el techo (31,2%)
está fuera.

**Recomendación.** Reemplazar "principal / techo" por el rango coherente, declarar la tasa supuesta
sobre el ingreso faltante y eliminar `altos_registros`. Separar siempre Bienes Personales (es
patrimonio, no ingreso).

---

## 4. Errores

### 4.1 Escala incoherente entre impuestos al trabajo e impuestos al consumo

**Qué.** Fracción de lo recaudado en el país que el modelo asigna a los hogares (EPH expandida):

| | 2004 | 2010 | 2017 | 2024 |
|---|---|---|---|---|
| Aportes personales | 2,87 | 1,26 | 1,11 | 1,23 |
| Contribuciones patronales | 0,97 | 0,83 | 0,70 | 0,75 |
| Ganancias personas humanas | 0,55 | 0,58 | 0,61 | 0,44 |
| IVA, Ingresos Brutos, Internos, Bienes Personales | 0,44 | 0,50 | 0,48 | 0,37 |

Los impuestos al trabajo entran casi enteros (la EPH capta bien el salario registrado) y los
indirectos a menos de la mitad (el consumo de encuesta es 37-50% del de Cuentas Nacionales). En 2024
los directos son 43% de lo que el modelo asigna y 27,5% de lo efectivamente recaudado. En la tasa
promedio de 26,2%, los aportes pesan 6,4 pp (serían 2,7 con la composición de la recaudación) y el
IVA 7,3 (serían 10,5).

Como los impuestos al trabajo crecen con el ingreso y los indirectos caen, sobreponderar los primeros
inclina el perfil hacia la progresividad. La documentación dice que las tasas son válidas "si la
subcobertura es proporcional entre deciles"; bajo esa misma hipótesis el ingreso también está
subcaptado y los impuestos al trabajo deberían reducirse en igual proporción.

**Cómo lo verifiqué.** `auditoria/a06_bugs.py` (bloque 5) y `auditoria/a07_efectos.py` (variante c:
cada impuesto reescalado para que lo asignado sea la misma fracción, 53%, de lo recaudado, manteniendo
el promedio).

**Cuánto mueve.**

| | D1 | D2 | D3 | D5 | D8 | D9 | D10 | Prom. |
|---|---|---|---|---|---|---|---|---|
| Principal publicada | 24,4 | 26,1 | 26,3 | 26,3 | 25,9 | 25,5 | 27,3 | 26,2 |
| Principal, misma cobertura | 29,6 | 29,8 | 28,6 | 27,4 | 25,0 | 24,0 | 27,1 | 26,2 |
| Ingreso declarado publicada | 34,9 | 27,5 | 26,3 | 26,3 | 25,9 | 25,5 | 27,3 | 26,5 |
| Ingreso declarado, misma cobertura | 42,4 | 31,4 | 28,6 | 27,4 | 25,0 | 24,0 | 27,1 | 26,5 |

**Aun con la corrección de recursos del decil 1, el perfil resulta regresivo del decil 1 al 9 (29,6 a
24,0).** La meseta "25-26%" de los deciles 2 a 9 depende de esta inconsistencia.

Salvedad: la cobertura pareja es una sensibilidad, no la verdad. Parte del exceso de aportes es real
(empleados públicos provinciales que aportan a cajas no incluidas en la recaudación nacional) y parte
del IVA no recae en hogares. La cobertura correcta de cada impuesto no se puede determinar sin una
cuenta de ingresos de los hogares.

**Recomendación.** Declararlo como limitación de primer orden, publicar la variante de cobertura
pareja y explicar que el nivel promedio coincide con la macro por compensación: impuestos incluidos
18,4% del PIB e ingreso del denominador 37% del PIB, con numerador asignado de 52%.

### 4.2 Mitad "consumidor" de las contribuciones patronales

**Qué.** IVA, Ingresos Brutos e Internos se asignan como recaudación / consumo privado de Cuentas
Nacionales × consumo de encuesta. La mitad de las contribuciones que se supone trasladada a precios
se reparte de otra forma: la mitad de lo *simulado sobre la EPH*, entera, sobre el consumo de encuesta
(`incidencia.py`, `contrib_consumidor`). Por peso de consumo resulta 4,67% contra 2,29% con el
criterio del IVA: 2,04 veces (2,22 en 2004; 1,68 en 2010; 1,46 en 2017). El factor cambia año a año,
así que también contamina la serie.

**Cómo.** `auditoria/a06_bugs.py` (bloque 4), `auditoria/a07_efectos.py` (variante b).

**Cuánto.** Corregido solo: principal D1 24,4 → 22,0; promedio 26,2 → 24,6; D10 27,3 → 26,0. Con
ingreso declarado, D1 34,9 → 31,6. Es un caso particular de 4.1 y va en sentido contrario para el
decil 1; no deben sumarse.

**Recomendación.** Usar para esa mitad `0,5 × ss_empleadores / consumo_privado`, igual que los demás
impuestos trasladados a precios.

### 4.3 Aguinaldo

**Qué.** `P21` no incluye aguinaldo (coincide con la suma de componentes sin `PP08J1` en 95-99% de los
registrados), pero el ingreso total del hogar sí. En el primer y tercer trimestre 34-36% de los
asalariados registrados declara aguinaldo, por 16-17% de la masa de `P21`; lo mismo en jubilaciones
(`V21_M` es 17% de `V2_M`). El modelo calcula aportes, contribuciones y Ganancias sobre `P21` y
divide por un ingreso que en esos dos trimestres incluye el aguinaldo sin sus impuestos.

**Cómo.** `auditoria/a06_bugs.py` (bloques 1 y 2). Las tasas oscilan todos los años: 2024, total
T1 24,0 / T2 25,6 / T3 24,8 / T4 25,6; aportes 6,0 / 6,9 / 6,3 / 6,7.

**Cuánto.** Usando sólo T2 y T4 (`auditoria/a07_efectos.py`, variante a): promedio 26,2 → 26,8; D10
27,3 → 27,9; D8 y D9 +0,7; D1 +0,4. En 2017 igual (+0,6 en promedio).

**Recomendación.** Sumar aportes y contribuciones sobre el aguinaldo declarado, o excluirlo del
ingreso.

### 4.4 Parámetros

- **Tope de aportes, 09/2007 a 02/2008.** `params/lmi.csv` pasa de $6.000 a $7.256. Falta el escalón
  de 84,375 MOPRE = **$6.750** desde septiembre de 2007 (Decreto 1346/2007, art. 5; RG AFIP 2340/2007).
  Además 7.256 / 6.750 = 1,075, el aumento de marzo de 2008. Efecto: menos de 0,05 pp en el decil 10.
- **Edad de hijo deducible en 2017.** `params/ganancias.yaml` tiene 24 años; la Ley 27.346 (vigente
  desde el período 2017) fija "menor de dieciocho (18) años". Efecto despreciable.

### 4.5 Documentación

- README: "deciles 2 a 9 entre 25% y 26%". La tabla da 25,2 a 26,5 (D2 26,1; D3 26,3; D4 26,5; D5 26,3).
- Metodología, sección 5: el piso `altos_sin_corregir` no es "sólo lo simulado"; incluye Bienes
  Personales (1,2 pp).
- README y metodología describen la corrección de recursos como si comparara gasto e ingreso de cada
  hogar; es por decil y con gasto imputado de otra encuesta.
- `docs/validacion.md` presenta el método CEQ como equivalente a la corrección; no lo es (2.3).

---

## 5. Supuestos discutibles

Además de los hallazgos 1 y 3 (secciones 2 y 3):

- **Reparto 50/50 de contribuciones patronales.** Ya publicado como variante: D1 entre 20,3 y 28,4.
  No hay evidencia argentina que lo ancle; la literatura local usa 75/25 o 100% trabajador.
- **ENGHo 2017/18 para 2019-2024.** El cociente gasto/ingreso se supone constante durante seis años
  con pandemia y tres recesiones. Con otras ediciones el D1 declarado va de 31,7 a 38,8. No verificable.
- **Reparto de Ganancias faltante entre deciles.** En 2024, 99,5% al decil 10. Parte de lo que falta
  es retención a asalariados que la simulación no reproduce (cubre 12% de lo recaudado en 2024, 37% en
  2016), y esos asalariados no están todos en el 0,4% superior. Sesga hacia arriba el decil 10.
- **Año fiscal 2023 para 2024**, escalado por el ingreso medio de la EPH (×3,1). El impuesto
  determinado así extrapolado (8,19 billones) supera lo recaudado (7,15).
- **Empleo público.** Se le calculan aportes pero no contribuciones patronales.
- **Aporte de jubilados al INSSJP** (Ley 19.032: 3% hasta el haber mínimo, 6% sobre el excedente):
  no modelado. Las jubilaciones son 8% a 20% del ingreso según el decil; con el piso de 3% faltan
  entre 0,3 pp (D1 y D10) y 0,6 pp (D5 y D6).
- **Decreto 1242/2013, art. 6:** +30% de deducciones en Patagonia, no modelado.
- **Deducciones generales de Ganancias** no modeladas (ya declarado por el proyecto).

---

## 6. Verificado y está bien

**Reproducibilidad.** Recalculé las 14 variantes para los 21 años desde `data/processed`: diferencia
máxima con `outputs/tables/tasas_por_decil_anual.csv` = 0 (`a01`). Los 7 tests pasan.

**Un hogar de punta a punta** (`auditoria/a05_hogar_a_mano.py`, EPH 2019T2, hogar
`TQRMNOPPRHMLKPCDEFPCH00635922_1`): jefe de 41 años, asalariado registrado privado, establecimiento
de 41 a 100 personas, ingreso de bolsillo $140.000; cónyuge inactiva e hijos de 1 y 5 años. Leí el
archivo crudo de INDEC sin usar el lector del proyecto y recalculé con fórmulas propias (bisección en
lugar de la iteración del proyecto) y parámetros transcriptos de la norma:

| | A mano | Proyecto |
|---|---|---|
| Bruto mensual | 198.559,66 | 198.559,66 |
| Aporte jubilatorio (11%, con tope) | 13.408,69 | 13.408,69 |
| INSSJP / obra social (3% c/u) | 3.656,92 | 3.656,92 |
| Ganancias mensual | 37.837,13 | 37.837,13 |
| Contribuciones patronales (20,4% sobre bruto − 7.003,68) | 39.077,42 | 39.077,42 |

El hogar cae en el decil 10. Los totales del decil recalculados (personas, IPCF, Ganancias, aportes,
contribuciones) coinciden con la fila publicada, y las tasas del decil rehechas a mano (aportes
6,72%; Ingresos Brutos 3,02%; contribuciones-consumidor 1,98%; Ganancias 2,61%) coinciden con la
función del proyecto.

**Deciles y ponderadores.** Un algoritmo independiente asigna el mismo decil a las 50.475 personas de
2019T2. Cada decil tiene 9,99-10,01% de la población. La suma de `PONDIH` iguala la de `PONDERA`
(28,33 millones); se descartan los hogares con `PONDIH` = 0 (24% de la población, reponderada por
INDEC), que es el uso correcto. No hay `IPCF` ni `P21` negativos entre los hogares válidos.

**Unidades.** Las conversiones entre millones anuales del país y pesos mensuales de la EPH en
`incidencia.py` y `09_ingresos_altos.py` son correctas.

**Promedio de trimestres.** El promedio simple de tasas no introduce sesgo apreciable por inflación:
2024, promedio por trimestre 25,2 / 26,8 / 26,1 / 26,9 (la oscilación es el aguinaldo, 4.3).

**Tope de aportes** (`auditoria/a04_tope_aportes.py`). Se aplica mes a mes sobre el bruto y ningún
aporte simulado supera 11% del tope. El tope es 3,0-3,2 veces el RIPTE entre 2006 y 2020 y baja a 2,3
en 2024. Efecto, como se espera, sólo en el decil 10:

| Trimestre | Registrados del D10 sobre el tope | Aportes / bruto en D10 | Ídem sin tope | Efecto en la tasa del D10 |
|---|---|---|---|---|
| 2006T2 | 6,8% | 10,5% | 11,4% | −0,31 pp |
| 2008T4 | 5,5% | 13,2% | 13,9% | −0,24 pp |
| 2012T2 | 5,2% | 13,4% | 14,0% | −0,24 pp |
| 2019T2 | 6,5% | 13,5% | 14,1% | −0,23 pp |
| 2024T3 | 10,9% | 12,3% | 14,0% | −0,61 pp |

(En 2006 la alícuota es menor porque el sector privado aportaba 7% a las AFJP.)

En el decil 9 el efecto es menor a 0,03 pp. No se aplica el tope por separado al aguinaldo (porque el
aguinaldo no se grava: ver 4.3).

**Cruce ENGHo-EPH.** La participación del decil 1 en el ingreso es 1,76% en la ENGHo 2017/18 y 1,77%
en la EPH 2024: el traslado por ingreso relativo es consistente.

**Parámetros legales.** Fuente primaria: texto de la norma en biblioteca.afip.gob.ar o
argentina.gob.ar/normativa, leído en esta auditoría. "DNIAF" = PDF del Ministerio de Economía incluido
en el proyecto (oficial, no es la norma).

| # | Parámetro | Valor en `params/` | Fuente | Resultado |
|---|---|---|---|---|
| 1 | Ganancia no imponible 2006 | 6.000 | Dto. 314/2006 art. 1 | Coincide |
| 2 | Cónyuge 2006 | 4.800 | Ídem | Coincide |
| 3 | Hijo 2006 | 2.400 | Ídem | Coincide |
| 4 | Reducción de deducciones 2006, tramos | 45.500 / 65.000 / 91.000 / 130.000 / 195.000 / 221.000 | Dto. 314/2006 art. 2 | Coincide |
| 5 | Ganancia no imponible 2016 | 42.318 | Dto. 394/2016 art. 1 | Coincide |
| 6 | Cónyuge / hijo 2016 | 39.778 / 19.889 | Ídem | Coincide |
| 7 | Ganancia no imponible 2017 | 51.967 | Ley 27.346 | Coincide |
| 8 | Cónyuge / hijo 2017 | 48.447 / 24.432 | Ídem | Coincide |
| 9 | Escala 2017, límites y alícuotas | 20.000 … 320.000; 5% a 35% | Ídem | Coincide |
| 10 | Edad máxima de hijo 2017 | 24 | Ídem: 18 | **No coincide** |
| 11 | Dto. 1242/2013, umbrales | 15.000 / 25.000 | Dto. 1242/2013 arts. 2 y 5 | Coincide |
| 12 | Incremento 2019 de GNI y deducción especial | +20% (103.018,79 / 494.490,17) | Dto. 561/2019 art. 1; DNIAF | Coincide |
| 13 | Ley 27.617, umbrales | 150.000 / 173.000 | Ley 27.617 | Coincide |
| 14 | Contribuciones desde 2020 | 20,40% / 18% | Ley 27.541 art. 19 | Coincide |
| 15 | Detracción desde 2020 | 7.003,68 | Ley 27.541 art. 22 | Coincide |
| 16 | Obra social | 3% | Ley 23.660 art. 16 | Coincide |
| 17 | Tope jubilatorio 04/2007 | 75 MOPRE = 6.000 | Ley 26.222 | Coincide |
| 18 | Tope jubilatorio 09/2007 | 6.000 | Dto. 1346/2007; RG AFIP 2340: 6.750 | **No coincide** |
| 19 | Tope INSSJP 2007 | 4.800 | RG AFIP 2340/2007 | Coincide |
| 20 | Fin del IVA 0% canasta | 31/12/2019 | Dto. 567/2019 art. 2 | Coincide |
| 21 | Deducciones y escala 2024 | 3.503.688,17; 16.817.703,23; 1.360.200 … 41.316.075 | DNIAF | Coincide (fuente secundaria) |
| 22 | Deducciones 2007-2023 (muestra de 13 valores) | 36.000; 43.200; 62.208; 74.649,60; 203.126,40; 249.441,60; 321.205,97; 594.533,62; 1.212.311,24; 2.168.079,35; escalas 2020 y 2022; cedular 10/2023 | DNIAF | Coincide (fuente secundaria) |
| 23 | Tope jubilatorio, 10 meses entre 2011 y 2024 | p. ej. 16.210,42; 19.066,69; 28.000,88; 31.166,10; 105.234,81; 1.471.621,62; 2.359.712,33 | Resoluciones ANSES citadas por consejos profesionales y prensa: 16.213,72; 19.070,55; 28.000,65; 31.167,56; 105.233,32; 1.471.616,10; 2.359.712,22 | Diferencias de hasta 0,02% por encadenar con el haber mínimo. Sin efecto |

**No pude verificar contra el texto de la norma:**

- Contribuciones 21% / 17% para 2003-2018: el texto recuperado del Dto. 814/2001 muestra el 16%
  original; no localicé el texto modificado por la Ley 25.453.
- Cronograma de la Ley 27.430 para 2018 y 2019 (20,70% / 17,50%; 20,40% / 18,00%; detracción 2.400):
  las fuentes secundarias que encontré se contradicen en el inciso b de 2018 (17,00% o 17,50%).
- Dto. 279/2008 (7.256 y 7.800): no localicé el texto; sólo lo citan los considerandos del Dto.
  1448/2008.
- Aporte reducido de 7% a AFJP y su vigencia hasta 12/2007.
- Aporte de 3% de trabajadores activos al INSSJP (leí el artículo; no el inciso).
- Tabla del régimen cedular de enero a junio de 2024 (el proyecto ya la declara aproximada).

---

## 7. Lo que no se puede resolver con los datos disponibles

- **El ingreso verdadero de los hogares.** Sin cuenta de ingresos del sector hogares no se sabe qué
  parte de cada impuesto recae sobre la población de la encuesta (4.1) ni cuánto ingreso le falta al
  decil 10 (sección 3). Es el límite real del estudio.
- **Si el decil 1 desahorra o subdeclara.** La ENGHo permite ver que el exceso de gasto se concentra en
  una minoría con cocientes extremos, no distinguir la causa.
- **El cociente gasto/ingreso de 2024.** No hay encuesta de gastos posterior a 2017/18.
- **Las comparaciones con la literatura por impuesto** más allá de las de 1.1: los demás estudios no
  publican tabla numérica por decil, o no pude abrirlos (Gómez Sabaini y Rossignolo, OIT 2009).

## 8. Qué cambiaría antes de publicar

1. Corregir aguinaldo (4.3) y la escala de las contribuciones trasladadas (4.2); corregir los dos
   parámetros (4.4).
2. Reemplazar "principal" por dos lecturas simétricas: contra ingreso y contra consumo.
3. Publicar la variante de cobertura pareja (4.1) y decir explícitamente que la forma del perfil en
   los deciles 2 a 9 depende de ella.
4. Decil 10: rango coherente 22-30% con centro en 26%; eliminar el techo de 31,2%.
5. Titular sugerido: "El sistema no es progresivo: los deciles medios pagan entre 24% y 29% de su
   ingreso; el decil más pobre paga probablemente algo más (28-30%, con mucha incertidumbre) y el más
   rico algo parecido al promedio".

## Fuentes consultadas en esta auditoría

- Santiere, Gómez Sabaini y Rossignolo (2002): https://repositorio.cepal.org/server/api/core/bitstreams/81e1b704-6b28-4aab-9c78-dc6f04d7b65d/content
- Gaggero y Rossignolo (2011): https://www.iade.org.ar/system/files/dt40.pdf
- Gómez Sabaini, Harriague y Rossignolo (2011): https://www.eco.unc.edu.ar/files/ief/workshops/2011/01dic11_Rossignolo_Workshop.pdf
- Rossignolo, CEQ WP 45: http://repec.tulane.edu/RePEc/ceq/ceq45.pdf
- Gaskín (2022): https://www.me.econo.unlp.edu.ar/wp-content/uploads/Tesis-Josefina-Paz-Gaskín.pdf
- Fernández Felices, Guardarucci y Puig (2016): https://www.redalyc.org/journal/5723/572368182002/572368182002.pdf
- CEQ Handbook, 2ª ed., vol. 1: https://www.brookings.edu/wp-content/uploads/2017/04/CEQ-Handbook-2022-Vol-1.pdf
- RG AFIP 2340/2007: https://www.argentina.gob.ar/normativa/nacional/norma-134739/texto
- Normas en https://biblioteca.afip.gob.ar/dcp/ : `DEC_C_000314_2006_03_21`, `DEC_C_001346_2007_10_04`,
  `DEC_C_001448_2008_09_10`, `DEC_C_001242_2013_08_27`, `DEC_C_000394_2016_02_22`,
  `LEY_C_027346_2016_12_22`, `DEC_C_000561_2019_08_14`, `DEC_C_000567_2019_08_15`,
  `LEY_C_027541_2019_12_21`, `LEY_C_027617_2021_04_08`, `LEY_C_026222_2007_02_27`,
  `LEY_C_023660_1988_12_29`, `LEY_C_019032_1971_05_13`, `DEC_C_000814_2001_06_20`

Las referencias de la sección 2.3 a Poterba, Meyer y Sullivan, Deaton y Caspersen y Metcalf son de
memoria: no las abrí en esta auditoría y conviene confirmarlas antes de citarlas.
