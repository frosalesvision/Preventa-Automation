# Exporta a PDF SOLO la pestana de cotizacion de una matriz (la de contado, o la financiada con
# -Financiada), por Excel (COM). La matriz se cierra SIN guardar: ocultar las lineas vacias es
# solo para el PDF.
#
#   powershell -NoProfile -ExecutionPolicy Bypass -File exportar_pdf.ps1 -Matriz "<xlsx>" -Pdf "<pdf>" [-Financiada]
#
# No exporta si: la pestana tiene celdas en error, la ruta del PDF pasa de 259 caracteres
# (Windows y Excel no la abren) o el PDF ya existe (se decide con el asesor: reemplazar o V2).
param(
    [Parameter(Mandatory = $true)][string]$Matriz,
    [Parameter(Mandatory = $true)][string]$Pdf,
    [switch]$Financiada
)
$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $Matriz)) { throw "no existe la matriz: $Matriz" }
if (Test-Path -LiteralPath $Pdf) { throw "ya existe el PDF (reemplazar o V2 lo decide el asesor): $Pdf" }
if ($Pdf.Length -gt 259) { throw ("la ruta del PDF tiene {0} caracteres (maximo 259): acortar el nombre" -f $Pdf.Length) }
$patron = if ($Financiada) { '^COTIZACI.N \(Financ' } else { '^COTIZACI.N$' }

