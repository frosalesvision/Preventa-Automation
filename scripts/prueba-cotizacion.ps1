# Prueba de punta a punta de UNA COTIZACION COMPLETA, contra el sandbox.
#
# El smoke test (smoke-machote.ps1) mira el machote aislado. Este mira el
# flujo entero como lo vive el asesor: crear la carpeta, copiar el machote,
# escribir el equipo, llenar la ficha y revisar que la cotizacion diga lo
# que tiene que decir.
#
# NUNCA toca la carpeta CLIENTES real ni los Excels de control: todo pasa
# en sandbox-pruebas/, y el monto que iria al control solo se imprime.
#
# Uso:  powershell -File scripts/prueba-cotizacion.ps1
#       powershell -File scripts/prueba-cotizacion.ps1 -Conservar
#         (deja la carpeta creada para poder abrirla; por defecto la borra)

param([switch]$Conservar)

$ErrorActionPreference = "Stop"

$raiz     = Split-Path $PSScriptRoot -Parent
$machote  = Join-Path $raiz "plugin-preventa\skills\armar-cotizacion\references\Machote Matriz y oferta.xlsx"
$sandbox  = Join-Path $raiz "sandbox-pruebas\CLIENTES"
$cliente  = Join-Path $sandbox "Sandbox-Fabian"
$anio     = 2026
$desc     = "prueba"

if (-not (Test-Path $machote)) { throw "No se encontro el machote en: $machote" }
if (-not (Test-Path $cliente)) { throw "No se encontro el cliente de prueba en: $cliente" }

$fallas = 0
function Chequear($ok, $texto, $detalle) {
    if (-not $ok) { $script:fallas++ }
    $marca = if ($ok) { "OK   " } else { "FALLA" }
    if ($detalle) { Write-Output ("  {0}  {1}  ->  {2}" -f $marca, $texto, $detalle) }
    else          { Write-Output ("  {0}  {1}" -f $marca, $texto) }
}

Write-Output "=========================================================="
Write-Output " PRUEBA DE COTIZACION COMPLETA (sandbox)"
Write-Output "=========================================================="

# ---------------------------------------------------------------
# 1. Numeracion: maximo del anio vs maximo global
# ---------------------------------------------------------------
Write-Output ""
Write-Output "--- 1. Numeracion de la cotizacion ---"
$previas = Get-ChildItem $cliente -Recurse -Directory | Where-Object { $_.Name -match '^Cotizaci' }
$nums = @()
foreach ($d in $previas) { if ($d.Name -match '#(\d+)-(\d{4})') { $nums += [PSCustomObject]@{ N = [int]$Matches[1]; A = [int]$Matches[2] } } }
$maxAnio = ($nums | Where-Object { $_.A -eq $anio } | Measure-Object N -Maximum).Maximum
$maxGlob = ($nums | Measure-Object N -Maximum).Maximum
if (-not $maxAnio) { $maxAnio = 0 }
if (-not $maxGlob) { $maxGlob = 0 }
$N = $maxAnio + 1
Chequear ($maxAnio -eq $maxGlob) "las dos convenciones coinciden, se propone #$N sin preguntar" "anio=$maxAnio global=$maxGlob"

# ---------------------------------------------------------------
# 2. Limite de ruta de Windows (H-4)
# ---------------------------------------------------------------
Write-Output ""
Write-Output "--- 2. Limite de ruta ---"
$carpeta = Join-Path $cliente ("Sandbox-Fabian -{0}\Cotizacion #{1}-{0} {2}" -f $anio, $N, $desc)
$destino = Join-Path $carpeta ("Matriz-Oferta\Matriz y oferta {0}.xlsx" -f $desc)
$largo = $destino.Length
Chequear ($largo -lt 259) "la ruta del machote cabe en Windows" "$largo de 259 caracteres"
# cuantos caracteres MAS aguantaria la descripcion (aparece dos veces)
$margen = [Math]::Floor((259 - $largo) / 2)
Write-Output ("         la descripcion podria crecer {0} caracteres mas" -f $margen)

