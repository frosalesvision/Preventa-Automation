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
