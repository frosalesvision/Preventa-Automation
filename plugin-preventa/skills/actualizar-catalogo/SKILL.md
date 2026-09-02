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

## Columnas del catálogo (23, orden fijo por prioridad — actualizado 2026-08-28)

El orden de columnas **no es alfabético ni de conveniencia técnica**:
está pensado para que un asesor de preventa vea lo más importante
primero al escanear la tabla de izquierda a derecha, sin tener que
scrollear. No reordenar sin razón — si se agrega una columna nueva,
ubicarla dentro del grupo que le corresponda (ver grupos abajo).

| # | Columna | Notas |
|---|---|---|
| 1 | Nombre de equipo/producto | |
| 2 | Marca | |
| 3 | Modelo / SKU | El identificador exacto del proveedor. Junto con "Proveedor" es la clave para no duplicar filas — ver abajo |
| 4 | Categoría / tipo | Cámara, control de acceso, alarma, incendio, cableado, accesorio, etc. |
| 5 | Proveedor | |
| 6 | Precio USD | Dejar vacío si el documento no da precio en dólares. Ver "Tipo de cambio y precios" abajo — puede ser el dato dado directamente o uno calculado a partir del CRC |
| 7 | Precio CRC | **Fórmula**, no se escribe a mano (ver "Tipo de cambio y precios") |
| 8 | Precio especial GV (USD) | Solo si el documento indica un precio negociado distinto al de lista |
| 9 | Precio especial GV (CRC) | **Fórmula**, igual que Precio CRC |
| 10 | Unidad de venta | `Unidad` en la mayoría de los casos; usar `Metro`, `Rollo`, `Caja`, etc. cuando el producto se venda por medida (ej. cable) en vez de por unidad |
| 11 | Tiempo de entrega (días) | Lead time del proveedor si lo indica. Útil para saber si un equipo se puede prometer a tiempo en una cotización |
| 12 | País de origen | Relevante para licitaciones que piden certificación de origen del fabricante (ej. tipo NDAA). Dejar vacío si el documento no lo indica |
| 13 | Descripción | Texto libre, tal como lo da el documento fuente. Si el documento trae una nota aparte (cambio de precio, aviso de reemplazo, "solo bajo pedido", etc.), agregarla al final de este mismo campo como `-- Nota del proveedor: <texto>` en vez de crear una columna nueva o perder el dato |
| 14 | Especificaciones técnicas clave | Lo necesario para comparar contra un pliego de condiciones (resolución, protección IP, certificaciones, etc.), si se puede extraer como algo distinto de la Descripción general |
| 15 | Fecha de última actualización | Fecha en la que se cargó/actualizó esta fila (no la fecha del documento si son distintas — aclarar cuál es cuál si hay duda). Guardar como texto `AAAA-MM-DD`, no como fecha de Excel |
| 16 | Vigencia del precio | Si el documento indica una validez (ej. "15 días") |
| 17 | Peso | Dejar vacío si el documento no lo indica |
| 18 | Dimensiones (H×W×D) | Dejar vacío si el documento no lo indica |
| 19 | Código HTS | Código arancelario, si el documento lo trae. Uso de logística/aduanas, no de preventa — dejar vacío si no aplica |
| 20 | Código ECCN | Clasificación de control de exportación, si el documento lo trae. Dejar vacío si no aplica |
| 21 | Código EAN | Código de barras, si el documento lo trae. Dejar vacío si no aplica |
| 22 | Archivo de origen | Nombre del documento dentro de `Catalogos Proveedor/<Proveedor>/` que sustenta esta fila. Si el dato vino pegado directo en el chat (sin documento), anotar algo como "Dato dado por <asesor> en chat, DD/MM/AAAA" en vez de dejarlo vacío — la trazabilidad importa igual |
| 23 | Pestaña / Hoja de origen | Si la fuente es un Excel: nombre exacto de la pestaña de donde vino esta fila (ej. "HVA Pricelist"), para poder rastrear el dato si algo se pierde o se ve raro. Vacío si el origen fue un PDF o un dato pegado en el chat (no aplica) |

**Grupos de columnas (para saber dónde insertar una columna nueva)**:
identidad y precio (1-9, lo primero que ve un asesor) → clasificación
de venta (10-12) → texto descriptivo (13-14) → metadata de la fila
(15-16) → logística/aduanas (17-21, dejar vacío si el documento no lo
trae, nunca inventar ni preguntar por cada campo faltante) →
trazabilidad de origen (22-23, siempre al final).

