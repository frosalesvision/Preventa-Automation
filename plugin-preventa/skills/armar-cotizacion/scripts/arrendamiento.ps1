# Arrendamiento (R32), solo si el pedido lo pide: agrega a una matriz ya llenada los cuadros de costo financiero
# del TOTAL del proyecto a varios plazos, cada uno con su tabla de amortizacion. Lo usa preventa o gerencia para
# ver cuotas; no sale en el PDF.
#
#   powershell -NoProfile -ExecutionPolicy Bypass -File arrendamiento.ps1 -Ruta "<matriz>" [-Plazos 4,8,2] [-Interes 0.11] [-Monto subtotal|total] [-Inicio 2026-12-01]
#
# Por cada plazo crea "RESUMEN (n)" (Total venta, anticipos, total a financiar, plazo, cuota mensual y anual,
# total de cuotas, costo financiero) y "PTMO (n)", copia del PTMO del machote conectada a ese cuadro. n empieza en 2.
# El monto sale de la cotizacion: el SUBTOTAL (sin IVA, por defecto) o el TOTAL. El PTMO del machote (el del
# financiamiento por linea, R13) no se toca. Interes, prima, plazo y fecha se pueden cambiar despues en cada cuadro.
param(
    [Parameter(Mandatory = $true)][string]$Ruta,
    [string[]]$Plazos = @("4", "8", "2"),
    [double]$Interes = 0.11,
    [ValidateSet("subtotal", "total")][string]$Monto = "subtotal",
    [string]$Inicio
)
$ErrorActionPreference = "Stop"
# con -File, "4,8,2" llega como un solo texto: se separa aca
$anos = [int[]]@($Plazos | ForEach-Object { ([string]$_) -split '[,; ]+' } | Where-Object { $_ -ne "" })
if ($anos.Count -eq 0 -or @($anos | Where-Object { $_ -lt 1 }).Count -gt 0) { throw "plazos invalidos: $($Plazos -join ', ')" }
$M = [System.Reflection.Missing]::Value
function Poner($celda, $valor) { [void][System.__ComObject].InvokeMember("Value2", [System.Reflection.BindingFlags]::SetProperty, $null, $celda, @(, $valor)) }
if (-not $Inicio) { $hoy = Get-Date; $Inicio = (Get-Date -Year $hoy.Year -Month $hoy.Month -Day 1).AddMonths(1).ToString("yyyy-MM-dd") }
$fecha = [datetime]::ParseExact($Inicio, "yyyy-MM-dd", [System.Globalization.CultureInfo]::InvariantCulture)

