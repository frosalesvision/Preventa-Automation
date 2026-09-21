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

**Pregunta concreta:** ¿en cuál de los tres niveles compra Grupo Visión?
¿Depende del programa de distribuidor, del volumen, o del proyecto?

**Si no llega:** hoy cargamos la más baja y la más alta. Usar la más baja
cuando en realidad compramos en la intermedia significa cotizar por
debajo del costo y perder plata en los proyectos que se ganen. Es la
pregunta con el riesgo más caro de toda la lista.

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
   MSRP) y entre la más baja y la más alta hay más de 3× de diferencia.
   Necesito saber cuál es la nuestra. Si me equivoco de columna, las
   cotizaciones salen por debajo del costo.

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

**Y lo más importante para saber si esto quedó bien hecho:**

10. **Dos o tres cotizaciones ya cerradas**, con la especificación
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
