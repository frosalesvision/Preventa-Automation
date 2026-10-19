# Carga al catalogo lo que dejo preparar_portales.py (portales de proveedor con
# la sesion de GV). Escribe por Excel (COM), nunca con openpyxl (borra los
# desplegables). Sin -Guardar es una prueba: escribe, verifica y cierra sin guardar.
#
#   powershell -File cargar_portales.ps1 -Ruta "<catalogo.xlsx>" -Datos "<carga.json>" [-Guardar]
#
# Hace:
#   1. Actualiza las filas existentes del mismo proveedor y codigo: precio de
#      lista (G), dealer (K), fecha (R), archivo de origen (Y), pestana (Z) y
#      tipo de precio (AB). Solo si la fila tiene todavia lo que tenia cuando
#      se preparo la carga; si cambio, no la toca.
#   2. Agrega las filas nuevas al final de TablaCatalogo, en lotes, con sus
#      formulas (H, I, J, L) y la validacion de Categoria / Subcategoria.
#   3. Verifica antes de guardar: cantidad de filas, celdas con error, que
#      ninguna fila vieja (salvo las actualizadas) cambio de precio, que todas
#      las nuevas tengan precio de compra, codigos, formulas y validaciones.
# Reglas de seguridad (actualizar-catalogo, "Formato"): respaldo siempre,
# Autoguardado apagado, OneDrive corriendo y el archivo sincronizado antes de
# escribir, y despues de guardar esperar a que lo suba. Nunca reiniciar OneDrive.
param(
    [Parameter(Mandatory = $true)][string]$Ruta,
    [Parameter(Mandatory = $true)][string]$Datos,
    [switch]$Guardar,
    [int]$Lote = 800
)
$ErrorActionPreference = "Stop"
$EN_US = [System.Globalization.CultureInfo]::GetCultureInfo("en-US")
function Poner($celda, $valor) { [void][System.__ComObject].InvokeMember("Value2", [System.Reflection.BindingFlags]::SetProperty, $null, $celda, @(, $valor)) }
function PonerBloque($rango, $arr) { [void][System.__ComObject].InvokeMember("Value2", [System.Reflection.BindingFlags]::SetProperty, $null, $rango, @(, $arr)) }
function PonerFormato($rango, $formato) { [void][System.__ComObject].InvokeMember("NumberFormat", [System.Reflection.BindingFlags]::SetProperty, $null, $rango, @($formato), $EN_US) }
function SinCopiar($app) { [void][System.__ComObject].InvokeMember("CutCopyMode", [System.Reflection.BindingFlags]::SetProperty, $null, $app, @($false)) }
function Txt($v) { if ($v -eq $null) { return "" } return ([string]$v).Trim() }
function Clave($s) { return ([string]$s).ToUpper() -replace "[^A-Z0-9]", "" }
function Vacio($v) { if ($v -eq $null) { return $null }; $t = [string]$v; if ($t.Trim() -eq "") { return $null }; return $t }
function Num($v) { if ($v -eq $null) { return $null }; return [double]$v }
function Igual($a, $b) {
    if (($a -eq $null -or "$a" -eq "") -and ($b -eq $null -or "$b" -eq "")) { return $true }
    if ($a -eq $null -or $b -eq $null) { return $false }
    $x = 0.0; $y = 0.0
    if ([double]::TryParse("$a", [ref]$x) -and [double]::TryParse("$b", [ref]$y)) { return [math]::Abs($x - $y) -lt 0.005 }
    return (Txt $a) -eq (Txt $b)
}
function EstadoNube($ruta) {
    $sh = New-Object -ComObject Shell.Application
    $it = $sh.Namespace((Split-Path -Parent $ruta)).ParseName((Split-Path -Leaf $ruta))
    return $it.ExtendedProperty("System.StorageProviderState")
}

