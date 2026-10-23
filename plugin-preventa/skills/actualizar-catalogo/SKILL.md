---
name: actualizar-catalogo
description: Mantiene actualizado el catálogo único de equipos y precios de proveedores en CLIENTES/00_IA_PREVENTAS/Preventas/Catalogo/Catalogo de productos por proveedor.xlsx, ya sea leyendo los PDFs (catálogos, listas de precios, cotizaciones) que el equipo agrega en CLIENTES/00_IA_PREVENTAS/Preventas/Catalogo/Catalogos Proveedor/<Proveedor>/, a partir de datos de producto/precio que el usuario pegue directo en el chat, o leyendo los portales web de los proveedores (Tectel, Sekunet, Intcomex, Syscom) con la sesión que abre la persona. Usar cuando el usuario agrega/actualiza un PDF de un proveedor, pega precios o specs de un producto para cargarlos, pregunta si el catálogo está al día, necesita agregar/actualizar precios de productos, o pide "actualizá los precios de los proveedores de la web", "de los portales", "de los proveedores con login", "traé los precios de Tectel / Sekunet / Intcomex / Syscom" o algo parecido.
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

### La otra carpeta de precios: `Precios Proveedores` (cargada el 2026-09-30)

En `COMERCIAL 2024 > PREVENTA 2026 > Precios Proveedores` hay una
subcarpeta por proveedor con dos tipos de documento, y cada uno se carga
distinto:

| Documento | Ejemplos | Va a | Tipo de precio cargado |
|---|---|---|---|
| **Lista de precios** del proveedor | Axis LATAM (en la subcarpeta de Intcomex), APC y Aruba (Solution Box), Control iD (Assa Abloy) | `Precio de lista` (col. 7) | `UN SOLO PRECIO EN LA LISTA` |
| **Cotización** del proveedor a Grupo Visión | Anixter, Epcom, Security Doctors, Seguritronic, ISTC, Sekunet, Ditesa, Iesa, Lamprosa, Salvavidas | `Precio dealer` (col. 11): es lo que el proveedor le cobra a GV | `COSTO DE UNA COTIZACION REAL` |

Reglas de la carga:

- **La fecha de la fila es la del precio** (la de la cotización o la de
  la lista), no la del día en que se cargó.
- **Lo que ya está en el catálogo no se vuelve a cargar**, aunque venga
  de otro proveedor: el código se compara normalizado (sin guiones ni
  espacios). Entre dos cotizaciones del mismo proveedor gana la más
  reciente.
- **Cotizaciones en colones** (Ditesa, Iesa, Lamprosa): se pasan a
  dólares con `TipoCambioVenta` y la Descripción dice el monto original
  y el tipo de cambio usado.
- **El `Archivo de origen` nunca lleva el nombre del cliente** de la
  cotización (los archivos de Anixter traen el proyecto en el nombre):
  se escribe "Cotización de <proveedor> a Grupo Visión del <fecha>".
- **Ningún dato de contacto, cuenta bancaria ni horario** puede quedar
  en un nombre o descripción: los pies de página de las cotizaciones los
  traen y un renglón de más los arrastra. Se revisa al final de la carga.
- **Antes de cargar las cotizaciones de un proveedor, comparar sus
  precios entre sí.** Una cotización de Anixter (enero 2025) repetía en
  el mismo orden los precios de otra anterior al mismo cliente, pero con
  otros productos: un transformador salía al precio de un comunicador.
  Se descartó entera. La señal: tres o más precios seguidos idénticos a
  los de otra cotización, con códigos distintos.

Cómo leer cada formato (los PDF no traen tablas limpias):

- **Anixter:** la descripción va centrada en el renglón del producto,
  parte arriba y parte abajo; los renglones entre dos productos se
  reparten por la mitad. La marca es la columna Fabricante, o sea la
  *última* marca antes del precio ("Dell Monitor ... DELL"). Algunas
  descripciones vienen con las letras separadas y no se pueden leer: esos
  nombres se escriben a mano a partir del mismo texto. En DSC para
  Latinoamérica la "N" final del modelo viene aparte (`HS2TCHP N`), igual
  que en el catálogo (`HS2LCD N`).
- **Security Doctors:** cada producto es un bloque que termina en un
  renglón `SKU:SD-<modelo>-INT-00`. El SKU que está entre un precio y el
  siguiente es del producto de ese precio.
- **Seguritronic:** la columna del código es angosta y sigue en los
  renglones de abajo, un pedazo por renglón (`RBH-INT-` / `UNC100-` /
  `122S`).
- **ISTC:** la descripción sigue abajo en mayúsculas; en los productos
  nuevos viene toda después del renglón del precio.
- **Epcom:** el texto trae letras encimadas ("Z W ALL MOUNTED",
  "SURVEILdLANCE"); se limpian solo en textos en mayúsculas.
- **Lista de Axis:** se cargan los productos vigentes, sin descontinuados,
  repuestos ni servicios. Trae Axis y 2N: la marca sale del nombre.

Los scripts de esa carga (lector de PDF y escritura por COM) no están en
el repo: llevan rutas y nombres de archivos de clientes. Lo que se
aprendió está en esta sección y en `docs/pruebas-validacion.md`.

### Portales de proveedor con sesión (probado 2026-10-19)

Decisión de Fabián (2026-10-19): la lista de precios periódica de cada
proveedor se levanta de su portal. Se activa con pedidos como
*"actualizá los precios de los proveedores de la web"*, *"de los
portales"*, *"de los proveedores con login"* o *"traé los precios de
Tectel"*.

**La sesión hace falta en los cuatro.** Sin ella no hay precio o hay uno
que no es el de GV (medido el 2026-10-19):

| Portal | Sin sesión | Con la sesión de GV |
|---|---|---|
| Tectel `tectelcr.com` | "Debe estar registrado para ver los precios" (la API deja ver uno, pero es 7-49% más caro) | precio de GV y de lista, sin IVA (`+iva`) |
| Sekunet `sekunet.com` | "Inicie sesión para ver precios" | precio de GV `$ … + IVA` y existencias por sucursal |
| Intcomex `myservices.intcomex.com` | el precio viene vacío | precio de GV y existencias en Costa Rica |
| Syscom `syscom.mx` | "Acceder a mi cuenta" | lista, especial y precio de GV, `+ IVA` |

La prueba de que es el precio correcto: en las 18 filas que ya estaban en
el catálogo, el precio con sesión coincide con el que teníamos (varias al
centavo).

