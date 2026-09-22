# Reglas de negocio de preventa — catálogo consolidado

> **Leer esto antes de tocar cualquier skill que calcule dinero.**
> Este documento es la fuente única de las reglas que determinan un
> número dentro de una cotización. Cada regla dice si está **confirmada**
> (alguien de preventa la dijo explícitamente), **pendiente** (sabemos
> que existe pero no tenemos el dato) o **supuesta** (la inferimos y hay
> que validarla).
>
> Si una regla cambia, se actualiza acá **primero** y después se revisa
> qué `SKILL.md` quedó desalineado. No duplicar el detalle de una regla
> dentro de un skill: el skill referencia esta página.
>
> Origen principal: reunión con Katherine (preventa) del **2026-09-14**,
> transcript completo analizado el 2026-09-18. Complementado con la
> auditoría del machote y del catálogo hecha el mismo día.

---

## R1 — "IMPORTADO" significa quién nos vende, no dónde se fabrica

**Estado: confirmada.**

La columna `IMPORTADO` de las pestañas de producto marca si **Grupo
Visión compra ese ítem fuera del país**, no el país de fabricación del
equipo.

> Ejemplo textual de preventa: un kit de panel solar se marca como
> importación *"porque se está comprando en \[el proveedor], \[el
> proveedor] está afuera del país, no está en Costa Rica"*.

Consecuencias en el machote (verificadas en las fórmulas):

- `Transporte` solo se aplica si es `"si"` → `=IF(C6="si", E6*$G$4, 0)`
- `DAI` solo se aplica si es `"si"` → `=IF(C6="si", (...)*$J$4, 0)`
- `Imprevistos`, `IVA` y `Administración` se aplican siempre.

**Cómo derivarlo:** del **proveedor** de la línea. Si el proveedor está
en Costa Rica → `"no"`. Si está fuera → `"si"`. Cuando el catálogo trae
una columna tipo "Precio Nacional" (`SI`/`NO`), esa mapea directo:
`SI` → `"no"` importado, `NO` → `"si"` importado.

⚠️ **Error a no repetir:** una versión anterior de
`armar-cotizacion/SKILL.md` decía inferirlo del **País de origen** del
catálogo. Eso es incorrecto: una cámara fabricada en Corea comprada a un
distribuidor local **no** es importación para Grupo Visión, y marcarla
como tal le suma transporte y DAI que no corresponden.

---

## R2 — Hay dos IVA distintos con el mismo nombre

**Estado: confirmada.** Es la regla que más confusión ha generado.

| | Qué es | Dónde vive | De qué depende |
|---|---|---|---|
| **IVA de línea** | Un **costo**: el impuesto que el proveedor nos cobra a nosotros al comprar | Columna `IVA` de `Equipos`, `MATERIALES`, `OPEX…` | De si a Grupo Visión le cobran IVA en esa compra |
| **IVA de la oferta** | Un **impuesto al cliente**: lo que el cliente paga sobre el total | Fila `IMPUESTO` de la pestaña `COTIZACIÓN ` | Del **régimen fiscal del cliente** (ver R3) |

> Palabras de preventa: *"si el equipo es de afuera, usted no les va a
> cobrar IVA \[al cliente]. Pero si se compró algún accesorio, a
> nosotros sí nos están cobrando el IVA, entonces nosotros sí lo
> cobramos… no se va a ver reflejado acá porque el cliente es exento,
> pero nosotros sí tenemos que cobrarlo a nivel de matriz porque a
> nosotros nos están cobrando ese monto."*

**No es doble cobro.** Son dos conceptos separados. Una cotización puede
legítimamente tener IVA de línea en materiales y 0% de impuesto al
cliente si el cliente es exento.

### Mapa completo: dónde vive cada IVA y cuándo se aplica

Rastreado celda por celda el 2026-09-22 sobre las 5 pestañas de
producto. **Ojo con la letra de columna: en `Equipos` el IVA es la `I`,
en las otras cuatro es la `H`.**

| Pestaña | Celda del % | Valor base | Fórmula que lo consume |
|---|---|---|---|
| `Equipos` | `I4` | **0%** | `I6 = (E6+G6+H6)*$I$4` |
| `Productos 2` | `H4` | **13%** | `H6 = (D6+F6+G6)*$H$4` |
| `MATERIALES` | `H4` | **13%** | `H6 = (D6+F6+G6)*$H$4` |
| `OPEX Proyecto` | `H4` | **13%** | `H6 = (D6+F6+G6)*$H$4` |
| `OPEX GV` | `H4` | **0%** | `H6 = (D6+F6+G6)*$H$4` |
| `COTIZACIÓN !J75` | — | según ficha | el impuesto **al cliente**, ver arriba |
| `COTIZACION (Financ)!J75` | — | según ficha | el mismo, sobre el total mensual |

**El momento del match es la elección de pestaña, no la línea.** Esto es
lo que hay que entender para automatizarlo: el IVA de línea **no se
decide por producto**, se decide por **en qué pestaña se escribe la
línea**. Es un porcentaje único en la fila 4 que multiplica a las 50
líneas de esa pestaña por igual. O sea: el instante en que
`armar-cotizacion` decide "esto va en `Equipos`" es el instante en que
queda decidido su IVA.

### ⚠️ El IVA no mira la columna `IMPORTADO`, y el transporte y el DAI sí

Verificado en las 5 pestañas, sin excepción:

```excel
G6 = IF(C6="si", E6*$G$4, 0)              <- Transporte: SOLO si es importado
J6 = IF(C6="si", (E6+G6+H6+I6)*$J$4, 0)   <- DAI:        SOLO si es importado
I6 = (E6+G6+H6)*$I$4                      <- IVA:        SIEMPRE, importado o no
```

Las dos primeras preguntan por `IMPORTADO`; la del IVA no. Eso significa
que la pestaña y la columna pueden contradecirse, y cuando lo hacen el
número sale mal sin ningún error visible:

- **Un producto de proveedor local metido en `Equipos`** (`IMPORTADO` =
  `no`) queda sin transporte y sin DAI —correcto— pero también con
  **0% de IVA**. Si a Grupo Visión sí le cobraron el 13% en esa compra,
  **el costo queda subvaluado en 13%** y la cotización sale con menos
  margen del que cree tener. Medido sobre $100 × 10 unidades: el costo
  nacionalizado unitario pasaría de `$103` a `$116,39`.