$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false; $excel.DisplayAlerts = $false; $excel.AskToUpdateLinks = $false
try {
    $wb = $excel.Workbooks.Open($Ruta)
    if ($wb.ReadOnly) { throw "el archivo esta abierto por alguien (solo lectura): no sigo" }
    $auto = $null; try { $auto = $wb.AutoSaveOn } catch { }
    if ($auto -eq $true) { [void][System.__ComObject].InvokeMember("AutoSaveOn", [System.Reflection.BindingFlags]::SetProperty, $null, $wb, @($false)) }
    $hojas = @{}; foreach ($w in $wb.Worksheets) { $hojas[$w.Name] = $w }
    $cot = $null; foreach ($n in $hojas.Keys) { if ($n -like "COTIZACI*N ") { $cot = $hojas[$n] } }
    if ($cot -eq $null) { throw "no encontre la pestana COTIZACION" }
    if (-not $hojas.ContainsKey("PTMO")) { throw "no encontre la pestana PTMO del machote" }
    $ptmo = $hojas["PTMO"]
    foreach ($i in 0..($anos.Count - 1)) { foreach ($p in "RESUMEN", "PTMO") { if ($hojas.ContainsKey(("{0} ({1})" -f $p, ($i + 2)))) { throw ("ya existe {0} ({1}): esta matriz ya tiene arrendamiento" -f $p, ($i + 2)) } } }

    # monto: la fila SUBTOTAL o TOTAL de la cotizacion, buscada por su etiqueta en la columna I
    $buscar = $(if ($Monto -eq "total") { "TOTAL" } else { "SUBTOTAL" })
    $celdaMonto = $null
    for ($r = 20; $r -le 130 -and $celdaMonto -eq $null; $r++) { if (([string]$cot.Cells.Item($r, 9).Value2).Trim() -eq $buscar) { $celdaMonto = "J$r" } }
    if ($celdaMonto -eq $null) { throw "no encontre la fila $buscar en la cotizacion" }

    # cuantas cuotas aguanta la tabla del PTMO (una fila con formula por cuota, desde la 19)
    $max = 0; for ($r = 19; $r -le 600; $r++) { if ($ptmo.Cells.Item($r, 1).HasFormula) { $max++ } else { break } }
    foreach ($a in $anos) { if ($a * 12 -gt $max) { throw ("{0} anos son {1} cuotas y la tabla del PTMO llega a {2}: usar un plazo menor" -f $a, ($a * 12), $max) } }

    $etq = [ordered]@{ "B2" = "CUADRO COSTOS FINANCIEROS"; "B3" = "Total Venta Proyecto"; "D3" = ("Inter" + [char]0xE9 + "s Anual");
        "B4" = "Anticipos"; "D4" = "Porcentaje de Prima"; "B5" = "Otros ingresos"; "B7" = "Total a Financiar";
        "B8" = ("Plazo (A" + [char]0xF1 + "os)"); "B9" = "Plazo (Meses)"; "B10" = "Cuota mensual"; "D10" = "Cuota anual"; "B13" = "TIR";
        "B14" = "Total Cuotas c/financiamiento"; "B16" = "Costo financiero" }
    $nota = ("Monto: el {0} de la cotizaci" + [char]0xF3 + "n{1}. Inter" + [char]0xE9 + "s, prima y plazo se pueden cambiar ac" + [char]0xE1 + "; su PTMO se actualiza solo.") -f $buscar, $(if ($buscar -eq "SUBTOTAL") { " (sin IVA)" } else { " (con IVA)" })
    $fmt = $cot.Range("J22").NumberFormat
    $color = $cot.Range("C21").Interior.Color
    $n = 2
    foreach ($a in $anos) {
        $h = $wb.Worksheets.Add($M, $wb.Worksheets.Item($wb.Worksheets.Count))
        $h.Name = "RESUMEN ($n)"
        foreach ($k in $etq.Keys) { $h.Range($k).Value2 = $etq[$k] }
        $h.Range("C3").Formula = ("='{0}'!{1}" -f $cot.Name, $celdaMonto)
        Poner ($h.Range("E3")) ($Interes)
        $h.Range("C4").Formula = "=+C3*E4"; Poner ($h.Range("E4")) (0.0); Poner ($h.Range("C5")) (0.0)
        $h.Range("C7").Formula = "=+C3-C4-C5"
        Poner ($h.Range("C8")) ([double]$a)
        $h.Range("C9").Formula = "=+C8*12"
        $h.Range("C10").Formula = "=PMT(E3/12,C9,-C7)"; $h.Range("E10").Formula = "=+C10*12"
        $h.Range("C14").Formula = "=C10*C9"; $h.Range("C16").Formula = "=+C14-C7"
        $h.Range("B18").Value2 = $nota
        [void]$h.Range("B2:E2").Merge(); $h.Range("B2").HorizontalAlignment = -4108
        $h.Range("B2").Font.Bold = $true; $h.Range("B2:E2").Interior.Color = $color
        foreach ($k in "B7", "C7", "B10", "C10", "B16", "C16") { $h.Range($k).Font.Bold = $true }
        $h.Range("C3:C16").NumberFormat = $fmt; $h.Range("E10").NumberFormat = $fmt
        $h.Range("C8:C9").NumberFormat = "0"; $h.Range("E3:E4").NumberFormat = "0.00%"
        [void]$h.Range("B2:E16").BorderAround(1, 2)
        $h.Columns.Item(1).ColumnWidth = 3; $h.Columns.Item(2).ColumnWidth = 30; $h.Columns.Item(3).ColumnWidth = 16
        $h.Columns.Item(4).ColumnWidth = 20; $h.Columns.Item(5).ColumnWidth = 14
        $h.Range("B18").Font.Italic = $true

        $ptmo.Copy($M, $h)
        $p = $wb.Worksheets.Item($h.Index + 1)
        $p.Name = "PTMO ($n)"
        $p.Visible = -1
        $p.Range("D5").Formula = "='RESUMEN ($n)'!C7"
        $p.Range("D6").Formula = "='RESUMEN ($n)'!E3"
        $p.Range("D7").Formula = "='RESUMEN ($n)'!C8"
        Poner ($p.Range("D9")) ($fecha.ToOADate())
        $n++
    }
    $excel.CalculateFull()
    $n = 2
    foreach ($a in $anos) {
        $h = $wb.Worksheets.Item("RESUMEN ($n)"); $p = $wb.Worksheets.Item("PTMO ($n)")
        $saldo = $p.Cells.Item(18 + $a * 12, 9).Value2
        if (-not ($saldo -is [double]) -or [math]::Abs($saldo) -gt 0.01) { throw ("PTMO ($n) no termina en saldo cero: {0}" -f $saldo) }
        Write-Output ("RESUMEN ({0}): {1} anos al {2:P2}, monto {3}, cuota {4}, total {5}, costo financiero {6}; PTMO ({0}) cierra en cero" -f $n, $a, $Interes, $h.Range("C3").Text.Trim(), $h.Range("C10").Text.Trim(), $h.Range("C14").Text.Trim(), $h.Range("C16").Text.Trim())
        $n++
    }
    $errores = 0
    foreach ($w in $wb.Worksheets) { if ($w.Visible -ne -1) { continue }; try { $errores += $w.UsedRange.SpecialCells(-4123, 16).Count } catch { } }
    if ($errores -gt 0) { throw "quedaron $errores celdas con error: no guardo" }
    $cot.Activate(); [void]$cot.Range("A1").Select()
    $wb.Save()
    $wb.Close($false)
    Write-Output ("ARRENDAMIENTO: {0} plazos, monto del {1}, inicio {2}" -f $anos.Count, $buscar, $Inicio)
}
finally {
    $excel.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($excel) | Out-Null
}
