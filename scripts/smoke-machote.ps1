# Smoke test del machote de matriz y oferta.
#
# Copia el machote a una carpeta temporal y verifica dos escenarios:
#   - EN BLANCO (P-06a): recien copiado, sin escribir nada.
#   - CON DATOS (P-01 a P-08): las entradas de docs/pruebas-validacion.md.
# Los dos importan: hubo divisiones entre cero que solo se ven en blanco.
#
# Correr despues de CUALQUIER cambio estructural en el machote.
# No modifica el machote: trabaja siempre sobre una copia.
#
# Uso:  powershell -File scripts/smoke-machote.ps1

$ErrorActionPreference = "Stop"

$src = Join-Path $PSScriptRoot "..\plugin-preventa\skills\armar-cotizacion\references\Machote Matriz y oferta.xlsx"
if (-not (Test-Path $src)) { throw "No se encontro el machote en: $src" }
$src = (Resolve-Path $src).Path
$test = Join-Path $env:TEMP "smoke_machote.xlsx"
Copy-Item $src $test -Force

# Estructura vigente (2026-09-21)
$FILA_EQ_FIN    = 55    # ultima fila de datos de Equipos
$FILA_EQ_TOT    = 57    # totales de Equipos
$FILA_COT_FIN   = 71    # ultima linea de COTIZACION
$FILA_COT_SUB   = 74    # SUBTOTAL
$FILA_COT_ESP   = 75    # IMPUESTO
$FILA_COT_TOTAL = 76    # TOTAL

$esperado = @{
    "P-01 Equipos!O6   Precio Venta unit"  = 184.853787878788
    "P-01 Equipos!P6   Precio Venta total" = 1848.53787878788
    "P-02 Equipos!K7   Costo Nac. unit"    = 103
    "P-02 Equipos!P7   Precio Venta total" = 1461.29476584022
    "P-03 MATERIALES!J7  Costo Nac. unit"  = 56.5
    "P-03 MATERIALES!O7  Venta total"      = 1662.71428571429
    "P-04 Equipos!P57  Total Venta"        = 3309.8326446281
    "P-04 COTIZACION!J76  TOTAL"           = 3740.11
    # El cuadro financia el precio UNITARIO (opcion A, 2026-09-21).
    "P-05 Financiamiento!C4   Total Venta" = 184.853787878788
    "P-05 Financiamiento!C12  Cuota"       = 4.77764275443391
    "P-05 Financiamiento!C18  Costo fin."  = 44.47306433404
    # La cotizacion financiada muestra cuota unitaria x cantidad.
    "P-08 Financiada!I22  Cuota unitaria"  = 4.77764275443391
    "P-08 Financiada!J22  Total mensual"   = 47.7764275443391
}

$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false
$fallas = 0

function Hoja($wb, $patron, $excluir) {
    foreach ($h in $wb.Worksheets) {
        if ($h.Name -like $patron) {
            if ($excluir -and $h.Name -like $excluir) { continue }
            return $h
        }
    }
    throw "No se encontro la hoja que coincide con '$patron'"
}

