# Mejoras de presentacion del machote (pedido de Fabian, 2026-10-19). Se aplica
# una vez al machote de references/ y sirve para poner al dia una matriz vieja.
# No cambia ningun calculo de costo ni de precio. Excel por COM, nunca openpyxl.
#
#   powershell -File mejorar_diseno_matriz.ps1 -Ruta "<matriz.xlsx>" [-Guardar]
#
#   1. COTIZACION y COTIZACION (Financ), filas 22-71: un cero se ve en blanco
#      (formato con la seccion del cero vacia). Antes cada linea vacia de
#      Equipos se veia como una fila de ceros.
#   2. Financiamiento: cada cuadro con titulo de color, borde, formatos de
#      moneda y porcentaje, celdas editables en amarillo, y columnas con
#      ancho suficiente para que no se corten los nombres.
#   3. PTMO: si el importe del prestamo es 0 la tabla queda vacia (antes
#      mostraba 48 filas de ceros); formatos, colores y anchos.
#   4. Saca la pestana "Guia de skills" (vive en el catalogo desde el
#      2026-10-19) y su renglon en LEEME.
# Sin -Guardar es una prueba: aplica, verifica y cierra sin guardar.
param(
    [Parameter(Mandatory = $true)][string]$Ruta,
    [switch]$Guardar
)
$ErrorActionPreference = "Stop"
$EN_US = [System.Globalization.CultureInfo]::GetCultureInfo("en-US")
function Fmt($rango, $formato) { [void][System.__ComObject].InvokeMember("NumberFormat", [System.Reflection.BindingFlags]::SetProperty, $null, $rango, @($formato), $EN_US) }
function LeerFmt($rango) { return [string][System.__ComObject].InvokeMember("NumberFormat", [System.Reflection.BindingFlags]::GetProperty, $null, $rango, $null, $EN_US) }
function Color($r, $g, $b) { return [int]($r + 256 * $g + 65536 * $b) }
$AZUL = Color 31 56 100; $BLANCO = Color 255 255 255; $AMARILLO = Color 255 242 204; $GRIS = Color 191 191 191; $CELESTE = Color 221 235 247
$MONEDA = '[$$-409]#,##0.00'; $PORC = '0.00%'

# Cero en blanco: positivo;negativo;(vacio);texto, conservando el formato que ya tiene.
function FmtSinCero($f) {
    if ($f -eq "" -or $f -eq $null -or $f -eq "@") { $f = "General" }   # en formato texto un cero no se puede ocultar
    $s = $f.Split(";")
    if ($s.Count -eq 3 -and $s[2] -eq "") { return $f }
    if ($s.Count -ge 4 -and $s[2] -eq "") { return $f }
    $pos = $s[0]; $neg = $(if ($s.Count -ge 2) { $s[1] } else { "-" + $s[0] })
    $txt = $(if ($s.Count -ge 4) { $s[3] } else { "@" })
    return ("{0};{1};;{2}" -f $pos, $neg, $txt)
}
function SinCero($rango) {
    # celda por celda sobre su area combinada (la descripcion va combinada de C a H)
    foreach ($c in $rango.Cells) { $a = $c.MergeArea; if ($a.Cells.Item(1, 1).Address() -ne $c.Address()) { continue }; Fmt $a (FmtSinCero (LeerFmt $c)) }
}

