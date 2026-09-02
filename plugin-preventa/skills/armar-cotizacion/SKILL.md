---
name: armar-cotizacion
description: Organiza los archivos y carpetas de una cotización de preventa dentro de la carpeta compartida del cliente (crear la carpeta "Cotización #N-AAAA <descripción>" con sus subcarpetas estándar, copiar el machote de matriz oficial, proponer numeración de carpeta y número de oferta, manejar versionado de nombres de archivo). NO calcula precios ni lee/edita el contenido de ninguna matriz ya llena — eso lo hace el asesor con sus propias fórmulas. Usar cuando el usuario pide crear/organizar la carpeta de una cotización nueva, agregar una versión a una cotización existente, o pide el siguiente número de "Cotización #N" u oferta para un cliente.
---

# Armar cotización

**Alcance (no cambiar sin confirmar con el usuario):** este skill
organiza **archivos y carpetas** en `CLIENTES/<Cliente>/.../Cotización
#N-AAAA <descripción>/`. **Nunca abre, lee celdas, ni calcula nada
dentro de una matriz de costos ya en uso** (`Matriz-Oferta/*.xlsx` de
una cotización real) — esa matriz contiene costos de proveedor y
fórmulas de margen internas, información financiera sensible que maneja
el asesor con su propio criterio. Este skill como mucho **mueve, copia
o nombra** ese archivo como un bloque opaco, nunca lee ni escribe sus
celdas.

La única excepción es el **machote en blanco** de `references/`
(verificado sin ningún dato real de cliente — ver más abajo): el skill
sí lo **copia** (operación de archivo, no de lectura de celdas) para
armar la carpeta de una cotización nueva.

⚠️ La carpeta `CLIENTES/` es la carpeta de producción real de la
empresa, no un entorno de prueba. Antes de crear o renombrar cualquier
carpeta/archivo ahí, mostrale al asesor exactamente qué vas a hacer
(ruta completa) y esperá confirmación explícita.

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
   `Matriz-Oferta/`. El asesor lo abre después y lo llena a mano — el
   skill no toca ninguna celda.

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

## Caso 2: nueva versión de una cotización existente

1. **Preguntá siempre** si el cambio es "menor" o "grande" — nunca lo
   infieras. No hay regla fija hoy, es criterio del asesor.
2. **Cambio menor:** dentro de la misma carpeta `Matriz-Oferta/`, se
   agrega un archivo nuevo (PDF y/o `.xlsx`) con sufijo de versión. El
   archivo anterior **se conserva**, nunca se borra ni se sobrescribe.
   Usá un formato de sufijo consistente (` V2`, ` V3`...) — hoy en la
   carpeta real es inconsistente (`v2`, `(V3)`, `// v3`), pero de acá en
   adelante usá siempre el mismo formato para lo que genere este skill.
3. **Cambio grande:** se crea una copia nueva — seguí el flujo completo
   del "Caso 1" (nueva carpeta "Cotización #N+1...", nuevo número de
   oferta propuesto) dentro del mismo cliente/año.

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
