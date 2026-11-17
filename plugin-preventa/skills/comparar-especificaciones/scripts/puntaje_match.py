# -*- coding: utf-8 -*-
"""
Calcula el % de match de cada modelo verificado contra un pliego y arma las
tablas para mostrar en el chat. Solo lee: no escribe en el catálogo.

    python -I puntaje_match.py "<requisitos.json>" "<carpeta con verif_*.json>" ^
        --modo marca+cercanos --marca Hanwha [--top 1] [--elegir L13=XNP-C9303RW] [--salida <carpeta>]

Modos:
  cercanos         todas las marcas en una tabla, las --top mejores por línea (por defecto 2)
  marca            solo --marca, la mejor por línea; las líneas sin esa marca salen como "no hay"
  marca+cercanos   dos tablas: la mejor de --marca y las --top mejores de las demás (por defecto 1)

Match  = requisitos con "C" ÷ requisitos de la línea.
"Hasta" = (C + "?") ÷ requisitos de la línea: el techo si lo que no se pudo
comprobar sale bien. Lo que no tiene ficha nunca cuenta como C (R30).

Escribe <salida>/resultado.json (todo, para un PDF o Excel después) y
<salida>/tablas.md, y muestra las tablas. Se niega si una verificación no trae
un item por requisito, en orden, o usa un estado que no sea C, N o ?.
El formato de los dos JSON está en el SKILL.md.
"""
import argparse
import datetime
import glob
import json
import os
import re
import sys
import unicodedata

RUTA = os.path.expandvars(
    r"%USERPROFILE%\OneDrive - GRUPO VISION - DYNAMIC\Accesos directos"
    r"\Archivos de Info Costa Rica - CLIENTES\00_IA_PREVENTAS\Preventas"
    r"\Catalogo\Catalogo de productos por proveedor.xlsx"
)
UMBRAL_DIAS = 60  # R12: precio de más de 2 meses se marca


def sin_acentos(s):
    s = unicodedata.normalize("NFKD", str(s or ""))
    return "".join(c for c in s if not unicodedata.combining(c))


def norm(s):
    return re.sub(r"[^A-Z0-9]", "", sin_acentos(s).upper())


def marca_base(m):
    """'Hanwha Vision' y 'Hanwha' son la misma marca; 'InVid (OEM Milesight)' es InVid."""
    return re.split(r"[ (]", str(m or "").strip())[0].lower()


def cargar_catalogo(ruta):
    import openpyxl
    wb = openpyxl.load_workbook(ruta, read_only=True, data_only=True)
    filas = []
    for n, r in enumerate(wb["Catalogo"].iter_rows(min_row=2, values_only=True), start=2):
        if not r or not r[0]:
            continue
        filas.append({"fila": n, "nombre": r[0], "marca": r[1], "codigo": r[2], "proveedor": r[5],
                      "lista": r[6], "compra": r[8], "fecha": r[17]})
    return filas


def dias_de(fecha, hoy):
    if isinstance(fecha, datetime.datetime):
        fecha = fecha.date()
    if isinstance(fecha, datetime.date):
        return (hoy - fecha).days
    try:
        return (hoy - datetime.date.fromisoformat(str(fecha)[:10])).days
    except ValueError:
        return None


def buscar_fila(cat, v, hoy):
    """Fila del catálogo: primero por 'codigo' exacto; si no, por el modelo."""
    candidatos = []
    if v.get("codigo"):
        c = norm(v["codigo"])
        candidatos = [r for r in cat if norm(r["codigo"]) == c]
    # Si no, cada pedazo del modelo con números ("AXIS S1296 Rack 192 TB (02543-001)"
    # prueba S1296 y 02543-001): primero contra el código, después contra el nombre.
    pedazos = [norm(t) for t in re.findall(r"[A-Za-z0-9][A-Za-z0-9./-]{3,}", str(v["modelo"]))]
    pedazos = [p for p in pedazos if len(p) >= 5 and re.search(r"\d", p)]
    for m in pedazos:
        if candidatos:
            break
        candidatos = [r for r in cat if norm(r["codigo"]) == m]
    for m in pedazos:
        if candidatos:
            break
        candidatos = [r for r in cat if norm(r["codigo"]).endswith(m) or m in norm(r["nombre"])]
    if not candidatos:
        return None, 0
    # Si lo venden varios proveedores, el precio más reciente; los otros se cuentan.
    candidatos.sort(key=lambda r: (dias_de(r["fecha"], hoy) is None, dias_de(r["fecha"], hoy) or 0))
    return candidatos[0], len(candidatos) - 1


