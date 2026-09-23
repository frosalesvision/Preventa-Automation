# Vuelve a poner los desplegables de Categoria y Subcategoria del catalogo.
#
# Hay que correr esto DESPUES de cualquier script que escriba el catalogo
# con openpyxl -- en particular generar_matriz_accesorios.py. openpyxl no
# soporta la extension x14 que usa la validacion con rango en otra hoja, asi
# que al guardar la borra **sin avisar**: el archivo queda sano, los datos
# intactos, y los desplegables simplemente dejan de existir.
#
# Medido el 2026-09-23: correr el generador de la matriz de accesorios dejo
# las dos validaciones en cero.
#
# Uso:  powershell -File scripts/reparar-desplegables.ps1

$ErrorActionPreference = "Stop"
$cat = Join-Path $env:USERPROFILE "OneDrive - GRUPO VISION - DYNAMIC\Accesos directos\Archivos de Info Costa Rica - CLIENTES\00_IA_PREVENTAS\Preventas\Catalogo\Catalogo de productos por proveedor.xlsx"
if (-not (Test-Path $cat)) { throw "No se encontro el catalogo en: $cat" }

$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false
try {
    $wb = $excel.Workbooks.Open($cat)
    $h  = $wb.Worksheets.Item("Catalogo")
    $l  = $wb.Worksheets.Item("_listas")

    # ultima fila de cada lista, para no dejar el rango corto si crecen
    $ultCat = $l.Cells.Item(1048576, 1).End(-4162).Row
    $ultSub = $l.Cells.Item(1048576, 5).End(-4162).Row
    $ultFila = $h.Cells.Item(1048576, 1).End(-4162).Row
    Write-Output ("categorias en _listas!A2:A{0}    subcategorias en _listas!E2:E{1}" -f $ultCat, $ultSub)
    Write-Output ("filas de catalogo: {0}" -f $ultFila)

    $defs = @(
        @{ Col = "D"; Rango = ("=_listas!`$A`$2:`$A`${0}" -f $ultCat)
           Titulo = "Categoria no valida"
           Msg = "Elegi una de la lista. Son las 16 categorias de la taxonomia mas 'Sin clasificar'." },
        @{ Col = "E"; Rango = ("=_listas!`$E`$2:`$E`${0}" -f $ultSub)
           Titulo = "Subcategoria no valida"
           Msg = "Elegi una de la lista. Si hace falta una nueva, agregala primero en scripts/taxonomia.py y regenera esta lista: si no, buscar-equipo no la va a encontrar." }
    )
    foreach ($d in $defs) {
        $rng = $h.Range(("{0}2:{0}{1}" -f $d.Col, $ultFila))
        try { $rng.Validation.Delete() } catch { }
        $rng.Validation.Add(3, 1, 1, $d.Rango) | Out-Null   # 3=xlValidateList, 1=xlValidAlertStop
        $rng.Validation.IgnoreBlank    = $true
        $rng.Validation.InCellDropdown = $true
        $rng.Validation.ErrorTitle     = $d.Titulo
        $rng.Validation.ErrorMessage   = $d.Msg
        $rng.Validation.ShowError      = $true
        Write-Output ("  columna {0} -> {1}" -f $d.Col, $d.Rango)
    }

    # verificacion: que ningun valor del catalogo quede fuera de su lista
    Write-Output ""
    Write-Output "--- verificacion ---"
    foreach ($par in @(@("D", 1), @("E", 5))) {
        $col = $par[0]; $colLista = $par[1]
        $validos = @{}
        $ult = $l.Cells.Item(1048576, $colLista).End(-4162).Row
        for ($r = 2; $r -le $ult; $r++) {
            $v = [string]$l.Cells.Item($r, $colLista).Value2
            if ($v) { $validos[$v] = $true }
        }
        $fuera = 0
        $vals = $h.Range(("{0}2:{0}{1}" -f $col, $ultFila)).Value2
        for ($i = 1; $i -le $ultFila - 1; $i++) {
            $x = [string]$vals[$i, 1]
            if ($x -and -not $validos.ContainsKey($x)) { $fuera++ }
        }
        Write-Output ("  columna {0}: {1} filas con un valor fuera de la lista" -f $col, $fuera)
    }
    Write-Output ("  D2 = {0}" -f $h.Range("D2").Validation.Formula1)
    Write-Output ("  E2 = {0}" -f $h.Range("E2").Validation.Formula1)

    $wb.Save()
    $wb.Close($false)
    Write-Output "GUARDADO"
}
finally {
    $excel.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($excel) | Out-Null
    [GC]::Collect(); [GC]::WaitForPendingFinalizers()
}
