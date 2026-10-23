# Ajusta lo que se ve en una matriz ya llenada (pedido de Fabian, 2026-10-19).
# No borra ni cambia nada: solo oculta y muestra filas y pestanas.
#
#   powershell -File ajustar_vista.ps1 -Ruta "<Matriz Cliente fecha.xlsx>"
#
#   - Equipos: se ven las lineas usadas mas 3 libres, para agregar algo a mano;
#     las demas (hasta la 55) se ocultan.
#   - COTIZACION y COTIZACION (Financ), que espejan esas lineas (fila de
#     Equipos + 16): SOLO las usadas, sin renglones en blanco. Si se agrega
#     una linea a mano en Equipos, hay que mostrar su fila aca (o correr este
#     script de nuevo); si no, el aviso rojo de L74 lo avisa.
#   - Si la ficha dice que NO lleva financiamiento (Datos del proyecto B42 =
#     "no"), se ocultan Financiamiento, PTMO y COTIZACION (Financ). Si dice
#     "si", se muestran. Vacio: no se tocan.
# Lo llama llenar_matriz.ps1 al final; tambien se puede correr solo.
param(
    [Parameter(Mandatory = $true)][string]$Ruta,
    [int]$Libres = 3
)
$ErrorActionPreference = "Stop"
$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false; $excel.DisplayAlerts = $false
try {
    $wb = $excel.Workbooks.Open($Ruta)
    if ($wb.ReadOnly) { throw "el archivo esta abierto por alguien (solo lectura): no sigo" }
    $auto = $null; try { $auto = $wb.AutoSaveOn } catch { }
    if ($auto -eq $true) { [void][System.__ComObject].InvokeMember("AutoSaveOn", [System.Reflection.BindingFlags]::SetProperty, $null, $wb, @($false)) }
    $hojas = @{}; foreach ($w in $wb.Worksheets) { $hojas[$w.Name] = $w }
    $eq = $hojas["Equipos"]
    $ultima = 5
    for ($r = 6; $r -le 55; $r++) {
        $b = [string]$eq.Cells.Item($r, 2).Value2; $d = $eq.Cells.Item($r, 4).Value2; $e = $eq.Cells.Item($r, 5).Value2
        if ($b.Trim() -ne "" -or ($d -is [double] -and $d -ne 0) -or ($e -is [double] -and $e -ne 0)) { $ultima = $r }
    }
    $hasta = [math]::Min(55, $ultima + $Libres)
    $eq.Range("A6:A55").EntireRow.Hidden = $false
    if ($hasta -lt 55) { $eq.Range(("A{0}:A55" -f ($hasta + 1))).EntireRow.Hidden = $true }
    # En lo que ve el cliente, solo las lineas usadas: ni un renglon en blanco
    # (preventa, 2026-10-19). Si alguien llena una linea libre de Equipos y no
    # muestra su fila aca, el aviso de L74 lo dice (mejorar_diseno_matriz.ps1).
    foreach ($n in @($hojas.Keys | Where-Object { $_ -like "COTIZACI*" })) {
        $h = $hojas[$n]
        $h.Range("A22:A71").EntireRow.Hidden = $false
        if ($ultima -lt 55) { $h.Range(("A{0}:A71" -f ($ultima + 17))).EntireRow.Hidden = $true }
    }
    Write-Output ("lineas usadas: {0}; Equipos muestra filas 6 a {1}; las cotizaciones, solo las usadas (22 a {2})" -f ($ultima - 5), $hasta, ($ultima + 16))
    # La linea de OPEX (fila 72 de COTIZACION) solo se ve si hay mano de obra o materiales.
    $opex = $hojas["OPEX GV"].Range("O17").Value2
    foreach ($n in @($hojas.Keys | Where-Object { $_ -like "COTIZACI*N " })) {
        $h = $hojas[$n]
        if (([string]$h.Range("I72").Formula) -like "*OPEX GV*") {
            $h.Rows.Item(72).Hidden = -not ($opex -is [double] -and $opex -gt 0)
            Write-Output ("linea de OPEX: {0}" -f $(if ($h.Rows.Item(72).Hidden) { "oculta (OPEX en cero)" } else { "visible (OPEX {0:N2})" -f $opex }))
        }
    }

    $fin = ([string]$hojas["Datos del proyecto"].Range("B42").Value2).Trim().ToLower()
    $tabs = @("Financiamiento", "PTMO") + @($hojas.Keys | Where-Object { $_ -like "COTIZACION (Financ)*" })
    if ($fin -eq "no" -or $fin -eq "si") {
        $vis = $(if ($fin -eq "si") { -1 } else { 0 })
        $hojas["Equipos"].Activate()
        foreach ($t in $tabs) { if ($hojas.ContainsKey($t)) { $hojas[$t].Visible = $vis } }
        Write-Output ("financiamiento '{0}': pestanas {1} {2}" -f $fin, ($tabs -join ", "), $(if ($vis -eq -1) { "visibles" } else { "ocultas" }))
    } else { Write-Output "financiamiento sin responder en la ficha: pestanas sin tocar" }
    foreach ($n in @($hojas.Keys | Where-Object { $_ -like "COTIZACI*N " })) { $hojas[$n].Activate(); [void]$hojas[$n].Range("A1").Select() }
    $wb.Save()
    $wb.Close($false)
    Write-Output "GUARDADO"
}
finally {
    $excel.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($excel) | Out-Null
    [GC]::Collect(); [GC]::WaitForPendingFinalizers()
}
