# -*- coding: utf-8 -*-
"""
Busca en el catalogo (solo lectura) y muestra una linea por candidato, con
los dos precios, los dias del precio y las existencias del portal si las hay.

    python -I buscar_catalogo.py "12v" "9ah" [--sub Bateria] [--prov Tectel] [--max 40]

Todas las palabras tienen que estar en el nombre, el codigo o la descripcion
(sin acentos ni mayusculas). --sub y --cat filtran por subcategoria o
categoria; --prov por proveedor. Sirve para el Paso 1 de buscar-equipo y
para la regla R21 (ver si el catalogo tiene el producto y que tan viejo es
su precio antes de buscar en tiendas).
"""
import argparse
import datetime
import os
import re
import sys
import unicodedata

import openpyxl

RUTA = os.path.expandvars(
    r"%USERPROFILE%\OneDrive - GRUPO VISION - DYNAMIC\Accesos directos"
    r"\Archivos de Info Costa Rica - CLIENTES\00_IA_PREVENTAS\Preventas"
    r"\Catalogo\Catalogo de productos por proveedor.xlsx"
)


def norm(s):
    s = unicodedata.normalize("NFKD", str(s or ""))
    return "".join(c for c in s if not unicodedata.combining(c)).lower()


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("palabras", nargs="+")
    ap.add_argument("--cat")
    ap.add_argument("--sub")
    ap.add_argument("--prov")
    ap.add_argument("--max", type=int, default=40)
    ap.add_argument("--ruta", default=RUTA)
    a = ap.parse_args()
    hoy = datetime.datetime.now()
    pal = [norm(p) for p in a.palabras]
    wb = openpyxl.load_workbook(a.ruta, read_only=True, data_only=True)
    hallados = []
    for r in wb["Catalogo"].iter_rows(min_row=2, values_only=True):
        if not r or not r[0]:
            continue
        if a.cat and norm(a.cat) not in norm(r[3]):
            continue
        if a.sub and norm(a.sub) not in norm(r[4]):
            continue
        if a.prov and norm(a.prov) not in norm(r[5]):
            continue
        texto = norm(" ".join(str(x) for x in (r[0], r[2], r[15]) if x))
        if all(p in texto for p in pal):
            hallados.append(r)
    print("%d candidatos" % len(hallados))
    for r in sorted(hallados, key=lambda r: (r[8] if isinstance(r[8], (int, float)) else 9e9))[:a.max]:
        dias = (hoy - r[17]).days if isinstance(r[17], datetime.datetime) else None
        exist = re.search(r"Existencias el [0-9-]+: ([^|]{0,60})", str(r[15] or ""))
        print("%-16s | %-12s | %-14s | compra %8s | lista %8s | %4s dias | %s | %s" % (
            str(r[2])[:16], str(r[1] or "")[:12], str(r[5])[:14], r[8], r[6],
            dias if dias is not None else "?", str(r[0])[:60], exist.group(1).strip() if exist else ""))
    if len(hallados) > a.max:
        print("... y %d mas: acotar con mas palabras, --sub o --prov" % (len(hallados) - a.max))


if __name__ == "__main__":
    main()
