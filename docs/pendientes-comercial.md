# Lo que hace falta del equipo comercial

> Una sola lista, no una por persona. Katherine y Alessandro se reparten
> quién contesta qué; lo importante es que el paquete quede completo.
> Cada punto dice **por qué** se necesita y **qué pasa si no llega**, para
> que se pueda priorizar si no hay tiempo de contestar todo junto.
>
> Contexto: comprometido en la reunión del 2026-09-14 — una primera pasada
> para el 16/17 de setiembre y el resto la semana siguiente. Meta conjunta:
> **empezar a usar el plugin en octubre.**
>
> El detalle de cada regla está en [`reglas-negocio.md`](reglas-negocio.md).

---

## Bloqueante — sin esto el cálculo no sirve

### 1. Reglas de descuento por proveedor y marca `R4`

Por cada marca o distribuidor con el que se compra:

- ¿Qué descuento da sobre el precio de lista?
- ¿De qué depende? (registro del proyecto, monto mínimo de compra,
  familia de producto, tipo de cliente)
- ¿Aplica a todo el catálogo de esa marca o solo a parte?
- Si hay varios niveles de descuento, cuáles son y qué activa cada uno.

**Prioridad dentro de este punto:** la marca donde el descuento es del
50%. Esa es justamente la que **no tiene ningún precio especial cargado**
hoy, porque su lista de precios oficial solo publica el precio de lista.

**Si no llega:** toda cotización que arme la IA parte de un costo
inflado, el margen se calcula sobre un número equivocado y la oferta sale
cara. Es el único punto que bloquea absolutamente todo lo demás.

### 2. En qué nivel de precio compra Grupo Visión `R4.2`

La lista de precios de uno de los distribuidores publica **tres**
columnas de precio: `Dealer Program`, `DEAL` y `MSRP`. Entre la más baja
y la más alta puede haber más de 3× de diferencia.

**Pregunta concreta (afinada el 2026-09-22):** ya sabemos exactamente
qué nivel cargamos. De las 945 filas con precio especial, **669 son
exactamente el MSRP dividido entre dos** y 202 son **iguales al MSRP**
(todas ellas software, licencias y accesorios de una línea). Filas de
los dos tipos conviven en las mismas páginas del PDF, así que no es un
error de carga: el nivel *Dealer Program* es **MSRP − 50% en hardware y
0% en software**.

Entonces la pregunta ya no es "cuál de tres", es una sola:

> **¿Grupo Visión compra al nivel Dealer Program (o sea el MSRP menos
> 50%), o al nivel intermedio DEAL que no cargamos?**

**Si no llega:** hoy tenemos cargada la más baja y la más alta. Usar la
más baja cuando en realidad compramos en la intermedia significa cotizar
por debajo del costo y perder plata en los proyectos que se ganen. Es la
pregunta con el riesgo más caro de toda la lista.

### 2b. ¿El IVA de las compras locales es un costo o se acredita? `R2`

Rastreando las fórmulas del machote apareció esto: **el transporte y el
DAI solo se cobran si la línea dice `IMPORTADO = si`, pero el IVA de
línea se aplica siempre**, con el porcentaje que tenga la pestaña. En
`Equipos` ese porcentaje es 0% y en `MATERIALES` es 13%. O sea que el
IVA lo decide *en qué pestaña se escribió la línea*, no el producto.

**Pregunta concreta:** cuando Grupo Visión le compra a un proveedor
local y le cobran el 13% de IVA, ¿ese IVA **es un costo** del proyecto,
o **se acredita** contra el IVA que después se le cobra al cliente?

**Por qué importa ahora:** el catálogo ya tiene 193 productos de
proveedores locales (Seguritronic, ISTC, EPA, Tectel y otros). Si ese
IVA es un costo, una línea de proveedor local escrita en `Equipos`
—que tiene IVA 0%— sale con el costo **subvaluado en 13%**: sobre $100
por unidad, el costo nacionalizado pasaría de $103 a $116,39. Si se
acredita, está bien como está y no hay nada que cambiar.

