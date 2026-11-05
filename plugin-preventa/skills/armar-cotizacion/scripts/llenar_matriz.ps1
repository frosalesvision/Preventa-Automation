# Copia el machote a $Destino (que no debe existir) y escribe las celdas de
# entrada que trae $Datos, un JSON en UTF-8:
#   {"celdas": [{"hoja": "Equipos", "celda": "B6", "valor": "..."}, ...],
#    "leer":   [["<hoja>", "J76"], ...]}
#   Una celda con formula no se escribe, salvo que traiga "reemplaza_formula": true.
# Dos llaves opcionales; si no vienen, la matriz sale como siempre:
#   "opex_filas_extra": 3    OPEX GV trae 10 lineas (filas 6-15): agrega filas con las mismas formulas.
#                            Las lineas pasan a ir de la 6 a la 15 + N; el total baja N filas.
#   "oferta_por_sistema": {"primer_titulo": "SISTEMA 1", "filas_titulo_equipos": [14, 19]}
#                            Solo si el pedido lo pide (R31). El primer titulo va en la fila 21 de la
#                            cotizacion; los demas son filas de Equipos con solo la descripcion.
# Recalcula, lee las celdas de "leer"
# (valor y texto como lo muestra Excel), cuenta las celdas con error de las
# hojas visibles y guarda. Excel por COM, nunca openpyxl (borra imagenes).
#   powershell -File llenar_matriz.ps1 -Machote "<references/Machote...xlsx>" -Destino "<.../Matriz y oferta X.xlsx>" -Datos "<celdas.json>"
# En CLIENTES solo con la carpeta ya confirmada por el asesor (armar-cotizacion).
param(
    [Parameter(Mandatory = $true)][string]$Machote,
    [Parameter(Mandatory = $true)][string]$Destino,
    [Parameter(Mandatory = $true)][string]$Datos
)
$ErrorActionPreference = "Stop"
function Poner($celda, $valor) { [void][System.__ComObject].InvokeMember("Value2", [System.Reflection.BindingFlags]::SetProperty, $null, $celda, @(, $valor)) }

if (Test-Path -LiteralPath $Destino) { throw "ya existe: $Destino" }
$dir = Split-Path -Parent $Destino
if (-not (Test-Path -LiteralPath $dir)) { New-Item -ItemType Directory -Path $dir | Out-Null }
Copy-Item -LiteralPath $Machote -Destination $Destino
$d = Get-Content -LiteralPath $Datos -Raw -Encoding UTF8 | ConvertFrom-Json

$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false; $excel.DisplayAlerts = $false
try {
    $wb = $excel.Workbooks.Open($Destino)
    $hojas = @{}
    foreach ($ws in $wb.Worksheets) { $hojas[$ws.Name] = $ws }
    # Antes de escribir, para que las celdas del JSON caigan en las filas nuevas. Copia la fila 14
    # con sus formulas; los totales y las referencias de las otras pestanas se corren solos.
    if ($d.opex_filas_extra) {
        $ox = $hojas["OPEX GV"]
        $hasta = 14 + [int]$d.opex_filas_extra
        [void]$ox.Range("15:$hasta").EntireRow.Insert()
        [void]$ox.Range("A14:Q14").Copy($ox.Range("A15:Q$hasta"))
        Write-Output ("OPEX GV: {0} filas mas, lineas de la 6 a la {1}" -f $d.opex_filas_extra, ($hasta + 1))
    }
    foreach ($c in $d.celdas) {
        if (-not $hojas.ContainsKey($c.hoja)) { throw "no existe la hoja [$($c.hoja)]" }
        $cel = $hojas[$c.hoja].Range($c.celda)
        # Una formula no se pisa, salvo que el dato diga "reemplaza_formula": true. Es para
        # las pocas entradas que el machote trae calculadas y preventa pone a mano
        # (ej. MANO DE OBRA!I5, combustible por dia, que viene de Transporte).
        if ($cel.HasFormula -and -not $c.reemplaza_formula) { throw "$($c.hoja)!$($c.celda) tiene formula, no se escribe" }
        if ($cel.HasFormula) { Write-Output ("REEMPLAZA FORMULA {0}!{1}: [{2}]" -f $c.hoja, $c.celda, $cel.Formula) }
        $antes = $cel.Value2
        $v = $c.valor
        if ($v -is [int] -or $v -is [long]) { $v = [double]$v }
        Poner $cel $v
        Write-Output ("ESCRITO {0}!{1}: [{2}] -> [{3}]" -f $c.hoja, $c.celda, $antes, $cel.Value2)
    }
    # Oferta dividida por sistema (R31). En las cotizaciones (fila de Equipos + 16) la fila de titulo
    # queda sin cantidad ni precios: con cantidad 0, exportar_pdf.ps1 la ocultaria.
    if ($d.oferta_por_sistema) {
        $eq = $hojas["Equipos"]
        $sis = $d.oferta_por_sistema
        foreach ($f in $sis.filas_titulo_equipos) {
            if (([string]$eq.Range("B$f").Value2).Trim() -eq "") { throw "Equipos!B$f es fila de titulo y esta vacia" }
            if ($eq.Range("D$f").Value2 -ne 0 -or $eq.Range("E$f").Value2 -ne 0) { throw "Equipos fila $f es de titulo: no puede llevar cantidad ni costo" }
            $eq.Range("B$f").Font.Bold = $true
        }
        if ($sis.primer_titulo) { $b5 = $eq.Range("B5"); Poner $b5 $sis.primer_titulo }
        foreach ($n in @($hojas.Keys | Where-Object { $_ -like "COTIZACI*" })) {
            $h = $hojas[$n]
            $m = $h.Range("C21")
            if ($sis.primer_titulo) { Poner $m $sis.primer_titulo }
            foreach ($f in $sis.filas_titulo_equipos) {
                $t = [int]$f + 16
                foreach ($col in "B", "I", "J") { [void]$h.Range("$col$t").ClearContents() }
                $r = $h.Range("B${t}:J$t")
                $r.Interior.Color = $m.Interior.Color
                $r.Font.Bold = $true
                $r.Font.Color = $m.Font.Color
                $h.Rows.Item($t).RowHeight = $h.Rows.Item(21).RowHeight
            }
        }
        Write-Output ("Oferta por sistema: titulos en las filas {0} de Equipos" -f ($sis.filas_titulo_equipos -join ", "))
    }
    $excel.CalculateFull()
    foreach ($par in $d.leer) {
        $cel = $hojas[$par[0]].Range($par[1])
        Write-Output ("LEIDO {0}!{1}: valor={2} texto=[{3}]" -f $par[0], $par[1], $cel.Value2, $cel.Text)
    }
    $errores = 0
    foreach ($ws in $wb.Worksheets) {
        if ($ws.Visible -ne -1) { continue }
        try { $r = $ws.UsedRange.SpecialCells(-4123, 16); $n = $r.Count; $errores += $n; Write-Output ("ERRORES en [{0}]: {1} ({2})" -f $ws.Name, $n, $r.Address(0, 0)) } catch { }
    }
    Write-Output "CELDAS EN ERROR (hojas visibles): $errores"
    $wb.Save()
    $wb.Close($false)
    Write-Output "GUARDADO: $Destino"
}
finally {
    $excel.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($excel) | Out-Null
}
# Lo que se ve: lineas usadas + 3 y, si no lleva financiamiento, sus pestanas ocultas.
& (Join-Path $PSScriptRoot "ajustar_vista.ps1") -Ruta $Destino
