# -*- coding: utf-8 -*-
"""
Prepara la carga al catalogo de los productos bajados de los portales de
proveedor (Tectel, Sekunet, Intcomex, Syscom) con la sesion de GV.

Solo LEE el catalogo (openpyxl, read_only) y los JSON de los portales, y deja
un JSON con lo que hay que escribir: filas existentes que se actualizan y
filas nuevas. La escritura la hace cargar_portales.ps1, por Excel (COM).

Uso:
    python -I preparar_portales.py <catalogo.xlsx> <carpeta_json> <salida.json>

Cada JSON de portal tiene {"proveedor", "fecha", "fuente", "productos": [...]},
con productos que traen al menos sku, nombre y precio_gv (el precio que ve la
cuenta de GV, sin IVA). Ver actualizar-catalogo, "Portales de proveedor".
"""
import datetime
import glob
import json
import os
import re
import sys
from collections import Counter, defaultdict

import openpyxl

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "scripts"))
import taxonomia  # noqa: E402

TIPO_SOLO_PORTAL = "PRECIO DEL PORTAL DEL PROVEEDOR"
TIPO_LISTA_Y_DEALER = "LISTA Y DEALER"

DOMINIO = {"Tectel": "tectelcr.com", "Sekunet": "sekunet.com",
           "Intcomex": "myservices.intcomex.com", "Syscom": "syscom.mx"}

# Syscom se baja por busquedas de productos pequenos (R21): solo entra lo que
# el clasificador pone en estas categorias. Lo demas es ruido de la busqueda.
SYSCOM_CATEGORIAS = {"Energia", "Control de acceso", "Alarma e intrusion",
                     "Deteccion de incendio", "Red y conectividad", "Almacenamiento",
                     "Materiales de instalacion", "Accesorio de instalacion"}
SYSCOM_SIN = {("Control de acceso", "Torniquete"), ("Control de acceso", "Intercomunicador"),
              ("Red y conectividad", "Firewall / router"), ("Red y conectividad", "Antena")}


# Cuando el nombre no alcanza para clasificar, la seccion del portal si dice la
# categoria (los modulos direccionables de incendio, por ejemplo, no dicen
# "incendio" en el nombre). Va despues del clasificador, nunca antes.
PISTAS_SECCION = [
    (r"incendio|fuego|fire|direccionable", "Deteccion de incendio"),
    (r"control de acceso|cerradura|boton(es)? de salida", "Control de acceso"),
    (r"energia|ups|respaldo|fuentes? de poder", "Energia"),
    (r"intrusion|alarma|cercas? electrica|sensores|sirenas", "Alarma e intrusion"),
]


def _sub_alarma(n):
    for claves, sub in [(["sirena", "siren"], "Sirena"), (["contacto magnetico", "magnetic contact"], "Contacto magnetico"),
                        (["panico", "panic"], "Boton de panico"), (["movimiento", " pir", "infrarrojo", "motion"], "Detector de movimiento"),
                        (["panel", "consola"], "Panel de alarma"), (["comunicador", "communicator"], "Comunicador")]:
        if any(k in n for k in claves):
            return sub
    return "Accesorio de alarma"


def clasificar_con_seccion(nombre, secciones):
    cat, sub, _ = taxonomia.clasificar(nombre, None)
    if cat != "Sin clasificar":
        return cat, sub
    # racks: van con los gabinetes (R19: el acompanante mas comun de camaras y controladoras)
    if re.match(r"(?i)\s*rack\b", str(nombre)):
        return "Accesorio de instalacion", "Caja / housing"
    if re.match(r"(?i)\s*(charola|organizador|bandeja|panel ciego|multicontacto)\b.*rack", str(nombre)):
        return "Accesorio de instalacion", "Otros accesorios"
    for s in secciones:
        cat, sub, _ = taxonomia.clasificar(nombre, s)
        if cat != "Sin clasificar":
            return cat, sub
    pista = taxonomia.norm(" ".join(secciones))
    n = taxonomia.norm(nombre)
    for patron, cat in PISTAS_SECCION:
        if re.search(patron, pista):
            if cat == "Alarma e intrusion":
                return cat, _sub_alarma(n)
            return cat, taxonomia.SUB_POR_SECCION[cat](n)
    # ultimo recurso: el nombre junto con el texto de la seccion ("Switches, APs y routers")
    cat, sub, _ = taxonomia.clasificar(nombre + " " + " ".join(secciones), None)
    return cat, sub