# ---------------------------------------------------------------
# 3. Carpeta y copia del machote
# ---------------------------------------------------------------
Write-Output ""
Write-Output "--- 3. Carpeta y machote ---"
if (Test-Path $carpeta) { Remove-Item $carpeta -Recurse -Force }
$subs = @("Cotizaciones", "Fichas Tecnicas", "Implementacion\Actas de entrega",
          "Implementacion\Boletas de servicio", "Implementacion\Documentacion del proyecto",
          "Implementacion\Mantenimiento", "Matriz-Oferta", "Visita tecnica")
foreach ($s in $subs) { New-Item -ItemType Directory -Force -Path (Join-Path $carpeta $s) | Out-Null }
Copy-Item $machote $destino -Force
# Se verifica cada ruta, no la cantidad: "Implementacion" se crea sola al
# crear sus hijas, asi que el conteo da 9 y no 8.
$faltan = @()
foreach ($s in $subs) { if (-not (Test-Path (Join-Path $carpeta $s))) { $faltan += $s } }
Chequear ($faltan.Count -eq 0) "existen las $($subs.Count) subcarpetas estandar" $(if ($faltan.Count) { "faltan: " + ($faltan -join ", ") } else { "todas" })
Chequear (Test-Path $destino) "el machote quedo copiado en Matriz-Oferta"

# ---------------------------------------------------------------
# 4 a 8. Todo lo que pasa dentro de Excel
# ---------------------------------------------------------------
$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false
function Hoja($wb, $p, $x) { foreach ($h in $wb.Worksheets) { if ($h.Name -like $p) { if ($x -and $h.Name -like $x) { continue }; return $h } } }