**Si no llega:** no se toca nada. La automatización solo va a **avisar**
cuando una línea de proveedor local caiga en una pestaña con IVA 0%,
para que quien cotiza lo revise.

### 3. Clientes con régimen fiscal especial `R3`

Una lista de clientes con:

- ¿Se le cobra impuesto o es exento?
- Si se le cobra, ¿qué porcentaje? (se mencionó un caso de 2% en vez de 13%)
- ¿Se le carga el 3% de administración o no?

No hace falta que esté completa de una vez: con los clientes recurrentes
de gobierno alcanza para arrancar, y se van agregando.

**Si no llega:** se cobra impuesto de más o de menos en una licitación de
gobierno. Es un error visible para el cliente y difícil de explicar.

---

## Necesario para cotizar instalación completa

### 4. Tarifario de mano de obra `R8`

Los precios que no cambian entre proyectos:

- Instalación por cámara (se mencionaron 48 dólares)
- Instalación por poste
- Programación / configuración
- Capacitación
- Cualquier otro concepto que se cobre por unidad

**Nota:** los días, la cantidad de personas y la complejidad **no** entran
acá. Eso se sigue preguntando en cada proyecto porque depende del trabajo.

### 5. Tabla de destinos y kilometraje `R9`

- Lista de **destinos/localidades** habituales con kilómetros ida y
  vuelta (la tabla ya tiene San José, Cartago, Liberia, Paso Canoas y
  algunos más; se trata de completar los que falten).
- Costo por kilómetro vigente.
- Viáticos: alimentación y hospedaje por día y por persona.

Esta tabla ya existe en el machote con unos pocos destinos cargados; se
trata de completarla. **Solo los kilómetros**: cuántos viajes y cuántos
vehículos lleva cada proyecto se pregunta al cotizar, no va en la tabla.

> **Ya no hace falta pedir las proporciones de materiales.** Se había
> pedido "cuántos metros de tubo por cámara"; esa tabla se descartó
> (regla R10) porque la cantidad depende del sitio y guardarla como dato
> fijo le daría autoridad de verdad a una estimación. Se va a preguntar
> en cada cotización. **Un punto menos de la lista.**

---

## Reglas de cálculo

### 6. Porcentajes por etapa `R6`

Para cada uno de estos: transporte, imprevistos, administración y margen,
cuál es el valor típico en **estudio de mercado**, en **oferta de
licitación** y en **cliente privado**, y entre qué rango se mueve.

Lo que ya sabemos: transporte ya no es el 10% fijo (se consulta a
compras por proyecto y se han visto 2% y 6%); administración baja a 2% o
0% en licitaciones agresivas; el margen ronda 28% y sube a 30–35% en
estudio de mercado.

### 7. Tipo de cambio `R7`

- ¿Banco Central o Banco de Costa Rica?
- ¿Tipo de cambio de compra o de venta?
- El redondeo hacia arriba (por ejemplo de 480 a 500) ¿es política de la
  empresa o criterio de cada asesor?

### 8. Registro de proyecto `R5`

- ¿Con qué distribuidores se registra?
- ¿Cuánto dura el registro antes de vencer?
- ¿Dónde se anota hoy, si es que se anota en algún lado?
- ¿Se puede agregar una columna al control de cotizaciones para llevarlo?
  (esto necesita permiso de quien administra ese archivo)

> **Ya resuelto, no hace falta preguntarlo:** la antigüedad del precio
> quedó fijada en **2 meses** (regla R12). Pasado ese plazo hay que
> reconfirmar con el proveedor; debajo de él igual se muestran los días.

---

## Para poder validar que funciona

### 10. Dos o tres cotizaciones cerradas completas

De proyectos ya entregados, con:

- La especificación original que mandó el cliente
- La matriz final tal como quedó
- Qué porcentajes se usaron
- El monto total ofertado

