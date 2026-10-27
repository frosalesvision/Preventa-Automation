# Ajuste del machote pedido por Fabian despues de la demo a gerencia (2026-10-27). Se aplica una
# vez al machote de references/ y sirve para poner al dia una matriz vieja. Excel por COM, nunca openpyxl.
#
#   powershell -NoProfile -ExecutionPolicy Bypass -File ajustar_materiales_viaticos.ps1 -Ruta "<matriz.xlsx>" [-Guardar]
#
#   1. MATERIALES llega a la cotizacion. El gerente: el cable de fibra (los materiales de
#      instalacion) va en MATERIALES, no en OPEX GV. Hasta hoy MATERIALES no llegaba a
#      COTIZACION, por eso los materiales terminaban en OPEX. Ahora la linea de la fila 72 suma
#      OPEX GV + MATERIALES (el texto dice que incluye materiales cuando los hay), y el control
#      K74/L75 tambien los cuenta.
#   2. MANO DE OBRA: combustible por viaje y hospedaje por noche. Antes los dos se multiplicaban
#      por los dias: "35 mil colones ida y vuelta" en 2 dias se veia como $35,71 por dia, y "$200
#      la noche" como $100. Se insertan tres columnas despues de Total (L:N):
#        L Viajes (ida y vuelta)   M Noches de hospedaje   N Combustible por viaje en colones
#      Vacias, viajes y noches valen lo mismo que los dias (el calculo de siempre). Si N tiene
#      colones, el combustible (I) se calcula con el tipo de cambio de Datos del proyecto!B47.
# Sin -Guardar es una prueba: aplica, verifica y cierra sin guardar.
param(
    [Parameter(Mandatory = $true)][string]$Ruta,
    [switch]$Guardar
)
$ErrorActionPreference = "Stop"
$EN_US = [System.Globalization.CultureInfo]::GetCultureInfo("en-US")
function Fmt($rango, $formato) { [void][System.__ComObject].InvokeMember("NumberFormat", [System.Reflection.BindingFlags]::SetProperty, $null, $rango, @($formato), $EN_US) }
function Formula($celda, $f) {
    # en una celda con formato "@" la formula quedaria guardada como texto; las demas conservan su formato
    $actual = [string][System.__ComObject].InvokeMember("NumberFormat", [System.Reflection.BindingFlags]::GetProperty, $null, $celda, $null, $EN_US)
    if ($actual -eq "@") { Fmt $celda "General" }
    $celda.Formula = $f
    if (-not $celda.HasFormula) { throw ("{0} no quedo como formula" -f $celda.Address(0, 0)) }
}
function Color($r, $g, $b) { return [int]($r + 256 * $g + 65536 * $b) }

