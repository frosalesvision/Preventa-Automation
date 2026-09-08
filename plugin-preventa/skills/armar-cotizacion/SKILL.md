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

   La pestaña `Equipos` del machote tiene, a partir de la fila 6, una
   fila en blanco por línea de equipo, con estas columnas de **entrada**
   (las únicas que se escriben):
   - **B (Description):** Marca + Modelo + descripción del catálogo (ej.
     `PAR-P8PTZXIR32NH-AI - 8 Megapixel IP Plug & Play, Outdoor PTZ...`)
     — así queda igual de legible que en las cotizaciones reales.
   - **C (IMPORTADO):** `"si"` o `"no"` — determina si aplica la fórmula
     de DAI (impuesto de importación). Inferilo del "País de origen" del
     catálogo (si no es Costa Rica, probablemente `"si"`), pero
     **confirmalo con el asesor antes de guardar** — afecta un cálculo
     de costo real, no lo asumas en silencio si el catálogo no trae el
     dato.
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

Ambos archivos tienen además una pestaña **"IA"** al final — es zona de
prueba (usada para confirmar acceso de escritura), **nunca escribas
datos de una cotización real ahí**, siempre en la pestaña real
correspondiente.

**Se registra en los dos** (decisión confirmada 2026-09-01 — es el
flujo de trabajo real de preventa, no se consolida).

**Cómo escribir, según el acceso disponible:**

1. **Si los dos archivos están sincronizados localmente** (caso normal
   desde 2026-09-07, ver `verificar-entorno` paso 4): escribí ahí
   directo por archivo (`openpyxl`) con el mismo criterio que el resto
   de este skill — leé el encabezado real primero (no asumas el orden
   de columnas de memoria), mostrale al asesor la fila completa antes
   de guardar, y agregala en la pestaña del asesor correspondiente
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
