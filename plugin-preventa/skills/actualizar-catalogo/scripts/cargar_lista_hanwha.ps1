# Carga al catalogo lo que dejo preparar_lista_hanwha.py. Escribe por Excel (COM),
# nunca con openpyxl (borra los desplegables). Sin -Guardar es una prueba: escribe,
# verifica y cierra sin guardar.
#
#   powershell -NoProfile -ExecutionPolicy Bypass -File cargar_lista_hanwha.ps1 -Ruta "<catalogo.xlsx>" -Datos "<carga.json>" [-Guardar]
#
# Hace, en este orden:
#   1. Actualiza las filas que siguen vigentes, solo si tienen el mismo codigo,
#      proveedor y precio que cuando se preparo la carga.
#   2. Quita las que pasaron a EOL, con la misma condicion (de abajo hacia arriba).
#   3. Agrega las nuevas al final de TablaCatalogo, con sus formulas y desplegables.
#   4. Verifica antes de guardar: cantidad de filas, celdas con error, que ninguna
#      fila fuera de la carga haya cambiado, que cada fila del proveedor quede con
#      precio de compra = lista x (1 - descuento).
# Respaldo siempre, Autoguardado apagado, OneDrive corriendo y el archivo
# sincronizado antes de escribir; al guardar, verificar_onedrive.ps1 (R26).
param(
    [Parameter(Mandatory = $true)][string]$Ruta,
    [Parameter(Mandatory = $true)][string]$Datos,
    [switch]$Guardar
)
$ErrorActionPreference = "Stop"
$EN_US = [System.Globalization.CultureInfo]::GetCultureInfo("en-US")
$TEXTO = @("U", "V", "W", "X")     # codigos: si no van como texto, Excel los vuelve numeros
function Poner($celda, $valor) { [void][System.__ComObject].InvokeMember("Value2", [System.Reflection.BindingFlags]::SetProperty, $null, $celda, @(, $valor)) }
function PonerFormato($rango, $formato) { [void][System.__ComObject].InvokeMember("NumberFormat", [System.Reflection.BindingFlags]::SetProperty, $null, $rango, @($formato), $EN_US) }
function SinCopiar($app) { [void][System.__ComObject].InvokeMember("CutCopyMode", [System.Reflection.BindingFlags]::SetProperty, $null, $app, @($false)) }
function Txt($v) { if ($v -eq $null) { return "" } return ([string]$v).Trim() }
function Clave($s) { return ([string]$s).ToUpper() -replace "[^A-Z0-9]", "" }
function Igual($a, $b) {
    if (($a -eq $null -or "$a" -eq "") -and ($b -eq $null -or "$b" -eq "")) { return $true }
    if ($a -eq $null -or $b -eq $null) { return $false }
    if ($a -is [double] -or $a -is [int]) { if ($b -is [double] -or $b -is [int]) { return [math]::Abs([double]$a - [double]$b) -lt 0.005 } }
    return (Txt $a) -eq (Txt $b)
}
function EstadoNube($ruta) {
    $sh = New-Object -ComObject Shell.Application
    return $sh.Namespace((Split-Path -Parent $ruta)).ParseName((Split-Path -Leaf $ruta)).ExtendedProperty("System.StorageProviderState")
}
# El valor tal cual para la celda: numero si es numero, texto (sin riesgo de formula) si no
function Valor($v) {
    if ($v -eq $null) { return $null }
    if ($v -is [string]) {
        if ($v -match '^[=+\-@]') { return "'" + $v }
        return $v
    }
    return [double]$v
}
function Escribir($hoja, $letra, $fila, $v) {
    $c = $hoja.Range(("{0}{1}" -f $letra, $fila))
    if ($TEXTO -contains $letra -and $v -ne $null) { PonerFormato $c "@"; Poner $c ([string]$v) }
    else { Poner $c (Valor $v) }
}

$enOneDrive = $Ruta -like "*OneDrive*"
if ($enOneDrive) {
    if (-not (Get-Process OneDrive -ErrorAction SilentlyContinue)) { throw "OneDrive no esta corriendo: no escribo" }
    $st = EstadoNube $Ruta
    if ($st -ne 2) { throw ("el catalogo no esta sincronizado (estado {0}): no escribo" -f $st) }
    Write-Output "OneDrive corriendo y catalogo sincronizado"
}
$D = Get-Content -LiteralPath $Datos -Raw -Encoding UTF8 | ConvertFrom-Json
$bak = Join-Path $env:TEMP ("catalogo_antes_lista_hanwha_{0}.xlsx" -f (Get-Date -Format "yyyyMMdd_HHmmss"))
Copy-Item -LiteralPath $Ruta $bak
Write-Output ("respaldo: {0}" -f $bak)
$mtime0 = (Get-Item -LiteralPath $Ruta).LastWriteTimeUtc

