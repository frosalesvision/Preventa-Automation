---
name: armar-cotizacion
description: Organiza los archivos y carpetas de una cotización de preventa dentro de la carpeta compartida del cliente (crear la carpeta "Cotización #N-AAAA <descripción>" con sus subcarpetas estándar, copiar el machote de matriz oficial, proponer numeración de carpeta y número de oferta, manejar versionado de nombres de archivo), y llenar la pestaña Equipos de esa matriz con el equipo/accesorios que se hayan encontrado (ej. vía `buscar-equipo`) — modelo, descripción, cantidad y costo unitario; las fórmulas de margen/precio de venta del machote calculan el resto solas, nunca se tocan a mano ni se inventan. En una cotización nueva la matriz se llena primero como borrador fuera de CLIENTES y se muestra la tabla de montos para que el asesor la acepte o la rechace; con el sí se crea la carpeta y se copia el borrador. También registra la cotización en los dos Excels de control compartidos ("Control de cotizaciones 2026.xlsx" y "Cotizaciones en Preventa.xlsx") cuando están sincronizados localmente. Usar cuando el usuario pide crear/organizar la carpeta de una cotización nueva, agregar una versión a una cotización existente, pide el siguiente número de "Cotización #N" u oferta para un cliente, pide cargar el equipo ya encontrado a la matriz, o pide registrar/anotar la cotización en el control de ofertas.
---

# Armar cotización

**Alcance (no cambiar sin confirmar con el usuario):** este skill
organiza **archivos y carpetas** en `CLIENTES/<Cliente>/.../Cotización
#N-AAAA <descripción>/`, y además **escribe líneas de equipo** (modelo,
descripción, cantidad, costo unitario) en la pestaña `Equipos` de la
matriz — **actualizado 2026-09-01: ya no está prohibido escribir en la
matriz** (la regla anterior de "nunca leer ni escribir" se eliminó por
decisión explícita del usuario). Lo que sigue firme:

- **Nunca se tocan las columnas de fórmula** (todo lo que calcula
  transporte/imprevistos/IVA/DAI/administración/margen/precio de venta)
  — esas quedan tal cual las trae el machote, calculando solas a partir
  de lo que se escribe en las columnas de entrada. Este skill nunca
  decide ni escribe un porcentaje de margen ni una fórmula.
- **Nunca se sobrescribe una fila que el asesor ya llenó a mano** en una
  cotización real en curso sin mostrarle antes exactamente qué se va a
  cambiar y esperar confirmación explícita — esto sigue siendo dinero
  real de un cliente real.
- Al crear una cotización **nueva**, el machote recién copiado está en
  blanco (solo fórmulas fijas, sin datos) — ahí sí se puede escribir
  equipo directamente, siempre mostrando la propuesta completa antes de
  guardar.

⚠️ La carpeta `CLIENTES/` es la carpeta de producción real de la
empresa, no un entorno de prueba. Antes de crear, renombrar o escribir
cualquier carpeta/archivo ahí, mostrale al asesor exactamente qué vas a
hacer (ruta completa, o la tabla de filas a escribir) y esperá
confirmación explícita.

⚠️ **Cómo escribir en el machote y en los dos Excels de control —
crítico, encontrado 2026-09-14:** estos tres archivos tienen imágenes y
dibujos reales incrustados (el logo/membrete de la matriz; imágenes y
comentarios en los Excels de control). **Escribir con `openpyxl` y
llamar `.save()` los destruye en silencio** — openpyxl lo advierte
("DrawingML support is incomplete... Shapes and drawings will be lost")
y se confirmó en la práctica: un archivo de prueba escrito con openpyxl
en la sesión anterior perdió un dibujo y una imagen que el machote
original sí tenía, sin ningún error visible. **Usar siempre Excel real
por automatización COM** (`New-Object -ComObject Excel.Application` en
PowerShell — abrir el libro, escribir con `.Cells.Item(fila,col).Value2`,
`.Save()`, `.Close()`, `.Quit()`, liberar los objetos COM) — nunca
`openpyxl` con `.save()` en estos tres archivos. `openpyxl` sigue
sirviendo para **leer** (no daña nada al solo leer) y para verificar
después de escribir con COM.

Ver [`docs/notas-proceso.md`](../../../docs/notas-proceso.md) para la
estructura de carpetas confirmada y las reglas de numeración/versionado.

## Caso 1: cotización nueva