$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false; $excel.DisplayAlerts = $false
try {
    $wb = $excel.Workbooks.Open($Matriz, 0, $true)          # solo lectura
    $h = $null
    foreach ($w in $wb.Worksheets) { if ($w.Name.Trim() -match $patron) { $h = $w } }
    if ($h -eq $null) { throw "no encontre la pestana de cotizacion ($patron)" }

    $errores = $null
    try { $errores = $h.UsedRange.SpecialCells(-4123, 16) } catch { }     # formulas con error
    if ($errores -ne $null) { throw ("celdas en error en [{0}]: {1}" -f $h.Name, $errores.Address(0, 0)) }

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
    if ($primera -eq 0 -or $ultima -eq 0) { throw "no encontre el bloque de lineas (Cantidad ... SUBTOTAL)" }
    $lineas = 0
    for ($r = $primera; $r -le $ultima; $r++) {
        $q = $h.Cells.Item($r, 2).Value2
        if (($q -is [double]) -and ($q -eq 0)) { $h.Rows.Item($r).Hidden = $true }
        elseif (($q -is [double]) -and -not $h.Rows.Item($r).Hidden) { $lineas++ }
    }

    # textos del machote para llenar, como "[Nombre del asesor responsable]" o "[correo del asesor]"
    $pendientes = @()
    foreach ($c in $h.UsedRange.Cells) {
        if (-not $c.EntireRow.Hidden -and ([string]$c.Value2) -match '\[[^\]]+\]') { $pendientes += ("{0}: {1}" -f $c.Address(0, 0), ([string]$c.Value2).Trim()) }
    }
    if ($pendientes.Count -gt 0) { throw ("quedan textos del machote sin llenar: {0}" -f ($pendientes -join " | ")) }

    # Como los PDF reales de preventa: pagina 1 = encabezado, lineas y totales; despues forma
    # de pago y firma. 2026-10-27: con "ajustar a 1 de ancho" el TOTAL quedo solo en la pagina 2
    # (subtotal e impuesto en la 1), y en otra el PDF salio con una pagina mas que la que
    # calculaba Excel (mide con la impresora activa). Por eso la escala se calcula aca, con un
    # salto manual despues del TOTAL, y se baja un poco si el PDF sale con mas paginas.
    $ultimaLinea = 0
    for ($r = $primera; $r -le $ultima; $r++) {
        if (($h.Cells.Item($r, 2).Value2 -is [double]) -and -not $h.Rows.Item($r).Hidden) { $ultimaLinea = $r }
    }
    $filaTotal = 0
    for ($r = $ultima + 1; $r -le $ultima + 15 -and $filaTotal -eq 0; $r++) {
        for ($c = 1; $c -le 12; $c++) { if (([string]$h.Cells.Item($r, $c).Value2).Trim() -eq "TOTAL") { $filaTotal = $r; break } }
    }
    if ($ultimaLinea -eq 0 -or $filaTotal -eq 0) { throw "no encontre la ultima linea o la fila del TOTAL" }

    $ps = $h.PageSetup
    # asignado adentro del if: como resultado de una expresion, PowerShell desarma el rango en celdas
    if ($ps.PrintArea) { $area = $h.Range($ps.PrintArea) } else { $area = $h.UsedRange }
    $fin = $area.Row + $area.Rows.Count - 1
    $col1 = $area.Column
    $papel = @{ 1 = @(612, 792); 5 = @(612, 1008); 9 = @(595.3, 841.9) }     # carta, oficio, A4 (pt)
    $dim = $papel[[int]$ps.PaperSize]
    if ($dim -eq $null) { throw ("tamano de papel no previsto: {0}" -f $ps.PaperSize) }
    $anchoUtil = $dim[1] - $ps.LeftMargin - $ps.RightMargin                  # horizontal
    $altoUtil = $dim[0] - $ps.TopMargin - $ps.BottomMargin
    $altos = @{}
    for ($r = $area.Row; $r -le $fin; $r++) { $altos[$r] = if ($h.Rows.Item($r).Hidden) { 0 } else { $h.Rows.Item($r).Height } }
    function Alto($desde, $hasta) { $t = 0; for ($r = $desde; $r -le $hasta; $r++) { $t += $altos[$r] }; return $t }
    # paginas que salen con una escala, y donde va un salto manual para no partir los totales
    # (si un salto cae entre la ultima linea y el TOTAL, la ultima linea pasa con los totales)
    function Simular($z) {
        $cap = $altoUtil * 0.97 * 100 / $z
        $acum = 0; $pags = 1; $saltos = @()
        for ($r = $area.Row; $r -le $fin; $r++) {
            if ($altos[$r] -eq 0) { continue }
            if ($acum + $altos[$r] -gt $cap) {
                $pags++
                if ($r -gt $ultimaLinea -and $r -le $filaTotal) { $saltos += $ultimaLinea; $acum = Alto $ultimaLinea ($r - 1) }
                else { $acum = 0 }
            }
            $acum += $altos[$r]
        }
        return @{ paginas = $pags; saltos = $saltos }
    }
    $ancho = 0
    for ($c = $col1; $c -lt $col1 + $area.Columns.Count; $c++) { if (-not $h.Columns.Item($c).Hidden) { $ancho += $h.Columns.Item($c).Width } }
    $maxZoom = [int][math]::Floor([math]::Min(1.0, $anchoUtil / $ancho) * 97)

    $ps.Orientation = 2
    [void]$h.ResetAllPageBreaks()
    $zoom = [int][math]::Floor([math]::Min($maxZoom, 97 * [math]::Min($altoUtil / (Alto $area.Row $filaTotal), $altoUtil / (Alto ($filaTotal + 1) $fin))))
    if ($zoom -ge 80) {
        [void]$h.HPageBreaks.Add($h.Cells.Item($filaTotal + 1, $col1))
        $esperadas = 2
        $modo = "lineas y totales en la pagina 1"
    }
    else {
        # no entran en la pagina 1 sin achicar de mas: las lineas siguen en la pagina 2, con la
        # escala mas grande (hasta 75%) que da la menor cantidad de paginas
        $mejor = $null
        for ($z = $maxZoom; $z -ge 75; $z -= 3) {
            $sim = Simular $z
            if ($mejor -eq $null -or $sim.paginas -lt $mejor.paginas) { $mejor = @{ zoom = $z; paginas = $sim.paginas; saltos = $sim.saltos } }
        }
        $zoom = $mejor.zoom
        $esperadas = $mejor.paginas
        foreach ($f in $mejor.saltos) { [void]$h.HPageBreaks.Add($h.Cells.Item($f, $col1)) }
        $modo = "lineas en varias paginas, totales sin partir"
    }

    $tmp = Join-Path $env:TEMP ("exportar_pdf_{0}.pdf" -f [guid]::NewGuid().ToString("N"))
    for ($intento = 1; $intento -le 4; $intento++) {
        $ps.Zoom = $zoom
        if (Test-Path -LiteralPath $tmp) { Remove-Item -LiteralPath $tmp }
        $h.ExportAsFixedFormat(0, $tmp)
        $paginas = ([regex]::Matches([System.IO.File]::ReadAllText($tmp, [System.Text.Encoding]::GetEncoding(28591)), '/Type\s*/Page[^s]')).Count
        if ($paginas -le $esperadas -or $zoom -lt 50) { break }
        $zoom -= 3
    }
    $nombre = $h.Name
    $wb.Close($false)                      # SIN guardar
    Move-Item -LiteralPath $tmp -Destination $Pdf
    Write-Output ("PDF: {0}" -f $Pdf)
    Write-Output ("pestana [{0}], {1} lineas con cantidad, {2} paginas (esperadas {3}), escala {4}%: {5}" -f $nombre, $lineas, $paginas, $esperadas, $zoom, $modo)
    if ($paginas -gt $esperadas) { Write-Output "REVISAR: el PDF salio con mas paginas que las calculadas; mirar que los totales no queden partidos" }
}
finally {
    $excel.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($excel) | Out-Null
}
