# Escribe la pestana "Compatibilidad de Accesorios" del catalogo por Excel
# (COM), con los pares que calculo generar_matriz_accesorios.py. Reemplaza
# solo las filas de la tabla y la seccion de la "Guia de columnas"; no toca
# ninguna otra pestana. COM y no openpyxl: openpyxl borra los desplegables.
#
# Uso:
#   python generar_matriz_accesorios.py "<catalogo.xlsx>" "<pares.json>"
#   powershell -File escribir_matriz_accesorios.ps1 -Ruta "<catalogo.xlsx>" -Datos "<pares.json>"            (prueba)
#   powershell -File escribir_matriz_accesorios.ps1 -Ruta "<catalogo.xlsx>" -Datos "<pares.json>" -Guardar   (de verdad)
#
# Sin -Guardar es una prueba. Siempre saca respaldo y apaga el Autoguardado.
# Codigo solo ASCII: PowerShell 5.1 lee como ANSI un .ps1 sin BOM; los
# textos con acentos vienen del JSON.
param(
    [Parameter(Mandatory = $true)][string]$Ruta,
    [Parameter(Mandatory = $true)][string]$Datos,
    [switch]$Guardar
)
$ErrorActionPreference = "Stop"
$HOJA = "Compatibilidad de Accesorios"

# Guardar en esta PC no es guardar en la nube (2026-10-06): sin OneDrive
# corriendo, o con el archivo a medio sincronizar, no se escribe.
if (-not (Get-Process OneDrive -ErrorAction SilentlyContinue)) { throw "OneDrive no esta corriendo: lo que se guarde no llega a la nube. Abrilo y volve a correr." }
$fi = Get-Item -LiteralPath $Ruta
$shell = New-Object -ComObject Shell.Application
$estado = $shell.Namespace($fi.DirectoryName).ParseName($fi.Name).ExtendedProperty("System.StorageProviderState")
if ($estado -ne 2) { throw ("El catalogo no esta sincronizado con la nube (estado {0}). Esperar a que OneDrive termine." -f $estado) }

$D = Get-Content -LiteralPath $Datos -Raw -Encoding UTF8 | ConvertFrom-Json
$filas = @($D.filas); $n = $filas.Count
if ($n -lt 1) { throw "el JSON no trae pares" }
$bak = Join-Path $env:TEMP ("catalogo_antes_compatibilidad_{0}.xlsx" -f (Get-Date -Format "yyyyMMdd_HHmmss"))
Copy-Item -LiteralPath $Ruta $bak
Write-Output ("respaldo: {0}" -f $bak)

$EN_US = [System.Globalization.CultureInfo]::GetCultureInfo("en-US")
function PonerBloque($rango, $arr) { [void][System.__ComObject].InvokeMember("Value2", [System.Reflection.BindingFlags]::SetProperty, $null, $rango, @(, $arr)) }
function Poner($celda, $valor) { [void][System.__ComObject].InvokeMember("Value2", [System.Reflection.BindingFlags]::SetProperty, $null, $celda, @(, $valor)) }
function PonerFormato($rango, $formato) { [void][System.__ComObject].InvokeMember("NumberFormat", [System.Reflection.BindingFlags]::SetProperty, $null, $rango, @($formato), $EN_US) }
function PonerProp($obj, $prop, $valor) { [void][System.__ComObject].InvokeMember($prop, [System.Reflection.BindingFlags]::SetProperty, $null, $obj, @($valor)) }
function Txt($v) { if ($v -eq $null) { return "" } return ([string]$v).Trim() }

