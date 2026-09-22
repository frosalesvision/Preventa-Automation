---
name: buscar-equipo
description: Busca marca y modelo específico de un equipo (cámara, control de acceso, alarma, etc.) que cumpla al 100% con una especificación técnica dada, usando el catálogo de proveedores de Grupo Visión CR (mantenido por `actualizar-catalogo`). Para cámaras y otros equipos que necesitan hardware de instalación, también identifica bases/soportes/lentes/accesorios compatibles y pregunta al asesor si quiere incluirlos. Usar cuando el usuario pide encontrar un equipo que cumpla ciertas especificaciones, pide ayuda para elegir marca/modelo para una licitación o cotización, pide armar el listado completo de equipo+accesorios para un proyecto, o necesita recalcular accesorios al cambiar de marca en un proyecto existente.
---

# Buscar equipo

Este skill **lee**, no mantiene, el catálogo de proveedores. La
carpeta/skill que lo escribe y lo mantiene al día es
[`actualizar-catalogo`](../actualizar-catalogo/SKILL.md) — el catálogo
vive en `CLIENTES/00_IA_PREVENTAS/Preventas/Catalogo/`. No tiene
sentido usar este skill si ese catálogo no tiene datos reales cargados.

## Por qué existe

Confirmado por preventa y por ventas (2026-08-26): el cuello de botella
más grande del proceso es, a partir de una especificación técnica dada
por el cliente/licitación, encontrar marca y modelo real que la cumpla
al 100% — hoy se hace "a pie" con ayuda de IA genérica, sin certeza.
Ver [`docs/notas-proceso.md`](../../../docs/notas-proceso.md) para el
contexto completo.

**Ampliación confirmada 2026-09-01:** la dificultad no termina al elegir
la cámara/equipo principal. Las bases, extensiones, housings y demás
hardware de instalación **varían de marca a marca** — en un proyecto
grande (ej. 400 cámaras) donde el cliente pide cotizar primero con una
marca y luego con otra, hay que rehacer también el listado de
accesorios de instalación para la marca nueva, no solo el de cámaras.
Esto se queda sin resolver hoy y genera trabajo manual repetido.

## Paso 1 — Encontrar el equipo principal por especificación

