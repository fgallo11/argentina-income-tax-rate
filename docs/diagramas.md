# Diagramas del proyecto

Dos diagramas: el primero explica **qué se calcula** (para cualquier lector); el segundo, **cómo
fluyen los datos** por los scripts del repositorio (para quien quiera reproducirlo o
modificarlo). GitHub los dibuja directamente. Qué es cada fuente: [glosario de fuentes](fuentes.md); el
método completo: [metodología](metodologia.md); los resultados: [informe](informe.md).

## 1. Cómo se calcula la tasa efectiva

La tasa efectiva de un grupo es **sus impuestos divididos por su ingreso**. Cada parte sale de
fuentes distintas:

```mermaid
flowchart LR
    subgraph FUENTES["Fuentes"]
        direction TB
        EPH["EPH (INDEC)<br/>ingreso de cada persona"]
        NORMA["Normativa<br/>escalas, alícuotas y topes de cada año"]
        ARCA["Declaraciones juradas (ARCA)<br/>ingreso y Ganancias de los de más arriba"]
        DNIAF["Recaudación (DNIAF)<br/>cuánto se cobró de cada impuesto"]
        CN["Cuentas Nacionales (INDEC)<br/>consumo privado del país"]
        ENGHO["ENGHo (INDEC)<br/>qué y cuánto consume cada nivel de ingreso"]
    end

    EPH --> ORD["1. Ordenar a las personas<br/>por ingreso per cápita familiar:<br/>deciles y el decil 10 en tres tramos"]
    EPH --> SIM["2. Simular persona por persona<br/>aportes, contribuciones y Ganancias"]
    NORMA --> SIM
    ARCA --> CIMA["3. Completar la cima:<br/>ingreso y Ganancias que la encuesta no ve,<br/>resto de Ganancias y Bienes Personales"]
    DNIAF --> CIMA
    ENGHO --> CONS["4. Consumo de cada grupo<br/>según su ingreso relativo"]
    DNIAF --> PESO["5. Recaudado por cada peso<br/>de consumo (IVA, Internos, Ingresos Brutos,<br/>contribuciones trasladadas a precios)"]
    CN --> PESO
    CONS --> IND["6. Impuestos al consumo del grupo<br/>= su consumo × recaudado por peso"]
    PESO --> IND

    SIM --> IMP["IMPUESTOS DEL GRUPO"]
    CIMA --> IMP
    IND --> IMP
    ORD --> ING["INGRESO DEL GRUPO<br/>declarado en la EPH, antes de impuestos directos,<br/>más lo que la cima declara al fisco"]
    CIMA --> ING

    IMP --> TASA(["TASA EFECTIVA<br/>= impuestos ÷ ingreso"])
    ING --> TASA

    TASA --> RES["Resultados 2004-2025:<br/>por decil y tramo, por impuesto,<br/>contra un sistema proporcional y uno progresivo"]
    TASA --> VAR["Variantes de supuestos:<br/>quién paga las contribuciones, IVA legal,<br/>ingreso no declarado, cheque, etc."]

    classDef fuente fill:#eef3fb,stroke:#2a78d6,color:#0b0b0b
    classDef paso fill:#fbfaf6,stroke:#9a998f,color:#0b0b0b
    classDef clave fill:#0b3d7a,stroke:#0b3d7a,color:#ffffff
    class EPH,NORMA,ARCA,DNIAF,CN,ENGHO fuente
    class ORD,SIM,CIMA,CONS,PESO,IND,RES,VAR paso
    class IMP,ING,TASA clave
```

**Cómo leerlo.**

- **Impuestos directos (paso 2):** a cada asalariado registrado y jubilado de la encuesta se le
  calculan los aportes, las contribuciones patronales y la Ganancias que le corresponden según la
  ley de ese año. Paso a paso, con ejemplos: [microsimulación](microsimulacion.md).
- **La cima (paso 3):** la encuesta casi no ve a los de más ingresos. Con las declaraciones
  juradas se les suma el ingreso que declaran al fisco y la Ganancias que pagan por él, y se
  reparte lo que falta de Ganancias y Bienes Personales.
- **Impuestos al consumo (pasos 4 a 6):** no se aplica la alícuota de la ley sino lo que
  efectivamente se recaudó por cada peso consumido, multiplicado por lo que consume cada grupo.
  Así se descuenta la evasión.

## 2. Flujo de datos en el repositorio

Cada caja es un script; las flechas entre etapas llevan los archivos principales.
`scripts/correr_todo.py` los corre en este orden.