⚠️ **El orden, desde el 2026-10-28 (regla R25 de
[`docs/reglas-negocio.md`](../../../docs/reglas-negocio.md)):** primero
se **calcula** todo (pasos 1 a 4 y 6) y la matriz se llena como
**borrador fuera de `CLIENTES`** (paso 7, en `%TEMP%\preventa-borrador\`).
Con [`scripts/vista_previa_montos.py`](scripts/vista_previa_montos.py)
se le muestra al asesor la tabla de montos, y junto a ella la carpeta, el
número de oferta, los nombres de la matriz y del PDF y las filas de
control. **Esa vista previa es la confirmación que piden los pasos de
abajo**: con un solo sí se crea la carpeta (paso 5), se copia el borrador
tal cual a `Matriz-Oferta/`, se registra en los dos Excels de control, se
genera el PDF en esa misma carpeta (`generar-pdf-cotizacion`) y se
entregan el PDF a la vista y el borrador del correo
(`seguimiento-correo`). Si la rechaza, se corrige el borrador y se vuelve
a mostrar. El flujo completo está en `nueva-cotizacion`, pasos 6 a 8.

1. **Ubicar al cliente.** Buscá la carpeta `CLIENTES/<Cliente>/`. Si no
   existe (cliente nuevo), confirmá el nombre exacto con el asesor antes
   de crear nada.
2. **Carpeta de año:**
   - Si el cliente ya tiene cotizaciones previas, mirá qué patrón usa
     (`<Cliente> -AAAA`, `Cotizaciones AAAA`, o plano sin carpeta de
     año) y **seguí ese mismo patrón** para el año actual.
   - Si el cliente es completamente nuevo (sin cotizaciones previas),
     usá `Cotizaciones AAAA` — es la convención unificada a partir de
     ahora.
3. **Número de "Cotización #N":** clientes distintos usan convenciones
   distintas — algunos numeran continuo entre años (ej. 2024 llega a
   #28, 2025 sigue en #28-63, 2026 sigue en #64+), otros reinician cada
   año (2025 tiene #1, 2026 vuelve a empezar en #1). Calculá **ambos**
   candidatos: el máximo N dentro de la carpeta del año actual +1, y el
   máximo N en todos los años del cliente +1. Si coinciden, proponé ese
   número. **Si difieren, mostrale los dos al asesor y preguntá cuál
   convención sigue este cliente** — no asumas una de las dos. En
   cualquier caso, esperá confirmación antes de crear la carpeta.
4. **Descripción corta:** preguntale al asesor la descripción breve que
   va en el nombre de la carpeta (ej. "mantenimiento control de acceso").

   ⚠️ **Antes de pedirla, calculá cuántos caracteres caben, y decí el
   número** (corregido 2026-09-22 — H-4). Windows y Excel no abren
   archivos con ruta de más de **259 caracteres**, y la versión anterior
   de este paso solo decía "pedile una descripción más corta" sin decir
   *cuánto*, que es justo el dato que el asesor necesita.

   El cálculo, para ese cliente concreto:

   1. Armá las rutas más profundas que va a tener la cotización: el
      machote en `…/Matriz-Oferta/Matriz <Cliente> <DD-MM-AAAA>.xlsx`,
      la carpeta `…/Implementacion/Documentación del proyecto` y el PDF
      `…/Matriz-Oferta/<número de oferta> <descripción corta>.pdf`. El PDF
      es el que más se olvida: el 2026-10-27 la carpeta y la matriz cabían
      (242) y el nombre de PDF propuesto llegaba a 263; se acortó la
      descripción del PDF a tres palabras (248).
   2. Desde el 2026-10-19 la descripción aparece **una sola vez** (en la
      carpeta); el nombre del archivo lleva el del cliente, que también
      cuenta como fijo.
   3. `máximo de la descripción = 259 − (todo lo fijo)`, con la más
      larga de las dos rutas.
   4. Decíselo así: *"para este cliente la descripción puede tener hasta
      N caracteres"*. Si N es muy chico, proponé vos dos o tres opciones
      que quepan en vez de hacerlo adivinar.

   **No es un caso raro.** Medido sobre los 286 clientes reales de la
   carpeta compartida: **83 (el 29%) solo admiten 20 caracteres o
   menos**, y el de nombre más largo —una institución pública con razón
   social completa y siglas, 62 caracteres— admite **1 solo carácter**.
   Con esos clientes hay que negociar el nombre, no pedir "algo más
   corto".

   Y verificá el resultado: después de crear la carpeta, medí la ruta
   real del machote y confirmá que quedó bajo 259.
5. **Crear la carpeta** `Cotización #N-AAAA <descripción>/` con las 5
   subcarpetas estándar:
   ```
   Cotizaciones/
   Fichas Técnicas/
   Implementacion/
   ├── Actas de entrega/
   ├── Boletas de servicio/
   ├── Documentación del proyecto/
   └── Mantenimiento/
   Matriz-Oferta/
   Visita técnica/
   ```
   Todas vacías, **excepto `Matriz-Oferta/`**: ahí copiá
   `references/Machote Matriz y oferta.xlsx` (nunca lo edites en
   `references/`, es la copia maestra), renombrado como **`Matriz
   <Cliente> <DD-MM-AAAA>.xlsx`** dentro de la nueva carpeta
   `Matriz-Oferta/` (Fabián, 2026-10-19: *"que los nombres tengan el
   nombre de la empresa que se le va a cotizar y fecha"*). Ejemplo:
   `Matriz Empresa Ejemplo 19-10-2026.xlsx`; una versión nueva agrega ` V2`.
   La fecha es la del día en que se arma. Antes era `Matriz y oferta
   <descripción>.xlsx`: las cotizaciones viejas quedan como están.

   (Hubo un segundo machote, `MCV_PLANTILLA_v8.xlsx`, para proyectos
   grandes multi-sitio — se descartó porque su último uso real
   confirmado es de 2022-2023, no forma parte de la práctica actual del
   equipo. No reintroducirlo por asunción.)
6. **Número de oferta real** (formato `T{prefijo}-{7 dígitos}-{año}`,
   el que va en el nombre del PDF final dentro de `Matriz-Oferta/`):
   - **No se conoce la regla que determina el prefijo** (`T1` vs `T4`
     vs `T5`) — ni siquiera el equipo de preventa la conoce; puede venir
     de Bitrix24 (categoría/pipeline) u otro sistema. No inventes una
     regla.
   - Revisá el Excel maestro (o las carpetas del cliente) para ver qué
     prefijo se usó más recientemente para ese cliente (o en general si
     es cliente nuevo) y proponé ese prefijo + el siguiente consecutivo
     de 7 dígitos disponible para el año actual.
   - **Cómo se arma, medido el 2026-10-19 en `Control de cotizaciones
     2026`** (falta que preventa lo confirme en palabras, pero los datos
     son claros):
     - **Los 7 dígitos son el número de cotización del cliente**, el de su
       carpeta `Cotización #N`: no es un consecutivo de la empresa. El
       mismo `…0000020-26` aparece en tres clientes distintos, y en un
       cliente 5 de 5 coinciden con su carpeta.
     - **El prefijo es el asesor de preventa: `T4` Katherine, `T5`
       Alessandro.** De 136 ofertas de 2026 de Katherine, 134 son T4; de
       102 de Alessandro, 94 son T5.

     Así que se propone `T<prefijo del asesor>-<N con 7 dígitos>-<año>`, y
     se dice de dónde sale cada parte. El primer caso real lo confirmó:
     se propuso `T4-0000020-26` y así se envió.
   - Mostrale la propuesta completa al asesor y **esperá que la
     confirme o la corrija** — nunca lo uses para nombrar un archivo sin
     esa confirmación explícita.
7. **Llenar la pestaña `Equipos` con el equipo cotizado (agregado
   2026-09-01).** Si ya se encontró equipo en esta conversación (ej. con
   [`buscar-equipo`](../buscar-equipo/SKILL.md)) o el asesor ya tiene una
   lista de equipo + accesorios + cantidades para esta cotización,
   ofrecé escribirla ahora en la matriz recién copiada. Si todavía no
   hay ninguna lista, preguntale al asesor si quiere armarla ahora (usando
   `buscar-equipo`) o dejar la pestaña en blanco para llenarla después a
   mano — las dos son válidas.

   **Capacidad y estructura (ampliada 2026-09-18, regla R14):** la
   pestaña `Equipos` admite **50 líneas, en las filas 6 a 55**, con los
   totales en la fila **57** (`F57` Total FOB, `M57` Costo
   nacionalizado, `P57` Total Venta) y la utilidad en `P58`. La pestaña
   `COTIZACIÓN ` espeja esas 50 líneas en sus filas **22 a 71**
   (SUBTOTAL `J74`, IMPUESTO `J75`, TOTAL `J76`). Antes eran 14 y 5
   respectivamente — si ves esos números en algún lado, están
   desactualizados.

   Cada fila de datos tiene estas columnas de **entrada** (las únicas
   que se escriben):
   - **B (Description):** Marca + Modelo + descripción del catálogo (ej.
     `PAR-P8PTZXIR32NH-AI - 8 Megapixel IP Plug & Play, Outdoor PTZ...`)
     — así queda igual de legible que en las cotizaciones reales.
   - **C (IMPORTADO):** `"si"` o `"no"`. **Significa si Grupo Visión
     compra ese ítem fuera del país — NO el país donde se fabrica**
     (regla R1 de [`docs/reglas-negocio.md`](../../../docs/reglas-negocio.md),
     corregida 2026-09-18). Se deriva del **proveedor** de la línea: si
     el proveedor está en Costa Rica → `"no"`; si está afuera → `"si"`.
     Cuando el catálogo trae una columna tipo "Precio Nacional"
     (`SI`/`NO`), esa mapea directo. **Confirmalo siempre con el asesor
     antes de guardar.**

     ⚠️ Una versión anterior de este skill decía inferirlo del "País de
     origen" del catálogo. **Eso era incorrecto**: una cámara fabricada
     en Corea comprada a un distribuidor local no es importación para
     Grupo Visión, y marcarla mal le suma transporte y DAI que no
     corresponden. El impacto está medido: sobre un costo de $100 × 10
     unidades con los porcentajes de fábrica, la diferencia entre `"si"`
     y `"no"` es de **$387,24 (26,5%)** — y Excel no muestra ningún
     error. Ver la prueba P-02 en
     [`docs/pruebas-validacion.md`](../../../docs/pruebas-validacion.md).
   - **D (Qty):** la cantidad que pide el proyecto — nunca la sabe
     `buscar-equipo` por su cuenta (busca qué equipo cumple la
     especificación, no cuántas unidades hacen falta), así que
     preguntale al asesor si no la tenés ya de la especificación del
     cliente.
   - **E (Costo Unit):** el precio que el asesor eligió para esta
     cotización (se pregunta una sola vez, al confirmar el equipo; ver
     [`buscar-equipo`](../buscar-equipo/SKILL.md), "El precio con que se
     arma la cotización"). Por defecto y recomendado: el **precio de
     compra** del catálogo (columna 9, `Precio de compra GV (USD)`), lo
     que Grupo Visión le paga al proveedor. Si el asesor pidió precio de
     lista: la columna 7. Es la base sobre la que el machote calcula
     transporte, impuestos, margen y precio de venta.

     ⚠️ **Por qué se recomienda el precio de compra y no el de lista.**
     Medido sobre 1.119 matrices reales: de las 134 líneas comparables,
     94 usan el Dealer y **cero** el MSRP. El MSRP es donde el precio al
     cliente *aterriza*, no de donde arranca; escrito acá, la cotización
     sale cerca del **doble** (ver R4). Si el asesor igual lo pide, se
     hace y se dice en la entrega.

     La columna 9 es una fórmula del catálogo: el precio dealer si la
     fila lo tiene, y si no, el precio de lista menos el descuento del
     proveedor (columna 12, que sale de la pestaña `Descuentos por
     proveedor`). Copiá su valor; no lo recalcules. **Decí en la entrega
     cuáles líneas llevan un descuento no confirmado**: medido (Hanwha,
     por ahora), `PENDIENTE` o vacío. Si el asesor te da el precio con
     descuento de un proyecto, va el suyo. El detalle está en
     [`buscar-equipo`](../buscar-equipo/SKILL.md), "Cuánto creerle al
     precio de cada fila".

   - **C (IMPORTADO):** `si` cuando Grupo Visión compra ese ítem fuera
     del país, `no` cuando lo compra local (R1). Manda sobre dos
     porcentajes a la vez: con `no`, transporte y DAI quedan en cero.

     ⚠️ **Una línea de flete va siempre como `no`** (R1.1). Cuando el
     proveedor cotiza el envío como un artículo más de su lista
     —transporte, flete, envío, courier, carga aérea, logística,
     nacionalización, desalmacenaje, aduana— y se marca `si`, recibe
     encima el 10% de transporte: se le cobra transporte al transporte.
     Medido sobre 728 líneas de flete reales, el 91,3% van como `no`.
     Si el asesor la quiere importada, que sea a propósito.

   **Todo lo demás (columnas F en adelante) son fórmulas fijas del
   machote — nunca se escriben a mano ni se recalculan aparte.** Si el
   equipo incluye accesorios de instalación que el asesor confirmó
   (bases, mounts, lentes, etc. — ver `buscar-equipo`), esos van como
   filas adicionales en la misma pestaña, con la misma lógica.

   ⚠️ **La mano de obra va en `OPEX GV`; los materiales de instalación,
   en `MATERIALES`.** En `Equipos` van solo los equipos. Así quedó después
   de dos correcciones: preventa (2026-10-21, *"OPEX, así se llama la hoja
   de la mano de obra en la matriz"*) y gerencia (2026-10-27, en la demo:
   el cable de fibra va en `MATERIALES`, no en OPEX). Del 2026-10-15 al
   2026-10-21 este skill escribía la mano de obra en `Equipos` (un mensaje
   de voz mal entendido), y del 2026-10-21 al 2026-10-27 los materiales en
   `OPEX GV`, porque `MATERIALES` no llegaba a la cotización.

   Cómo se carga:

   - **Las personas y los días** van en `MANO DE OBRA ` (fila del
     Configurador): días `E5`, personas `F5`, alimentación por día y
     persona `H5`. Su total llega solo a `OPEX GV!D6`, y en `OPEX GV!C6` va
     cantidad **1** para que cuente. **Viajes y hospedaje, desde el
     2026-10-27** (antes los dos se multiplicaban por los días, y en la
     demo *"₡35.000 ida y vuelta"* se vio como $35,71 por día):
     - **Combustible por viaje de ida y vuelta** en `I5`, y **cuántos
       viajes** en `L5`. Si lo dan **en colones**, va en `N5` (ej. `35000`)
       e `I5` lo pasa a dólares con el tipo de cambio de `Datos del
       proyecto!B47`: no se convierte a mano ni se pisa la fórmula. Si no
       dan nada, `I5` sale de `Transporte` (los km del destino).
     - **Hospedaje: el costo de una noche para todo el equipo** en `J5`, y
       **cuántas noches** en `M5`.
     - Si `L5` o `M5` quedan vacíos, cuentan como los días (el cálculo de
       antes: un viaje y una noche por día).

     Al confirmar con el asesor, mostrá la conversión: *"₡35.000 ida y
     vuelta = $71,43 al tipo de cambio 490, 1 viaje"*.
   - **Los materiales de la instalación** (cable, fibra, tubería, cajas,
     conectores) van en `MATERIALES`: descripción en `A`, `IMPORTADO` en
     `B` (**`no`** si se compra en el país: la plantilla trae `si`),
     cantidad en `C`, costo unitario en `D`. Las filas 6 a 32 traen una
     lista de materiales comunes con cantidad 0: si el material está ahí,
     se usa esa fila; si no, la primera vacía (33-36, 38-42 o 44; las
     filas `Sección` no se tocan). `MATERIALES` tiene sus porcentajes
     propios: IVA de compra 13% y **margen 30%**, no el 27,4% de `Equipos`.
     Las cantidades las da preventa: nunca se estiman (R10).
   - **En la cotización**, la **fila 72** de `COTIZACIÓN ` lleva `OPEX GV`
     + `MATERIALES` en una línea, cantidad 1, y su texto cambia solo:
     *"Instalación, configuración y puesta en marcha de los equipos
     ofertados"*, con *"(mano de obra y materiales)"* si hay de los dos, o
     *"Materiales de instalación"* si hay solo materiales. El texto se
     puede cambiar. `ajustar_vista.ps1` la oculta si da cero. `K74`
     (Equipos + OPEX GV + MATERIALES) tiene que dar igual al SUBTOTAL; si
     no, avisa `L75`. Una matriz armada antes del 2026-10-27 se pone al día
     con [`scripts/ajustar_materiales_viaticos.ps1`](scripts/ajustar_materiales_viaticos.ps1).

   ⚠️ La cotización **financiada** no tiene esa línea: financia solo
   `Equipos`. Si la instalación también va financiada, decíselo al asesor:
   hoy se agrega a mano.

   Cuando la instalación tiene **precio cerrado** ("la instalación se
   cobra $100"), va en `OPEX GV` con cantidad 1. El monto que dan es lo
   que **paga el cliente**, así que el costo unitario se despeja para que
   el margen no lo infle (`OPEX GV` usa los mismos porcentajes):

   ```
   Costo Unit = precio al cliente × (1 − margen) / ((1 + imprevistos) × (1 + administración))
   ```

   Con los porcentajes del machote (27,4%, 3%, 3%) es el precio ÷
   1,461301: $100 → $68,43, y el cliente ve $100,00. Si dicen que el monto
   es el costo, va tal cual y el cliente ve más. Ante la duda, preguntá
   cuál de los dos es.

   ⚠️ **Un precio cerrado no va redondo** (preventa, 2026-10-19, regla
   R23): *"siempre tratamos de poner números con coma… que no sea un 30
   ahí cerrado"*. Si el monto que dan es redondo ($30, $100), decíselo al
   asesor y proponé uno con decimales cercano y algo menor (por ejemplo
   $29,25 o $27,50); que él elija. En el primer caso real se cotizó $30, y
   preventa lo cambió antes de enviarla: puso $20 de costo, y el cliente
   vio $29,23.

   **Los porcentajes (Transporte, Imprevistos, IVA, DAI, Administración,
   Margen) varían por proyecto y por etapa comercial** — ver la regla R6
   en [`docs/reglas-negocio.md`](../../../docs/reglas-negocio.md) para el
   detalle de cómo se mueve cada uno en estudio de mercado vs. licitación
   vs. cliente privado.

   **Los valores del machote son una recomendación inicial, no una
   verdad** (decisión del usuario, 2026-09-18). El flujo correcto es:
   mostrárselos al asesor **antes** de escribir nada, y preguntarle si
   alguno cambia para este proyecto. Si no sabe o dice "los de siempre",
   se dejan tal cual. Son las celdas de la **fila 4** de cada pestaña
   (`$G$4`, `$H$4`, etc.): un valor por columna que aplica a todas las
   líneas de esa pestaña, así que cambiarlo es editar una sola celda.

   **Base del machote — `Equipos`:** Transporte 10%, Imprevistos 3%, IVA
   0%, DAI 15%, Administración 3%, Margen 27,4%. **`MATERIALES` y
   `OPEX Proyecto`:** Transporte 10%, Seguros 0%, IVA 13%, DAI 14%,
   Administración 3%, Margen 30%. **`OPEX GV`:** Transporte 10%,
   Imprevistos 3%, IVA 0%, DAI 14%, Administración 3%.

   ⚠️ **No son "dos juegos independientes" — son 18 pestañas con su
   propia fila de porcentajes, y hay un vínculo cruzado** (verificado
   2026-09-18): `OPEX GV!M4` (margen) es la fórmula `=+Equipos!$N$4`, así
   que **cambiar el margen en `Equipos` mueve también el de `OPEX GV`**,
   sin ningún aviso. `MATERIALES` y `OPEX Proyecto` sí tienen el suyo
   independiente. Si el asesor cambia el margen, decile explícitamente
   qué pestañas se movieron.

   ⚠️ **El IVA de la columna NO es el impuesto que paga el cliente**
   (regla R2). El IVA de línea es un **costo**: lo que el proveedor nos
   cobra a nosotros al comprar. El impuesto al cliente es la fila
   `IMPUESTO` de la pestaña `COTIZACIÓN ` y depende del **régimen fiscal
   del cliente** (regla R3) — hay clientes exentos y clientes con un
   porcentaje distinto al 13%. Una cotización puede legítimamente llevar
   IVA de línea en materiales y 0% de impuesto al cliente. **Preguntá
   siempre por el régimen del cliente si no lo tenés confirmado**; no
   asumas 13% ni asumas exención.

   **Cómo se aplica desde el 2026-09-22 (importante):** la fila
   `IMPUESTO` (`J75`) de `COTIZACIÓN ` y de `COTIZACION (Financ)` ya
   **no** tiene el 13% escrito a mano — lee `Datos del proyecto!B15`
   (`Cliente exento`, si/no) y `B16` (`% impuesto al cliente`). Eso
   cambia lo que tenés que hacer: **para que la exención surta efecto
   hay que escribirla en la ficha**, no basta con saberla. Si dejás
   las dos celdas vacías, el machote aplica 13% igual que siempre.
   `C16` muestra en vivo la tasa que se está aplicando — miralo antes
   de dar la cotización por buena. Hasta esa fecha la ficha preguntaba
   el régimen fiscal y la cotización lo ignoraba en silencio: un
   cliente exento pagaba 13% sin ningún error visible en Excel.

   ⚠️ **Y una cosa más sobre el IVA de línea (R2, rastreado 2026-09-22).**
   El transporte y el DAI se calculan con `IF(IMPORTADO="si", ...)`; el
   IVA de línea **no** — se aplica siempre, con el porcentaje que tenga
   la fila 4 de esa pestaña (`Equipos` 0%, `MATERIALES` 13%). O sea que
   el IVA de una línea lo decide **en qué pestaña la escribiste**, no el
   producto.

   **Qué tenés que hacer con eso:** cuando escribas una línea cuyo
   proveedor es local (`IMPORTADO = "no"`) en una pestaña con IVA 0%
   —o una importada en una con 13%— **decíselo al asesor**. No cambies
   el porcentaje por tu cuenta: si ese IVA es un costo o se acredita es
   una decisión contable de la empresa, y está pendiente de respuesta en
   [`docs/pendientes-comercial.md`](../../../docs/pendientes-comercial.md).
   Avisar es lo único correcto mientras tanto.

   Mostrale al asesor la tabla completa (Modelo | Descripción |
   Importado | Cantidad | Costo Unit) que vas a escribir **antes** de
   tocar el archivo, y esperá confirmación — igual que con cualquier
   otro dato que se escribe en `CLIENTES/`.

   **Para escribir:** [`scripts/llenar_matriz.ps1`](scripts/llenar_matriz.ps1)
   copia el machote y escribe las celdas de un JSON (`Equipos`, `Datos
   del proyecto`, el encabezado de `COTIZACIÓN `), por Excel. **Primero
   con `-Destino` en `%TEMP%\preventa-borrador\`** (R25): sobre ese
   borrador corre
   [`scripts/vista_previa_montos.py`](scripts/vista_previa_montos.py)
   (`python -I`), que imprime en Markdown lo que ve el cliente, el costo
   interno por pestaña y los controles (K74 = subtotal, celdas con error;
   sale con código 1 si algo falla). Con el sí del asesor, el borrador se
   **copia** a `Matriz-Oferta/` con su nombre final: no se vuelve a
   llenar, para que lo entregado sea exactamente lo que se aceptó.

   ⚠️ **La firma de `COTIZACIÓN ` también va en el JSON** (2026-10-27,
   primer PDF de una cotización real): `B88` con el nombre completo del asesor de
   preventa y `B92` con `E-mail: <su correo>`. El machote trae
   `[Nombre del asesor responsable]` y `[correo del asesor]`, y así
   saldrían en el PDF que ve el cliente. El dato sale de la última matriz
   de ese asesor (preventa lo llena en las suyas) o se le pregunta; nunca
   se inventa. `generar-pdf-cotizacion` no exporta si quedan corchetes.
   Se corre
   con `powershell -NoProfile -ExecutionPolicy Bypass -File` (ver `verificar-entorno`,
   punto 5). No escribe
   en una celda con fórmula, recalcula, lee los totales y cuenta las
   celdas con error. Se probó el 2026-10-15 con el primer caso real: un
   borrador fuera de `CLIENTES`, cero errores, totales iguales a los
   calculados a mano.

## Registrar la cotización en los Excels de control (agregado 2026-09-01, ruta confirmada 2026-09-07)

Además de la carpeta y la matriz, cada cotización nueva (o cambio de
estado de una existente) se registra en **dos** Excels compartidos —
ver `verificar-entorno/SKILL.md` paso 4 para la ruta exacta y cómo
verificar el acceso (viven dentro de la carpeta compartida `COMERCIAL
2024`, no dentro de `CLIENTES` ni en la raíz de OneDrive):

- `Control de cotizaciones 2026.xlsx`, pestaña **"Cotizaciones
  Pendientes 2026"** (tiene 15 pestañas, las demás son de otros
  años/usos, no tocarlas). Encabezado real leído el 2026-09-21:

  | Col | Encabezado |
  |---|---|
  | A | Fecha Solicitud |
  | B | Importancia |
  | C | Empleado |
  | D | Nombre de cliente |
  | E | Descripción del producto/servicio |
  | F | Fecha oficial de entrega |
  | G | Fecha en que se realiza oferta |
  | H | Fecha de envío |
  | I | Número de oferta |
  | **J** | **Monto sin IVA** ← ojo, ver la regla del monto abajo |
  | K | Días de retraso |
  | L | Proveedor / Contratista |

- `Cotizaciones en Preventa.xlsx` — **una pestaña por asesor** (hoy:
  `Katherine`, `Alessandro ` —con espacio final— y `IA`).

  ⚠️ **Las dos pestañas de asesor NO tienen las mismas columnas: están
  corridas una posición** (verificado 2026-09-21). Escribir la fila de
  una con el orden de la otra mete el nombre del cliente en la columna
  de fecha, sin ningún error visible.

  | Col | `Katherine` | `Alessandro ` |
  |---|---|---|
  | A | Cliente | Fecha que se realiza la oferta |
  | B | Descripcion | Cliente |
  | C | Numero de Oferta | Descripcion |
  | D | **Monto de Oferta** | Numero de Oferta |
  | E | Estado | **Monto de Oferta** |
  | F | Fecha de Ingreso | Estado |
  | G | Ejecutiva | Fecha de Ingreso |
  | H | Simb de Estado Cotización | Ejecutiva |
  | I | Color | Comentarios |
  | J | — | Simb de Estado Cotización |
  | K | — | Color |

  La pestaña de Katherine **no tiene columna de fecha de oferta**; la de
  Alessandro sí, y además tiene `Comentarios`. Esta tabla es una ayuda
  para saber qué esperar, **no un reemplazo de leer el encabezado
  real**: si alguien agrega una columna, la tabla queda vieja y el
  archivo no. Leé siempre el encabezado de la pestaña en la que vas a
  escribir: está en la **fila 6** (arriba hay un título), y la próxima
  fila libre es la de abajo de la última con cliente.

  ⚠️ **Quién usa cada pestaña** (medido el 2026-10-19): la de Alessandro
  sí, con 117 filas de julio a octubre de 2026; la de Katherine casi
  no, dos filas y la última de febrero. Katherine registra solo en
  `Control de cotizaciones 2026`. Antes de escribir en la pestaña de un
  asesor que no la usa, preguntá: agregarle una fila después de meses no
  es lo que hace el equipo.

**El "Monto" que se escribe (corregido 2026-09-22 — la versión del
2026-09-14 decía lo contrario y estaba mal):**

- **Va el SUBTOTAL, sin el impuesto al cliente.** La columna de
  `Control de cotizaciones 2026.xlsx` se llama literalmente
  **`Monto sin IVA`**. La versión anterior de este skill mandaba
  escribir "el TOTAL con impuesto, nunca el subtotal" — es exactamente
  al revés para este archivo.

  **La evidencia, para no volver a darlo vuelta sin datos:** se
  cruzaron los dos Excels por número de oferta (join estricto sobre el
  formato `T#-#######`). De las **26 ofertas que aparecen en ambos, 19
  tienen el monto idéntico** y **ninguna** está en relación 1,13 ni
  1/1,13. Las 7 restantes tienen ratios absurdos (166×, 10.390×), o sea
  ruido de digitación, no un patrón de impuesto. Conclusión: los dos
  archivos guardan **el mismo número**, y el único de los dos que dice
  qué número es lo llama *sin IVA*.

- **De dónde sacarlo:** la pestaña `COTIZACIÓN ` de la matriz, fila con
  etiqueta **"SUBTOTAL"** (la que está *antes* de "IMPUESTO" y
  "TOTAL"). Buscá la fila por su etiqueta, no asumas un número fijo
  —cambia según cuántas líneas tenga la cotización—. Leé el valor ya
  calculado por Excel (`openpyxl` con `data_only=True`, después de que
  el archivo se guardó por COM) en vez de sumar las líneas a mano.

- **El mismo número va en los dos archivos.** No conviertas ni ajustes
  para uno y no para el otro.

  ⚠️ **Confirmalo con preventa la primera vez que lo uses.** El
  encabezado podría estar viejo y la práctica haber cambiado sin que
  nadie renombrara la columna. Los datos dicen "subtotal" con bastante
  fuerza, pero el que sabe es quien llena ese archivo todos los días —
  y si la respuesta es que va el total, hay que renombrar la columna,
  no cambiar esta regla en silencio.
- **Mantené dólares, nunca inventes una conversión a colones.** La
  matriz trabaja en USD; los dos Excels de control no tienen una
  columna de moneda fija — las filas reales existentes muestran el
  monto como texto libre con el símbolo `$` escrito a mano (ej. `"$16
  599,84"`). **Escribí el monto como texto con el símbolo `$` explícito**
  (ej. `"$ 15,010.64"`), nunca como un número plano.
- **Cuidado: escribir un string con `$` no garantiza que quede como
  texto.** Por COM, asignar `Value2 = "$ 15,010.64"` puede hacer que
  Excel lo interprete como número y le aplique el formato de celda que
  ya estuviera ahí — y se confirmó en la práctica (2026-09-14) que una
  celda puede tener heredado un formato de **colones** (`₡#,##0.00`) en
  esa misma columna, mostrando un monto en dólares con símbolo de
  colón, sin ningún error ni advertencia. **Después de escribir,
  siempre releé `.Text` (no `.Value2`) de esa celda por COM para
  confirmar qué símbolo de moneda se ve de verdad.** Si no es `$`,
  forzá la celda a texto antes de escribir (`.NumberFormat = "@"` y
  recién ahí `.Value2 = "$ ..."`) y volvé a verificar `.Text`.

Ambos archivos tienen además una pestaña **"IA"** al final — es zona de
prueba (usada para confirmar acceso de escritura), **nunca escribas
datos de una cotización real ahí**, siempre en la pestaña real
correspondiente.

**Se registra en los dos** (decisión confirmada 2026-09-01 — es el
flujo de trabajo real de preventa, no se consolida).

**Para escribir:** [`scripts/registrar_control.ps1`](scripts/registrar_control.ps1)
(2026-10-27, primer uso en la demo a gerencia). Agrega una fila debajo de
la última con datos, con las columnas en un JSON: no corre sin OneDrive
sincronizado, saca respaldo, apaga el Autoguardado, no escribe sobre una
celda con algo, y relee `.Text` de cada celda (así se vio que una fecha
quedaba como `46322` si la celda de arriba no tenía formato de fecha).
Primero sin `-Guardar` y después con `-Guardar`. La fila ya se le mostró
al asesor en la vista previa (R25): la corrida sin `-Guardar` es para
confirmar que lo que se va a escribir es eso; si difiere (otra fila, otro
monto), se para y se pregunta. Con `-Quitar` borra la fila de una cotización de prueba o
anulada, buscándola por contenido (cliente + número de oferta), y solo si
coincide una sola fila. Con `-Actualizar` corrige la fila ya registrada de
una cotización que cambió (descripción, monto), con la misma búsqueda; no
se agrega una fila nueva por la misma oferta. El número de oferta solo no
alcanza: cada cliente lleva su consecutivo. Encabezados medidos ese día: `Control de
cotizaciones 2026` en la **fila 2** (A Fecha solicitud · C Empleado, con
la inicial: `A`/`K` · D Cliente · E Descripción · G Fecha de la oferta ·
I Número · J Monto sin IVA, como texto con `$` · K `=+NETWORKDAYS(A<f>,$K$1)`
· L Proveedor), `Cotizaciones en Preventa` / `Alessandro ` en la **fila
6** (Comentarios con el estado: `EN PROCESO (AL)`, `ENVIADA (AL)`).

**Cómo escribir, según el acceso disponible:**

1. **Si los dos archivos están sincronizados localmente** (caso normal
   desde 2026-09-07, ver `verificar-entorno` paso 4): escribí ahí
   directo por archivo, **con Excel real por automatización COM, nunca
   con `openpyxl`** (ambos archivos tienen imágenes/comentarios reales
   — ver la advertencia de arriba, en "Alcance") — mismo criterio que
   el resto de este skill: leé el encabezado real primero (no asumas el
   orden de columnas de memoria), mostrale al asesor la fila completa
   antes de guardar, y agregala en la pestaña del asesor correspondiente
   (preguntale cuál es la suya si no lo sabés).
2. **Si no están sincronizados localmente** (fallback, no debería ser
   el caso normal): ⚠️ **nunca los edites en vivo por navegador con
   datos reales.** Se probó en la práctica (2026-09-01): estos archivos
   son pesados (cientos de filas, autoguardado activo, uso compartido
   en tiempo real con Katherine/Alessandro) y la automatización de
   navegador resultó **inestable de verdad** — pantallas en blanco,
   capturas que se cuelgan, atajos de teclado que no registran — sin
   ninguna red de seguridad porque el archivo se guarda solo en cada
   cambio. En vez de arriesgarte a escribir mal en un documento
   compartido real: **armá la fila exacta (todas las columnas) y
   mostrásela al asesor para que la pegue él mismo** en el archivo
   abierto — seguís siendo más rápido que hoy (ya no arma los datos a
   mano) sin tocar el archivo en vivo vos.
3. Si el acceso local se llega a caer, avisá y sugerí correr
   `verificar-entorno` de nuevo — no sigas usando
   el navegador como método principal aunque funcione una vez.

## Caso 2: nueva versión de una cotización existente

1. **Preguntá siempre** si el cambio es "menor" o "grande" — nunca lo
   infieras. No hay regla fija hoy, es criterio del asesor.
2. **Cambio menor:** dentro de la misma carpeta `Matriz-Oferta/`, se
   agrega un archivo nuevo (PDF y/o `.xlsx`) con sufijo de versión. El
   archivo anterior **se conserva**, nunca se borra ni se sobrescribe.
   Usá un formato de sufijo consistente (` V2`, ` V3`...) — hoy en la
   carpeta real es inconsistente (`v2`, `(V3)`, `// v3`), pero de acá en
   adelante usá siempre el mismo formato para lo que genere este skill.
   Si el cambio es agregar/ajustar líneas de equipo en ese archivo
   nuevo, aplicá el mismo criterio del paso 7 de "Caso 1" (solo columnas
   de entrada B-E, mostrar la tabla antes de escribir) — pero como este
   archivo puede ya tener datos reales del asesor, **mostrale primero
   qué filas existen y cuáles vas a agregar/cambiar**, nunca sobrescribas
   una fila ya llena sin que lo confirme explícitamente.
3. **Cambio grande** (ej. cambiar de marca de cámara completa): se crea
   una copia nueva — seguí el flujo completo del "Caso 1" (nueva carpeta
   "Cotización #N+1...", nuevo número de oferta propuesto, y el paso 7
   completo usando el equipo nuevo que salga de `buscar-equipo` para la
   marca nueva) dentro del mismo cliente/año.

## Financiamiento (implementado 2026-09-14)

El machote ya tiene financiamiento — construido a partir de un CSV real
exportado por una compañera (pestañas `Financiamiento` y `PTMO` de una
matriz real de un proyecto con financiamiento) y verificado contra un
ejemplo numérico real que ella misma dio a mano. **Los tres números
clave del ejemplo real coinciden exacto con lo que calcula el machote
ahora** ($4,511.24 a financiar, 11% anual, 48 meses → cuota $116.60,
interés total $1,085.34, total con financiamiento $5,596.58) — no es
una aproximación, es la misma fórmula que usa la empresa.

**Regla de negocio, no cambiar**: si la columna "Financ." de una
pestaña de producto está vacía para todas sus líneas, **no aplica
financiamiento** — no llenar nada de esto "por si acaso". **Antes de
tocar cualquier cosa de financiamiento en una cotización nueva,
preguntale siempre al asesor si el proyecto necesita esa opción** —
nunca lo asumas por el tamaño del proyecto ni por ningún otro criterio
propio.

### Columna "Financ." (ID de financiamiento)

Se agregó una columna **"Financ."** al final de las columnas existentes
en `Equipos`, `Productos 2`, `MATERIALES` y `OPEX GV` — vacía por
defecto. Si el asesor confirma que una línea de equipo/material entra en
financiamiento, escribile ahí un número entero simple, único dentro de
esa misma pestaña (1, 2, 3...) — es el ID que conecta esa línea con su
cuadro correspondiente en la pestaña `Financiamiento`.

### Pestaña `Financiamiento`

Una cuadrícula de cajas "CUADRO COSTOS FINANCIEROS", una por cada fila
posible de `Equipos` (**50 cajas** desde 2026-09-18, antes 14),
`Productos 2` (10), `MATERIALES` (39) y `OPEX GV` (10) — agrupadas en 4
bloques de columnas, uno por pestaña de origen. Las cajas de `Equipos`
están en la columna A/B: la caja *n* arranca en la fila
`3 + (n−1)·17`, o sea la caja 1 en la fila 3 y la caja 50 en la 836.
Cada caja:

- **Total Venta Proyecto**: `=SUMIF(<pestaña>!Financ., <ID de esta
  caja>, <pestaña>!Precio Venta Total)` — trae automáticamente el precio
  de venta de la línea que tenga ese ID en la columna "Financ." de la
  pestaña de origen. Si ninguna línea tiene ese ID, da $0 — no rompe
  nada, solo no aplica esa caja.
- **Total a Financiar** = Total Venta Proyecto − Anticipos − Otros
  ingresos (los dos últimos en 0 por defecto, editables).
- **Interés Anual** (11% por defecto) y **Plazo (Años)** (4 por
  defecto) son editables por caja — no hay una tasa global única, cada
  caja se puede ajustar individualmente si un proyecto lo necesita.
- **Cuota mensual/anual, Total Cuotas, Costo financiero**: fórmulas de
  anualidad estándar, verificadas contra el ejemplo real arriba.
- **TIR**: queda como etiqueta sin fórmula — se revisaron ~29 cuadros
  reales y "TIR" está vacío en todos, sin excepción. No se inventó una
  fórmula de TIR para algo que en la práctica nunca se llena.

### Pestaña `PTMO`

En el archivo real esta pestaña está **rota** (fórmulas `#¡REF!` en
todo, evidencia real vía CSV exportado) — no se replicó ese estado.
Se construyó una versión **funcional** desde cero, misma plantilla
visual (tipo Microsoft, "Especificar valores" / "Resumen del préstamo" /
tabla de amortización mes a mes), pero con fórmulas de anualidad reales
que sí calculan — verificado con el mismo ejemplo real (coincide exacto
en cuota, interés total, y la tabla termina sola en el pago 48 con saldo
$0). Es una calculadora de amortización de uso general — el asesor
escribe a mano el monto/tasa/plazo que quiere detallar (no está
automáticamente conectado a una caja específica de `Financiamiento`,
igual que en el archivo real).

### Verificado 2026-09-18

Las pestañas `Financiamiento` y `PTMO` **existen y calculan bien** en el
machote actual. `PTMO` está reconstruida con fórmulas reales de
amortización (el archivo original del que se partió tenía esa pestaña
rota con `#¡REF!`). Comprobado con la prueba P-05 de
[`docs/pruebas-validacion.md`](../../../docs/pruebas-validacion.md):
sobre una línea de $1.848,54 al 11% a 4 años, la cuota mensual da
exactamente `47.7764275443391` y el costo financiero `444.7306433404`.

También quedó confirmado por preventa que **el diseño replica su método
manual exacto**: ella numera cada línea que entra en financiamiento y
copia el cuadro de costos uno por uno (29 líneas de equipo y 5 de OPEX
en el ejemplo que mostró), *"porque en las primeras 5 líneas tal vez lo
haga bien, pero ya si voy por la línea 15 o 20 me puedo equivocar"*. La
columna `Financ.` + `SUMIF` es precisamente eso, automatizado.

### La cotización financiada (construida 2026-09-21)

Ya existe la pestaña **`COTIZACION (Financ)`**, el documento que ve el
cliente en modalidad financiada. Está justo después de `COTIZACIÓN ` y
se construyó copiando la lógica de una cotización financiada real de la
empresa.

Muestra **`Precio Unitario Mensual` × cantidad = `Total Mensual`**, y el
precio unitario es la cuota del cuadro que le corresponde a esa línea
**por ID** (no por posición fija, que es como lo hace el archivo
original — el vínculo por ID es justo lo que evita el error de copiar
cuadro por cuadro que describió preventa).

⚠️ **Los cuadros financian el precio UNITARIO, no el total de la
línea.** Por eso **un ID por línea**: si dos líneas comparten ID, se
suman dos precios unitarios y el resultado no significa nada.

Detalle completo, fórmulas incluidas, en la regla R13 de
[`docs/reglas-negocio.md`](../../../docs/reglas-negocio.md).

## Checklist final

Después de cualquier acción, mostrá un resumen claro de qué se creó,
dónde, y qué números se propusieron (aclarando cuáles todavía necesitan
confirmación del asesor).

`references/` tiene el machote oficial de la empresa en uso actual
(verificado en blanco, sin datos de ningún cliente real — ver
[`docs/notas-proceso.md`](../../../docs/notas-proceso.md)):
`Machote Matriz y oferta.xlsx`.

**Estructura vigente desde el 2026-09-22: 33 pestañas, 17 visibles**
(la cuenta del 2026-10-19, ya sin `Guia de skills`; ver abajo).
Antes eran 40. Se quitaron 10 que contenían la matriz de costo de un
proyecto real anterior (equipo, precios de compra y el nombre del
cliente en la fila 1) más una tabla de cantidades fijas de material de
instalación por cámara, que es el mismo antipatrón de
`Proporciones Instalacion` y por eso se eliminó (regla R10). A otras dos
se les borraron 305 constantes numéricas dejando las fórmulas. Todo eso
viajaba oculto dentro de cada cotización que se le mandaba a un cliente
distinto.

Se agregaron tres pestañas de inducción, que **no calculan nada** y
están solo para quien llega nuevo al equipo:

- **`LEEME`** (primera): qué es el archivo, la regla de oro de que solo
  se escriben cuatro columnas, en qué orden se llena y los tres errores
  que más caro salen.
- **`Guia de pestanas`** (penúltima): las 17 visibles, con qué se
  escribe a mano, qué sale solo y con qué otra pestaña está conectada.
- **`Guia de formulas`** (última): las fórmulas que deciden la plata,
  explicadas en palabras — incluido que el margen se aplica sobre el
  precio de venta y no sobre el costo (27,40% de margen equivale a
  37,74% sobre el costo), y los vínculos cruzados que sorprenden
  (`OPEX GV` ← `Equipos`, `OPEX GV` ← `MANO DE OBRA` ← `Transporte`).

Hubo una cuarta, `Guia de skills` (cómo pedirle cada cosa a la IA). El
2026-10-19 **pasó al catálogo** (Fabián: no tiene que viajar en cada
cotización), con un renglón en su `LEEME`. El machote quedó en 33
pestañas.

### Cómo se ve la matriz (pedido de Fabián, 2026-10-19)

Antes, una cotización de dos líneas mostraba 48 filas de ceros en las
dos hojas de cotización, 45 líneas vacías en `Equipos`, las pestañas de
financiamiento aunque no llevara, y cuadros de `Financiamiento` sin
formato y con los nombres cortados. Quedó así:

| Qué | Dónde se resuelve |
|---|---|
| **Un cero se ve en blanco** en las líneas 22-71 de `COTIZACIÓN ` y `COTIZACION (Financ)` | En el machote (formato de número con la sección del cero vacía; no cambia ninguna fórmula) |
| **`Financiamiento`**: cada cuadro con título de color, borde, moneda y porcentaje, editables en amarillo, columnas anchas y encabezado por bloque | En el machote |
| **`PTMO`**: si el importe es 0 la tabla queda vacía (antes, 48 filas de ceros); formatos y estilo | En el machote (la columna A pide además `N($D$5)>0`) |
| **`Equipos`: las líneas usadas + 3 libres**; el resto oculto | En cada cotización: [`scripts/ajustar_vista.ps1`](scripts/ajustar_vista.ps1), que corre solo al final de `llenar_matriz.ps1` |
| **Las dos cotizaciones: solo las líneas usadas, sin un renglón en blanco** (preventa, 2026-10-19: *"abajo habían otras dos líneas en blanco… para que quede la oferta bien presentable"*) | En cada cotización, el mismo script |
| **Aviso rojo en `L74`** (fuera del área de impresión) si una fila oculta tiene monto: suma en el total pero no aparece escrita | En el machote |
| **Sin financiamiento** (ficha `B42 = no`): `Financiamiento`, `PTMO` y `COTIZACION (Financ)` ocultas; con `si`, visibles | En cada cotización, el mismo script |

Las mejoras del machote las aplica
[`scripts/mejorar_diseno_matriz.ps1`](scripts/mejorar_diseno_matriz.ps1),
que también pone al día una matriz armada con el machote anterior. Se
verificó con `smoke-machote.ps1` y `prueba-cotizacion.ps1`: todas las
pruebas pasan, mismos números al centavo.

⚠️ **Si el asesor agrega una línea a mano** en una de las 3 libres de
`Equipos`, su fila en `COTIZACIÓN ` está oculta (la línea *n* de
`Equipos` es la fila *n + 16* de la cotización): hay que mostrarla, o
volver a correr `ajustar_vista.ps1`, que lo hace solo. Si no, la línea
suma en el total pero no aparece escrita, y el aviso rojo de `L74` lo
dice. `generar-pdf-cotizacion` igual oculta, al exportar, toda fila con
cantidad cero.

Si agregás o quitás pestañas, actualizá esas guías: son documentación,
se desactualizan solas. Cualquier otro catálogo, tabla de
precios o machote adicional que se agregue después debe pasar por la
misma verificación (sin datos reales de clientes, con evidencia de uso
reciente) antes de subirse acá.
