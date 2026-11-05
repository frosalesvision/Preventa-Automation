# -*- coding: utf-8 -*-
"""
Prepara la carga al catalogo de una lista de precios nueva de Hanwha Vision
America (Excel con las pestanas New, HVA Pricelist, Limited Stock y EOL Product).

Solo LEE el catalogo y las dos listas, y deja un JSON con lo que hay que hacer.
La escritura la hace cargar_lista_hanwha.ps1, por Excel (COM).

Uso:
    python -I preparar_lista_hanwha.py <catalogo.xlsx> <lista_nueva.xlsx> <lista_anterior.xlsx> <salida.json> <fecha AAAA-MM-DD>

La fecha es la de la lista ("New & Change in November 1, 2026"), no la del dia
de la carga. Por cada fila de "Hanwha Vision America" en el catalogo:

- Sigue vigente en la lista: se actualiza el precio si cambio, la fecha, el
  archivo y la pestana de origen, y los datos que el fabricante cambio.
- Paso a la pestana EOL: se propone quitarla, con su reemplazo recomendado.
- No esta en ninguna pestana: se reporta y no se toca.

Lo que no esta en el catalogo y si en la lista es una fila nueva.

Una persona pudo haber corregido un dato a proposito (R28): un campo solo se
pisa si en el catalogo esta vacio o tiene lo que decia la lista anterior. Si
tiene otra cosa, se conserva y se reporta. La categoria y la subcategoria de una
fila que ya existe nunca se tocan.
"""
import datetime
import json
import os
import re
import sys
import warnings
from collections import Counter, defaultdict

import openpyxl

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "scripts"))
import taxonomia  # noqa: E402

warnings.filterwarnings("ignore", category=UserWarning)

PROVEEDOR = "Hanwha Vision America"
MARCA = "Hanwha"
TIPO = "SOLO PRECIO PUBLICO (MSRP)"
ACTIVAS = ("HVA Pricelist", "New", "Limited Stock")     # de la mas completa a la menos

# columna del catalogo (letra) -> encabezado de la lista. P (descripcion) se arma aparte.
CAMPOS = {"A": "Item Type", "N": "Avg. Lead Time (Days)", "O": "Country of Origin", "T": "Weight (Lbs)",
          "U": "H*W*D (Inches)", "V": "HTS", "W": "ECCN", "X": "EAN code", "AA": "Category"}
POS = {"A": 0, "C": 2, "D": 3, "E": 4, "F": 5, "G": 6, "K": 10, "N": 13, "O": 14, "P": 15, "R": 17,
       "T": 19, "U": 20, "V": 21, "W": 22, "X": 23, "Y": 24, "Z": 25, "AA": 26, "AB": 27}
NOTA = " -- Nota del proveedor: "
SUFIJO_LIMITADO = NOTA + "Precio de stock limitado / liquidacion (disponibilidad no garantizada)"


def clave(s):
    return re.sub(r"[^A-Z0-9]", "", str(s or "").upper())


def limpio(v):
    """La lista trae espacios duros y celdas con solo un espacio duro."""
    if isinstance(v, str):
        return v.replace("\xa0", " ").strip() or None
    return v


def numero(v):
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return float(v)
    try:
        return float(str(v).replace(",", "").strip())
    except (TypeError, ValueError):
        return None


def comparable(v):
    v = limpio(v)
    if v is None:
        return ""
    n = numero(v)
    return "%.6f" % n if n is not None else re.sub(r"\s+", " ", str(v)).strip()


def igual(a, b):
    return comparable(a) == comparable(b)


def como_dato(v):
    """Numeros como numeros (actualizar-catalogo, 'Los tipos de dato importan')."""
    n = numero(v)
    return (int(n) if n == int(n) else n) if n is not None else limpio(v)


def leer_lista(ruta):
    """{pestana: {clave: fila}}; en cada fila, el primer valor de cada encabezado."""
    wb = openpyxl.load_workbook(ruta, read_only=True, data_only=True)
    res = {}
    for tab in ACTIVAS + ("EOL Product",):
        filas, enc = {}, None
        for r in wb[tab].iter_rows(values_only=True):
            vals = [str(x).strip() if x is not None else "" for x in r]
            if "Item #" in vals:        # New trae dos tablas, cada una con su encabezado
                enc = vals
                continue
            if enc is None:
                continue
            d = {}
            for i, h in enumerate(enc):
                if h and i < len(r) and h not in d:
                    d[h] = r[i]
            if limpio(d.get("Item #")) is not None:
                filas.setdefault(clave(d["Item #"]), d)
        res[tab] = filas
    return res


def en_tabs(lista, k):
    return {t: lista[t][k] for t in ACTIVAS if k in lista[t]}


def dato(filas, h, primero=None):
    """El primer valor que aparezca: de la pestana dada y despues de la mas completa a la menos."""
    for t in ((primero,) if primero else ()) + ACTIVAS:
        if t in filas and limpio(filas[t].get(h)) is not None:
            return limpio(filas[t].get(h))
    return None


