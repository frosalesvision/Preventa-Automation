---
name: actualizar-catalogo
description: Mantiene actualizado el catálogo único de equipos y precios de proveedores en CLIENTES/00_IA_PREVENTAS/Preventas/Catalogo/Catalogo de productos por proveedor.xlsx, ya sea leyendo los PDFs (catálogos, listas de precios, cotizaciones) que el equipo agrega en CLIENTES/00_IA_PREVENTAS/Preventas/Catalogo/Catalogos Proveedor/<Proveedor>/, o a partir de datos de producto/precio que el usuario pegue directo en el chat sin ningún documento. Usar cuando el usuario agrega/actualiza un PDF de un proveedor, pega precios o specs de un producto para cargarlos, pregunta si el catálogo está al día, o necesita agregar/actualizar precios de productos.
---

# Actualizar catálogo

Mantiene `CLIENTES/00_IA_PREVENTAS/Preventas/Catalogo/Catalogo de
productos por proveedor.xlsx`, ya sea a partir de documentos de
proveedores en `CLIENTES/00_IA_PREVENTAS/Preventas/Catalogo/Catalogos
Proveedor/<Proveedor>/`, o de datos que el asesor pegue directo en el
chat sin ningún documento de por medio. Es el skill de **escritura**
sobre el catálogo — [`buscar-equipo`](../buscar-equipo/SKILL.md) es el
de lectura/búsqueda y depende de que este exista y tenga datos.

⚠️ Esto vive dentro de la carpeta compartida de producción real de la
empresa (`CLIENTES/00_IA_PREVENTAS/`, no en una carpeta aparte — ver
[`docs/notas-proceso.md`](../../../docs/notas-proceso.md) para el
detalle de ubicación y por qué se movió ahí). Antes de escribir
cualquier fila nueva o modificar una existente en el Excel, mostrale al
asesor exactamente qué vas a agregar/cambiar y esperá confirmación
explícita — igual que `armar-cotizacion`.

## Estructura de carpetas (actualizada 2026-08-28)

`00_IA_PREVENTAS/` vive **dentro de `CLIENTES`**, como una carpeta más
al mismo nivel que las carpetas de cada cliente — es la carpeta general
para todo lo de automatización/IA de preventa de Grupo Visión, no solo
el catálogo:

```
CLIENTES/
└── 00_IA_PREVENTAS/
    └── Preventas/
        └── Catalogo/
            ├── Catalogo de productos por proveedor.xlsx
            └── Catalogos Proveedor/
                ├── INVID/
                ├── AXIS/
                ├── Assa Abloy/
                └── <Proveedor>/         ← una subcarpeta por proveedor
```

Los compañeros solo tocan `Catalogos Proveedor/<Proveedor>/` (agregan o
reemplazan un documento). Nadie edita el Excel a mano línea por línea —
este skill lo hace por ellos, con confirmación.

## Columnas del catálogo

| Columna | Notas |
|---|---|
| Nombre de equipo/producto | |
| Categoría / tipo | Cámara, control de acceso, alarma, incendio, cableado, accesorio, etc. |
| Marca | |
| Modelo / SKU | El identificador exacto del proveedor. Junto con "Proveedor" es la clave para no duplicar filas — ver abajo |
| Descripción | Texto libre, tal como lo da el documento fuente |
| Especificaciones técnicas clave | Lo necesario para comparar contra un pliego de condiciones (resolución, protección IP, certificaciones, etc.) |
| Unidad de venta | `Unidad` en la mayoría de los casos; usar `Metro`, `Rollo`, `Caja`, etc. cuando el producto se venda por medida (ej. cable) en vez de por unidad |
| Proveedor | |
| Precio USD | Dejar vacío si el documento no da precio en dólares |
| Precio CRC | Dejar vacío si el documento no da precio en colones |
| Precio especial GV (USD) | Solo si el documento indica un precio negociado distinto al de lista |
| Precio especial GV (CRC) | Ídem, en colones |
| Fecha de última actualización | Fecha en la que se cargó/actualizó esta fila (no la fecha del documento si son distintas — aclarar cuál es cuál si hay duda) |
| Archivo de origen | Nombre del PDF dentro de `Catalogos Proveedor/<Proveedor>/` que sustenta esta fila. Si el dato vino pegado directo en el chat (sin documento), anotar algo como "Dato dado por <asesor> en chat, DD/MM/AAAA" en vez de dejarlo vacío — la trazabilidad importa igual |
| Vigencia del precio | Si el documento indica una validez (ej. "15 días") |