- **Un producto importado metido en `MATERIALES`** (`IMPORTADO` = `si`)
  recibe transporte y DAI —correcto— y además **13% de IVA que no se
  pagó**, porque en una importación el impuesto entra por aduanas.

Esto **importa ahora** porque el catálogo ya tiene 193 productos de
proveedores locales (Seguritronic, ISTC, EPA, Tectel y otros) además de
los importados. Antes casi todo era importado y la simplificación no se
notaba.

**No lo estoy llamando un error todavía**, y a propósito: puede ser
correcto si Grupo Visión **acredita** el IVA de las compras locales
contra el IVA que le cobra al cliente, en cuyo caso no es un costo y el
0% de `Equipos` está bien puesto. Eso es una decisión contable de la
empresa, no algo que se pueda deducir del archivo. Está planteado como
pregunta en [`pendientes-comercial.md`](pendientes-comercial.md).

**Mientras no se responda:** `armar-cotizacion` no debe mover el IVA de
la fila 4 por su cuenta. Lo que sí debe hacer es **avisar** cuando una
línea con `IMPORTADO="no"` cae en una pestaña con IVA 0%, o al revés —
es el único momento en que se puede detectar la contradicción.

### El impuesto al cliente ya no está quemado (2026-09-22)

La versión anterior de esta regla decía que `COTIZACIÓN ` tenía el 13%
*"escrito duro en la fórmula `=+J29*0.13`"*. Dos cosas cambiaron: la
celda es `J75` (no `J29`, que quedó viejo al ampliar a 50 líneas), y ya
no está quemado. Ver el detalle en R3.

---

## R3 — El impuesto al cliente depende del cliente

**Estado: confirmada como regla, pendientes los datos.**

No todos los clientes pagan lo mismo. Casos que dio preventa
(genéricos a propósito, sin nombrar instituciones en este archivo):

- Una institución de gobierno: se le cobra impuesto completo.
- Una municipalidad: no se le cobra impuesto sobre el equipo importado.
- Una universidad pública: se le cobró **2%**, no 13%.
- El 3% de administración: a unos clientes se les carga y a otros no.

**Diseño acordado con Fabián (2026-09-18):** dos niveles, no uno.

1. **Tabla maestra** en el Excel del catálogo, pestaña
   `Regimen Fiscal Clientes`, con la misma lógica que `Tipo de Cambio`:
   dato de referencia que el equipo mantiene a mano.
   Columnas: `Cliente` · `Exento de impuesto (si/no)` ·
   `% impuesto al cliente` · `% administración` · `Notas` ·
   `Fecha de actualización` · `Confirmado por`.
   ✅ **La pestaña ya existe, creada vacía el 2026-09-18.** Falta que el
   equipo comercial la llene.
2. **Copia congelada dentro de cada cotización**, en la pestaña
   `Datos del proyecto` del machote. Cuando se arma una cotización se
   copian ahí los valores vigentes ese día.
   ✅ **La pestaña ya existe, creada el 2026-09-18** — es la última del
   libro (posición 39, se agregó al final a propósito para no correr los
   índices de las hojas existentes). Tiene seis secciones:
   identificación, régimen fiscal, costo y registro de proyecto,
   porcentajes usados, alcance y mano de obra, financiamiento y tipo de
   cambio. Los porcentajes **se espejan solos por fórmula** desde la
   fila 4 de `Equipos` y `MATERIALES`, así que no hay que copiarlos a
   mano ni pueden quedar desfasados.

**Por qué las dos y no solo la tabla maestra:** las cotizaciones viejas
son archivos `.xlsx` separados, así que cambiar la tabla maestra no las
altera — pero sí hace imposible explicar *por qué* una oferta de hace
seis meses llevaba 2% si hoy la tabla dice 13%. La copia congelada
resuelve la trazabilidad; la tabla maestra evita mantener el dato en 300
lugares. Es el mismo patrón de "referencia + snapshot" que ya se usa
con el tipo de cambio.

**Regla de ejecución:** si el cliente no está en la tabla, **preguntar**
y ofrecer agregarlo. Nunca asumir 13% en silencio, y nunca asumir
exención en silencio.

### La ficha ahora sí manda sobre el impuesto (corregido 2026-09-22)

Hasta la corrida en seco del 2026-09-21, esta regla estaba escrita pero
**no conectada**: la fila `IMPUESTO` de `COTIZACIÓN ` era literalmente
`=+J74*0.13`, con el 13% escrito a mano, y lo mismo en
`COTIZACION (Financ)`. La ficha preguntaba el régimen fiscal y la
cotización lo ignoraba. Una municipalidad exenta pagaba 13% y **Excel no
mostraba ningún error** — el modo de falla era silencioso. Medido sobre
la cotización de prueba: **$793,02 de más sobre un subtotal de
$6.100,18**.

`J75` de las dos pestañas ahora es:

```excel
=J74*IF(LOWER(TRIM('Datos del proyecto'!$B$15))="si",0,
       IF(ISNUMBER('Datos del proyecto'!$B$16),
          IF('Datos del proyecto'!$B$16>1,
             'Datos del proyecto'!$B$16/100,
             'Datos del proyecto'!$B$16),
          0.13))
```

Cuatro decisiones dentro de esa fórmula, cada una por una razón:

- **`B15="si"` gana sobre todo lo demás.** Si el cliente está marcado
  exento, no importa qué diga `B16`: el impuesto es 0.
- **Ficha vacía = 13%.** El machote en blanco se comporta exactamente
  como antes, así que nada de lo ya cotizado cambia de valor.
- **`B16>1` se divide entre 100.** La celda es de formato General: quien
  escriba `13` queriendo decir `13%` habría cobrado 1.300%. El guard
  convierte el error tipográfico más probable en el número correcto.
- **No lleva `IFERROR`.** `ISNUMBER` ya cubre el texto, y devolver `""`
  rompería `J76 = ROUNDDOWN(J74+J75,2)` con `#¡VALOR!` — es exactamente
  el bug que tuvo la cotización financiada con `""*cantidad`.

`Datos del proyecto!C16` dejó de ser la pista fija "13% por defecto" y
ahora muestra **la tasa que de verdad se está aplicando**
(`Se aplica 0% (vacio = 13%)`), para que la exención no sea invisible
mientras se llena la ficha. Se calcula multiplicando por 100 y pegando
el `%`, no con `TEXT(...,"0.##%")`: el código de formato de `TEXT` lo
interpreta Excel según el idioma de la interfaz, y en español el punto
es separador de miles — la primera versión mostraba `0.13%`.