$enOneDrive = $Ruta -like "*OneDrive*"
$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false; $excel.DisplayAlerts = $false; $excel.ScreenUpdating = $false
try {
    $wb = $excel.Workbooks.Open($Ruta)
    if ($wb.ReadOnly) { throw "el archivo esta abierto por alguien (solo lectura): no sigo" }
    $auto = $null; try { $auto = $wb.AutoSaveOn } catch { }
    if ($auto -eq $true) { [void][System.__ComObject].InvokeMember("AutoSaveOn", [System.Reflection.BindingFlags]::SetProperty, $null, $wb, @($false)) }
    $hojas = @{}; foreach ($w in $wb.Worksheets) { $hojas[$w.Name] = $w }
    $antes = @{}
    foreach ($par in @(@("COTIZACI*N ", "J76"), @("Equipos", "P57"), @("Financiamiento", "C4"))) {
        $w = ($hojas.Keys | Where-Object { $_ -like $par[0] } | Select-Object -First 1); if ($w) { $antes["$w!$($par[1])"] = $hojas[$w].Range($par[1]).Formula }
    }

    # --- 1. cotizaciones: cero en blanco ---
    foreach ($nombre in @($hojas.Keys | Where-Object { $_ -like "COTIZACI*" })) {
        $h = $hojas[$nombre]
        foreach ($col in @("B", "C", "I", "J")) { SinCero ($h.Range(("{0}22:{0}71" -f $col))) }
        # Aviso fuera del area de impresion: una fila oculta con monto suma en
        # el SUBTOTAL pero no aparece escrita. SUBTOTAL(109) ignora lo oculto.
        $h.Range("L74").Formula = '=IF(ROUND(SUM(J22:J71)-SUBTOTAL(109,J22:J71),2)<>0,"OJO: hay l"&UNICHAR(237)&"neas ocultas con monto. Mostralas: si no, suman pero no aparecen en la cotizaci"&UNICHAR(243)&"n.","")'
        $h.Range("L74").Font.Bold = $true; $h.Range("L74").Font.Color = (Color 192 0 0)
        Write-Output ("{0}: ceros en blanco en las lineas 22-71 y aviso de lineas ocultas en L74" -f $nombre.Trim())
    }

    # --- 2. Financiamiento ---
    if ($hojas.ContainsKey("Financiamiento")) {
        $f = $hojas["Financiamiento"]
        $bloques = @(@(1, "Equipos"), @(7, "Productos 2"), @(13, "MATERIALES"), @(19, "OPEX GV"))
        $f.Range("A1").Font.Bold = $true; $f.Range("A1").Font.Size = 14; $f.Range("A1").Font.Color = $AZUL
        $cuadros = 0
        foreach ($b in $bloques) {
            $s = $b[0]
            $f.Columns.Item($s).ColumnWidth = 5
            $f.Columns.Item($s + 1).ColumnWidth = 30
            $f.Columns.Item($s + 2).ColumnWidth = 15
            $f.Columns.Item($s + 3).ColumnWidth = 21
            $f.Columns.Item($s + 4).ColumnWidth = 13
            if ($s -lt 19) { $f.Columns.Item($s + 5).ColumnWidth = 3 }
            $enc = $f.Range($f.Cells.Item(2, $s), $f.Cells.Item(2, $s + 4))
            [void][System.__ComObject].InvokeMember("Value2", [System.Reflection.BindingFlags]::SetProperty, $null, $f.Cells.Item(2, $s + 1), @("Lineas de " + $b[1]))
            $enc.Font.Bold = $true; $enc.Interior.Color = $CELESTE
            $k = 0
            while ($true) {
                $r = 3 + 17 * $k
                if ([string]$f.Cells.Item($r, $s + 1).Value2 -notlike "CUADRO COSTOS*") { break }
                $caja = $f.Range($f.Cells.Item($r, $s), $f.Cells.Item($r + 15, $s + 4))
                $tit = $f.Range($f.Cells.Item($r, $s), $f.Cells.Item($r, $s + 4))
                $tit.Interior.Color = $AZUL; $tit.Font.Color = $BLANCO; $tit.Font.Bold = $true
                [void]$caja.BorderAround(1, -4138)
                foreach ($p in @(@(1, 2), @(2, 2), @(3, 2), @(5, 2), @(9, 2), @(9, 4), @(13, 2), @(15, 2))) { Fmt ($f.Cells.Item($r + $p[0], $s + $p[1])) $MONEDA }
                foreach ($p in @(@(1, 4), @(2, 4))) { Fmt ($f.Cells.Item($r + $p[0], $s + $p[1])) $PORC }
                foreach ($p in @(@(6, 2), @(7, 2))) { Fmt ($f.Cells.Item($r + $p[0], $s + $p[1])) "0" }
                foreach ($p in @(@(1, 4), @(2, 2), @(2, 4), @(3, 2), @(6, 2))) { $f.Cells.Item($r + $p[0], $s + $p[1]).Interior.Color = $AMARILLO }
                foreach ($p in @(@(5, 1), @(5, 2), @(9, 1), @(9, 2), @(9, 3), @(9, 4), @(15, 1), @(15, 2))) { $f.Cells.Item($r + $p[0], $s + $p[1]).Font.Bold = $true }
                $k++; $cuadros++
            }
        }
        $f.Activate(); $excel.ActiveWindow.FreezePanes = $false; [void]$f.Range("A3").Select(); $excel.ActiveWindow.FreezePanes = $true; [void]$f.Range("A1").Select()
        Write-Output ("Financiamiento: {0} cuadros con estilo" -f $cuadros)
    }

    # --- 3. PTMO ---
    if ($hojas.ContainsKey("PTMO")) {
        $p = $hojas["PTMO"]
        $p.Range("A19:A118").Formula = '=IF(AND(N($D$5)>0,ROW()-19+1<=$D$12),ROW()-19+1,"")'
        $p.Range("A1").Font.Bold = $true; $p.Range("A1").Font.Size = 14; $p.Range("A1").Font.Color = $AZUL
        foreach ($c in @("B4:D4", "I4:K4")) { $x = $p.Range($c); $x.Interior.Color = $AZUL; $x.Font.Color = $BLANCO; $x.Font.Bold = $true }
        [void]$p.Range("B4:D12").BorderAround(1, -4138); [void]$p.Range("I4:K12").BorderAround(1, -4138)
        $p.Range("D5:D11").Interior.Color = $AMARILLO
        Fmt ($p.Range("D5")) $MONEDA; Fmt ($p.Range("D10")) $MONEDA; Fmt ($p.Range("D6")) $PORC
        Fmt ($p.Range("D7:D8")) "0"; Fmt ($p.Range("D11:D12")) "0"; Fmt ($p.Range("D9")) "dd/mm/yyyy"
        Fmt ($p.Range("J5")) $MONEDA; Fmt ($p.Range("J8:J9")) $MONEDA; Fmt ($p.Range("K12")) $MONEDA; Fmt ($p.Range("J6:J7")) "0"
        $p.Range("K12").Font.Bold = $true; $p.Range("J5").Font.Bold = $true
        $tab = $p.Range("A17:J17"); $tab.Interior.Color = $AZUL; $tab.Font.Color = $BLANCO; $tab.Font.Bold = $true; $tab.WrapText = $true
        Fmt ($p.Range("B19:B118")) "dd/mm/yyyy"; Fmt ($p.Range("C19:J118")) $MONEDA; Fmt ($p.Range("A19:A118")) "0"
        $anchos = @{ 1 = 8; 2 = 13; 3 = 38; 4 = 15; 5 = 14; 6 = 14; 7 = 14; 8 = 13; 9 = 36; 10 = 15; 11 = 15 }
        foreach ($c in $anchos.Keys) { $p.Columns.Item($c).ColumnWidth = $anchos[$c] }
        $t = $p.Range("A19:J118")
        [void]$t.FormatConditions.Delete()
        try {
            $fc = $t.FormatConditions.Add(2, [System.Reflection.Missing]::Value, '=$A19<>""')
            $fc.Borders.Item(-4107).LineStyle = 1; $fc.Borders.Item(-4107).Color = $GRIS
        } catch { Write-Output ("AVISO PTMO: sin bordes condicionales ({0})" -f $_.Exception.Message) }
        Write-Output "PTMO: tabla vacia si el importe es 0, con formatos y estilo"
    }

    # --- 4. Guia de skills fuera ---
    if ($hojas.ContainsKey("Guia de skills")) {
        $hojas["Guia de skills"].Delete()
        Write-Output "Guia de skills: eliminada (vive en el catalogo)"
    }
    if ($hojas.ContainsKey("LEEME")) {
        $l = $hojas["LEEME"]
        foreach ($r in 1..60) { if ([string]$l.Cells.Item($r, 2).Value2 -eq "Guia de skills") { [void]$l.Range(("B{0}:C{0}" -f $r)).ClearContents(); Write-Output ("LEEME: renglon {0} de Guia de skills borrado" -f $r) } }
    }

    # --- verificacion ---
    $excel.CalculateFull()
    $mal = @()
    foreach ($k in $antes.Keys) { $w, $c = $k.Split("!"); if ($wb.Worksheets.Item($w).Range($c).Formula -ne $antes[$k]) { $mal += "cambio la formula de $k" } }
    $err = 0
    foreach ($w in $wb.Worksheets) { if ($w.Visible -ne -1) { continue }; try { $x = $w.UsedRange.SpecialCells(-4123, 16); $err += $x.Count; Write-Output ("errores en [{0}]: {1}" -f $w.Name, $x.Count) } catch { } }
    if ($err -gt 0) { $mal += "$err celdas con error" }
    Write-Output ("verificacion: formulas clave iguales, errores {0}" -f $err)
    if ($mal.Count -gt 0) { foreach ($x in $mal) { Write-Output ("  MAL: " + $x) }; throw "quedo algo mal, NO se guarda" }
    if ($Guardar) { $wb.Save(); Write-Output "GUARDADO" } else { Write-Output "prueba: no se guarda" }
    $wb.Close($false)
}
finally {
    $excel.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($excel) | Out-Null
    [GC]::Collect(); [GC]::WaitForPendingFinalizers()
}
if ($Guardar -and $enOneDrive) {
    $sh = New-Object -ComObject Shell.Application
    for ($i = 0; $i -lt 24; $i++) { Start-Sleep -Seconds 5; $st = $sh.Namespace((Split-Path -Parent $Ruta)).ParseName((Split-Path -Leaf $Ruta)).ExtendedProperty("System.StorageProviderState"); if ($st -eq 2) { break } }
    Write-Output ("OneDrive: estado {0}" -f $st)
}
