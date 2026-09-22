# -*- coding: utf-8 -*-
"""Revisa que el catalogo de productos este sano antes de darlo por bueno.

Existe por H-11 (2026-09-22): 29 de las 40 filas de una subcategoria no
pertenecian ahi, y nadie se dio cuenta durante semanas porque Excel no tiene
forma de avisarlo. Una fila con la subcategoria equivocada no desaparece
--sigue en el catalogo-- pero `buscar-equipo` filtra por categoria y
subcategoria, asi que deja de aparecer en las busquedas. El producto se
vuelve invisible sin que nada falle.

Correrlo DESPUES de cada carga de proveedor y DESPUES de cualquier edicion
manual del catalogo.

Uso:
    python scripts/verificar-catalogo.py
    python scripts/verificar-catalogo.py "ruta\\a\\otro\\catalogo.xlsx"

Solo lee: nunca escribe en el catalogo.
Devuelve 0 si todo esta bien, 1 si hay algo que revisar.
"""

import collections
import os
import sys
import warnings

warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import taxonomia  # noqa: E402

try:
    import openpyxl
except ImportError:
    sys.exit("Falta openpyxl.  Instalalo con:  pip install openpyxl")


RUTA_POR_DEFECTO = os.path.expandvars(
    r"%USERPROFILE%\OneDrive - GRUPO VISION - DYNAMIC\Accesos directos"
    r"\Archivos de Info Costa Rica - CLIENTES\00_IA_PREVENTAS\Preventas"
    r"\Catalogo\Catalogo de productos por proveedor.xlsx"
)

# Columnas, base 0, segun el orden fijo documentado en actualizar-catalogo
COL_NOMBRE, COL_MARCA, COL_SKU = 0, 1, 2
COL_CATEGORIA, COL_SUBCATEGORIA, COL_PROVEEDOR = 3, 4, 5
COL_PRECIO = 6


def cargar(ruta):
    wb = openpyxl.load_workbook(ruta, read_only=True, data_only=True)
    if "Catalogo" not in wb.sheetnames:
        sys.exit("El archivo no tiene una pestana 'Catalogo'.")
    filas = list(wb["Catalogo"].iter_rows(min_row=2, values_only=True))
    wb.close()
    return filas