$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false; $excel.DisplayAlerts = $false; $excel.ScreenUpdating = $false
try {
    $wb = $excel.Workbooks.Open($Ruta)
    if ($wb.ReadOnly) { throw "el catalogo esta abierto por alguien: no sigo" }
    $auto = $null; try { $auto = $wb.AutoSaveOn } catch { }
    if ($auto -eq $true) {
        [void][System.__ComObject].InvokeMember("AutoSaveOn", [System.Reflection.BindingFlags]::SetProperty, $null, $wb, @($false))
        if ($wb.AutoSaveOn -ne $false) { throw "no pude apagar el Autoguardado: no sigo" }
        Write-Output "Autoguardado apagado para esta corrida"
    }
    $excel.Calculation = -4135   # manual mientras escribe; al final se recalcula todo
    $h = $wb.Worksheets.Item("Catalogo")
    $lo = $h.ListObjects.Item("TablaCatalogo")
    $n0 = $lo.ListRows.Count
    $encab = @(); foreach ($c in $lo.ListColumns) { $encab += $c.Name }
    if ($encab.Count -ne 28 -or $encab[2] -ne "Modelo / SKU" -or $encab[5] -ne "Proveedor" -or $encab[6] -notlike "Precio de lista*USD*" -or $encab[27] -ne "Tipo de precio cargado") { throw ("el catalogo cambio de forma: {0}" -f ($encab -join " | ")) }
    $valD2 = $h.Range("D2").Validation.Formula1; $valE2 = $h.Range("E2").Validation.Formula1
    $aC = $lo.ListColumns.Item(3).DataBodyRange.Value2; $aF = $lo.ListColumns.Item(6).DataBodyRange.Value2
    $aG = $lo.ListColumns.Item(7).DataBodyRange.Value2; $aI = $lo.ListColumns.Item(9).DataBodyRange.Value2
    $aK = $lo.ListColumns.Item(11).DataBodyRange.Value2
    Write-Output ("catalogo antes: {0} filas" -f $n0)

    # --- 1. actualizaciones ---
    $actualizadas = @{}; $noA = 0; $hechas = 0
    foreach ($a in $D.actualizar) {
        $r = [int]$a.fila; $i = $r - 1
        if ($i -lt 1 -or $i -gt $n0 -or (Clave $aC[$i, 1]) -ne (Clave $a.sku) -or (Txt $aF[$i, 1]) -ne $D.proveedor -or -not (Igual $aG[$i, 1] $a.antes.G)) {
            $noA++; Write-Output ("AVISO fila {0} ({1}): cambio desde que se preparo la carga, no se toca" -f $r, $a.sku); continue
        }
        foreach ($p in $a.cambios.PSObject.Properties) { Escribir $h $p.Name $r $p.Value }
        $actualizadas[$r] = $a; $hechas++
    }
    Write-Output ("actualizadas: {0}; no tocadas porque cambiaron: {1}" -f $hechas, $noA)

    # --- 2. las que pasaron a EOL ---
    $quitadas = @{}; $noQ = 0
    foreach ($q in ($D.quitar | Sort-Object { [int]$_.fila } -Descending)) {
        $r = [int]$q.fila; $i = $r - 1
        if ($i -lt 1 -or $i -gt $n0 -or (Clave $aC[$i, 1]) -ne (Clave $q.sku) -or (Txt $aF[$i, 1]) -ne $D.proveedor -or -not (Igual $aG[$i, 1] $q.G)) {
            $noQ++; Write-Output ("AVISO fila {0} ({1}): cambio desde que se preparo la carga, no se quita" -f $r, $q.sku); continue
        }
        $lo.ListRows.Item($i).Delete()
        $quitadas[$r] = $true
    }
    Write-Output ("quitadas: {0}; no quitadas porque cambiaron: {1}" -f $quitadas.Count, $noQ)

    # --- 3. filas nuevas ---
    $n1 = $lo.ListRows.Count; $ult = $n1 + 1; $n = @($D.filas).Count; $ini = $ult + 1; $fin = $ult + $n
    if ($n -gt 0) {
        if ($excel.WorksheetFunction.CountA($h.Range(("A{0}:AB{1}" -f $ini, $fin))) -ne 0) { throw "hay datos debajo de la tabla: no se agrega nada" }
        $lo.Resize($h.Range(("A1:AB{0}" -f $fin)))
        [void]$h.Range(("A{0}:AB{0}" -f $ult)).Copy()
        [void]$h.Range(("A{0}:AB{1}" -f $ini, $fin)).PasteSpecial(-4122)
        SinCopiar $excel
        PonerFormato ($h.Range(("C{0}:C{1}" -f $ini, $fin))) "@"
        $r = $ini
        foreach ($f in $D.filas) {
            foreach ($p in $f.PSObject.Properties) { if ($p.Value -ne $null) { Escribir $h $p.Name $r $p.Value } }
            $r++
        }
        $h.Range(("H{0}:H{1}" -f $ini, $fin)).Formula = ('=IF(G{0}="","",IF(TipoCambioVenta="","Actualizar TC",ROUND(G{0}*TipoCambioVenta,2)))' -f $ini)
        $h.Range(("I{0}:I{1}" -f $ini, $fin)).Formula = ('=IF(ISNUMBER($K{0}),$K{0},IF(ISNUMBER($G{0}),IF(N($L{0})=0,$G{0},ROUND($G{0}*(1-N($L{0})),2)),""))' -f $ini)
        $h.Range(("J{0}:J{1}" -f $ini, $fin)).Formula = ('=IF(I{0}="","",IF(TipoCambioVenta="","Actualizar TC",ROUND(I{0}*TipoCambioVenta,2)))' -f $ini)
        $h.Range(("L{0}:L{1}" -f $ini, $fin)).Formula = ('=IFERROR(INDEX(TablaDescuentos[Valor],MATCH(TRIM($F{0})&"|"&TRIM($B{0})&"|"&TRIM($D{0}),TablaDescuentos[Clave],0)),IFERROR(INDEX(TablaDescuentos[Valor],MATCH(TRIM($F{0})&"|"&TRIM($B{0})&"|",TablaDescuentos[Clave],0)),IFERROR(INDEX(TablaDescuentos[Valor],MATCH(TRIM($F{0})&"||",TablaDescuentos[Clave],0)),IF(COUNTIFS(TablaDescuentos[Proveedor],TRIM($F{0}),TablaDescuentos[Estado],"PENDIENTE")>0,"PENDIENTE",""))))' -f $ini)
        $h.Range(("A{0}:A{1}" -f $ini, $fin)).EntireRow.RowHeight = $h.Rows.Item($ult).RowHeight
        $h.Range(("A{0}:AB{1}" -f $ini, $fin)).WrapText = $false
        $valFin = $null; try { $valFin = $h.Range(("E{0}" -f $fin)).Validation.Formula1 } catch { }
        if ($valFin -ne $valE2) {
            [void]$h.Range("D2:E2").Copy()
            [void]$h.Range(("D{0}:E{1}" -f $ini, $fin)).PasteSpecial(6)
            SinCopiar $excel
            Write-Output "validacion de Categoria/Subcategoria copiada a las filas nuevas"
        }
        Write-Output ("filas nuevas: {0} (filas {1} a {2})" -f $n, $ini, $fin)
    }

    # --- 4. verificacion ---
    $excel.Calculation = -4105
    $excel.CalculateFull()
    $mal = @()
    $esperadas = $n0 - $quitadas.Count + $n
    if ($lo.ListRows.Count -ne $esperadas) { $mal += ("filas: {0}, esperaba {1}" -f $lo.ListRows.Count, $esperadas) }
    $err = 0; try { $x = $h.UsedRange.SpecialCells(-4123, 16); if ($x -ne $null) { $err = $x.Count } } catch { }
    if ($err -gt 0) { $mal += ("{0} celdas con error" -f $err) }
    $dC = $lo.ListColumns.Item(3).DataBodyRange.Value2; $dF = $lo.ListColumns.Item(6).DataBodyRange.Value2
    $dG = $lo.ListColumns.Item(7).DataBodyRange.Value2; $dI = $lo.ListColumns.Item(9).DataBodyRange.Value2
    $dK = $lo.ListColumns.Item(11).DataBodyRange.Value2; $dL = $lo.ListColumns.Item(12).DataBodyRange.Value2
    # las filas conservan el orden: se recorren las viejas saltando las quitadas
    $j = 0; $otras = 0; $corridas = 0; $malPrecio = 0
    for ($i = 1; $i -le $n0; $i++) {
        if ($quitadas.ContainsKey($i + 1)) { continue }
        $j++
        if ((Clave $aC[$i, 1]) -ne (Clave $dC[$j, 1]) -or (Txt $aF[$i, 1]) -ne (Txt $dF[$j, 1])) { $corridas++; continue }
        if ($actualizadas.ContainsKey($i + 1)) {
            $esp = $actualizadas[$i + 1].cambios.G
            if ($esp -ne $null -and -not (Igual $dG[$j, 1] ([double]$esp))) { $malPrecio++ }
            continue
        }
        if (-not (Igual $aG[$i, 1] $dG[$j, 1]) -or -not (Igual $aK[$i, 1] $dK[$j, 1]) -or -not (Igual $aI[$i, 1] $dI[$j, 1])) { $otras++ }
    }
    if ($corridas -gt 0) { $mal += ("{0} filas quedaron con otro codigo o proveedor" -f $corridas) }
    if ($otras -gt 0) { $mal += ("{0} filas fuera de la carga cambiaron de precio" -f $otras) }
    if ($malPrecio -gt 0) { $mal += ("{0} filas no quedaron con el precio nuevo" -f $malPrecio) }
    # precio de compra de todo el proveedor (incluye las nuevas)
    $malCompra = 0; $del = 0
    for ($i = 1; $i -le $lo.ListRows.Count; $i++) {
        if ((Txt $dF[$i, 1]) -ne $D.proveedor) { continue }
        $del++
        if ($dK[$i, 1] -is [double]) { continue }
        $g = $dG[$i, 1]; $l = $dL[$i, 1]; $c = $dI[$i, 1]
        if ($g -isnot [double] -or $c -isnot [double] -or $l -isnot [double]) { $malCompra++; continue }
        if ([math]::Abs($c - [math]::Round($g * (1 - $l), 2, [MidpointRounding]::AwayFromZero)) -gt 0.011) { $malCompra++ }
    }
    if ($malCompra -gt 0) { $mal += ("{0} filas del proveedor sin precio de compra correcto" -f $malCompra) }
    if ($n -gt 0) {
        foreach ($r in @($ini, [int](($ini + $fin) / 2), $fin)) {
            if ([string]$h.Cells.Item($r, 9).Formula -notlike ('=IF(ISNUMBER($K{0}),$K{0},*' -f $r)) { $mal += ("formula de compra mal en la fila {0}" -f $r) }
            if ([string]$h.Cells.Item($r, 12).Formula -notlike ('*TRIM($F{0})*' -f $r)) { $mal += ("formula de descuento mal en la fila {0}" -f $r) }
        }
        try { $vf = $h.Range(("E{0}" -f $fin)).Validation.Formula1 } catch { $vf = "" }
        if ($vf -ne $valE2) { $mal += "las filas nuevas no tienen la validacion de Subcategoria" }
    }
    if ($h.Range("D2").Validation.Formula1 -ne $valD2 -or $h.Range("E2").Validation.Formula1 -ne $valE2) { $mal += "cambio la validacion de D2/E2" }
    foreach ($nm in @("TipoCambioVenta", "TipoCambioCompra")) { try { [void]$wb.Names.Item($nm).RefersTo } catch { $mal += ("falta el nombre {0}" -f $nm) } }
    Write-Output ("verificacion: filas {0} (del proveedor {1}); errores {2}; fuera de la carga con otro precio {3}; precio nuevo mal {4}; compra mal {5}; corridas {6}" -f $lo.ListRows.Count, $del, $err, $otras, $malPrecio, $malCompra, $corridas)
    if ($mal.Count -gt 0) { foreach ($x in $mal) { Write-Output ("  MAL: " + $x) }; throw "quedo algo mal, NO se guarda" }
    if ($Guardar) { $wb.Save(); Write-Output "GUARDADO" } else { Write-Output "prueba: no se guarda" }
    $wb.Close($false)
}
finally {
    $excel.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($excel) | Out-Null
    [GC]::Collect(); [GC]::WaitForPendingFinalizers()
}
if (-not $Guardar) {
    if ((Get-Item -LiteralPath $Ruta).LastWriteTimeUtc -ne $mtime0) { Write-Output "AVISO: la prueba cambio la fecha del archivo" } else { Write-Output "la prueba no toco el archivo" }
}
if ($Guardar -and $enOneDrive) {
    & (Join-Path $PSScriptRoot "..\..\armar-cotizacion\scripts\verificar_onedrive.ps1") $Ruta
    exit $LASTEXITCODE
}
