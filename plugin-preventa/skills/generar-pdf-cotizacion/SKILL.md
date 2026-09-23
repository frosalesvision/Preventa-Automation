---
name: generar-pdf-cotizacion
description: Genera el PDF final de una cotización a partir de la matriz ya completa, después de confirmar con el asesor de preventa que todo está correcto (equipo, cantidades, precios, condiciones). Usar cuando el asesor dice que la cotización está lista/terminada y hay que generar el PDF para enviarlo al cliente.
---

# Generar PDF de cotización — PENDIENTE

Este skill todavía no tiene lógica real. Idea propuesta por el usuario
(2026-09-09): cuando una cotización queda terminada (matriz completa y
revisada), **antes de generar el PDF final preguntarle siempre al
asesor si todo está correcto** — nunca generar el PDF en silencio ni
asumir que está listo solo porque la matriz tiene datos cargados. Esto
es la misma disciplina de "mostrar antes de escribir/generar y esperar
confirmación" que ya usan
[`armar-cotizacion`](../armar-cotizacion/SKILL.md) y
[`buscar-equipo`](../buscar-equipo/SKILL.md).

Relacionado con [`seguimiento-correo`](../seguimiento-correo/SKILL.md):
ese skill asume que este PDF ya existe para adjuntarlo al correo de
seguimiento — sin este skill, el asesor sigue generando el PDF a mano
como hoy.

## Falta información real para completarlo

- ¿Cómo se genera hoy el PDF a mano? (¿Un rango de impresión específico
  de la matriz, un botón/macro de "Guardar como PDF", una pestaña
  aparte pensada para imprimir, portada o membrete distinto?)
- ¿El PDF sale directo de la pestaña `COTIZACIÓN ` del machote (existe
  en `Machote Matriz y oferta.xlsx`, ver
  [`armar-cotizacion`](../armar-cotizacion/SKILL.md)), o de otra
  pestaña/archivo?
- ¿Nombre de archivo y ubicación? ¿Mismo criterio que el número de
  oferta `T{prefijo}-{7 dígitos}-{año}` que ya usa `armar-cotizacion`
  dentro de `Matriz-Oferta/`?
- ¿Hay versionado del PDF igual que de la matriz (Caso 2 de
  `armar-cotizacion`, ej. `V2`, `V3`), o el PDF siempre se
  regenera/reemplaza?

No armar la lógica de este skill hasta tener estas respuestas — es fácil
generar un PDF con el formato equivocado o desde la pestaña equivocada
si se asume en vez de preguntar.

## Qué exportar, exactamente (confirmado por preventa, 2026-09-23)

Fabián le preguntó al equipo si el cliente llega a ver la matriz. La
respuesta cierra la ambigüedad más importante de este skill:

> *Correcto, eso es a nivel interno. Al cliente se le pasa el PDF de la
> hoja que se llama Cotización, esta aparece en el Excel llamado matriz
> y oferta.*

- **El Excel de matriz es INTERNO.** Tiene costos de compra, márgenes y
  utilidad. **Nunca se le manda al cliente**, ni completo ni por error.
- **Lo que ve el cliente es UNA sola pestaña**, exportada a PDF: la que
  se llama `COTIZACIÓN ` — con espacio al final, ojo al buscarla.
- Si la cotización va en modalidad financiada, la pestaña equivalente es
  `COTIZACION (Financ)`, que muestra la cuota mensual en vez del precio
  de contado. **Preguntar cuál de las dos va**, o si van las dos.

### Cómo exportar una sola pestaña

Por COM, sobre la **hoja**. No sobre el libro ni sobre las hojas
seleccionadas: `SelectedSheets` no tiene ese método y falla.

```powershell
$h = $wb.Worksheets.Item("COTIZACION ")   # buscarla por patron, lleva acento
$h.PageSetup.Orientation    = 2           # horizontal
$h.PageSetup.Zoom           = $false
$h.PageSetup.FitToPagesWide = 1
$h.PageSetup.FitToPagesTall = $false
$h.ExportAsFixedFormat(0, $rutaPdf)
```

### Antes de exportar, verificar cuatro cosas

1. **Que no queden celdas en error** en esa pestaña. Un `#¡VALOR!` en el
   PDF que ve el cliente es peor que no mandarlo.
2. **Que el impuesto sea el correcto** para ese cliente — sale de
   `Datos del proyecto` (regla R3). En un caso real medido, un cliente
   **privado** llevaba **0%**: no asumir 13% nunca.
3. **Que el total cuadre** con lo que se registró en los Excels de
   control. Ojo: al control va el **subtotal sin IVA** y al cliente el
   **total**. No son el mismo número.
4. Mostrarle al asesor el nombre del archivo y la ruta **antes** de
   generarlo, y esperar confirmación. Es el documento que sale de la
   empresa.