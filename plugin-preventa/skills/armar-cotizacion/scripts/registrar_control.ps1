# Registra una cotizacion en una pestana de los Excels de control (Control de cotizaciones 2026,
# Cotizaciones en Preventa): agrega UNA fila debajo de la ultima con datos, por Excel (COM),
# nunca openpyxl (los dos archivos tienen imagenes y comentarios). Con -Quitar, borra la fila
# que se registro (una cotizacion de prueba o anulada). Con -Actualizar, reescribe celdas de la
# fila ya registrada (la cotizacion se corrigio y cambio el monto o la descripcion).
#
#   powershell -NoProfile -ExecutionPolicy Bypass -File registrar_control.ps1 -Ruta "<xlsx>" -Hoja "<pestana>" -Datos "<fila.json>" [-Guardar]
#   powershell -NoProfile -ExecutionPolicy Bypass -File registrar_control.ps1 -Ruta "<xlsx>" -Hoja "<pestana>" -Datos "<buscar.json>" -Quitar [-Guardar]
#   powershell -NoProfile -ExecutionPolicy Bypass -File registrar_control.ps1 -Ruta "<xlsx>" -Hoja "<pestana>" -Datos "<corregir.json>" -Actualizar [-Guardar]
#
# fila.json (UTF-8; los textos van aca para que este archivo quede en ASCII):
#   {"claves": ["A", "D"],                       columnas que dicen si una fila tiene datos
#    "celdas": {"A": {"fecha": "2026-10-27"},    fecha: con el formato de la ultima fecha de esa columna
#               "D": {"texto": "Cliente"},
#               "J": {"texto": "$1 234,56", "formato": "@"},   "@" = texto, para que el $ no se pierda
#               "K": {"formula": "=+NETWORKDAYS(A{f},$K$1)"}}} {f} = numero de la fila nueva
# buscar.json, para -Quitar: {"buscar": {"D": "Cliente", "I": "T5-0000001-26"}}
#   Se borra la fila entera solo si UNA fila coincide en todas esas columnas; si hay 0 o mas de 1, no toca nada.
#   El numero de oferta solo no alcanza: cada cliente lleva su consecutivo (hay dos T5-0000012-26).
# corregir.json, para -Actualizar: {"buscar": {...igual que arriba...}, "celdas": {...igual que fila.json...}}
#   Misma regla de UNA fila; muestra cada celda antes -> despues y no toca las columnas que no trae.
#   Cada celda lleva "antes": el valor que se espera encontrar, ej. {"texto": "$2 000,00", "formato": "@",
#   "antes": "$1 500,00"}. Si la celda dice otra cosa, alguien la cambio y no se toca nada (R28).
#
# Sin -Guardar: muestra lo que haria y cierra sin guardar.
# Con -Guardar termina con verificar_onedrive.ps1 (R26): sale con codigo 1 si no quedo en la nube.
# Seguridad: no corre sin OneDrive sincronizado; respaldo antes de abrir; apaga el Autoguardado;
# no escribe si la fila destino ya tiene algo en una columna a escribir; relee .Text de cada celda.
param(
    [Parameter(Mandatory = $true)][string]$Ruta,
    [Parameter(Mandatory = $true)][string]$Hoja,
    [Parameter(Mandatory = $true)][string]$Datos,
    [switch]$Quitar,
    [switch]$Actualizar,
    [switch]$Guardar
)
if ($Quitar -and $Actualizar) { throw "-Quitar o -Actualizar, no los dos" }
$ErrorActionPreference = "Stop"
$EN_US = [System.Globalization.CultureInfo]::GetCultureInfo("en-US")
function Poner($obj, $prop, $valor) { [void][System.__ComObject].InvokeMember($prop, [System.Reflection.BindingFlags]::SetProperty, $null, $obj, @(, $valor), $EN_US) }
function Txt($v) { if ($v -eq $null) { return "" } return ([string]$v).Trim() }
# la unica fila que coincide en todas las columnas de $buscar; si hay 0 o mas de 1, para
function UnaFila($ws, $fin, $buscar) {
    $cols = @($buscar.PSObject.Properties.Name)
    $hallado = @()
    for ($r = 1; $r -le $fin; $r++) {
        $ok = $true
        foreach ($c in $cols) { if ((Txt $ws.Range("$c$r").Value2) -ne (Txt $buscar.$c)) { $ok = $false; break } }
        if ($ok) { $hallado += $r }
    }
    if ($hallado.Count -ne 1) { throw ("coinciden {0} filas ({1}): no toco nada" -f $hallado.Count, ($hallado -join ", ")) }
    return $hallado[0]
}
# escribe una celda de fila.json: fecha (con el formato de la ultima fecha de la columna), formula o texto
function Escribir($ws, $c, $f, $x) {
    $cel = $ws.Range("$c$f")
    if ($x.formato) { Poner $cel "NumberFormat" $x.formato }
    if ($x.fecha) {
        # el formato de la ultima fecha de esa columna (la celda de arriba puede estar vacia y en General)
        $fmt = "dd/mm/yyyy"
        for ($r = $f - 1; $r -ge [math]::Max(1, $f - 60); $r--) {
            $arriba = $ws.Range("$c$r")
            if ($arriba.Value2 -is [double] -and $arriba.NumberFormat -ne "General") { $fmt = $arriba.NumberFormat; break }
        }
        Poner $cel "NumberFormat" $fmt
        Poner $cel "Value2" ([datetime]::ParseExact($x.fecha, "yyyy-MM-dd", $EN_US).ToOADate())
    }
    elseif ($x.formula) { Poner $cel "Formula" ($x.formula -replace '\{f\}', "$f") }
    else { Poner $cel "Value2" ([string]$x.texto) }
}
function EstadoNube($ruta) {
    $sh = New-Object -ComObject Shell.Application
    return $sh.Namespace((Split-Path -Parent $ruta)).ParseName((Split-Path -Leaf $ruta)).ExtendedProperty("System.StorageProviderState")
}

