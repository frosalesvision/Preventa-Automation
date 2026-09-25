---
name: generar-pdf-cotizacion
description: Genera el PDF que se le manda al cliente, exportando SOLO la pestaña de cotización de la matriz (la de contado o la financiada), después de verificar que no haya errores, que el impuesto sea el del cliente y que el total cuadre, y de confirmar con el asesor el nombre y la ruta del archivo. Usar cuando el asesor dice que la cotización está lista/terminada y hay que generar el PDF para enviarla.
---

# Generar PDF de cotización

**Estado: funcional.** Probado el 2026-09-25 sobre una copia del machote,
con una línea de prueba: sale en 2 páginas —cotización y totales, después
forma de pago y firma—, igual que los PDF reales que envía preventa, y la
matriz queda intacta. **Falta usarlo con una cotización real.**

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
   `IMPUESTO` dice 13% y el cliente es de la tabla de régimen fiscal con
   otra tasa, pará y preguntá.
3. **Que el total cuadre** con lo registrado en los Excels de control. Al
   control va el **subtotal sin impuesto**; al cliente, el **total**. No
   son el mismo número.

### 3. Proponer nombre y ruta, y esperar confirmación

Por defecto, igual que los PDF reales que ya envió el equipo
(`T4-0000010-26 Equipos Edwards.pdf`):

```
<carpeta de la cotización>\Matriz-Oferta\<número de oferta> <descripción corta>.pdf
```

Si ya existe un PDF con ese nombre, **preguntá**: reemplazarlo, o
guardarlo con ` V2` al final, igual que se versiona la matriz. Mostrá la
ruta completa y esperá el sí: **es el documento que sale de la empresa.**

### 4. Exportar

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

```powershell
$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false; $excel.DisplayAlerts = $false
try {
    $wb = $excel.Workbooks.Open($rutaMatriz)
    $h = $null
    foreach ($w in $wb.Worksheets) {
        # contado: '^COTIZACI.N$'   financiada: '^COTIZACI.N \(Financ'
        if ($w.Name.Trim() -match '^COTIZACI.N$') { $h = $w }
    }
    # el bloque de lineas va del encabezado "Cantidad" a la fila del SUBTOTAL
    $primera = 0; $ultima = 0
    for ($r = 1; $r -le 120; $r++) {
        if ($primera -eq 0 -and ([string]$h.Cells.Item($r, 2).Value2).Trim() -eq "Cantidad") { $primera = $r + 1 }
        if ($ultima -eq 0) {
            for ($c = 1; $c -le 12; $c++) {
                if (([string]$h.Cells.Item($r, $c).Value2).Trim() -eq "SUBTOTAL") { $ultima = $r - 1; break }
            }
        }
    }
    for ($r = $primera; $r -le $ultima; $r++) {
        $q = $h.Cells.Item($r, 2).Value2
        if (($q -is [double]) -and ($q -eq 0)) { $h.Rows.Item($r).Hidden = $true }
    }
    $h.PageSetup.Orientation    = 2        # horizontal
    $h.PageSetup.Zoom           = $false
    $h.PageSetup.FitToPagesWide = 1
    $h.PageSetup.FitToPagesTall = $false
    $h.ExportAsFixedFormat(0, $rutaPdf)
    $wb.Close($false)                      # SIN guardar
}
finally {
    $excel.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($excel) | Out-Null
}
```

### 5. Confirmar el resultado

Decile al asesor la ruta del PDF y cuántas páginas tiene, y recordale
revisarlo antes de enviarlo. Si va a mandarlo por correo,
[`seguimiento-correo`](../seguimiento-correo/SKILL.md) redacta el texto;
el PDF se adjunta a mano.

## Lo que este skill no hace nunca

- **Mandar la matriz**, ni completa ni una pestaña que no sea la de
  cotización.
- **Guardar la matriz** después de ocultar filas.
- **Generar el PDF sin que el asesor confirme** nombre y ruta.
- **Enviar el PDF.** Lo genera; el envío lo hace una persona.
