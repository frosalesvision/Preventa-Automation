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

## Índice: todas las reglas de un vistazo

Actualizado el 2026-09-28. **De dónde sale** dice si la regla la dijo
preventa, si sale de medir las cotizaciones reales, o si la decidió
Fabián. Las que salen de medir están pendientes de que preventa las
apruebe.

| | Regla, en una línea | De dónde sale | Estado |
|---|---|---|---|
| R1 | `IMPORTADO` = a quién se le compra, no dónde se fabrica. Con `no`, transporte y DAI quedan en cero | preventa; verificado en cotizaciones | vigente |
| R1.1 | Una línea de flete va como `no` importada | medido: 728 líneas, el 91% así | vigente |
| R2 | Hay dos IVA: el de línea (un costo nuestro) y el impuesto al cliente | preventa | vigente |
| R3 | El impuesto al cliente depende del cliente: se pregunta, con 13% recomendado | preventa; medido: 873 cotizaciones, 29% exentas | vigente, tabla de 46 clientes |
| R4 | El costo recomendado es el **precio de compra de GV** (dealer, o lista menos el descuento del proveedor), no el MSRP. Se pregunta una vez por cotización con cuál se arma | medido: 94 de 134 líneas, ninguna con MSRP; la pregunta, Fabián | vigente |
| R5 | Sin registro de proyecto no aplica el descuento mayor | preventa | concepto vigente, falta el mecanismo |
| R6 | No hay tabla de porcentajes; los del machote son los más usados, y el margen se mueve según el tipo | preventa; medido: 499 matrices | vigente |
| R7 | Tipo de cambio: por defecto el de la pestaña del catálogo; en cada cotización se confirma o se cambia | preventa y Fabián | vigente |
| R8 | Mano de obra: valores por defecto medidos, en el machote, editables en cada cotización | medido: 184 matrices | vigente |
| R9 | Transporte: km × viajes × carros × costo por km, ya en el machote | preventa; verificado | vigente |
| R10 | Materiales de instalación: en el catálogo; la cantidad se pregunta, no se estima | decidido y confirmado | vigente |
| R11 | Un solo catálogo, con categorías normalizadas | decidido | vigente |
| R12 | Se avisa si el precio tiene más de 2 meses | Fabián | vigente |
| R13 | Financiamiento: siempre preguntar | preventa | vigente |
| R14 | Hasta 50 líneas por cotización | medido | vigente |
| R15 | Modelo de precios: los precios se cargan tal cual y el `Precio de compra GV` se calcula solo, con el dealer o con la pestaña `Descuentos por proveedor` | medido y decidido | vigente desde 2026-09-28 |
| R16 | Solo dólares; otra moneda la convierte quien cotiza | Fabián | vigente |
| R17 | La primera corrida apunta a quedar bien; el Excel siempre se corrige a mano | Fabián | principio de diseño |
| R18 | Marca exacta o equivalente: lo decide el asesor | Fabián; caso patrón #5 | vigente |
| R19 | Los accesorios que nadie pide se sugieren con su %, nunca se agregan solos | medido: 666 cotizaciones | vigente |
| R20 | La ruta de la carpeta compartida se resuelve por el registro, nunca se asume | incidente del 2026-09-18 | vigente |

Lo que se le está pidiendo a preventa y a contabilidad está en
[`pendientes-comercial.md`](pendientes-comercial.md). Cómo se verifica
cada regla está en [`pruebas-validacion.md`](pruebas-validacion.md).

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