```mermaid
flowchart LR
    subgraph RAW["1. Datos crudos<br/>data/raw/ y params/"]
        direction LR
        r_eph[("EPH")]
        r_engho[("ENGHo")]
        r_rec[("Recaudación DNIAF")]
        r_arca[("Anuarios ARCA")]
        r_macro[("Series macro y precios")]
        r_par[("params/: Ganancias,<br/>seguridad social")]
    end

    subgraph PREP["2. Preparación"]
        direction LR
        s02["02_procesar_engho<br/>consumo por nivel de ingreso;<br/>IVA e internos por artículo"]
        s03["03_recaudacion_macro<br/>recaudación, consumo, PIB"]
        s_arca["aux_anuarios_arca<br/>declaraciones por tramo"]
        s_lmi["aux_construir_lmi<br/>tope de aportes"]
        s_ipc["aux_deflactor<br/>IPC y canasta básica"]
    end

    subgraph MICRO["3. Microsimulación y cima"]
        direction LR
        s04["04_microsimulacion_eph<br/>impuestos directos persona<br/>por persona; deciles y tramos"]
        s09["09_ingresos_altos<br/>empalme con las<br/>declaraciones juradas"]
        s_cn["aux_cuentas_nacionales<br/>cobertura de la EPH;<br/>activos externos"]
    end

    subgraph CALC["4. Tasas"]
        direction LR
        s05["05_incidencia<br/>tasas por decil,<br/>todas las variantes"]
        s11["11_tramos_decil10<br/>decil 10 partido"]
        s10["10_top1<br/>1% con declaraciones"]
        s08["08_poblacion_fija"]
        s06["06_validacion"]
    end

    subgraph OUT["5. Resultados"]
        direction LR
        tablas[("outputs/tables/")]
        s07["07_graficos<br/>figuras 0 a 9"]
        s12["12_informe_graficos<br/>+ data/externos/"]
        inf(["docs/informe.md"])
    end

    RAW --> PREP
    PREP -- "engho_grupos<br/>recaudacion_macro<br/>ddjj_ganancias_tramos<br/>lmi" --> MICRO
    MICRO -- "eph_trimestral_decil / tramos<br/>ajuste_altos_ingresos<br/>cn_ingresos" --> CALC
    CALC -- "tasas por decil y tramo<br/>top1, validación" --> OUT

    classDef datos fill:#eef3fb,stroke:#2a78d6,color:#0b0b0b
    classDef script fill:#fbfaf6,stroke:#9a998f,color:#0b0b0b
    classDef salida fill:#0b3d7a,stroke:#0b3d7a,color:#ffffff
    class r_eph,r_engho,r_rec,r_arca,r_macro,r_par,tablas datos
    class s02,s03,s_arca,s_lmi,s_ipc,s04,s09,s_cn,s05,s11,s10,s08,s06,s07,s12 script
    class inf salida
```

**Qué usa cada script** (además de lo de la etapa anterior):

| Script | Lee | Escribe |
|---|---|---|
| `04_microsimulacion_eph` | EPH, `params/`, RIPTE, haber mínimo, SMVM | deciles y tramos con impuestos directos |
| `09_ingresos_altos` | salida de `04`, declaraciones por tramo, recaudación | `ajuste_altos_ingresos.csv` |
| `aux_cuentas_nacionales` | salida de `04`, recaudación, CGI, PII, dólar | `cn_ingresos.csv` |
| `05_incidencia` | `04`, `02`, `03`, `09`, `aux_cuentas_nacionales` | tasas por decil, todas las variantes |
| `11_tramos_decil10` | lo mismo, con los tramos | tasas del decil 10 partido |
| `10_top1` | declaraciones por tramo, `02`, `03`, `04`, `aux_cuentas_nacionales` | `top1.csv` |
| `08_poblacion_fija` | EPH de 2004 y 2017, `params/`, `02`, `03`, `09` | `serie_poblacion_fija.csv` |
| `06_validacion` | `04`, `02`, `03`, `09` | tablas de validación |
| `07_graficos` | tablas, `aux_deflactor` | `outputs/figures/` |
| `12_informe_graficos` | tablas, `data/externos/` | `outputs/figures/informe/` |

**Archivos intermedios** (`data/processed/`, no se versionan):

| Archivo | Lo escribe | Qué tiene |
|---|---|---|
| `eph_trimestral_decil.csv` | `04` | Por año, trimestre y decil: ingreso, personas e impuestos directos simulados |
| `eph_trimestral_tramos.csv` | `04` | Lo mismo con el decil 10 partido en P90-95, P95-99 y 1% |
| `eph_cola_alta.csv.gz` | `04` | Las personas de más ingreso, para el empalme con las declaraciones juradas |
| `engho_grupos.csv` | `02` | Consumo y canasta por veintil de ingreso relativo, por edición |
| `recaudacion_macro.csv` | `03` | Recaudación por impuesto, consumo privado, PIB y población, por año |
| `ddjj_ganancias_tramos.csv` | `aux_anuarios_arca` | Declaraciones juradas por tramo: casos, ingreso, impuesto, patrimonio |
| `ajuste_altos_ingresos.csv` | `09` | Ganancias e ingreso faltantes y cómo se reparten entre grupos |
| `cn_ingresos.csv` | `aux_cuentas_nacionales` | Cobertura de salarios e ingreso mixto; activos externos |
| `deflactor.csv` | `aux_deflactor` | IPC empalmado y canasta básica |

Las tablas finales (`outputs/tables/`) se describen al principio de cada script que las escribe.