**Pasos:**

1. **Abrir solo los portales que se pidieron** (Fabián, 2026-10-19), en
   el navegador integrado, una pestaña por proveedor:

   | Si la persona dice… | Se abre |
   |---|---|
   | "cargame todas las de web", "actualizá los proveedores con login" | los cuatro |
   | "recargá el catálogo de Tectel" | solo Tectel |
   | "traé Sekunet y Syscom" | esos dos |

   Si no queda claro cuáles, se pregunta. Las direcciones:
   `tectelcr.com/mi-cuenta`, `sekunet.com/web/login`,
   `myservices.intcomex.com/es/XCR/store`, `syscom.mx`. **La persona
   inicia sesión**; el asistente nunca escribe usuarios ni contraseñas,
   ni los guarda en ningún lado. Después se carga solo lo de esos
   portales: `preparar_portales.py` lee todos los `*_productos.json` de la
   carpeta, así que en ella van solo los de esta vez.
2. **Extraer** con [`scripts/portales/extraer.js`](scripts/portales/extraer.js):
   se pega en cada pestaña y se llama `gvTectel()`, `gvSekunet()`,
   `gvIntcomex()` o `gvSyscom()`. Usa la misma consulta que usa la página
   y corre en segundo plano (avance en `window.__job`; Sekunet tarda
   unos minutos). Así no se gasta un token por producto.
3. **Bajar el archivo**: al terminar aparece un botón rojo *"GV: bajar
   datos"*, y **un clic real** en él baja `<portal>_productos.json`. El
   navegador no deja descargar sin un clic (`a.click()` desde el script
   no hace nada, y el portapapeles tampoco se deja escribir). En la PC de
   Fabián las descargas van al **Escritorio**: se mueven a una carpeta de
   trabajo.
4. **Preparar**: `python -I scripts/preparar_portales.py "<catálogo>"
   "<carpeta con los json>" "<carga.json>"`. Solo lee. Por cada producto:
   si el proveedor ya tiene ese código en el catálogo, es una
   actualización; si no, una fila nueva. Clasifica con `taxonomia.py`, con
   la sección del portal como respaldo, y omite lo que queda fuera de las
   16 categorías (teléfonos IP, NAS, focos inteligentes…), lo obsoleto,
   lo repetido y lo que no trae código o precio. Marca los saltos de
   precio de más de +50% o menos de -40%.
5. **Probar sobre una copia**: copiar el catálogo a una carpeta temporal,
   correr `scripts/cargar_portales.ps1 -Ruta <copia> -Datos <carga.json>
   -Guardar`, y pasarle `python scripts/verificar-catalogo.py <copia>`.
6. **Mostrar el resumen** (nuevas por proveedor y categoría, las
   actualizaciones con precio viejo y nuevo, los saltos) y **esperar el
   OK**.
7. **Cargar el real** con `cargar_portales.ps1` (primero sin `-Guardar`,
   después con `-Guardar`). El script comprueba que OneDrive esté
   corriendo y el archivo sincronizado, saca respaldo, apaga el
   Autoguardado, no toca una fila que cambió desde que se preparó, y no
   guarda si algo no cuadra. Después espera a que OneDrive lo suba.
8. **Verificar** con `verificar-catalogo.py` y regenerar la pestaña de
   compatibilidad solo si `generar_matriz_accesorios.py` da otro número de
   pares.

**Cómo queda cada fila:**

- El precio de GV va a `Precio dealer` (col. 11), siempre **sin IVA**.
  Si el portal muestra también la lista (Tectel, Syscom), va a la col. 7
  y el tipo es `LISTA Y DEALER`; si muestra solo el de GV (Sekunet,
  Intcomex), la col. 7 queda vacía y el tipo es `PRECIO DEL PORTAL DEL
  PROVEEDOR`.
- La fecha es la de la consulta. El `Archivo de origen` dice *"Portal de
  <proveedor> (<dominio>) con la sesión de GV, consultado el <fecha>"*.
- **Las existencias de ese día van al final de la Descripción**, para que
  `buscar-equipo` no ofrezca lo agotado (R21).
- Syscom es México: se le compra afuera (`IMPORTADO = "si"`).

**Alcance de la carga del 2026-10-19:** Tectel y Sekunet completos;
Intcomex solo Seguridad, Redes, UPS, Almacenamiento y Monitores (el resto
es cómputo, oficina y gaming); Syscom solo búsquedas de productos
pequeños (R21), porque su catálogo tiene decenas de miles de productos.
Intcomex Costa Rica **no vende Axis en su tienda**: la lista de Axis del
catálogo viene aparte y no se actualiza desde el portal.

⚠️ Al extraer, **no se copia nada de la cuenta**: las páginas traen datos
de la cuenta de GV (vendedor asignado, correos, identificadores). Los
scripts solo toman campos de producto.