def clave(s):
    return re.sub(r"[^A-Z0-9]", "", str(s or "").upper())


def texto(s, largo=None):
    t = re.sub(r"\s+", " ", str(s or "")).strip()
    if t[:1] in ("=", "+", "-", "@"):
        t = "'" + t
    return t[:largo] if largo else t


def numero(v):
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None
    return round(x, 2) if x > 0 else None


def unidad(nombre):
    n = taxonomia.norm(nombre)
    if " rollo" in n or " bobina" in n or "305m" in n or "305 m" in n:
        return "Rollo"
    if " por metro" in n or " x metro" in n:
        return "Metro"
    return "Unidad"


def leer_catalogo(ruta):
    wb = openpyxl.load_workbook(ruta, read_only=True, data_only=True)
    ws = wb["Catalogo"]
    filas, marcas = [], Counter()
    for i, r in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
        if not r or not any(v not in (None, "") for v in r[:6]):
            continue
        filas.append((i, r))
        if r[1] and len(str(r[1]).strip()) >= 3:
            marcas[str(r[1]).strip()] += 1
    return filas, marcas


def marca_por_nombre(nombre, marcas):
    n = " " + re.sub(r"[^A-Z0-9]+", " ", str(nombre or "").upper()) + " "
    for m in marcas:
        if " " + re.sub(r"[^A-Z0-9]+", " ", m.upper()).strip() + " " in n:
            return m
    return None


