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
import re
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

# Columnas, base 0, segun el orden fijo documentado en actualizar-catalogo.
# Desde el 2026-09-28 son 28: la 9 (Precio de compra GV) es FORMULA, y se
# agregaron la 11 (Precio dealer, dato) y la 12 (Descuento del proveedor,
# formula que lee la pestana Descuentos por proveedor).
COL_NOMBRE, COL_MARCA, COL_SKU = 0, 1, 2
COL_CATEGORIA, COL_SUBCATEGORIA, COL_PROVEEDOR = 3, 4, 5
COL_PRECIO = 6            # G  Precio de lista del proveedor (USD), dato
COL_CRC = 7               # H  Precio de lista (CRC), formula
COL_COMPRA_USD = 8        # I  Precio de compra GV (USD), FORMULA
COL_COMPRA_CRC = 9        # J  Precio de compra GV (CRC), formula
COL_DEALER_USD = 10       # K  Precio dealer (USD), dato
COL_DESCUENTO = 11        # L  Descuento del proveedor, formula
# Por NOMBRE de posicion, nunca "la ultima columna": el 2026-09-24 se agrego
# la columna del tipo de precio y el chequeo 3, que usaba r[-1], empezo a
# pasarle "TIPO SIN CONFIRMAR" al clasificador como si fuera la categoria del
# proveedor. Paso de 2 a 564 diferencias sin que ninguna fila cambiara.
COL_CAT_ORIGINAL = 26
COL_TIPO_PRECIO = 27

# Los valores validos de la columna 28 (Tipo de precio cargado): dicen que
# trae la fuente. True = tiene que haber Precio dealer; False = no deberia
# haberlo; None = puede o no. Si se agrega un tipo, va aca, en
# actualizar-catalogo y en "Cuanto creerle al precio de cada fila" de
# buscar-equipo.
TIPOS_PRECIO = {
    "LISTA Y DEALER": True,
    "COSTO DE UNA COTIZACION REAL": True,
    "UN SOLO PRECIO EN LA LISTA": None,
    "SOLO PRECIO PUBLICO (MSRP)": False,
}


def es_numero(v):
    return isinstance(v, (int, float))


def precio_efectivo(r):
    """El precio con el que se cotizaria esta fila (R15): el Precio de compra GV.

    Es formula, asi que se lee el valor que Excel dejo guardado. Si falta
    (un archivo guardado por algo que no calcula), se rehace a mano: el
    dealer si lo hay, si no el de lista. Es el que tiene sentido comparar al
    buscar filas repetidas: dos filas con el mismo precio de lista pero
    distinto dealer no son la misma fila.
    """
    if len(r) > COL_COMPRA_USD and es_numero(r[COL_COMPRA_USD]):
        return r[COL_COMPRA_USD]
    if len(r) > COL_DEALER_USD and es_numero(r[COL_DEALER_USD]):
        return r[COL_DEALER_USD]
    return r[COL_PRECIO] if es_numero(r[COL_PRECIO]) else None


def cargar(ruta):
    wb = openpyxl.load_workbook(ruta, read_only=True, data_only=True)
    if "Catalogo" not in wb.sheetnames:
        sys.exit("El archivo no tiene una pestana 'Catalogo'.")
    filas = list(wb["Catalogo"].iter_rows(min_row=2, values_only=True))
    wb.close()
    return filas


