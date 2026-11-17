# -*- coding: utf-8 -*-
"""
Busca en el catalogo (solo lectura) y muestra una linea por candidato, con
los dos precios, los dias del precio y las existencias del portal si las hay.

    python -I buscar_catalogo.py "12v" "9ah" [--sub Bateria] [--prov Tectel] [--max 40]
    python -I buscar_catalogo.py "4 ?x ?5 ?mp|20 ?mp" --regex --cat Camara --por-marca 3 --detalle 150

Todas las palabras tienen que estar en el nombre, el codigo o la descripcion
(sin acentos ni mayusculas). --sub y --cat filtran por subcategoria o
categoria; --prov por proveedor; --marca por marca. Sirve para el Paso 1 de
buscar-equipo y para la regla R21 (ver si el catalogo tiene el producto y que
tan viejo es su precio antes de buscar en tiendas).

Para el modo pliego (R30), donde hay que mirar todas las marcas:
  --regex        cada palabra es una expresion regular; asi una busqueda cubre
                 "4x5 MP", "20MP" y las otras formas de escribir lo mismo.
  --por-marca N  cuenta los candidatos por marca y muestra los N mas baratos de
                 cada una. Sin esto, las marcas de entrada tapan a las demas.
  --detalle N    agrega los primeros N caracteres de la descripcion. En marcas
                 como Axis el nombre no dice las especificaciones.
"""
import argparse
import collections
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


def sin_acentos(s):
    s = unicodedata.normalize("NFKD", str(s or ""))
    return "".join(c for c in s if not unicodedata.combining(c))


def norm(s):
    return sin_acentos(s).lower()


def marca_de(r):
    """Clave para agrupar: 'AVIGILON' y 'Avigilon' son la misma marca."""
    return str(r[1]).strip().upper() if r[1] else "(SIN MARCA)"


def precio(r):
    return r[8] if isinstance(r[8], (int, float)) else 9e9


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("palabras", nargs="+")
    ap.add_argument("--cat")
    ap.add_argument("--sub")
    ap.add_argument("--prov")
    ap.add_argument("--marca")
    ap.add_argument("--regex", action="store_true")
    ap.add_argument("--por-marca", type=int, metavar="N")
    ap.add_argument("--detalle", type=int, default=0, metavar="N")
    ap.add_argument("--max", type=int, default=40)
    ap.add_argument("--ruta", default=RUTA)
    a = ap.parse_args()
    hoy = datetime.datetime.now()
    if a.regex:
        pruebas = [re.compile(sin_acentos(p), re.I).search for p in a.palabras]
    else:
        pruebas = [(lambda t, p=norm(p): p in t) for p in a.palabras]
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
        if a.marca and norm(a.marca) not in norm(r[1]):
            continue
        texto = norm(" ".join(str(x) for x in (r[0], r[2], r[15]) if x))
        if all(p(texto) for p in pruebas):
            hallados.append(r)
    print("%d candidatos" % len(hallados))
    elegidos = sorted(hallados, key=precio)
    if a.por_marca:
        cuenta = collections.Counter(marca_de(r) for r in hallados)
        print("Por marca: " + ", ".join("%s %d" % kv for kv in cuenta.most_common()))
        vistos = collections.Counter()
        tope = []
        for r in elegidos:
            vistos[marca_de(r)] += 1
            if vistos[marca_de(r)] <= a.por_marca:
                tope.append(r)
        elegidos = sorted(tope, key=marca_de)
    for r in elegidos[:a.max]:
        dias = (hoy - r[17]).days if isinstance(r[17], datetime.datetime) else None
        exist = re.search(r"Existencias el [0-9-]+: ([^|]{0,60})", str(r[15] or ""))
        linea = "%-16s | %-12s | %-14s | compra %8s | lista %8s | %4s dias | %s | %s" % (
            str(r[2])[:16], str(r[1] or "(sin marca)")[:12], str(r[5])[:14], r[8], r[6],
            dias if dias is not None else "?", str(r[0])[:60], exist.group(1).strip() if exist else "")
        if a.detalle:
            linea += " | " + str(r[15] or "")[:a.detalle].replace("\n", " ")
        print(linea)
    if len(elegidos) > a.max:
        print("... y %d mas: acotar con mas palabras, --sub o --prov" % (len(elegidos) - a.max))
    elif a.por_marca and len(hallados) > len(elegidos):
        print("... y %d mas de esas marcas: subir --por-marca o acotar" % (len(hallados) - len(elegidos)))


if __name__ == "__main__":
    main()