def main(ruta_cat, carpeta, salida):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # con -I no se lee PYTHONIOENCODING
    filas, marcas_cat = leer_catalogo(ruta_cat)
    # marcas conocidas, de la mas larga a la mas corta ("Western Digital" antes que "Digital")
    marcas = sorted({m for m in marcas_cat if not re.fullmatch(r"[0-9 .-]+", m)}, key=len, reverse=True)
    existentes = defaultdict(list)          # (proveedor, sku) -> filas del catalogo
    for i, r in filas:
        prov = str(r[5] or "").strip().lower()
        if r[2]:
            existentes[(prov, clave(r[2]))].append((i, r))

    actualizar, nuevas, omitidas = [], [], Counter()
    ejemplos_omitidas = defaultdict(list)
    resumen = {}
    for ruta in sorted(glob.glob(os.path.join(carpeta, "*_productos.json"))):
        d = json.load(open(ruta, encoding="utf-8"))
        prov = d["proveedor"]
        fecha = d["fecha"]
        f_excel = (datetime.date.fromisoformat(fecha) - datetime.date(1899, 12, 30)).days
        origen = "Portal de %s (%s) con la sesion de GV, consultado el %s" % (prov, DOMINIO.get(prov, ""), fecha)
        vistos = set()
        c = Counter()
        for p in d["productos"]:
            sku = str(p.get("sku") or "").strip()
            gv = numero(p.get("precio_gv"))
            lista = numero(p.get("precio_lista"))
            nombre = texto(p.get("nombre"), 250)
            if not sku or not gv or not nombre:
                omitidas[prov + ": sin codigo o sin precio"] += 1
                continue
            k = clave(sku)
            if k in vistos:
                omitidas[prov + ": repetido en el portal"] += 1
                continue
            vistos.add(k)
            if prov == "Syscom" and p.get("obsoleto"):
                omitidas[prov + ": obsoleto"] += 1
                continue
            cats = p.get("categorias") or p.get("terminos") or []
            if p.get("categoria"):
                cats = [p["categoria"]] + [x.strip() for x in p["categoria"].split(">")]
            cat_orig = p.get("categoria") or " / ".join(cats)
            cat, sub = clasificar_con_seccion(nombre, cats)
            if cat == "Sin clasificar":
                omitidas[prov + ": fuera de las categorias del catalogo"] += 1
                if len(ejemplos_omitidas[prov]) < 6:
                    ejemplos_omitidas[prov].append(nombre[:70])
                continue
            if sub not in dict(taxonomia.TAXONOMIA).get(cat, []):
                omitidas[prov + ": par categoria/subcategoria invalido %s / %s" % (cat, sub)] += 1
                continue
            if prov == "Syscom" and (cat not in SYSCOM_CATEGORIAS or (cat, sub) in SYSCOM_SIN):
                omitidas[prov + ": fuera de productos pequenos (R21)"] += 1
                continue
            if lista is not None and lista < gv:
                lista = None                      # una lista menor que el precio de GV no es una lista
            tipo = TIPO_LISTA_Y_DEALER if lista is not None else TIPO_SOLO_PORTAL
            marca = texto(p.get("marca")) or marca_por_nombre(nombre, marcas)
            # existencias: van en la descripcion, para que buscar-equipo no ofrezca lo agotado (R21)
            if prov == "Tectel":
                exist = "en existencia: %s" % (p.get("stock") or ("si" if p.get("en_stock") else "no"))
                desc = texto(p.get("descripcion"), 300)
            elif prov == "Sekunet":
                exist = "por sucursal: %s" % (p.get("existencias") or "no indica")
                desc = ""
            elif prov == "Intcomex":
                exist = "Coyol %s, otras bodegas %s" % (p.get("existencias_coyol"), p.get("existencias_otras"))
                desc = "MPN %s" % p.get("mpn") if p.get("mpn") else ""
            else:
                exist = "con existencia" if p.get("tiene_stock") else ("bajo pedido" if p.get("bajo_pedido") else "sin existencia")
                desc = ""
            nota = "-- Precio de GV sin IVA, del portal del proveedor (%s). Existencias el %s: %s" % (fecha, fecha, exist)
            descripcion = texto((desc + " " + nota).strip(), 900)
            m = existentes.get((prov.lower(), k))
            if m:
                if len(m) > 1:
                    omitidas[prov + ": el codigo esta repetido en el catalogo, no se toca"] += 1
                    continue
                i, r = m[0]
                actualizar.append({
                    "fila": i, "sku": str(r[2]), "proveedor_actual": str(r[5]),
                    "antes": {"G": r[6], "K": r[10], "R": r[17].strftime("%Y-%m-%d") if isinstance(r[17], datetime.datetime) else r[17], "AB": r[27]},
                    "G": lista, "K": gv, "R": f_excel, "Y": origen, "AB": tipo,
                    "compra_antes": r[8], "nombre": str(r[0])[:60]})
                c["actualizadas"] += 1
                continue
            nuevas.append({"c1": nombre, "c2": marca, "c3": sku, "c4": cat, "c5": sub, "c6": prov,
                           "c7": lista, "c11": gv, "c13": unidad(nombre), "c16": descripcion,
                           "c18": f_excel, "c25": origen, "c27": texto(cat_orig, 250), "c28": tipo})
            c["nuevas"] += 1
        resumen[prov] = {"en el portal": len(d["productos"]), **c}

    # Revision de precios de las actualizaciones: un salto grande se marca
    saltos = []
    for a in actualizar:
        antes = a["compra_antes"]
        if isinstance(antes, (int, float)) and antes > 0:
            ratio = a["K"] / antes
            a["cambio_pct"] = round((ratio - 1) * 100, 1)
            if ratio > 1.5 or ratio < 0.6:
                saltos.append(a)
    json.dump({"actualizar": actualizar, "filas": nuevas}, open(salida, "w", encoding="utf-8"), ensure_ascii=False)

    print("catalogo leido:", len(filas), "filas")
    for prov, r in resumen.items():
        print("%-9s %s" % (prov, r))
    print("omitidas:")
    for k, v in sorted(omitidas.items()):
        print("   %-60s %d" % (k, v))
    for prov, ej in ejemplos_omitidas.items():
        print("   ej. %s fuera de categorias: %s" % (prov, " | ".join(ej)))
    print("nuevas por categoria:", Counter(f["c4"] for f in nuevas).most_common())
    print("nuevas sin marca:", sum(1 for f in nuevas if not f["c2"]), "de", len(nuevas))
    print("actualizaciones con salto de precio >50%% o <-40%%: %d" % len(saltos))
    for a in saltos[:12]:
        print("   fila %d %s (%s): compra %s -> %s (%+.0f%%)" % (a["fila"], a["sku"], a["proveedor_actual"], a["compra_antes"], a["K"], a["cambio_pct"]))
    print("GUARDADO", salida, "| actualizar", len(actualizar), "| nuevas", len(nuevas))


if __name__ == "__main__":
    main(*sys.argv[1:4])