$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false; $excel.DisplayAlerts = $false; $excel.ScreenUpdating = $false
try {
    $wb = $excel.Workbooks.Open($Ruta)
    if ($wb.ReadOnly) { throw "el archivo esta abierto por alguien (solo lectura): no sigo" }
    $auto = $null; try { $auto = $wb.AutoSaveOn } catch { }
    if ($auto -eq $true) { [void][System.__ComObject].InvokeMember("AutoSaveOn", [System.Reflection.BindingFlags]::SetProperty, $null, $wb, @($false)) }
    $hojas = @{}; foreach ($w in $wb.Worksheets) { $hojas[$w.Name] = $w }
    $mo = $hojas["MANO DE OBRA "]; $op = $hojas["OPEX GV"]; $mat = $hojas["MATERIALES"]
    $cot = $hojas[@($hojas.Keys | Where-Object { $_ -like "COTIZACI*N " })[0]]
    $antes = @{ "OPEX GV!D6" = $op.Range("D6").Formula; "Equipos!P57" = $hojas["Equipos"].Range("P57").Formula; "MATERIALES!O46" = $mat.Range("O46").Formula; "COT!J74" = $cot.Range("J74").Formula; "COT!J76" = $cot.Range("J76").Formula }

    # --- 1. MATERIALES en la linea 72 de la cotizacion ---
    if (([string]$cot.Range("I72").Formula) -notlike "*OPEX GV*") { throw "la fila 72 de COTIZACION no es la linea de OPEX: correr antes mejorar_diseno_matriz.ps1" }
    Formula $cot.Range("I72") "='OPEX GV'!O17+MATERIALES!O46"
    Formula $cot.Range("B72") "=IF(I72>0,1,0)"
    $ins = '"Instalaci"&UNICHAR(243)&"n, configuraci"&UNICHAR(243)&"n y puesta en marcha de los equipos ofertados'
    [void]$cot.Range("C72").MergeArea.ClearContents()
    Formula $cot.Range("C72") ("=IF(AND('OPEX GV'!O17>0,MATERIALES!O46>0)," + $ins + ' (mano de obra y materiales)",IF(MATERIALES!O46>0,"Materiales de instalaci"&UNICHAR(243)&"n",' + $ins + '"))')
    Formula $cot.Range("K74") "=+Equipos!P57+'OPEX GV'!O17+MATERIALES!O46"
    Formula $cot.Range("L75") '=IF(ROUND(J74-K74,2)<>0,"OJO: el SUBTOTAL no da Equipos + OPEX GV + MATERIALES ("&TEXT(K74,"#,##0.00")&"). Revis"&UNICHAR(225)&" las l"&UNICHAR(237)&"neas.","")'
    $cot.Range("L75").Font.Bold = $true; $cot.Range("L75").Font.Color = (Color 192 0 0)
    Write-Output "COTIZACION: la fila 72 suma OPEX GV + MATERIALES; control K74/L75 con MATERIALES"

    # --- 2. MANO DE OBRA: viajes, noches y combustible en colones ---
    if ([string]$mo.Range("L4").Value2 -ne "Viajes") {
        if ([string]$mo.Range("K4").Value2 -ne "Total") { throw "MANO DE OBRA K4 no es Total: la hoja no es la esperada" }
        [void]$mo.Range("L:N").EntireColumn.Insert()
        Write-Output "MANO DE OBRA: tres columnas insertadas en L:N (las notas de la derecha se corrieron)"
    }
    $mo.Range("I4").Value2 = "Combustible por viaje"
    $mo.Range("J4").Value2 = "Hospedaje por noche"
    $mo.Range("L4").Value2 = "Viajes"
    $mo.Range("M4").Value2 = "Noches"
    $mo.Range("N4").Value2 = "Combustible por viaje en colones"
    $mo.Range("L3").Value2 = "Si quedan vacios, viajes y noches = dias"
    [void]$mo.Range("K4").Copy(); [void]$mo.Range("L4:N4").PasteSpecial(-4122)
    [void]$mo.Range("H5:H8").Copy(); [void]$mo.Range("L5:N8").PasteSpecial(-4122)
    [void][System.__ComObject].InvokeMember("CutCopyMode", [System.Reflection.BindingFlags]::SetProperty, $null, $excel, @($false))
    $mo.Range("L4:N4").WrapText = $true
    $mo.Range("L3").WrapText = $true; $mo.Range("L3").Font.Italic = $true
    $mo.Columns.Item(12).ColumnWidth = 10; $mo.Columns.Item(13).ColumnWidth = 10; $mo.Columns.Item(14).ColumnWidth = 16
    Fmt ($mo.Range("L5:M8")) "0;-0;;@"
    Fmt ($mo.Range("N5:N8")) '#,##0;-#,##0;;@'
    foreach ($r in 5..8) {
        Formula $mo.Range("K$r") ("=(H{0}*E{0}*F{0})+(I{0}*IF(L{0}=`"`",E{0},L{0}))+(J{0}*IF(M{0}=`"`",E{0},M{0}))" -f $r)
    }
    Formula $mo.Range("I5") "=IF(N5<>`"`",N5/'Datos del proyecto'!`$B`$47,Transporte!I3)"
    # la nota vieja del hospedaje (se corrio de M8 a P8)
    foreach ($c in @($mo.Range("P1:P40").Cells)) {
        if ([string]$c.Value2 -like "OJO: el hospedaje*") { $c.Value2 = "El hospedaje (col. J) es el costo de UNA noche para todo el equipo, por las noches de la col. M. El combustible (col. I) es por viaje de ida y vuelta, por los viajes de la col. L; si te lo dan en colones, va en la col. N." }
    }
    Write-Output "MANO DE OBRA: combustible por viaje x viajes, hospedaje por noche x noches, colones en N"

    # --- verificacion ---
    $excel.CalculateFull()
    $mal = @()
    if ($op.Range("D6").Formula -ne $antes["OPEX GV!D6"]) { $mal += "cambio OPEX GV!D6: " + $op.Range("D6").Formula }
    foreach ($k in @("Equipos!P57", "MATERIALES!O46")) { $w, $c = $k.Split("!"); if ($hojas[$w].Range($c).Formula -ne $antes[$k]) { $mal += "cambio $k" } }
    if ($cot.Range("J74").Formula -ne $antes["COT!J74"] -or $cot.Range("J76").Formula -ne $antes["COT!J76"]) { $mal += "cambio el SUBTOTAL o el TOTAL de la cotizacion" }
    $err = 0
    foreach ($w in $wb.Worksheets) { if ($w.Visible -ne -1) { continue }; try { $x = $w.UsedRange.SpecialCells(-4123, 16); $err += $x.Count; Write-Output ("errores en [{0}]: {1} ({2})" -f $w.Name, $x.Count, $x.Address(0, 0)) } catch { } }
    if ($err -gt 0) { $mal += "$err celdas con error" }
    Write-Output ("verificacion: OPEX GV!D6 = {0}; K5 = {1}; I72 = {2}; errores {3}" -f $op.Range("D6").Formula, $mo.Range("K5").Formula, $cot.Range("I72").Formula, $err)
    if ($mal.Count -gt 0) { foreach ($x in $mal) { Write-Output ("  MAL: " + $x) }; throw "quedo algo mal, NO se guarda" }
    if ($Guardar) { $wb.Save(); Write-Output "GUARDADO" } else { Write-Output "prueba: no se guarda" }
    $wb.Close($false)
}
finally {
    $excel.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($excel) | Out-Null
    [GC]::Collect(); [GC]::WaitForPendingFinalizers()
}