def cargar_formulas(ruta):
    """Las formulas en texto, que `cargar` no ve porque pide los valores."""
    wb = openpyxl.load_workbook(ruta, read_only=True)
    hoja = wb["Catalogo"]
    out = []
    for n, f in enumerate(hoja.iter_rows(min_row=2, values_only=True), start=2):
        def col(i):
            return f[i] if len(f) > i else None
        out.append((n, col(COL_CRC), col(COL_COMPRA_CRC), col(COL_COMPRA_USD), col(COL_DESCUENTO)))
    wb.close()
    return out


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
            orig = r[COL_CAT_ORIGINAL] if len(r) > COL_CAT_ORIGINAL else None
            cat, sub, _ = taxonomia.clasificar(r[COL_NOMBRE], orig)
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
    # Desde R15 (2026-09-24) una fila puede traer solo el precio dealer, sin
    # precio de lista: es la mejor fila posible, no una incompleta. Lo grave
    # es no tener NINGUN precio, porque ahi no hay con que cotizar.
    #
    # Desde el 2026-09-28 el precio de compra sale solo, y lo que importa es
    # CUANTO CREERLE cuando no hay dealer: con descuento PENDIENTE (Hanwha)
    # o con el proveedor sin registrar en Descuentos por proveedor, el precio
    # de compra es el de lista tal cual y la cotizacion lo tiene que avisar.
    def descuento(r):
        return r[COL_DESCUENTO] if len(r) > COL_DESCUENTO else None

    def sin_dealer(r):
        return not (len(r) > COL_DEALER_USD and es_numero(r[COL_DEALER_USD]))

    sin_precio = sum(1 for r in filas if precio_efectivo(r) is None)
    pendiente = sum(1 for r in filas if sin_dealer(r) and descuento(r) == "PENDIENTE")
    sin_registro = sum(1 for r in filas
                       if sin_dealer(r) and es_numero(r[COL_PRECIO]) and descuento(r) in (None, ""))
    sin_marca = sum(1 for r in filas if not r[COL_MARCA])
    sin_prov = sum(1 for r in filas if not r[COL_PROVEEDOR])
    print("--- 4. Campos vacios que impiden cotizar esa fila ---")
    for etiqueta, n, grave in (("sin Modelo / SKU (equipo)", sin_sku, True),
                               ("sin ningun precio", sin_precio, True),
                               ("sin Proveedor", sin_prov, True),
                               ("sin Marca", sin_marca, False),
                               ("descuento PENDIENTE: compra = lista", pendiente, False),
                               ("proveedor sin descuento registrado", sin_registro, False),
                               ("sin SKU, material o servicio", sin_sku_ok, False)):
        marca = "FALTA" if (n and grave) else ("aviso" if n else "OK   ")
        print("    %-6s %-37s %d" % (marca, etiqueta, n))
        if n and grave:
            problemas += n
    if pendiente or sin_registro:
        print("           (no es error: esas filas se cotizan con el precio de lista")
        print("            y la cotizacion lo avisa; se resuelve en Descuentos por proveedor)")
    if sin_sku_ok:
        print("           (normal: materiales genericos y servicios no llevan SKU)")
    print()

    # --- 5. Mismo producto cargado dos veces ---
    #
    # Existe por un error del 2026-09-23: cargue "SS2421EM-ES" sin ver que el
    # catalogo ya tenia "SS2421EMES".  Compare las cadenas EXACTAS y un guion
    # basto para colar una fila repetida con otro precio.  Paso tres veces.
    #
    # Dos cosas que hay que tener claras para leer esto:
    #
    #   1. El SKU se compara NORMALIZADO (sin guiones, puntos ni espacios) y
    #      el nombre con los espacios colapsados.  Doce filas repetidas se
    #      escondian nada mas detras de un espacio de mas.
    #
    #   2. El catalogo es POR PROVEEDOR: el mismo producto ofrecido por dos
    #      proveedores son dos filas legitimas, y es justo lo que se quiere
    #      poder comparar al cotizar.  Un duplicado de verdad es una fila de
    #      mas DEL MISMO PROVEEDOR.
    def clave(v):
        return re.sub(r"[^A-Z0-9]", "", str(v).upper())

    def nombre(v):
        return re.sub(r"\s+", " ", str(v or "")).strip().lower()

    def precio(v):
        try:
            return round(float(v), 2)
        except (TypeError, ValueError):
            return None

    grupos = collections.defaultdict(list)
    for n, r in enumerate(filas, start=2):
        if r[COL_SKU] and clave(r[COL_SKU]):
            grupos[clave(r[COL_SKU])].append(n)

    repetidas, precio_raro, varios_prov = [], [], []
    for k, nums in grupos.items():
        if len(nums) < 2:
            continue
        por_prov = collections.defaultdict(list)
        for n in nums:
            por_prov[nombre(filas[n - 2][COL_PROVEEDOR])].append(n)
        if len(por_prov) > 1:
            varios_prov.append((k, sorted(nums)))
        for mismos in por_prov.values():
            if len(mismos) < 2:
                continue
            base = filas[mismos[0] - 2]
            for n in mismos[1:]:
                r = filas[n - 2]
                if precio(precio_efectivo(r)) == precio(precio_efectivo(base)):
                    repetidas.append((k, mismos[0], n, precio(precio_efectivo(base))))
                else:
                    precio_raro.append((k, mismos[0], n,
                                        precio(precio_efectivo(base)),
                                        precio(precio_efectivo(r))))

    print("--- 5. Mismo producto cargado dos veces ---")
    if repetidas:
        problemas += len(repetidas)
        print("    GRAVE: %d fila(s) sobran.  Mismo proveedor, mismo SKU y el" % len(repetidas))
        print("    mismo precio: es la misma fila cargada dos veces.")
        for k, a, b, pre in repetidas[:12]:
            print("      %-22s filas %d y %d   $%s" % (k[:22], a, b, pre))
    if precio_raro:
        problemas += len(precio_raro)
        print("    REVISAR: %d caso(s) del MISMO proveedor con el mismo SKU a" % len(precio_raro))
        print("    dos precios.  O una fila quedo vieja, o son articulos")
        print("    distintos con el codigo mal puesto.  Hay que verlo a mano.")
        for k, a, b, p1, p2 in precio_raro[:12]:
            print("      %-22s filas %d y %d   $%s vs $%s" % (k[:22], a, b, p1, p2))
    if varios_prov:
        print("    %d producto(s) los ofrece mas de un proveedor.  Es normal y" % len(varios_prov))
        print("    es lo que se busca: deja comparar precio al cotizar.")
        for k, nums in varios_prov[:5]:
            print("      %-22s filas %s" % (k[:22], ", ".join(str(n) for n in nums)))
    if not (repetidas or precio_raro):
        print("    OK: ninguna fila esta cargada dos veces")
    print()

    # --- 6. Formulas de colones apuntando a otra fila ---
    #
    # Existe por lo que aparecio el 2026-09-24: 2.534 de 2.569 filas tenian
    # el precio en colones de OTRO producto.
    #
    # La causa es una trampa de openpyxl: al borrar filas NO reajusta las
    # formulas. Una que decia `G500` en la fila 500 se mueve a la 499 y
    # sigue diciendo `G500`. Cada borrado corre una fila mas el desfase, y
    # no falla nada: la celda muestra un numero perfectamente creible que
    # pertenece a otro producto.
    #
    # Por eso se revisa que cada formula mire su PROPIA fila. La de Excel
    # (COM) si reajusta bien; la trampa es solo de openpyxl.
    #
    # Desde el 2026-09-28 tambien son formula el Precio de compra GV (col. 9)
    # y el Descuento del proveedor (col. 12). Ahi el riesgo es otro: que
    # alguien escriba un numero ENCIMA. La celda sigue mostrando un precio
    # creible, pero ya no sigue al dealer ni al descuento, y nadie se entera.
    print("--- 6. Formulas del catalogo: que esten y que miren su propia fila ---")
    corridas, rotas, pisadas = [], [], []
    RX_REF = re.compile(r"\$?([A-Z]{1,2})\$?(\d+)")
    for n, f_crc, f_compra_crc, f_compra, f_desc in cargar_formulas(ruta):
        for col, f, obligatoria in (("Precio de lista (CRC)", f_crc, False),
                                    ("Precio de compra GV (CRC)", f_compra_crc, False),
                                    ("Precio de compra GV (USD)", f_compra, True),
                                    ("Descuento del proveedor", f_desc, True)):
            if not isinstance(f, str) or not f.startswith("="):
                if obligatoria:
                    pisadas.append((n, col, f))
                continue
            if "#REF!" in f:
                rotas.append((n, col))
                continue
            # las referencias a TablaDescuentos[...] no llevan numero de fila
            filas_ref = {int(m.group(2)) for m in RX_REF.finditer(f)}
            otras = [x for x in filas_ref if x != n]
            if otras:
                corridas.append((n, col, otras[0] - n))
    if rotas:
        problemas += len(rotas)
        print("    GRAVE: %d celda(s) con #REF!.  Quedaron apuntando a una" % len(rotas))
        print("    fila que se borro.  La celda no muestra ningun precio.")
        for n, col in rotas[:6]:
            print("      fila %-6d %s" % (n, col))
    if corridas:
        problemas += len(corridas)
        print("    GRAVE: %d celda(s) calculan con los datos de OTRA fila." % len(corridas))
        print("    No da error: da un numero creible y equivocado.")
        desfases = collections.Counter((c, d) for _, c, d in corridas)
        for (c, d), k in sorted(desfases.items()):
            print("      %-28s corridas %+d fila(s): %d celdas" % (c, d, k))
        print("    Se arregla reescribiendo la formula de cada fila para que")
        print("    mire su propia fila.  Los precios en dolares cargados NO estan")
        print("    afectados: son datos fijos, no formulas.")
    if pisadas:
        problemas += len(pisadas)
        print("    GRAVE: %d celda(s) con un valor escrito encima de la formula." % len(pisadas))
        print("    Ese precio ya no sigue al dealer ni al descuento del proveedor.")
        for n, col, v in pisadas[:6]:
            print("      fila %-6d %-28s tiene %r" % (n, col, v))
        print("    Se arregla copiando la formula de la fila de arriba.  Si el valor")
        print("    escrito era un precio de compra real, va en Precio dealer (col. 11).")
    if not (rotas or corridas or pisadas):
        print("    OK: todas las formulas estan y cada una mira su propia fila")
    print()

    # --- 7. Tipo de precio cargado: que exista y que cuadre con los precios ---
    #
    # La columna 28 dice que trae la fuente de cada fila. Un tipo mal escrito
    # no rompe el calculo, pero deja a quien lee sin saber de donde salio el
    # precio; y un tipo que promete precio dealer sin tenerlo es un dato que
    # se perdio al cargar.
    print("--- 7. Tipo de precio cargado ---")
    conteo = collections.Counter()
    desconocidos, sin_su_dealer, dealer_de_mas = [], [], []
    for n, r in enumerate(filas, start=2):
        tipo = str(r[COL_TIPO_PRECIO] or "").strip() if len(r) > COL_TIPO_PRECIO else ""
        conteo[tipo or "(vacio)"] += 1
        tiene_dealer = len(r) > COL_DEALER_USD and es_numero(r[COL_DEALER_USD])
        if tipo not in TIPOS_PRECIO:
            desconocidos.append((n, tipo or "(vacio)"))
        elif TIPOS_PRECIO[tipo] is True and not tiene_dealer:
            sin_su_dealer.append((n, tipo))
        elif TIPOS_PRECIO[tipo] is False and tiene_dealer:
            dealer_de_mas.append((n, tipo))
    for tipo, c in conteo.most_common():
        print("      %-34s %d" % (tipo, c))
    if desconocidos:
        problemas += len(desconocidos)
        print("    GRAVE: %d fila(s) con el tipo vacio o mal escrito.  Validos:" % len(desconocidos))
        print("    %s" % ", ".join(TIPOS_PRECIO))
        for n, t in desconocidos[:6]:
            print("      fila %-6d '%s'" % (n, t))
    if sin_su_dealer:
        problemas += len(sin_su_dealer)
        print("    REVISAR: %d fila(s) dicen traer precio dealer y la columna 11" % len(sin_su_dealer))
        print("    esta vacia: se estan cotizando con el precio de lista.")
        for n, t in sin_su_dealer[:6]:
            print("      fila %-6d %s" % (n, t))
    if dealer_de_mas:
        print("    aviso: %d fila(s) tienen precio dealer y el tipo dice que la" % len(dealer_de_mas))
        print("    lista trae solo el precio publico.  Se cotizan bien (manda el")
        print("    dealer); falta actualizar el tipo.")
        for n, t in dealer_de_mas[:6]:
            print("      fila %-6d %s" % (n, t))
    if not (desconocidos or sin_su_dealer):
        print("    OK: todos los tipos existen y cuadran con los precios")
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