$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false; $excel.DisplayAlerts = $false
try {
    $wb = $excel.Workbooks.Open($Ruta)
    $auto = $null; try { $auto = $wb.AutoSaveOn } catch { }
    if ($auto -eq $true) { PonerProp $wb "AutoSaveOn" $false; if ($wb.AutoSaveOn -ne $false) { throw "no pude apagar el Autoguardado" }; Write-Output "Autoguardado apagado" }
    $activa = $wb.ActiveSheet.Name
    $h = $wb.Worksheets.Item($HOJA)
    $enc = @($D.encabezados)
    for ($c = 1; $c -le 10; $c++) { if ((Txt $h.Cells.Item(1, $c).Value2) -ne $enc[$c - 1]) { throw ("la columna {0} de la pestana no es '{1}': no sigo" -f $c, $enc[$c - 1]) } }
    if ($h.ListObjects.Count -ne 1) { throw "la pestana no tiene exactamente una tabla" }
    $lo = $h.ListObjects.Item(1)
    $nViejo = $lo.ListRows.Count
    $cat = $wb.Worksheets.Item("Catalogo")
    $nCat = $cat.ListObjects.Item("TablaCatalogo").ListRows.Count
    $valAntes = @(); foreach ($dir in "D2", "E2") { try { $valAntes += $cat.Range($dir).Validation.Type } catch { $valAntes += "sin" } }

    # --- 1. las filas de la tabla
    if ($lo.DataBodyRange -ne $null) { [void]$lo.DataBodyRange.ClearContents() }
    [void]$lo.Resize($h.Range($h.Cells.Item(1, 1), $h.Cells.Item($n + 1, 10)))
    if ($nViejo -gt $n) { [void]$h.Range($h.Cells.Item($n + 2, 1), $h.Cells.Item($nViejo + 1, 10)).Clear() }
    # los modelos como texto ANTES de escribir: "02939-001" o "5800-931" no son numeros
    PonerFormato ($h.Range($h.Cells.Item(2, 1), $h.Cells.Item($n + 1, 1))) "@"
    PonerFormato ($h.Range($h.Cells.Item(2, 4), $h.Cells.Item($n + 1, 4))) "@"
    $rg = $h.Range($h.Cells.Item(2, 1), $h.Cells.Item($n + 1, 10)); $arr = $rg.Value2
    for ($i = 0; $i -lt $n; $i++) {
        $f = @($filas[$i])
        for ($c = 0; $c -lt 10; $c++) {
            $v = $f[$c]
            if ($v -eq $null -or ([string]$v).Trim() -eq "") { $arr[($i + 1), ($c + 1)] = $null } else { $arr[($i + 1), ($c + 1)] = [string]$v }
        }
    }
    PonerBloque $rg $arr
    $h.Columns.Item(9).ColumnWidth = 40
    $h.Columns.Item(10).ColumnWidth = 90
    $h.Activate(); $w = $excel.ActiveWindow; $w.FreezePanes = $false; $w.ScrollRow = 1; $w.ScrollColumn = 1
    [void]$h.Range("A2").Select(); $w.FreezePanes = $true
    Write-Output ("pares: {0} (antes {1})" -f $n, $nViejo)

    # --- 2. la seccion de la Guia de columnas
    $g = $wb.Worksheets.Item("Guia de columnas"); $rG = $null
    for ($r = 1; $r -le 400; $r++) { if ((Txt $g.Cells.Item($r, 1).Value2) -like ("Pesta*" + $HOJA)) { $rG = $r; break } }
    if (-not $rG) { throw "no encontre la seccion de la pestana en la Guia de columnas" }
    Poner ($g.Cells.Item($rG + 1, 1)) ([string]$D.guia.descripcion)
    $cambiadas = 0
    for ($r = $rG + 3; $r -le $rG + 15; $r++) {
        $col = Txt $g.Cells.Item($r, 2).Value2
        if ($col -eq "") { break }
        $t = $D.guia.$col
        if ($t) { Poner ($g.Cells.Item($r, 3)) ([string]$t[0]); Poner ($g.Cells.Item($r, 4)) ([string]$t[1]); $cambiadas++ }
    }
    if ($cambiadas -ne 3) { throw ("en la Guia cambie {0} filas, esperaba 3" -f $cambiadas) }
    $wb.Worksheets.Item($activa).Activate()

    # --- 3. verificacion
    $excel.CalculateFull()
    $mal = @()
    if ($lo.ListRows.Count -ne $n) { $mal += ("la tabla quedo con {0} filas" -f $lo.ListRows.Count) }
    for ($c = 1; $c -le 10; $c++) { if ((Txt $h.Cells.Item(1, $c).Value2) -ne $enc[$c - 1]) { $mal += "cambio un encabezado" } }
    $distintas = 0
    foreach ($i in @(0, [int]($n / 3), [int]($n / 2), ($n - 1))) {
        $f = @($filas[$i])
        for ($c = 0; $c -lt 10; $c++) { if ((Txt $h.Cells.Item($i + 2, $c + 1).Value2) -ne (Txt $f[$c])) { $distintas++ } }
    }
    if ($distintas -gt 0) { $mal += ("{0} celdas de muestra no coinciden con el JSON" -f $distintas) }
    if ((Txt $h.Cells.Item($n + 2, 1).Value2) -ne "") { $mal += "quedo algo debajo de la tabla" }
    if ($cat.ListObjects.Item("TablaCatalogo").ListRows.Count -ne $nCat) { $mal += "cambio el catalogo de productos" }
    $valDespues = @(); foreach ($dir in "D2", "E2") { try { $valDespues += $cat.Range($dir).Validation.Type } catch { $valDespues += "sin" } }
    if (($valAntes -join ",") -ne ($valDespues -join ",")) { $mal += "cambiaron los desplegables del catalogo" }
    $err = 0; foreach ($s in @($HOJA, "Catalogo", "Guia de columnas")) { try { $z = $wb.Worksheets.Item($s).UsedRange.SpecialCells(-4123, 16); if ($z -ne $null) { $err += $z.Count } } catch { } }
    if ($err -gt 0) { $mal += ("{0} celdas con error" -f $err) }
    Write-Output ("verificacion: filas {0}; productos {1}; desplegables {2}; errores {3}" -f $lo.ListRows.Count, $nCat, ($valDespues -join "/"), $err)
    if ($mal.Count -gt 0) { foreach ($x in $mal) { Write-Output ("  MAL: " + $x) }; throw "quedo algo mal, NO se guarda" }
    if ($Guardar) { $wb.Save(); Write-Output "GUARDADO" } else { Write-Output "prueba: no se guarda" }
    $wb.Close($false)
}
finally {
    $excel.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($excel) | Out-Null
    [GC]::Collect(); [GC]::WaitForPendingFinalizers()
}
