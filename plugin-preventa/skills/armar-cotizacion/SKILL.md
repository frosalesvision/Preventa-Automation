---
name: armar-cotizacion
description: Organiza los archivos y carpetas de una cotización de preventa dentro de la carpeta compartida del cliente (crear la carpeta "Cotización #N-AAAA <descripción>" con sus subcarpetas estándar, copiar el machote de matriz oficial, proponer numeración de carpeta y número de oferta, manejar versionado de nombres de archivo), y llenar la pestaña Equipos de esa matriz con el equipo/accesorios que se hayan encontrado (ej. vía `buscar-equipo`) — modelo, descripción, cantidad y costo unitario; las fórmulas de margen/precio de venta del machote calculan el resto solas, nunca se tocan a mano ni se inventan. También registra la cotización en los dos Excels de control compartidos ("Control de cotizaciones 2026.xlsx" y "Cotizaciones en Preventa.xlsx") cuando están sincronizados localmente. Usar cuando el usuario pide crear/organizar la carpeta de una cotización nueva, agregar una versión a una cotización existente, pide el siguiente número de "Cotización #N" u oferta para un cliente, pide cargar el equipo ya encontrado a la matriz, o pide registrar/anotar la cotización en el control de ofertas.
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
   **Antes de seguir, calculá la ruta completa** que va a tener el
   archivo más profundo (el machote dentro de `Matriz-Oferta/`, o
   `Implementacion/Documentación del proyecto/`) con ese nombre de
   cliente + carpeta de año + descripción. Windows/Excel no puede abrir
   archivos con ruta de más de ~259 caracteres — si la ruta calculada se
   acerca a ese límite (dejá margen, ej. más de 230), avisale al asesor
   y pedile una descripción más corta antes de crear nada. Esto es
   más probable con clientes de nombre largo (ej. nombres de
   licitaciones completos) — no lo asumas como caso raro.
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
   `references/`, es la copia maestra), renombrado como `Matriz y
   oferta <descripción corta>.xlsx` dentro de la nueva carpeta
   `Matriz-Oferta/`.

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
   - **E (Costo Unit):** el "Precio USD" del catálogo (el costo real de
     compra, no un precio especial/negociado) — es la base sobre la que
     el machote calcula transporte, impuestos, margen y precio de venta.

   **Todo lo demás (columnas F en adelante) son fórmulas fijas del
   machote — nunca se escriben a mano ni se recalculan aparte.** Si el
   equipo incluye accesorios de instalación que el asesor confirmó
   (bases, mounts, lentes, etc. — ver `buscar-equipo`), esos van como
   filas adicionales en la misma pestaña, con la misma lógica.

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

   Mostrale al asesor la tabla completa (Modelo | Descripción |
   Importado | Cantidad | Costo Unit) que vas a escribir **antes** de
   tocar el archivo, y esperá confirmación — igual que con cualquier
   otro dato que se escribe en `CLIENTES/`.

## Registrar la cotización en los Excels de control (agregado 2026-09-01, ruta confirmada 2026-09-07)

Además de la carpeta y la matriz, cada cotización nueva (o cambio de
estado de una existente) se registra en **dos** Excels compartidos —
ver `verificar-entorno/SKILL.md` paso 4 para la ruta exacta y cómo
verificar el acceso (viven dentro de la carpeta compartida `COMERCIAL
2024`, no dentro de `CLIENTES` ni en la raíz de OneDrive):

- `Control de cotizaciones 2026.xlsx`, pestaña **"Cotizaciones
  Pendientes 2026"** (tiene más pestañas, son de otros años/usos, no
  tocarlas) — columnas confirmadas: Fecha Solicitud, Importancia, letra
  del asesor, Nombre de cliente, Descripción del producto/servicio,
  Fecha entrega (hay más columnas a la derecha, no las asumas de
  memoria — leé el encabezado real antes de escribir).
- `Cotizaciones en Preventa.xlsx` — **una pestaña por asesor** (hoy:
  "Katherine", "Alessandro ", ambos nombres con variaciones menores —
  leé los nombres reales, no los tipees de memoria). Columnas
  confirmadas: Fecha de oferta, Cliente, Descripción, Número de
  Oferta, Monto de Oferta, Estado (hay al menos una columna más a la
  derecha, mismo criterio: leé el encabezado real).

**El "Monto" que se escribe (crítico, corregido 2026-09-14):**

- **Usar el TOTAL con impuesto, nunca el subtotal.** La pestaña
  `Equipos` de la matriz calcula un "Precio Venta" **antes de
  impuesto** — ese número **no** es el monto que va en los Excels de
  control. El monto real de la oferta está en la pestaña `COTIZACIÓN `
  de la matriz, fila con etiqueta "TOTAL" (después de "SUBTOTAL" e
  "IMPUESTO") — buscá esa fila por su etiqueta, no asumas un número de
  fila fijo (cambia según cuántas líneas de equipo tenga la
  cotización). Leé ese valor ya calculado por Excel (con `openpyxl`
  `data_only=True`, después de que el archivo se guardó con Excel/COM —
  ver la nota de más abajo sobre por qué no se escribe con `openpyxl`)
  en vez de sumar manualmente las líneas de `Equipos` — así no hay
  riesgo de olvidar el impuesto u otro ajuste que la matriz sí aplica.
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
`Machote Matriz y oferta.xlsx`. Cualquier otro catálogo, tabla de
precios o machote adicional que se agregue después debe pasar por la
misma verificación (sin datos reales de clientes, con evidencia de uso
reciente) antes de subirse acá.