## Columnas del catálogo (26, orden fijo por prioridad — actualizado 2026-09-28)

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
| 4 | Categoría | **Una de las 16 categorías canónicas** — ver R11 en `docs/reglas-negocio.md`. Tiene lista desplegable. No escribir aquí el texto crudo del proveedor: ese va en la columna 27 |
| 5 | Subcategoría | El detalle dentro de la categoría (ej. Cámara → PTZ). Ver R11 |
| 6 | Proveedor | Tal como aparece en la pestaña `Proveedores`: es la llave con la que se busca su descuento |
| 7 | Precio de lista del proveedor (USD) | **Dato.** El precio que trae la lista del proveedor, tal cual (en Hanwha e InVid es el MSRP). **Nunca se reemplaza por el precio con descuento.** Dejar vacío si el documento no da precio en dólares |
| 8 | Precio de lista del proveedor (CRC) | **Fórmula**, no se escribe a mano (ver "Tipo de cambio y precios") |
| 9 | Precio de compra GV (USD) | **Fórmula: no se escribe.** Lo que Grupo Visión le **paga** al proveedor, y lo que va al `Costo Unit` de la matriz; el cliente nunca lo ve. Es el Precio dealer (col. 11) si la fila lo tiene; si no, el precio de lista menos el Descuento del proveedor (col. 12). Medido el 2026-09-24 sobre 1.119 matrices: 94 de 134 líneas comparables usan el dealer y cero el MSRP |
| 10 | Precio de compra GV (CRC) | **Fórmula**, igual que la columna 8 |
| 11 | Precio dealer (USD) | **Dato.** El precio para distribuidores, cuando la lista del proveedor lo trae aparte (InVid), o el costo de una cotización real. Si está, manda sobre el descuento. Agregada el 2026-09-28: estos precios estaban antes en la columna 9 |
| 12 | Descuento del proveedor | **Fórmula**: lo busca en la pestaña `Descuentos por proveedor`. Muestra el porcentaje (`0%`, `30%`), `PENDIENTE` si el proveedor está anotado pero falta confirmarlo, o vacío si el proveedor no está en esa pestaña. Agregada el 2026-09-28 |
| 13 | Unidad de venta | `Unidad` en la mayoría de los casos; usar `Metro`, `Rollo`, `Caja`, etc. cuando el producto se venda por medida (ej. cable) en vez de por unidad |
| 14 | Tiempo de entrega (días) | Lead time del proveedor si lo indica. Útil para saber si un equipo se puede prometer a tiempo en una cotización |
| 15 | País de origen | Relevante para licitaciones que piden certificación de origen del fabricante (ej. tipo NDAA). Dejar vacío si el documento no lo indica |
| 16 | Descripción | Texto libre, tal como lo da el documento fuente. Si el documento trae una nota aparte (cambio de precio, aviso de reemplazo, "solo bajo pedido", etc.), agregarla al final de este mismo campo como `-- Nota del proveedor: <texto>` en vez de crear una columna nueva o perder el dato |
| 17 | Especificaciones técnicas clave | Lo necesario para comparar contra un pliego de condiciones (resolución, protección IP, certificaciones, etc.), si se puede extraer como algo distinto de la Descripción general |
| 18 | Fecha de última actualización | Fecha en la que se cargó/actualizó esta fila (no la fecha del documento si son distintas — aclarar cuál es cuál si hay duda). Se guarda como **fecha real de Excel** con formato `yyyy-mm-dd`, nunca como texto: así se puede ordenar y filtrar (ver "Los tipos de dato importan" abajo) |
| 19 | Vigencia del precio | Si el documento indica una validez (ej. "15 días") |
| 20 | Peso | Dejar vacío si el documento no lo indica |
| 21 | Dimensiones (H×W×D) | Dejar vacío si el documento no lo indica |
| 22 | Código HTS | Código arancelario, si el documento lo trae. Uso de logística/aduanas, no de preventa — dejar vacío si no aplica |
| 23 | Código ECCN | Clasificación de control de exportación, si el documento lo trae. Dejar vacío si no aplica |
| 24 | Código EAN | Código de barras, si el documento lo trae. Dejar vacío si no aplica |
| 25 | Archivo de origen | Nombre del documento dentro de `Catalogos Proveedor/<Proveedor>/` que sustenta esta fila. Si el dato vino pegado directo en el chat (sin documento), anotar algo como "Dato dado por <asesor> en chat, DD/MM/AAAA" en vez de dejarlo vacío — la trazabilidad importa igual |
| 26 | Pestaña / Hoja de origen | Si la fuente es un Excel: nombre exacto de la pestaña de donde vino esta fila (ej. "HVA Pricelist"), para poder rastrear el dato si algo se pierde o se ve raro. Vacío si el origen fue un PDF o un dato pegado en el chat (no aplica) |
| 27 | Categoría original del proveedor | El texto de categoría tal cual venía en el documento fuente, antes de normalizar (agregada 2026-09-18). Sirve para auditar una clasificación que se vea rara y para volver a normalizar si cambian las reglas |
| 28 | Tipo de precio cargado | Qué trae la fuente de esta fila (agregada 2026-09-24, simplificada 2026-09-28). Cinco valores: `LISTA Y DEALER` (los dos precios; el dealer va en la col. 11), `UN SOLO PRECIO EN LA LISTA`, `SOLO PRECIO PUBLICO (MSRP)` (la lista trae solo el precio público: Hanwha), `COSTO DE UNA COTIZACION REAL` (el costo que se usó en una cotización real, en la col. 11, con la fecha de esa cotización) y `PRECIO DEL PORTAL DEL PROVEEDOR` (el precio que ve la cuenta de GV en el portal, en la col. 11, con la fecha de la consulta; agregado el 2026-10-19). Si un precio único ya es el de compra o le falta un descuento **no se dice acá**: lo dice la pestaña `Descuentos por proveedor`. **Al cargar un proveedor nuevo hay que llenarla** |

### Dónde va el precio de un proveedor nuevo (R15)

Cada proveedor publica sus precios como quiere: uno trae tres niveles,
otro dos, **la mayoría trae uno solo**. La cotización necesita **un**
número: el costo. Así que el catálogo se ordena alrededor de eso, no
alrededor de cómo publica cada proveedor.

**El `Precio de compra GV` (col. 9) no se carga: se calcula solo.** Al
cargar solo se escriben datos, cada uno en su columna, y **nunca se
reemplaza un precio por el precio con descuento**:

| Si el proveedor publica… | Qué se carga | Tipo (col. 28) |
|---|---|---|
| tres niveles (dealer / intermedio / lista) | el de **dealer** a `Precio dealer` (col. 11), el de lista a `Precio de lista` (col. 7). **El intermedio no se carga**: no se usa para cotizar y solo agrega ruido | `LISTA Y DEALER` |
| dos niveles | el más bajo al que podemos comprar de verdad a `Precio dealer`, el otro a `Precio de lista` | `LISTA Y DEALER` |
| un solo precio | a `Precio de lista` | `UN SOLO PRECIO EN LA LISTA` |
| solo el precio público (MSRP), y el proveedor nos hace un descuento sobre él | el MSRP a `Precio de lista` | `SOLO PRECIO PUBLICO (MSRP)` |

Cuando la lista no trae dealer, **el descuento va en la pestaña
`Descuentos por proveedor`**, no en el catálogo. Una fila por
descuento: proveedor, y si hace falta marca y categoría (gana la fila más
específica). Al escribir el porcentaje ahí, todo el catálogo de ese
proveedor se recalcula. Ejemplos de hoy:

- **Hanwha:** su lista trae el MSRP y una casilla para que cada
  distribuidor reste su descuento. Desde el 2026-09-28 lleva los
  descuentos medidos en las cotizaciones reales, uno general y uno por
  tipo de equipo, con estado `MEDIDO` (decisión de Fabián: aplicarlos
  tal cual lo medido; desde el 2026-10-12 no esperan confirmación).
  **Desde el 2026-10-21 (preventa): por defecto 50% sobre el MSRP**, *"por ley para Hanwha"*; lo medido (58% en cámaras) queda como la opción que se le pregunta al asesor. Ver `buscar-equipo`, "Hanwha: 50% sobre el MSRP por defecto". Desde el 2026-10-22 la pestaña `Descuentos por proveedor` tiene **50% en las cinco filas de Hanwha**, estado `CONFIRMADO POR PREVENTA` (lo medido sigue en su columna), y el catálogo muestra el costo con 50% en los 1.381 productos Hanwha. Se cambió con `cambiar_descuento.ps1`.
- **ISTC, Seguritronic y Security Doctors:** `0%`, porque su precio de lista ya es
  el de compra (medido en las cotizaciones reales, mediana 1,00).
- **Axis por Anixter:** medido en una cotización de 2024. Todavía no hay
  productos Axis cargados; la fila se aplica cuando se cargue su lista, y
  hay que revisar que el proveedor de la fila sea el mismo que el de esas
  filas del catálogo.

⚠️ **Descuento es lo que se RESTA, no lo que se paga.** Si el proveedor
nos cobra el 40% de la lista, el descuento es **60%**. Ya pasó una vez
(2026-09-28: se cargaron los "se paga" de Hanwha como descuento, y el
precio de compra quedó más alto que el real). Por eso la pestaña tiene
al lado una columna calculada, `Se paga (% de la lista)`: si ahí sale un
número grande donde se esperaba un descuento grande, está al revés.

**Un proveedor nuevo con un solo precio y sin fila en esa pestaña** queda
con el descuento vacío: se cotiza con su precio tal cual y la cotización
avisa que no se sabe si ya trae descuento. Para resolverlo **se mide**,
sin preguntarle a nadie: `python scripts/medir-descuento-por-proveedor.py`
compara el precio cargado con el costo que se usó en las cotizaciones
reales. Cerca de 1,00 = su precio ya es el de compra: se anota `0%`.
Bastante menos de 1,00 = falta un descuento: se anota como `PENDIENTE`
con lo medido, y lo confirma preventa.

**La regla en una línea:** se carga lo que dice la lista, tal cual; el
precio de compra lo calcula el catálogo con el dealer o con el descuento
del proveedor.

⚠️ **Nunca inventes un descuento.** Si el documento no dice si su
precio ya es el de compra, se carga como precio de lista y se sigue: la
pestaña de descuentos y la cotización se encargan de avisarlo. Adivinar
mal hacia un lado infla la cotización al doble; hacia el otro la deja
sin margen.

**Otras monedas:** el catálogo es en **dólares** y punto (R16). Si la
lista del proveedor viene en euros o en cualquier otra moneda, el asesor
la convierte antes y se cargan dólares. No se guarda una tasa de cambio
de otra moneda en ningún lado: envejece sola y nadie se entera.

**Grupos de columnas (para saber dónde insertar una columna nueva)**:
identidad y clasificación (1-6, lo primero que ve un asesor) → precios
(7-12) → condiciones de venta (13-15) → texto descriptivo (16-17) →
metadata de la fila (18-19) → logística/aduanas (20-24, dejar vacío si
el documento no lo trae, nunca inventar ni preguntar por cada campo
faltante) → trazabilidad de origen (25-28, siempre al final).

⚠️ **Insertar una columna corre a todas las de su derecha**, y hay
scripts que leen por posición (`scripts/verificar-catalogo.py`,
`medir-*.py`, `casos-patron-linea-base.py`). Después de insertar,
actualizá sus constantes y corré el verificador. Así se hizo el
2026-09-28 al agregar las columnas 11 y 12.

## Las pestañas `Descuentos por proveedor` y `Proveedores` (2026-09-28)

**`Descuentos por proveedor`** es de donde el catálogo saca el descuento
de cada fila sin precio dealer. Columnas: Proveedor, Marca, Categoria,
Descuento, Se paga (% de la lista, calculada), Estado, De dónde sale,
Medido en cotizaciones reales, Fecha, Notas, y dos técnicas (Clave y
Valor) que usa la fórmula. Reglas:

- **Para cambiar el descuento de un proveedor** (todas sus filas, o de una marca): `scripts/cambiar_descuento.ps1 -Ruta <catálogo> -Datos <json> [-Guardar]`. Saca respaldo, no corre sin OneDrive sincronizado, y no guarda si cambió el precio de compra de otro proveedor o si alguna fila no quedó en lista × (1 − descuento). Se usó el 2026-10-22 para dejar Hanwha en 50%.
- El **Descuento vacío** no se aplica: el catálogo muestra `PENDIENTE` y
  usa el precio de lista tal cual.
- Si escriben `30` en vez de `30%`, se entiende como 30% (el mismo
  criterio que el impuesto en el machote).
- **Estado:** `CONFIRMADO POR PREVENTA`, `MEDIDO`, `PENDIENTE` o
  `NO APLICA`. `MEDIDO` (antes `MEDIDO: FALTA CONFIRMAR`) se aplica tal
  cual, sin esperar confirmación (Fabián, 2026-10-12); la cotización
  solo avisa lo `PENDIENTE` o lo que no tiene fila.
- Es una tabla de Excel: una fila nueva hereda sola las fórmulas técnicas.

**`Proveedores`** dice a quién se le compra, qué vende, si se le compra
afuera (lo que va en `IMPORTADO`, R1), dónde está y dónde están sus
precios; y cuenta con una fórmula cuántos productos suyos hay cargados.
Salió de la base de datos de proveedores de COMERCIAL 2024, de la Lista
de precios General (su columna "Precio Nacional") y, para los seis que
no estaban en la base, de internet. Trae también **vendedor, teléfono y
correo** (pedido de Fabián, 2026-09-28), copiados de la base de
proveedores; los de EPA, Security Doctors y Salvavidas salieron de su
web o de sus cotizaciones. **Las notas de la base no se copian**: una
traía el usuario y la contraseña de un portal. Si un contacto cambia, se
actualiza acá. Al cargar un proveedor nuevo, agregale su fila acá
también.

⚠️ **La base de proveedores es de SOLO LECTURA** (decisión de Fabián,
2026-10-06). Es `COMERCIAL 2024 > PREVENTA 2026 > Base datos de
proveedores > BD Proveedores - Clientes.xltm`, la agenda de proveedores
y clientes que lleva preventa: se consulta o se toma de referencia,
**nunca se escribe**, ni para agregar ni para corregir. Si un dato de
ahí está mal, se corrige en el catálogo y se le avisa a preventa.