No hay una pestaña de historial de precios — el archivo vive en
SharePoint/OneDrive, que ya guarda automáticamente el historial de
versiones del archivo completo (el asesor puede ver "Historial de
versiones" desde el navegador si necesita ver un precio anterior). No
dupliques ese trabajo con una pestaña propia.

## Regla de no duplicados

**Una fila es "la misma" si coinciden Modelo/SKU + Proveedor** (o
Nombre + Proveedor cuando el documento no da SKU). El mismo producto
ofrecido por dos proveedores distintos son dos filas válidas, no un
duplicado.

## Proceso

1. **Identificar qué querés que se cargue.** No siempre hay un
   documento nuevo en `Catalogos Proveedor/<Proveedor>/` — el asesor puede simplemente
   **pegar los datos directo en el chat** (un producto, una lista, un
   precio que le dieron por WhatsApp) sin agregar ningún archivo. En
   ambos casos el objetivo es el mismo: identificar qué está tratando
   de hacer el usuario (agregar producto(s) nuevo(s), actualizar un
   precio, o solo consultar) y a qué proveedor corresponde, no asumir
   que siempre hay un PDF de por medio.
   - Si el pedido no aclara la fuente, preguntá: ¿viene de un
     documento en `Catalogos Proveedor/<Proveedor>/`, o son los datos que me estás
     pasando directo?
   - Si hay ambigüedad sobre qué archivo es (cuando sí hay documento),
     listá `Catalogos Proveedor/<Proveedor>/` y preguntale cuál es.
2. **Extraer las líneas de producto**, ya sea leyendo el documento
   (PDF, o el formato que sea) o tomando los datos que el usuario pegó
   directo en el chat: nombre, marca, modelo/SKU, descripción, specs,
   unidad de venta, precio(s) y moneda(s), y vigencia si la indica. En
   cualquier caso hay que llegar a estas líneas y agregarlas al Excel
   siguiendo los pasos 3 en adelante — no importa si vinieron de un
   archivo o de texto pegado.
   - Si el documento es un PDF escaneado sin texto seleccionable (solo
     imagen), avisá que no se puede leer automáticamente — no inventes
     los datos ni le pidas a nadie que los adivine.
   - Si un precio o dato viene ambiguo (ej. no está claro si es USD o
     CRC), preguntale al asesor en vez de asumir.
3. **Para cada línea extraída**, buscá en el Excel si ya existe una
   fila con el mismo Modelo/SKU (o Nombre) + Proveedor:
   - Si existe → es una **actualización**: proponé el precio/fecha
     nuevos, mostrando el valor anterior para comparar.
   - Si no existe → es una **fila nueva**.
4. **Mostrale al asesor un resumen claro** de todo lo que vas a
   agregar/actualizar (tipo tabla) antes de tocar el Excel, y esperá
   confirmación. Se puede confirmar todo junto o línea por línea si el
   asesor lo pide.
5. **Escribí los cambios confirmados** al `Catalogo de productos por proveedor.xlsx`,
   completando "Archivo de origen" y "Fecha de última actualización"
   para cada fila tocada.
6. **Mostrá un checklist final**: cuántas filas se agregaron, cuántas
   se actualizaron, y si algo quedó sin poder procesar (y por qué).

## Sobre quién mantiene esto al día

No hay una persona encargada — hoy preventa son 2 personas. La
responsabilidad de notar que algo está desactualizado recae en quien
usa [`buscar-equipo`](../buscar-equipo/SKILL.md): al traer un producto,
debe mirar "Fecha de última actualización" para decidir si conviene
confirmar el precio con el proveedor antes de cotizar, y si vale la
pena disparar una actualización de esa fila.

## Estado

Escrito el 2026-08-26. Estructura creada primero como carpeta hermana
`GV_IA_Automation/` (2026-08-27), pero esa carpeta nunca quedó
realmente sincronizada/compartida en OneDrive (se creó como carpeta
local suelta, sin el atributo de sincronización que sí tienen las
carpetas reales de SharePoint) — no llegó a ser visible para los
compañeros. Corregido el 2026-08-28: la estructura se recreó dentro de
`CLIENTES/00_IA_PREVENTAS/Preventas/Catalogo/`, confirmada como
realmente sincronizada (mismo atributo de OneDrive que tiene
`CLIENTES`). Incluye `Catalogos Proveedor/` y el Excel `Catalogo de
productos por proveedor.xlsx` con las 15 columnas confirmadas ya
escritas como encabezado (sin filas de datos todavía). **Falta probar
con al menos un PDF real de ejemplo (o datos pegados en chat) en un
sandbox**, igual que se hizo con `armar-cotizacion`, antes de darlo por
funcional.
