r"""IVA dentro del precio unitario (regla R29): agrega al JSON de llenar_matriz.ps1 las celdas que hacen
que el IVA (13% por defecto) se cobre en el precio unitario de Equipos y OPEX GV, y no en el costo
nacionalizado. Es para el cliente exento al que preventa le quiere cobrar el IVA dentro de cada linea:
la cotizacion queda exenta (Datos del proyecto B15 = si).

  python -I iva_en_precio.py "<datos.json>" [--iva 0.13]

Reescribe el JSON en el mismo lugar. Lo que cambia, en todas las lineas (Equipos 6-55, OPEX GV 6-15):
  Equipos   I = (K+L+N) * $I$4   el IVA es el % del precio sin IVA
            J = DAI sin el IVA   K = costo nacionalizado sin el IVA   O = N+K+L+I
  OPEX GV   H = (J+K+M) * $H$4   I = DAI sin el IVA   J = costo sin el IVA   N = M+J+K+H
Asi el IVA no lleva utilidad, administracion ni DAI. La fila UTILIDAD de cada hoja lo cuenta como
ganancia: vista_previa_montos.py muestra aparte el IVA y la utilidad real.
MATERIALES no cambia: si la cotizacion tiene materiales ahi, se avisa.
"""
import argparse, json, sys


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("datos")
    ap.add_argument("--iva", type=float, default=0.13)
    a = ap.parse_args()
    d = json.load(open(a.datos, encoding="utf-8"))

    nuevas = []
    def poner(hoja, celda, valor, rf=False):
        x = {"hoja": hoja, "celda": celda, "valor": valor}
        if rf:
            x["reemplaza_formula"] = True
        nuevas.append(x)

    poner("Equipos", "I4", a.iva)
    poner("OPEX GV", "H4", a.iva)
    for f in range(6, 56):
        poner("Equipos", "I%d" % f, "=(K{0}+L{0}+N{0})*$I$4".format(f), True)
        poner("Equipos", "J%d" % f, '=IF(C{0}="si",(E{0}+G{0}+H{0})*$J$4,0)'.format(f), True)
        poner("Equipos", "K%d" % f, "=E{0}+G{0}+H{0}+J{0}".format(f), True)
        poner("Equipos", "O%d" % f, "=N{0}+K{0}+L{0}+I{0}".format(f), True)
    for f in range(6, 16):
        poner("OPEX GV", "H%d" % f, "=(J{0}+K{0}+M{0})*$H$4".format(f), True)
        poner("OPEX GV", "I%d" % f, '=IF(B{0}="si",(D{0}+F{0}+G{0})*$I$4,0)'.format(f), True)
        poner("OPEX GV", "J%d" % f, "=D{0}+F{0}+G{0}+I{0}".format(f), True)
        poner("OPEX GV", "N%d" % f, "=M{0}+J{0}+K{0}+H{0}".format(f), True)
    # el IVA ya va en las lineas: la cotizacion no lo cobra otra vez
    poner("Datos del proyecto", "B15", "si")
    poner("Datos del proyecto", "B16", 0)

    pisadas = {(x["hoja"], x["celda"]) for x in nuevas}
    antes = d.get("celdas", [])
    for x in antes:
        k = (x["hoja"], x["celda"])
        if k in {("Datos del proyecto", "B15"), ("Datos del proyecto", "B16"), ("Equipos", "I4"), ("OPEX GV", "H4")} and x["valor"] not in ("si", 0, a.iva):
            print("AVISO: %s!%s decia %r y queda %r" % (k[0], k[1], x["valor"], next(n["valor"] for n in nuevas if (n["hoja"], n["celda"]) == k)))
    if any(x["hoja"] == "MATERIALES" and x["celda"].startswith("C") and x["valor"] not in (0, None) for x in antes):
        print("AVISO: hay lineas en MATERIALES y ahi el IVA sigue en el costo (H4 13%, con margen encima): decirselo al asesor")
    d["celdas"] = [x for x in antes if (x["hoja"], x["celda"]) not in pisadas] + nuevas
    json.dump(d, open(a.datos, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("IVA %.0f%% en el precio unitario de Equipos y OPEX GV; cotizacion exenta. %d celdas en %s" % (a.iva * 100, len(nuevas), a.datos))


main()
