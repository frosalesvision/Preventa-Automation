---
name: nueva-cotizacion
description: Punto de entrada único para atender de punta a punta un pedido de cotización descrito en lenguaje natural (ej. "necesito un proyecto para el cliente X, al menos 15 cámaras, presupuesto de ₡5 millones, la mejor calidad posible") — analiza qué datos ya vinieron en el pedido, pregunta SOLO lo que falte y sea necesario (nunca inventa ni omite), y orquesta en el orden correcto `buscar-equipo` (encontrar marca/modelo real que cumpla) y `armar-cotizacion` (carpeta, matriz, pestaña Equipos, registro en los dos Excels de control) sin que el asesor tenga que invocar cada skill por separado. Usar cuando el usuario describe una necesidad de cliente/proyecto nueva de forma libre y espera que se arme la cotización completa, cuando pide "arma la cotización de punta a punta", o cuando no está seguro de por dónde empezar. Para pasos sueltos (solo buscar equipo, solo organizar una carpeta ya con el equipo decidido) seguí usando `buscar-equipo` o `armar-cotizacion` directo.
---

# Nueva cotización (orquestador de punta a punta)

Este skill no reemplaza a `buscar-equipo` ni a `armar-cotizacion` — **los
llama a los dos, en orden, con los datos ya reunidos.** No reinventes acá
ninguna regla que ya vive en esos dos skills (numeración de carpeta,
lógica de búsqueda en catálogo, qué columnas de la matriz se escriben,
etc.) — seguilas tal cual están documentadas ahí. Este skill solo se
encarga de la parte que hoy no existe: **entender el pedido, detectar qué
falta, preguntar de forma inteligente, y encadenar los pasos.**

## Regla dura (no negociable)

**Nunca inventes ni omitas un dato necesario.** Si algo hace falta para
buscar equipo o para armar la cotización y no vino en el pedido original,
**preguntalo siempre** — aunque parezca obvio, aunque "probablemente" el
asesor quiera tal cosa. Es mejor una pregunta de más que una cotización
armada sobre un supuesto equivocado (cantidad mal, característica que no
correspondía, presupuesto mal interpretado). Esto aplica en cada paso de
este skill, no solo al principio.

## La ficha de cotización (agregado 2026-09-18 — acordado con preventa)

Antes de armar nada, este skill levanta una **ficha del proyecto**: un
set corto de preguntas con los valores por defecto ya puestos, para que
el asesor solo confirme o corrija. Es la parte que preventa aceptó
explícitamente en la reunión del 2026-09-14: *"que la IA pregunte si se
van a mantener los valores por defecto o si se van a cambiar"*, con el
trato de que **ellos aportan el número y la IA llena el Excel**.

**No es un formulario que se llena aparte y se sube.** Se pregunta en el
chat, agrupado, con los defaults visibles. Un documento externo se
desactualiza, obliga a abrir otra herramienta, y no puede precargar el
valor que ya conocemos.

**Campos, en este orden.** Lo que ya vino en el pedido no se vuelve a
preguntar; lo que no se sabe **siempre** se pregunta.

