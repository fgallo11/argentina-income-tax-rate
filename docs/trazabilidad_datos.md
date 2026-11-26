# Trazabilidad de los datos: de dónde sale cada número

Para una descripción de cada fuente (qué es, qué aporta, cómo se usa) ver el
[glosario de fuentes](fuentes.md); para el flujo entre scripts, los [diagramas](diagramas.md).

Inventario hecho el 14/11/2026 sobre el commit `63c1d49`. Objetivo: que cada dato del
proyecto se pueda verificar a mano contra su fuente.

> **Agregados después del inventario:** anuarios de ARCA del año fiscal 2024 (anuario 2025) y, el
> 26/11/2026, sus cuadros 2.2.2.1.1, 2.2.2.1.2, 2.2.2.1.4 y 2.2.2.1.8 de todos los años (categorías,
> deducciones y justificación patrimonial; categoría A, controlados contra su fila TOTAL); datos de
> terceros sólo para comparar en `data/externos/` (Argendata, ITO; categoría D, con su README); la
> serie de impuestos a la propiedad de la OCDE citada en `docs/metodologia.md`, sección 15 (categoría D);
> `params/monotributo.yaml` (categoría B: tablas de ARCA 2010-2026 leídas con un programa y controladas
> fila por fila contra su total; Ley 25.865 para 2004-2009, texto original sin actualizaciones verificadas). Cuatro categorías:

- **A. Descargado por el pipeline** (`scripts/01_descargar_datos.py`): el número no lo tipeó
  nadie; se verifica revisando que la URL/ID sea la serie correcta.
- **B. Transcrito a mano desde una fuente citada** (`params/`): hay que cotejar valor por valor.
- **C. Escrito en el código sin fuente citada**: o es un supuesto declarado, o es un dato que
  alguien escribió de memoria. Es la categoría de riesgo.
- **D. Cifras de terceros en la documentación** (literatura, Pessino, ITO): no entran al
  cálculo, pero se citan.

Columna "Chequeo 14/11": lo que se contrastó en esta revisión contra la fuente original
descargada. "—" = no contrastado.

---

## A. Datos descargados por el pipeline

| Dato | Fuente / ID | Dónde se usa | Chequeo 14/11 |
|---|---|---|---|
| Microdatos EPH 2003T3-2025T4 | INDEC FTP, `nombre_eph()` en `01_descargar_datos.py:28` | todo | — (5 GB; no se bajó) |
| Microdatos ENGHo 2004/05, 2012/13, 2017/18 | INDEC FTP, `ENGHO` en `01_descargar_datos.py:47` | `02_procesar_engho.py` | — |
| Ganancias: escalas y deducciones | DNIAF, PDF "Impuesto a las Ganancias… desde el año 2000 al 2025" (2025: tabla anual, pág. 34) | `params/ganancias.yaml` (ver B) | PDF bajado |
| Recaudación por impuesto | DNIAF, "Recaudación nominal, clasificación internacional" (xlsx) | `03_recaudacion_macro.py` | **Sí:** los 22 índices de `FILAS` (`03_recaudacion_macro.py:24`) corresponden al concepto que dice el código (p. ej. `1.1.1` = Ganancias de Personas Físicas, `3.1.2.2` = Créditos y Débitos, `10.2.1` = generales provinciales = IIBB) |
| Consumo privado corriente | datos.gob.ar `4.3_DGCP_2004_A_27` | escala de indirectos | **Sí:** "Consumo privado, millones de pesos corrientes, anual", INDEC base 2004 |
| PIB corriente | `4.3_OGP_2004_A_17` | validación | **Sí:** "PIB a precios de comprador, corrientes, anual", INDEC |
| Haber mínimo | `58.1_MP_0_M_13` | tope de aportes (`lmi.csv`), deducción de jubilados | **Sí:** ANSES, pesos corrientes |
| SMVM | `57.1_SMVMM_0_M_34` | régimen cedular 2024 | **Sí:** Secretaría de Trabajo, mensual |
| RIPTE | infra.datos.gob.ar, dataset 158 | anualización de Ganancias, población fija | — |
| IPC GBA / San Luis / Nacional | `97.2_ING_2008_M_17`, `197.1_NIVEL_GENERAL_2014_0_13`, `148.3_INIVELNAL_DICI_M_26` | deflactor (fig. 6b) | **Sí:** coinciden con lo que dice `aux_deflactor.py` |
| Canasta básica total GBA | `444.1_CANASTA_batotGBA_0_0_26_47` | fig. 6 | **Sí** (INDEC). Que sea "por adulto equivalente" no figura en los metadatos: confirmar en el informe del INDEC |
| Tipo de cambio A 3500 | `168.1_T_CAMBI500_D_0_0_17`, promedio anual | activos externos | **Sí** (BCRA) |
| Cuenta de generación del ingreso | INDEC `serie_cgi_10_26.xls`, hojas RTA, IBM, EEB | ajuste a Cuentas Nacionales | — |
| Posición de inversión internacional | INDEC `cin_II_2026.xls`, cuadro 18 | activos externos | — |
| Declaraciones juradas de Ganancias por tramo | Anuarios ARCA 2003-2025 (años fiscales 2002-2024). Los de 2003-2008 traen las planillas dentro de `AFIP.CAB`, que `01_descargar_datos.py` extrae desde el 16/11/2026 (antes se hacía a mano) | `09`, `10` | — (el script controla suma de tramos vs TOTAL < 0,2%) |
| Población total | **Banco Mundial** `SP.POP.TOTL` | expansión de la EPH al país | — Nota: no es la proyección del INDEC; difieren algo |