⚠️ Estos contactos son datos de personas: viven en el catálogo y en la
base, que son internos, y **nunca se copian a ningún archivo del repo**.

**`Guia de skills`** (en el catálogo desde el 2026-10-19; antes viajaba
en cada matriz): qué hace cada skill y un ejemplo de cómo pedírselo a la
IA. Es texto fijo, con su renglón en el `LEEME`. **Si se agrega un skill
o cambia cómo se pide algo, se actualiza acá** (por Excel, con las mismas
precauciones de cualquier escritura en el catálogo).

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

- **Precio de lista (CRC)** (columna 8, `H`) y **Precio de compra GV (CRC)** (columna 10, `J`;
  antes se llamaba "Precio especial GV (CRC)") son fórmulas, no valores
  escritos a mano:
  `=IF(G2="","",IF(TipoCambioVenta="","Actualizar TC",ROUND(G2*TipoCambioVenta,2)))`
  para la columna `H`, y la misma apuntando a `I` para la `J`. Usan el
  tipo de cambio de **venta** para convertir el precio en dólares a
  colones. ⚠️ Estas referencias cambiaron el 2026-09-21 al insertarse la
  columna `Subcategoria`: antes eran `F` e `H`.
  Si `B4` todavía no tiene un valor cargado, la celda muestra
  "Actualizar TC" en vez de 0, para que no se lea como un precio real.

  ⚠️ **Nunca borres filas del catálogo con `openpyxl`.** No reajusta
  estas fórmulas: una que decía `G500` en la fila 500 se mueve a la 499
  y sigue diciendo `G500`. El 2026-09-24 se encontraron **2.534 filas**
  mostrando el precio en colones de otro producto por esta causa. No
  falla ni avisa: muestra un número creible y equivocado. Borrá filas
  con Excel por COM, que sí las reajusta, y cerrá con
  `python scripts/verificar-catalogo.py`, cuyo chequeo 6 compara cada
  fórmula contra la fila en la que está.
- **El `Precio de compra GV` (col. 9, `I`) también es fórmula**, desde el
  2026-09-28:
  `=IF(ISNUMBER($K2),$K2,IF(ISNUMBER($G2),IF(N($L2)=0,$G2,ROUND($G2*(1-N($L2)),2)),""))`.
  O sea: el dealer si lo hay; si no, el de lista menos el descuento; y si
  el descuento es 0, `PENDIENTE` o vacío, el de lista exacto, sin redondear.
  El **Descuento del proveedor** (col. 12, `L`) es otra fórmula, que busca
  en `TablaDescuentos` la fila más específica: proveedor + marca +
  categoría, después proveedor + marca, después solo proveedor.
- **Al agregar una fila nueva**: escribí solo los datos en dólares —
  columna 7 (`G`, precio de lista) y, si la lista lo trae, columna 11
  (`K`, precio dealer)—, según "Dónde va el precio de un proveedor
  nuevo". **No escribas nada en las columnas 8, 9, 10 ni 12**: son
  fórmulas. Si la fila queda dentro de `TablaCatalogo`, Excel las copia
  solo; si no, copiá la fórmula de la fila anterior hacia abajo (mismo
  patrón relativo) en vez de tipear una nueva.
- **Si el documento fuente solo da el precio en colones** (no en
  dólares): calculá el equivalente en USD como
  `precio en colones del documento / TipoCambioVenta` y escribí ese
  resultado como valor literal en la columna en dólares que corresponda
  (7 u 11) — la fórmula en colones recalculará y debería coincidir (con
  un margen mínimo de redondeo) con el valor original del documento.
  Nunca escribas un valor literal directamente en las columnas 8, 9, 10
  ni 12; el verificador (chequeo 6) avisa si alguien lo hizo.
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
- Congelados (`FreezePanes`) el encabezado (fila 1) y las columnas
  Nombre, Marca y Modelo (`A` a `C`), para que se vean al hacer scroll.
  Categoría y Subcategoría **no** van congeladas (decisión de Fabián,
  2026-09-28): ocupaban media pantalla.
- Los precios llevan su signo, para que se sepa de un vistazo en qué
  moneda están: columnas 7, 9 y 11 en dólares (`[$$-409]#,##0.00`),
  columnas 8 y 10 en colones (`"₡"#,##0.00`), columna 12 en porcentaje.
  El formato va puesto sobre la columna entera de la tabla, así las filas
  nuevas lo heredan. Hasta el 2026-09-28 estaban en formato General y un
  precio se veía como `1234`; ahora se ve `$1 234,00`, con los
  separadores de la PC.

  ⚠️ **Dos trampas al poner un formato por COM desde PowerShell**, las
  dos vistas el 2026-09-28. (1) PowerShell le habla a Excel en el idioma
  de Windows (es-CR), y Excel lee `$#,##0.00` con la coma como
  *decimal*: guarda `$#.##0\.00` y un precio de 1234 se ve `$1234,0.00`. El
  formato se pasa en inglés con
  `[System.__ComObject].InvokeMember("NumberFormat", SetProperty, $null, $rango, @($formato), [CultureInfo]"en-US")`.
  (2) En inglés, un `$` suelto —o entre comillas— significa "la moneda
  del país" y en una PC de Costa Rica sale en **colones**. Para dólares
  va `[$$-409]`, el dólar de EE. UU., que se ve igual en cualquier PC.

  ⚠️ **El Autoguardado de OneDrive guarda solo, aunque el script no
  llame a `Save()`** (visto el 2026-09-30). El catálogo vive en OneDrive y
  Excel le prende el Autoguardado: una "prueba" que no guardaba quedó
  guardada **a medias**, porque falló a la mitad y lo que alcanzó a
  escribir ya se había grabado (hasta una fila con la categoría nueva y la
  subcategoría vieja). Por eso todo script que escriba en el catálogo:
  (1) **apaga el Autoguardado apenas abre el archivo**
  (`InvokeMember("AutoSaveOn", SetProperty, ..., @($false))`, y si no
  queda apagado, no sigue); (2) **saca el respaldo siempre**, también en
  prueba; (3) antes de escribir una celda comprueba que tenga el valor
  que espera, así una segunda corrida no pisa nada; y (4) después de la
  prueba se confirma que la fecha de modificación del archivo no cambió.

  ⚠️ **Guardar en esta PC no es guardar en la nube** (visto el
  2026-10-06). Un ajuste del 09-30 se guardó acá, OneDrive no lo subió,
  alguien abrió el catálogo en Excel Online —que trabaja sobre la copia
  de la nube— y cuando OneDrive volvió a sincronizar, la versión de la
  nube reemplazó a la local sin avisar. Por eso, (5) **antes de escribir**
  se confirma que OneDrive esté corriendo (`Get-Process OneDrive`) y que
  el archivo esté sincronizado; y **después de guardar** se espera a que
  termine de subirlo antes de dar el trabajo por hecho. El estado se lee
  con `Shell.Application`:
  `Namespace(carpeta).ParseName(archivo).ExtendedProperty("System.StorageProviderState")`
  da `2` cuando está sincronizado y `4` mientras falta subirlo (tarda
  unos segundos).

  **Si a los dos minutos sigue en `4`** (visto el 2026-10-12: 26 minutos
  trabado), el guardado quedó en la caché de Office esperando, casi
  siempre porque alguien tiene el catálogo abierto en la nube. **No
  reiniciar OneDrive**: el 2026-10-06 eso hizo que la versión de la nube
  pisara la local. Lo que lo destraba es lo que haría una persona: abrir
  el catálogo en Excel (también sirve por COM) y cerrarlo sin guardar;
  Office termina la subida y el estado pasa a `2`. Y antes de escribir
  otra vez, esperar a que esté en `2`.
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
   con las fórmulas de las columnas 8, 9, 10 y 12 copiadas de la fila anterior, no un valor
   a mano — ver "Tipo de cambio y precios" y "Formato y presentación"
   arriba para el detalle de cómo escribir cada columna.
