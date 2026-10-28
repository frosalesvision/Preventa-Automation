---
name: generar-pdf-cotizacion
description: Genera el PDF que se le manda al cliente, exportando SOLO la pestaña de cotización de la matriz (la de contado o la financiada), después de verificar que no haya errores, que el impuesto sea el del cliente y que el total cuadre, y de confirmar con el asesor el nombre del archivo; el PDF queda siempre en la misma carpeta que la matriz (Matriz-Oferta), se le muestra al asesor en el chat y se sigue con la vista previa del correo para enviarlo. Usar cuando el asesor dice que la cotización está lista/terminada y hay que generar el PDF para enviarla.
---

# Generar PDF de cotización

**Estado: funcional, usado con una cotización real** (2026-10-27: 7
líneas, 2 páginas, la matriz intacta). Antes, el 2026-09-25, se probó
sobre una copia del machote con una línea: sale en 2 páginas
—cotización y totales, después forma de pago y firma—, igual que los PDF
reales que envía preventa.

## Qué se exporta, y qué nunca

Lo confirmó preventa el 2026-09-23:

> *Correcto, eso es a nivel interno. Al cliente se le pasa el PDF de la
> hoja que se llama Cotización, esta aparece en el Excel llamado matriz
> y oferta.*

- **El Excel de matriz es INTERNO.** Tiene costos de compra, márgenes y
  utilidad. **Nunca se le manda al cliente**, ni completo ni por error.
- **Lo que ve el cliente es UNA sola pestaña**, exportada a PDF:
  `COTIZACIÓN ` —con acento y espacio al final— para contado, o
  `COTIZACION (Financ)` si la oferta va financiada (R13).

## Los pasos

### 1. Preguntar qué versión va

> *"¿Genero el PDF de contado, el financiado, o los dos?"*

Si la ficha del proyecto no tiene financiamiento, el financiado sale con
los montos en guión: no lo generes sin que lo pidan.

### 2. Verificar antes de exportar

1. **Que no queden celdas en error** en esa pestaña. Un `#¡VALOR!` en el
   PDF que ve el cliente es peor que no mandarlo.
2. **Que el impuesto sea el del cliente.** Sale de `Datos del proyecto`
   (R3). Casi un tercio de las cotizaciones van exentas: si la fila
   `IMPUESTO` dice 13% y la pestaña `Clientes` del catálogo le da otra
   tasa a ese cliente, pará y preguntá.
3. **Que el total cuadre** con lo registrado en los Excels de control. Al
   control va el **subtotal sin impuesto**; al cliente, el **total**. No
   son el mismo número.
4. **Que no queden textos del machote entre corchetes.** La firma (`B88`
   nombre del asesor, `B92` su correo) viene como `[Nombre del asesor
   responsable]` y `[correo del asesor]`: se llena en la matriz
   (`armar-cotizacion`), nunca solo en el PDF. El script no exporta si
   queda alguno visible.

### 3. Proponer nombre y ruta, y esperar confirmación