Cómo verificar los IDs: `https://apis.datos.gob.ar/series/api/series/?ids=<ID>&metadata=only`.

---

## B. Transcrito a mano (`params/`)

### `params/ganancias.yaml` — fuente: PDF de la DNIAF

**Chequeo 14/11:** se extrajo el texto del PDF y se buscó cada número del YAML. **Todos
aparecen** en el PDF: escalas 2000-2024, deducciones 2003-2024, tramos del Dto. 1242/2013,
"tablita de Machinea" 2003-2008 y umbrales de la Ley 27.617 (`exento` y `transicion`). Lo
mismo para las 6/8 veces el haber mínimo de jubilados. Limitación: se buscó que el número
exista en el PDF, no que esté en la página y celda que corresponde. Para valores redondos
(10.000, 20.000…) la coincidencia es débil; para los que tienen centavos (p. ej. 33.039,81)
es fuerte. Pendiente a mano: confirmar año ↔ página.

| Ítem | Origen | Estado |
|---|---|---|
| `smvm_base: 132000` | Derivado: el PDF (p. 30) dice "$1.9800.000 [sic], equivalente a 15 veces el SMVM"; 1.980.000/15 = 132.000. El 132.000 no figura literal | Verificar contra la serie SMVM de octubre 2023 |
| Cedular ene-jun 2024 | Tabla de oct-2023 reescalada por SMVM | **Aproximación declarada**, no es la norma |
| Tramo de transición Ley 27.617 | Interpolación lineal entre `exento` y `transicion` | **Supuesto** (las tablas de AFIP no se transcribieron) |
| 2013 con valores de marzo todo el año | Simplificación declarada | — |

### `params/seguridad_social.yaml`

