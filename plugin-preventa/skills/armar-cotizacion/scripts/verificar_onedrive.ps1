# Verifica que OneDrive subio a la nube lo que se escribio (regla R26): cada archivo dado, o todo
# lo que hay dentro de cada carpeta dada, tiene que quedar en la nube: estado 2 (sincronizado) o 1
# (esta en la nube y no se descargo a esta PC, ej. lo subio otra persona). Espera hasta
# -Segundos. Si un Excel sigue en 4 (falta subir) o 10 (pendiente), lo abre por Excel en lectura-escritura y lo
# cierra sin guardar, que es lo que lo destraba (nunca reiniciar OneDrive), y vuelve a esperar.
# Imprime el estado de cada archivo y sale con codigo 1 si algo no quedo sincronizado.
#
#   powershell -NoProfile -ExecutionPolicy Bypass -File verificar_onedrive.ps1 "<archivo o carpeta>" ["<otro>" ...] [-Segundos 180]
#
# Estados (System.StorageProviderState): 2 sincronizado, 1 solo en la nube, 4 falta subir,
# 10 sincronizacion pendiente; cualquier otro se informa con su numero y el texto del Explorador. Un archivo "~$..." en la carpeta = alguien lo tiene
# abierto: se avisa. Una ruta de mas de 259 caracteres tambien: Windows y Excel no la abren
# (un PDF asi, subido desde otra PC, aca ni se descarga).
param(
    [int]$Segundos = 180,
    [Parameter(Mandatory = $true, Position = 0, ValueFromRemainingArguments = $true)][string[]]$Rutas
)
$ErrorActionPreference = "Stop"
$sh = New-Object -ComObject Shell.Application
function Estado($p) { return $sh.Namespace((Split-Path -Parent $p)).ParseName((Split-Path -Leaf $p)).ExtendedProperty("System.StorageProviderState") }
function Nombre($e) { switch ($e) { 2 { "sincronizado" } 1 { "en la nube" } 4 { "falta subir" } 10 { "pendiente" } default { "estado $e" } } }
# el texto que muestra el Explorador (columna "Estado de disponibilidad"), para lo que no es 1 ni 2
function Texto($p) {
    $f = $sh.Namespace((Split-Path -Parent $p))
    if ($script:colDisp -eq $null) {
        $script:colDisp = -1
        foreach ($i in 0..400) { if ($f.GetDetailsOf($null, $i) -match '^(Estado de disponibilidad|Availability status)$') { $script:colDisp = $i; break } }
    }
    if ($script:colDisp -lt 0) { return "" }
    return $f.GetDetailsOf($f.ParseName((Split-Path -Leaf $p)), $script:colDisp)
}
function EnNube($p) { return @(1, 2) -contains (Estado $p) }

# por el Shell y no por Get-ChildItem: asi tambien salen los de ruta de mas de 259 (el Shell da
# esas rutas en nombre corto 8.3, por eso se arma la ruta larga con el nombre real del archivo)
function Listar($dir) {
    foreach ($i in $sh.NameSpace($dir).Items()) {
        $p = Join-Path $dir ([string]$i.ExtendedProperty("System.FileName"))
        if ($i.IsFolder -and $p -notmatch '\.zip$') { Listar $p }
        elseif ($i.Name -ne "desktop.ini") { $p }
    }
}

if (-not (Get-Process OneDrive -ErrorAction SilentlyContinue)) { Write-Output "NO SINCRONIZADO: OneDrive no esta corriendo"; exit 1 }
$archivos = @(); $abiertos = @()
foreach ($r in $Rutas) {
    if (-not (Test-Path -LiteralPath $r)) { Write-Output "NO EXISTE: $r"; exit 1 }
    if ($r -notlike "*OneDrive*") { Write-Output "FUERA DE ONEDRIVE (no se sube): $r"; exit 1 }
    if (Test-Path -LiteralPath $r -PathType Container) {
        $archivos += @(Listar $r)
        $abiertos += @(Get-ChildItem -LiteralPath $r -Recurse -Force -Filter '~$*' -ErrorAction SilentlyContinue | ForEach-Object { $_.FullName })
    }
    else {
        $archivos += $r
        # Excel le pone "~$" adelante del nombre; Word, en vez de las dos primeras letras
        $hoja = Split-Path -Leaf $r
        $abiertos += @(Get-ChildItem -LiteralPath (Split-Path -Parent $r) -Force -Filter '~$*' -ErrorAction SilentlyContinue |
            Where-Object { $_.Name -eq ('~$' + $hoja) -or $_.Name -eq ('~$' + $hoja.Substring(2)) } | ForEach-Object { $_.FullName })
    }
}
$archivos = @($archivos | Where-Object { (Split-Path -Leaf $_) -notlike '~$*' })
foreach ($a in $abiertos) { Write-Output ("ABIERTO por alguien: {0}" -f $a) }
$largos = @($archivos | Where-Object { $_.Length -gt 259 })
foreach ($a in $largos) { Write-Output ("RUTA DE {0} CARACTERES (Windows y Excel no la abren, maximo 259): {1}" -f $a.Length, $a) }

function Esperar($lista, $seg) {
    $hasta = (Get-Date).AddSeconds($seg)
    while ($true) {
        $pend = @($lista | Where-Object { -not (EnNube $_) })
        if ($pend.Count -eq 0 -or (Get-Date) -gt $hasta) { return $pend }
        Start-Sleep -Seconds 5
    }
}

$pend = Esperar $archivos $Segundos
# 4 "falta subir" o 10 "sincronizacion pendiente": un Excel guardado por COM se queda asi a veces
$trabados = @($pend | Where-Object { @(4, 10) -contains (Estado $_) -and $_ -match '\.xls[xm]$' })
if ($trabados.Count -gt 0) {
    $excel = New-Object -ComObject Excel.Application
    $excel.Visible = $false; $excel.DisplayAlerts = $false
    try {
        foreach ($t in $trabados) {
            $wb = $excel.Workbooks.Open($t, 0, $false)
            $ro = $wb.ReadOnly
            $wb.Close($false)
            if ($ro) { Write-Output ("DESTRABAR: se abrio solo lectura (alguien lo tiene abierto): {0}" -f $t) }
            else { Write-Output ("DESTRABAR: abierto y cerrado sin guardar: {0}" -f $t) }
        }
    }
    finally {
        $excel.Quit()
        [System.Runtime.InteropServices.Marshal]::ReleaseComObject($excel) | Out-Null
    }
    $pend = Esperar $archivos $Segundos
}

foreach ($a in $archivos) {
    $e = Estado $a
    $extra = if (@(1, 2) -contains $e) { "" } else { " (Explorador: {0})" -f (Texto $a) }
    Write-Output ("{0,-13} {1}{2}" -f (Nombre $e), $a, $extra)
}
if ($pend.Count -eq 0 -and $abiertos.Count -eq 0 -and $largos.Count -eq 0) { Write-Output ("TODO SINCRONIZADO: {0} archivos" -f $archivos.Count); exit 0 }
if ($pend.Count -gt 0) { Write-Output ("NO SINCRONIZADO: {0} de {1} archivos" -f $pend.Count, $archivos.Count) }
else { Write-Output ("EN LA NUBE, pero con avisos: {0} abierto(s) por alguien, {1} con ruta larga" -f $abiertos.Count, $largos.Count) }
exit 1