| # | Campo | Default / de dónde sale |
|---|---|---|
| 1 | **Tipo de cotización** | Estudio de mercado · Oferta de licitación · Cliente privado. Define los porcentajes de abajo (regla R6) |
| 2 | **Cliente** | Si está en la tabla de régimen fiscal, se precarga exención y porcentajes. Si no está, se pregunta ofreciendo **13% como primera opción recomendada** — ver abajo (R3) |
| 3 | **Proyecto** | Descripción corta y número de licitación si aplica |
| 4 | **Ubicación** | Para el kilometraje. La **distancia** sale de la columna `Destino / localidad` de la pestaña `Transporte` del machote; si el destino no está, se pregunta y se ofrece agregarlo (R9) |
| 5 | **Asesor responsable** | Para los Excel de control y la firma de la cotización |
| 6 | **Registro de proyecto** | ¿Registrado? ¿Con qué distribuidor y marca? ¿Desde cuándo? Si no lo está, avisar que el descuento mayor no aplica (R5) |
| 7 | **Alcance** | Solo equipo · con accesorios de montaje · con materiales de instalación · con mano de obra. Determina qué pestañas se llenan |
| 7b | **Materiales de instalación** *(opcional)* | Si el alcance los incluye: qué materiales y **qué cantidades**. **Preguntar siempre, pero no insistir**: si el proyecto no los lleva o todavía no se sabe, se deja en blanco y se sigue. **Nunca estimar la cantidad por cuenta propia** (regla R10) |
| 8 | **Transporte %** | Valor del machote; preguntar si compras ya dio el del proyecto |
| 9 | **Imprevistos %** | Valor del machote |
| 10 | **Administración %** | Valor del machote; puede bajar a 0 en licitaciones agresivas |
| 11 | **Margen %** | **27,4%, el estándar. No proponer cambiarlo.** Aclarar que se puede cambiar a mano en el Excel, y que hacerlo en `Equipos` mueve también `OPEX GV` |
| 12 | **Mano de obra** | Días y personas: se preguntan siempre. El precio unitario sale del tarifario (R8) |
| 12b | **Viajes al sitio** | Cuántos viajes, cuántos vehículos y si hay hospedaje. **Se preguntan**: solo los kilómetros salen de la tabla de destinos (R9) |
| 13 | **Financiamiento** | **Siempre preguntar**, sin importar el tamaño del proyecto. Si va: plazo y tasa. Si no: la columna `Financ.` queda vacía (R13) |
| 14 | **Tipo de cambio** | **Preguntar siempre el precio de COMPRA y el de VENTA del dólar.** No hay una regla fija: a veces se usa el del BCCR tal cual y a veces se sube un poco a favor de la empresa, y eso se decide por proyecto (R7) |
| 15 | **Vigencia** | Días de validez de la oferta y fecha límite de entrega |

### Sobre el margen: informar, no decidir (agregado 2026-09-23)

El default **sigue siendo el del machote, 27,4%**, y no cambia solo.
Pero al preguntarlo, si ya sabés el tipo de cotización, contale al
asesor qué hizo el equipo en casos parecidos. Sale de leer 499 matrices
reales de 2025 y 2026 (regla R6):

| Tipo | Lo que hizo el equipo |
|---|---|
| Estudio de mercado | 6 de 6 lo subieron. Mediana **35%**, rango 35–42% |
| Licitación | 12 de 15 lo movieron. Mediana **23%**, rango 20,8–30% |
| Mantenimiento | mediana 25% entre los que lo movieron |
| Privado / otro | la mayoría deja el 27,4% |

**Decisión de Fabián (2026-09-23): el 27,4% es el estándar y se deja.**
No lo cambies, y **tampoco propongas cambiarlo** — la ficha no tiene que
convertir cada cotización en una negociación sobre el margen.

Lo que sí: al mostrar los porcentajes, aclará que **se pueden cambiar a
mano en el Excel** si ese proyecto lo amerita. Y si el asesor pregunta
qué suele usarse en un tipo de cotización, ahí sí le das la tabla de
arriba. **Responder si preguntan, no ofrecer.**

### Cuando el cliente no está en la tabla de régimen fiscal

No preguntes en abstracto. **Ofrecé el 13% como primera opción** — es lo
que aplica a la mayoría — y listá al lado los otros casos que el equipo
ya confirmó que existen:

> *"Ese cliente no está en la tabla de régimen fiscal. ¿Cuál le aplica?*
> - ***13%** — lo normal, es lo que lleva la mayoría* ← recomendada
> - *Exento — hay instituciones que no pagan*
> - *2% — algunas universidades públicas*
> - *Otro porcentaje*
>
> *Si es de zona franca hay que confirmarlo caso por caso: unos están
> exonerados y otros no."*

**Nunca lo apliques en silencio, ni el 13% ni la exención.** El default
del machote ya es 13% si la ficha queda vacía, así que no preguntar
equivale a elegir — y en el caso real que se midió, un cliente **privado**
llevaba **0%**.

Cuando conteste, ofrecé **agregarlo a la tabla** del catálogo para la
próxima vez.

