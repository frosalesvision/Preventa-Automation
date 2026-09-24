# Lo que falta, y de dónde sale

> **Casi nada falta ya del equipo comercial.** Este documento empezó
> siendo una lista de nueve preguntas para ellos y hoy tiene **una sola**,
> que además no es para preventa sino para contabilidad.
>
> El resto se resolvió **midiendo 649 cotizaciones reales** en vez de
> preguntando. Abajo está lo que quedó abierto, lo que se resolvió
> midiendo, y lo que ellos contestaron en su momento.
>
> Contexto: comprometido en la reunión del 2026-09-14 — una primera pasada
> para el 16/17 de setiembre y el resto la semana siguiente. Meta conjunta:
> **empezar a usar el plugin en octubre.**
>
> El detalle de cada regla está en [`reglas-negocio.md`](reglas-negocio.md).

---

# Lo que sigue pendiente

> **Cambio de estrategia, 2026-09-23.** Fabián lo dijo así:
>
> > *"ellos ahorita están muy ocupados, no pueden responder. Nuestro
> > filtro de verdad son las cotizaciones a las que podemos acceder y
> > estudiar, tal cual lo hemos hecho."*
>
> **Dejamos de preguntar y empezamos a medir.** Ya se leyeron 649
> matrices reales de 2025 y 2026; ahí está lo que el equipo hace de
> verdad, y sale más rápido y más confiable que una entrevista. Lo que
> antes era una lista de nueve preguntas quedó en **una sola**, y ni
> siquiera es para preventa.

## La única que sigue abierta

### ¿El IVA de las compras locales se acredita? `R2`

**Aplazada a propósito.** No es para preventa: la contesta quien lleva
la contabilidad o los impuestos de la empresa.

Cuando Grupo Visión compra local y paga 13% de IVA, ¿ese dinero **se
recupera** después contra el IVA que se le cobra al cliente, o **se
queda como costo** del proyecto?

**Mientras tanto se replica lo que hacen hoy**, que es lo que muestran
las 649 matrices: `Equipos` con IVA de línea 0% y `MATERIALES` con 13%.
No se toca nada.

---

# Lo que se resolvió midiendo, no preguntando

Todo esto se cerró el 2026-09-23 con el mismo criterio: **el valor más
común de las cotizaciones reales pasa a ser el default del machote, y se
puede cambiar a mano cuando el proyecto lo amerite.** La automatización
nunca lo impone.

| Lo que faltaba | Cómo quedó | De dónde sale |
|---|---|---|
| **Tarifario de mano de obra** | Hora hombre **$8,90**, día **$48** | 99% de 496 matrices con datos |
| **Alimentación** | **$12** por día y persona | 88% de los casos |
| **Costo por kilómetro** | **$0,60** | 99% de los casos |
| **Hospedaje** | **Cero por defecto** | Es el valor más común: el 88% de las cotizaciones no lo cobra |
| **Tarifa de hospedaje cuando aplica** | **$100 por noche** | 37 de 58 casos donde sí se cobró |
| **Margen** | **27,4%** | El default del machote, y el más usado |
| **DAI, transporte, imprevistos, administración** | Como los trae el machote | 75% a 97% de los casos |
| **Las dos fórmulas de viáticos** | Unificadas en la de la fila 5 | Es la fila que de verdad se llena |
| **Estados de las ofertas** | Se quedan como están | Decisión de Fabián |

### Sobre el hospedaje, que es el caso interesante

Ponérle $100 por defecto habría parecido lo correcto — es la tarifa más
usada. Pero **el 88% de las cotizaciones no cobra hospedaje**, porque la
mayoría de los trabajos no requieren quedarse. El valor más común es
**cero**, y ponerle $100 le habría agregado costo a nueve de cada diez
cotizaciones.

Queda en cero, con la tarifa anotada en la propia pestaña para cuando
haga falta.

### Sobre el margen y el 1,85×

Escribir el MSRP en `Costo Unit` hace que el cliente vea **1,85 veces el
MSRP**, porque la matriz le suma transporte, DAI, administración y
margen. Se deja así: es lo que hacen en la mayoría de las cotizaciones
medidas, y el margen se puede cambiar a mano en el Excel.

---

# Lo que ya se cerró

Se conserva para que nadie lo vuelva a preguntar.

## Contestadas por preventa el 2026-09-22


Llegaron siete de las nueve. **Varias no se contestaron con un dato sino
con una decisión: eso se hace a mano y no se va a automatizar.** Eso es
una respuesta válida y cierra el tema.

| Pregunta | Cómo quedó |
|---|---|
| **1. Descuentos por proveedor y marca** | **No hay tabla y no la va a haber.** El descuento depende de marca, tipo de equipo, nivel de partner y proyecto. Se cotiza con MSRP y ellos aplican el descuento a mano. Cuando el proyecto se registra, el proveedor manda los precios ya con descuento. Ver R4 |
| **2. En qué nivel de precio compramos** | **MSRP, siempre.** La columna del nivel Dealer quedó renombrada como referencia con aviso de no usar. Ver R4.2 |
| **3. Clientes exentos** | ✅ **Datos cargados** en `Regimen Fiscal Clientes`. Una institución de seguridad social exenta, dos universidades públicas al 2%, zona franca varía caso por caso. El 3% de administración **no se modela**: lo deciden según qué tan competitivos quieran ser |
| **5. Proporciones de materiales** | **Confirmado que no se puede estandarizar.** *"Una cámara puede instalarse a 5 metros del grabador, pueden ser 70, 80 mts."* Coincide con lo que ya se había decidido. Ver R10 |
| **6. Destinos y kilometraje** | **Ya estaba resuelto en el machote** y ellos lo sabían: `Transporte` + `MANO DE OBRA` lo calculan. Al verificarlo apareció un `-1` en la fórmula de viáticos, ya corregido. Ver R9 |
| **7. Porcentajes por etapa** | **No hay valores establecidos y es a propósito.** Varía por magnitud del proyecto y por cuán agresivos quieran ser. Queda manual. Ver R6 |
| **8. Tipo de cambio** | **Banco Central, precio de venta.** Ya anotado en la pestaña `Tipo de Cambio` |