| Ítem | Valor | Estado en el archivo | Comentario |
|---|---|---|---|
| Aporte jubilatorio general | 11% | verificado | |
| Aporte capitalización hasta 12/2007 | 7% | verificado (texto Dto. 390/2003 y notas) | Asignado a **todo** el sector privado: supuesto |
| INSSJP | 3% | **no_verificado** | |
| Obra social | 3% | **no_verificado** | |
| Contribuciones 2003-01/2018 | 21% / 17% | **no_verificado** | |
| Contribuciones 2018 | 20,70% / 17,50%, detracción $2.400 | **no_verificado** ("el cronograma figura como imagen") | |
| Contribuciones 2019 | 20,40% / 18,00%, detracción $7.003,68 | **no_verificado** | |
| Contribuciones 2020-2024 | 20,40% / 18,00%, detracción $7.003,68 | verificado (Ley 27.541) | Confirmar si la detracción tuvo actualizaciones o montos distintos para empleadores chicos en 2020-2024 |
| Contribuciones 2025 | 20,40% / 18,00%, detracción $7.003,68 | **no_verificado** | Se supone que siguió la Ley 27.541: la página de ARCA y la prensa especializada no registran cambios en 2025 (la baja de la reforma laboral es de 2026). Falta contrastar con texto primario |
| Umbral inc. a): >40 personas | 40 | **supuesto** | La norma usa ventas, no tamaño |
| Reparto 50/50 | 0,5 | decisión | |

### `params/lmi.csv` (tope de aportes) — construido por `scripts/aux_construir_lmi.py`

| Mes | Valor | Fuente | Estado |
|---|---|---|---|
| hasta 03/2007 | 4.800 | 60 MOPRE, Dto. 290/2000 | verificado indirecto (citado en Dto. 1448/2008) |
| 04/2007 | 6.000 | Ley 26.222 | **mes de inicio (03 u 04) no verificado** |
| 09/2007, 03/2008, 07/2008, 11/2008 | 6.750, 7.256, 7.800 | Dto. 1346/2007, Dto. 279/2008, Dto. 1448/2008 | verificado |
| 03/2009 y 09/2009 | +11,69% y +7,34% | `MOVILIDAD_OVERRIDE` (`aux_construir_lmi.py:45`) | **Sin fuente citada en el código**: verificar contra Res. ANSES de movilidad 2009 |
| 03/2009 en adelante | cadena con la variación del haber mínimo | serie ANSES | derivado; controlado contra anclas (falla si difiere >0,05%) |
| 2015-09 (ancla) | 48.598,08 | SICOSS v39 r2, Consejo Profesional CABA | **Fuente secundaria**: buscar la Res. ANSES |
| 2020-03 (ancla) | 173.945,70 | "valor vigente marzo 2020 (consistente con Res. ANSES 325/2020 / 1,075 / 1,0612)" | **No es un valor leído en una norma**: se calculó hacia atrás desde el de 09/2020. Y como `REANCLAR` lo impone, no se controla |
| Resto de anclas | Res. ANSES 130/2010, 30/2013, 325/2020, 36/2023, 979/2024, 1122/2024 | citadas | verificar cada una |
| 2025-06, 2025-11, 2025-12 (anclas) | 3.335.458,18; 3.645.898,00; 3.731.212,01 | Res. ANSES 237/2025 (leída en el Boletín Oficial), 338/2025 y 359/2025 (estas dos, según fuentes secundarias) | La cadena de movilidad las reproduce con diferencias ≤0,0004%, lo que también respalda los dos valores secundarios |

---

## C. Escrito en el código sin fuente citada

Esta es la lista de lo que puede venir "de memoria". Algunos son supuestos declarados; otros
son datos fácticos (códigos de encuesta, fechas legales) que deberían tener una cita.

### C.1 Datos fácticos sin cita (verificar)