⚠️ **Lo que la ficha pregunta y no busca en ninguna tabla.** Hay datos
que dependen del sitio y no de un catálogo: **la cantidad de material de
instalación**, los **días y personas** de mano de obra, y los **viajes y
vehículos**. Para esos no existe —a propósito— una tabla de referencia:
guardarlos como valor fijo le daría a una estimación la autoridad de una
fuente de verdad, y después nadie la cuestiona. Se preguntan en cada
cotización y **se pueden dejar en blanco** si el proyecto no los lleva.

**Guardar la ficha.** Una vez confirmada, escribila como archivo corto
dentro de la carpeta de la cotización. Sirve para dos cosas: que una
versión nueva arranque de ahí sin repreguntar todo, y que dentro de seis
meses se pueda explicar por qué esa oferta llevaba esos porcentajes.

El detalle de cada regla está en
[`docs/reglas-negocio.md`](../../../docs/reglas-negocio.md).

## Paso 1 — Leer el pedido y armar un inventario de lo que ya se sabe

Antes de preguntar nada, releé el pedido completo (puede venir en una sola
frase larga, como el ejemplo de arriba) y extraé todo lo que puedas
mapear contra esta lista. Sé generoso interpretando lo que el usuario ya
dijo — "la más alta calidad" sí es información (orienta la búsqueda hacia
los candidatos top del catálogo, no hace falta preguntar "¿qué calidad
querés?" de nuevo), pero no inventes un número/spec exacto a partir de una
frase vaga si no se puede derivar con confianza.

**Checklist — lo necesario para poder buscar equipo (Paso 3):**

- Cliente (nombre, aunque sea corto/informal por ahora).
- Tipo de producto/categoría (cámaras, control de acceso, alarma, etc.).
- Cantidad total — y si hay varios tipos/ubicaciones, cuánto de cada uno.
- ¿Todas las unidades son iguales, o hay variantes (interior/exterior,
  fija/PTZ, con/sin audio, etc.)?
- Características técnicas obligatorias si el cliente las dio
  (resolución, IP, IR/visión nocturna, analítica, certificaciones,
  rango de lente) — si el pedido es vago ("la mejor calidad"), no hace
  falta un número exacto, pero sí conviene confirmar el techo del
  presupuesto para que la búsqueda sepa hasta dónde llegar.
- ¿Necesita grabador/NVR y almacenamiento? ¿Cuántos días de retención?
- ¿Incluye accesorios de instalación (bases, mounts, cableado, PoE) o
  es solo equipo? (si no se sabe, se pregunta en el Paso 3 igual que lo
  hace `buscar-equipo`, no hace falta adelantarlo acá si no vino claro).
- Presupuesto: monto, moneda, si es con o sin IVA, y si incluye
  instalación/mano de obra o es solo equipo.
- Marca preferida, si la hay (o "abierto, la mejor opción").

**No preguntes por algo que el pedido ya contestó**, ni reformules la
misma pregunta con otras palabras. El objetivo es una lista corta con
huecos reales, no un cuestionario completo repetido de memoria.

## Paso 2 — Preguntar lo que falte, agrupado en un solo mensaje

Con la lista de huecos del Paso 1, hacé **una sola tanda de preguntas**
(no una por una, no varias rondas) cubriendo solo lo que falta para poder
arrancar la búsqueda. Ejemplo de tono (adaptar siempre al pedido real, no
copiar literal):

- "¿Las 15 cámaras son todas del mismo tipo, o necesitás una mezcla de
  interior/exterior o fija/PTZ?"
- "¿Necesitás también grabador (NVR) y almacenamiento, o el cliente ya
  tiene? Si hace falta, ¿cuántos días de grabación quieren guardar?"
- "¿El presupuesto de ₡5 millones es solo equipo, o incluye instalación
  y cableado?"
- "¿Es con o sin IVA?"
- "¿Querés que incluya también accesorios de instalación (bases,
  soportes) o solo el equipo principal?"

Si el usuario responde parcialmente o con nueva ambigüedad, repreguntá
puntual solo sobre eso — no reinicies la tanda completa.

## Paso 3 — Buscar el equipo

Con los datos ya completos, seguí exactamente el proceso de
[`buscar-equipo`](../buscar-equipo/SKILL.md): Paso 1 (equipo principal
por especificación, mostrando todos los candidatos razonables y sus
brechas si no hay match perfecto) y Paso 2 (accesorios de instalación, si
correspondía según el Paso 2 de acá).