**Idealmente:** una con financiamiento, una sin, y al menos una de más de
30 líneas.

**Para qué:** se reconstruye esa misma cotización con la IA sin mirar el
resultado, y se comparan los dos archivos celda por celda. Todo lo que no
coincida es una regla que falta. **Es lo único de toda esta lista que no
se puede reemplazar con criterio propio** — sin un caso real contra el
cual comparar, no hay forma de saber si la herramienta acierta.

---

## Catálogos y documentos

### 11. Lo que falte cargar

- PDFs o Excel de proveedores que todavía no estén cargados.
- La "lista de precios general" de la nube que se mencionó.
- Cualquier lista propia que alguien mantenga aparte.

No hace falta pasarlos a ningún formato: el PDF o el Excel tal como
llegó del proveedor sirve.

### 12. Dos confirmaciones sobre el machote

- Las pestañas de resumen traían datos de un proyecto anterior
  (cantidades, costos y un nombre de cliente). Se limpiaron. **¿Estaba
  bien limpiarlas, o se dejaban a propósito como ejemplo?**
- Cuatro pestañas de servicio tenían el margen roto. Se las dejó
  apuntando al mismo margen del proyecto que usa OPEX. **¿Es correcto,
  o esos servicios llevan un margen propio?**

### 12b. ¿El monto de los Excels de control va con IVA o sin IVA?

La columna del `Control de cotizaciones 2026.xlsx` se llama **`Monto sin
IVA`**, pero el `Cotizaciones en Preventa.xlsx` solo dice `Monto de
Oferta`. Cruzando los dos archivos por número de oferta, **19 de las 26
ofertas que están en ambos tienen el mismo monto**, y ninguna está en
relación 1,13 — o sea los dos guardan el mismo número.

**Pregunta concreta:** ¿ese número es el subtotal (antes del impuesto al
cliente) o el total? Si es el total, la columna está mal nombrada y
conviene renombrarla.

**Por qué importa:** es lo que se reporta hacia arriba. Si la mitad de
las filas trae subtotal y la otra mitad total, ningún acumulado de ese
archivo significa nada. Por ahora la automatización escribe el
**subtotal**, que es lo que dice el encabezado.

### 13. El prefijo del número de oferta

Qué determina que una oferta sea `T1`, `T4` o `T5`. Ya se preguntó una
vez y nadie lo supo; si sale de Bitrix, sirve saberlo.

---

# Mensaje para Teams

> Copiar y pegar. Está escrito para que se pueda contestar por partes y
> sin abrir ningún documento.

---

Hola 👋 Les comparto ordenado lo que necesito de su lado para terminar de
armar la automatización de cotizaciones. Lo dejé por orden de
importancia, así si no hay tiempo de todo, con los primeros tres ya
puedo avanzar bastante.

No hace falta que sea formal ni un documento bonito — un mensaje acá, un
TXT o un Excel a mano me sirve igual.

**Lo que me bloquea (si me pasan solo esto, ya arranco):**

1. **Descuentos por proveedor y marca.** Por cada marca: qué descuento
   nos dan, y de qué depende (registro del proyecto, monto mínimo,
   familia de producto). Katherine ya me comentó que el 50% de una marca
   no aplica a todas — es justo ese tipo de detalle el que necesito.
   Ojo con una cosa: revisé los archivos y de esa marca **no tenemos
   ningún precio con descuento cargado**, porque su lista oficial solo
   trae el precio de lista. O sea que ese 50% solo puede llegar de
   ustedes.

2. **¿En qué nivel de precio compramos?** La lista de uno de los
   distribuidores trae tres columnas de precio (Dealer Program, DEAL y
   MSRP). Ya revisé qué tenemos cargado: el precio especial que aparece
   en el catálogo es **exactamente el MSRP dividido entre dos** en todo
   el hardware, y el MSRP tal cual en software y licencias. O sea que lo
   que tenemos cargado es el nivel **Dealer Program**.

   Entonces la pregunta es una sola: **¿nosotros compramos a ese nivel
   (MSRP menos 50%), o al intermedio (DEAL) que no está cargado?** Si me
   equivoco, las cotizaciones salen por debajo del costo.

