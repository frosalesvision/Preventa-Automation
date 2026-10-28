# -*- coding: utf-8 -*-
r"""
Arma la tabla de montos de una matriz ya llenada (la vista previa que el
asesor acepta o rechaza antes de crear nada en CLIENTES, regla R25).

    python -I vista_previa_montos.py "<Matriz ... .xlsx>"

La matriz es el BORRADOR que dejo llenar_matriz.ps1 fuera de CLIENTES (en
%TEMP%\preventa-borrador). Lee los valores que Excel calculo y guardo; no
calcula nada por su cuenta. Solo lectura: nunca guarda (openpyxl borraria
las imagenes del machote).

Imprime en Markdown:
  1. Lo que ve el cliente: las lineas de COTIZACION con cantidad, el
     subtotal, el impuesto (con su tasa) y el total.
  2. El costo interno, que no ve el cliente: Equipos, OPEX GV y MATERIALES,
     con costo y venta por linea.
  3. Los controles: K74 igual al SUBTOTAL y celdas con error.
Los montos van como los ve preventa: $ 60.905,30.
"""
import sys
import warnings

import openpyxl

warnings.filterwarnings("ignore")

# como openpyxl lee los errores que Excel dejo guardados
ERRORES = {"#DIV/0!", "#VALUE!", "#REF!", "#NAME?", "#N/A", "#NUM!", "#NULL!"}


def plata(v):
    if not isinstance(v, (int, float)):
        return ""
    s = "{:,.2f}".format(v).replace(",", "_").replace(".", ",").replace("_", ".")
    return "$ " + s


def cant(v):
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    return "{:,}".format(v).replace(",", ".") if isinstance(v, int) else str(v)


def num(v):
    return v if isinstance(v, (int, float)) else 0


def texto(v):
    return str(v or "").strip()


def hoja(wb, nombre):
    for ws in wb.worksheets:
        if ws.title.strip() == nombre:
            return ws
    raise SystemExit("no encontre la pestana [%s]" % nombre)


def fila_total(ws, desde):
    # la fila de totales dice "Total FOB": columna D en OPEX GV y MATERIALES, E en Equipos
    for r in range(desde, desde + 60):
        if any(texto(ws.cell(r, c).value).startswith("Total") for c in (4, 5)):
            return r
    raise SystemExit("no encontre la fila de totales en [%s]" % ws.title)


def lineas(ws, col_desc, col_cant, col_costo, col_venta_u, col_venta_t, col_imp=None):
    fin = fila_total(ws, 6)
    out = []
    for r in range(6, fin):
        q = ws.cell(r, col_cant).value
        if isinstance(q, (int, float)) and q > 0:
            out.append({
                "desc": texto(ws.cell(r, col_desc).value),
                "imp": texto(ws.cell(r, col_imp).value) if col_imp else "",
                "cant": q,
                "costo": num(ws.cell(r, col_costo).value),
                "venta_u": num(ws.cell(r, col_venta_u).value),
                "venta_t": num(ws.cell(r, col_venta_t).value),
            })
    return out, fin


def tabla_interna(titulo, filas, con_importado):
    if not filas:
        return
    print("\n**%s**\n" % titulo)
    enc = "| Cant. | Descripción |" + (" Importado |" if con_importado else "") + " Costo unit. | Costo total | Precio unit. | Venta total |"
    print(enc)
    print("|" + "---|" * (enc.count("|") - 1))
    tc = tv = 0
    for f in filas:
        ct = f["costo"] * f["cant"]
        tc += ct
        tv += f["venta_t"]
        print("| %s | %s |%s %s | %s | %s | %s |" % (
            cant(f["cant"]), f["desc"], (" %s |" % f["imp"]) if con_importado else "",
            plata(f["costo"]), plata(ct), plata(f["venta_u"]), plata(f["venta_t"])))
    vacias = " |" if con_importado else ""
    print("| | **Total** |%s | **%s** | | **%s** |" % (vacias, plata(tc), plata(tv)))


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    wb = openpyxl.load_workbook(sys.argv[1], data_only=True)

    cot = hoja(wb, "COTIZACIÓN")
    sub = imp = tot = None
    primera = None
    for r in range(1, 130):
        if primera is None and texto(cot.cell(r, 2).value) == "Cantidad":
            primera = r + 1
        etiqueta = texto(cot.cell(r, 9).value).upper()
        if etiqueta == "SUBTOTAL" and sub is None:
            sub = r
        elif etiqueta == "IMPUESTO" and imp is None:
            imp = r
        elif etiqueta == "TOTAL" and tot is None:
            tot = r
    if None in (primera, sub, imp, tot):
        raise SystemExit("no encontre Cantidad / SUBTOTAL / IMPUESTO / TOTAL en COTIZACION")
    if cot.cell(sub, 10).value is None:
        raise SystemExit("la matriz no tiene valores calculados: guardarla con Excel (llenar_matriz.ps1) antes")

    print("### Lo que ve el cliente\n")
    print("| Cant. | Descripción | Precio unit. | Total |")
    print("|---|---|---|---|")
    for r in range(primera, sub):
        q = cot.cell(r, 2).value
        if isinstance(q, (int, float)) and q > 0:
            print("| %s | %s | %s | %s |" % (cant(q), texto(cot.cell(r, 3).value),
                                           plata(cot.cell(r, 9).value), plata(cot.cell(r, 10).value)))
    vs, vi, vt = num(cot.cell(sub, 10).value), num(cot.cell(imp, 10).value), num(cot.cell(tot, 10).value)
    tasa = (vi / vs * 100) if vs else 0
    print("| | **SUBTOTAL** | | **%s** |" % plata(vs))
    print("| | IMPUESTO (%s%%) | | %s |" % (("%.2f" % tasa).rstrip("0").rstrip(".").replace(".", ","), plata(vi)))
    print("| | **TOTAL** | | **%s** |" % plata(vt))

    print("\n### Costo interno (no lo ve el cliente)")
    eq, fin_eq = lineas(hoja(wb, "Equipos"), 2, 4, 5, 15, 16, col_imp=3)
    tabla_interna("Equipos", eq, True)
    ox, _ = lineas(hoja(wb, "OPEX GV"), 1, 3, 4, 14, 15)
    tabla_interna("OPEX GV (mano de obra y lo que preventa puso ahí)", ox, False)
    mt, _ = lineas(hoja(wb, "MATERIALES"), 1, 3, 4, 14, 15, col_imp=2)
    tabla_interna("MATERIALES", mt, True)
    utilidad = hoja(wb, "Equipos").cell(fin_eq + 1, 16).value
    if isinstance(utilidad, (int, float)):
        print("\nUtilidad de Equipos (P%d): %s" % (fin_eq + 1, plata(utilidad)))

    print("\n### Controles\n")
    k = num(cot.cell(sub, 11).value)
    ok = abs(k - vs) < 0.01
    print("- K%d (Equipos + OPEX GV + MATERIALES) = %s: %s" % (sub, plata(k), "igual al SUBTOTAL" if ok else "NO CUADRA con el SUBTOTAL"))
    errores = []
    for ws in wb.worksheets:
        if ws.sheet_state != "visible":
            continue
        for fila in ws.iter_rows():
            for c in fila:
                if isinstance(c.value, str) and c.value in ERRORES:
                    errores.append("%s!%s" % (ws.title.strip(), c.coordinate))
    print("- Celdas con error en pestañas visibles: %d%s" % (len(errores), (" (" + ", ".join(errores[:10]) + ")") if errores else ""))
    if not ok or errores:
        sys.exit(1)


if __name__ == "__main__":
    main()