def leer_verificaciones(rutas):
    salida = []
    for ruta in rutas:
        archivos = sorted(glob.glob(os.path.join(ruta, "verif_*.json"))) if os.path.isdir(ruta) else [ruta]
        for f in archivos:
            with open(f, encoding="utf-8") as fh:
                datos = json.load(fh)
            for v in datos if isinstance(datos, list) else [datos]:
                v["_archivo"] = os.path.basename(f)
                salida.append(v)
    return salida


def validar(req, verifs):
    errores = []
    lineas = {L["id"]: L for L in req["lineas"]}
    vistos = set()
    for v in verifs:
        donde = f"{v['_archivo']}: {v.get('linea')} {v.get('modelo')}"
        L = lineas.get(v.get("linea"))
        if not L:
            errores.append(f"{donde}: la línea no está en requisitos.json")
            continue
        clave = (v["linea"], norm(v["modelo"]))
        if clave in vistos:
            errores.append(f"{donde}: está dos veces")
        vistos.add(clave)
        items = v.get("items", [])
        if [i.get("n") for i in items] != [r["n"] for r in L["requisitos"]]:
            errores.append(f"{donde}: trae {len(items)} items y la línea tiene {len(L['requisitos'])} requisitos "
                           f"(tiene que haber uno por requisito, en orden)")
        malos = sorted({str(i.get("estado")) for i in items} - {"C", "N", "?"})
        if malos:
            errores.append(f"{donde}: estados que no son C, N ni ?: {malos}")
    return errores


def puntuar(req, verifs, cat, hoy, excluidas):
    lineas = {L["id"]: L for L in req["lineas"]}
    res = []
    for v in verifs:
        if marca_base(v.get("marca")) in excluidas:
            print(f"AVISO: {v['modelo']} es de una marca excluida por el pliego; no entra en las tablas.", file=sys.stderr)
            continue
        L = lineas[v["linea"]]
        etq = {r["n"]: r.get("etiqueta") or r["texto"][:40] for r in L["requisitos"]}
        its = v["items"]
        c = [i for i in its if i["estado"] == "C"]
        n = [i for i in its if i["estado"] == "N"]
        q = [i for i in its if i["estado"] == "?"]
        tot = len(its)
        fila, otros = buscar_fila(cat, v, hoy) if cat else (None, 0)
        res.append({
            "linea": L["id"], "nombre_linea": L["nombre"], "marca": v.get("marca"), "modelo": v["modelo"],
            "pct": round(100 * len(c) / tot), "pot": round(100 * (len(c) + len(q)) / tot),
            "nc": len(c), "nn": len(n), "nq": len(q), "tot": tot,
            "cumple": [etq[i["n"]] for i in c],
            "falta": [f"{etq[i['n']]} ({i.get('dato', '')})" for i in n],
            "sin": [etq[i["n"]] for i in q],
            "fila": fila["fila"] if fila else None,
            "codigo": fila["codigo"] if fila else v.get("codigo"),
            "producto": fila["nombre"] if fila else None,
            "proveedor": fila["proveedor"] if fila else None,
            "compra": fila["compra"] if fila and isinstance(fila["compra"], (int, float)) else None,
            "lista": fila["lista"] if fila and isinstance(fila["lista"], (int, float)) else None,
            "dias": dias_de(fila["fecha"], hoy) if fila else None,
            "otros_proveedores": otros,
            "fuentes": v.get("fuentes", []), "notas": v.get("notas", ""),
        })
    return res


def dinero(x):
    if x is None:
        return "sin precio en catálogo"
    return "$" + f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def corto(s, n=50):
    s = " ".join(str(s or "").split())
    return s if len(s) <= n else s[: n - 1] + "…"


def celda(x):
    return str(x).replace("|", "/").replace("\n", " ")


def fila_md(x):
    if x is None:
        return None
    precio = dinero(x["compra"])
    if x["compra"] is not None and x["dias"] is not None:
        precio += f" ({x['dias']} d{' ⚠' if x['dias'] > UMBRAL_DIAS else ''})"
    match = f"**{x['pct']} %**" + (f" (hasta {x['pot']} %)" if x["pot"] != x["pct"] else "") + f"<br>{x['nc']} de {x['tot']}"
    prov = x["proveedor"] or "—"
    if x["otros_proveedores"]:
        prov += f" (+{x['otros_proveedores']} prov.)"
    producto = f"{x['marca']} " + corto(x["producto"] or x["modelo"])
    return "| " + " | ".join(celda(c) for c in [
        f"{x['linea']} {x['nombre_linea']}", x["codigo"] or x["modelo"], producto, prov, precio, match,
        ", ".join(x["cumple"]) or "—", "; ".join(x["falta"]) or "—", ", ".join(x["sin"]) or "—"]) + " |"