| Dato | Dónde | Contra qué verificar |
|---|---|---|
| Códigos EPH: `ESTADO==1` ocupado, `CAT_OCUP==3` asalariado, `PP07H==1` con descuento jubilatorio, `PP04B1==1` servicio doméstico, `PP04A==1` estatal, `CH03` 1/2/3 = jefe/cónyuge/hijo | `directos.py:179-181`, `eph.py:38` | "Diseño de registro" de la EPH (INDEC). El pipeline no lo descarga |
| `PP04C` en {9,10,11,12} o `PP04C99==3` = "más de 40 personas" | `directos.py:182` | Ídem. Si los códigos no son esos, cambia la alícuota patronal asignada |
| `V8_M`, `V9_M`, `V10_M` = alquileres, ganancias de negocios, intereses; `PP08J1` y `V21_M` = aguinaldo | `eph.py:16`, `eph.py:27` | Ídem (el aguinaldo dice "verificado en los microdatos") |
| Trimestres EPH no publicados: 2007T3, 2015T3-T4, 2016T1 | `config.py:23` | Página de bases de datos del INDEC |
| Período desaconsejado por el INDEC: 2007-2015 | `config.py:29` | Comunicado del INDEC (2016) |
| Mapeo de códigos ENGHo 2004/05 y 2012/13 a divisiones COICOP (`"122"`→02, `"13"`→11, `"911"`→02, etc.) | `clasificador.py:49` | `ENGHo_2017_2018_codigos_12_9_divisiones.xlsx` (se descarga y **no se usa**). Muestreo: alcohol y tabaco caen en 02 y comidas fuera en 11, como corresponde |
| Artículos excluidos del consumo: prefijos 25, 26, 27, 98, 99 y 3112, 3115, 3116, **3121, 3122** | `02_procesar_engho.py:69` | Catálogo ENGHo. El docstring dice "alquileres imputados (3112, 3115, 3116)"; 3121 y 3122 no están explicados |
| Carne aviar y porcina al 10,5% "desde 02/2018" | `indirectos.py:71` | Ley 27.430, vigencia de la modificación del art. 28 de IVA |
| Dto. 567/2019: 16/08 a 31/12/2019 (4,5 meses) | `indirectos.py:32` | Dto. 567/2019 y su prórroga/modificación. El clasificador dice "verificado" |
| Reglas de IVA "no verificado": gas licuado, medicina prepaga, informática al 10,5% | `clasificador.py` | Ley de IVA art. 28 |
| Medicamentos al 21% pleno | `clasificador.py` (clase MED) | Aproximación: la reventa está exenta |
| Anclas temporales ENGHo: 2005, 2012, 2018 ("puntos medios del trabajo de campo") | `indirectos.py:33` | Fechas de campo en los manuales de cada ENGHo. Si la 2012/13 fue mar-2012 a feb-2013, el punto medio es ~2012,7, no 2012,0 |

### C.2 Supuestos numéricos (no son datos; son decisiones)

| Supuesto | Valor | Dónde | Comentario |
|---|---|---|---|
| Contribución patronal de empleados públicos | 18% del bruto | `aux_cuentas_nacionales.py:88` | Sin fuente. Afecta `cob_asal` |
| Obra social patronal | 6% | `aux_cuentas_nacionales.py:88` | Sin cita (Ley 23.660) |
| Cobertura 2004-2015 = promedio 2016-2018 | | `aux_cuentas_nacionales.py` | Declarado |
| Activos externos 2004-2005 = los de 2006 | | `aux_cuentas_nacionales.py` | Declarado |
| Rentas de la EPH ×7 | 7 | `incidencia.py:92` | De Rosa et al. dicen 5 a 10; el 7 es elección |
| Renta de activos externos | 4% anual sobre la cartera (3% sobre cartera y depósitos, cota) | `incidencia.py:88`, `10_top1.py` | Elección |
| 1% más rico (control): contribución patronal 20% sobre la parte de la 4ta categoría de empleados | 0,20 | `10_top1.py:63, 108` | El 20% no es ninguna alícuota legal ("aproximada"); la parte de empleados sale de los casos de los anuarios |
| 1% más rico (control): consumo = punto medio entre el "monto consumido" de ARCA y el de la versión A | 0,5 | `10_top1.py:118` | Elección: ninguna fuente mide el consumo del 1% |
| 1% más rico (control): ingreso no salarial no declarado | 5%, 10%, 25% | `10_top1.py:65` | Escenarios; el 25% sigue a Alstadsæter, Johannesen y Zucman (2019), dato del 0,01% de Escandinavia |
| 1% más rico (control): desde 2012 | 2012 | `10_top1.py:64` | Antes, pocos empleados declaraban sus aportes |
| Aguinaldo devengado 13/12 | | `directos.py:29` | Definición |

---

## D. Cifras de terceros en la documentación