**Qué de esto es regla de la empresa y qué lo agregué yo** (distinción
pedida por Fabián el 2026-09-22 — *"no estamos inventando fórmulas, lo
que hacemos es analizar lo que ya hay, entender el flujo, e intentar
mejorarlo y automatizarlo"*):

| Parte | Origen |
|---|---|
| Que el impuesto depende del régimen del cliente | **Regla de la empresa**, la explicó preventa |
| Los campos `B15` / `B16` de la ficha | **Ya existían** en el machote |
| Que `J75` los lea en vez del 13% quemado | **Automatización** de esa regla, no invención |
| Que la ficha vacía siga dando 13% | **Conservar** el comportamiento anterior |
| El guard `>1` (si escriben `13` se divide entre 100) | Lo propuse yo, **Fabián lo confirmó como regla** el 2026-09-22: *"si escriben 13 en vez de 13%, debería tomarlo como 13%"* |
| El fallback `ISNUMBER` ante texto | **Agregado mío.** Evita que `J76` dé `#¡VALOR!` |

El fallback ante texto sigue siendo criterio mío y se puede quitar; el
guard `>1` ya no, porque es comportamiento pedido. La celda es de formato
General, así que sin él escribir `13` queriendo decir `13%` cobraría
1.300% sin avisar.

Cubierto por la prueba **P-09** de
[`pruebas-validacion.md`](pruebas-validacion.md), que corre los seis
escenarios (vacío, exento, 0.04, 4, texto basura, ` SI ` con espacios y
mayúsculas) más la comprobación de que la financiada respeta la
exención. Si alguien vuelve a quemar un porcentaje, el smoke test falla.

⚠️ **Lo que esto NO resuelve:** la pestaña `Regimen Fiscal Clientes`
sigue vacía, así que el valor de `B15`/`B16` hoy lo tiene que escribir
la persona que cotiza. La fórmula garantiza que *si se escribe, se
respeta* — no que alguien lo sepa.

---

## R4 — El costo unitario no es el precio de lista

**Estado: confirmada la regla, pendientes todos los datos.** Es el
bloqueante número uno del proyecto.

El costo real de Grupo Visión depende de:

1. **Registro del proyecto** con el distribuidor (ver R5).
2. **Monto mínimo de compra** — por debajo de cierto monto el
   distribuidor no aplica el descuento mayor.
3. **La marca / el distribuidor** — el descuento de una marca no es el
   de otra.
4. **La familia de producto** — dentro de una misma marca, el descuento
   puede no aplicar a todo.

Preventa confirmó que **por ahora esta columna se llena a mano**, hasta
que existan las reglas cargadas.

**Dónde van a vivir las reglas:** pestaña `Reglas de Descuento` del
Excel del catálogo — `Proveedor` · `Marca` ·
`Familia / categoría (vacío = toda la marca)` · `% de descuento` ·
`Requiere registro de proyecto (si/no)` · `Monto mínimo de compra (USD)`
· `Nivel de precio base` · `Notas` · `Fecha` · `Confirmado por`. Una
marca puede tener varias filas. ✅ **Ya existe, creada vacía el
2026-09-18.** El cálculo del descuento **no se guarda en el catálogo**:
se resuelve al momento de cotizar y va al "Costo Unit" de esa cotización
puntual.

### R4.1 — Qué hacer mientras no haya reglas

> Decisión de Fabián (2026-09-18): *"Si un proveedor no le hace
> descuentos a Grupo Visión por X razón, o no tenemos las reglas
> cargadas para ese proveedor, use directamente el precio registrado."*

- Si **hay** una regla de descuento aplicable → calcular con ella.
- Si **no hay** regla → usar el precio del catálogo tal cual, diciendo
  explícitamente que es precio de lista sin descuento.
- **Nunca** inventar un porcentaje ni aplicar el de otra marca.

### R4.2 — El catálogo tiene tres niveles de precio y no sabemos cuál es el nuestro

**Hallazgo del 2026-09-18, verificado contra el PDF del proveedor.
Pendiente de respuesta del equipo.**

El PDF de lista de precios de uno de los distribuidores publica en su
encabezado **tres** columnas: `Dealer Program` · `DEAL` · `MSRP`.

- Nuestra columna `Precio USD` = **MSRP** (el más alto).
- Nuestra columna `Precio especial GV (USD)` = **Dealer Program** (el más
  bajo).
- **La columna intermedia (`DEAL`) no se cargó** — está en el PDF, se
  puede re-extraer cuando se sepa que hace falta.

En un ítem cualquiera los tres niveles pueden diferir por más de 3×.
**Cuál de los tres es el costo real de Grupo Visión depende del programa
de distribuidor en el que esté la empresa, y eso nadie lo ha confirmado.**

⚠️ Riesgo concreto en las dos direcciones: usar el nivel más bajo cuando
el real es el intermedio produce cotizaciones que **pierden plata** si se
ganan; usar el MSRP produce cotizaciones **no competitivas**. Por eso la
regla de ejecución hasta que respondan es: **mostrar los niveles
disponibles y que el asesor confirme cuál aplica**, nunca elegir uno
automáticamente.

### R4.3 — Estado real del dato por marca (verificado 2026-09-18)

| Origen | Filas | `Precio especial GV` |
|---|---|---|
| Distribuidor con PDF de 3 niveles | 948 | Cargado (nivel `Dealer Program`) |
| Fabricante con pricelist de un solo precio | 1.410 | Vacío — su lista solo publica MSRP |
| Proveedores locales varios | ~194 | Vacío |

⚠️ **Corrección a una creencia previa:** nunca se aplicó una "regla del
50%" a nada. Los precios especiales cargados salieron de la segunda
columna del PDF del proveedor. Y la marca donde el 50% *sí* aplicaría
según preventa es justamente la que **no tiene ningún precio especial
cargado**, porque su pricelist no publica esa columna — ese descuento
tiene que llegar como regla escrita del equipo.

**Además:** hasta el 2026-09-18 ninguna skill leía la columna
`Precio especial GV`. Los precios de distribuidor que ya están cargados
se estaban ignorando.

---

## R5 — Registro de proyecto

**Estado: confirmada como concepto, pendiente el mecanismo.**

**Qué es:** antes de que salga una licitación se hacen estudios de
mercado. En ese momento Grupo Visión le pide al distribuidor de una
marca que **registre el proyecto a su nombre**. Si nadie lo registró
antes, Grupo Visión queda con el proyecto "protegido" y obtiene el
descuento mayor de esa marca. Si otro integrador ya lo registró, Grupo
Visión obtiene a lo sumo un descuento menor, y puede tener que bajar su
utilidad o no participar del todo.

**No es un registro legal ni un trámite del cartel.** Es una figura
comercial entre integrador y distribuidor, para que dos integradores no
compitan con el mismo precio de compra sobre el mismo proyecto.

**El problema operativo que preventa quiere resolver:** entre el
registro (durante el estudio de mercado) y la licitación pueden pasar de
dos a seis meses. *"Si lo registramos hace un mes uno se acuerda, pero
si ya pasaron cinco meses, ese montón de proyectos que uno cotizó tal
vez se le puede ir."* Hoy no hay ningún lugar donde consultar qué
proyectos están registrados y con quién.

**Lo que ella pidió:** una columna en el control de cotizaciones que
diga si el proyecto está registrado. Eso toca un Excel compartido de
producción → requiere permiso de quien lo administra antes de agregarla.

**Datos que hay que llevar:** distribuidor · marca · fecha de registro ·
estado (activo / vencido / lo tiene otro) · contacto que lo gestionó.

**Conexión con R4:** el registro es la variable de entrada del descuento.
Sin modelar esto, las reglas de descuento no se pueden ejecutar solas.

---

## R6 — Porcentajes por etapa comercial

**Estado: regla confirmada, valores pendientes.**

El 95% del trabajo de preventa es gobierno. Una misma necesidad produce
dos cotizaciones con precios distintos:

1. **Estudio de mercado** — precios más altos, porque esa información la
   ve todo el mundo y hay que dejar margen para bajarse después.
2. **Oferta de licitación** — precios competitivos, a veces agresivos.

Lo que varía según preventa:

| Concepto | Base del machote (`Equipos`) | Comportamiento real |
|---|---|---|
| Transporte | 10% | Ya no es fijo: se le pide a compras que consulte aduanas/fletes por proyecto. Se han visto 2% y 6% |
| Imprevistos | 3% | Varía poco |
| IVA de línea | 0% | Ver R2 |
| DAI | 15% | Varía por partida |
| Administración | 3% | Baja a 2% o 0% en licitaciones agresivas |
| Margen GV | 27,4% | ~28% base; 30–35% en estudio de mercado; más bajo en la oferta final |

**Base del machote en las otras pestañas:** `MATERIALES` y
`OPEX Proyecto` — Transporte 10%, Seguros 0%, IVA 13%, DAI 14%,
Administración 3%, Margen 30%. `OPEX GV` — Transporte 10%, Imprevistos
3%, IVA 0%, DAI 14%, Administración 3%. `PRODUCTO G` a `PRODUCTO O` —
todo en 0% salvo Administración 3% y Margen 23%.

**Regla de ejecución (decisión de Fabián, 2026-09-18):** los valores del
machote se presentan como **recomendación inicial**, no como verdad.
Antes de armar la cotización se muestran y se pregunta si alguno cambia
para este proyecto. Si el asesor no sabe o dice "los de siempre", se
dejan tal cual.

⚠️ **Trampa verificada:** `OPEX GV!M4` (margen) es la fórmula
`=+Equipos!$N$4`. Cambiar el margen en `Equipos` **mueve también el de
OPEX GV**, sin aviso. `MATERIALES` y `OPEX Proyecto` tienen el suyo
independiente. Hay 18 pestañas con su propia fila de porcentajes —
decir "dos juegos independientes" es incorrecto.

---

## R7 — Tipo de cambio con colchón hacia arriba

**Estado: regla confirmada, fuente exacta pendiente.**

Se toma el tipo de cambio del banco y **se redondea hacia arriba** como
colchón ante variación futura. Ejemplo dado por preventa: con el tipo de
cambio alrededor de 470–480, ella usa 500.

**Regla de ejecución:** consultar el tipo de cambio de venta vigente,
**proponer** el valor redondeado hacia arriba, y que una persona lo
acepte o lo corrija. Nunca escribirlo directo en la pestaña
`Tipo de Cambio` del catálogo.

**Pendiente de confirmar:** si la fuente es el Banco Central o el Banco
de Costa Rica (en la reunión la pregunta mencionaba un banco y la
respuesta fue "el de Costa Rica", que puede ser eco de la pregunta), y
si el redondeo es política de la empresa o criterio de cada asesor.

---

## R8 — Mano de obra: mitad tarifario, mitad estimación

**Estado: regla confirmada, tarifario pendiente.**

No es todo estimación. Hay dos mitades y solo una se automatiza.

**Se automatiza — tarifario fijo por tipo de unidad.** Preventa:
*"por instalación de cámaras se cobran 48 dólares. Por instalación de
postes… al final siempre va a ser lo mismo, independientemente del
proyecto."* También hay tarifa de programación y de capacitación.

**No se automatiza — se pregunta siempre.** Días, cantidad de personas y
complejidad. Los estima el asesor; en proyectos complejos pide apoyo a
operaciones. Puede cambiar en la ejecución (se estimaron 10 días y
duró 12).

**Dónde vive hoy:** pestaña `MANO DE OBRA ` del machote — filas por rol
(configurador, supervisor, project manager, diseño) con hora hombre,
precio por día, días, personas, y un bloque de viáticos
(alimentación / combustible / hospedaje). El total alimenta
`OPEX GV!D6`.

⚠️ Las filas `Instalación de equipos MO`, `Mano de obra contratista` e
`Imprevistos` de `OPEX GV` traen **100** como valor de relleno del
machote. No es un precio real.

**Pestaña `Tarifario Mano de Obra`** en el Excel del catálogo (mismo
criterio que `Tipo de Cambio`): `Concepto` · `Unidad` · `Precio USD` ·
`Aplica a (tipo de equipo)` · `Notas` · `Fecha de actualización` ·
`Confirmado por`. ✅ **Ya existe, creada vacía el 2026-09-18.** Falta
que el equipo comercial la llene.

---

## R9 — Transporte terrestre y combustible

**Estado: mecanismo ya existe en el machote, datos pendientes.**

Preventa lo hace a mano hoy: *"¿cuántos kilómetros hay de aquí a
\[destino]? En otra tabla se mete el kilometraje y te lo jala acá."*

**Verificado en el machote:** la pestaña `Transporte` ya tiene una tabla
de destinos con kilómetros ida y vuelta, un costo por kilómetro y un
cálculo de cantidad de carros y viajes. La celda de combustible de
`MANO DE OBRA ` ya está enlazada por fórmula a esa pestaña. O sea que el
mecanismo existe y lo que falta es la lista completa de destinos y que
el flujo la use.

**Cómo la usa la IA (corregido 2026-09-21).** Hay que separar dos cosas
que la versión anterior de esta regla mezclaba:

- **Los kilómetros son un hecho** y viven en la tabla de la pestaña
  `Transporte` del machote, columna **`Destino / localidad`** (se
  llamaba "Cliente" hasta el 2026-09-21; ver R10 para por qué ese
  nombre estaba mal). Se busca por la ubicación del proyecto. Si el
  destino no está, se pregunta el kilometraje y se ofrece agregarlo —
  nunca se estima una distancia por cuenta propia.
- **La cantidad de viajes, los vehículos y el hospedaje dependen del
  proyecto y SE PREGUNTAN.** La versión anterior decía que con la
  ubicación "se llenan kilómetros y viajes", y eso era un error del mismo
  tipo que el que hizo eliminar la tabla de proporciones (ver R10): un
  dato que varía por obra tratado como si saliera de una tabla.

⚠️ No confundir con el porcentaje `Transporte` de las pestañas de
producto (R6), que es flete internacional de importación. Son dos cosas
distintas con el mismo nombre.

---

## R10 — Materiales de instalación: sí en el catálogo, no en una tabla de proporciones

**Estado: decidido 2026-09-21. La pestaña de proporciones se eliminó.**

Además del equipo principal y de los accesorios de montaje, una
instalación consume **materiales**: tubería conduit, gazas, cable,
conectores, cajas, breakers.

**Lo que SÍ está:** los materiales, como productos del catálogo. Hay
~194 filas de proveedores locales cargadas, y tras la normalización de
categorías quedan bajo `Materiales de instalacion` con subcategorías
`Canalizacion y tuberia`, `Cableado`, `Material electrico` y
`Ferreteria / postes`. Buscarlos y cotizarlos funciona.

**Lo que NO está, a propósito: cuánto lleva cada proyecto.**

Se había diseñado una pestaña `Proporciones Instalacion` para guardar
cuántos metros de tubo o cuántas gazas lleva cada cámara instalada. **Se
construyó y se eliminó el mismo mes**, por decisión de Fabián, y la
razón vale para cualquier tabla futura:

> Una tabla de proporciones convierte **una estimación que depende del
> sitio** en **un número con autoridad de fuente de verdad**. El problema
> no es que el número esté mal hoy: es que mañana nadie lo cuestiona. Un
> tendido superficial y uno empotrado, en el mismo edificio, no llevan
> los mismos metros de tubo — y quien abre el Excel no tiene cómo saber
> que ese "6 metros por cámara" salió de un promedio de un proyecto
> puntual.

Y el error se propaga callado: un precio viejo se detecta porque tiene
fecha; una proporción mal aplicada a 40 cámaras son 240 metros de tubo
cotizados que nadie revisa.

**Regla de ejecución:** la cantidad de material **se pregunta en cada
cotización** (campo 7b de la ficha de `nueva-cotizacion`), es
**opcional** —si el proyecto no los lleva o todavía no se sabe, se deja
en blanco y se sigue— y **nunca se estima por cuenta propia**.

### El criterio general que dejó esta decisión

Antes de guardar un dato como tabla de referencia, preguntarse: **¿es un
hecho, un acuerdo, o una estimación que depende del sitio?**

| | Ejemplo | ¿Tabla? |
|---|---|---|
| **Hecho** | La distancia a una localidad; qué base sirve para qué cámara; el tipo de cambio de hoy | Sí |
| **Acuerdo comercial** | El descuento de una marca, con sus condiciones; la tarifa por instalar una cámara | Sí, con sus condiciones como columnas |
| **Estimación que depende del sitio** | Metros de tubo por cámara; días y personas; **cuántos viajes y cuántos vehículos** | **No.** Se pregunta cada vez |

⚠️ **Cuidado con el ejemplo de los kilómetros, que es el más resbaloso
de los tres.** Una primera versión de esta tabla ponía "kilómetros a un
destino" como caso limpio de hecho, y eso era demasiado cómodo. La
formulación correcta es: **la distancia es un hecho, el viaje no.**
Liberia está a 420 km ida y vuelta se haga el proyecto que se haga —
eso no es criterio de nadie. Pero el costo de transporte es
`viajes × km × vehículos × costo por km`, y de esos cuatro **solo la
distancia sale de la tabla**: los viajes y los vehículos dependen del
proyecto y se preguntan, y el costo por km es una tarifa de la empresa
que cambia con el combustible.

La misma trampa estaba en el propio Excel: la columna de la tabla se
llamaba **"Cliente"** cuando sus valores son localidades (San José,
Cartago, Liberia, Paso Canoas). Ese encabezado invitaba a tratar la
distancia como una propiedad del cliente, cuando un mismo cliente puede
tener obras en lugares distintos. **Se renombró a "Destino / localidad"
el 2026-09-21**, y se agregó debajo de la tabla la nota de que solo la
distancia sale de ahí.

Las pestañas que sobrevivieron a este filtro y por qué: `Tipo de Cambio`
es un hecho fechado; `Compatibilidad de Accesorios` es un hecho físico y
además trae su propia columna de nivel de confianza;
`Reglas de Descuento` es un acuerdo y sus condiciones (registro, monto
mínimo) son columnas; `Tarifario Mano de Obra` lo avaló preventa
textualmente (*"al final siempre va a ser lo mismo, independientemente
del proyecto"*) y lo que sí varía —días y personas— quedó como pregunta.

⚠️ **`Regimen Fiscal Clientes` quedó con una advertencia.** Es la que más
se acerca al problema: una exención puede cambiar por contrato, no solo
por cliente. No se eliminó porque preventa misma la propuso y porque
cobrar mal un impuesto en una licitación es peor — pero está documentada
en el Excel como **valor por defecto que se confirma en cada cotización**,
no como verdad fija.

## R11 — Un solo catálogo, no varios

**Estado: decidida 2026-09-18.**

Se evaluó separar cámaras y monturas de tubería y materiales en archivos
o pestañas distintas. **Se decidió mantener un solo catálogo**, por tres
razones:

1. La regla de no duplicados (`Modelo/SKU + Proveedor`) y la fórmula de
   precio en colones son las mismas para todo. Separar obliga a
   mantener dos veces la misma lógica.
2. Una cotización real mezcla las tres capas. Una sola tabla se filtra
   por `Categoría / tipo`; dos tablas hay que cruzarlas.
3. El equipo ya sabe filtrar una tabla de Excel. Un archivo más es un
   lugar más donde buscar.

### Categorías normalizadas — versión vigente desde 2026-09-21

`Categoría / tipo` tenía **80 valores distintos** para 2.552 filas,
porque heredaba los encabezados de sección de cada PDF: convivían
`Camera - Network` con `IP CAMERAS & NVR's`, `HDD FOR TODAY`, la marca
`INVID` usada como categoría, cinco duraciones de licencia (`3-Year`,
`30-Day`…) y hasta una fila con la categoría literal `Category`.
Filtrar por categoría no servía.

**Hoy son 16 categorías con 64 subcategorías, en dos columnas:**
`Categoria` (D) y `Subcategoria` (E). **Ninguna fila quedó sin
clasificar.**

| Categoría | Filas | | Categoría | Filas |
|---|---|---|---|---|
| Camara | 888 | | Optica | 58 |
| Grabacion y video | 561 | | Audio | 49 |
| Accesorio de instalacion | 407 | | Deteccion de incendio | 42 |
| Software y licencias | 129 | | Almacenamiento | 20 |
| Red y conectividad | 97 | | Alarma e intrusion | 19 |
| Energia | 73 | | Servicios | 2 |
| Control de acceso | 71 | | Equipo de computo | 1 |
| Monitor y visualizacion | 70 | | | |
| Materiales de instalacion | 63 | | | |

El texto original del proveedor **no se perdió**: vive en la columna 25,
`Categoria original del proveedor`, marcada en su propio encabezado como
*referencia, NO filtrar por aquí*. La tabla es `A1:Y2551`.

**Dos filas se borraron en vez de clasificarse:** un encabezado del PDF
que se había colado como producto (`Item Type` / `Item #` /
`Description`) y un **cargo de flete de $6.500** (`FREIGHT CIP`) que
estaba cargado como si fuera un artículo — si alguien lo cotizaba,
metía $6.500 de más.

**Cómo clasificar un catálogo nuevo** (el método, por si hay que
repetirlo):

1. **Las categorías limpias del proveedor se respetan.** Las de Hanwha
   lo son y resolvieron 1.307 filas solas.
2. **Las que son encabezados de sección se resuelven por el NOMBRE del
   producto, nunca por la descripción.** Un primer intento matcheando
   contra la descripción mandó **1.079 cámaras a "Almacenamiento"**,
   porque la descripción de una cámara menciona lente, mount, SD y PoE.
3. **Cuando la sección acierta la categoría pero el nombre no alcanza
   para el detalle**, la sección fija la categoría y las palabras clave
   deciden solo la subcategoría. Esto resolvió de golpe 22 productos de
   incendio que venían abreviados en inglés (`SMK DET`, `CHIMESTROBE`,
   `IDNET ISOLATOR`) sin escribir 22 reglas.

**Cuatro errores que costó encontrar y conviene no repetir:**

- `fire` sin delimitar capturaba **DESFire**, y mandaba lectores de
  tarjeta a detección de incendio.
- Los teclados de alarma caían en "Cableado" porque su propio nombre
  dice *"Teclado Cableado LCD…"*.
- `mount` tiene que evaluarse **después** de detectar cámara: *"Flush
  Mount Dome Camera"* es una cámara, no una montura.
- Las reglas de tipo de producto (`NVR`, `DVR`) van **antes** que las de
  característica: *"Enterprise NVR with Redundant Power Supply"* es un
  NVR, no una fuente de poder.

Script: `scripts/taxonomia.py` (la taxonomía y las reglas) y
`scripts/construir-catalogo-v2.py`.

### Pestañas de onboarding (agregadas 2026-09-21)

El archivo tiene tres pestañas pensadas para alguien que recién entra a
preventa, y el orden importa: **`LEEME` primero**, el `Catalogo`
segundo, y las dos guías al final.

- **`LEEME`** — el punto de entrada: qué hacer según lo que se busque,
  qué hay en cada pestaña (quién la llena y si se edita a mano), y cinco
  reglas de oro.
- **`Guia de columnas`** — qué significa cada columna, **pestaña por
  pestaña**, no solo las del catálogo. Cada bloque es una pestaña
  distinta.
- **`Glosario de categorias`** — categoría, subcategoría, qué incluye,
  un ejemplo real del catálogo y **cómo lo llama el proveedor en sus
  documentos**. Esa última columna es la que explica por qué
  `Camera - Network`, `IP CAMERAS & NVR's` y `AI IP 4MP…` son lo mismo.

Hay además una hoja oculta `_listas` que alimenta el desplegable de
`Categoria`. ⚠️ **No la borres**: una validación de lista escrita en
línea tiene un límite de 255 caracteres y las 16 categorías juntas dan
277, así que Excel rechaza el archivo. Tiene que ser un rango.

---

## R12 — Antigüedad del precio: siempre informar

**Estado: confirmada, con una ambigüedad a resolver.**

Cada vez que se trae un precio del catálogo hay que decir **cuántos días
tiene** ese dato (columna `Fecha de última actualización`), como
información para que el asesor decida si conviene confirmarlo con el
proveedor antes de cotizar.

**Regla de ejecución (2026-09-18):** mostrar siempre el número de días,
aunque sea reciente, y avisar explícitamente cuando pasa el umbral. La
responsabilidad de confirmar el precio vigente es de quien cotiza; la IA
solo informa.

**Umbral: 2 meses.** Cerrado por Fabián el 2026-09-18 (hubo un momento
en que se mencionaron 2 semanas; queda descartado). Pasados los 60 días
desde la "Fecha de última actualización", hay que advertir
explícitamente que conviene reconfirmar el precio con el proveedor antes
de cotizar. Debajo de ese umbral igual se muestran los días.

**Nota:** esto resuelve solo una parte de lo que pidió preventa. Ella
planteó además **consistencia de precio hacia un mismo cliente** — al
mismo cliente recurrente se le cotizó el mismo artículo a precios
distintos con semanas de diferencia. Eso no lo cubre la antigüedad del
catálogo: requiere mirar qué se le cotizó antes a ese cliente. Queda
como pendiente separado, de prioridad baja.

---

## R13 — Financiamiento: siempre preguntar, nunca asumir

**Estado: completo desde 2026-09-21.**

Preventa describió su método manual: numerar cada línea que entra en
financiamiento y copiar el cuadro de costos financieros uno por uno
—29 líneas de equipo y 5 de OPEX en el ejemplo que mostró— *"porque en
las primeras 5 líneas tal vez lo haga bien, pero ya si voy por la línea
15 o 20, me puedo equivocar"*.

El machote lo replica automáticamente con tres piezas:

| Pieza | Qué hace |
|---|---|
| Columna **`Financ.`** (`Equipos!Q`) | El asesor escribe un número entero: el ID del cuadro que financia esa línea |
| Pestaña **`Financiamiento`** | 50 cuadros "CUADRO COSTOS FINANCIEROS" para `Equipos` (más los de `Productos 2`, `MATERIALES` y `OPEX GV`). El cuadro *n* arranca en la fila `3+(n−1)·17` y su cuota mensual está 9 filas más abajo |
| Pestaña **`COTIZACION (Financ)`** | El documento que ve el cliente en modalidad financiada |

### Qué mide cada cuadro: el precio UNITARIO

**Decisión del 2026-09-21, tras ver una cotización financiada real de la
empresa.** El cuadro toma el **precio de venta unitario** de la línea
(`Equipos!O`), no el total:

```
C4 = SUMIF(Equipos!$Q$6:$Q$55, A3, Equipos!$O$6:$O$55)
```

Antes tomaba el total (`$P$`), y eso era un error latente: la cotización
financiada presenta **"Precio Unitario Mensual × Cantidad = Total
Mensual"**, así que si el cuadro ya venía multiplicado por la cantidad,
el monto se contaba dos veces.

⚠️ **Consecuencia: un ID por línea.** Como los cuadros ahora miden un
precio unitario, **no tiene sentido que dos líneas compartan el mismo
ID** — se sumarían dos precios unitarios distintos. Una línea, un
cuadro.

### La pestaña `COTIZACION (Financ)`

Se construyó copiando la lógica de una cotización financiada real de la
empresa. Es **idéntica a `COTIZACIÓN `** salvo en tres cosas:

| | Normal | Financiada |
|---|---|---|
| Encabezados | `Precio U.` / `Total Contado` | `Precio Unitario Mensual` / `Total Mensual` |
| Precio unitario | `=+Equipos!O6` | La cuota del cuadro que le toca **por ID** |
| Etiqueta del total | `TOTAL` | `TOTAL MENSUAL` |

La fórmula del precio unitario busca el cuadro por ID en vez de por
posición fija —que es como lo hace el archivo original de la empresa—
justamente para evitar el error que describió preventa:

```
=IFERROR(IF(Equipos!Q6="","",INDEX(Financiamiento!$C:$C,12+(Equipos!Q6-1)*17)),"")
```

Y la columna del total mensual va blindada, porque una línea sin
financiamiento deja la cuota vacía y `"" × cantidad` da `#¡VALOR!`:

```
=IFERROR(I22*B22,"")
```

### Reglas que no cambian

- **Preguntar siempre, al inicio**, si el proyecto lleva financiamiento.
  No inferirlo del tamaño del proyecto ni de ningún otro criterio.
- Si no lleva, la columna `Financ.` queda **vacía** y no se toca nada de
  esas pestañas. Un solo machote para los dos casos.
- La pestaña `PTMO` es una calculadora de amortización de uso general:
  el asesor escribe a mano el monto, la tasa y el plazo que quiera
  detallar. No está conectada a un cuadro puntual.

## R14 — Capacidad de líneas

**Estado: resuelto el 2026-09-18.** Las cotizaciones reales son de 28 a
50 líneas o más; el machote llegaba a 14, y la pestaña que ve el cliente
a 5.

**Estructura vigente del machote** (los números de fila cambiaron, hay
que usar estos):

| Pestaña | Capacidad | Filas de datos | Totales |
|---|---|---|---|
| `Equipos` | **50 líneas** | 6 a 55 | Total FOB `F57`, Costo Nac. `M57`, Total Venta `P57`, Utilidad `P58` |
| `COTIZACIÓN ` | **50 líneas** | 22 a 71 | SUBTOTAL `J74`, IMPUESTO `J75`, TOTAL `J76` |
| `Financiamiento` | **50 cuadros** para `Equipos` | cuadro *n* en la fila `3 + (n−1)·17`; el 50 en la 836 | — |

La lista `si`/`no` de la validación de `IMPORTADO` se movió a
`Equipos!B61:B62`.

**Cómo se hizo, por si hay que repetirlo en otra pestaña:** se
insertaron filas **dentro** de los rangos existentes (no debajo), para
que Excel expandiera solo los `SUM`, los `SUMIF` y las validaciones. En
`Equipos` se insertaron 36 filas en la 19 y se copiaron las fórmulas de
la fila 18; en `COTIZACIÓN ` se insertaron 45 filas en la 26 y se copió
la fila 25, cuyas referencias relativas a `Equipos` se ajustan solas. Es
cirugía estructural sobre un archivo con imágenes incrustadas, así que
va **por Excel COM, nunca con openpyxl**. Verificado antes y después:
14 imágenes y 38 pestañas intactas, cero celdas en error.

**Pendiente menor:** el resto de las pestañas de producto
(`Productos 2-5`, `MATERIALES`, `OPEX GV`, `OPEX Proyecto`) conserva su
capacidad original. Ampliarlas sigue el mismo procedimiento, pero
todavía no hizo falta.

---

## ⚠️ R15 — La ruta de la carpeta compartida (corregido 2026-09-18, crítico)

**Hay dos carpetas locales con el mismo contenido y el mismo nombre, y
solo UNA sincroniza con SharePoint.** Trabajar en la equivocada
significa que nada de lo que se haga llega al equipo.

| | Ruta | ¿Sincroniza? |
|---|---|---|
| ❌ **NO usar** | `C:\Users\<usuario>\GRUPO VISION - DYNAMIC\Info Costa Rica - CLIENTES\` | **No.** Copia local huérfana de una configuración vieja |
| ✅ **La buena** | `C:\Users\<usuario>\OneDrive - GRUPO VISION - DYNAMIC\Accesos directos\Archivos de Info Costa Rica - CLIENTES\` | Sí |

Las dos tienen las mismas 287 carpetas de cliente, así que **no se
distinguen mirándolas**. Cómo verificar cuál es cuál, en orden:

1. **Registro de Windows** — `HKCU:\Software\Microsoft\OneDrive\Accounts\Business1`,
   valor `UserFolder`. Lo que devuelve es la **única** raíz que OneDrive
   sincroniza. Hoy devuelve `C:\Users\<usuario>\OneDrive - GRUPO VISION - DYNAMIC`.
   Todo lo que esté fuera de esa raíz **no sincroniza**, por más que se
   llame igual.
2. **Placeholders de nube** — en la carpeta sincronizada la mayoría de
   los archivos tienen el atributo `ReparsePoint` (son archivos "solo en
   la nube" hasta que se abren). En la huérfana **ningún** archivo lo
   tiene. Se mide con `Get-Item -Force | Select Attributes`; en una
   muestra de 400 archivos dio 391 contra 0.
3. **`desktop.ini`** — la carpeta sincronizada tiene uno que apunta al
   icono de OneDrive. La huérfana no tiene ninguno.

⚠️ **Ojo con el criterio viejo.** Las notas decían que una carpeta
sincronizada se reconoce porque *la carpeta* tiene `ReparsePoint`. Eso
ya no discrimina: hoy el atributo aparece en los **archivos** que están
solo en la nube, y una carpeta sincronizada con todo descargado se ve
igual que una local. **Usar el registro como prueba principal.**

**Cómo pasó.** La biblioteca se sincronizaba antes en
`GRUPO VISION - DYNAMIC\...`. En algún momento esa configuración se
reemplazó por un acceso directo dentro del OneDrive personal, y la
carpeta vieja quedó en disco con todo su contenido, sin conexión con la
nube. Es **la misma trampa** que ya había pasado en agosto con la
carpeta `GV_IA_Automation/`, que nunca llegó a ser visible para los
compañeros.

**Consecuencia concreta detectada el 2026-09-18:** el catálogo de la
carpeta huérfana tenía 2.552 filas y 8 pestañas; el de la carpeta
sincronizada (lo que el equipo ve en SharePoint) tenía 2.358 filas y 4
pestañas, con fecha del 14 de setiembre. Los 194 productos de
proveedores locales —tubos, gazas, conectores, cajas, cerraduras,
detección de incendio— y las pestañas de reglas **nunca habían llegado
al equipo**. Se verificó que la nube no tenía **ningún** SKU que la
local no tuviera, así que copiar la local sobre la sincronizada no
pierde nada.

**Regla de ejecución:** antes de leer o escribir cualquier cosa en
`CLIENTES/`, resolver la ruta por el registro. Nunca escribir una ruta
de `CLIENTES` a mano en un skill ni asumir la de una sesión anterior.

### Qué se hizo el 2026-09-18 (con autorización de Fabián)

1. **Catálogo migrado.** Se copió el catálogo bueno (2.552 filas, 8
   pestañas) desde la carpeta huérfana a la sincronizada, reemplazando
   la versión del 14 de setiembre. Verificado en destino: 2.552 filas,
   las 8 pestañas, 945 precios especiales, ninguno en cero,
   `TablaCatalogo` en `A1:W2553`, los nombres definidos
   `TipoCambioCompra`/`TipoCambioVenta`, la fórmula de colones y el
   panel congelado en `A2`. Sin copias de conflicto.
2. **La carpeta huérfana NO se pudo renombrar.** Windows devuelve
   "Acceso denegado" aunque el usuario tiene control total: OneDrive
   sigue teniendo esa raíz registrada a nivel de shell (tiene su propio
   `desktop.ini` con el icono de OneDrive) y su driver bloquea el
   renombrado. **Si hace falta renombrarla, hay que cerrar OneDrive
   primero** — quedó pendiente, no es bloqueante.
3. **En su lugar se marcó el contenido**: el catálogo de la carpeta
   huérfana se renombró a
   `_NO_USAR_Catalogo (copia local sin sincronizar, migrado 2026-09-18).xlsx`
   y se dejó un `_LEEME_NO_USAR.txt` explicando cuál es la carpeta
   buena y cómo verificarlo.

### Alcance: esto es un problema de una sola máquina

Confirmado por Fabián: **OneDrive se comporta raro solo en su equipo**,
desde el inicio. En las máquinas de los compañeros no hay razón para
esperar dos árboles duplicados. Para ellos, `verificar-entorno` solo
tiene que confirmar que la cuenta de la empresa está conectada a
OneDrive y que la carpeta se lee. Lo que sí aplica en toda máquina es
**resolver la ruta por el registro en vez de asumirla**.

---

## Reglas de higiene que aplican a todo

- **Nunca escribir un número que no confirmó una persona.** Ante un dato
  faltante se pregunta; no se rellena.
- **Nunca tocar una columna de fórmula** de las pestañas de producto.
  Solo se escriben las columnas de entrada.
- **Nunca sobrescribir una fila que el asesor ya llenó** sin mostrarle
  antes exactamente qué cambia y esperar confirmación.
- **Nunca dejar una celda en `#REF!` ni un costo en `0`.** Un cero en
  costo unitario produce una línea gratis sin ningún error visible.
- **Ningún dato real de cliente, precio negociado o margen de un
  proyecto puntual entra a un archivo versionado en git.** Este
  documento usa ejemplos genéricos a propósito.

---

## Estado de las reglas de un vistazo

| | Regla | Estado | Bloquea |
|---|---|---|---|
| R1 | Importado = quién nos vende | Confirmada, corregir skill | — |
| R2 | Dos IVA distintos | Confirmada | — |
| R3 | Régimen fiscal por cliente | Pestaña creada, falta llenarla | Cotizar a gobierno sin error |
| R4 | Costo real de GV | Pestaña creada, **faltan las reglas** | **Todo el cálculo** |
| R5 | Registro de proyecto | Falta el mecanismo | R4 |
| R6 | Porcentajes por etapa | Faltan los rangos | — |
| R7 | Tipo de cambio | Falta confirmar la fuente | — |
| R8 | Mano de obra | Pestaña creada, falta llenarla | Cotizar instalación |
| R9 | Transporte terrestre | Faltan los destinos | — |
| R10 | Materiales de instalación | Catálogo listo; la cantidad se pregunta, sin tabla | — |
| R11 | Un solo catálogo, categorías normalizadas | **Vigente en producción desde 2026-09-21** | — |
| R12 | Antigüedad del precio | Cerrada: 2 meses | — |
| R13 | Financiamiento | **Completo: cuadros + cotización financiada** | — |
| R14 | Capacidad de líneas | **Resuelta: 50 líneas** | — |
| R15 | Ruta real de la carpeta compartida | **Corregida, falta migrar el catálogo** | Que el equipo vea el trabajo |

Lo que hace falta pedirle al equipo comercial está en
[`pendientes-comercial.md`](pendientes-comercial.md). Cómo se verifica
cada regla está en [`pruebas-validacion.md`](pruebas-validacion.md).