**El PDF va siempre en la misma carpeta que la matriz**, `Matriz-Oferta/`
(Fabián, 2026-10-28: *"el PDF debe ir en la misma carpeta de la
matriz"*). Nunca en otra carpeta, en Descargas o en un temporal, y nunca
solo mostrado en el chat: el chat es para revisarlo, la carpeta es donde
el equipo lo busca. El nombre, igual que los PDF reales que ya envió el
equipo (`T4-0000010-26 Equipos Edwards.pdf`):

```
<carpeta de la cotización>\Matriz-Oferta\<número de oferta> <descripción corta>.pdf
```

Si ya existe un PDF con ese nombre, **preguntá**: reemplazarlo, o
guardarlo con ` V2` al final, igual que se versiona la matriz. Mostrá la
ruta completa y esperá el sí: **es el documento que sale de la empresa.**
En una cotización nueva ese sí es el de la vista previa de montos (R25),
que ya mostraba el nombre del PDF: no se vuelve a preguntar.

⚠️ **Medí la ruta antes de proponerla: máximo 259 caracteres**, como la
matriz (Windows y Excel no abren una ruta más larga). La carpeta de la
cotización ya trae la descripción larga, así que en el PDF va corta. El
2026-10-27 la propuesta confirmada daba 263 y hubo que acortarla.

### 4. Exportar

Con [`scripts/exportar_pdf.ps1`](scripts/exportar_pdf.ps1) (2026-10-27):

```
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/exportar_pdf.ps1 -Matriz "<xlsx>" -Pdf "<pdf>" [-Financiada]
```

Hace lo de abajo y además se niega si hay celdas en error, corchetes sin
llenar, una ruta de más de 259 o un PDF que ya existe. Al final dice
cuántas páginas salieron, contadas en el PDF.

⚠️ **Los totales nunca se parten, y la escala la calcula el script**
(2026-10-27, dos cotizaciones reales):
- Con "ajustar a 1 página de ancho", una cotización de 3 líneas dejó
  subtotal e impuesto en la página 1 y el **TOTAL solo en la 2**.
- En otra, Excel calculaba 2 páginas y el PDF salió en 3, la última con
  solo el teléfono y el correo del pie. Excel mide con la impresora
  activa (en esta máquina, una de AnyDesk) y el PDF usa otras medidas.

Ahora el script mide las filas y elige:
1. **Si las líneas y los totales entran en la página 1 al 80% o más:**
   página 1 con encabezado, líneas y totales (salto manual después del
   TOTAL), y página 2 con forma de pago y firma, como los PDF reales.
2. **Si no:** las líneas siguen en la página 2 y el bloque de totales
   nunca se separa (si el salto cae ahí, la última línea pasa con los
   totales). Usa la escala más grande, entre 97% y 75%, que dé la menor
   cantidad de páginas.

Si el PDF igual sale con más páginas que las calculadas, baja la escala
de a 3% y lo dice. **Mirá siempre el PDF antes de darlo por bueno.**

Por Excel (COM), sobre la **hoja**. Nunca sobre el libro ni sobre las
hojas seleccionadas: `SelectedSheets` no tiene ese método y falla.

⚠️ **Hay que ocultar las líneas vacías antes de exportar.** La pestaña
trae espacio para 50 líneas; sin ocultarlas, una cotización de una sola
línea sale en **7 páginas**, cinco de ellas llenas de `0  $ -`. Se
ocultan **solo las filas cuya cantidad es exactamente cero**: el título
de sección ("Equipos") y la línea de asteriscos que separa los totales
no tienen cantidad numérica, y ocultarlas le quitaría información al
cliente.

⚠️ **Y se cierra SIN guardar.** Ocultar filas es solo para el PDF; la
matriz no se toca.

El código está en el script, que abre la matriz en solo lectura; la
financiada se busca con `'^COTIZACI.N \(Financ'`.

### 5. Mostrar el resultado y el correo (R25)

1. **Miralo vos primero** (por ejemplo, las páginas como imagen): líneas
   y totales juntos, firma completa, sin corchetes.
2. **Mostrale el PDF al asesor en el chat**, que lo pueda abrir y revisar
   ahí mismo, con la ruta en `Matriz-Oferta/` y cuántas páginas tiene. No
   basta con decir dónde quedó.
3. **Seguí con la vista previa del correo** para enviarlo:
   [`seguimiento-correo`](../seguimiento-correo/SKILL.md), modelo de
   cotización lista. Es parte de la entrega, no un extra que hay que
   pedir. El PDF se adjunta a mano y el correo lo manda una persona.

## Lo que este skill no hace nunca

- **Mandar la matriz**, ni completa ni una pestaña que no sea la de
  cotización.
- **Guardar la matriz** después de ocultar filas.
- **Generar el PDF sin que el asesor confirme** nombre y ruta (en una
  cotización nueva, la vista previa aceptada de R25 es esa confirmación).
- **Dejar el PDF fuera de la carpeta de la matriz**, o entregarlo solo en
  el chat.
- **Enviar el PDF.** Lo genera; el envío lo hace una persona.
