# Validación

Tablas completas en `outputs/tables/validacion_*.csv`. Se reportan las discrepancias tal
como salen.

## 1. Contra la recaudación oficial (DNIAF)

Cociente simulado / recaudado, con la simulación expandida a la población total del país.

| Impuesto | 2004-2008 | 2009-2025 | Lectura |
|---|---|---|---|
| Aportes personales | 2,54 a 3,09 | 1,09 a 1,42 | Hasta 2008 la recaudación no incluía los aportes a AFJP. Sin ellos, 2008 da 1,27 |
| Contribuciones patronales | 0,94 a 1,05 | 0,65 a 0,94 | La simulación sólo cubre empleadores privados |
| Ganancias personas físicas | 0,17 a 0,21 | 0,13 a 0,40 | Subdeclaración, ingresos altos ausentes de la EPH, independientes y rentas de capital no simulados |

- **IVA:** lo recaudado por peso de consumo privado es entre 73% y 87% del contenido legal
  de la canasta de la ENGHo. La brecha combina evasión y exenciones no captadas.
- **Cobertura:** el consumo de encuesta expandido al país es entre 37% y 55% del consumo
  privado de Cuentas Nacionales. El modelo asigna a los hogares de la encuesta esa misma
  proporción de los impuestos indirectos; el resto corresponde a consumo que las encuestas
  no captan.
- **Ingresos altos:** el impuesto determinado en las declaraciones juradas es entre 53% y
  82% de lo recaudado por Ganancias de personas humanas en el mismo año (2004-2024; 2025 usa
  las declaraciones de 2024 extrapoladas) (el resto son
  retenciones a asalariados que no presentan declaración). En el punto de empalme, lo
  declarado al fisco es entre 1,2 y 1,8 veces lo que la EPH muestra para el mismo número
  de personas. Detalle por año en `outputs/tables/ajuste_altos_ingresos.csv`.
- Los impuestos incluidos suman entre 13,7% y 22,0% del PIB.

## 2. Contra estudios previos

Relevamiento hecho por un agente auxiliar (`docs/literatura_previa.md`). **No
revisé personalmente cada cuadro**: las cifras deben contrastarse con la fuente antes de
citarlas. Presión tributaria total, % del ingreso.

| Estudio | Datos | D1 | D5 | D10 | Promedio |
|---|---|---|---|---|---|
| Santiere, Gómez Sabaini y Rossignolo (CEPAL) | 1997 | 58,7 | 43,6 | 39,8 | 42,4 |
| Gómez Sabaini, Harriague y Rossignolo | 2008 | 38,3 | 34,3 | 35,5 | 34,6 |
| Gaggero y Rossignolo (CEFID-AR DT 40) | 2010 | 49,7 | 43,0 | 47,0 | 45,4 |
| Rossignolo (CEQ WP 45), suma propia del agente | 2012/13 | 44,6 | 34,7 | 45,5 | 39,6 |
| **Este proyecto, principal (ingreso declarado)** | 2010 | 37,3 | 26,3 | 28,7 | 27,0 |
| Este proyecto, variante `recursos_gasto` | 2010 | 20,3 | 26,3 | 28,7 | 26,4 |

Diferencias que explican la distancia de nivel:

- Esos estudios reparten **toda** la recaudación (incluidas Ganancias de sociedades,
  impuesto al cheque, combustibles y, en algunos, retenciones). Este proyecto cubre 56% a
  71% de la recaudación.
- Ajustan los ingresos a Cuentas Nacionales y corrigen subdeclaración; la medida principal de
  este proyecto no (la variante `ajuste_cn` lo hace para salarios e ingreso mixto).
  Por eso su decil 10 muestra mucha más carga: es la principal discrepancia y va en la
  dirección esperada.
- Reparto de contribuciones patronales distinto (75/25 en CEPAL 1997; 100% trabajador en
  Fernández Felices et al.).
- En IVA e Ingresos Brutos los órdenes de magnitud coinciden: Gaggero y Rossignolo dan
  para 2010 IVA 15,8 / 11,8 / 9,3 e Ingresos Brutos 6,2 / 5,1 / 4,3 (D1 / D5 / D10); este
  proyecto (principal) da IVA 19,4 / 9,2 / 6,4 e Ingresos Brutos 8,7 / 4,1 / 2,9.
- Forma del perfil: los estudios previos encuentran una U (más carga en ambas puntas).
  Aquí la punta alta no aparece porque la EPH no capta los ingresos altos, y la punta baja
  depende de cómo se mida el ingreso del decil 1.

**Tratamiento del decil 1.** Según la lectura del agente, el manual CEQ (Enami, Higgins y
Lustig, cap. 6, sección 3.7.1, 2ª ed.) recomienda, cuando el consumo supera al ingreso,
no restar el impuesto calculado sobre el consumo sino reescalarlo al ingreso disponible.
**No es equivalente** a la corrección de recursos de la variante `recursos_gasto`: el manual
(vol. 1, p. 273, verificado en la auditoría) la aplica a todos los hogares, y el proyecto
sólo donde el gasto del decil supera a su ingreso. Aplicada a todos, el decil 10 sube a
34% y el sistema resulta progresivo (`docs/auditoria.md`, 2.3 y 2.4).

Sin verificar: Gómez Sabaini y Rossignolo (OIT 2009), Fernández Felices et al. (2016),
Dondo, Hanni, Martner y Podestá (2015).

## 3. Contra Pessino et al. (~2018) y el International Tax Observatory (2026)

| Decil | 1 | 2 | 3 | 5 | 9 | 10 | 1% más rico |
|---|---|---|---|---|---|---|---|
| Pessino et al., ~2018 (Argendata) | 35,8 | 30,8 | 27,8 | 25,6 | 24,2 | 24,9 | — |
| Este proyecto, 2018 (principal) | 33,6 | 25,3 | 25,0 | 25,7 | 24,5 | 24,0 | — |
| ITO 2026, según la prensa | ~37 | | | ~29-30 | | ~25 | ~30 |
| Este proyecto, 2024 | 31,4 | 25,0 | 24,3 | 25,0 | 24,8 | 25,0 | 28,1 (26,6 a 29,5) |
| Este proyecto, 2025 | 28,7 | 23,3 | 23,0 | 23,7 | 23,7 | 23,8 | 26,6 (25,1 a 28,1), extrapolado |

La forma coincide: el decil 1 paga bastante más y del decil 3 al 9 la carga es pareja. Las
diferencias: Pessino et al. incluyen más impuestos (cheque y otros en cascada, que pesan más
abajo), lo que explica su decil 2 más alto; en el decil 10 este proyecto suma la Ganancias
y los Bienes Personales que la encuesta no capta (declaraciones juradas), lo que lo sube.
Para el 1% más rico, con las declaraciones de 2024 el rango de este proyecto (26,6% a 29,5%)
queda algo por debajo del ~30% citado del ITO (con la extrapolación anterior lo contenía).