6. **Mostrá un checklist final**: cuántas filas se agregaron, cuántas
   se actualizaron, y si algo quedó sin poder procesar (y por qué).

## Pestaña "Compatibilidad de Accesorios" (agregado 2026-09-01)

Después de cargar o reemplazar un catálogo de proveedor grande (ej. un
pricelist completo nuevo), refrescá también la pestaña
**`Compatibilidad de Accesorios`**. La consume
[`buscar-equipo`](../buscar-equipo/SKILL.md) para saber qué bases,
soportes, lentes y cubiertas sirven para cada equipo. Son dos pasos:

```
python scripts/generar_matriz_accesorios.py "<catalogo.xlsx>" "<pares.json>"
powershell -File scripts/escribir_matriz_accesorios.ps1 -Ruta "<catalogo.xlsx>" -Datos "<pares.json>"            (prueba)
powershell -File scripts/escribir_matriz_accesorios.ps1 -Ruta "<catalogo.xlsx>" -Datos "<pares.json>" -Guardar
```

El primero solo lee y calcula los pares: **solo entra lo que el
fabricante documenta**, y cada par lleva en `Notas` la frase que lo
respalda. El segundo los escribe por Excel (COM), reemplazando solo las
filas de la tabla y la sección de la `Guia de columnas`. Desde el
2026-10-12 ya no se usa openpyxl para esto (borraba los desplegables).
El detalle, y lo que se sacó y por qué, está en `buscar-equipo/SKILL.md`,
sección "Cómo se construye la pestaña Compatibilidad de Accesorios". No
es un paso bloqueante: si no se regenera, `buscar-equipo` no va a poder
sugerir accesorios para los productos más nuevos hasta que se corra.

## Estado real de la columna "Precio especial GV" (corregido 2026-09-18)

> **Hoy esa columna se llama `Precio de compra GV (USD)`** (el 2026-09-24
> pasó a llamarse `COSTO USD (precio Dealer)`, y el 2026-09-28 tomó su
> nombre actual; R4 y R15). Esta sección es la historia de cómo se descubrió
> qué había cargado en ella; los nombres de abajo son los de entonces.

⚠️ **Corrección a lo que decía antes este archivo.** Esta sección
afirmaba que la columna 8 estaba vacía "porque ningún documento cargado
trae ese dato". **Eso es falso** — verificado sobre el catálogo de
producción (2.552 filas):

| Origen | Filas | Precio especial |
|---|---|---|
| Distribuidor con PDF de 3 niveles de precio | 948 | **Cargado** |
| Fabricante con pricelist de un solo precio | 1.410 | Vacío |
| Proveedores locales varios | ~194 | Vacío |

**De dónde salió ese dato:** el PDF de ese distribuidor publica en su
encabezado **tres** columnas de precio — `Dealer Program`, `DEAL` y
`MSRP`. La extracción mapeó `MSRP` → "Precio USD" y `Dealer Program` →
"Precio especial GV". **La columna intermedia (`DEAL`) no se cargó**;
sigue en el PDF y se puede re-extraer cuando se sepa cuál nivel aplica.

**Nunca se aplicó una "regla del 50%".** 681 de esas filas dan
exactamente la mitad porque ese es el descuento de distribuidor que el
proveedor publica en su propia lista; 202 vienen iguales al precio de
lista; el resto da otros ratios. Y la marca donde el 50% *sí* aplicaría
según preventa es justamente la que **no tiene ningún precio especial**,
porque su pricelist oficial solo trae MSRP.

**Corregido el 2026-09-18:** 3 filas tenían el precio especial en `0`
(artefacto de extracción: en el PDF esas filas solo traen dos valores y
la tercera columna viene vacía). Un costo en `0` produce una línea
gratis sin ningún error visible. Se dejaron en blanco para que caigan al
precio de lista. Ver la regla R4 en
[`../../../docs/reglas-negocio.md`](../../../docs/reglas-negocio.md).

**Verificación adicional que sí salió limpia:** el pricelist del
fabricante tiene una pestaña `EOL Product` con 57 SKU descontinuados.
Se comprobó que **ninguno** se coló al catálogo. Al cargar una versión
nueva de ese pricelist, repetir el chequeo: cotizar un producto
descontinuado es un error caro y silencioso. Esa misma pestaña trae el
**reemplazo recomendado** de cada SKU — útil si alguna vez el cliente
pide un modelo viejo por nombre.

## ~~Pendiente: reglas de descuento GV por proveedor/proyecto (agregado 2026-09-14)~~

> **Cerrado.** No hay tabla de descuentos y no la va a haber (R4): el costo
> sale de la columna `Precio de compra GV`. La pestaña `Reglas de Descuento`, que
> nunca se llenó, se eliminó del catálogo el 2026-09-28. Lo que sigue es
> la historia.

La columna 8 también sirve para un caso puntual distinto: un proveedor
que da por escrito un precio negociado fijo. Ese caso todavía no se ha
cargado para ningún proveedor.

