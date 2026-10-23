# Cambia el descuento de un proveedor (y marca) en la pestana "Descuentos por
# proveedor" del catalogo, en todas sus filas (todas las categorias). Excel por
# COM. Sin -Guardar es una prueba.
#
#   powershell -File cambiar_descuento.ps1 -Ruta "<catalogo.xlsx>" -Datos "<descuento.json>" [-Guardar]
#
# descuento.json (UTF-8):
#   {"proveedor": "Hanwha Vision America", "marca": "Hanwha", "descuento": 0.5,
#    "estado": "CONFIRMADO POR PREVENTA", "de_donde_sale": "...", "fecha": "2026-10-21"}
#
# Verifica antes de guardar: que solo cambie el precio de compra de las filas
# de ese proveedor y marca sin precio dealer, que cada una quede en
# lista x (1 - descuento), y que ninguna otra fila del catalogo se mueva.
param(
    [Parameter(Mandatory = $true)][string]$Ruta,
    [Parameter(Mandatory = $true)][string]$Datos,
    [switch]$Guardar
)
$ErrorActionPreference = "Stop"
function Poner($celda, $valor) { [void][System.__ComObject].InvokeMember("Value2", [System.Reflection.BindingFlags]::SetProperty, $null, $celda, @(, $valor)) }
function Txt($v) { if ($v -eq $null) { return "" } return ([string]$v).Trim() }
function Estado($ruta) { $sh = New-Object -ComObject Shell.Application; return $sh.Namespace((Split-Path -Parent $ruta)).ParseName((Split-Path -Leaf $ruta)).ExtendedProperty("System.StorageProviderState") }
function Col($lo, $patron) { foreach ($c in $lo.ListColumns) { if ($c.Name -like $patron) { return $c.Index } }; throw "no encuentro la columna '$patron'" }

