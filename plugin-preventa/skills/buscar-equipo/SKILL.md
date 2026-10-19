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
   con su Marca/Modelo/Costo/Categoría (el costo sale como dice "El
   precio con que se arma la cotización", abajo) y explicá en una línea por qué
   cada uno cumple o no cumple del todo — dejá que el asesor elija, no
   elijas vos en su lugar.
4. Si **ninguno** cumple al 100%, decilo explícitamente y mostrá el más
   cercano con la brecha específica (ej. "el más cercano es IP66, se
   pide IP67") — nunca digas que algo cumple si no cumple.

   **Cuando el número pedido no existe, recomendá el inmediato superior,
   no uno holgado** (Fabián, 2026-10-15). Si piden una batería de 12 V
   9 Ah y el catálogo salta de 8 a 10 Ah, la recomendada es la de 10 Ah,
   no la de 12 Ah: más capacidad suele ser un equipo más grande, y una
   batería de reposición va dentro de un gabinete, un panel o una UPS
   donde puede no caber. Lo de abajo (menos capacidad, menos resolución)
   no cumple y solo se muestra como brecha. Si el cliente no dijo para
   qué es, preguntalo; si nadie sabe, igual va el inmediato superior.
5. **Si dos o más candidatos cumplen lo mismo, preguntá cuál usar, con
   la antigüedad del precio de cada uno a la vista** (Fabián,
   2026-10-15). La antigüedad suele decidir —un precio de un mes le gana
   a uno de un año y medio—, pero la elección es del asesor: puede
   preferir otra marca o un proveedor local. Recomendá el de precio más
   reciente y preguntá; no lo elijas en silencio.
6. **Si el producto exacto existe pero es importado, decilo y que elija
   el asesor: importado o del país** (Fabián, 2026-10-19, regla R22).
   Importado = se le compra a un proveedor de afuera (columna `¿Se le
   compra afuera?` de la pestaña `Proveedores`: Syscom, ISTC…). Mostrá
   los dos lados con lo que vería el cliente, porque el importado carga
   10% de transporte y 15% de DAI (R1) y tarda más en llegar:
   - **Si un proveedor del país tiene el mismo producto**, ponelos lado a
     lado y que elija.
   - **Si en el país no está el mismo**, recomendá los **similares** del
     país: el inmediato superior en la especificación (punto 4), de
     marcas que el equipo ya compra, con existencias si se saben. Buscá
     primero en el catálogo (Tectel, Sekunet, Intcomex y los demás
     locales) y, si es un producto pequeño, en tiendas de Costa Rica
     (R21).

   Nunca elijas vos entre importado y del país, aunque uno sea más
   barato: el plazo de entrega y la disponibilidad pesan, y eso lo sabe
   el asesor.
7. **Mostrá siempre cuántos días tiene el precio.** Calculá los días
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

### El precio con que se arma la cotización (R4 y R15)

El catálogo trae dos precios por producto, y **se pregunta una sola vez
por cotización con cuál se arma** (decisión de Fabián, 2026-09-28):

| Precio | Columna | Qué es |
|---|---|---|
| **Precio de compra GV** | 9 | lo que Grupo Visión paga: el precio dealer si la lista lo trae; si no, el de lista menos el descuento del proveedor. **Es el recomendado** |
| Precio de lista | 7 | el precio de la lista del proveedor, tal cual (en Hanwha e InVid, el MSRP) |

La columna 9 es una fórmula del catálogo; vos no calculás nada:

```
Precio de compra GV  =  Precio dealer (col. 11)                     si la fila lo tiene
                        Precio de lista (col. 7) × (1 − descuento)   si no
```

El descuento (col. 12) sale de la pestaña `Descuentos por proveedor`.

**Cuándo y cómo se pregunta.** Cuando ya está elegido el equipo, al
mostrar la tabla para confirmar: **una sola pregunta para toda la
cotización**, no una por línea, con los descuentos de esos productos a
la vista. Agrupalos por marca y tipo de equipo, con su estado:

> *"Para estos productos, los descuentos que tenemos son: Hanwha
> cámaras X% y grabadores Y% (medidos en cotizaciones, falta que
> preventa los confirme); ISTC 0%, su precio ya es el de compra; EPA sin
> descuento registrado. ¿Armamos con el precio con descuento de GV
> (recomendado) o con el precio de lista (MSRP)? Con el de lista, el
> precio al cliente sale alrededor de 1,85 veces el MSRP."*

- **Si no contesta o dice "lo normal":** precio con descuento de GV.
- **Si pide una mezcla** (por ejemplo "Hanwha con descuento, lo demás
  lista"): se hace así, y en la tabla se marca qué precio lleva cada
  línea.
- **Si pide precio de lista:** columna 7 en todas las líneas, y se dice
  que el margen real va a ser bastante mayor que el que muestra la
  matriz.

**Por qué el de compra y no el MSRP.** Se midieron 1.119 matrices y
57.607 líneas de equipo. De las 134 líneas comparables contra las dos
columnas: 94 coinciden con el dealer y **cero** con el MSRP. Las 35 que
no pegan con ninguno son todas *más baratas* que el MSRP.

El MSRP es donde el precio al cliente **aterriza** después de transporte,
DAI, administración y margen, no de donde arranca. Puesto en `Costo
Unit`, la cotización sale cerca del **doble**: el cliente ve alrededor
de 1,85 veces el MSRP.

⚠️ **Cotizar con el precio de compra no significa mostrárselo al
cliente.** El archivo de matriz son dos cosas a la vez:

| Pestaña | Qué es | ¿La ve el cliente? |
|---|---|---|
| `Equipos` | la matriz de **costo**, cuentas internas | **nunca** |
| `COTIZACIÓN ` | la oferta que se imprime y se manda | sí |

El precio de compra va en la primera. Lo que el cliente ve es el precio
de venta, que en las cotizaciones reales sale alrededor de **1,85×** ese
costo. En el caso patrón #3: costo $79 → el cliente vio $145,35.

### Cuánto creerle al precio de cada fila

Lo dicen las columnas 11 y 12 de la fila, y el estado del descuento en la
pestaña `Descuentos por proveedor`. Es lo que se muestra en la pregunta de
arriba:

| Si la fila tiene… | El precio de compra es… | Qué decirle al asesor |
|---|---|---|
| `Precio dealer` (col. 11) | el dealer | nada especial. Si el tipo (col. 28) dice `COSTO DE UNA COTIZACION REAL`, que es el costo de esa cotización: mostrá los días. Si dice `PRECIO DEL PORTAL DEL PROVEEDOR` o el origen es un portal, es el precio que ve la cuenta de GV, sin IVA; las existencias de ese día están al final de la Descripción, y lo agotado no se ofrece |
| un porcentaje, estado `CONFIRMADO POR PREVENTA` | lista menos ese descuento | nada especial |
| un porcentaje, estado `MEDIDO` | lista menos ese descuento | que el descuento sale de medir las cotizaciones reales, y en cuántas (columna `Medido en cotizaciones reales`). **No pidas confirmación**: lo medido se aplica tal cual (Fabián, 2026-10-12). Es el caso de Hanwha y Axis |
| `0%` | el precio de lista, que ya es el de compra | nada especial (ISTC, Seguritronic, Security Doctors) |
| `PENDIENTE` | **el precio de lista tal cual** | que el proveedor está anotado pero su descuento todavía no tiene número: el costo real es menor |
| vacío | el precio de lista tal cual | que ese proveedor no está en `Descuentos por proveedor`: no se sabe si su precio ya trae descuento |

**El descuento de Hanwha cambia según el proyecto**: con registro en el
portal de Wisenet es mayor que el anotado. Si el asesor dice que el
proyecto está registrado, preguntale si tiene el precio del proyecto.

**Nunca inventes ni ajustes un descuento por tu cuenta.** Solo vale lo
que está en la pestaña `Descuentos por proveedor`; el catálogo lo aplica
solo, y no se deduce al cotizar.

**Si el asesor te da un precio para una línea** —por ejemplo, porque el
proyecto está registrado y el proveedor mandó precios con descuento—,
**usá el suyo** y decí en cuáles líneas.

**Una cotización mezclada no es un error**, pero al mostrar la lista
marcá las líneas cuyo costo puede ser menor (descuento `PENDIENTE` o
proveedor sin fila), y por qué. Las de descuento `MEDIDO` no se marcan
como dudosas: se dice de dónde salió el número y nada más.

### Lo que había contestado preventa, que no coincide

El 2026-09-22 preventa contestó que el descuento *"varía dependiendo de
la marca, tipo de equipo y qué nivel de partners somos"* y que usan
**siempre los MSRP**, aplicando el descuento a mano. Y que cuando el
proyecto se registra *"el proveedor nos manda directamente los precios
ya con el descuento"*.

Lo medido no coincide. La explicación más probable es que describían el
**precio al cliente** —que sí aterriza cerca del MSRP— y se entendió como
la casilla de costo. Por eso se recomienda el precio con descuento, pero
se pregunta: si para una cotización quieren el precio de lista, es
decisión de ellos.

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
| `Accesorio de instalacion` | 414 | Montaje · Caja / housing · Adaptador / conversor · Otros accesorios · Cubierta / carcasa |
| `Software y licencias` | 129 | Suscripcion en la nube · Licencia VMS · Integracion / plugin |
| `Red y conectividad` | 97 | Switch · Extensor · Switch PoE · Fibra / transceiver · Firewall / router · Accesorio de red · Antena |
| `Energia` | 75 | Fuente de poder · Bateria · Inyector PoE · Sistema solar · UPS · Proteccion electrica |
| `Monitor y visualizacion` | 70 | Monitor · Monitor publico (PVM) · Senalizacion digital |
| `Materiales de instalacion` | 63 | Cableado · Canalizacion y tuberia · Material electrico · Ferreteria / postes |
| `Control de acceso` | 59 | Torniquete · Intercomunicador · Controladora · Lector / terminal · Credencial / tarjeta · Boton de salida · Cerradura / electroiman |
| `Optica` | 58 | Lente |
| `Audio` | 49 | Altavoz · Sistema de audio IP · Microfono |
| `Deteccion de incendio` | 42 | Notificacion · Detector · Accesorio · Panel |
| `Alarma e intrusion` | 22 | Accesorio de alarma · Comunicador · Sensor ambiental · Detector de movimiento · Panel de alarma · Contacto magnetico |
| `Almacenamiento` | 20 | Disco duro · Tarjeta de memoria |
| `Servicios` | 2 | Instalacion |
| `Equipo de computo` | 1 | Computadora / workstation |

**2. Buscá el texto en `Nombre de equipo/producto` (col. 1) y
`Descripcion` (col. 16).** Nada más. El script
[`scripts/buscar_catalogo.py`](scripts/buscar_catalogo.py) lo hace sin
gastar tokens: `python -I scripts/buscar_catalogo.py 12v 9ah --sub
bateria` devuelve una línea por candidato, con precio de compra, de
lista, días del precio y existencias del portal si las tiene.

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

### Cuando el cliente da el modelo: buscalo tolerante, no exacto

Los clientes y los proveedores escriben el mismo modelo de formas
distintas, y una búsqueda exacta los pierde. Pasó en dos casos patrón:

| Caso | El cliente escribió | El catálogo tiene | Por qué no apareció |
|---|---|---|---|
| #5 | `ED-SIGA-278` | `SIGA-278` | **prefijo de marca** (`ED-` es Edwards) |
| #3 | `PN3A-16X16FNH` | `PN3A-16X16FNH2` | **sufijo de variante** (el `2` es parte del modelo real) |

En el #5 el catálogo tenía el costo **exacto** que se usó ($80,69) y la
búsqueda no lo encontró. Así que, en este orden:

1. **Exacto, normalizado** — sin guiones, puntos ni espacios, en
   mayúsculas.
2. **Sin el prefijo de marca** — si empieza por `ED-`, probá sin él.
3. **Por prefijo** — el SKU del catálogo empieza con lo que escribió el
   cliente (`PN3A16X16FNH` → `PN3A16X16FNH2`).

⚠️ **Lo que encuentres en el paso 2 o 3 no es el mismo producto hasta que
se confirme.** Un sufijo puede ser una variante real y distinta
(`QNO-6012R` y `QNO-6012R1` son dos modelos, uno sin audio). Mostralo
como "probablemente es este", con las dos descripciones lado a lado, y
que el asesor decida.

### Productos pequeños: si el catálogo no alcanza, tiendas de Costa Rica (R21)

Pedido por preventa y decidido por Fabián el 2026-10-15. Baterías,
cerraduras, botones de salida y productos parecidos se cotizan seguido,
pero el catálogo tiene pocas filas de cada uno y muchos precios viejos.
Para esos:

1. **Primero el catálogo**, como siempre: candidatos con la antigüedad de
   cada precio.
2. **Si no hay ninguno que cumpla, o todos tienen el precio de más de 2
   meses (R12), buscá en internet, solo en tiendas y proveedores de
   Costa Rica**: negocios con dirección o teléfono en el país y precio
   en colones. Nunca Amazon, Mercado Libre ni tiendas de otro país,
   aunque salgan más baratas: el precio tiene que ser comprable acá.
3. **Mostrá 3 a 5 opciones en una tabla**: marca y modelo, tienda,
   precio publicado en colones, IVA, disponibilidad, el enlace y la
   fecha de consulta. Al lado, el equivalente en dólares con el tipo de
   cambio de esa cotización (R7) y lo que vería el cliente. Que elija
   quien cotiza; vos recomendás.
4. **Lo agotado no se muestra** (Fabián, 2026-10-19). Si la página dice
   agotado o no disponible, esa opción no entra en la tabla. "Por
   pedido" sí entra, dicho así; si la página no dice nada de
   existencias, también, con "no indica disponibilidad".
5. **El IVA, siempre explícito** (Fabián, 2026-10-19). En cada precio
   va una de dos: **"IVA incluido"**, si la página lo dice, o **"el IVA
   no está aplicado a este monto"**, si la página dice que no lo incluye
   o no dice nada. Nunca un precio sin esa aclaración.
6. **Qué recomendar.** Primero las marcas que el equipo ya compra (las
   que están en el catálogo), después marcas reconocidas con ficha
   técnica (para baterías: AGM/VRLA, certificación UL, medidas y
   terminal). Marcá las que no traen marca.
7. **Lo que no sabés, decilo.** Si el título y la ficha no coinciden
   (una batería "9 Ah" cuya ficha dice 900 mAh), mostralo así. Si el
   enlace redirige a otro dominio, no lo sigas: anotá esa tienda como
   no verificada.
8. Una compra en una tienda local va con `IMPORTADO = "no"` (R1). El
   precio de tienda es precio al público: un distribuidor puede dar uno
   mejor, y vale la pena avisarlo.
9. Si eligen una, ofrecé cargarla al catálogo con `actualizar-catalogo`,
   con la tienda y la fecha como fuente, para que la próxima vez esté.

Nunca comprás, ni llenás formularios, ni iniciás sesión en una tienda:
solo leés precios publicados. Los portales de proveedor con usuario y
contraseña (Intcomex, Syscom, Sekunet, Tectel) no entran en esta
búsqueda: ver "Portales de proveedor con login" en R21.

**A qué productos aplica** (medido sobre el catálogo el 2026-10-15; el
detalle está en R21 de [`docs/reglas-negocio.md`](../../../docs/reglas-negocio.md)):
baterías, fuentes de poder, protección eléctrica y UPS pequeñas;
cerraduras y electroimanes, botones de salida y tarjetas; contactos
magnéticos, sirenas y botones de pánico; **detección de incendio**
(detectores, bases, estaciones manuales, sirenas y estrobos, módulos);
accesorios de red, inyectores PoE y switches PoE pequeños; discos duros
y tarjetas de memoria; cable, tubería y material eléctrico; y gabinetes
pequeños, que no están en el catálogo.

⚠️ **Lo que tiene que ser compatible con un panel o una marca se busca
de esa marca y familia, y de ninguna otra.** Un detector direccionable
solo habla con los paneles de su fabricante; un detector inalámbrico de
alarma, solo con su panel. Para esos, en la tienda se busca el mismo
modelo o uno de la misma familia que el panel, nunca un "equivalente".

**A qué no aplica**: cámaras, grabadores, servidores, licencias,
controladoras e intercomunicadores. Tampoco cuando la licitación amarra
la marca. Eso se cotiza con el distribuidor.

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

**Hay dos clases de accesorio, y viven en dos pestañas distintas:**

| Pestaña | Pregunta que responde | Ejemplo |
|---|---|---|
| `Compatibilidad de Accesorios` | ¿qué montaje **sirve** para este modelo? | el mount de poste de una cámara |
| `Accesorios Requeridos` | ¿qué **hace falta** para que el sistema funcione? | la fuente de poder de un panel de incendio |

Los segundos son los que nadie pide porque se dan por sabidos. En el caso
patrón #5 el cliente pidió detectores y paneles, y la cotización traía
además **9 fuentes de poder** en las dos versiones.

**Con `Accesorios Requeridos` se sugiere, nunca se agrega solo.** Medido
sobre 666 cotizaciones, ninguno llega al 70%: el más alto es la batería
de respaldo con un panel de incendio (61%). Así que se muestra con su
número y se pregunta:

> *"Las cotizaciones con panel de incendio traen batería de respaldo en
> el 61% de los casos, base de detector en el 61% y módulo aislador en
> el 54%. ¿Agrego alguno?"*

Un accesorio inventado es peor que uno que falta y se pregunta.

⚠️ **Gabinetes y racks no están en el catálogo.** Son el acompañante más
común de las cámaras (41%) y de las controladoras (52%), y no hay ninguna
subcategoría donde buscarlos. Si hacen falta, decilo.

Si el asesor confirma que sí necesita accesorios de montaje:

1. **Buscá el modelo elegido** en la pestaña **`Compatibilidad de
   Accesorios`** del mismo `Catalogo de productos por proveedor.xlsx`
   (columna "Modelo Camara") — ver "Cómo se construye esta pestaña"
   abajo. Cada fila es un par cámara↔accesorio que el fabricante
   documenta (Modelo/Nombre/Marca del accesorio, tipo, proveedor,
   fuente), y en `Notas` trae la frase del fabricante que lo respalda.
   Si la fuente dice que el fabricante nombró solo la familia, avisalo
   al mostrarlo.
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

Tabla resumen simple: por cada línea, Marca | Modelo | Nombre | Costo
USD | Días del precio | Cantidad, con una sección separada para "Equipo
principal" y "Accesorios de instalación" (si el asesor los pidió).
Mostrá el precio de lista y el precio con descuento de GV de cada línea,
para que la pregunta de "El precio con que se arma la cotización" se
conteste mirando los dos. Marcá las líneas cuyo descuento no está
confirmado (ver "Cuánto creerle al precio de cada fila"). Aclarar
siempre qué quedó pendiente de confirmar (accesorio sin match, cantidad
no 1:1, candidato que no cumple al 100%, descuento sin confirmar).

## Cómo se construye la pestaña "Compatibilidad de Accesorios" (nota técnica)

Vive **dentro del mismo** `Catalogo de productos por proveedor.xlsx` (no
en un archivo aparte: el equipo ya sabe filtrar Excel). Una fila por par
equipo↔accesorio. Las columnas dicen "Camara" por historia; el equipo
también puede ser un intercomunicador, un monitor o un iluminador.
Columnas: Modelo Camara, Nombre Camara, Marca Camara, Modelo Accesorio,
Nombre Accesorio, Tipo Accesorio, Marca Accesorio, Proveedor, Fuente,
Notas.

**Regla de fondo (rehecha el 2026-10-12): un par solo entra si un
documento del fabricante lo dice.** Cada fila trae en `Notas` la frase
exacta que lo respalda (*"El descripcion de 02939-001 dice: '...smoked
dome for AXIS Q6124-E, Q6128-E...'"*), para que cualquiera pueda
revisarlo sin abrir la lista de precios. Si el asesor duda, mostrale esa
frase.

**Dos fuentes, columna `Fuente`:**

1. **`Fabricante: nombra el modelo exacto`** — casi todos. El nombre o
   la descripción del fabricante en su lista nombra el modelo: Hanwha,
   InVid y 2N por número de parte; **Axis por nombre de modelo**, porque
   su número de parte (`02939-001`) no aparece en los textos y el
   modelo sí (`AXIS Q6124-E`). El script expande las abreviaturas de
   Axis ("Q3626/8 VE" son Q3626-VE y Q3628-VE; "P1355/-E" son P1355 y
   P1355-E; "M4317/M4318-PLVE"), exige que coincida la versión Mk si el
   texto la dice, distingue "I7010-VE" de "I7010-VE Safety" (llevan
   placas distintas) y no ofrece una pieza que el fabricante dice que
   ya viene incluida en el equipo.
2. **`Fabricante: nombra la familia, no el modelo - verificar antes de
   cotizar`** — solo los casos de `FAMILIAS_VERIFICADAS`, revisados a
   mano contra el PDF de origen. Hoy: los soportes de pared y de esquina
   de InVid *"for Paramont PTZ Cameras"*, aplicados a las PTZ domo con
   zoom óptico (las mini PTZ 2.8-12 mm tienen su propio soporte, IPM-TXWM2,
   y la PTZ bullet es otro formato). Nunca se infiere una familia sola.

Qué lado del par es el accesorio lo decide la **Categoría del catálogo**,
no palabras sueltas del nombre: accesorio de instalación, lente, fuente,
inyector o cable de un lado; cámara, control de acceso, audio,
grabación, alarma, incendio o monitor del otro. Si los dos lados son
accesorios (una caja con su soporte de pared) el par no entra. Dos
excepciones medidas: una pieza que quedó con la categoría del equipo al
que acompaña ("White Cover for Video Intercom TID-600" está como
Intercomunicador) cuenta como accesorio por su nombre, y los
iluminadores IR cuentan como equipo.

**Lo que se sacó el 2026-10-12, y por qué (no reponer sin una razón
nueva):**

- **Los 10 pares "de cotización real"** (cámaras Paramont con soportes
  i-PRO y con la base de poste Hanwha SBD-180PMW). Al verificarlos
  contra la matriz de origen, esa cotización se armó **copiando la
  versión i-PRO del mismo proyecto y cambiando solo las cámaras**: los
  soportes quedaron debajo de las Paramont de arrastre, no porque
  sirvan. Ninguna ficha del fabricante los respalda. Lección: una
  cotización vieja no prueba compatibilidad; una ficha sí.
- **El emparejamiento automático "por categoría genérica"**. Con la
  lista de Axis cargada producía 832 pares por palabras sueltas como
  "dome" (un sensor emparejado con un soporte empotrado de otro
  modelo), y en InVid aplicaba a todas las PTZ un soporte de techo que
  el PDF dice que es para un solo modelo.
- **17 pares entre dos accesorios** que la versión anterior ponía uno
  como si fuera "la cámara".

**Cuándo y cómo regenerarla:** después de cada carga grande de
proveedor (si no, `buscar-equipo` va a decir "no tengo accesorio
documentado" para productos nuevos que sí lo tienen escrito). Son dos
pasos, en `../actualizar-catalogo/scripts/`:

```
python generar_matriz_accesorios.py "<catalogo.xlsx>" "<pares.json>"
powershell -File escribir_matriz_accesorios.ps1 -Ruta "<catalogo.xlsx>" -Datos "<pares.json>"
powershell -File escribir_matriz_accesorios.ps1 -Ruta "<catalogo.xlsx>" -Datos "<pares.json>" -Guardar
```

El primero solo lee el catálogo. El segundo escribe por Excel (COM),
nunca con openpyxl (que borra los desplegables): saca respaldo, apaga el
Autoguardado, no corre si OneDrive no está corriendo o el archivo no
está sincronizado, reemplaza solo las filas de la tabla y la sección de
la `Guia de columnas`, y no guarda si cambió algo fuera de esa pestaña.
Sin `-Guardar` es una prueba.

**Cobertura (2026-10-12, catálogo de 4.091 productos):** 1.247 pares,
445 equipos distintos. Por marca del equipo: Hanwha 832, Axis 350, 2N
39, Paramont 22, InVid 2, Vision 2. 1.235 nombran el modelo exacto y 12
la familia.

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
genérica y 10 pares de una cotización real (793 pares, 264 cámaras).
**Rehecha el 2026-10-12** con la regla de que solo entra lo que el
fabricante documenta: se sacaron el match por categoría y los pares de
cotización (ver "Lo que se sacó"), se agregaron Axis y 2N, y cada par
lleva su evidencia. Quedó en 1.247 pares y 445 equipos.

**Todavía no probado en una conversación real** con el equipo de
preventa (una búsqueda por especificación de punta a punta, con y sin
accesorios, un caso de cambio de marca, y el fallback de lista buscable
para marcas sin match exacto). Antes de llamar esto "Funcional", correr
al menos un caso real de cada uno con Fabián o el equipo de ventas.