try {
    $wb  = $excel.Workbooks.Open($test)
    # Hojas por NOMBRE, no por indice: los indices se corren al agregar pestanas.
    $eq  = Hoja $wb "Equipos" $null
    $mat = Hoja $wb "MATERIALES" $null
    $cot = Hoja $wb "COTIZACI*" "*Financ*"
    $cfn = Hoja $wb "*Financ)*" $null
    $fin = Hoja $wb "Financiamiento" $null
    Write-Output ("hojas: {0} | {1} | {2} | {3} | {4}" -f $eq.Name, $mat.Name, $cot.Name, $cfn.Name, $fin.Name)

    # ---------- P-06a: el machote EN BLANCO no muestra ningun error ----------
    # Este barrido va ANTES de escribir nada. Es el caso que importa: asi lo
    # recibe el asesor al copiar el machote. Barrer solo despues de cargar
    # datos esconde las divisiones entre cero (paso de verdad: 6 celdas
    # #DIV/0! vivieron sin detectarse porque la prueba miraba tarde).
    Write-Output ""
    Write-Output "=== P-06a: errores con el machote EN BLANCO ==="
    $excel.CalculateFullRebuild()
    $errBlanco = 0
    foreach ($ws in $wb.Worksheets) {
        try {
            $rng = $ws.UsedRange.SpecialCells(-4123, 16)
            if ($null -ne $rng) {
                Write-Output ("  FALLA  {0}: {1} celdas -> {2}" -f $ws.Name, $rng.Count, $rng.Address($false, $false))
                $errBlanco += $rng.Count
            }
        } catch { }
    }
    if ($errBlanco -eq 0) { Write-Output "  OK    cero celdas en error en blanco" } else { $fallas++ }

    # P-01 linea importada, con ID de financiamiento 1
    $eq.Range("B6").Value2 = "EQUIPO-TEST-IMPORTADO"
    $eq.Range("C6").Value2 = "si"
    $eq.Range("D6").Value2 = 10
    $eq.Range("E6").Value2 = 100
    $eq.Range("Q6").Value2 = 1

    # P-02 misma linea, nacional
    $eq.Range("B7").Value2 = "EQUIPO-TEST-NACIONAL"
    $eq.Range("C7").Value2 = "no"
    $eq.Range("D7").Value2 = 10
    $eq.Range("E7").Value2 = 100

    # P-03 material nacional (fila 7: la 6 tiene el seguro como literal)
    $mat.Range("A7").Value2 = "MATERIAL-TEST"
    $mat.Range("B7").Value2 = "no"
    $mat.Range("C7").Value2 = 20
    $mat.Range("D7").Value2 = 50

    $excel.CalculateFullRebuild()

    $obtenido = @{
        "P-01 Equipos!O6   Precio Venta unit"  = $eq.Range("O6").Value2
        "P-01 Equipos!P6   Precio Venta total" = $eq.Range("P6").Value2
        "P-02 Equipos!K7   Costo Nac. unit"    = $eq.Range("K7").Value2
        "P-02 Equipos!P7   Precio Venta total" = $eq.Range("P7").Value2
        "P-03 MATERIALES!J7  Costo Nac. unit"  = $mat.Range("J7").Value2
        "P-03 MATERIALES!O7  Venta total"      = $mat.Range("O7").Value2
        "P-04 Equipos!P57  Total Venta"        = $eq.Range("P$FILA_EQ_TOT").Value2
        "P-04 COTIZACION!J76  TOTAL"           = $cot.Range("J$FILA_COT_TOTAL").Value2
        "P-05 Financiamiento!C4   Total Venta" = $fin.Range("C4").Value2
        "P-05 Financiamiento!C12  Cuota"       = $fin.Range("C12").Value2
        "P-05 Financiamiento!C18  Costo fin."  = $fin.Range("C18").Value2
        "P-08 Financiada!I22  Cuota unitaria"  = $cfn.Range("I22").Value2
        "P-08 Financiada!J22  Total mensual"   = $cfn.Range("J22").Value2
    }

    Write-Output ""
    Write-Output "=== Pruebas numericas (P-01 a P-05, P-08) ==="
    foreach ($k in ($esperado.Keys | Sort-Object)) {
        $e = [double]$esperado[$k]
        $o = [double]$obtenido[$k]
        $ok = [Math]::Abs($e - $o) -lt 0.000001
        if (-not $ok) { $fallas++ }
        Write-Output ("  {0}  {1,-40} esperado={2}  obtenido={3}" -f $(if ($ok) { "OK  " } else { "FALLA" }), $k, $e, $o)
    }

    # ---------- P-07: capacidad de 50 lineas ----------
    Write-Output ""
    Write-Output "=== P-07: capacidad de 50 lineas ==="
    for ($i = 8; $i -le $FILA_EQ_FIN; $i++) {
        $eq.Range("B$i").Value2 = ("LINEA-{0}" -f ($i - 5))
        $eq.Range("C$i").Value2 = "no"
        $eq.Range("D$i").Value2 = 1
        $eq.Range("E$i").Value2 = 100
    }
    $eq.Range("Q$FILA_EQ_FIN").Value2 = 50     # la linea 50 tambien se financia
    $excel.CalculateFullRebuild()

    $unitNac   = $eq.Range("O7").Value2
    $esperaTot = $eq.Range("P6").Value2 + $eq.Range("P7").Value2 + (48 * $unitNac)
    $totalReal = $eq.Range("P$FILA_EQ_TOT").Value2
    $okTot = [Math]::Abs($esperaTot - $totalReal) -lt 0.000001
    if (-not $okTot) { $fallas++ }
    Write-Output ("  {0}  Equipos suma las 50 lineas      esperado={1}  obtenido={2}" -f $(if ($okTot) { "OK  " } else { "FALLA" }), $esperaTot, $totalReal)

    $okUlt = ($cot.Range("B$FILA_COT_FIN").Value2 -eq 1)
    if (-not $okUlt) { $fallas++ }
    Write-Output ("  {0}  COTIZACION llega a la linea 50" -f $(if ($okUlt) { "OK  " } else { "FALLA" }))

    $sub = $cot.Range("J$FILA_COT_SUB").Value2
    $okSub = [Math]::Abs($sub - $totalReal) -lt 0.01
    if (-not $okSub) { $fallas++ }
    Write-Output ("  {0}  SUBTOTAL de COTIZACION cuadra   esperado={1}  obtenido={2}" -f $(if ($okSub) { "OK  " } else { "FALLA" }), $totalReal, $sub)

    # la cuota del cuadro 50 debe ser la del precio unitario de esa linea
    $caja50 = $fin.Range("C837").Value2
    $unit50 = $eq.Range("O$FILA_EQ_FIN").Value2
    $okFin = [Math]::Abs($caja50 - $unit50) -lt 0.000001
    if (-not $okFin) { $fallas++ }
    Write-Output ("  {0}  Cuadro 50 toma el unitario      esperado={1}  obtenido={2}" -f $(if ($okFin) { "OK  " } else { "FALLA" }), $unit50, $caja50)

    # y la cotizacion financiada debe mostrar esa cuota en su ultima linea
    $cuota50 = $cfn.Range("I$FILA_COT_FIN").Value2
    $okCfn = ($cuota50 -is [double]) -and ($cuota50 -gt 0)
    if (-not $okCfn) { $fallas++ }
    Write-Output ("  {0}  Financiada linea 50 con cuota   obtenido={1}" -f $(if ($okCfn) { "OK  " } else { "FALLA" }), $cuota50)

    # una linea SIN ID no debe mostrar cuota
    $vacia = $cfn.Range("I23").Value2
    $okVacia = ([string]$vacia -eq "")
    if (-not $okVacia) { $fallas++ }
    Write-Output ("  {0}  Linea sin financiamiento vacia  obtenido='{1}'" -f $(if ($okVacia) { "OK  " } else { "FALLA" }), $vacia)

    # ---------- P-09: el impuesto al cliente sale de la ficha ----------
    # Antes estaba escrito a mano como 0.13 en COTIZACION y en la financiada.
    # Un cliente exento pagaba 13% y Excel no mostraba ningun error: el modo
    # de falla es silencioso, por eso esta prueba existe.
    Write-Output ""
    Write-Output "=== P-09: impuesto al cliente desde 'Datos del proyecto' ==="
    $dp  = $wb.Worksheets.Item("Datos del proyecto")
    $sub = $cot.Range("J$FILA_COT_SUB").Value2
    $casos = @(
        @("ficha vacia -> 13%",        "",     "",     0.13),
        @("exento=si -> 0%",           "si",   "",     0.00),
        @("4% escrito como 0.04",      "no",   "0.04", 0.04),
        @("4% escrito como 4",         "no",   "4",    0.04),
        @("B16 no numerico -> 13%",    "no",   "x",    0.13),
        @("exento con espacios/mayus", " SI ", "",     0.00)
    )
    foreach ($c in $casos) {
        $dp.Range("B15").Formula = $c[1]
        $dp.Range("B16").Formula = $c[2]
        $excel.CalculateFullRebuild()
        $tasa = $cot.Range("J$FILA_COT_ESP").Value2 / $sub
        $ok = [Math]::Abs($tasa - [double]$c[3]) -lt 0.000001
        if (-not $ok) { $fallas++ }
        Write-Output ("  {0}  {1,-30} esperado={2:P2}  obtenido={3:P2}" -f $(if ($ok) { "OK  " } else { "FALLA" }), $c[0], [double]$c[3], $tasa)
    }
    # la financiada usa la misma tasa
    $dp.Range("B15").Formula = "si"
    $excel.CalculateFullRebuild()
    $okFin = ($cfn.Range("J$FILA_COT_ESP").Value2 -eq 0)
    if (-not $okFin) { $fallas++ }
    Write-Output ("  {0}  la cotizacion financiada respeta la exencion" -f $(if ($okFin) { "OK  " } else { "FALLA" }))
    # dejar la ficha como estaba: el barrido de errores viene despues
    $dp.Range("B15").Formula = ""
    $dp.Range("B16").Formula = ""
    $excel.CalculateFullRebuild()

    # ---------- P-06: errores de Excel ----------
    Write-Output ""
    Write-Output ("=== P-06b: errores de Excel CON DATOS, en las {0} pestanas ===" -f $wb.Worksheets.Count)
    $errores = 0
    foreach ($ws in $wb.Worksheets) {
        try {
            $rng = $ws.UsedRange.SpecialCells(-4123, 16)   # xlCellTypeFormulas, xlErrors
            if ($null -ne $rng) {
                Write-Output ("  FALLA  {0}: {1} celdas -> {2}" -f $ws.Name, $rng.Count, $rng.Address($false, $false))
                $errores += $rng.Count
            }
        } catch { }
    }
    if ($errores -eq 0) { Write-Output "  OK    cero celdas en error con datos" } else { $fallas++ }

    $wb.Close($false)

    Write-Output ""
    if ($fallas -eq 0) { Write-Output "RESULTADO: todas las pruebas pasan." }
    else { Write-Output ("RESULTADO: {0} verificacion(es) fallaron. Revisar arriba." -f $fallas) }
}
finally {
    $excel.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($excel) | Out-Null
    [GC]::Collect(); [GC]::WaitForPendingFinalizers()
}

exit $(if ($fallas -eq 0) { 0 } else { 1 })