Es un caso **distinto** al que viene: según la compañera de preventa,
cada proveedor (y posiblemente cada tipo de proyecto) tiene **reglas de
descuento** (porcentajes) que determinan el costo real para Grupo
Visión — pueden ser varias reglas por proveedor. Fabián todavía no tiene
las reglas reales (se las van a pasar). Diseño acordado para cuando
lleguen:

- Las reglas en sí (qué proveedor, qué % o condición, según qué varíe)
  van en una **pestaña nueva de este mismo Excel** — es dato de
  referencia/configuración, igual que `Tipo de Cambio`.
- El **cálculo del precio con descuento aplicado no se guarda en el
  catálogo** — se calcula en el momento de cotizar (en `buscar-equipo`/
  `armar-cotizacion`), y el resultado va directo al "Costo Unit" de la
  pestaña `Equipos` de esa cotización puntual, nunca como un valor fijo
  reescrito en `Catalogo de productos por proveedor.xlsx`. Razón: el
  descuento aplicable depende del proyecto, no es una propiedad fija del
  producto.

No diseñar la estructura de la pestaña de reglas todavía — depende de
qué varíe realmente (¿solo proveedor? ¿proveedor + tipo de proyecto?
¿por volumen/cantidad?) y eso lo define el contenido real de las reglas
cuando lleguen, no hay que adivinarlo antes.

## Materiales de instalación (confirmado 2026-09-14)

Materiales genéricos de instalación (cable UTP, conectores, breakers,
tubería conduit, sensores/paneles de detección de incendio, etc.) **van
en el mismo `Catalogo de productos por proveedor.xlsx`, mismas 23
columnas, mismo proceso** — no hace falta una pestaña aparte. Usá la
columna "Categoría / tipo" para distinguirlos (ej. "Material eléctrico",
"Detección de incendio", en vez de "Cámara"). Validado contra un
ejemplo real de lista de precios de materiales (proveedor Sekunet,
~190 SKU, detección de incendio) — encaja sin cambios en el esquema
actual (Proveedor, Código SKU → Modelo/SKU, Artículo → Nombre, Precio $
→ Precio USD, unidad "UN" → Unidad de venta). La columna "Precio
Nacional" (SI/NO) de ese archivo **es el dato de importación**
(confirmado 2026-09-14) — mapea directo a nuestras columnas "País de
origen"/"IMPORTADO": `"SI"` → se puede tratar como producto nacional (no
importado, `IMPORTADO = "no"`); `"NO"` → es importado
(`IMPORTADO = "si"`). Igual que con cualquier fila, si el archivo no
trae el país de origen puntual, dejar "País de origen" vacío está bien —
lo que sí hay que completar siempre es el `IMPORTADO` de la fila
correspondiente en la matriz cuando se use, a partir de esta columna.

(Distinto de la pestaña `MATERIALES` que ya existe dentro del
**machote de matriz** — esa es la sección de cálculo de costo/margen
para materiales dentro de una cotización puntual, no un catálogo de
referencia. Ver `armar-cotizacion/SKILL.md`.)

**Estado 2026-09-18:** ya hay ~194 filas de materiales y equipos de
proveedores locales cargadas (control de acceso, material eléctrico,
detección de incendio, switches, cerraduras, fuentes), aproximadamente
de la fila 2.360 en adelante del catálogo de producción.

**Decisión: un solo catálogo, no varios** (regla R11 de
[`../../../docs/reglas-negocio.md`](../../../docs/reglas-negocio.md)).
Se evaluó separar cámaras y monturas de tubería y materiales en archivos
distintos y se descartó: la regla de no duplicados y la fórmula de
precio en colones son las mismas para todo, una cotización real mezcla
las tres capas, y un archivo más es un lugar más donde buscar. Se
distinguen por `Categoría / tipo`.

**`Categoría` y `Subcategoría` ya están normalizadas (vigente desde
2026-09-21).** Pasó de 80 valores heredados de los encabezados de
sección de cada PDF a **16 categorías y 64 subcategorías, sin ninguna
fila sin clasificar**, así que ahora **sí** se puede filtrar con
confianza. El texto original del proveedor se conservó en la columna 25,
`Categoria original del proveedor`. Ver el detalle, el método y los
errores a no repetir en la regla R11 de
[`../../../docs/reglas-negocio.md`](../../../docs/reglas-negocio.md).

**Al cargar un catálogo de proveedor nuevo hay que volver a
normalizar**, porque las filas nuevas entran con la categoría cruda del
documento de origen:

Las reglas viven en `scripts/taxonomia.py`. **Corré siempre una
simulación primero** y revisá el reparto y la lista de `Sin clasificar`
antes de aplicar; hacé respaldo antes de escribir.

- Si el proveedor nuevo trae **categorías limpias**, agregalas al
  diccionario `CONFIABLES`.
- Si trae **encabezados de sección**, agregá palabras clave a `ANTES` o
  `DESPUES` — y acordate de que se matchea contra el **nombre** del
  producto, **nunca contra la descripción**.
- Si la sección acierta la categoría pero los nombres vienen crípticos,
  usá `SECCION_FIJA`: la sección fija la categoría y las palabras clave
  resuelven solo la subcategoría.

⚠️ **Dos trampas de Excel al tocar este archivo por script:** una
validación de lista escrita en línea tiene un límite de **255
caracteres** (las 16 categorías dan 277 → Excel rechaza el archivo sin
avisar; hay que usar un rango, por eso existe la hoja oculta
`_listas`). Y `insert_cols` amplía el rango de la tabla pero **no**
declara la columna dentro de ella: hay que borrar y recrear el
`ListObject`, o Excel da el archivo por dañado.

**Lo que falta para poder cotizar instalación** no es catálogo, son las
**proporciones de consumo**: cuántos metros de tubo, cuántas gazas y
cuánto cable lleva cada cámara instalada. Sin eso hay materiales pero no
hay cálculo. Diseño acordado: una pestaña `Proporciones de Instalación`
en este mismo Excel (mismo criterio que `Tipo de Cambio`). Ver R10.

## Verificar el catálogo después de cada carga (obligatorio)

```
python scripts/verificar-catalogo.py
```

**Corrélo después de cada carga de proveedor y después de cualquier
edición manual.** Solo lee; nunca escribe. Devuelve 0 si está sano.

