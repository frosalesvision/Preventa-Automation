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

## Lo que ya se resolvió

### Contestadas por preventa el 2026-09-22

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

## Lo que sigue pendiente

### 4. Tarifario de mano de obra `R8`

**No es que no contestaran: no existe todavía.** Tienen anotados un par
de precios base y **la tarea pendiente de armar un cuadro de
instalaciones con costos estandarizados**.

⚠️ **Asumir que no va a llegar** (criterio de Fabián, 2026-09-23:
*"posiblemente no lo pasen"*). O sea: el plugin tiene que funcionar
bien **sin** tarifario de forma permanente, no "mientras tanto". La
pestaña `MANO DE OBRA` se llena a mano y eso es el estado final, no un
estado transitorio.

**Qué hacer mientras tanto:** nada, y no insistir. La pestaña
`MANO DE OBRA` se llena a mano en cada cotización. Cuando construyan el
cuadro, se carga en la pestaña `Tarifario Mano de Obra` del catálogo,
que ya está lista y vacía esperándolo.

### ~~7b. El redondeo del tipo de cambio~~ — CERRADO el 2026-09-23

Es criterio por proyecto: a veces se usa el del BCCR tal cual, a veces
se sube un poco a favor de la empresa. **No hay regla que cargar.** La
ficha pregunta el precio de compra y el de venta en cada cotización.

### 2b. ¿El IVA de las compras locales se acredita? `R2` — va a contabilidad, no a preventa

**Esta pregunta estaba mal dirigida** (aclarado 2026-09-23). No es sobre
los dos IVA —eso ya está claro en R2 y preventa lo tiene claro—; es una
pregunta **contable**:

> Cuando Grupo Visión compra local y paga 13% de IVA, ¿ese dinero **se
> recupera** después contra el IVA que la empresa le cobra a sus
> clientes, o **se queda como costo** del proyecto?

Si se recupera, no es un costo y el 0% de `Equipos` está bien. Si no se
recupera, es un costo real y hoy está faltando en las líneas de
proveedor local. **La respuesta la tiene quien lleva la contabilidad o
los impuestos de la empresa, no preventa.**

Rastreando las fórmulas del machote apareció que **el transporte y el
DAI solo se cobran si la línea dice `IMPORTADO = si`, pero el IVA de
línea se aplica siempre**, con el porcentaje que tenga la pestaña. En
`Equipos` ese porcentaje es 0% y en `MATERIALES` es 13%. O sea que el
IVA lo decide *en qué pestaña se escribió la línea*, no el producto.

**Pregunta concreta:** cuando Grupo Visión le compra a un proveedor
local y le cobran el 13% de IVA, ¿ese IVA **es un costo** del proyecto,
o **se acredita** contra el IVA que después se le cobra al cliente?

**Por qué importa:** el catálogo tiene 193 productos de proveedores
locales. Si ese IVA es un costo, una línea de proveedor local escrita en
`Equipos` —que tiene IVA 0%— sale con el costo **subvaluado en 13%**:
sobre $100 por unidad, el costo nacionalizado pasaría de $103 a $116,39.
Si se acredita, está bien como está.

**Si no llega:** no se toca nada. La automatización solo **avisa**
cuando una línea de proveedor local cae en una pestaña con IVA 0%.

### 6b. La pestaña `MANO DE OBRA` tiene dos fórmulas distintas para lo mismo `R9`

Salió al verificar la respuesta del punto 6, y es más concreto de lo que
suena. En esa pestaña, las columnas de viáticos son: `H` alimentación,
`I` combustible, `J` hospedaje, `E` días, `F` personas. El total va en
`K`. **Pero `K` no se calcula igual en todas las filas:**

```excel
fila 5   (Configurador)   K5 = (H5*E5*F5) + (I5*E5) + (J5*E5)
filas 6-8 (Supervisor,    K6 = ((H6+I6+J6)*E6)*F6
           PM, Diseño)
```

En la fila 5, la alimentación se multiplica por días **y** personas,
pero el combustible y el hospedaje **solo por días**. En las filas 6 a
8, **todo** se multiplica por días y personas, incluido el combustible.

**Con los mismos datos, dan distinto.** Dos técnicos, tres días,
alimentación $12 por día, combustible $21,60, hospedaje $40 la noche:

| | Cálculo | Total |
|---|---|---|
| Fórmula de la fila 5 | 72 + 64,80 + 120 | **$256,80** |
| Fórmula de las filas 6-8 | (73,60 × 3) × 2 | **$441,60** |

**$184,80 de diferencia por el mismo viaje**, según en qué fila se
escriba el rol.

**Dos preguntas concretas:**

1. El **hospedaje**, ¿se paga por persona (dos técnicos, dos
   habitaciones) o por viaje?