def main():
    ruta = sys.argv[1] if len(sys.argv) > 1 else RUTA_POR_DEFECTO
    if not os.path.exists(ruta):
        sys.exit("No se encontro el catalogo en:\n  %s" % ruta)

    filas = cargar(ruta)
    validas = {cat: set(subs) for cat, subs in taxonomia.TAXONOMIA}

    print("=" * 66)
    print(" REVISION DEL CATALOGO")
    print("=" * 66)
    print("archivo: %s" % os.path.basename(ruta))
    print("filas:   %d" % len(filas))
    print()

    problemas = 0

    # --- 1. La categoria existe ---
    malas_cat = collections.Counter()
    for r in filas:
        if r[COL_CATEGORIA] not in validas:
            malas_cat[r[COL_CATEGORIA]] += 1
    print("--- 1. Categorias que no existen en la taxonomia ---")
    if malas_cat:
        for k, v in malas_cat.most_common():
            print("    %-40s %d filas" % (repr(k), v))
        problemas += sum(malas_cat.values())
    else:
        usadas = len(set(r[COL_CATEGORIA] for r in filas))
        print("    OK: las %d categorias en uso estan entre las %d de la taxonomia"
              % (usadas, len(validas)))
    print()

    # --- 2. La subcategoria corresponde a ESA categoria ---
    # Es el chequeo que importa: un desplegable plano deja poner "Montaje"
    # en una fila de camara, y eso se ve valido pero sigue estando mal.
    malos_pares = collections.Counter()
    for r in filas:
        cat, sub = r[COL_CATEGORIA], r[COL_SUBCATEGORIA]
        if cat in validas and sub not in validas[cat]:
            malos_pares[(cat, sub)] += 1
    print("--- 2. Subcategorias que no pertenecen a su categoria ---")
    if malos_pares:
        for (cat, sub), v in malos_pares.most_common():
            print("    %-30s + %-28s %d filas" % (cat, repr(sub), v))
        problemas += sum(malos_pares.values())
    else:
        print("    OK: todos los pares categoria/subcategoria son validos")
    print()

    # --- 3. Lo que el clasificador diria hoy ---
    # No es un error por si mismo: puede haber filas corregidas a mano a
    # proposito. Pero una diferencia grande avisa que el clasificador quedo
    # viejo, o que alguien reclasifico sin dejar constancia.
    difiere = []
    for i, r in enumerate(filas, 2):
        try:
            cat, sub, _ = taxonomia.clasificar(r[COL_NOMBRE], r[-1])
        except Exception:
            continue
        if (cat, sub) != (r[COL_CATEGORIA], r[COL_SUBCATEGORIA]):
            difiere.append((i, r[COL_SKU], r[COL_CATEGORIA], r[COL_SUBCATEGORIA], cat, sub))
    print("--- 3. Filas donde el clasificador diria otra cosa ---")
    if difiere:
        print("    %d filas (no es error: puede ser correccion manual a proposito)" % len(difiere))
        for i, sku, c1, s1, c2, s2 in difiere[:10]:
            print("      fila %-5d %-22s %s / %s  ->  %s / %s"
                  % (i, str(sku)[:22], c1, s1, c2, s2))
        if len(difiere) > 10:
            print("      ... y %d mas" % (len(difiere) - 10))
    else:
        print("    OK: el catalogo coincide con lo que dice el clasificador")
    print()

    # --- 4. Campos sin los que la fila no sirve para cotizar ---
    # Un SKU vacio NO es error en materiales genericos ni en servicios:
    # nadie le pone numero de parte a "tubo metal 3/4" ni a "instalacion de
    # poste". Si lo es en cualquier categoria de equipo.
    SIN_SKU_OK = {"Materiales de instalacion", "Servicios"}
    sin_sku_ok = sum(1 for r in filas
                     if not r[COL_SKU] and r[COL_CATEGORIA] in SIN_SKU_OK)
    sin_sku = sum(1 for r in filas
                  if not r[COL_SKU] and r[COL_CATEGORIA] not in SIN_SKU_OK)
    sin_precio = sum(1 for r in filas if not isinstance(r[COL_PRECIO], (int, float)))
    sin_marca = sum(1 for r in filas if not r[COL_MARCA])
    sin_prov = sum(1 for r in filas if not r[COL_PROVEEDOR])
    print("--- 4. Campos vacios que impiden cotizar esa fila ---")
    for etiqueta, n, grave in (("sin Modelo / SKU (equipo)", sin_sku, True),
                               ("sin Precio USD", sin_precio, True),
                               ("sin Proveedor", sin_prov, True),
                               ("sin Marca", sin_marca, False),
                               ("sin SKU, material o servicio", sin_sku_ok, False)):
        marca = "FALTA" if (n and grave) else ("aviso" if n else "OK   ")
        print("    %-6s %-30s %d" % (marca, etiqueta, n))
        if n and grave:
            problemas += n
    if sin_sku_ok:
        print("           (normal: materiales genericos y servicios no llevan SKU)")
    print()

    # --- 5. SKU repetido para el mismo proveedor ---
    vistos = collections.Counter()
    for r in filas:
        if r[COL_SKU] and r[COL_PROVEEDOR]:
            vistos[(str(r[COL_SKU]).strip().lower(), str(r[COL_PROVEEDOR]).strip().lower())] += 1
    repes = {k: v for k, v in vistos.items() if v > 1}
    print("--- 5. Mismo SKU repetido para el mismo proveedor ---")
    if repes:
        print("    %d SKU repetidos (puede ser legitimo: dos precios distintos" % len(repes))
        print("    del mismo articulo, ej. uno con descuento por stock limitado)")
        for (sku, prov), v in sorted(repes.items(), key=lambda x: -x[1])[:8]:
            print("      %-26s %-22s x%d" % (sku[:26], prov[:22], v))
    else:
        print("    OK: ningun SKU repetido dentro del mismo proveedor")
    print()

    print("=" * 66)
    if problemas == 0:
        print(" RESULTADO: el catalogo esta sano.")
    else:
        print(" RESULTADO: %d fila(s) necesitan revision.  Ver arriba." % problemas)
    print("=" * 66)
    return 1 if problemas else 0


if __name__ == "__main__":
    sys.exit(main())
