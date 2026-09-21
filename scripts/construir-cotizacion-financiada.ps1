# Construye la pestana de cotizacion financiada en el machote, copiando la
# logica de una cotizacion real de la empresa (opcion A) pero conservando el
# vinculo por ID de la columna Financ. en vez de la posicion fija.
#
# Dos partes:
#   1. Los cuadros de Financiamiento pasan a medir el PRECIO UNITARIO.
#      Antes sumaban el total de la linea; si esa cuota se muestra como
#      "Precio Unitario Mensual" y se multiplica por la cantidad, el monto
#      se contaria dos veces.
#   2. Se duplica 'COTIZACION ' y se cambian tres cosas: los encabezados de
#      precio, el origen del precio unitario (la cuota del cuadro que le
#      corresponde por ID) y la etiqueta del total.
$ErrorActionPreference = "Stop"
$path = (Resolve-Path "plugin-preventa\skills\armar-cotizacion\references\Machote Matriz y oferta.xlsx").Path

$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false

try {
    $wb = $excel.Workbooks.Open($path)

    # --- localizar hojas por nombre (sin depender del indice) ---
    $hCot = $null; $hFin = $null; $hEq = $null
    foreach ($h in $wb.Worksheets) {
        if ($h.Name -like "COTIZACI*" -and $h.Name -notlike "*Financ*") { $hCot = $h }
        if ($h.Name -eq "Financiamiento") { $hFin = $h }
        if ($h.Name -eq "Equipos") { $hEq = $h }
    }
    Write-Output ("cotizacion: '{0}'  financiamiento: '{1}'  equipos: '{2}'" -f $hCot.Name, $hFin.Name, $hEq.Name)

    # =========== 1. cuadros: del total al unitario ===========
    $cambiados = 0
    $bloques = @(
        @{ col = 3;  hoja = "Equipos";      de = "`$P`$";  a = "`$O`$" },
        @{ col = 9;  hoja = "Productos 2";  de = "`$O`$";  a = "`$N`$" },
        @{ col = 15; hoja = "MATERIALES";   de = "`$O`$";  a = "`$N`$" },
        @{ col = 21; hoja = "OPEX GV";      de = "`$O`$";  a = "`$N`$" }
    )
    for ($r = 1; $r -le $hFin.UsedRange.Rows.Count; $r++) {
        foreach ($b in $bloques) {
            $cel = $hFin.Cells.Item($r, $b.col)
            $f = $cel.Formula
            if ($f -is [string] -and $f.StartsWith("=SUMIF(") -and $f.Contains($b.hoja)) {
                # el segundo rango del SUMIF es el que se suma: cambiar su columna
                $partes = $f -split ","
                if ($partes.Count -eq 3) {
                    $partes[2] = $partes[2].Replace($b.de, $b.a)
                    $nueva = $partes -join ","
                    if ($nueva -ne $f) { $cel.Formula = $nueva; $cambiados++ }
                }
            }
        }
    }
    Write-Output ("cuadros de financiamiento pasados a precio unitario: {0}" -f $cambiados)
    Write-Output ("  ejemplo C4 = {0}" -f $hFin.Range("C4").Formula)

    # =========== 2. la pestana de cotizacion financiada ===========
    $nombreNuevo = "COTIZACION (Financ)"
    foreach ($h in @($wb.Worksheets)) { if ($h.Name -eq $nombreNuevo) { $h.Delete() } }

    $hCot.Copy([System.Reflection.Missing]::Value, $hCot) | Out-Null
    $hNew = $wb.Worksheets.Item($hCot.Index + 1)
    $hNew.Name = $nombreNuevo
    Write-Output ("creada '{0}' en la posicion {1}, justo despues de la cotizacion normal" -f $hNew.Name, $hNew.Index)

    # encabezados de las columnas de precio
    $hNew.Range("I20").Value2 = "Precio Unitario Mensual"
    $hNew.Range("J20").Value2 = "Total Mensual"

    # precio unitario = cuota mensual del cuadro que le toca por ID.
    # el cuadro n arranca en la fila 3+(n-1)*17 y su cuota esta 9 filas abajo.
    $FILA_INI = 22   # primera linea de la cotizacion
    $FILA_FIN = 71   # ultima (50 lineas)
    for ($r = $FILA_INI; $r -le $FILA_FIN; $r++) {
        $filaEq = $r - 16
        $f = '=IFERROR(IF(Equipos!Q{0}="","",INDEX(Financiamiento!$C:$C,12+(Equipos!Q{0}-1)*17)),"")' -f $filaEq
        $hNew.Cells.Item($r, 9).Formula = $f
    }
    Write-Output ("precio unitario enlazado a la cuota por ID en las filas {0} a {1}" -f $FILA_INI, $FILA_FIN)

    # etiqueta del total
    $hNew.Range("I76").Value2 = "TOTAL MENSUAL"

    $excel.CalculateFullRebuild()
    Write-Output ""
    Write-Output "verificacion:"
    Write-Output ("  I20 = {0}" -f $hNew.Range("I20").Value2)
    Write-Output ("  J20 = {0}" -f $hNew.Range("J20").Value2)
    Write-Output ("  I22 = {0}" -f $hNew.Range("I22").Formula)
    Write-Output ("  J22 = {0}" -f $hNew.Range("J22").Formula)
    Write-Output ("  I71 = {0}" -f $hNew.Range("I71").Formula)
    Write-Output ("  I74/I75/I76 = {0} / {1} / {2}" -f $hNew.Range("I74").Value2, $hNew.Range("I75").Value2, $hNew.Range("I76").Value2)
    Write-Output ("  J76 = {0}" -f $hNew.Range("J76").Formula)
    Write-Output ("  hojas totales: {0}" -f $wb.Worksheets.Count)

    $wb.Save()
    $wb.Close($false)
    Write-Output "GUARDADO"
}
finally {
    $excel.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($excel) | Out-Null
    [GC]::Collect(); [GC]::WaitForPendingFinalizers()
}