$D = Get-Content -LiteralPath $Datos -Raw -Encoding UTF8 | ConvertFrom-Json
if ($Ruta -like "*OneDrive*") {
    if (-not (Get-Process OneDrive -ErrorAction SilentlyContinue)) { throw "OneDrive no esta corriendo: no escribo" }
    if ((Estado $Ruta) -ne 2) { throw "el catalogo no esta sincronizado: no escribo" }
}
$bak = Join-Path $env:TEMP ("catalogo_antes_descuento_{0}.xlsx" -f (Get-Date -Format "yyyyMMdd_HHmmss")); Copy-Item -LiteralPath $Ruta $bak; Write-Output "respaldo: $bak"
$mt0 = (Get-Item -LiteralPath $Ruta).LastWriteTimeUtc
$x = New-Object -ComObject Excel.Application; $x.Visible = $false; $x.DisplayAlerts = $false
try {
    $wb = $x.Workbooks.Open($Ruta)
    if ($wb.ReadOnly) { throw "el catalogo esta abierto por alguien: no sigo" }
    try { if ($wb.AutoSaveOn) { [void][System.__ComObject].InvokeMember("AutoSaveOn", [System.Reflection.BindingFlags]::SetProperty, $null, $wb, @($false)) } } catch { }
    $cat = $wb.Worksheets.Item("Catalogo").ListObjects.Item("TablaCatalogo")
    $lo = $wb.Worksheets.Item("Descuentos por proveedor").ListObjects.Item("TablaDescuentos")
    $cP = Col $lo "Proveedor"; $cM = Col $lo "Marca"; $cC = Col $lo "Categor*"; $cD = Col $lo "Descuento"; $cE = Col $lo "Estado"; $cF = Col $lo "De d*nde sale"; $cFe = Col $lo "Fecha"
    $antesI = $cat.ListColumns.Item(9).DataBodyRange.Value2
    $G = $cat.ListColumns.Item(7).DataBodyRange.Value2; $K = $cat.ListColumns.Item(11).DataBodyRange.Value2
    $F = $cat.ListColumns.Item(6).DataBodyRange.Value2; $B = $cat.ListColumns.Item(2).DataBodyRange.Value2
    $n = $cat.ListRows.Count
    $tocadas = 0
    foreach ($lr in $lo.ListRows) {
        $r = $lr.Range
        if ((Txt $r.Cells.Item(1, $cP).Value2) -ne $D.proveedor -or (Txt $r.Cells.Item(1, $cM).Value2) -ne $D.marca) { continue }
        Write-Output ("antes: {0} | {1} | {2} -> descuento {3}, estado {4}" -f $D.proveedor, $D.marca, (Txt $r.Cells.Item(1, $cC).Value2), $r.Cells.Item(1, $cD).Value2, (Txt $r.Cells.Item(1, $cE).Value2))
        Poner ($r.Cells.Item(1, $cD)) ([double]$D.descuento)
        Poner ($r.Cells.Item(1, $cE)) ([string]$D.estado)
        Poner ($r.Cells.Item(1, $cF)) ([string]$D.de_donde_sale)
        Poner ($r.Cells.Item(1, $cFe)) ([double]((Get-Date $D.fecha) - (Get-Date "1899-12-30")).Days)
        $tocadas++
    }
    if ($tocadas -eq 0) { throw "no hay filas de '$($D.proveedor) | $($D.marca)' en Descuentos por proveedor" }
    $x.CalculateFull()
    $despuesI = $cat.ListColumns.Item(9).DataBodyRange.Value2
    $mal = @(); $propias = 0; $otras = 0; $malCalc = 0
    for ($i = 1; $i -le $n; $i++) {
        $esPropia = ((Txt $F[$i, 1]) -eq $D.proveedor) -and ((Txt $B[$i, 1]) -eq $D.marca) -and -not ($K[$i, 1] -is [double])
        if ("$($antesI[$i,1])" -ne "$($despuesI[$i,1])") { if ($esPropia) { $propias++ } else { $otras++ } }
        $lista = $G[$i, 1]; $compra = $despuesI[$i, 1]   # fuera de la llamada: ahi la coma separa argumentos
        if ($esPropia -and $lista -is [double]) {
            $esp = [math]::Round($lista * (1 - [double]$D.descuento), 2)
            if (-not ($compra -is [double]) -or [math]::Abs($compra - $esp) -gt 0.011) { $malCalc++ }
        }
    }
    if ($otras -gt 0) { $mal += "$otras filas de otros proveedores cambiaron de precio de compra" }
    if ($malCalc -gt 0) { $mal += "$malCalc filas no quedaron en lista x (1 - descuento)" }
    $err = 0; try { $e = $wb.Worksheets.Item("Catalogo").UsedRange.SpecialCells(-4123, 16); $err = $e.Count } catch { }
    if ($err -gt 0) { $mal += "$err celdas con error" }
    Write-Output ("filas de descuento tocadas: {0}; productos cuyo precio de compra cambio: {1}; de otros proveedores: {2}; mal calculados: {3}; errores: {4}" -f $tocadas, $propias, $otras, $malCalc, $err)
    if ($mal.Count) { foreach ($m in $mal) { Write-Output "  MAL: $m" }; throw "no se guarda" }
    if ($Guardar) { $wb.Save(); Write-Output "GUARDADO" } else { Write-Output "prueba: no se guarda" }
    $wb.Close($false)
}
finally { $x.Quit(); [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($x); [GC]::Collect() }
if (-not $Guardar) { if ((Get-Item -LiteralPath $Ruta).LastWriteTimeUtc -eq $mt0) { Write-Output "la prueba no toco el archivo" } else { Write-Output "AVISO: cambio la fecha del archivo" } }
if ($Guardar -and $Ruta -like "*OneDrive*") { for ($i = 0; $i -lt 24; $i++) { Start-Sleep 5; $st = Estado $Ruta; if ($st -eq 2) { break } }; Write-Output "OneDrive: estado $st" }
