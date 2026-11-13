# Brief para Fable — LegisTracker: definición antes que diseño

> Pegalo como primer mensaje de una sesión NUEVA en `/home/fran/legis-tracker-ar`, en modo plan.
> Antes de pegarlo, completá las partes marcadas con ✏️.

---

Trabajás en LegisTracker Argentina (`/home/fran/legis-tracker-ar`). Leé `CLAUDE.md`,
`docs/estado.md` y recorré `src/pages/` y `src/data/` para entender qué datos hay.

**Esta sesión NO escribe código de producción.** El entregable es un documento de definición
(`docs/definicion-web.md`) y, al final, 2 o 3 bocetos de baja fidelidad. La construcción va en
otra sesión que va a leer ese documento.

## Qué es el proyecto (la idea central, no negociable)

Todo nace del **análisis de impacto de las normas**. Es lo único que tengo y nadie más tiene.

La cadena es:

**norma → impactos (por sector, en el tiempo) → quién la firmó o votó → legislador → bloque/partido**

- Los impactos de las normas se suman por **gobierno**: eso cuantifica cómo gobierna cada
  presidente (cuánto reforma, a qué sectores afecta, a favor o en contra, cuándo).
- Como las leyes se votan, **quienes las votaron son responsables de esos impactos**, y según
  cómo votaron se les suman. Los legisladores se agrupan por partido y bloque.
- El objetivo es que cualquiera pueda ver, de forma **simple, rastreable, linkeable y
  transparente**, cómo gobiernan, cómo legislan y cómo votan los actores políticos, y **a quién
  afectan**.
- Pobreza, empleo y presupuesto son contexto: los saca cualquiera, no son centrales.

Cobertura actual: Milei completo, Alberto Fernández ~77%. Hay que decir que está incompleto,
sin esconderlo.

## Para quién

- **Periodistas:** tienen que poder encontrar un dato, entenderlo y citarlo con un link en
  menos de un minuto.
- **Ciudadanos:** tienen que entender la idea central sin leer instrucciones.

✏️ Las 3 preguntas que un visitante tiene que poder responder en 30 segundos:
1. ✏️ (ej.: «¿A qué sectores benefició y perjudicó más este gobierno?»)
2. ✏️ (ej.: «¿Cómo votó mi diputado las leyes que afectaron a X?»)
3. ✏️ (ej.: «¿Qué partido acompañó más las reformas de este gobierno?»)

## Cosas que ya sé que quiero

- Ver los efectos **sumados** y poder hacer zoom en un sector hasta llegar norma por norma.
- La vista de **impactos por sector a lo largo del tiempo** es la más reveladora: un solo
  gráfico donde elijo qué sectores se muestran.
- **Comparar presidentes:** en cualquier vista de un presidente, poder traer a otro
  (superpuesto o lado a lado), alineados de principio a fin del mandato aunque duren distinto.
  Por defecto **no** se muestra otro presidente: lo traigo yo si quiero.
- Medidas de «estilo» de gobierno: cantidad de impactos como medida de reformismo,
  caracteres por norma, etc.
- Todo estado de la vista va en la URL (linkeable), como ya hace `/normas`.
- Estética: estilo de expediente o despacho del Estado argentino usado como **recurso
  artístico** (carpetas, folios, birome azul, resaltador, post-its), no como copia de un
  documento oficial. Ver `expediente/`. Los controles tienen que sentirse objetos del
  escritorio (ej.: sectores anotados en el margen con birome que se tachan o destachan), no
  botones impuestos.

✏️ Qué NO se toca / qué no me gustó de intentos anteriores:
- No partir de `prototype/`: transformó cosas de una manera que no comparto. La fuente de
  verdad de la información es la web actual (`src/`).
- ✏️ …

## Cómo quiero que trabajes

1. **Primero entrevistame.** Antes de proponer nada, haceme las preguntas que necesites (de a
   pocas) hasta estar seguro de que entendés la idea central igual que yo. Repetímela con tus
   palabras y esperá a que te diga «sí, es eso».
2. Después escribí `docs/definicion-web.md` con:
   - El mapa de páginas y cómo se navega la cadena norma → impacto → voto → legislador → partido.
   - Para cada página: qué pregunta responde, qué dato muestra primero y qué se puede
     comparar.
   - Qué datos de `src/data/` alimentan cada vista y **qué datos faltan** o son débiles.
   - Cómo se comunica que la cobertura está incompleta.
3. Proponé **2 o 3 direcciones visuales distintas** como bocetos simples (HTML estático, una
   pantalla cada una: la del presidente con comparación). Nada de pulido: quiero elegir la
   dirección, no el detalle.
4. Pará ahí. No implementes en `src/`.

Si en algún punto algo de lo que te pido contradice la idea central, decímelo.