**Verificado sobre una cotización real el 2026-09-24** (caso patrón #4):
en sus 12 líneas marcadas como nacionales, transporte y DAI quedaron en
cero y los otros tres porcentajes se aplicaron igual. Hasta entonces la
regla estaba leída de las fórmulas del machote; ahora está confirmada
sobre líneas que alguien cotizó de verdad.

### R1.1 — Una línea de flete va como nacional

**Medida el 2026-09-24 sobre 728 líneas de flete en las 1.119 matrices.**

Cuando el proveedor cotiza el **flete como un artículo más** de su lista
—pasa seguido—, esa línea entra a la matriz como cualquier otra. Si se
marca `IMPORTADO = si`, recibe encima el 10% de transporte: se le cobra
transporte al transporte.

| | Líneas | |
|---|---|---|
| con el 10% aplicado encima | 63 | **8,7%** |
| sin transporte encima | 665 | **91,3%** |

**No es una política, es un descuido.** Nueve de cada diez veces la línea
va marcada como nacional, que es lo correcto: el flete es un servicio
contratado, no una mercancía que se importa y se nacionaliza.

**Regla:** una línea cuya descripción empieza por transporte, flete,
envío, courier, carga aérea, logística, nacionalización, desalmacenaje o
aduana se marca `IMPORTADO = no`. Si el asesor la quiere importada, que
sea a propósito.

Lo aplica `armar-cotizacion` al escribir las líneas.

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

**Estado: RESUELTA el 2026-09-22.** Llegaron los datos y ya están
cargados en la pestaña `Regimen Fiscal Clientes` del catálogo, que desde
el 2026-10-06 se llama **`Clientes`** y trae también los datos de cada
cliente (ver "La pestaña Clientes", abajo).

> **Lo que contestó preventa:** hay una institución de seguridad social
> exenta; **dos universidades públicas llevan únicamente 2%**, no 13%; y
> los clientes de zona franca **varían caso por caso** — algunos
> exonerados y otros no, hay que confirmarlo por cliente y nunca asumir.
>
> Sobre el 3% de administración: *"eso nosotros lo dejamos o no lo
> cobramos dependiendo de qué tan competitivos queramos ser"*. **No es
> una característica del cliente**, así que esa columna queda vacía a
> propósito y la decisión se toma al armar cada cotización. No intentes
> modelarla.

(Los nombres concretos están en el catálogo, que es archivo interno de
la empresa. No se copian a este repositorio.)

No todos los clientes pagan lo mismo. Casos que dio preventa
(genéricos a propósito, sin nombrar instituciones en este archivo):

- Una institución de gobierno: se le cobra impuesto completo.
- Una municipalidad: no se le cobra impuesto sobre el equipo importado.
- Una universidad pública: se le cobró **2%**, no 13%.
- El 3% de administración: a unos clientes se les carga y a otros no.

**Diseño acordado con Fabián (2026-09-18):** dos niveles, no uno.

1. **Tabla maestra** en el Excel del catálogo, pestaña `Clientes`
   (hasta el 2026-10-06, `Regimen Fiscal Clientes`), con la misma lógica
   que `Tipo de Cambio`: dato de referencia que el equipo mantiene a mano.
   Columnas del impuesto, A a F: `Cliente` · `Exento de impuesto (si/no)` ·
   `% impuesto al cliente` · `% administración` · `Notas` ·
   `Fecha de actualización`. Las columnas G a P son los datos del
   cliente (ver abajo).
   ✅ Creada vacía el 2026-09-18, cargada el 2026-09-24 y ampliada el
   2026-10-06.
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

⚠️ **Lo que esto NO resuelve:** la pestaña `Clientes` tiene 247
clientes, casi todos con el impuesto derivado de las cotizaciones (82
con una sola cotización, sin confirmar, y 31 sin el dato), pero un
cliente nuevo no está, y 38 cambian de tasa según el proyecto. La
fórmula garantiza que *si se escribe, se respeta* — no que alguien lo
sepa. Por eso el impuesto se pregunta siempre.

### La pestaña Clientes (2026-10-06)

**Pedido de preventa, por medio de Fabián:** tener a mano los datos de
cada cliente (nombre, cédula o cédula jurídica, contacto, teléfono,
correo, dirección, asesor, lo que se le cotizó y si es exento de IVA)
sin tener que ir carpeta por carpeta a buscarlos.

**Dónde vive: en el catálogo, y solo ahí.** Fabián lo decidió así: la
pestaña de régimen fiscal pasó a llamarse `Clientes` y se le agregaron
columnas, en vez de crear otro archivo. Es el Excel al que todo el
equipo ya tiene acceso, y **preventa lo abre y lo corrige ahí, no en
ningún otro archivo**. El plugin trabaja sobre el mismo.

Una primera carga se hizo en la pestaña `Cliente` de
`BD Proveedores - Clientes.xltm`, la agenda de preventa, porque sus
columnas eran las del pedido. Se revirtió el mismo día: el archivo quedó
idéntico a como lo dejó preventa, y desde entonces es de **solo
lectura** (se consulta o se toma de referencia, nunca se escribe).

| Columnas | Qué traen |
|---|---|
| A a F | El impuesto, igual que antes. **No se movieron**: el plugin las lee |
| G | Cédula / cédula jurídica |
| H a K | Contacto, teléfono, correo y dirección |
| L | Asesor comercial |
| M | Ventas: **vacía**, la llena preventa (no hay de dónde sacarla, ver abajo) |
| N y O | Lo que se le cotizó y la fecha de la última cotización |
| P | De dónde salió cada dato |

**De dónde salieron los datos.** De las matrices de cotización desde
2024 (el encabezado de la pestaña de cotización trae nombre, atención,
dirección, teléfono y correo), de las órdenes de servicio y del control
de cotizaciones de preventa. Cuando un cliente tiene varias, manda la
más reciente. Las cédulas jurídicas son solo las que salieron rápido y
seguras: las de órdenes de compra y las de instituciones públicas, que
se tomaron de la consulta pública de Hacienda (`api.hacienda.go.cr/fe/ae`)
recorriendo los rangos donde están las municipalidades, las instituciones
autónomas y los ministerios, y cruzando por nombre oficial. **Las cédulas
de personas físicas no se buscan** (decisión de Fabián), y las de
empresas privadas quedan para que preventa las complete.

**Ventas no se pudo llenar.** Ninguna fuente dice qué cotización se
ganó: el control de cotizaciones no tiene una columna de estado y solo
hay órdenes de compra de unos pocos clientes. Se dejó la columna para
que preventa la llene al cerrar una venta.

**Los nombres y los datos de los clientes no se copian a este
repositorio**: viven en el catálogo, que es archivo interno.

---

## R4 — El costo sale del precio Dealer, no del MSRP

**Estado: MEDIDA el 2026-09-24 sobre 1.119 matrices y 57.607 líneas de
equipo. Reemplaza lo que esta regla decía desde el 2026-09-22.**

De las 134 líneas que se pudieron comparar contra las dos columnas de
precio del catálogo:

| El `Costo Unit` coincide con | Líneas | |
|---|---|---|
| **el precio Dealer** | **94** | **70,1%** |
| **el MSRP** | **0** | **0,0%** |
| los dos (valen igual) | 5 | 3,7% |
| ninguno de los dos | 35 | 26,1% |

**Cero.** Y las 35 que no pegan con ninguno tampoco se acercan al MSRP:
son todas más baratas, mediana 0,37×, y varias quedan por debajo del
propio Dealer.

**El MSRP es donde el precio al cliente aterriza, no de donde arranca.**
En la cotización ganada del caso patrón #3, el costo fue el nivel
*Dealer Program* y el precio final al cliente quedó cerca del MSRP. Si
el MSRP se escribe en `Costo Unit` y encima se le aplica la cadena, la
cotización sale cerca del **doble**.

### La tensión con lo que dijo preventa, que no se borra

Preventa había contestado el 2026-09-22 que el descuento *"varía
dependiendo de la marca, tipo de equipo y qué nivel de partners
somos"*, y propuso **usar siempre los MSRP** aplicando el descuento a
mano, porque *"aunque esto sea un proceso manual, es rápido"*. Y que
cuando el proyecto se registra *"el proveedor nos manda directamente los
precios ya con el descuento"*.

Lo que se midió no coincide con eso. Las dos lecturas posibles:

1. Describieron el **precio al cliente** (que sí aterriza cerca del
   MSRP) y se entendió como la casilla de costo.
2. La práctica real difiere de la práctica declarada.

La primera explica los datos sin que nadie se haya equivocado, y encaja
con que el precio final del caso patrón quedó al 92% del MSRP en la
línea principal.

### Cómo se decide en cada cotización (Fabián, 2026-09-28)

Primero dijo: *"se toma el precio dealer siempre, si por alguna razón
ese precio no está en nuestro catálogo se toma el precio default"*. Ese
es el **default recomendado**. Y después, para no imponerlo: el plugin
pregunta **una sola vez por cotización** —no por línea— si arma con el
precio con descuento de GV o con el precio de lista (MSRP), mostrando
los descuentos que aplican a los productos elegidos, con su estado
(confirmado, medido o sin registrar). Si el asesor elige el de lista, se
hace y se le dice que el precio al cliente sale alrededor de 1,85 veces
el MSRP (R4.1).

### Lo que de verdad limitaba, y cómo quedó

Más importante que "Dealer o MSRP": de 2.524 productos, solo **945**
tenían las dos columnas, y los 945 eran de **un mismo proveedor**. Para
los otros **1.579** había un solo número y no se sabía de qué tipo era.

**Resuelto el 2026-09-28** (ver R15): el precio de compra dejó de ser un
dato que alguien tiene que conseguir y pasó a calcularse. Para los
productos sin precio dealer, sale del **precio de lista menos el
descuento del proveedor**, anotado en la pestaña `Descuentos por
proveedor`. Se midió proveedor por proveedor:

- **ISTC, Seguritronic y Security Doctors:** su único precio ya es el de
  compra (mediana 1,00 entre el costo usado y el precio cargado). Van con
  0%.
- **Hanwha:** su lista trae solo el MSRP y una casilla para que cada
  distribuidor reste su descuento. El descuento se midió en las
  cotizaciones reales y en las de Anixter, por tipo de equipo, y se
  aplica desde el 2026-09-28 con estado `MEDIDO: FALTA CONFIRMAR`
  (decisión de Fabián: *"apliquémoslos tal cual la data que
  recolectamos"*). Los porcentajes viven en la pestaña, no acá: son una
  condición comercial.
- **El resto** no tiene fila todavía: se cotiza con su precio tal cual y
  la cotización avisa que no se sabe si ya trae descuento.

La pestaña `Reglas de Descuento` que había antes nunca se llenó y se
eliminó el 2026-09-28. La diferencia con la nueva es que **esta está
conectada**: el precio de compra se calcula con ella.

### R4.1 — Lo que el MSRP como costo le hace al precio final

**Medido el 2026-09-23. CONFIRMADO el 2026-09-24** por la medición sobre
las 1.119 matrices: esto dejó de ser una hipótesis.

Hay que separar dos cosas que suenan iguales:

- **Cotizar "con MSRP"** = escribir el MSRP en la columna `Costo Unit`
  de `Equipos`. Es la base sobre la que la matriz calcula.
- **Cotizarle al cliente "a MSRP"** = que el precio que ve el cliente
  *sea* el MSRP.

**La matriz hace lo primero, no lo segundo.** Sobre el `Costo Unit` le
suma transporte, imprevistos, DAI, administración y margen. Medido sobre
una cámara importada con los porcentajes de fábrica:

| Se escribe en `Costo Unit` | Precio de venta unitario | Factor |
|---|---|---|
| $135 (nivel Dealer) | $249,55 | 1,85× |
| **$270 (MSRP)** | **$499,11** | **1,85×** |

Desglose del caso del MSRP: costo 270 → transporte 27 → imprevistos 8,91
→ DAI 45,89 → **costo nacionalizado 351,80** → administración 10,55 →
margen 136,75 → **precio de venta 499,11**.

O sea: **con el MSRP como costo, el cliente ve 1,85 veces el MSRP.**

Eso es coherente con lo que dijo preventa —los precios de lista son para
cotizaciones *base*, y el descuento entra después si el proceso avanza—
y es conservador: nunca se cotiza por debajo del costo. Pero conviene
que lo confirmen, porque si un competidor cotiza cerca del MSRP, una
oferta base a 1,85× queda fuera de rango.

⚠️ **Y una limitación que hay que tener presente:** mientras el costo
real de Grupo Visión no viva en ningún lado, **la matriz no puede decir
cuál es el margen real**. Calcula el margen sobre un costo que no es el
nuestro. El número de "utilidad" de la matriz es, hoy, una utilidad
teórica sobre precio de lista.

Lo que sigue abajo queda como registro de cómo se entendía antes. Es el
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

**Dónde iban a vivir las reglas** *(nunca se llenó; la pestaña se
eliminó el 2026-09-28)*: pestaña `Reglas de Descuento` del
Excel del catálogo — `Proveedor` · `Marca` ·
`Familia / categoría (vacío = toda la marca)` · `% de descuento` ·
`Requiere registro de proyecto (si/no)` · `Monto mínimo de compra (USD)`
· `Nivel de precio base` · `Notas` · `Fecha` · `Confirmado por`. Una
marca puede tener varias filas. ✅ **Ya existe, creada vacía el
2026-09-18.** El cálculo del descuento **no se guarda en el catálogo**:
se resuelve al momento de cotizar y va al "Costo Unit" de esa cotización
puntual.

### R4.4 — Qué hacer mientras no haya reglas

> Decisión de Fabián (2026-09-18): *"Si un proveedor no le hace
> descuentos a Grupo Visión por X razón, o no tenemos las reglas
> cargadas para ese proveedor, use directamente el precio registrado."*

- Si **hay** una regla de descuento aplicable → calcular con ella.
- Si **no hay** regla → usar el precio del catálogo tal cual, diciendo
  explícitamente que es precio de lista sin descuento.
- **Nunca** inventar un porcentaje ni aplicar el de otra marca.

### R4.2 — Cuál de los tres niveles de precio usamos (RESUELTO)

**Resuelto el 2026-09-22.** Preventa lo contestó en dos palabras:
*"Utilizamos siempre los precios MSRP."*

Vale la pena dejar escrito cómo se llegó ahí, porque la pregunta empezó
mucho más vaga:

1. Se vio en el PDF del distribuidor que publica **tres** columnas:
   `Dealer Program`, `DEAL` y `MSRP`, con más de 3× entre la más baja y
   la más alta.
2. Midiendo las 945 filas del catálogo que tenían precio especial
   cargado se descubrió que **669 son exactamente el MSRP dividido entre
   dos** y 202 son **iguales al MSRP** (software, licencias y accesorios
   de una línea). Filas de los dos tipos conviven en las mismas páginas,
   así que no era un error de carga: lo que teníamos cargado era el
   nivel **Dealer Program**, que es MSRP−50% en hardware y 0% en
   software.
3. Eso convirtió la pregunta de *"¿cuál de tres?"* en *"¿compramos al
   Dealer Program o al DEAL intermedio?"* — mucho más fácil de contestar.
4. La respuesta de preventa fue: ninguno de los dos para cotizar, **se
   cotiza con el MSRP** y el descuento lo aplican ellos a mano.

**Y el punto 4 se cayó el 2026-09-24.** Al medir las 1.119 matrices
resultó que el `Costo Unit` es el **Dealer Program** en el 70% de las
líneas comparables y el MSRP en **ninguna**. Ver R4, que es la regla
vigente. Lo que sigue en pie de esta sección es el punto 2: lo que el
catálogo tiene cargado es el nivel Dealer Program, MSRP−50% en hardware
y 0% en software.

**Dos moralejas, y la segunda salió cara:**

1. **Medir primero y preguntar después.** La versión medible de la
   pregunta se contestó en una línea; la vaga llevaba semanas abierta.
2. **Una respuesta clara no es una respuesta verificada.** *"Utilizamos
   siempre los precios MSRP"* se dio por resuelta sin contrastarla
   contra una sola cotización real, y estuvo dos días en las reglas
   diciendo lo contrario de lo que hacen las 1.119 matrices. Lo que
   contesta el equipo es una hipótesis con buena fuente, no un hecho:
   se escribe como regla cuando los documentos la respaldan.

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

**Estado: RESUELTA el 2026-09-22 — no hay valores que cargar.**

> **Lo que contestó preventa:** *"jugamos con muchos márgenes
> diferentes, no tenemos nada establecido"*. A veces desde estudio de
> mercado van muy baratos y con otros clientes suben el margen, y
> depende mucho de la magnitud del proyecto. *"Este cálculo o decisión
> de margen también nos toca valorarlo de manera variable y manual."*

**No hay tabla escrita, pero el comportamiento SÍ tiene patrón**
(medido el 2026-09-23 sobre las cotizaciones reales de 2026).

### Lo que dicen las 499 matrices de 2025 y 2026

Se leyeron las 649 matrices de los dos años (`scripts/analizar-matrices.py`);
**499 tenían la fila de porcentajes legible** (317 de 2025, 182 de 2026).
Las que faltan no se pudieron bajar de OneDrive.

| Tipo de cotización | n | Movieron el margen | Mediana de las que movieron | Rango |
|---|---|---|---|---|
| **Estudio de mercado** | 6 | **100%** | **35%** | 35–42% |
| **Licitación** | 15 | **80%** | **23%** | 20,8–30% |
| Mantenimiento | 9 | 33% | 25% | 25–29% |
| Otro / privado | 346 | 34% | 30% | 8–40% |

**El patrón aguantó al duplicar la muestra.** Licitación pasó de 7 a 15
casos y siguió igual: el 80% mueve el margen, mediana 23%. Estudio de
mercado sigue en 100% con 6 casos — pocos, pero *todos* lo mueven, y
siempre hacia arriba.

> licitación ~23%  <  privado ~27%  <  estudio de mercado ~35%

### El DAI cambió entre 2025 y 2026

Esto salió al separar los años, y es un dato duro:

| Año | DAI dominante | En cuántas |
|---|---|---|
| 2025 | **14%** | 307 de 312 (98%) |
| 2026 | **15%** | 136 de 182 (75%), con 14% en otro 18% |

2025 fue casi monolítico en 14%. 2026 se movió a 15% con una cola de
transición.

**Decisión de Fabián (2026-09-23): se deja como lo trae el machote de
2026** — 15% en `Equipos`, 14% en `MATERIALES` — y no se pregunta nada.
Si en algún proyecto corresponde otro, se cambia en el Excel.

### Lo que dicen las 182 matrices de 2026

Se leyeron las 249 matrices de 2026 de la carpeta compartida
(`scripts/analizar-matrices.py`); 182 tenían la fila de porcentajes
legible. Preventa tenía razón en que no hay nada *establecido*, y aun
así hacen casi siempre lo mismo:

| Porcentaje | Valor dominante | En cuántas |
|---|---|---|
| Transporte | **10%** | 93% |
| DAI | **15%** (y 14% en otro 18%) | 75% |
| Imprevistos | **3%** | 76% |
| Administración | **3%** | 76% |
| IVA de línea | **0%** | 73% |
| Margen GV | **27,4%** | 59% |

**El margen es el que de verdad se mueve: el 41% de las cotizaciones lo
cambió.** Y no lo cambian al azar — lo cambian según el tipo:

| Tipo de cotización | n | Cuántas movieron el margen | Mediana de las que movieron | Rango |
|---|---|---|---|---|
| **Estudio de mercado** | 4 | **100%** | **35%** | 35–42% |
| **Licitación** | 7 | **86%** | **23%** | 22–24% |
| Mantenimiento | 7 | 43% | 25% | 25–29% |
| Otro / privado | 117 | 40% | 25,2% | 8–38% |

**El orden es claro y tiene sentido de negocio:**

> licitación ~23%  <  privado ~27%  <  estudio de mercado ~35%

En una licitación se compite por precio, así que aprietan. Un estudio de
mercado es un precio de referencia sin compromiso, así que van holgados.

⚠️ **Con qué confianza.** Las muestras de licitación (7) y estudio de
mercado (4) son chicas: sirven para orientar, no para fijar una regla.
Lo que sí es sólido es que **el 100% de los estudios de mercado y el 86%
de las licitaciones movieron el margen a propósito** — eso no es ruido,
es una decisión deliberada y repetida. El bloque "otro / privado" es un
cajón: incluye todo lo que el clasificador no pudo tipificar, y su
mediana de 27,4% refleja en parte a quien simplemente no tocó el default.

### Qué hacer con esto

**No convertirlo en una tabla que decida sola.** Sigue siendo criterio
del asesor. Pero la ficha puede dejar de preguntar a ciegas: si el tipo
de cotización es estudio de mercado, proponer ~35% en vez de 27,4%; si
es licitación, proponer ~23%. Mostrando siempre de dónde sale el número
y dejando que lo cambien.

Es la diferencia entre *"¿qué margen querés?"* y *"en estudios de
mercado el equipo suele usar 35%, ¿lo dejamos ahí?"*.

### Una pista de por qué el margen varía tanto (sin probar)

Al leer el pliego del caso más atípico del censo —una compra de tarjetas
con margen 20%, imprevistos 0% y administración 0%— apareció que era una
**licitación reducida de un commodity, sin instalación**, y que el
documento **publicaba el presupuesto disponible**:

| | Monto |
|---|---|
| Presupuesto publicado | ₡2.084.380 |
| Total de la oferta | ₡2.019.571 |
| | **96,9% del techo** |

Eso sugiere que en licitación **el margen no se elige, se deduce**: se
parte del precio al que se quiere llegar y el margen sale de ahí. Si
fuera cierto explicaría todo el rango de 8% a 42% sin necesidad de
ninguna tabla.

⚠️ **Está sin probar, y hay que decirlo así.** Se intentó verificar sobre
los 28 pares pliego↔matriz disponibles
(`scripts/probar-hipotesis-presupuesto.py`) y **solo uno** dio los dos
números comparables — y ese salió en **108%**, o sea *por encima* del
presupuesto. La extracción falla porque los pliegos escriben el
presupuesto de muchas formas distintas, a veces dentro de tablas, y las
matrices viejas tienen estructuras heterogéneas.

**Entonces: un caso a favor, un caso en contra, 26 sin medir.**

**Cerrado el 2026-09-23 sin preguntarlo.** No tiene sentido llevarle al
equipo comercial una pregunta que nosotros mismos no pudimos verificar:
les costaría tiempo contestar algo que igual no podríamos contrastar.

Queda acá como **observación**, no como regla ni como pregunta abierta,
por si algún día aparece una razón nueva para retomarla. El script
`scripts/probar-hipotesis-presupuesto.py` sigue en el repositorio con su
limitación documentada.

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

## R7 — Tipo de cambio: por defecto el del catálogo, y se confirma en cada cotización

**Estado: decidida por Fabián el 2026-09-28.** Reemplaza la versión del
2026-09-23, que pedía preguntar compra y venta desde cero en cada
cotización.

> *"el tipo de cambio se toma por default de la pestaña de catálogo, tipo
> de cambio, pero aun así consulta algo tipo 'en la pestaña de catálogo
> tenemos el tipo de cambio X, ¿seguimos utilizándolo o cambiás el tipo de
> cambio para este proyecto en específico?'"*

**Cómo funciona:**

1. **El valor por defecto es el de la pestaña `Tipo de Cambio` del
   catálogo**: `B3` compra, `B4` venta.
2. Al armar cada cotización, el sistema **lo propone y pregunta** si se
   mantiene o se cambia para ese proyecto.
3. Lo que se elija queda **en esa cotización**. Desde una cotización la
   pestaña del catálogo no se toca: la actualiza el equipo cuando
   corresponde.
4. **Si la pestaña está vacía, el sistema pregunta cuál usar.** Al
   2026-09-28 lo está.

**Por qué así.** Preventa había dicho que es política de cada proyecto:

> *"Podemos manejarlos al tipo de cambio del banco central al precio de
> venta."* Y Fabián: *"a veces se usa el monto del BCCR, o a veces se
> sube un poco hacia arriba para beneficiar a la empresa."* Ejemplo de
> preventa: con el tipo de cambio alrededor de 470–480, usa 500.

Un valor por defecto compartido evita escribirlo cada vez, y la pregunta
deja la decisión por proyecto donde estaba. Nunca se toma en silencio.

---

## R8 — Mano de obra: mitad tarifario, mitad estimación

**Estado: vigente. Decidido el 2026-09-28: no se arma un tarifario
aparte.** Los valores por defecto —medidos sobre las cotizaciones de 2025 y
2026— viven en la pestaña `MANO DE OBRA` del machote y se cambian desde el
Excel en cada cotización, como se hizo siempre. La pestaña `Tarifario
Mano de Obra` del catálogo, que estaba vacía, se eliminó ese día.

Lo que sigue es la historia de cómo se llegó ahí.

> **Lo que contestó preventa:** *"eso aún no lo tenemos 100%
> establecido. Tengo anotado un par de precios base por instalaciones
> pero de hecho tenemos la tarea de elaborar un cuadro de instalaciones,
> con costos estandarizados."*

**No es que no contestaran: es que no existe todavía.** Tienen la tarea
pendiente de armarlo. Hasta entonces la pestaña `MANO DE OBRA` se llena
a mano en cada cotización, y no hay que insistirles: hay que esperar a
que lo construyan.

### Pero en las matrices hay números, y hay que leerlos con cuidado

Medido el 2026-09-23 sobre 184 matrices de 2026 con datos de mano de
obra:

| Dato | Valor | Frecuencia |
|---|---|---|
| Hora hombre | **$8,90** | 183 de 184 (99%) |
| Precio por día | **$48,00** | 183 de 184 (99%) |
| Alimentación | **$12,00** | 116 de 128 (91%) |
| Costo por kilómetro | **$0,60** | 182 de 182 (100%) |

⚠️ **Un valor que aparece en el 99% de los archivos NO prueba que sea una
tarifa acordada.** El machote trae `$8,90` y `$48` escritos a mano en la
fila del Configurador. Si nadie los toca, se ven en todas las matrices
aunque no representen ninguna decisión. Y hay una pista fuerte de que es
justo eso: **$8,90 × 8 horas = $71,20, pero el precio por día dice
$48,00.** Los dos valores del propio machote no son consistentes entre
sí — y el único archivo que muestra $71,20 es aquel donde alguien dejó
que la fórmula calculara.

### Corregido al sumar 2025: la conclusión era demasiado amplia

La primera lectura (solo 2026) decía que *todos* esos números eran
defaults heredados. Con los dos años, **hay que separar**:

**Sí son defaults que nadie toca:**

| Dato | 2025 | 2026 |
|---|---|---|
| Hora hombre $8,90 | 337 de 339 (99%) | 183 de 184 (99%) |
| Costo por km $0,60 | 316 de 317 (99%) | 182 de 182 (100%) |

**No: estos sí se editan.**

| Dato | Variación real |
|---|---|
| Alimentación | $12 domina, pero hay $30 (×17), $20, $11, $16, $14… en 42 de 288 casos en 2025 |
| Hospedaje | 2025: $100 (×34), $85 (×8), $200 (×3), $60. 2026: $60, $100, $55, $50, $45 |

Y el **precio por día tiene dos valores compitiendo**, que es más grave
que un default olvidado:

| Valor | 2025 | 2026 |
|---|---|---|
| **$48,00** (escrito a mano) | 252 (74%) | 183 (99%) |
| **$71,20** (= $8,90 × 8, calculado) | **79 (23%)** | 1 |

**En 2025, casi una de cada cuatro matrices usó $71,20** — o sea la
fórmula calculando — y en 2026 eso casi desapareció. No es que nadie
haya decidido: es que **alguien reemplazó la fórmula por un 48 fijo y
esa versión se propagó.** Los dos números están en circulación y
difieren un 48%.

**Cerrado el 2026-09-23: el machote usa el valor más común de las
cotizaciones reales como default, y se puede cambiar a mano.**

| Dato | Default | De dónde sale |
|---|---|---|
| Hora hombre | **$8,90** | 99% de 496 matrices |
| Precio por día | **$48** | Confirmado por Fabián y por preventa |
| Alimentación | **$12** por día y persona | 88% de los casos |
| Costo por kilómetro | **$0,60** | 99% de los casos |
| Hospedaje | **0** | Es el valor más común: el 88% no lo cobra |
| Tarifa de hospedaje cuando aplica | **$100** la noche | 37 de 58 casos |

Están anotados en la propia pestaña `MANO DE OBRA` para que se vean sin
abrir ningún documento.

**Sobre el $48:** Katherine lo había dicho
así, y el `$71,20` calculado queda descartado. El `48` escrito a mano en
el machote es correcto, no un error — lo que pasó es que reemplazó a una
fórmula que daba otro número, y eso explica los 79 casos de 2025.

**Como todos los valores del machote, es un default y no una imposición:**
quien cotiza puede cambiarlo en el Excel cuando el trabajo lo amerite.

**La prueba que sigue sirviendo:** un número que varía es una decisión;
uno idéntico en el 99% de los archivos es una celda que nadie tocó. Lo
que cambió es a cuáles se aplica.

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

~~**Pestaña `Tarifario Mano de Obra`** en el Excel del catálogo.~~
**Eliminada el 2026-09-28.** Se había creado vacía el 2026-09-18 para que
el equipo la llenara. Nunca se llenó, y dejó de tener sentido cuando los
valores por defecto quedaron fijados en el machote, donde se editan.

---

## R9 — Transporte terrestre y combustible

**Estado: RESUELTA el 2026-09-22 — ya estaba resuelto en el machote.**

> **Lo que contestó preventa:** *"En la matriz, en la hoja de mano de
> obra es donde calculamos la parte de kilometraje, viáticos y
> hospedaje, esa parte creo que sí la tenemos automatizada en la misma
> matriz."*

Verificado y es cierto: `Transporte` calcula
`kms × viajes × carros × costo por km`, y `MANO DE OBRA` toma el
combustible de ahí con `=Transporte!I3`. La cadena funciona.

**Pero al verificarlo aparecieron dos cosas** (2026-09-22):

1. **Un error real, ya corregido.** El total de viáticos era
   `=(H5*E5*F5)+(I5*E5)+((J5*E5)-1)`. Ese `-1` **restaba un dólar
   siempre**: en el machote en blanco el total daba −$1,00. No hay regla
   de negocio que reste exactamente un dólar. Quitado.
2. **Dos fórmulas distintas para lo mismo. Unificadas el 2026-09-23.**
   La fila 5 calculaba `(H*E*F)+(I*E)+(J*E)` y las filas 6 a 8
   `((H+I+J)*E)*F`. Con dos técnicos y tres días daban **$256,80 y
   $441,60 por el mismo viaje**.

   Se unificó en la lógica de la **fila 5**, porque es la que de verdad
   se usa: en las 496 matrices con datos de mano de obra, la fila del
   Configurador es la que se llena. La diferencia está en que el
   combustible y el hospedaje **no** se multiplican por personas — van
   en el mismo carro, y si se quedan, la cantidad de habitaciones se
   pone a mano en la columna.

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

**Estado: decidido 2026-09-21 y CONFIRMADO POR EL NEGOCIO el 2026-09-22.**

> **Lo que contestó preventa cuando se les pidió la tabla de
> proporciones:** *"eso varía totalmente. A como puede instalarse una
> cámara a 5 metros de distancia del grabador, pueden ser 70, 80 mts…
> no tenemos forma de estandarizarlo, cada cámara lleva diferentes
> distancias. Esto es una de las cosas que sí o sí nos toca sacar
> manualmente."*

La decisión se había tomado por criterio —que una tabla le daría a una
estimación la autoridad de una fuente de verdad— y el negocio llegó a la
misma conclusión por su cuenta. **No reabrir esto.** Se eliminaron tres
versiones de esa misma tabla (`Proporciones Instalacion`, `calc mat`, y
la petición al equipo); si aparece una cuarta, es el mismo error.

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

*(Esas dos últimas se eliminaron el 2026-09-28: la de descuentos nunca se
usó —R4— y la del tarifario dejó de tener sentido cuando los valores por
defecto se fijaron en el machote —R8—.)*

⚠️ **`Regimen Fiscal Clientes` (hoy `Clientes`) quedó con una advertencia.** Es la que más
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

## ⚠️ R20 — La ruta de la carpeta compartida (corregido 2026-09-18, crítico)

> Hasta el 2026-09-25 esta regla se numeraba **R15**. Se renumeró porque
> el 2026-09-24 se le asignó ese número, por error, al modelo de precios,
> que ya está citado en skills y scripts.

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

## R15 — Modelo de precios: se carga lo que dice la lista, y el precio de compra se calcula

**Estado: definida el 2026-09-24, después de medir. Rehecha el
2026-09-28 a pedido de Fabián:** *"no debes cambiar el precio que
tenemos en el catálogo por el precio con descuento"*, y que el precio de
compra sea *"una fórmula que tome el precio normal y le haga la fórmula
con el descuento"*, con los descuentos en una pestaña aparte.

Cada proveedor publica sus precios como se le antoja. Uno trae tres
niveles (`Dealer Program`, `DEAL`, `MSRP`), otro trae dos, la mayoría
trae uno solo. El descuento que nos aplican *"varía dependiendo de la
marca, tipo de equipo y qué nivel de partners somos"*, y averiguarlo es
manual. Cargar eso tal cual, cada proveedor con su estructura, vuelve el
catálogo inservible para automatizar.

**La cotización necesita un número por producto: el costo.** El catálogo
lo calcula en vez de pedírselo a alguien.

### Las columnas de precio (desde el 2026-09-28)

| Col. | Columna | Qué es | ¿Dato o fórmula? |
|---|---|---|---|
| 7 | `Precio de lista del proveedor (USD)` | el precio que trae la lista, tal cual (en Hanwha e InVid, el MSRP). **Nunca se reemplaza por el precio con descuento** | dato |
| 9 | `Precio de compra GV (USD)` | **lo que Grupo Visión paga** | **fórmula** |
| 11 | `Precio dealer (USD)` | el precio para distribuidores, si la lista lo trae aparte; o el costo de una cotización real | dato |
| 12 | `Descuento del proveedor` | el que corresponde a esa fila, buscado en la pestaña `Descuentos por proveedor` | fórmula |
| 28 | `Tipo de precio cargado` | qué trae la fuente: `LISTA Y DEALER`, `UN SOLO PRECIO EN LA LISTA`, `SOLO PRECIO PUBLICO (MSRP)` o `COSTO DE UNA COTIZACION REAL` | dato |

```
Precio de compra GV  =  Precio dealer                          si la fila lo tiene
                        Precio de lista × (1 − descuento)      si no
```

**La regla al cargar un proveedor nuevo, sin importar cuántos niveles
publique:**

1. El **precio de lista** va a la columna 7, tal cual.
2. Si la lista trae un **precio dealer** (el más bajo al que GV compra de
   verdad), va a la columna 11.
3. Los niveles intermedios **no se cargan**: no se usan para cotizar y
   solo agregan ruido.
4. Si no hay dealer, el **descuento del proveedor** se anota en la
   pestaña `Descuentos por proveedor`: una fila por proveedor, y si hace
   falta por marca y por tipo de equipo (gana la más específica). Si su
   precio ya es el de compra, va con 0%.
5. `Tipo de precio cargado` dice qué trajo la fuente.

### Qué hace la cotización con esto

Pregunta **una vez por cotización** si arma con el precio de compra de GV
(recomendado) o con el de lista, mostrando los descuentos que aplican y
su estado (R4). Y en la entrega marca, línea por línea, lo que no esté
confirmado:

| El descuento de la fila… | Qué se dice |
|---|---|
| viene del precio dealer | nada |
| está `CONFIRMADO POR PREVENTA` | nada |
| es `MEDIDO: FALTA CONFIRMAR` | que es medido y falta que preventa lo confirme |
| dice `PENDIENTE` o está vacío | que el costo es el precio de lista tal cual y el real puede ser menor |

⚠️ **El descuento es lo que se resta, no lo que se paga.** El
2026-09-28 se cargaron los de Hanwha al revés (lo que se paga en vez del
descuento) y el precio de compra quedó más alto que el real. Desde
entonces la pestaña muestra al lado `Se paga (% de la lista)`.

### Para qué sirve entonces el precio de lista

Para **revisar el resultado**. El precio al cliente sale de la cadena
(costo + transporte + DAI + administración + margen), no del MSRP. Pero
si el número que sale queda muy por encima del precio público, el cliente
lo puede googlear. Ese contraste es el uso real de la columna de lista:
**un chequeo de cordura al final, no una entrada al principio.**

Medido en el caso patrón #3, el precio final quedó entre el 92% y el 157%
del MSRP según la línea. Así que no es un techo, pero sí un aviso.

### Estado del dato hoy (2026-09-28)

| `Tipo de precio cargado` | Filas | De dónde sale su precio de compra |
|---|---|---|
| `SOLO PRECIO PUBLICO (MSRP)` | 1.381 | del descuento medido de Hanwha, por tipo de equipo |
| `LISTA Y DEALER` | 743 | del precio dealer de InVid |
| `UN SOLO PRECIO EN LA LISTA` | 382 | 202 de InVid con su dealer; 89 con 0% (ISTC, Seguritronic, Security Doctors y 3 de InVid); 91 de proveedores sin descuento registrado, que la cotización avisa |
| `COSTO DE UNA COTIZACION REAL` | 35 | del costo de esa cotización |

Y el catálogo es **92% dos proveedores** (2.329 de 2.524 filas). El caso
patrón #4 mostró lo que eso cuesta: de 10 equipos de un proyecto real,
**cero** estaban cargados. Ampliar la cobertura pesa hoy más que
cualquier ajuste de fórmula.

---

## R16 — Solo dólares. Las otras monedas las convierte quien cotiza

**Estado: decidida por Fabián el 2026-09-24.**

Toda la cadena trabaja en **dólares**, y de ahí a colones con el tipo de
cambio de venta. **No se manejan otras monedas.**

Esto salió del caso patrón #4, donde dos proveedores europeos cotizaron
en euros y la matriz entró los montos ya convertidos. Se podría haber
deducido una regla de conversión, pero la decisión fue **no hacerlo**:

> *"las reglas de euros ignóralas por completo, solo trabajamos en
> dólares, si ellos quieren euros que lo transformen ellos."*

Es la decisión correcta y conviene entender por qué: una tasa de cambio
metida en el plugin envejece sola y nadie se entera. El día que el euro
se mueva, las cotizaciones saldrían mal sin que nada falle — la misma
clase de error silencioso que el precio en colones corrido.

**Si una lista de proveedor viene en otra moneda**, el asesor la convierte
y carga dólares. Si le pide al plugin cotizar en euros, la respuesta es
que no, y por qué.

---

## R17 — La primera corrida apunta a quedar bien; el Excel siempre se puede corregir

**Estado: principio de diseño, fijado por Fabián el 2026-09-24.**

> *"lo ideal de esta automatización es que quede lo mejor posible desde
> la primera corrida pero como es un Excel siempre se va a poder
> modificar a mano en caso de ser necesario."*

Esto ordena las decisiones cuando no hay certeza, y vale para todo el
plugin:

- **Ningún valor se deja en blanco esperando que alguien lo llene.** Se
  pone el default medido sobre las cotizaciones reales, y se dice que es
  un default.
- **Ningún default se escribe como fórmula fija.** Todos viven en celdas
  que el equipo puede cambiar sin tocar nada más.
- **Cuando el plugin no está seguro, cotiza igual y lo dice.** Entregar
  una cotización con tres avisos es más útil que no entregar nada.
- **Lo que el plugin no sabe hacer, lo deja señalado en el Excel**, no en
  un mensaje de chat que se pierde.

La medida de éxito no es que el plugin acierte solo: es **cuántas celdas
tiene que tocar el asesor después**, y que sepa exactamente cuáles.

---

## R18 — Marca exacta o equivalente: lo decide el asesor, no el plugin

**Estado: fijada por Fabián el 2026-09-25, a partir del caso patrón #5.**

Una solicitud puede tener **varias cotizaciones válidas**. En el caso #5
el cliente pidió Edwards y el propio equipo armó dos: la Edwards que se
envió y una alternativa Kidde con el equipo a menos de la mitad del
costo. Ninguna de las dos estaba mal.

> *"en ocasiones depende del presupuesto o si el cliente no le importa se
> cambian las marcas de lo solicitado, en otras ocasiones no."*

Lo que decide no está en el documento del cliente. Por eso:

1. **Se pregunta al inicio**, en `nueva-cotizacion`: el mismo modelo,
   un equivalente, o las dos.
2. **Nunca se sustituye en silencio.** Si el asesor pidió el modelo
   exacto y no está en el catálogo, se dice; no se ofrece otro.
3. **Licitación con marca amarrada: nunca equivalente** (caso #2).
4. **Validar el plugin exige lo mismo:** un equivalente funcional cuenta
   como acierto, porque el equipo mismo cotiza alternativas. Se compara
   contra **todas** las versiones guardadas de la cotización, no contra
   la última.

---

## R19 — Los accesorios que nadie pide se sugieren, nunca se agregan solos

**Estado: medida el 2026-09-25 sobre 666 cotizaciones.**

> Fabián: *"un sistema de detección no funciona sin alimentación [...]
> es parte de accesorios de montaje en todo caso."*

Hay accesorios que el cliente no pide porque se dan por sabidos: la
fuente de poder de un panel, la batería de respaldo, la base del
detector, el disco del NVR. En el caso patrón #5 aparecieron **9 fuentes
de poder** que no estaban en la solicitud, en las dos versiones.

Se midió qué acompaña a cada equipo principal
(`scripts/medir-accesorios-requeridos.py`):

| Cuando trae… | Acompañante | % |
|---|---|---|
| Panel de incendio | batería de respaldo | 61% |
| Panel de incendio | base de detector | 61% |
| Panel de incendio | módulo aislador | 54% |
| Panel de incendio | fuente de poder | 41% |
| NVR | disco duro | 55% |
| NVR | switch | 48% |
| Cerradura magnética | fuente de poder | 44% |
| Cerradura magnética | botón de salida | 42% |
| Controladora de acceso | gabinete / rack | 52% |
| Cámara | gabinete / rack | 41% |

**Ninguno llega al 70%.** O el accesorio viene incluido en otra línea, o
el cliente ya lo tiene, o a veces se olvida: desde afuera no se
distingue. Por eso:

1. **Se sugiere con su número y se pregunta.** Nunca se agrega solo: un
   accesorio inventado es peor que uno que falta y se pregunta.
2. **Vive en la pestaña `Accesorios Requeridos` del catálogo**, separada
   de `Compatibilidad de Accesorios`. Son preguntas distintas —qué
   *sirve* contra qué *hace falta*— y la de compatibilidad la regenera un
   script que borraría cualquier cosa agregada a mano.
3. **Tiene que estar en el catálogo para poder sugerirse.** Gabinetes y
   racks no están: no existe la subcategoría, y son el acompañante más
   común de las cámaras.

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

Está en el [índice al principio de este documento](#índice-todas-las-reglas-de-un-vistazo).
Hasta el 2026-09-25 había acá una tabla del 2026-09-18 que nadie
actualizó: decía que a R4 le faltaban las reglas y que R6 no tenía
rangos, lo contrario de lo que dicen hoy las propias reglas. Se sacó
para que no la lea nadie como vigente.