Existe por H-11: 29 de las 40 filas de una subcategoría no pertenecían
ahí, y pasó semanas sin que nadie lo notara. Una fila mal
subcategorizada **no desaparece** —sigue en el catálogo— pero
`buscar-equipo` filtra por categoría y subcategoría, así que deja de
aparecer en las búsquedas. El producto se vuelve invisible sin que nada
falle.

Revisa siete cosas:

1. Que la categoría exista en la taxonomía.
2. **Que la subcategoría pertenezca a esa categoría.** Es el chequeo que
   importa: un desplegable plano deja poner `Montaje` en una fila de
   cámara, y eso se ve válido pero sigue estando mal.
3. Qué diría el clasificador hoy. Una diferencia no es error —puede ser
   una corrección manual a propósito— pero una diferencia grande avisa
   que `taxonomia.py` quedó viejo.
4. Campos vacíos que impiden cotizar esa fila. Ojo: un SKU vacío **no**
   es error en materiales genéricos ni en servicios; nadie le pone
   número de parte a "tubo metal 3/4". También cuenta, como aviso,
   cuántas filas se cotizan con el precio de lista porque su descuento
   está `PENDIENTE` o el proveedor no está en `Descuentos por proveedor`.
5. El mismo producto cargado dos veces por el mismo proveedor (SKU
   comparado sin guiones ni espacios). El mismo producto de dos
   proveedores distintos es normal: sirve para comparar.
6. **Que las fórmulas estén y miren su propia fila**: precios en
   colones, Precio de compra GV y Descuento del proveedor. Detecta el
   desfase que deja `openpyxl` al borrar filas y, desde el 2026-09-28,
   un número escrito encima de la fórmula del precio de compra.
7. Que el `Tipo de precio cargado` sea uno de los cinco valores y
   cuadre con el Precio dealer.

## Los tipos de dato importan, no solo los valores (corregido 2026-09-22)

Tres columnas guardaban números y fechas **como texto**. El valor se
veía bien y todo parecía normal, pero Excel no los puede ordenar,
filtrar ni sumar: al ordenar por precio, `'1000'` queda antes que
`'950'`.

| Columna | Estaban como texto | Consecuencia |
|---|---|---|
| `Precio USD` | **1.409 filas**, todas de un mismo proveedor | Es el 55% del catálogo. Ordenar por precio daba un orden equivocado |
| `Tiempo de entrega (dias)` | 1.091 filas | No se podía filtrar "entrega menor a 30 días" |
| `Fecha de ultima actualizacion` | las 2.550 | Es justo la columna que sirve para ver qué precios están viejos |

Ya están convertidos. **Al cargar un proveedor nuevo, escribí números
como números y fechas como fecha real** (`datetime.date` con formato de
celda `yyyy-mm-dd`), nunca como cadena.

No confundir con `Precio de lista (CRC)` y `Precio de compra GV (CRC)`: esas **sí**
son texto a veces, y está bien — son fórmulas que devuelven
`"Actualizar TC"` mientras la pestaña `Tipo de Cambio` esté vacía.

## Desplegables de Categoría y Subcategoría

Las dos columnas tienen validación de datos, o sea desplegable:

- `Categoria` → `=_listas!$A$2:$A$18` (16 categorías + "Sin clasificar")
- `Subcategoria` → `=_listas!$E$2:$E$72` (71 subcategorías)

⚠️ **La lista de subcategorías vive en `_listas` columna E, no en la C.**
La columna C tiene los mismos nombres pero **con el prefijo de
categoría** (`Camara > IP / de red`), que es un formato de lectura y
**no** coincide con lo que guarda la columna `Subcategoria` del catálogo
(`IP / de red`, pelado). Apuntar la validación a la C obligaría a
escribir un valor que no coincide con ninguna de las 2.550 filas
existentes.

Si agregás una subcategoría nueva: primero a `scripts/taxonomia.py`,
después regenerás `_listas!E` y ampliás el rango de la validación. Si se
hace al revés, `buscar-equipo` no la va a encontrar.

⚠️ **Guardar el catálogo con `openpyxl` borra los desplegables.** No
soporta la extensión x14 de la validación con rango en otra hoja y la
**elimina sin avisar** (comprobado el 2026-09-23 con el generador viejo
de la matriz de accesorios, que desde el 2026-10-12 ya escribe por COM).
Si algo llegara a guardar el catálogo con `openpyxl`, después hay que
correr:

```
powershell -File scripts/reparar-desplegables.ps1
```

**El desplegable es una comodidad, no la garantía.** Evita el error de
dedo, pero deja poner una subcategoría que existe y no corresponde a esa
categoría. Para eso está el paso 2 del verificador.

## Columnas que hoy salen mal o vacías (medido 2026-09-22)

Se contó celda por celda sobre las 2.550 filas del catálogo de
producción. Tres cosas que hay que corregir al próximo cargue:

**1. `Especificaciones tecnicas clave` está vacía en las 2.550 filas.**
La columna existe desde el diseño original y **nunca se llenó**. No es
un detalle cosmético: `buscar-equipo` mandaba explícitamente a comparar
las especificaciones contra esa columna, así que media instrucción
apuntaba al vacío (ya corregido ahí). Al cargar un proveedor, o se llena
con lo que traiga la ficha, o la columna se elimina — pero no puede
quedarse como está, prometiendo un dato que no existe.

**2. `Vigencia del precio` también está vacía en las 2.550.** Mismo
criterio.

**3. Las fechas y los precios como texto ya se corrigieron** — ver la
sección de tipos de dato más arriba.

**Cobertura del resto, por si sirve para priorizar:** `Precio especial
GV` 945 de 2.550 (solo InVidTech), `Tiempo de entrega` 1.103, `Pais de
origen` 1.122, `Peso` 992, `Dimensiones` 1.009, `Codigo HTS` 1.111,
`Codigo EAN` 1.409. `Categoria`, `Subcategoria`, `Proveedor`,
`Precio USD` y `Unidad de venta` están al 100%.

## Sobre quién mantiene esto al día

No hay una persona encargada — hoy preventa son 2 personas. La
responsabilidad de notar que algo está desactualizado recae en quien
usa [`buscar-equipo`](../buscar-equipo/SKILL.md): al traer un producto,
debe mirar "Fecha de última actualización" y **avisar siempre si tiene
más de 2 meses** (regla exacta, confirmada 2026-09-14) para decidir si
conviene confirmar el precio con el proveedor antes de cotizar, y si
vale la pena disparar una actualización de esa fila.

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