No hay una pestaña de historial de precios — el archivo vive en
SharePoint/OneDrive, que ya guarda automáticamente el historial de
versiones del archivo completo (el asesor puede ver "Historial de
versiones" desde el navegador si necesita ver un precio anterior). No
dupliques ese trabajo con una pestaña propia.

## Tipo de cambio y precios (agregado 2026-08-28)

Hay una segunda pestaña, **`Tipo de Cambio`**, con dos celdas
editables a mano por el equipo (`B3` = tipo de cambio de compra, `B4`
= tipo de cambio de venta, ambos colones por USD) y dos nombres
definidos a nivel de libro que las referencian: `TipoCambioCompra` y
`TipoCambioVenta`.

- **Precio CRC** (columna 7) y **Precio especial GV (CRC)** (columna
  9) son fórmulas, no valores escritos a mano:
  `=IF(F2="","",IF(TipoCambioVenta="","Actualizar TC",ROUND(F2*TipoCambioVenta,2)))`
  (ajustando la columna de referencia para la fila 9). Usan el tipo de
  cambio de **venta** para convertir el precio en dólares a colones.
  Si `B4` todavía no tiene un valor cargado, la celda muestra
  "Actualizar TC" en vez de 0, para que no se lea como un precio real.
- **Al agregar una fila nueva**: escribí el precio en dólares en
  "Precio USD" (columna 6) y dejá que la fórmula de "Precio CRC"
  calcule sola — no escribas un valor literal en esa columna. Copiá la
  fórmula de la fila anterior hacia abajo (mismo patrón relativo) en
  vez de tipear una fórmula nueva a mano.
- **Si el documento fuente solo da el precio en colones** (no en
  dólares): calculá el equivalente en USD como
  `Precio CRC del documento / TipoCambioVenta` y escribí ese resultado
  como valor literal en "Precio USD" — la fórmula de "Precio CRC"
  recalculará y debería coincidir (con un margen mínimo de redondeo)
  con el valor original del documento. Nunca escribas un valor literal
  directamente en la columna "Precio CRC".
- Si el equipo pide actualizar el tipo de cambio, el cambio va en `B3`/
  `B4` de la pestaña `Tipo de Cambio` — eso solo actualiza todas las
  filas del catálogo automáticamente vía la fórmula, no hay que tocar
  fila por fila.

## Formato y presentación (agregado 2026-08-28)

El Excel es una tabla de Excel real (`ListObject`, nombre
`TablaCatalogo`), no un rango suelto — esto da los filtros desplegables
por columna y el sombreado alternado de filas automáticamente. Al
agregar filas nuevas, **hay que agregarlas dentro del rango de la
tabla** (extendiendo `TablaCatalogo`, no escribiendo debajo de ella) para
que hereden el estilo, los filtros y (en las columnas de precio CRC) la
fórmula automáticamente.

Reglas de formato a mantener:
- **Sin ajuste de texto (wrap text) en ninguna celda** y altura de fila
  fija (18pt). La Descripción y otros campos largos se ven truncados en
  pantalla — es intencional, así cada fila ocupa un solo renglón y la
  tabla es escaneable. El contenido completo sigue ahí; se ve entero
  haciendo clic en la celda (barra de fórmulas) o ensanchando la
  columna, no hace falta que la fila crezca.
- Encabezado (fila 1) congelado (`FreezePanes`) para que se mantenga
  visible al hacer scroll.
- Precio USD y Precio especial GV (USD) con formato de moneda en
  dólares; Precio CRC y Precio especial GV (CRC) con formato de moneda
  en colones (símbolo ₡).
- Anchos de columna pensados para lectura rápida: Nombre y Descripción
  anchas, Archivo de origen ancha (los nombres de archivo reales son
  largos), campos de código (HTS/ECCN/EAN) angostos.

Nota técnica para quien ejecute este skill: si hay que escribir cientos
o miles de filas de una sola vez (ej. cargando un pricelist completo de
un proveedor), la forma confiable de hacerlo (confirmado 2026-08-28/29,
probado con Hanwha + InVid combinados, ~2,360 filas) es con **Python +
`openpyxl`** — sí está disponible en este entorno (`python` en PowerShell/
Bash, se puede `pip install openpyxl pdfplumber` si hace falta) —, no
con automatización COM de Excel: escribir miles de filas con texto largo
vía COM (`Range.Value2` masivo, o incluso celda por celda) agota la
memoria del proceso (`OutOfMemoryException`) y en esta máquina en
particular la configuración regional de Excel está corrompida
(`Excel.International()` devuelve separadores inválidos), lo que
además distorsiona cualquier número con formato de moneda o decimales
escrito por esa vía. `openpyxl`
escribe el `.xlsx` directamente sin pasar por el motor de Excel, evita
ambos problemas, y además permite crear la tabla (`openpyxl.worksheet.
table.Table`), las fórmulas, los nombres definidos y el formato en el
mismo script. Si el documento fuente es un PDF con tablas, usá
`pdfplumber` (`page.extract_tables()`) en vez de extracción de texto
lineal — el texto lineal puede mezclar el orden de columnas de precio
de forma inconsistente entre secciones, mientras que la extracción de
tabla respeta la estructura real. **Importante**: verificá la
distribución de cantidad de columnas por fila (`len(row)`) antes de
asumir un índice fijo — un mismo PDF puede tener secciones con distinta
cantidad de columnas (ej. una columna de imagen que solo existe en
algunas páginas), y asumir el índice equivocado corre el SKU y la
descripción una posición sin dar ningún error visible.

## Regla de no duplicados

**Una fila es "la misma" si coinciden Modelo/SKU + Proveedor** (o
Nombre + Proveedor cuando el documento no da SKU). El mismo producto
ofrecido por dos proveedores distintos son dos filas válidas, no un
duplicado.

**Excepción confirmada**: si el mismo Modelo/SKU + Proveedor aparece
con un **precio distinto** porque una de las dos filas es stock
limitado/liquidación (visto en Hanwha: el mismo SKU en la pestaña
principal y en "Limited Stock" a un precio más bajo), no es un
duplicado — son dos ofertas reales distintas. Dejá ambas filas y
agregale a la de menor precio una nota en Descripción tipo "Precio de
stock limitado / liquidación (disponibilidad no garantizada)" para que
no se confunda con un error de carga. Sí hay que deduplicar cuando el
mismo SKU + el mismo precio aparece repetido sin razón (ej. un producto
"nuevo" que también sigue en la lista general con el mismo precio) —
ahí quedate con una sola fila.

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
   completando "Archivo de origen", "Pestaña / Hoja de origen" (si la
   fuente es un Excel; vacío si es PDF o dato pegado en chat), y "Fecha
   de última actualización" para cada fila tocada. Las filas nuevas van
   dentro del rango de la tabla `TablaCatalogo` (no debajo, suelto) y
   con la fórmula de Precio CRC copiada de la fila anterior, no un valor
   a mano — ver "Tipo de cambio y precios" y "Formato y presentación"
   arriba para el detalle de cómo escribir cada columna.
6. **Mostrá un checklist final**: cuántas filas se agregaron, cuántas
   se actualizaron, y si algo quedó sin poder procesar (y por qué).

## Pestaña "Compatibilidad de Accesorios" (agregado 2026-09-01)

Después de cargar o reemplazar un catálogo de proveedor grande (ej. un
pricelist completo nuevo), corré también
`scripts/generar_matriz_accesorios.py "<ruta al Catalogo de productos
por proveedor.xlsx>"` para refrescar la pestaña **`Compatibilidad de
Accesorios`** dentro del mismo Excel (agrega/reemplaza esa pestaña
puntual, no toca `Catalogo` ni `Tipo de Cambio`). La consume
[`buscar-equipo`](../buscar-equipo/SKILL.md) para saber qué bases/
soportes/lentes son compatibles con cada modelo de cámara. Combina tres
fuentes (columna "Fuente" de la pestaña): compatibilidad que el propio
fabricante escribe en el catálogo, match por categoría genérica dentro
del mismo catálogo, y un puñado de pares verificados a mano en una
cotización real (estos últimos viven como lista literal dentro del
script — regenerar no los borra, pero tampoco los descubre solos). Ver
el detalle completo en `buscar-equipo/SKILL.md`, sección "Cómo se
construye la pestaña Compatibilidad de Accesorios". No es un paso
bloqueante del proceso de arriba — si no se regenera, `buscar-equipo`
simplemente no va a poder sugerir accesorios para los productos más
nuevos hasta que se corra.

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
realmente sincronizada/compartida en OneDrive — no llegó a ser visible
para los compañeros. Corregido el 2026-08-28: la estructura se recreó
dentro de `CLIENTES/00_IA_PREVENTAS/Preventas/Catalogo/`, confirmada
como realmente sincronizada.

Probado en sandbox el 2026-08-28/29 con datos reales de **dos**
proveedores (no sintéticos): el pricelist completo de Hanwha Vision
America (Excel, 3 pestañas) y el catálogo completo de InVidTech
(PDF de 40 páginas, marcas InVid/Milesight/Paramont/Vision/Secure),
cargados juntos en
`sandbox-pruebas/CLIENTES/00_IA_PREVENTAS/Preventas/Catalogo/`.
Catálogo final: **2,358 productos únicos** (1,410 Hanwha + 948 del PDF
de InVid). Esta prueba llevó al diseño final de columnas (23,
reordenadas por prioridad), la pestaña de Tipo de Cambio con fórmulas
de conversión, el formato de tabla, y la pestaña de Guía de columnas —
todo documentado arriba. También destapó y corrigió dos bugs reales de
extracción (ver "Formato y presentación" arriba para el detalle
técnico):
- El PDF de InVid cambia de 7 a 6 columnas a partir de la página 32
  (sin columna de imagen), lo que corría el SKU y la descripción una
  posición si se asumía un índice fijo — corregido detectando el
  ancho real de cada fila.
- El Excel de Hanwha repite el mismo producto en más de una pestaña
  ("New" y "HVA Pricelist"); 268 filas eran puro duplicado y se
  quitaron, pero 28 casos tenían un precio distinto porque una fila
  era stock limitado — esos se dejaron como dos filas válidas (ver
  "Regla de no duplicados" arriba).

Fabián revisó el archivo de sandbox y aprobó el paso a producción — el
catálogo real (`CLIENTES/00_IA_PREVENTAS/Preventas/Catalogo/Catalogo de
productos por proveedor.xlsx`) ya tiene estos mismos 2,358 productos
cargados (2026-08-29/09-01). Pendiente antes de darlo por completamente
funcional: probar el flujo de **actualización** de una fila existente
(no solo alta de filas nuevas) y el flujo de datos pegados directo en
el chat sin ningún archivo de por medio.