try {
    $wb  = $excel.Workbooks.Open($destino)
    $eq  = $wb.Worksheets.Item("Equipos")
    $cot = Hoja $wb "COTIZACI*" "*Financ*"
    $cfn = Hoja $wb "*Financ)*" $null
    $dp  = $wb.Worksheets.Item("Datos del proyecto")

    Write-Output ""
    Write-Output "--- 4. Las guias viajan con la copia ---"
    foreach ($g in @("LEEME", "Guia de pestanas", "Guia de formulas", "Guia de skills")) {
        $existe = $false
        foreach ($w in $wb.Worksheets) { if ($w.Name -eq $g) { $existe = $true } }
        Chequear $existe ("la pestana '{0}' esta en la copia" -f $g)
    }
    $primera = $wb.Worksheets.Item(1).Name
    Chequear ($primera -eq "LEEME") "LEEME es la primera pestana" $primera

    Write-Output ""
    Write-Output "--- 5. Se escribe el equipo (solo las 4 columnas de entrada) ---"
    $eq.Range("B6").Value2 = "PAR-P4BIRA2812NH-AI - 4MP IP Outdoor Bullet, 2.8-12mm Motorized AF"
    $eq.Range("C6").Value2 = "si"
    $eq.Range("D6").Value2 = 20
    $eq.Range("E6").Value2 = 135
    $eq.Range("B7").Value2 = "VN4A-32X24 - 32 Ch NVR con 24 puertos Plug and Play, 4K"
    $eq.Range("C7").Value2 = "si"
    $eq.Range("D7").Value2 = 1
    $eq.Range("E7").Value2 = 600
    $excel.CalculateFullRebuild()

    $esperados = @{
        "Equipos!O6 precio venta unitario camara" = 249.552613636364
        "Equipos!P6 total de la linea de camaras" = 4991.05227272727
        "Equipos!P7 total de la linea del NVR"    = 1109.12272727273
        "Equipos!P57 total de venta"              = 6100.175
    }
    $obtenidos = @{
        "Equipos!O6 precio venta unitario camara" = $eq.Range("O6").Value2
        "Equipos!P6 total de la linea de camaras" = $eq.Range("P6").Value2
        "Equipos!P7 total de la linea del NVR"    = $eq.Range("P7").Value2
        "Equipos!P57 total de venta"              = $eq.Range("P57").Value2
    }
    foreach ($k in ($esperados.Keys | Sort-Object)) {
        $e = [double]$esperados[$k]; $o = [double]$obtenidos[$k]
        Chequear ([Math]::Abs($e - $o) -lt 0.000001) $k ("esperado {0:N6}  obtenido {1:N6}" -f $e, $o)
    }

    Write-Output ""
    Write-Output "--- 6. COTIZACION espeja lo que se escribio ---"
    Chequear ($cot.Cells.Item(22, 2).Value2 -eq 20) "la cantidad se espeja" $cot.Cells.Item(22,2).Value2
    Chequear ($cot.Cells.Item(22, 3).Text -like "PAR-P4BIRA2812NH-AI*") "la descripcion se espeja"
    $sub = $cot.Range("J74").Value2
    Chequear ([Math]::Abs($sub - 6100.175) -lt 0.001) "el SUBTOTAL cuadra con Equipos!P57" ("{0:N2}" -f $sub)

    Write-Output ""
    Write-Output "--- 7. El impuesto sale de la ficha, no de la formula ---"
    $dp.Range("B15").Formula = ""
    $dp.Range("B16").Formula = ""
    $excel.CalculateFullRebuild()
    $imp13 = $cot.Range("J75").Value2
    $tot13 = $cot.Range("J76").Value2
    Chequear ([Math]::Abs($imp13 / $sub - 0.13) -lt 0.000001) "ficha vacia: aplica 13%" ("impuesto {0:N2}, total {1:N2}" -f $imp13, $tot13)

    $dp.Range("B15").Formula = "si"
    $excel.CalculateFullRebuild()
    $imp0 = $cot.Range("J75").Value2
    $tot0 = $cot.Range("J76").Value2
    Chequear ($imp0 -eq 0) "cliente exento: el impuesto baja a cero" ("total {0:N2}, se ahorra {1:N2}" -f $tot0, $imp13)
    Chequear ($cfn.Range("J75").Value2 -eq 0) "la cotizacion financiada respeta la exencion"
    Write-Output ("         eco de la ficha: '{0}'" -f $dp.Range("C16").Text)

    $dp.Range("B15").Formula = "no"
    $dp.Range("B16").Formula = "2"
    $excel.CalculateFullRebuild()
    Chequear ([Math]::Abs($cot.Range("J75").Value2 / $sub - 0.02) -lt 0.000001) "cliente al 2% escrito como '2'" ("{0:N2}" -f $cot.Range("J75").Value2)

    Write-Output ""
    Write-Output "--- 8. Financiamiento no se asume ---"
    Chequear ([string]$cfn.Range("I22").Value2 -eq "") "sin ID en Financ., la cuota queda vacia"
    Chequear ($wb.Worksheets.Item("Financiamiento").Range("C4").Value2 -eq 0) "el cuadro 1 de Financiamiento esta en cero"

    Write-Output ""
    Write-Output "--- 9. Cero errores de Excel en todo el libro ---"
    $err = 0
    foreach ($w in $wb.Worksheets) {
        try { $x = $w.UsedRange.SpecialCells(-4123, 16); if ($x -ne $null) { Write-Output ("         {0}: {1}" -f $w.Name, $x.Address($false,$false)); $err += $x.Count } } catch { }
    }
    Chequear ($err -eq 0) ("ninguna celda en error en las {0} pestanas" -f $wb.Worksheets.Count)

    Write-Output ""
    Write-Output "--- 10. El monto que iria a los Excels de control ---"
    $dp.Range("B15").Formula = ""
    $dp.Range("B16").Formula = ""
    $excel.CalculateFullRebuild()
    Write-Output ("         SUBTOTAL (va al control, columna 'Monto sin IVA'):  `$ {0:N2}" -f $cot.Range("J74").Value2)
    Write-Output ("         TOTAL con impuesto (NO va al control):             `$ {0:N2}" -f $cot.Range("J76").Value2)
    Write-Output "         Este script no escribe en los Excels de control: solo muestra el numero."

    $wb.Save()
    $wb.Close($false)
}
finally {
    $excel.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($excel) | Out-Null
    [GC]::Collect(); [GC]::WaitForPendingFinalizers()
}

Write-Output ""
if ($Conservar) {
    Write-Output ("Carpeta conservada en: {0}" -f $carpeta)
    Write-Output "Para borrarla:  git clean -fd sandbox-pruebas/"
} else {
    Remove-Item $carpeta -Recurse -Force
    Write-Output "Carpeta de prueba borrada (usa -Conservar para dejarla)."
}

Write-Output ""
if ($fallas -eq 0) { Write-Output "RESULTADO: la cotizacion completa sale correcta." }
else { Write-Output ("RESULTADO: {0} verificacion(es) fallaron. Revisar arriba." -f $fallas) }
exit $(if ($fallas -eq 0) { 0 } else { 1 })