**Si el presupuesto no alcanza** para la cantidad/calidad pedida con
candidatos reales del catálogo, decilo con números concretos (ej.
"15 unidades del modelo X a $180 c/u = $2,700, más NVR e instalación
supera el presupuesto de ₡5M") — **nunca bajes en silencio la cantidad,
la calidad o saltees accesorios para que cuadre el número.** Mostrale la
brecha real al asesor y dejá que decida (bajar cantidad, subir
presupuesto, o aceptar una especificación menor).

## Paso 4 — Confirmar el equipo antes de escribir nada

Mostrá la tabla completa (Marca | Modelo | Nombre | Precio | Cantidad,
separando equipo principal de accesorios — mismo formato de
`buscar-equipo`) y esperá confirmación explícita del asesor. Este es el
mismo checkpoint que ya exige `armar-cotizacion` antes de tocar un
archivo real — no lo saltees aunque el pedido inicial sonara muy
específico.

## Paso 5 — Completar los datos administrativos que falten

Recién acá, si todavía no los tenés, preguntá lo que hace falta para
`armar-cotizacion` (no antes — no tiene sentido pedir esto si la
búsqueda de equipo todavía podía cambiar todo):

- Nombre legal completo del cliente (si es distinto al usado hasta
  ahora) y si ya existe carpeta en `CLIENTES/` o es cliente nuevo.
- Descripción corta para el nombre de la carpeta de la cotización.
- Asesor/ejecutiva responsable (para las columnas de los dos Excels de
  control) — si no lo sabés, preguntalo, no asumas que es quien está
  escribiendo en el chat.
- Fecha límite de entrega de la oferta, si el cliente dio una.

## Paso 6 — Armar la cotización

Con todo reunido, seguí el proceso completo de
[`armar-cotizacion`](../armar-cotizacion/SKILL.md) tal cual está
documentado ahí, sin saltar ningún paso: cálculo/confirmación de
numeración de carpeta y de oferta, copia del machote, llenado de la
pestaña `Equipos` con lo confirmado en el Paso 4, y registro en los dos
Excels de control (`Control de cotizaciones 2026.xlsx` y `Cotizaciones en
Preventa.xlsx`).

Si en cualquier momento falla un acceso (carpeta compartida, Excels de
control), corré [`verificar-entorno`](../verificar-entorno/SKILL.md) y
explicá al asesor qué falta antes de seguir — es especialmente probable
que esto pase la primera vez que alguien nuevo del equipo usa el plugin.

## Paso 7 — Resumen final

Mostrá un resumen claro de todo lo que se hizo: carpeta creada (ruta
completa), número de cotización y de oferta usados, equipo cargado en la
matriz, y en qué filas quedó registrado en cada uno de los dos Excels de
control. Aclará explícitamente cualquier cosa que haya quedado pendiente
de confirmar (precio no actualizado, accesorio sin match exacto, brecha
de presupuesto, etc.) — nunca cierres el resumen dando algo por resuelto
que en realidad quedó a medias.

## Caso: cambio de marca o versión sobre una cotización existente

Si el pedido no es un cliente nuevo sino "recotizar esto que ya existe
con otra marca" o "hacele una versión nueva a esta cotización", el Paso 1
de acá sigue aplicando para detectar qué cambió (cantidad, spec, marca
nueva), pero el Paso 3 usa el flujo de "cambio de marca" de
`buscar-equipo` y el Paso 6 usa el "Caso 2" de `armar-cotizacion`
(versionado) en vez del "Caso 1" — el resto de la orquestación (preguntar
lo que falte, confirmar antes de escribir, registrar en los dos Excels)
es igual.

## Estado

Diseñado 2026-09-08 a partir del flujo de punta a punta ya probado
manualmente (ver `sandbox-pruebas/`) encadenando `buscar-equipo` +
`armar-cotizacion` a mano. Esta capa de orquestación (detectar huecos,
preguntar agrupado, encadenar automáticamente) **todavía no se probó en
una conversación real** iniciada solo con un pedido en lenguaje natural —
antes de darla por "Funcional", correr al menos un caso de punta a punta
así con Fabián o el equipo de preventa.
