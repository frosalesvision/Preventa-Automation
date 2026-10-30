# Agrega una subcategoria nueva al desplegable del catalogo: la escribe al final de _listas
# (C "Categoria > Subcategoria" y E "Subcategoria") y amplia la validacion de Catalogo!E hasta
# la nueva ultima fila. ANTES hay que agregarla en scripts/taxonomia.py; si no, buscar-equipo
# no la encuentra (actualizar-catalogo, "Desplegables de Categoria y Subcategoria").
# Excel por COM, nunca openpyxl (borra los desplegables). Sin -Guardar es una prueba.
#
#   powershell -NoProfile -ExecutionPolicy Bypass -File agregar_subcategoria.ps1 -Categoria "Control de acceso" -Subcategoria "Puerta / porton automatico" [-Guardar]
#
# Seguridad: OneDrive corriendo y el archivo sincronizado; respaldo; Autoguardado apagado; no
# agrega si ya esta o si la categoria no existe en _listas!A. Con -Guardar termina con
# verificar_onedrive.ps1 (R26).
param(
    [string]$Ruta = (Join-Path $env:USERPROFILE "OneDrive - GRUPO VISION - DYNAMIC\Accesos directos\Archivos de Info Costa Rica - CLIENTES\00_IA_PREVENTAS\Preventas\Catalogo\Catalogo de productos por proveedor.xlsx"),
    [Parameter(Mandatory = $true)][string]$Categoria,
    [Parameter(Mandatory = $true)][string]$Subcategoria,
    [switch]$Guardar
)
$ErrorActionPreference = "Stop"
if (-not (Test-Path -LiteralPath $Ruta)) { throw "no existe: $Ruta" }
if (-not (Get-Process OneDrive -ErrorAction SilentlyContinue)) { throw "OneDrive no esta corriendo: no escribo" }
$sh = New-Object -ComObject Shell.Application
$st = $sh.Namespace((Split-Path -Parent $Ruta)).ParseName((Split-Path -Leaf $Ruta)).ExtendedProperty("System.StorageProviderState")
if ($st -ne 2) { throw ("el catalogo no esta sincronizado (estado {0}): no escribo" -f $st) }
$bak = Join-Path $env:TEMP ("catalogo_antes_subcategoria_{0}.xlsx" -f (Get-Date -Format "yyyyMMdd_HHmmss"))
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
    $h = $wb.Worksheets.Item("Catalogo")
    $l = $wb.Worksheets.Item("_listas")
    $ultCat = $l.Cells.Item(1048576, 1).End(-4162).Row
    $ultSub = $l.Cells.Item(1048576, 5).End(-4162).Row
    $cats = @(for ($r = 2; $r -le $ultCat; $r++) { [string]$l.Cells.Item($r, 1).Value2 })
    if ($cats -notcontains $Categoria) { throw "la categoria [$Categoria] no esta en _listas!A" }
    for ($r = 2; $r -le $ultSub; $r++) {
        if ([string]$l.Cells.Item($r, 5).Value2 -eq $Subcategoria) { throw "[$Subcategoria] ya esta en _listas!E$r" }
    }
    $f = $ultSub + 1
    if ($l.Cells.Item($f, 3).Value2 -ne $null -or $l.Cells.Item($f, 5).Value2 -ne $null) { throw "_listas fila $f no esta vacia: no escribo" }
    $l.Cells.Item($f, 3).Value2 = "$Categoria > $Subcategoria"
    $l.Cells.Item($f, 5).Value2 = $Subcategoria
    Write-Output ("_listas fila {0}: C [{1}] | E [{2}]" -f $f, $l.Cells.Item($f, 3).Text, $l.Cells.Item($f, 5).Text)

    # la validacion de Subcategoria, hasta la nueva ultima fila de la lista (como reparar-desplegables.ps1)
    $ultFila = $h.Cells.Item(1048576, 1).End(-4162).Row
    $rng = $h.Range(("E2:E{0}" -f $ultFila))
    try { $rng.Validation.Delete() } catch { }
    $rng.Validation.Add(3, 1, 1, ("=_listas!`$E`$2:`$E`${0}" -f $f)) | Out-Null
    $rng.Validation.IgnoreBlank = $true
    $rng.Validation.InCellDropdown = $true
    $rng.Validation.ErrorTitle = "Subcategoria no valida"
    $rng.Validation.ErrorMessage = "Elegi una de la lista. Si hace falta una nueva, agregala primero en scripts/taxonomia.py y despues con agregar_subcategoria.ps1."
    $rng.Validation.ShowError = $true
    Write-Output ("validacion Catalogo!E2:E{0} = {1}" -f $ultFila, $h.Range("E2").Validation.Formula1)

    if ($Guardar) { $wb.Save(); Write-Output "GUARDADO: $Ruta" } else { Write-Output "prueba: no se guardo (falta -Guardar)" }
    $wb.Close($false)
}
finally {
    $excel.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($excel) | Out-Null
}
if ($Guardar) {
    & (Join-Path $PSScriptRoot "..\..\armar-cotizacion\scripts\verificar_onedrive.ps1") $Ruta
    exit $LASTEXITCODE
}
