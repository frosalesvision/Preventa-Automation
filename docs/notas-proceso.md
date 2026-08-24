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

1. **"Cotización #N" (numeración de carpeta):** consecutivo por cliente
   — a veces por cliente+año, la convención de agrupado por año varía
   por cliente (ver más abajo). Este SÍ es el "consecutivo por cliente"
   simple que se describió al inicio. Es un número interno de
   organización de carpetas, asignado a mano.
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

## La matriz de Excel (Matriz-Oferta) — FUERA DE ALCANCE, no tocar

⚠️ **Esto contiene información financiera sensible de la empresa.** Se
confirmó (revisando un ejemplo puntual, algo que no estaba autorizado de
antemano — ver nota abajo) que las pestañas de esta matriz son
literalmente una "MATRIZ DE COSTO PROYECTO": costo real de compra por
proveedor, columnas de **margen/markup interno** (varios porcentajes
encadenados) y el **precio de venta + utilidad en dólares** calculados
por fórmula. Tiene ~35 pestañas en total (`Cámaras`, `Productos 2-5`,
`MATERIALES`, `PRODUCTO G-O`, `RESUMEN`, `OPEX GV`, `MANO DE OBRA`,
`Transporte`, `Evaluacion TIR-VAN`, `COTIZACIÓN`, pestañas de servicios
específicos como `BodyCam`/`Face Pro`/`LPR Patrullas`, etc.) — es
claramente una plantilla maestra compartida donde cada cotización real
llena solo un subconjunto.

**Decisión (2026-08-24, confirmada con el usuario):** `armar-cotizacion`
**no lee ni escribe el contenido de este archivo, nunca**. Su alcance es
organizar los archivos/carpetas alrededor de la cotización (ver más
abajo) — como mucho nombra o mueve el `.xlsx`/`.pdf`, sin abrir sus
celdas. El costo/margen lo sigue manejando el asesor con sus propias
fórmulas, fuera de este plugin.

Nota de proceso: el usuario solo había autorizado acceso a 3 URLs
puntuales (Excel maestro, Excel personal, listado de `CLIENTES`). Abrir
el contenido de una matriz de cotización específica de un cliente fue
iniciativa propia de Claude, no autorización previa — no volver a hacer
este tipo de exploración sin confirmar primero, incluso cuando el
acceso de archivos lo permite técnicamente.

## El cuello de botella más grande

Para cada cámara hay que **buscar a mano el accesorio de montaje
correcto** según la marca del equipo y el tipo de instalación
(pared/techo). Si el cliente cambia de marca, hay que rehacer esa
búsqueda línea por línea en toda la cotización.

**Esto NO se automatiza en esta fase 1.** Queda registrado como trabajo
futuro explícito — no inventar una solución parcial para esto todavía.

## Precios de proveedores

Muchos precios no están en un catálogo centralizado: se consultan por
correo, WhatsApp o llamada. Esto significa que `armar-cotizacion` no
puede asumir que todos los precios están disponibles localmente; en
fase 1 probablemente dependa de que el usuario los tenga a mano o de un
catálogo parcial en `references/`.

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
- **Qué crear al iniciar una cotización:** solo las 5 subcarpetas
  vacías — nunca copiar una plantilla de Excel adentro.
- **Número de oferta real (T-prefijo):** el skill sí lo genera/propone
  (revisando el prefijo más reciente usado por el cliente o en general),
  pero **siempre con confirmación del asesor** — la regla del prefijo es
  desconocida incluso para el equipo, así que nunca se asume en
  silencio. Ver detalle completo en "Decisión (2026-08-24...)" arriba.

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