No entran al cálculo, pero se citan. Ordenadas de menos a más confiable.

| Cifra | Dónde | Origen declarado | Riesgo |
|---|---|---|---|
| ITO 2026 para Argentina: 50% inferior 37%, 40% medio 29%, 10% superior 25%, 1% ~30% | `validacion.md` §3, informe §1, `data/externos/` | **Fuente primaria desde el 17/11/2026:** nota del ITO sobre Argentina (p. 3) e informe n.° 10, figura 5 (composición leída del gráfico). No son deciles | Medio (la composición es aproximada) |
| Pessino et al. (2018), tabla por decil | `validacion.md` §3, informe §1, README | CSV de Argendata bajado el 17/11/2026 (`data/externos/`); el CSV cita Oxford Open Economics, vol. 4 | Bajo |
| Santiere et al. 1997, Gaggero-Rossignolo 2010, Gómez Sabaini et al. 2008, Rossignolo 2012/13 | `validacion.md` §2, `literatura_previa.md` | Transcritos por un agente auxiliar; `auditoria.md` §1.1 dice haberlos verificado contra los PDF | Medio-bajo. Rossignolo es **suma propia**, no cifra publicada |
| Gaskín (2022) | sólo `auditoria.md` §1.1 | Auditor | No está en `literatura_previa.md` |
| CEQ Handbook p. 273 | `validacion.md`, `literatura_previa.md` §7 | 2ª ed. (2022); la 1ª no se abrió | Bajo |
| INDEC 4T2024: media $442.596, población 29.783.755, D10 $1.430.619 | `metodologia.md` §10 | Informe "Evolución de la distribución del ingreso", cuadro 1 | Bajo (validado por el pipeline) |

---

## E. Inconsistencias encontradas entre documentación y tablas

Cifras de la documentación que no coincidían con `outputs/tables/`. **Los puntos 1, 2 y 4
y los de `validacion.md` §1 (cocientes simulado/recaudado de aportes, contribuciones y
Ganancias, que eran anteriores al ajuste de aguinaldo; y el impuesto de las declaraciones
juradas sobre lo recaudado, 53%-82% y no 70%-80%) se corrigieron el 14/11/2026.** El 3 sigue
pendiente.

1. **`validacion.md` §2**, filas del proyecto para 2010: dice "principal 22,1 / 27,4 / 29,0
   / 27,2" e "ingreso declarado 40,4 / 27,4 / 29,0 / 27,8". Son de antes de la auditoría (la
   principal era `recursos_gasto`). Hoy: principal 2010 = **37,3 / 26,3 / 28,7 / 27,0**;
   `recursos_gasto` = 20,3 / 26,3 / 28,7 / 26,4.
2. **`validacion.md` §3**, 1% más rico 2024: dice "30,1 a 38,5". Mezcla la estimación
   `completo` (30,1) con `total_alto` (38,5, sólo lo declarado al fisco). El README dice
   "30,1% (28,5% a 31,7%)", que es lo que da `top1.csv` para `completo`.
3. **`metodologia.md` §2**: gasto/ingreso del decil 1 "entre 1,45 y 2,1"; la tabla da 1,41 a
   2,15. Diferencia menor.
4. **`validacion.md` §2**, IVA 2010 decil 1: dice 19,3; la tabla da 19,4. Menor.

Coinciden: resultado 2024 del README (25,4 / 31,4 / 26,8), variantes con cheque, población
fija (§7), cociente gasto/ingreso del decil 1 por edición (1,59 / 1,68 / 1,45), filas 2018 de
`validacion.md` §3.

---

## Cómo repetir el chequeo de `ganancias.yaml`

```bash
curl -o /tmp/g.pdf "https://www.argentina.gob.ar/sites/default/files/impuesto_a_las_ganancias_desde_el_ano_2000_al_2025_0.pdf"
pdftotext -layout /tmp/g.pdf /tmp/g.txt
```
Normalizar los números del texto (sacar puntos de miles, coma → punto) y buscar cada valor del
YAML con dos decimales y, si es entero, sin decimales.