ENCABEZADO = ("| Línea | Código | Producto | Proveedor | Compra (días) | Match | Cumple | Falta | Sin comprobar |\n"
              "|---|---|---|---|---|---|---|---|---|")


def ordenar(cands):
    return sorted(cands, key=lambda x: (-x["pct"], -x["pot"], x["compra"] if x["compra"] is not None else 9e12))


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("requisitos")
    ap.add_argument("verificaciones", nargs="+", help="carpeta(s) con verif_*.json o archivos sueltos")
    ap.add_argument("--modo", choices=["cercanos", "marca", "marca+cercanos"], required=True)
    ap.add_argument("--marca")
    ap.add_argument("--top", type=int)
    ap.add_argument("--elegir", action="append", default=[],
                    help="L13=XNP-C9303RW fuerza el elegido de la marca; L13o=... el de las otras")
    ap.add_argument("--salida", default=".")
    ap.add_argument("--ruta", default=RUTA, help="catálogo (por defecto el de OneDrive)")
    ap.add_argument("--sin-catalogo", action="store_true", help="no cruza con el catálogo (para probar)")
    a = ap.parse_args()
    if a.modo != "cercanos" and not a.marca:
        sys.exit("Con --modo marca o marca+cercanos hace falta --marca.")

    with open(a.requisitos, encoding="utf-8") as fh:
        req = json.load(fh)
    verifs = leer_verificaciones(a.verificaciones)
    if not verifs:
        sys.exit("No encontré verificaciones (verif_*.json).")
    errores = validar(req, verifs)
    if errores:
        print("NO SE CALCULA. Corregí estas verificaciones:", *errores, sep="\n- ")
        sys.exit(1)

    hoy = datetime.date.today()
    cat = None if a.sin_catalogo else cargar_catalogo(a.ruta)
    excluidas = {marca_base(e["marca"]) for e in req.get("excluidas", [])}
    res = puntuar(req, verifs, cat, hoy, excluidas)
    forz = dict(e.split("=", 1) for e in a.elegir)

    def elegido(cands, clave, top):
        cands = ordenar(cands)
        if clave in forz:
            f = [x for x in cands if forz[clave].upper() in (str(x["modelo"]) + " " + str(x["codigo"])).upper()]
            if f:
                cands = f + [x for x in cands if x is not f[0]]
        return cands[:top]

    partes, usados = [], set()
    marca = marca_base(a.marca) if a.marca else None
    for titulo, filtro, top, sufijo in (
        [("Todas las marcas: lo más cercano por línea", lambda x: True, a.top or 2, "")] if a.modo == "cercanos" else
        [(f"Solo {a.marca}: lo más cercano por línea", lambda x: marca_base(x["marca"]) == marca, 1, "")] +
        ([("Otras marcas: lo más cercano por línea", lambda x: marca_base(x["marca"]) != marca, a.top or 1, "o")]
         if a.modo == "marca+cercanos" else [])):
        filas = [f"### {titulo}", "", ENCABEZADO]
        for L in req["lineas"]:
            cands = [x for x in res if x["linea"] == L["id"] and filtro(x)]
            if not cands:
                filas.append(f"| {L['id']} {celda(L['nombre'])} | — | No hay candidato verificado | — | — | — | — | — | — |")
                continue
            for x in elegido(cands, L["id"] + sufijo, top):
                usados.add(id(x))
                filas.append(fila_md(x))
        partes.append("\n".join(filas))

    resto = [x for x in res if id(x) not in usados]
    if resto:
        alt = ["### Alternativas revisadas", ""]
        for x in sorted(resto, key=lambda x: ([L["id"] for L in req["lineas"]].index(x["linea"]), -x["pct"])):
            p = dinero(x["compra"]) + (f" ({x['dias']} d)" if x["compra"] is not None and x["dias"] is not None else "")
            alt.append(f"- {x['linea']} {x['marca']} {x['codigo'] or x['modelo']}: {x['pct']} % (hasta {x['pot']} %), {p}")
        partes.append("\n".join(alt))

    sin_fila = [x["modelo"] for x in res if cat is not None and x["fila"] is None]
    if sin_fila:
        partes.append("Sin fila en el catálogo (no hay precio): " + ", ".join(sin_fila))

    md = "\n\n".join(partes) + "\n"
    os.makedirs(a.salida, exist_ok=True)
    with open(os.path.join(a.salida, "tablas.md"), "w", encoding="utf-8") as fh:
        fh.write(md)
    with open(os.path.join(a.salida, "resultado.json"), "w", encoding="utf-8") as fh:
        json.dump({"documento": req.get("documento"), "modo": a.modo, "marca": a.marca,
                   "fecha": hoy.isoformat(), "resultados": res}, fh, ensure_ascii=False, indent=1, default=str)
    print(md)


if __name__ == "__main__":
    main()