2. El **combustible**, ¿se multiplica por la cantidad de personas? En la
   fila 5 no, en las filas 6-8 sí. Intuitivamente van en el mismo carro,
   así que la de la fila 5 parece la correcta — pero es criterio de
   ellos, no nuestro.

**No se tocó ninguna de las dos fórmulas.** Solo se quitó un `-1` que
restaba un dólar siempre y que no tenía explicación posible.

### 1b. ¿La cotización base debe quedar a 1,85× el MSRP? `R4.1`

Preventa dijo que se cotiza siempre con MSRP. Medido lo que eso produce:
escribir el MSRP en `Costo Unit` hace que **el cliente vea 1,85 veces el
MSRP**, porque la matriz le suma transporte, DAI, administración y
margen encima.

**Pregunta concreta:** ¿es eso lo que esperan de una cotización base, o
la intención era que el cliente viera un precio más cerca del MSRP?

**Por qué importa:** es conservador y nunca se cotiza bajo costo, que
está bien. Pero si un competidor cotiza cerca del MSRP, una oferta base
a 1,85× queda fuera de rango antes de empezar a negociar.

### ~~10. Dos o tres cotizaciones cerradas~~ — YA LAS TENEMOS, sin pedirlas

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

### 12. No se registra qué ofertas se ganan

De los estados del `Control de cotizaciones` —751 cotizaciones entre
2025 y 2026— **ninguno indica que una oferta se haya ganado**:

| Estado | 2026 | 2025 |
|---|---|---|
| Enviada | 253 | 338 |
| Descartada | 75 | 59 |
| Pendiente | 14 | 1 |
| En espera | 7 | — |

El flujo termina en *Enviada*. Lo ganado se anota aparte, en la
proyección de ventas, sin número de oferta que permita volver a la
cotización que lo produjo.

**Pregunta concreta:** ¿se puede agregar el número de oferta a la
proyección de ventas, o un estado "Ganada/Adjudicada" al control?

**Por qué importa más de lo que parece:** hoy no se puede contestar
*"¿qué margen llevaban las ofertas que ganamos?"*, que es exactamente lo
que haría falta para saber a qué precio se gana. Con un solo campo en
común, esa pregunta se contesta sola.

### ~~13 a 16~~ — CERRADAS por Fabián el 2026-09-23

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

### 10b. Las cotizaciones cerradas siguen sirviendo, para otra cosa

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

### 17. Hay una línea de producto entera que se cotiza y no está en el catálogo

Minando 936 matrices reales aparecieron **149 líneas distintas** de
productos **Panasonic i-PRO** que el equipo cotiza y que el catálogo no
tiene. Las más repetidas:

| Producto | Veces | Costo visto |
|---|---|---|
| NVR de 16 canales | 16 | $1.213,26 |
| Cámara box de interior 1080p | 26 | $281 y $326 |
| Lente 2.8-8.0mm | 11 | $219 |
| Montaje pendant/pared | 15 | $13,26 y $18 |
| Cámara bullet 5MP AI con zoom | 7 | $1.052,68 |
| Cámara PTZ 6MP 30x | 5 | $2.501,70 |
| Servidor NVR 128TB | 5 | $16.279 a $16.641 |

**Preguntas concretas:**

1. ¿De qué proveedor se compra i-PRO? No aparece en ninguna lista de
   precios de las que tenemos cargadas.
2. ¿Hay lista de precios de esa marca? Si la hay, se carga completa y se
   deja de cotizar de memoria.
3. Los costos de arriba salen de cotizaciones viejas: ¿siguen vigentes?

**Por qué importa:** hoy, si alguien pide una cámara i-PRO, la
automatización **no puede proponerla** — no existe para ella. El asesor
tiene que buscar el precio en una cotización vieja, que es exactamente lo
que este proyecto quiere eliminar.

**Ya se cargaron dos a mano** con lo que se pudo verificar: el montaje
`PUM9` y la solución solar `INVID-ISSS-300W`. Los dos quedaron marcados
en la columna de origen con **"PRECIO NO CONFIRMADO"**, porque el número
sale de una cotización y no de una lista de proveedor.

⚠️ Y un detalle que conviene revisar: **`INVID-ISSS-300W` es un SKU de
InVidTech**, el mismo proveedor cuya lista ya está cargada, pero no vino
en ella. Puede que esa carga haya dejado más productos afuera.

### 11. Lo que falte cargar

- PDFs o Excel de proveedores que todavía no estén cargados.
- La "lista de precios general" de la nube que se mencionó.
- Cualquier lista propia que alguien mantenga aparte.

No hace falta pasarlos a ningún formato: el PDF o el Excel tal como
llegó del proveedor sirve.

### Cerradas el 2026-09-22 (no preguntar de nuevo)

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