3. **Clientes exentos de impuesto.** Una lista de los clientes
   recurrentes diciendo si se les cobra impuesto, cuánto, y si se les
   carga el 3% de administración. Katherine me mencionó un caso de 2% en
   vez de 13% — ese tipo de excepciones.

**Lo que necesito para que calcule la instalación:**

4. **Tarifario de mano de obra:** lo que se cobra por instalación de
   cámara, de poste, programación, capacitación. Lo que no cambia entre
   proyectos. (Los días y la cantidad de personas no, eso lo sigo
   preguntando en cada cotización.)

5. **Destinos y kilometraje:** la lista de **localidades** con
   kilómetros ida y vuelta, el costo por kilómetro, y los viáticos por
   día y persona. Solo la distancia: cuántos viajes y cuántos carros
   lleva cada proyecto se los pregunto al cotizar.

   (Ojo: **ya no necesito las proporciones de materiales** que les había
   pedido — cuántos metros de tubo por cámara. Lo pensamos mejor y esa
   cantidad depende demasiado del sitio como para dejarla fija en una
   tabla, así que se las voy a preguntar en cada cotización.)

**Reglas de cálculo:**

6. **Porcentajes por etapa:** transporte, imprevistos, administración y
   margen — cuánto se usa en estudio de mercado, cuánto en licitación y
   cuánto en cliente privado.

7. **Tipo de cambio:** ¿Banco Central o Banco de Costa Rica? ¿Compra o
   venta? Y el redondeo hacia arriba, ¿es política de la empresa o
   criterio de cada quien?

8. **Registro de proyecto:** con qué distribuidores se registra, cuánto
   dura, y dónde lo anotan hoy. Katherine me comentó que sería útil
   llevar el control en algún lado — lo podemos armar, solo necesito
   saber cómo funciona hoy.

9. **Antigüedad del precio:** ¿a partir de cuántos días hay que
    reconfirmar un precio con el proveedor antes de cotizarlo?

10. **Una rapidita, Katherine:** en el control de cotizaciones, el monto
    que anotan, ¿es con IVA o sin IVA? Lo pregunto porque la columna se
    llama "Monto sin IVA" pero quería confirmarlo antes de que la
    automatización empiece a llenarla sola.

**Y lo más importante para saber si esto quedó bien hecho:**

11. **Dos o tres cotizaciones ya cerradas**, con la especificación
    original del cliente, la matriz final, los porcentajes que usaron y
    el monto total. Ideal si una lleva financiamiento y otra no, y al
    menos una de más de 30 líneas.

    La idea es armar esa misma cotización con la IA sin ver el
    resultado, y después compararlas celda por celda. Todo lo que no
    coincida es una regla que me falta. Sin un caso real contra el cual
    comparar, no tengo forma de demostrarles que la herramienta acierta.

**Dos cositas puntuales del machote:**

- Las pestañas de resumen traían datos de otro proyecto (cantidades,
  costos, un nombre de cliente) y las limpié, porque ese archivo se copia
  a la carpeta de cada cliente nuevo. ¿Estaba bien, o las dejaban a
  propósito como ejemplo?
- Cuatro pestañas de servicio (BodyCam, Face Pro, LPR, Cámara
  Antivandálica) tenían el margen roto con un error de Excel. Se lo dejé
  apuntando al mismo margen del proyecto. ¿Está bien así, o esos
  servicios llevan margen propio?

Y si tienen algún catálogo o lista de precios que todavía no me hayan
pasado, mándenmelo como esté — el PDF o el Excel tal cual les llegó me
sirve, no hay que pasarlo a ningún formato.

Gracias 🙌
