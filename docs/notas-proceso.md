# Notas del proceso de negocio — Preventa (Grupo Visión)

> Documento de contexto interno, NO es un skill. Sirve para que cualquiera
> que mantenga este plugin entienda el proceso real sin tener que
> preguntarle a preventa de nuevo. Si el proceso cambia, actualizar acá
> primero y después revisar si algún SKILL.md quedó desalineado.

## Quién hace qué

El equipo de preventa arma cotizaciones de sistemas de seguridad/cámaras
para clientes. Hoy el proceso es 100% manual, en Excel, con trabajo
duplicado entre un Excel maestro compartido y el Excel personal de cada
asesor.

## Flujo actual (manual)

1. **Registro en Excel maestro compartido.** Columnas: letra de quién
   trabaja, cliente, descripción, fecha del proyecto, fecha de entrega,
   número de oferta, monto sin IVA, proveedor, estado, asesor comercial,
   notas.
2. **Duplicado en Excel personal.** Cada asesor replica la misma info en
   su propio archivo. Es trabajo repetido, no aporta nada nuevo — candidato
   claro a eliminar cuando haya una fuente única de verdad.
3. **Armado de la cotización** en una matriz de Excel con pestañas:
   cámaras, productos, materiales, OPEX/mano de obra, y una hoja final
   que se exporta a PDF como la cotización oficial para el cliente.
4. **Cierre y traspaso a Bitrix24.** Al cerrar la cotización se sube
   manualmente a un tablero Kanban en Bitrix24. De ahí Compras y luego
   Operaciones/Implementación continúan el flujo. **El proceso de
   preventa termina en este punto** — todo lo posterior (compras,
   implementación) está fuera del alcance de este plugin.

## Numeración — DOS sistemas distintos (confirmado con datos reales)

Lo que se dijo al inicio ("consecutivo por cliente, formato T0010") no es
exacto. Revisando el Excel maestro real y las carpetas compartidas hay
**dos numeraciones separadas**:

1. **"Cotización #N" (numeración de carpeta):** consecutivo por cliente,
   asignado a mano — pero **no todos los clientes lo llevan igual**: se
   confirmó al menos un caso donde es continuo entre años (2024 llega a
   #28, 2025 sigue 28-63, 2026 sigue en #64+) y otro donde parece
   reiniciar cada año (2025 tiene #1, 2026 vuelve a #1). No hay una
   regla única — `armar-cotizacion` calcula ambos candidatos y pregunta
   si no coinciden, en vez de asumir uno.
2. **"Número de oferta" real (el que ve el cliente):** formato
   `T{prefijo}-{7 dígitos}-{año}` (ej. `T4-0000006-26`, `T5-0000003-26`).
   Solo se encontraron los prefijos **T1, T4, T5** en el Excel maestro.
   T4 y T5 se reparten entre MUCHOS clientes distintos (no es por
   cliente) y el consecutivo se reinicia varias veces en el año — no es
   tampoco un contador global único. Qué determina T1 vs T4 vs T5
   **se confirmó que nadie lo sabe** — se le preguntó directamente al
   equipo de preventa y "no sabían que así era el standard, ellos se
   adaptan al mismo pero no tenían idea". Hipótesis sin confirmar: podría
   venir de Bitrix24 (categoría/pipeline asignada al crear el deal) —
   revisar esto cuando `sync-bitrix` tenga credenciales. Este es el
   número que **ancla el proyecto en Operaciones**, no el "Cotización
   #N" de la carpeta.
- El versionado (ver abajo) se aplica sobre el número de oferta real
  (T-xxx), agregando un sufijo — nunca sobre el "Cotización #N".

## Versionado de cotizaciones (confirmado con archivos reales)

- **Cambio menor:** dentro de la misma carpeta `Matriz-Oferta/` aparece
  un PDF nuevo con sufijo de versión agregado al número de oferta —
  visto en la práctica como `V2`, `v2`, `(V3)`, `// v3`, `-v2`, sin un
  formato fijo (se escribe a mano, cada quien lo hace distinto). **El
  PDF anterior se conserva**, no se borra. A veces también se duplica el
  `.xlsx` de la matriz con el mismo sufijo; otras veces se sobrescribe el
  mismo `.xlsx` y solo se ve la versión nueva en el PDF. **Sin carpeta
  nueva** — se confirmó exactamente como se describió al inicio.
- **Cambio grande** (ej. cambiar de marca de cámara completa): se genera
  una **copia nueva** del Excel (no una versión del mismo archivo).
- La distinción entre "menor" y "grande" hoy la decide el criterio del
  asesor — no hay una regla dura escrita. Cualquier automatización debe
  preguntar o inferir con cautela, no asumir.

## Estructura real de las carpetas compartidas (paso 3, confirmada)

Cada cliente es una carpeta de primer nivel dentro de `CLIENTES/`
(revisados ~283 clientes). Debajo de cada cliente, la convención de
agrupado por año **varía** — se vieron los tres patrones siguientes en
clientes distintos, sin una regla única:

- Carpetas de cotización directamente bajo el cliente, sin año (plano).
- `<Cliente> -AAAA/Cotización #N[-AAAA] <descripción corta>/` (una
  subcarpeta por año).
- `Cotizaciones AAAA/Cotización #N[-AAAA] <descripción corta>/` (variante
  de nombre de la subcarpeta de año).

El nombre de la subcarpeta de año y el "-AAAA" dentro del nombre de
"Cotización #N" a veces **no coinciden** (ej. una cotización etiquetada
"#1-2025" dentro de una carpeta de año "2026") — es error humano de
tipeo, no una regla. `armar-cotizacion` debe tolerar esto, no asumir que
siempre van a coincidir.

**Dentro de cada carpeta "Cotización #N..." las mismas 5 subcarpetas
aparecen de forma consistente:**

```
Cotización #N-AAAA <descripción>/
├── Cotizaciones/          → PDFs de la oferta enviada, docs fuente de licitación, cuadros comparativos
├── Fichas Técnicas/       → hojas de especificación de los equipos cotizados
├── Implementacion/        → (ya es de Operaciones, pero la carpeta existe desde preventa)
│   ├── Actas de entrega/
│   ├── Boletas de servicio/
│   ├── Documentación del proyecto/
│   └── Mantenimiento/
├── Matriz-Oferta/         → el Excel matriz + el/los PDF(s) final(es), nombrados con el número de oferta real
└── Visita técnica/        → fotos/notas de la visita al sitio
```

Excepción observada: al menos un cliente tenía una iniciativa grande
(ej. un proyecto de RFID) organizada totalmente distinto, con
subcarpetas ad hoc (`Oferta Final/`, `PROYECTO AMPLIACION/`, `Old/`) y
sufijos `_OLD`, `V2`, `V3` sin convención fija. No hay que asumir que el
patrón de 5 subcarpetas es universal — `armar-cotizacion` debe manejar
el caso de no encontrarlo y avisar, no fallar en silencio.

## La matriz de Excel (Matriz-Oferta) — nunca leer/escribir una ya en uso

⚠️ **El contenido de una matriz YA EN USO por un cliente es información
financiera sensible de la empresa.** Se confirmó que las pestañas de
esta matriz son literalmente una "MATRIZ DE COSTO PROYECTO": costo real
de compra por proveedor, columnas de **margen/markup interno** (varios
porcentajes encadenados, ya fijos en la plantilla — no los decide el
asesor cada vez) y el **precio de venta + utilidad en dólares**
calculados por fórmula.

**Decisión (2026-08-24, confirmada con el usuario):** `armar-cotizacion`
**nunca lee ni escribe el contenido de una matriz ya en uso**. Como
mucho nombra, mueve o copia el `.xlsx`/`.pdf` como bloque opaco. El
costo/margen lo sigue manejando el asesor con sus propias fórmulas.

**Actualización (2026-08-26):** el usuario consultó directamente con el
equipo de preventa (Alessandro) y confirmó autorización para trabajar
con estos archivos **a nivel de plantilla/machote** (no de datos reales
de un cliente específico). Se encontró y verificó **en blanco** (sin
ningún dato real, solo estructura y las fórmulas de margen fijas) la
plantilla oficial en uso actual, ya copiada a
`plugin-preventa/skills/armar-cotizacion/references/`:

- **`Machote Matriz y oferta.xlsx`** (35 pestañas: `Equipos` — antes
  llamada `Cámaras`, `Productos 2-5`, `MATERIALES`, `PRODUCTO G-O`,
  `RESUMEN`, `RESUMEN (OPEX)`, `OPEX GV`, `MANO DE OBRA`, `Transporte`,
  `Evaluacion TIR-VAN`, `COTIZACIÓN`, servicios específicos como
  `BodyCam`/`Face Pro`/`LPR Patrullas`). Para proyectos de equipos
  individuales (cámaras, control de acceso, alarmas) — que en la
  práctica es prácticamente todo lo que arma preventa hoy.

**Cómo se llegó a la versión final (lección importante):** el primer
intento fue copiar una copia de `Machote Matriz y oferta.xlsx` desde la
carpeta de un cliente real (Banco Nacional, modificada 28/01/2025) y
verificarla en blanco — eso funcionó. Pero al preguntarle a Alessandro
si esa era la actual, dijo que hace poco hubo cambios. Buscar "la copia
modificada más recientemente con ese nombre" **no funcionó**: la más
reciente encontrada (Moog Medical, 12/08/2026) resultó ser una
cotización real ya llena que alguien nunca renombró, y la copia de la
carpeta oficial `A-Machotes Cotizaciones/` tampoco estaba en blanco (con
un `#REF!` roto) — parece ser un ejemplo de trabajo terminado para
enseñar el formato, no una plantilla vacía. **La única forma confiable
fue que Alessandro compartiera su copia directamente** (vía chat, quedó
en `Descargas` del usuario) — verificada en blanco, con el cambio real:
la pestaña `Cámaras` ahora se llama `Equipos`. Lección: nombre de
archivo + fecha de modificación **no sirven** para identificar una
plantilla en blanco — siempre verificar el contenido, y preferir pedir
el archivo directo a quien lo usa en vez de buscarlo por patrón.

Se descartó una segunda plantilla, `MCV_PLANTILLA_v8.xlsx` (12 pestañas,
usada en 51 archivos de AVIANCA/EKONO/Condominio Bellavista/Condominio
Noa) — parecía una segunda familia para "proyectos multi-sitio", pero
**"multi-sitio" es una categoría que Claude infirió, no un término que
el equipo reconozca**: al preguntarle directamente a Alessandro, nunca
había hecho una carpeta así. Revisando fechas de modificación de los
archivos reales, el último uso confirmado es de **2022-2023** — no es
parte de la práctica actual del equipo. No se incluye en `references/`
por ahora; si en el futuro reaparece una cuenta grande multi-sitio,
agregar la plantilla de nuevo con evidencia de uso reciente, no por
asunción.

Existe además una carpeta oficial de la empresa `A-Machotes
Cotizaciones/` con estos machotes y un `readme.txt` que advierte que
`Implementacion/Documentación del proyecto/` guarda **IPs, usuarios y
contraseñas de equipos instalados** — esa subcarpeta específica sigue
totalmente fuera de alcance, nunca leerla ni abrir nada dentro.

`armar-cotizacion` **copia** (no lee celdas) el machote al crear una
cotización nueva — sin preguntar "qué tipo de proyecto es", porque en
la práctica actual solo hay un tipo.

Nota de proceso (sigue vigente): el usuario solo había autorizado acceso
a 3 URLs puntuales al inicio. Cualquier exploración más profunda de
carpetas/archivos específicos de clientes reales se confirma primero
con el usuario — la autorización del 2026-08-26 fue explícita y
puntual para machotes en blanco, no una autorización general para leer
cotizaciones reales de clientes.

## Cómo trabaja el equipo en la práctica (confirmado con Alessandro, 2026-08-26)

- Todo el trabajo es en la nube vía **OneDrive sincronizado** (no vía
  navegador web) — al menos Alessandro y Katherine confirman el mismo
  proceso.
- **Solo el Excel de la matriz se trabaja en vivo** dentro de la carpeta
  sincronizada (autoguardado). El resto de los archivos —oferta en PDF,
  fichas técnicas, info del proyecto, fotos de la visita— se arman
  **aparte** y se **suben a la carpeta recién cuando están listos**, no
  en vivo.
- Implicación para `armar-cotizacion`: es normal y esperado que
  `Cotizaciones/`, `Fichas Técnicas/`, `Visita técnica/` e
  `Implementacion/*` queden vacías por un buen rato después de crear la
  carpeta de la cotización — no es una señal de que algo falló.
- Se decidió **no** construir un fallback por navegador web para cuando
  alguien no tenga OneDrive activo (ver discusión en el chat) — es
  frágil (ver los problemas de sesión que tuvimos nosotros mismos
  probando esto) y mejor que `verificar-entorno` lo marque como
  bloqueante claro en vez de ofrecer un plan B poco confiable.

## El cuello de botella más grande (ampliado 2026-08-26, confirmado por ventas)

La descripción original ("buscar a mano el accesorio de montaje según
marca de cámara") era **una versión chica del problema real**. Ventas
lo confirmó directamente: a partir de una especificación técnica dada
por el cliente o una licitación, hay que **buscar marca y modelo de
CUALQUIER equipo** (no solo accesorios de cámara — control de acceso,
alarmas, NVR, lo que sea) que la cumpla al 100%. Hoy lo hacen "a pie"
con ayuda de IA genérica, sin certeza — y lo pidieron explícitamente:
*"nos serviría demasiado tener una IA que busque con más certeza para
tener un norte de cuáles equipos podrían ser."*

Casos donde el cliente indica marca/modelo directamente (ej. UCR) son
la excepción, no la regla — casi nadie lo hace así.

**Esto sigue sin automatizarse en fase 1**, pero ya se registró como
skill futuro planeado: `buscar-equipo` (placeholder en
`plugin-preventa/skills/buscar-equipo/`) — no inventar la lógica
todavía, falta definir alcance con el usuario primero, igual que se
hizo con `armar-cotizacion`.

## Cómo llega una solicitud de licitación (confirmado con ejemplo real, 2026-08-26)

Por correo o Bitrix (según ventas, "llega a ser lo mismo"), a preventa
le llega para una licitación de gobierno: **cliente + número de
licitación**, **fechas clave** (plazo de aclaraciones, plazo de entrega
de oferta), y **documentos** con requisitos de admisibilidad +
especificaciones técnicas con cantidades. Preventa se enfoca en la
parte de **equipos** (especificaciones, cantidades, mano de obra) — el
resto (garantías, multas, cláusulas legales del cartel) no es su
trabajo. Para clientes corporativos es el mismo patrón, a veces con
visita técnica para valorar equipo y mano de obra.

⚠️ **Regla sobre documentos de terceros (confirmada 2026-08-26):** a
veces estos documentos (ej. un "estudio de mercado" municipal) incluyen
como anexo las **propuestas completas de la competencia** — vistas en
un caso real, incluso con aviso explícito de confidencialidad propio
del competidor. Estos documentos se usan **únicamente para entender el
proceso/contexto**, nunca se copia, cita ni incorpora nada de su
contenido específico (precios, specs, personal) a ningún archivo de
este plugin ni a `references/`.

## Precios de proveedores

Muchos precios no están en un catálogo centralizado: se consultan por
correo, WhatsApp o llamada. Existen sí algunas fuentes semi-
centralizadas (en revisión, 2026-08-26):

- `BD Proveedores - Clientes.xltm` — en
  `GRUPO VISION CR/COMERCIAL 2024/PREVENTA 2026/Base datos de
  proveedores/` (biblioteca de SharePoint distinta a `CLIENTES`,
  requiere acceso directo de OneDrive aparte).
- Carpeta `PRECIOS EQUIPOS Y ACCESORIOS` en el OneDrive personal de
  Alessandro (cuenta `alazzarotto_grupovision_org`) — según él, "lo más
  actualizado".

Esto significa que `armar-cotizacion` no puede asumir que todos los
precios están disponibles localmente; en fase 1 probablemente dependa
de que el usuario los tenga a mano o de un catálogo parcial en
`references/`. El futuro skill `buscar-equipo` sí dependería
directamente de estas fuentes una vez verificadas.

## Integración con Bitrix24

- Tableros tipo Kanban.
- Preventa sube manualmente la cotización cerrada; de ahí sigue Compras
  y Operaciones/Implementación.
- **Fase 1 de este plugin NO tiene webhook/API key de Bitrix24 todavía.**
  Se va a pedir a nivel gerencial más adelante. Por eso `sync-bitrix` es
  un placeholder y `plugin-preventa/.mcp.json` tiene la config comentada,
  lista para activarse cuando llegue la credencial.

## Decisiones de diseño de `armar-cotizacion` (confirmadas 2026-08-24)

- **Número de "Cotización #N":** el skill lo propone (lista carpetas
  existentes del cliente y sugiere N+1); el asesor confirma antes de
  crear.
- **Cambio menor vs. grande:** el skill **siempre pregunta**, nunca
  infiere — no hay regla fija hoy.
- **Carpeta de año:** si el cliente ya tiene un patrón (`<Cliente>
  -AAAA` o `Cotizaciones AAAA`), seguirlo. Si el cliente es
  **completamente nuevo**, usar `Cotizaciones AAAA` como convención
  unificada de acá en adelante.
- **Qué crear al iniciar una cotización (actualizado 2026-08-26):** las
  5 subcarpetas estándar, y en `Matriz-Oferta/` copiar siempre
  `Machote Matriz y oferta.xlsx` (ver sección de la matriz más abajo) —
  sin preguntar "qué tipo de proyecto es", esa categoría no existe en la
  práctica actual del equipo. Decisión anterior ("solo carpetas
  vacías") quedó reemplazada al confirmar que sí hay un machote oficial
  en blanco y autorización para usarlo.
- **Número de oferta real (T-prefijo):** el skill sí lo genera/propone
  (revisando el prefijo más reciente usado por el cliente o en general),
  pero **siempre con confirmación del asesor** — la regla del prefijo es
  desconocida incluso para el equipo, así que nunca se asume en
  silencio. Ver detalle completo en "Decisión (2026-08-24...)" arriba.
- **Límite de longitud de ruta de Windows (encontrado probando en el
  sandbox, 2026-08-26):** Excel no abre archivos cuya ruta completa pasa
  de ~259 caracteres — pasó de verdad probando con nombres de prueba
  largos. Con clientes reales de nombre largo (licitaciones con número
  de expediente completo, por ejemplo) esto es un riesgo real, no solo
  de la prueba. El skill calcula la ruta completa antes de crear nada y
  avisa si se acerca al límite, pidiendo una descripción más corta.

Detalle completo de la lógica en
[`armar-cotizacion/SKILL.md`](../plugin-preventa/skills/armar-cotizacion/SKILL.md).

## Alcance de fase 1 (lo que SÍ se construye ahora)

- `verificar-entorno`: chequeo de accesos/conexiones disponibles.
- `armar-cotizacion`: **organización de archivos y carpetas** de una
  cotización (crear/versionar la carpeta "Cotización #N-AAAA", ubicar
  archivos en la subcarpeta correcta, proponer numeración) — NO toca el
  contenido de la matriz de costos (ver sección de arriba).
- `seguimiento-correo`: redacción (no envío) de borradores de respuesta
  a clientes según etapa de la cotización.
- `sync-bitrix`: placeholder hasta tener credenciales de Bitrix24.

**Fuera de fase 1, ya registrado como planeado:** `buscar-equipo`
(búsqueda de marca/modelo por especificación técnica) — ver "El cuello
de botella más grande" arriba. Es trabajo futuro explícito, no se
construye todavía.

## Fuente de verdad para `armar-cotizacion`

Estado real (no asumir que sigue igual — revisar de nuevo si cambia):

- El **paso 1** (Excel maestro, export CSV) y **paso 2** (Excel personal
  por asesor, export CSV) ya se revisaron — están en
  `plugin-preventa/recursos-originales/` (ignorada por git, nunca se
  sube). Columnas confirmadas arriba en "Numeración" y en el flujo.
- El **paso 3** (carpetas compartidas por cliente) se puede leer
  directamente del disco local — OneDrive Business quedó sincronizado
  en esta máquina bajo `GRUPO VISION - DYNAMIC/Info Costa Rica -
  CLIENTES/` (fuera de la carpeta `OneDrive/` normal; la ruta exacta
  depende del registro de Windows, `HKCU\...\OneDrive\Accounts\Business1\
  Tenants`, si hay que volver a ubicarla en otra máquina). Es de
  **solo lectura** — nunca escribir ni modificar nada ahí.
- **No hace falta revisar el contenido de la matriz de costos** — ver
  "La matriz de Excel (Matriz-Oferta) — FUERA DE ALCANCE" arriba. Con
  la estructura de carpetas confirmada alcanza para diseñar la parte de
  `armar-cotizacion` que sí está en alcance (organización de archivos).