---


## ~~7b. El redondeo del tipo de cambio~~ — CERRADO el 2026-09-23


Es criterio por proyecto: a veces se usa el del BCCR tal cual, a veces
se sube un poco a favor de la empresa. **No hay regla que cargar.** La
ficha pregunta el precio de compra y el de venta en cada cotización.

## ~~10. Cotizaciones ya terminadas para comparar~~ — YA LAS TENEMOS, sin pedirlas


**Resuelto el 2026-09-23 yendo a la carpeta compartida en vez de
pidiéndolas.** Medido:

- **165 cotizaciones de 2025-2026** tienen a la vez **visita técnica con
  contenido y matriz** en su carpeta.
- Cruzando `Proyeccion de Ventas 2026.xlsx` (que sí registra el cierre)
  contra las carpetas de cliente: **35 negocios ganados en 2026** por
  $780.427, de los cuales **16 tienen matriz y visita técnica**
  ($367.019 entre ellos).

Esos 16 son el caso patrón, disponibles hoy. No hace falta pedir nada.

⚠️ **Lo que sí falta preguntar, y es más importante:** el resultado de
una oferta vive en un archivo distinto (`Proyeccion de Ventas`), con una
llave distinta (cliente + proyecto, **sin número de oferta**), mientras
el `Control de cotizaciones` solo llega hasta *Enviada*. Ver abajo.

## ~~13 a 16~~ — CERRADAS por Fabián el 2026-09-23


Las cuatro se resolvieron con el mismo criterio: **el machote es el valor
por defecto, y siempre se puede cambiar a mano en el Excel.** No hay que
preguntarle nada de esto al equipo comercial.

| Pregunta | Cómo quedó |
|---|---|
| ¿El día son $48 o $71,20? | **$48.** Katherine lo había dicho así. El `$71,20` calculado queda descartado |
| ¿El DAI es 14% o 15%? | **Como lo trae el machote de 2026**: 15% en `Equipos`, 14% en `MATERIALES`. Sin preguntas |
| Los porcentajes estables (transporte 10%, admin 3%, imprevistos 3%, km $0,60) | **Se quedan como están** |
| ¿Se cotiza contra el techo del pliego? | Ver abajo: la pregunta estaba mal explicada |

**La condición que aplica a las cuatro:** son valores por defecto, no
valores fijos. La ficha los muestra al armar cada cotización y el asesor
puede cambiarlos; y quien prefiera hacerlo directo en el Excel, también
puede. La automatización **nunca** los impone.

El machote trae la hora hombre en **$8,90** y el precio por día en
**$48,00**, y se copian a casi todas las cotizaciones sin que nadie los
toque (99% de 184 matrices de 2026).

**Pero no son consistentes entre sí: $8,90 × 8 horas = $71,20, no $48.**

**Pregunta concreta:** ¿cuál de los dos es el correcto, o ninguno? Lo
mismo con la alimentación en $12,00 por día y el costo por kilómetro en
$0,60, que aparecen idénticos en el 91% y el 100% de las matrices.

## Cerradas el 2026-09-22 (no preguntar de nuevo)


Se resolvieron sin necesidad del equipo comercial. Quedan anotadas para
que nadie las vuelva a abrir.

| Pregunta | Cómo quedó |
|---|---|
| Antigüedad del precio: ¿2 semanas o 2 meses? | **2 meses.** La mención a 2 semanas quedó descartada. `buscar-equipo` sigue mostrando siempre los días exactos |
| ¿Qué determina el prefijo de la oferta (`T1`/`T4`/`T5`)? | **No se sabe, y se deja como réplica de lo que hay:** se propone el prefijo usado más recientemente para ese cliente y el asesor confirma |
| ¿El monto de los Excels de control va con o sin IVA? | **Sin IVA.** Se escribe el SUBTOTAL, que es lo que dice el encabezado de la columna |
| Las pestañas de resumen traían datos de un proyecto anterior: ¿estaba bien limpiarlas? | Sí, y además aparecieron **más**, ocultas, con la matriz de costo completa de ese proyecto. Se borraron el 2026-09-22 |
| El margen de las cuatro pestañas de servicio | **Ya no aplica:** esas pestañas se borraron el 2026-09-22, eran del mismo proyecto anterior |

---

# Mensaje para Teams

> ⚠️ **Este mensaje ya se envió y ya lo contestaron** (2026-09-22). Se
> conserva como registro. Lo que quedó pendiente está arriba; para
> preguntarlo hace falta un mensaje nuevo y mucho más corto.

---

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

9. **Una rapidita, Katherine:** en el control de cotizaciones, el monto
    que anotan, ¿es con IVA o sin IVA? Lo pregunto porque la columna se
    llama "Monto sin IVA" pero quería confirmarlo antes de que la
    automatización empiece a llenarla sola.

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