if (-not (Test-Path -LiteralPath $Ruta)) { throw "no existe: $Ruta" }
if ($Ruta -like "*OneDrive*") {
    if (-not (Get-Process OneDrive -ErrorAction SilentlyContinue)) { throw "OneDrive no esta corriendo: no escribo" }
    $st = EstadoNube $Ruta
    if ($st -ne 2) { throw ("el archivo no esta sincronizado (estado {0}): no escribo" -f $st) }
}
$D = Get-Content -LiteralPath $Datos -Raw -Encoding UTF8 | ConvertFrom-Json
$bak = Join-Path $env:TEMP ("control_antes_{0}_{1}.xlsx" -f ((Split-Path -Leaf $Ruta) -replace '\W', ''), (Get-Date -Format "yyyyMMdd_HHmmss"))
Copy-Item -LiteralPath $Ruta $bak
Write-Output ("respaldo: {0}" -f $bak)

$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false; $excel.DisplayAlerts = $false
try {
    $wb = $excel.Workbooks.Open($Ruta)
    $auto = $null; try { $auto = $wb.AutoSaveOn } catch { }
    if ($auto -eq $true) {
        [void][System.__ComObject].InvokeMember("AutoSaveOn", [System.Reflection.BindingFlags]::SetProperty, $null, $wb, @($false))
        if ($wb.AutoSaveOn -ne $false) { throw "no pude apagar el Autoguardado: no sigo" }
    }
    $ws = $wb.Worksheets.Item($Hoja)
    $fin = $ws.UsedRange.Row + $ws.UsedRange.Rows.Count - 1

    if ($Quitar) {
        $f = UnaFila $ws $fin $D.buscar
        $arriba = ($ws.Range("A$($f - 1):M$($f - 1)").Value2 | ForEach-Object { Txt $_ }) -join "|"
        $abajo = ($ws.Range("A$($f + 1):M$($f + 1)").Value2 | ForEach-Object { Txt $_ }) -join "|"
        Write-Output ("fila {0}: [{1}]" -f $f, (($ws.Range("A${f}:M$f").Value2 | ForEach-Object { Txt $_ }) -join " | "))
        [void]$ws.Rows.Item($f).Delete()
        # lo de arriba sigue igual y lo de abajo subio una fila; la buscada ya no esta
        if ((($ws.Range("A$($f - 1):M$($f - 1)").Value2 | ForEach-Object { Txt $_ }) -join "|") -ne $arriba) { throw "cambio la fila de arriba: no guardo" }
        if ((($ws.Range("A${f}:M$f").Value2 | ForEach-Object { Txt $_ }) -join "|") -ne $abajo) { throw "la fila de abajo no subio como se esperaba: no guardo" }
        Write-Output ("BORRADA la fila {0}; arriba igual, lo de abajo subio una fila" -f $f)
    }
    elseif ($Actualizar) {
        $f = UnaFila $ws $fin $D.buscar
        $cols = @($D.celdas.PSObject.Properties.Name)
        $antes = @{}
        foreach ($c in $cols) { $antes[$c] = $ws.Range("$c$f").Text }
        # R28: cada celda trae el valor que se espera encontrar; si alguien la cambio, no se toca nada
        foreach ($c in $cols) {
            $x = $D.celdas.$c
            if ($x.PSObject.Properties.Name -notcontains "antes") { throw "falta 'antes' en $c : -Actualizar exige el valor que se espera encontrar (R28)" }
            $cel = $ws.Range("$c$f")
            if ((Txt $cel.Value2) -ne (Txt $x.antes) -and (Txt $cel.Text) -ne (Txt $x.antes)) {
                throw ("$c$f dice [{0}] y se esperaba [{1}]: alguien la cambio, no toco nada (R28)" -f (Txt $cel.Text), (Txt $x.antes))
            }
        }
        foreach ($c in $cols) { Escribir $ws $c $f $D.celdas.$c }
        $excel.Calculate()
        foreach ($c in $cols) { Write-Output ("{0}{1}: [{2}] -> [{3}]" -f $c, $f, $antes[$c], $ws.Range("$c$f").Text) }
    }
    else {
        $ult = 0
        for ($r = $fin; $r -ge 1; $r--) {
            foreach ($c in $D.claves) {
                $v = $ws.Range("$c$r").Value2
                if ($v -ne $null -and "$v".Trim() -ne "") { $ult = $r; break }
            }
            if ($ult) { break }
        }
        $f = $ult + 1
        Write-Output ("ultima fila con datos: {0}; fila nueva: {1}" -f $ult, $f)
        $cols = @($D.celdas.PSObject.Properties.Name)
        foreach ($c in $cols) {
            $cel = $ws.Range("$c$f")
            if ($cel.HasFormula -or ($cel.Value2 -ne $null -and "$($cel.Value2)".Trim() -ne "")) { throw "la fila $f ya tiene algo en $c$f : no escribo" }
        }
        foreach ($c in $cols) { Escribir $ws $c $f $D.celdas.$c }
        $excel.Calculate()
        foreach ($c in $cols) { Write-Output ("{0}{1} = [{2}]" -f $c, $f, $ws.Range("$c$f").Text) }
    }
    if ($Guardar) {
        $wb.Save()
        Write-Output ("GUARDADO: {0}, pestana [{1}], fila {2}" -f $Ruta, $Hoja, $f)
    }
    else { Write-Output "prueba: no se guardo (falta -Guardar)" }
    $wb.Close($false)
}
finally {
    $excel.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($excel) | Out-Null
}
# R26: no esta hecho hasta que OneDrive lo subio
if ($Guardar -and $Ruta -like "*OneDrive*") {
    & (Join-Path $PSScriptRoot "verificar_onedrive.ps1") $Ruta
    exit $LASTEXITCODE
}