$enOneDrive = $Ruta -like "*OneDrive*"
if ($enOneDrive) {
    if (-not (Get-Process OneDrive -ErrorAction SilentlyContinue)) { throw "OneDrive no esta corriendo: no escribo" }
    $st = EstadoNube $Ruta
    if ($st -ne 2) { throw ("el catalogo no esta sincronizado (estado {0}): no escribo" -f $st) }
    Write-Output "OneDrive corriendo y catalogo sincronizado"
}
$D = Get-Content -LiteralPath $Datos -Raw -Encoding UTF8 | ConvertFrom-Json
$bak = Join-Path $env:TEMP ("catalogo_antes_portales_{0}.xlsx" -f (Get-Date -Format "yyyyMMdd_HHmmss"))
Copy-Item -LiteralPath $Ruta $bak
Write-Output ("respaldo: {0}" -f $bak)
$mtime0 = (Get-Item -LiteralPath $Ruta).LastWriteTimeUtc

$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false; $excel.DisplayAlerts = $false; $excel.ScreenUpdating = $false
try {
    $wb = $excel.Workbooks.Open($Ruta)
    $auto = $null; try { $auto = $wb.AutoSaveOn } catch { }
    if ($auto -eq $true) {
        [void][System.__ComObject].InvokeMember("AutoSaveOn", [System.Reflection.BindingFlags]::SetProperty, $null, $wb, @($false))
        if ($wb.AutoSaveOn -ne $false) { throw "no pude apagar el Autoguardado: no sigo" }
        Write-Output "Autoguardado apagado para esta corrida"
    }
    $excel.Calculation = -4135   # manual mientras escribe; al final se recalcula todo
    $h = $wb.Worksheets.Item("Catalogo")
    $lo = $h.ListObjects.Item("TablaCatalogo")
    $n0 = $lo.ListRows.Count; $ult0 = $n0 + 1
    $encab = @(); foreach ($c in $lo.ListColumns) { $encab += $c.Name }
    if ($encab.Count -ne 28 -or $encab[2] -ne "Modelo / SKU" -or $encab[5] -ne "Proveedor" -or $encab[10] -notlike "Precio dealer*" -or $encab[27] -ne "Tipo de precio cargado") { throw ("el catalogo cambio de forma: {0}" -f ($encab -join " | ")) }
    $valD2 = $h.Range("D2").Validation.Formula1; $valE2 = $h.Range("E2").Validation.Formula1
    $valAB = $null; try { $valAB = $h.Range("AB2").Validation.Formula1 } catch { }
    if ($valAB) { Write-Output ("AVISO: la columna AB tiene validacion: {0}" -f $valAB) }
    $antesG = $lo.ListColumns.Item(7).DataBodyRange.Value2
    $antesI = $lo.ListColumns.Item(9).DataBodyRange.Value2
    $antesK = $lo.ListColumns.Item(11).DataBodyRange.Value2
    Write-Output ("catalogo antes: {0} filas" -f $n0)

    # --- 1. actualizaciones ---
    $actualizadas = @{}; $okA = 0; $noA = 0
    foreach ($a in $D.actualizar) {
        $r = [int]$a.fila
        $mismo = ((Clave $h.Cells.Item($r, 3).Value2) -eq (Clave $a.sku)) -and ((Txt $h.Cells.Item($r, 6).Value2) -eq (Txt $a.proveedor_actual))
        $rv = $h.Cells.Item($r, 18).Value2; $rTxt = $(if ($rv -is [double]) { [DateTime]::FromOADate($rv).ToString("yyyy-MM-dd") } else { Txt $rv })
        $igual = $mismo -and (Igual $h.Cells.Item($r, 7).Value2 $a.antes.G) -and (Igual $h.Cells.Item($r, 11).Value2 $a.antes.K) -and ($rTxt -eq (Txt $a.antes.R)) -and ((Txt $h.Cells.Item($r, 28).Value2) -eq (Txt $a.antes.AB))
        if (-not $igual) { $noA++; Write-Output ("AVISO fila {0} ({1}): cambio desde que se preparo la carga, no se toca" -f $r, $a.sku); continue }
        Poner ($h.Cells.Item($r, 7)) (Num $a.G)
        Poner ($h.Cells.Item($r, 11)) (Num $a.K)
        Poner ($h.Cells.Item($r, 18)) ([double]$a.R)
        Poner ($h.Cells.Item($r, 25)) ([string]$a.Y)
        Poner ($h.Cells.Item($r, 26)) $null
        Poner ($h.Cells.Item($r, 28)) ([string]$a.AB)
        $actualizadas[$r] = $true; $okA++
    }
    Write-Output ("actualizadas: {0}; no tocadas porque cambiaron: {1}" -f $okA, $noA)

    # --- 2. filas nuevas ---
    $n = $D.filas.Count; $ini = $ult0 + 1; $fin = $ult0 + $n
    if ($n -gt 0) {
        if ($excel.WorksheetFunction.CountA($h.Range(("A{0}:AB{1}" -f $ini, $fin))) -ne 0) { throw "hay datos debajo de la tabla: no se agrega nada" }
        $lo.Resize($h.Range(("A1:AB{0}" -f $fin)))
        [void]$h.Range(("A{0}:AB{0}" -f $ult0)).Copy()
        [void]$h.Range(("A{0}:AB{1}" -f $ini, $fin)).PasteSpecial(-4122)
        SinCopiar $excel
        PonerFormato ($h.Range(("C{0}:C{1}" -f $ini, $fin))) "@"
        for ($desde = 0; $desde -lt $n; $desde += $Lote) {
            $cant = [math]::Min($Lote, $n - $desde); $a0 = $ini + $desde; $a1f = $a0 + $cant - 1
            $b1 = $h.Range(("A{0}:G{1}" -f $a0, $a1f)); $v1 = $b1.Value2
            $b2 = $h.Range(("K{0}:K{1}" -f $a0, $a1f)); $v2 = $b2.Value2
            $b3 = $h.Range(("M{0}:AB{1}" -f $a0, $a1f)); $v3 = $b3.Value2
            for ($i = 0; $i -lt $cant; $i++) {
                $f = $D.filas[$desde + $i]; $k = $i + 1
                $v1[$k, 1] = Vacio $f.c1; $v1[$k, 2] = Vacio $f.c2; $v1[$k, 3] = Vacio $f.c3
                $v1[$k, 4] = Vacio $f.c4; $v1[$k, 5] = Vacio $f.c5; $v1[$k, 6] = Vacio $f.c6
                $v1[$k, 7] = Num $f.c7
                $v2[$k, 1] = Num $f.c11
                $v3[$k, 1] = Vacio $f.c13          # M  unidad
                $v3[$k, 4] = Vacio $f.c16          # P  descripcion
                $v3[$k, 6] = [double]$f.c18        # R  fecha del precio
                $v3[$k, 13] = Vacio $f.c25         # Y  archivo de origen
                $v3[$k, 14] = $null                # Z  pestana
                $v3[$k, 15] = Vacio $f.c27         # AA categoria original
                $v3[$k, 16] = Vacio $f.c28         # AB tipo de precio
            }
            PonerBloque $b1 $v1; PonerBloque $b2 $v2; PonerBloque $b3 $v3
            Write-Output ("  lote: filas {0} a {1}" -f $a0, $a1f)
        }
        $h.Range(("H{0}:H{1}" -f $ini, $fin)).Formula = ('=IF(G{0}="","",IF(TipoCambioVenta="","Actualizar TC",ROUND(G{0}*TipoCambioVenta,2)))' -f $ini)
        $h.Range(("I{0}:I{1}" -f $ini, $fin)).Formula = ('=IF(ISNUMBER($K{0}),$K{0},IF(ISNUMBER($G{0}),IF(N($L{0})=0,$G{0},ROUND($G{0}*(1-N($L{0})),2)),""))' -f $ini)
        $h.Range(("J{0}:J{1}" -f $ini, $fin)).Formula = ('=IF(I{0}="","",IF(TipoCambioVenta="","Actualizar TC",ROUND(I{0}*TipoCambioVenta,2)))' -f $ini)
        $h.Range(("L{0}:L{1}" -f $ini, $fin)).Formula = ('=IFERROR(INDEX(TablaDescuentos[Valor],MATCH(TRIM($F{0})&"|"&TRIM($B{0})&"|"&TRIM($D{0}),TablaDescuentos[Clave],0)),IFERROR(INDEX(TablaDescuentos[Valor],MATCH(TRIM($F{0})&"|"&TRIM($B{0})&"|",TablaDescuentos[Clave],0)),IFERROR(INDEX(TablaDescuentos[Valor],MATCH(TRIM($F{0})&"||",TablaDescuentos[Clave],0)),IF(COUNTIFS(TablaDescuentos[Proveedor],TRIM($F{0}),TablaDescuentos[Estado],"PENDIENTE")>0,"PENDIENTE",""))))' -f $ini)
        $alto = $h.Rows.Item($ult0).RowHeight
        $h.Range(("A{0}:A{1}" -f $ini, $fin)).EntireRow.RowHeight = $alto
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

    # --- 3. verificacion ---
    $excel.Calculation = -4105
    $excel.CalculateFull()
    $mal = @()
    if ($lo.ListRows.Count -ne $n0 + $n) { $mal += ("filas: {0}, esperaba {1}" -f $lo.ListRows.Count, ($n0 + $n)) }
    $err = 0; try { $x = $h.UsedRange.SpecialCells(-4123, 16); if ($x -ne $null) { $err = $x.Count } } catch { }
    if ($err -gt 0) { $mal += ("{0} celdas con error" -f $err) }
    $dG = $lo.ListColumns.Item(7).DataBodyRange.Value2; $dI = $lo.ListColumns.Item(9).DataBodyRange.Value2; $dK = $lo.ListColumns.Item(11).DataBodyRange.Value2
    $cambio = 0
    for ($r = 1; $r -le $n0; $r++) {
        if ($actualizadas.ContainsKey($r + 1)) {
            if (-not (Igual $dI[$r, 1] $dK[$r, 1])) { $mal += ("fila actualizada {0}: el precio de compra no es el dealer" -f ($r + 1)) }
            continue
        }
        if ("$($antesG[$r, 1])" -ne "$($dG[$r, 1])" -or "$($antesK[$r, 1])" -ne "$($dK[$r, 1])" -or "$($antesI[$r, 1])" -ne "$($dI[$r, 1])") { $cambio++ }
    }
    if ($cambio -gt 0) { $mal += ("{0} filas viejas cambiaron de precio sin estar en la carga" -f $cambio) }
    $sinCompra = 0; $skuMal = 0
    if ($n -gt 0) {
        $sku = $h.Range(("C{0}:C{1}" -f $ini, $fin)).Value2
        for ($i = 1; $i -le $n; $i++) {
            $fi = $n0 + $i
            if ($dI[$fi, 1] -isnot [double]) { $sinCompra++ }
            if ((Txt $sku[$i, 1]) -ne (Txt $D.filas[$i - 1].c3)) { $skuMal++ }
        }
        foreach ($r in @($ini, [int](($ini + $fin) / 2), $fin)) {
            if ([string]$h.Cells.Item($r, 9).Formula -notlike ('=IF(ISNUMBER($K{0}),$K{0},*' -f $r)) { $mal += ("formula de compra mal en la fila {0}" -f $r) }
            if ([string]$h.Cells.Item($r, 12).Formula -notlike ('*TRIM($F{0})*' -f $r)) { $mal += ("formula de descuento mal en la fila {0}" -f $r) }
        }
        try { $vf = $h.Range(("E{0}" -f $fin)).Validation.Formula1 } catch { $vf = "" }
        if ($vf -ne $valE2) { $mal += "las filas nuevas no tienen la validacion de Subcategoria" }
    }
    if ($sinCompra -gt 0) { $mal += ("{0} filas nuevas sin precio de compra" -f $sinCompra) }
    if ($skuMal -gt 0) { $mal += ("{0} codigos no quedaron igual" -f $skuMal) }
    if ($h.Range("D2").Validation.Formula1 -ne $valD2 -or $h.Range("E2").Validation.Formula1 -ne $valE2) { $mal += "cambio la validacion de D2/E2" }
    foreach ($nm in @("TipoCambioVenta", "TipoCambioCompra")) { try { [void]$wb.Names.Item($nm).RefersTo } catch { $mal += ("falta el nombre {0}" -f $nm) } }
    Write-Output ("verificacion: filas {0}; errores {1}; filas viejas con otro precio {2}; nuevas sin compra {3}; codigos distintos {4}" -f $lo.ListRows.Count, $err, $cambio, $sinCompra, $skuMal)
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
    for ($s = 0; $s -lt 24; $s++) { Start-Sleep -Seconds 5; $st = EstadoNube $Ruta; if ($st -eq 2) { break } }
    Write-Output ("OneDrive: estado {0} ({1})" -f $st, $(if ($st -eq 2) { "subido" } else { "todavia subiendo: abrir y cerrar el catalogo en Excel, nunca reiniciar OneDrive" }))
}