1. Pedile al asesor la especificación técnica (texto libre, pliego de
   licitación, o ya con marca/modelo conocido — ver "Formatos de
   entrada" abajo).
2. Buscá en `Catalogo de productos por proveedor.xlsx` (pestaña
   `Catalogo`) candidatos que cumplan la especificación, comparando
   contra "Especificaciones técnicas clave" y "Descripción". Esto es
   razonamiento semántico tuyo (no hay un motor de búsqueda exacto) —
   fijate en la especificación completa (resolución, protección IP,
   certificaciones tipo NDAA, rango de lente, etc.), no solo en
   palabras sueltas.
3. Si hay varios candidatos que cumplen razonablemente, mostrá todos
   con su Marca/Modelo/Precio/Categoría y explicá en una línea por qué
   cada uno cumple o no cumple del todo — dejá que el asesor elija, no
   elijas vos en su lugar.
4. Si **ninguno** cumple al 100%, decilo explícitamente y mostrá el más
   cercano con la brecha específica (ej. "el más cercano es IP66, se
   pide IP67") — nunca digas que algo cumple si no cumple.
5. **Mostrá siempre cuántos días tiene el precio.** Calculá los días
   desde la "Fecha de última actualización" del candidato y decilos
   **aunque el dato sea reciente** (regla R12, actualizada 2026-09-18) —
   es información para que el asesor decida si conviene reconfirmar con
   el proveedor antes de cotizar. Si pasa el umbral, avisalo
   explícitamente además del número. La responsabilidad de confirmar el
   precio vigente es de quien cotiza; vos solo informás.

   **El umbral es 2 meses** (cerrado por Fabián el 2026-09-22; ya se
   había confirmado el 2026-09-14 y una mención a "2 semanas" quedó
   descartada). Aun así **mostrá siempre los días exactos**, que es lo
   que de verdad le sirve al asesor para decidir.

   Esto aplica en cualquier punto donde se muestre un precio del
   catálogo, incluyendo `armar-cotizacion` al tomar el "Costo Unit".

**Sobre el "Costo Unit" que se usa (reescrito 2026-09-18 — ver la regla
R4 en [`docs/reglas-negocio.md`](../../../docs/reglas-negocio.md)):**

El precio del catálogo **es precio de lista, no el costo de Grupo
Visión**. Preventa lo confirmó: el costo real depende del registro del
proyecto, del monto mínimo de compra, de la marca y hasta de la familia
de producto, y **por ahora esa columna se llena a mano**.

Orden de precedencia, sin excepciones:

1. **Si hay una regla de descuento documentada** para ese proveedor y
   ese proyecto → calculá el costo con esa regla y decí cuál aplicaste.
2. **Si la fila del catálogo tiene un `Precio especial GV (USD)`** →
   mostralo, **pero aclarando de qué nivel de precio del proveedor
   salió** (ver abajo) y pidiendo confirmación antes de usarlo.
3. **Si no hay ninguna de las dos** → usá el "Precio USD" tal cual y
   **decí explícitamente que es precio de lista sin descuento.**

**Nunca inventes un porcentaje, nunca reuses el descuento de otra marca,
y nunca escribas un costo en la matriz que una persona no haya
confirmado.**

⚠️ **El catálogo tiene más de un nivel de precio y no sabemos cuál es el
nuestro** (hallazgo 2026-09-18, verificado contra el PDF del proveedor).
La lista de precios de uno de los distribuidores publica **tres**
columnas en su encabezado: `Dealer Program`, `DEAL` y `MSRP`. Nuestra
columna "Precio USD" es el **MSRP** y "Precio especial GV" es el
**Dealer Program**; la intermedia no se cargó. Entre la más baja y la
más alta puede haber más de 3× de diferencia, y **cuál aplica a Grupo
Visión nadie lo ha confirmado todavía**. Por eso, mientras no
respondan: **mostrale al asesor los niveles que existan para esa fila y
que él confirme cuál usar** — nunca elijas uno por tu cuenta. Elegir el
más bajo cuando el real es el intermedio produce cotizaciones que
pierden plata; elegir el MSRP produce cotizaciones no competitivas.

Nota de estado: la marca con más filas del catálogo **no tiene ningún
precio especial cargado** porque su lista oficial solo publica un precio;
el descuento que preventa menciona para esa marca tiene que llegar como
regla escrita del equipo. Ver R4.3.

### Cómo filtrar el catálogo (agregado 2026-09-22 — H-5, H-6, H-7)

Este skill se escribió **antes** de que el catálogo se normalizara, así
que decía "buscá candidatos" sin explicar por dónde. Con 2.550 filas eso
no alcanza. El orden que sí funciona:

**1. Filtrá primero por `Categoria` y `Subcategoria`.** Son las columnas
4 y 5, y solas bajan el universo de 2.550 a unos cientos. Hay **16
categorías y 64 subcategorías**, todas con valor en las 2.550 filas
(medido 2026-09-22). La pestaña `Glosario de categorias` del mismo
archivo las explica una por una. Cuidado con los singulares: la
categoría es **`Camara`**, no "Camaras".

| Categoría | Filas | Subcategorías |
|---|---|---|
| `Camara` | 888 | IP / de red · PTZ · Analogica · Termica · A prueba de explosion · Panoramica / fisheye · LPR / placas |
| `Grabacion y video` | 561 | NVR · Servidor / appliance · DVR / hibrido · Codificador / decodificador |
| `Accesorio de instalacion` | 407 | Montaje · Caja / housing · Adaptador / conversor · Otros accesorios · Cubierta / carcasa |
| `Software y licencias` | 129 | Suscripcion en la nube · Licencia VMS · Integracion / plugin |
| `Red y conectividad` | 97 | Switch · Extensor · Switch PoE · Fibra / transceiver · Firewall / router · Accesorio de red · Antena |
| `Energia` | 73 | Fuente de poder · Bateria · Inyector PoE · Sistema solar · UPS · Proteccion electrica |
| `Control de acceso` | 71 | Lector / terminal · Torniquete · Intercomunicador · Credencial / tarjeta · Boton de salida · Controladora · Cerradura / electroiman |
| `Monitor y visualizacion` | 70 | Monitor · Monitor publico (PVM) · Senalizacion digital |
| `Materiales de instalacion` | 63 | Cableado · Canalizacion y tuberia · Material electrico · Ferreteria / postes |
| `Optica` | 58 | Lente |
| `Audio` | 49 | Altavoz · Sistema de audio IP · Microfono |
| `Deteccion de incendio` | 42 | Notificacion · Detector · Accesorio · Panel |
| `Almacenamiento` | 20 | Disco duro · Tarjeta de memoria |
| `Alarma e intrusion` | 19 | Accesorio de alarma · Comunicador · Sensor ambiental · Detector de movimiento · Panel de alarma · Contacto magnetico |
| `Servicios` | 2 | Instalacion |
| `Equipo de computo` | 1 | Computadora / workstation |

**2. Buscá el texto en `Nombre de equipo/producto` (col. 1) y
`Descripcion` (col. 14).** Nada más.

⚠️ **No busques en `Especificaciones tecnicas clave`.** Una versión
anterior de este skill mandaba comparar contra esa columna: **está
vacía en las 2.550 filas** (medido 2026-09-22), igual que `Vigencia del
precio`. Existen como encabezado y nunca se llenaron.

**3. Contá los candidatos antes de mostrarlos.** Una especificación
normal deja muchos más de los que se pueden leer: "exterior, 4MP, con
IR" dio **68 candidatos** en la corrida del 2026-09-21.

- **Hasta 10 candidatos:** mostralos todos con su detalle, como dice el
  Paso 1.
- **Más de 10:** **no los listes.** Decí cuántos hay, agrupalos por
  marca con su rango de precio, y preguntá por dónde acotar —marca,
  techo de precio, tipo de lente (fijo o motorizado), formato (bullet,
  domo, turret)—. Una lista de 68 filas no es una respuesta, es
  devolverle el problema al asesor.

**4. Descartá los que contradicen el pedido, aunque el texto coincida.**
Un filtro por palabras clave produce falsos positivos reales, medidos en
la misma corrida:

- Una cámara **interior** entró en una búsqueda de exterior porque su
  descripción menciona IP66.
- Cámaras **multisensor** de 2MP × 2 entraron en una búsqueda de 4MP
  porque la suma da 4MP.
- Si piden fija, una **PTZ** no sirve aunque cumpla resolución e IR.

Leé el nombre completo antes de proponer una fila. El filtro acota; la
decisión de si sirve es tuya.

### Formatos de entrada que debés soportar

- Especificación técnica en texto libre o copiada de un pliego de
  licitación ("mínimo 4MP, IP67, certificación NDAA, lente varifocal
  2.8-12mm").
- Marca/modelo ya conocido por el cliente (raro, pero ocurre — ej.
  UCR) — en ese caso el "match" es directo, solo confirmá que existe en
  el catálogo y traé sus datos.
- Una lista de varios equipos de una vez (ej. todo el listado de un
  proyecto) — procesá uno por uno, mismo criterio.

## Paso 2 — Accesorios de instalación (agregado 2026-09-01)

Después de identificar el equipo principal (típicamente una cámara),
**preguntale siempre al asesor** si necesita también el hardware de
instalación (bases, soportes, housings, lentes, inyectores PoE, etc.)
o si esta cotización es solo de equipo/materia prima — **nunca asumas
ninguna de las dos** ni las incluyas sin confirmar. Muchos casos
legítimamente solo necesitan el equipo principal (ej. reposición de una
cámara sobre un mount que el cliente ya tiene instalado).

Si el asesor confirma que sí necesita accesorios:

1. **Buscá el modelo elegido** en la pestaña **`Compatibilidad de
   Accesorios`** del mismo `Catalogo de productos por proveedor.xlsx`
   (columna "Modelo Camara") — ver "Cómo se construye esta pestaña"
   abajo. Cada fila es un par cámara↔accesorio ya validado (Modelo/
   Nombre/Marca del accesorio, tipo, proveedor, fuente).
2. **Si el modelo no aparece en esa pestaña** (va a pasar seguido con
   InVid/Milesight/Paramont/Vision/Secure — ver limitación de cobertura
   abajo): **no digas simplemente "no hay match" y ahí lo dejes.**
   Mostrale al asesor una lista buscable de los accesorios disponibles
   de esa misma marca (filtrá la pestaña `Catalogo` por Marca +
   categoría/nombre con pinta de accesorio: mount, bracket, housing,
   lente, junction box, etc.) para que la revise y elija manualmente
   cuál aplica — dejá que te diga palabras clave para acotar la lista
   (ej. "buscá algo de pared para esta domo") en vez de mostrarle
   cientos de filas de una vez. Esto resuelve en la práctica casos
   donde el fabricante sí vende el accesorio pero lo describe a nivel
   de familia de producto en vez de por SKU exacto (ej. un accesorio de
   InVid llamado literalmente "Back Box for Milesight Vandal Dome" no
   queda capturado por el match automático porque no nombra un SKU
   exacto, pero aparece de inmediato si el asesor busca "vandal dome").
   Nunca inventes ni asumas un accesorio solo porque "debería tener
   uno" — mostrá candidatos reales del catálogo o decí que no hay
   ninguno.
3. **Si aparecen varias opciones del mismo tipo de necesidad** (ej.
   mount de pared, mount de poste, mount de techo, mount pendant, para
   la misma cámara) — es normal, cada uno sirve para un tipo de
   instalación física distinta. **Mostrá todas las opciones agrupadas
   por tipo y preguntale al asesor cuál aplica según el sitio** (pared,
   poste, cielorraso, empotrado, etc.) — nunca elijas uno por tu
   cuenta, no tenés información de la visita técnica.
4. **Cantidades:** por defecto asumí 1 accesorio de mount por cámara,
   pero **confirmá con el asesor** antes de multiplicar — hay casos
   (inyectores PoE, cajas de alimentación) que no son 1:1 (ej. un
   inyector puede alimentar más de una cámara). Si el tipo de accesorio
   no dice nada sobre esto, preguntá en vez de asumir.
5. **Armá el listado combinado** (equipo principal + accesorios
   elegidos, con cantidades) como resumen final — ver "Formato de
   salida" abajo.

### Caso: cambio de marca en un proyecto ya armado

Cuando el asesor pide recotizar un proyecto existente (lista de
cámaras + accesorios) con una marca distinta (ej. pasar de Hanwha a
InVid/Milesight para las mismas 400 cámaras):

1. Repetí el Paso 1 para cada línea de cámara, buscando el equivalente
   más cercano en la marca nueva que cumpla la misma especificación
   (no asumas que existe un "equivalente exacto" — mostrá el candidato
   más cercano y la diferencia si la hay).
2. Repetí el Paso 2 completo para cada cámara nueva — **los accesorios
   de la marca anterior casi nunca sirven con la marca nueva** (bases y
   housings son específicos de fabricante/modelo). No reutilices el
   accesorio viejo solo porque "es del mismo tipo".
3. Si la marca nueva no tiene compatibilidad documentada en el índice
   para ese modelo (más probable con InVid/Milesight — ver limitación
   de cobertura abajo), decilo explícitamente y sugerí confirmar el
   mount directamente con el proveedor antes de cotizar la mano de
   obra de instalación.

## Formato de salida

Tabla resumen simple: por cada línea, Marca | Modelo | Nombre | Precio
| Cantidad, con una sección separada para "Equipo principal" y
"Accesorios de instalación" (si el asesor los pidió). Aclarar siempre
qué quedó pendiente de confirmar (accesorio sin match, cantidad no
1:1, candidato que no cumple al 100%).

## Cómo se construye la pestaña "Compatibilidad de Accesorios" (nota técnica)

Vive **dentro del mismo** `Catalogo de productos por proveedor.xlsx`
(no un archivo aparte — se probó primero como `.json` independiente,
pero se decidió con el usuario moverlo a una pestaña más porque el
equipo ya sabe filtrar/editar Excel y no un JSON, y es más fácil de
auditar a ojo). Columnas: Modelo Camara, Nombre Camara, Marca Camara,
Modelo Accesorio, Nombre Accesorio, Tipo Accesorio, Marca Accesorio,
Proveedor, Fuente, Notas — una fila por cada par cámara↔accesorio (una
misma cámara puede aparecer en varias filas si tiene varios accesorios
compatibles, ej. distintos tipos de mount).

**Tres fuentes, distinguidas por la columna "Fuente" (cada una con su
propio nivel de confianza):**

1. **`Catalogo de proveedor (descripcion/nombre del fabricante)`** — la
   principal y más confiable. Sale de leer el propio campo Nombre/
   Descripción de las filas del catálogo de proveedores, donde el
   fabricante ya escribe la compatibilidad en texto libre (ej. *"Wall
   mount compatible with XNP-6120HW"*, *"Ceiling Mount for
   PAR-ALLDRXIRBD"*). Generada automáticamente por el script, se puede
   regenerar cuando haga falta.
2. **`Match por categoria generica (no por SKU exacto) - verificar
   antes de cotizar`** — cuando el accesorio nombra una marca +
   categoría reconocible pero no un SKU exacto (ej. "Corner Mount for
   Paramont PTZ Cameras"), se empareja con **todas** las cámaras reales
   de esa marca+categoría en nuestro propio catálogo (nunca con datos
   de internet — el catálogo ya trae "PTZ", "Vandal", "Dome", etc. en
   la descripción de cada cámara). Si la frase solo dice algo genérico
   sin categoría clara (ej. "Junction Box for Paramont Series
   Cameras"), se descarta en vez de matchear contra toda la marca —
   sería un alcance inventado. También generada por el script.
3. **`Cotizacion real (patron usado por el equipo, no documentado por
   el fabricante) - verificar antes de usar`** — pares confirmados a
   mano revisando cotizaciones reales (autorizado 2026-09-01, ver
   `docs/notas-proceso.md`). Estos **no se regeneran solos** corriendo
   el script — viven como una lista literal (`PARES_VERIFICADOS_
   MANUALMENTE`) dentro del mismo script, para agregar a mano cuando
   se encuentre un caso útil revisando otra cotización.

Script: [`../actualizar-catalogo/scripts/generar_matriz_accesorios.py`](../actualizar-catalogo/scripts/generar_matriz_accesorios.py).
Uso (escribe sobre el mismo archivo, agrega/reemplaza solo esa
pestaña):

```
python generar_matriz_accesorios.py "<Catalogo de productos por proveedor.xlsx>"
```

**Lógica de las fuentes 1 y 2**: escanea **todas** las filas del
catálogo (no solo las categorizadas como "accesorio" — se confirmó que
varias filas de Paramont/Vision quedaron categorizadas como
"CAMERAS..." por herencia del encabezado de sección del PDF de origen,
aun siendo mounts reales con la compatibilidad escrita en su propio
Nombre), buscando patrones como "compatible with", "for (...)", "for
the ...", "for X" suelto (mayúsculas o minúsculas), "supported cameras
(...)", "used with ...". Cada SKU mencionado se valida contra los SKU
reales del catálogo (para no confundir texto como "IP66" o "VESA" con
un modelo real), incluyendo un rescate para SKU que quedan enterrados
en texto descriptivo (ej. "Wall Mount for Paramont Series:
PAR-P4PTZXIR2812NH-AIWL"). Si ningún SKU exacto valida, se intenta la
fuente 2 (categoría genérica). Para decidir **cuál lado del par es la
cámara y cuál el accesorio**, se clasifica el Nombre de ambos lados
contra una lista de palabras típicas de accesorio (mount, bracket,
adapter, housing, lens, cap adapter, back box, junction box, plate,
power supply, etc. — con cuidado de no confundir "license plate" de
una cámara LPR con un accesorio tipo "plate"): si exactamente un lado
"suena a accesorio", ese va en las columnas de Accesorio y el otro en
las de Cámara; si **los dos** lados suenan a accesorio (ej. un cap
adapter que se acopla a otro adaptador base) o **ninguno** (dos equipos
principales relacionados, ej. un decoder y el servidor que lo usa), el
par se descarta — no hay forma confiable de decidir la dirección sin
inventar, mejor no escribir nada a escribir algo probablemente al
revés.

**Sobre la fuente 3 (cotizaciones reales) — qué se intentó y qué
funcionó, y qué no (2026-09-01)**: el usuario autorizó explícitamente
leer cotizaciones reales para este análisis (ver `docs/notas-proceso.md`,
sección de la matriz de Excel) y detectar por cuenta propia cuáles
tenían equipos InVid/Milesight — un escaneo ligero (solo nombres de
archivo + texto compartido del `.xlsx`, sin leer celda por celda) sobre
las ~287 carpetas de `CLIENTES` corrió dos veces (tardó ~10-40 min según
el momento) y encontró consistentemente 71 cotizaciones reales con
equipos de esta familia. Se probaron **dos estrategias de extracción**:

1. **Por estructura de hoja** (secciones "Cámaras"/"Accesorios" en
   celdas separadas): de las 15 cotizaciones más densas, **solo 1**
   (Municipalidad Alajuelita, proyecto "Ciudad Segura") tenía esa
   estructura parseable automáticamente — las otras 14 organizan sus
   hojas de forma distinta (consistente con `notas-proceso.md`: "cada
   quien lo hace distinto", no hay convención única).
2. **Por texto de línea, sin depender de estructura** (reusando la
   misma extracción "compatible with X"/"for X" del catálogo, aplicada
   directamente a la descripción de cada línea de las 71 cotizaciones):
   corrida completa sobre las 71, con un bug real encontrado y corregido
   en el camino (el patrón de "for X" cortaba la captura justo en el
   ":", perdiendo la lista de SKU en frases tipo "for Paramont Series
   Cameras: PAR-P3BIR, PAR-P4BIR..." — corregido, y de paso mejoró el
   match dentro del propio catálogo). Aun así, **no aparecieron pares
   nuevos más allá de los de Alajuelita**: se investigó un caso
   prometedor (Reina Dragón, con "Junction Box for Paramont Series
   Cameras: PAR-P3BIR, PAR-P4BIR, PAR-P8BIR...") y los SKU que menciona
   **no existen tal cual en nuestro catálogo actual** — son nombres
   cortos/abreviados del proveedor en una cotización más vieja, no los
   SKU completos que usamos hoy. No es un problema de la lógica de
   extracción, es un desajuste real de nomenclatura entre lo que
   escribió el proveedor en ese momento y el catálogo actual.

De la única cotización que sí funcionó (Alajuelita) salieron 10 pares
verificados, con dos hallazgos genuinamente útiles: (a) para la PTZ
`PAR-P8PTZXIR32NH-AI` y la bullet `PAR-P6BIRA2812-LC3`, el equipo usó
brackets **Panasonic i-PRO** (marca que ni siquiera está en nuestro
catálogo) porque Paramont no tenía mount propio — dato que no se
podría haber sacado de ningún catálogo de proveedor nuestro; (b)
también usaron el `SBD-180PMW` (pole mount de **Hanwha**) para estas
mismas cámaras Paramont, aunque la ficha oficial de ese mount **no**
lista modelos Paramont como compatibles — un caso real de
"funciona en la práctica aunque no está documentado", marcado con nota
de advertencia explícita para que se verifique el encaje físico antes
de repetirlo.

**Conclusión (no reabrir sin una razón nueva):** con dos intentos
completos (estructura de hoja, y texto de línea sin depender de
estructura) sobre las 71 cotizaciones disponibles, el rendimiento de
seguir mirando cotizaciones viejas es bajo — el cuello de botella real
ya no es la lógica de extracción, es que muchas usan nomenclatura de
SKU que quedó obsoleta. Si en el futuro Fabián tiene en mente un
proyecto puntual reciente que sepa que usó InVid/Milesight con
accesorios documentados, vale la pena revisarlo a mano — pero no seguir
invirtiendo en automatizar esto contra el histórico completo.

**Cuándo regenerar la pestaña:** cada vez que `actualizar-catalogo`
agregue o reemplace un catálogo de proveedor grande, volvé a correr el
script — refresca las fuentes 1 y 2 automáticamente y conserva los
pares de la fuente 3 (siempre que la cámara siga existiendo en el
catálogo). Si no se regenera, `buscar-equipo` va a decir "no tengo
accesorio documentado" para productos nuevos que en realidad sí lo
tienen escrito.

**Cobertura real (medida 2026-09-01, sobre el catálogo de 2,358
productos):** 793 pares cámara-accesorio, cubriendo 264 modelos de
cámara distintos — 749 por SKU exacto (fuente 1), 34 por categoría
genérica (fuente 2), 10 de cotización real verificada a mano (fuente
3). Por marca de cámara: Hanwha es ampliamente mayoritario; Paramont e
InVid tienen cobertura chica pero real; Milesight, Vision y Secure
siguen con cobertura mínima o nula por SKU exacto.

⚠️ **Por qué Milesight/Secure quedan casi sin cobertura por SKU exacto
(investigado 2026-09-01, no es un bug pendiente de arreglar)**: se
revisó a fondo por qué, incluyendo una búsqueda en internet de las
fichas oficiales de Milesight (que sí documentan brackets como A71/A72/
A81/A82 para sus líneas de mini/pro dome). El problema real no es falta
de información de compatibilidad — es que **el catálogo de proveedores
de InVidTech que tenemos cargado casi no incluye SKU de mounts/
brackets propios para esas marcas**: las cámaras Milesight en nuestro
catálogo o traen el hardware de montaje integrado (ej. "Integrated
Junction Box" en su propia descripción) o InVid los vende bajo un
nombre de familia genérico en vez de por SKU exacto (ej. existe
`INVID-A84 | BACK BOX FOR MILESIGHT VANDAL DOME` — es un accesorio real
y comprable, pero no menciona un modelo de cámara específico, y en este
caso tampoco hay ninguna cámara Milesight con "vandal" en su propia
descripción dentro de nuestro catálogo, así que ni el match por SKU ni
el de categoría genérica lo encuentran — no es que falte lógica, es que
ese modelo de cámara Milesight específico no está en nuestro price list
actual). Agregar los SKU "oficiales" de Milesight (A71, A72...) a esta
pestaña **no serviría** porque no son artículos que Grupo Visión pueda
comprar por esta vía. Por esto el "Paso 2" de arriba pide mostrar una
lista buscable en vez de forzar un match automático para estas marcas.

## Estado

Diseñado 2026-09-01 junto con la capa de accesorios de instalación
(antes era solo un placeholder), incluyendo dos vueltas de revisión de
calidad de los datos: (1) la primera versión (270 cámaras) tenía un bug
de direccionalidad (un accesorio que menciona a otro accesorio, o una
cámara modular que menciona su lente compatible, quedaban invertidos:
el accesorio aparecía como si fuera "la cámara") — corregido
clasificando ambos lados de cada par por nombre antes de decidir cuál
va en qué columna; (2) después se sumaron el match por categoría
genérica y los pares verificados de una cotización real (ver arriba),
subiendo la cobertura final a **793 pares, 264 cámaras**, con tres
niveles de confianza distinguidos por la columna "Fuente". Se investigó
a fondo ampliar la fuente 3 a más cotizaciones (dos estrategias
distintas sobre las 71 cotizaciones reales disponibles) sin encontrar
pares nuevos aprovechables — ver "Sobre la fuente 3" arriba para el
detalle de por qué, y no reabrir ese punto sin una razón nueva.

**Todavía no probado en una conversación real** con el equipo de
preventa (una búsqueda por especificación de punta a punta, con y sin
accesorios, un caso de cambio de marca, y el fallback de lista buscable
para marcas sin match exacto). Antes de llamar esto "Funcional", correr
al menos un caso real de cada uno con Fabián o el equipo de ventas.