def descripcion(filas, primero=None):
    """El texto de la fila del catalogo: descripcion + nota del fabricante. Una fila con el
    precio de Limited Stock lleva la nota de esa pestana (a veces distinta de la general)."""
    d, n = dato(filas, "Description", primero), dato(filas, "Notes", primero)
    return (d or "") + (NOTA + n if n else "")


def precios_de(filas):
    return {t: numero(f.get("MSRP")) for t, f in filas.items() if numero(f.get("MSRP")) is not None}


def elegir_precio(filas, actual):
    """Devuelve (precio, pestana). Hanwha puede publicar dos precios para un modelo:
    el general y el de Limited Stock. Se respeta el que ya tiene el catalogo mientras
    siga publicado; si no esta, manda el de la lista general."""
    p = precios_de(filas)
    if not p:
        return None, None
    for t in ACTIVAS:
        if t in p and actual is not None and abs(p[t] - actual) < 0.005:
            return p[t], t
    t = next(x for x in ACTIVAS if x in p)
    return p[t], t


def main(ruta_cat, ruta_nueva, ruta_ant, salida, fecha):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # con -I no se lee PYTHONIOENCODING
    archivo = os.path.basename(ruta_nueva)
    archivo_ant = os.path.basename(ruta_ant)
    f_excel = (datetime.date.fromisoformat(fecha) - datetime.date(1899, 12, 30)).days
    nueva, ant = leer_lista(ruta_nueva), leer_lista(ruta_ant)
    activas = {k for t in ACTIVAS for k in nueva[t]}

    wb = openpyxl.load_workbook(ruta_cat, read_only=True, data_only=True)
    catalogo, otros_prov = {}, defaultdict(list)
    repetidos = []
    for i, r in enumerate(wb["Catalogo"].iter_rows(min_row=2, values_only=True), start=2):
        if not r or not r[2]:
            continue
        k = clave(r[2])
        if str(r[5] or "").strip() == PROVEEDOR:
            if k in catalogo:
                repetidos.append(str(r[2]))
            catalogo[k] = (i, list(r[:28]))
        elif "hanwha" in str(r[1] or "").lower():
            otros_prov[k].append((i, str(r[2]), str(r[5])))
    if repetidos:
        print("AVISO: codigos repetidos en el catalogo, se tomo la ultima fila:", repetidos[:20])

    actualizar, quitar, ausentes, conservados = [], [], [], []
    cuenta = Counter()
    for k, (fila, r) in catalogo.items():
        filas = en_tabs(nueva, k)
        if not filas:
            if k in nueva["EOL Product"]:
                e = nueva["EOL Product"][k]
                quitar.append({"fila": fila, "sku": str(r[2]), "G": r[POS["G"]], "subcategoria": r[POS["E"]], "nombre": str(r[0])[:70],
                               "fecha_eol": str(e.get("EOL Date"))[:10], "reemplazo": limpio(e.get("Replacement"))})
            else:
                ausentes.append({"fila": fila, "sku": str(r[2]), "G": r[POS["G"]]})
            continue
        previas = en_tabs(ant, k)
        actual = numero(r[POS["G"]])
        precio, tab = elegir_precio(filas, actual)
        if precio is None:
            cuenta["sin precio en la lista: no se toca"] += 1
            continue
        cambios = {"R": f_excel, "Z": tab}
        y = str(r[POS["Y"]] or "")
        cambios["Y"] = y.replace(archivo_ant, archivo) if archivo_ant in y else archivo
        cambio_precio = actual is None or abs(precio - actual) >= 0.005
        if cambio_precio:
            cambios["G"] = precio
            cuenta["precio sube" if actual is not None and precio > actual else "precio baja"] += 1
        else:
            cuenta["precio igual"] += 1
        # los demas datos, campo por campo
        for col, h in CAMPOS.items():
            en_cat, en_nueva = r[POS[col]], dato(filas, h)
            if en_nueva is None or igual(en_cat, en_nueva):
                continue
            if limpio(en_cat) is None or any(igual(en_cat, limpio(f.get(h))) for f in previas.values()):
                cambios[col] = como_dato(en_nueva) if col in ("N", "T") else en_nueva
                cuenta["dato de " + h] += 1
            else:
                conservados.append({"fila": fila, "sku": str(r[2]), "col": col, "catalogo": str(en_cat)[:80], "lista": str(en_nueva)[:80]})
        # la nota de liquidacion la agrego el catalogo, no la lista: se compara sin ella y se conserva
        en_cat, en_nueva = str(r[POS["P"]] or "").rstrip(), descripcion(filas, tab)
        sufijo = SUFIJO_LIMITADO if en_cat.endswith(SUFIJO_LIMITADO) else ""
        if sufijo:
            en_cat = en_cat[:-len(sufijo)]
        if en_nueva and not igual(en_cat, en_nueva):
            if limpio(en_cat) is None or any(igual(en_cat, descripcion({t: f})) for t, f in previas.items()):
                cambios["P"] = en_nueva + sufijo
                cuenta["descripcion o nota"] += 1
            else:
                conservados.append({"fila": fila, "sku": str(r[2]), "col": "P", "catalogo": en_cat[:80], "lista": en_nueva[:80]})
        actualizar.append({"fila": fila, "sku": str(r[2]), "nombre": str(r[0])[:70], "subcategoria": r[POS["E"]], "antes": {"G": r[POS["G"]]}, "cambios": cambios})

    nuevas, sin_clasificar = [], []
    for k in sorted(activas - set(catalogo)):
        filas = en_tabs(nueva, k)
        precio, tab = elegir_precio(filas, None)
        d0 = next(iter(filas.values()))
        nombre, cat_orig = dato(filas, "Item Type"), dato(filas, "Category")
        if precio is None or not nombre:
            cuenta["nueva sin precio o sin nombre: no entra"] += 1
            continue
        cat, sub, _ = taxonomia.clasificar(nombre, cat_orig)
        if cat == "Sin clasificar":
            sin_clasificar.append({"sku": str(d0["Item #"]).strip(), "nombre": nombre, "categoria": cat_orig})
        nuevas.append({"A": nombre, "B": MARCA, "C": str(d0["Item #"]).strip(), "D": cat, "E": sub, "F": PROVEEDOR, "G": precio,
                       "M": "Unidad", "N": como_dato(dato(filas, "Avg. Lead Time (Days)")), "O": dato(filas, "Country of Origin"),
                       "P": descripcion(filas), "R": f_excel, "T": como_dato(dato(filas, "Weight (Lbs)")),
                       "U": dato(filas, "H*W*D (Inches)"), "V": dato(filas, "HTS"), "W": dato(filas, "ECCN"),
                       "X": dato(filas, "EAN code"), "Y": archivo, "Z": tab, "AA": cat_orig, "AB": TIPO})

    json.dump({"proveedor": PROVEEDOR, "archivo": archivo, "fecha": fecha, "actualizar": actualizar, "quitar": quitar, "filas": nuevas},
              open(salida, "w", encoding="utf-8"), ensure_ascii=False)

    # --- resumen ---
    print("lista nueva:", {t: len(v) for t, v in nueva.items()})
    print("catalogo, filas de %s: %d" % (PROVEEDOR, len(catalogo)))
    print("siguen vigentes: %d | a quitar (EOL): %d | no estan en ninguna pestana: %d | nuevas: %d" % (len(actualizar), len(quitar), len(ausentes), len(nuevas)))
    for k, v in cuenta.most_common():
        print("   %-42s %d" % (k, v))

    subidas = [(a, numero(a["antes"]["G"]), a["cambios"]["G"]) for a in actualizar if "G" in a["cambios"] and numero(a["antes"]["G"])]
    if subidas:
        pct = sorted((n / v - 1) * 100 for _, v, n in subidas)
        print("cambio de precio: min %+.1f%% | mediana %+.1f%% | max %+.1f%%" % (pct[0], pct[len(pct) // 2], pct[-1]))
        por = defaultdict(list)
        for a, v, n in subidas:
            por[a["subcategoria"]].append((n / v - 1) * 100)
        for s, l in sorted(por.items(), key=lambda x: -len(x[1])):
            l.sort()
            print("   %-34s %3d modelos, mediana %+.0f%%, de %+.0f%% a %+.0f%%" % (s, len(l), l[len(l) // 2], l[0], l[-1]))
        print("saltos de mas de +50%:")
        for a, v, n in sorted(subidas, key=lambda x: -(x[2] / x[1])):
            if n / v > 1.5:
                print("   fila %d %-22s %-34s %10.2f -> %10.2f (%+.0f%%)" % (a["fila"], a["sku"], a["nombre"][:34], v, n, (n / v - 1) * 100))
    print("a quitar por subcategoria:", Counter(q["subcategoria"] for q in quitar).most_common())
    print("sin reemplazo:", [q["sku"] for q in quitar if not q["reemplazo"] or "no replacement" in str(q["reemplazo"]).lower()])
    malos = [q for q in quitar if q["reemplazo"] and "no replacement" not in str(q["reemplazo"]).lower() and clave(q["reemplazo"]) not in activas]
    print("con reemplazo que no esta vigente en la lista:", [(q["sku"], q["reemplazo"]) for q in malos])
    print("no estan en ninguna pestana:", ausentes[:20])
    print("nuevas por categoria:", Counter((f["D"], f["E"]) for f in nuevas).most_common())
    print("nuevas sin clasificar:", sin_clasificar)
    print("datos conservados porque el catalogo tiene otra cosa (R28): %d" % len(conservados))
    for c in conservados[:15]:
        print("   ", c)
    eol_otros = [v for k, v in otros_prov.items() if k in nueva["EOL Product"] and k not in activas]
    print("modelos Hanwha de otros proveedores que pasaron a EOL (no se tocan):", eol_otros)
    largos = [(f["C"], len(f["P"])) for f in nuevas if len(f["P"]) > 900]
    print("descripciones de mas de 900 caracteres en las nuevas:", largos[:10])
    print("GUARDADO", salida)


if __name__ == "__main__":
    main(*sys.argv[1:6])
