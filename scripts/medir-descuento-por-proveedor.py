# -*- coding: utf-8 -*-
"""Que descuento sobre el precio cargado se usa de verdad, proveedor por proveedor.

Existe por lo que aparecio el 2026-09-28 al abrir la lista de precios de
Hanwha: trae UN solo precio, el MSRP, y una columna que calcula el precio
propio con la formula `MSRP - descuento x MSRP`, donde el descuento lo
escribe cada distribuidor. O sea que el precio de compra de Hanwha no esta
en ningun archivo: sale de aplicarle al MSRP el porcentaje que Hanwha le da
a Grupo Vision.

En vez de preguntar ese porcentaje a ciegas, se mide. Por cada producto del
catalogo que tiene un solo precio cargado, se busca en las cotizaciones
reales cuanto se uso como costo, y se divide por ese precio:

    cerca de 1,00  -> el precio cargado ES lo que se paga (un costo)
    0,60 a 0,85    -> el precio cargado es de lista, y el cociente dice el
                      descuento (0,68 = 32% de descuento)

Solo cuentan las coincidencias EXACTAS de modelo: una por prefijo puede ser
otra variante, con otro precio. Y cada producto se cuenta una vez por
proyecto, aunque la cotizacion tenga varias versiones.

Limite honesto: el precio del catalogo es el de la lista actual y las
cotizaciones son de 2025 y 2026. Si el proveedor subio precios, el cociente
de las cotizaciones viejas sale mas bajo. Por eso se reporta tambien por ano.

Solo lee.

Uso:
    python scripts/medir-descuento-por-proveedor.py
"""

import collections
import importlib.util
import os
import re
import statistics
import sys
import warnings

warnings.filterwarnings("ignore")

try:
    import openpyxl
except ImportError:
    sys.exit("Falta openpyxl.  Instalalo con:  pip install openpyxl")

AQUI = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("lb", os.path.join(AQUI, "casos-patron-linea-base.py"))
lb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lb)

RX_CARPETA = re.compile(r"cotizaci.n\s*#?\s*\d+\s*-\s*(\d{4})", re.I)


def leer_catalogo():
    """Solo las filas con UN precio (sin precio de compra): son las que hay que interpretar."""
    wb = openpyxl.load_workbook(lb.mm.CATALOGO, read_only=True, data_only=True)
    filas = list(wb["Catalogo"].iter_rows(min_row=2, values_only=True))
    wb.close()
    idx, cubos = {}, collections.defaultdict(list)
    for r in filas:
        k = lb.mm.clave(r[2])
        if not k or not lb.es_modelo(str(r[2])) or k in idx:
            continue
        tiene_compra = len(r) > 8 and isinstance(r[8], (int, float))
        lista = r[6] if isinstance(r[6], (int, float)) else None
        if tiene_compra or not lista:
            idx[k] = None          # se indexa para no confundir, pero no se mide
        else:
            idx[k] = (float(lista), str(r[5] or ""))
        if len(k) >= 6:
            cubos[k[:5]].append(k)
    return idx, cubos


def main():
    idx, cubos = leer_catalogo()
    print("productos con un solo precio cargado: %d" % sum(1 for v in idx.values() if v))

    archivos = []
    for root, dirs, files in os.walk(lb.mm.CLIENTES):
        if "00_IA_PREVENTAS" in root:
            continue
        for f in files:
            if f.startswith("~$") or not f.lower().endswith((".xlsx", ".xlsm")):
                continue
            if not re.search(r"matriz|oferta", f, re.I):
                continue
            p = os.path.join(root, f)
            try:
                if os.path.getsize(p) < 40000:
                    continue
            except OSError:
                continue
            archivos.append(p)
    print("matrices: %d" % len(archivos))

    visto = set()
    por_prov = collections.defaultdict(list)
    por_anio = collections.defaultdict(lambda: collections.defaultdict(list))
    for i, p in enumerate(archivos, start=1):
        if i % 150 == 0:
            print("    %d/%d   coincidencias: %d" % (i, len(archivos), len(visto)))
        carpeta, anio = os.path.dirname(p), None
        d = carpeta
        while d and len(d) > len(lb.mm.CLIENTES):
            m = RX_CARPETA.search(os.path.basename(d))
            if m:
                carpeta, anio = d, m.group(1)
                break
            d = os.path.dirname(d)
        v = lb.leer_version(p)
        if not v:
            continue
        for texto, costo, qty in v["lineas"]:
            modo, k = lb.buscar(texto, idx, cubos)
            if modo != "exacto" or not idx.get(k):
                continue
            if (carpeta, k) in visto:
                continue
            visto.add((carpeta, k))
            lista, prov = idx[k]
            r = costo / lista
            if 0.05 < r < 3:          # fuera de eso es otra cosa (un kit, una unidad distinta)
                por_prov[prov].append(r)
                if anio:
                    por_anio[prov][anio].append(r)

    print()
    print("=" * 78)
    print(" COSTO USADO EN LAS COTIZACIONES / PRECIO CARGADO EN EL CATALOGO")
    print("=" * 78)
    print("%-26s %5s %8s %8s %8s %9s %9s" % ("proveedor", "n", "mediana", "cuart1", "cuart3", "~1,00", "0,5-0,85"))
    print("-" * 78)
    for prov, rs in sorted(por_prov.items(), key=lambda x: -len(x[1])):
        if len(rs) < 3:
            continue
        rs = sorted(rs)
        q1, q3 = rs[len(rs) // 4], rs[(3 * len(rs)) // 4]
        uno = sum(1 for x in rs if abs(x - 1) <= 0.05)
        lista = sum(1 for x in rs if 0.5 <= x <= 0.85)
        print("%-26s %5d %8.2f %8.2f %8.2f %8d%% %8d%%" % (
            prov[:26], len(rs), statistics.median(rs), q1, q3,
            100 * uno // len(rs), 100 * lista // len(rs)))
    print()
    for prov in sorted(por_anio, key=lambda x: -len(por_prov[x])):
        if len(por_prov[prov]) < 10:
            continue
        print("  %s, por ano:" % prov)
        for anio in sorted(por_anio[prov]):
            rs = por_anio[prov][anio]
            print("     %s   n=%-4d mediana %.2f" % (anio, len(rs), statistics.median(rs)))
        rs = por_prov[prov]
        cubetas = collections.Counter(min(19, int(x / 0.05)) for x in rs)
        print("     reparto (cada # es un producto-proyecto):")
        for b in range(8, 22):
            if cubetas.get(b):
                print("       %.2f-%.2f  %s" % (b * 0.05, b * 0.05 + 0.05, "#" * min(60, cubetas[b])))
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
