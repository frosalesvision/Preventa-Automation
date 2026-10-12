"""Calcula los pares de la pestana "Compatibilidad de Accesorios" del
Catalogo de productos por proveedor.xlsx y los deja en un JSON.

Uso:
    python generar_matriz_accesorios.py "<catalogo.xlsx>" "<salida.json>"

SOLO LEE el catalogo. La pestana la escribe despues, por Excel (COM),
escribir_matriz_accesorios.ps1 -- nunca openpyxl, que al guardar borra los
desplegables de Categoria y Subcategoria (medido el 2026-09-23).

Regla de fondo (rehecho el 2026-10-12): un par solo entra si un documento
del fabricante lo dice. Cada par lleva en "Notas" la frase exacta que lo
respalda, para que cualquiera pueda revisarlo sin abrir la lista de precios.

Tres fuentes, columna "Fuente":
1. El texto del fabricante nombra el modelo exacto (Hanwha, InVid y 2N por
   numero de parte; Axis por nombre de modelo, porque su numero de parte
   es otro: "Hard coated smoked dome for AXIS Q6124-E, Q6128-E").
2. El fabricante dice la familia, no el modelo ("Wall Mount for Paramont
   PTZ Cameras"): solo los casos de FAMILIAS_VERIFICADAS, revisados a mano
   contra el PDF de origen. Nunca se infiere una familia sola: la version
   anterior lo hacia por palabras sueltas y emparejaba, por ejemplo, un
   soporte de techo para un solo modelo con todas las PTZ de la marca.
3. Pares vistos en cotizaciones reales: PARES_DE_COTIZACIONES, hoy vacia
   (ver la nota ahi).

Que lado del par es el accesorio lo decide la Categoria del catalogo, no
palabras sueltas del nombre. Si los dos lados son accesorios (un soporte de
esquina que va con un soporte de pared) o ninguno lo es, el par no entra.
"""
import collections
import json
import re
import sys
import warnings

import openpyxl

warnings.filterwarnings("ignore")

SHEET_NAME = "Compatibilidad de Accesorios"
HEADERS = [
    "Modelo Camara", "Nombre Camara", "Marca Camara",
    "Modelo Accesorio", "Nombre Accesorio", "Tipo Accesorio", "Marca Accesorio",
    "Proveedor", "Fuente", "Notas",
]
FUENTE_EXACTA = "Fabricante: nombra el modelo exacto"
FUENTE_FAMILIA = "Fabricante: nombra la familia, no el modelo - verificar antes de cotizar"
FUENTE_COTIZACION = "Cotizacion real (no lo documenta el fabricante) - verificar antes de usar"

# Lado "accesorio" y lado "equipo", segun la taxonomia del catalogo.
SUB_ACCESORIO = {"Lente", "Fuente de poder", "Inyector PoE", "Cableado"}
CAT_EQUIPO = {"Camara", "Control de acceso", "Audio", "Grabacion y video",
              "Alarma e intrusion", "Deteccion de incendio", "Monitor y visualizacion"}
# Fuera de las camaras, algunas piezas quedaron con la categoria del equipo
# al que acompanan ("White Cover for Video Intercom TID-600" esta como
# Intercomunicador). Si el nombre dice que es una pieza de montaje, cuenta
# como accesorio. No se aplica a camaras: "Wall Mount Panoramic Camera" es
# una camara.
PIEZA = re.compile(r"\b(cover|back\s?box|backbox|flush box|surface box|junction box|mount|bracket|"
                   r"housing|adapter|adaptor|frame|chassis|chassi|plate|gooseneck|spacer)\b", re.I)
# Los iluminadores son equipos (llevan soporte propio) aunque el catalogo
# los tenga entre los accesorios.
ILUMINADOR = re.compile(r"\billuminator\b", re.I)

# Frases con las que el fabricante dice "esto sirve para":
TRIGGERS = [
    re.compile(r"[Cc]ompatible with:?\s+(.+?)(?:\s--\s|\n|\.\s|\.$|$)"),
    re.compile(r"[Ff]or(?: [Tt]he)?\s*\(([^)]+)\)"),
    re.compile(r"[Ff]or [Tt]he\s+([^.\n]+?)(?:\s--\s|\.\s|\.$|\n|$)"),
    re.compile(r"\b[Ff][Oo][Rr]\s+([A-Za-z0-9][A-Za-z0-9\-/:, &.]*?)(?:\s--\s|\.\s|\.$|\n|$)"),
    re.compile(r"[Ss]upported cameras?\s*\(([^)]+)\)"),
    re.compile(r"[Uu]sed with\s+(.+?)(?:\s--\s|\.\s|\.$|\n|$)"),
    re.compile(r"[Ff]its\s+(.+?)(?:\s--\s|\.\s|\.$|\n|$)"),
    re.compile(r"[Ss]uitable for\s+(.+?)(?:\s--\s|\.\s|\.$|\n|$)"),
    re.compile(r"[Dd]esigned for\s+(.+?)(?:\s--\s|\.\s|\.$|\n|$)"),
    re.compile(r"[Ii]ntended for\s+(.+?)(?:\s--\s|\.\s|\.$|\n|$)"),
    re.compile(r"[Aa]ccessor(?:y|ies) for\s+(.+?)(?:\s--\s|\.\s|\.$|\n|$)"),
]

# Familias que el fabricante nombra sin modelo, verificadas a mano contra
# el documento de origen. (sku_accesorio, regla para elegir los equipos,
# frase y pagina del documento). Si una frase no alcanza para decidir a
# que modelos aplica, NO se agrega aca.
FAMILIAS_VERIFICADAS = [
    # LISTA DE PRECIOS INVID-MILESIGH.pdf, pag. 21. La misma pagina trae
    # soporte propio para las mini PTZ 2.8-12mm (IPM-TXWM2) y la PTZ
    # bullet es otro formato: la familia son las PTZ domo con zoom optico.
    ("IPM-PTZWALL1", {"marca": "Paramont", "nombre": [r"Outdoor PTZ", r"\d+x (?:Optical )?Zoom"], "no": [r"Bullet", r"2\.8-12mm"]},
     'Lista de InVid, pag. 21: "Wall Mount for Paramont PTZ Cameras"'),
    ("IPM-PTZCORNER", {"marca": "Paramont", "nombre": [r"Outdoor PTZ", r"\d+x (?:Optical )?Zoom"], "no": [r"Bullet", r"2\.8-12mm"]},
     'Lista de InVid, pag. 21: "Corner Mount for Paramont PTZ Cameras"'),
]

# Pares vistos en cotizaciones reales del equipo. Vacia desde el
# 2026-10-12: los 10 que habia salian de una cotizacion que se armo copiando
# la version i-PRO del mismo proyecto y cambiando solo las camaras; los
# soportes i-PRO y la base Hanwha quedaron debajo de las Paramont de
# arrastre, no porque sirvan. Antes de agregar uno, confirmar en la ficha
# del fabricante o con el proveedor. (sku_equipo, sku_accesorio, nota)
PARES_DE_COTIZACIONES = []

TIPOS = [
    (r"\blens\b|\blente\b", "Lente"),
    (r"recessed|flush|in-ceiling", "Mount empotrado (flush)"),
    (r"pendant", "Mount pendant"),
    (r"corner", "Mount de esquina"),
    (r"parapet", "Mount de parapeto"),
    (r"wall\s*(?:&|and|/)\s*pole|pole\s*(?:&|and|/)\s*wall", "Mount pared/poste"),
    (r"pole", "Mount de poste"),
    (r"wall", "Mount de pared"),
    (r"ceiling", "Mount de cielo"),
    (r"back\s?box|backbox|conduit box", "Back box"),
    (r"junction|j-box|gang\s?box|gangbox|gangplate", "Caja de conexiones"),
    (r"dome cover|smoked dome|clear dome|bubble|\bdome\b.*\bcover|top cover|tinted", "Cubierta / domo"),
    (r"\bcover\b|skin|weathershield|weather cap|hood|face plate", "Cubierta / carcasa"),
    (r"housing|casing|enclosure", "Housing/carcasa"),
    (r"cap adapter", "Adaptador tipo cap"),
    (r"power supply|psu|power adapter", "Fuente de poder"),
    (r"\bcables?\b|patch", "Cableado"),
    (r"midspan|injector|\bpoe\b", "Inyector/convertidor PoE"),
    (r"adapter|adaptor|converter|coupler", "Adaptador / conversor"),
    (r"bracket|mount|stand|arm\b|plate", "Mount (otro)"),
]


def tipo_accesorio(nombre, subcategoria):
    n = (nombre or "").lower()
    for patron, tipo in TIPOS:
        if re.search(patron, n):
            return tipo
    return subcategoria or "Otro"


def es_iluminador(r):
    return bool(ILUMINADOR.search(r["nombre"])) and not PIEZA.search(r["nombre"])


ES_CAMARA = re.compile(r"\bcamera\b|megapixel|\b\d+\s?MP\b", re.I)
PIEZA_PARA = re.compile(r"\b(plate|mount|bracket|box|backbox|adapter|adaptor|housing|cover)\b[^.]*?\bfor\b", re.I)


def es_accesorio(r):
    if es_iluminador(r):
        return False
    if r["categoria"] == "Accesorio de instalacion" or r["subcategoria"] in SUB_ACCESORIO:
        return True
    if ES_CAMARA.search(r["nombre"]):
        return False
    # Del PDF de InVid quedaron soportes con categoria Camara ("Plate for
    # Dome to Attach to IVM-PM1"). En una camara solo cuenta si el nombre es
    # "<pieza> for ...": "4K IR Flush Mount Dome" es una camara.
    if r["categoria"] == "Camara":
        return bool(PIEZA_PARA.search(r["nombre"]))
    return bool(PIEZA.search(r["nombre"]))


def es_equipo(r):
    return (r["categoria"] in CAT_EQUIPO or es_iluminador(r)) and not es_accesorio(r)


# ---- Modelos de Axis: el numero de parte (02939-001) no aparece en los
# textos; aparece el nombre del modelo (Q6124-E). Se indexa el nombre de
# cada equipo Axis y se leen las menciones con sus abreviaturas.
AXIS_NOMBRE = re.compile(r"\bAXIS\s+([A-Z]{1,2}\d{3,4}[A-Z]?(?:-[A-Z0-9]+)?)(?:\s+(MK\s?I{1,3}|MKI{1,3}))?", re.I)
MK = re.compile(r"^\s*(?:MK\s?(I{1,3})\b)", re.I)


def mk_de(s):
    m = re.search(r"MK\s?(I{1,3})\b", s or "", re.I)
    return len(m.group(1)) if m else 0


def modelo_axis(nombre):
    m = AXIS_NOMBRE.search(nombre or "")
    if not m:
        return None, 0
    return m.group(1).upper(), mk_de(nombre)


MENCION = re.compile(
    r"\b([A-Z]{1,2})(\d{3,4})([A-Z]?)"            # P1355, Q3626, M3905
    r"((?:/\d{1,4})*)"                             # /8, /19, /6020
    r"((?:/?-[A-Z0-9]+)*)"                         # -E, /-E, -PLE, -R
    r"(?:\s(VE|LVE|PLE|PLVE|E|LE|R|V|LV)\b)?"      # "Q3626/8 VE"
    r"(?:\s?(MK\s?I{1,3}|MkI{1,3}|Mk\s?I{1,3}))?", re.I)


def menciones_axis(texto):
    """Devuelve [(modelo, mk, inicio, fin)]: cada modelo Axis que nombra el
    texto, con las abreviaturas expandidas ("Q3626/8 VE" -> Q3626-VE y
    Q3628-VE; "P1355/-E" -> P1355 y P1355-E)."""
    out = []
    encontradas = list(MENCION.finditer(texto or ""))
    for i, m in enumerate(encontradas):
        serie, num, letra, barras, sufijos, sufijo_esp, mk = m.groups()
        # "M4317/M4318-PLVE": el primero hereda el sufijo del siguiente.
        if not sufijos and not sufijo_esp and i + 1 < len(encontradas) and texto[m.end():m.end() + 1] == "/" \
                and encontradas[i + 1].start() == m.end() + 1:
            sufijos = encontradas[i + 1].group(5) or ""
        bases = [num + (letra or "")]
        for b in [x for x in (barras or "").split("/") if x]:
            bases.append(num[: len(num) - len(b)] + b)
        sufs = [s for s in re.findall(r"/?-([A-Z0-9]+)", sufijos or "", re.I)]
        con_barra = "/-" in (sufijos or "")
        if sufijo_esp:
            sufs.append(sufijo_esp)
        variantes = []
        for b in bases:
            nombre = (serie + b).upper()
            if not sufs:
                variantes.append(nombre)
            else:
                if con_barra:
                    variantes.append(nombre)
                for s in sufs:
                    variantes.append(nombre + "-" + s.upper())
        for v in dict.fromkeys(variantes):
            out.append((v, mk_de(mk or ""), m.start(), m.end()))
    return out


# ---- Numeros de parte (Hanwha, InVid, 2N): "XND-6010/6020R/8020R" hereda
# el prefijo de letras al numero siguiente.
PREFIJO = re.compile(r"^([A-Z]{2,}-)")
SKU_EMBEBIDO = re.compile(r"\b[A-Z0-9]{2,}(?:-[A-Z0-9]+)+\b")


def skus_en(frase, skus):
    encontrados, prefijo = [], None
    for trozo in re.split(r",| and |;", frase):
        for sub in trozo.split("/"):
            sub = sub.strip(" ()")
            if not sub:
                continue
            pm = PREFIJO.match(sub)
            if pm:
                prefijo, cand = pm.group(1), sub
            elif prefijo and re.match(r"^[A-Z0-9]+$", sub):
                cand = prefijo + sub
            else:
                cand = sub
            if cand.upper() in skus:
                encontrados.append(cand.upper())
    if not encontrados:
        encontrados = [t.upper() for t in SKU_EMBEBIDO.findall(frase) if t.upper() in skus]
    return list(dict.fromkeys(encontrados))


def frases(texto):
    return [(m.group(1), m.start(1)) for pat in TRIGGERS for m in pat.finditer(texto or "")]


def evidencia(texto, inicio, fin, ancho=70):
    a, b = max(0, inicio - ancho), min(len(texto), fin + ancho)
    s = texto[a:b].replace("\n", " ").strip()
    return ("..." if a > 0 else "") + s + ("..." if b < len(texto) else "")


def leer_catalogo(ruta):
    wb = openpyxl.load_workbook(ruta, read_only=True, data_only=True)
    filas = list(wb["Catalogo"].iter_rows(values_only=True))
    wb.close()
    I = {h: i for i, h in enumerate(filas[0])}
    out = []
    for r in filas[1:]:
        sku = r[I["Modelo / SKU"]]
        if not sku:
            continue
        out.append({
            "sku": str(sku).strip(), "nombre": str(r[I["Nombre de equipo/producto"]] or "").strip(),
            "marca": r[I["Marca"]] or "", "proveedor": r[I["Proveedor"]] or "",
            "categoria": r[I["Categoria"]] or "", "subcategoria": r[I["Subcategoria"]] or "",
            "descripcion": str(r[I["Descripcion"]] or ""),
        })
    return out


def construir(cat):
    por_sku = {}
    for r in cat:
        por_sku.setdefault(r["sku"].upper(), r)
    axis_por_modelo = collections.defaultdict(list)
    for r in cat:
        if r["marca"] == "Axis" and es_equipo(r):
            mod, mk = modelo_axis(r["nombre"])
            if mod:
                axis_por_modelo[mod].append((r, mk))

    pares = {}

    def agregar(equipo, acc, fuente, nota):
        if equipo["sku"].upper() == acc["sku"].upper():
            return
        clave = (equipo["sku"].upper(), acc["sku"].upper())
        if clave in pares:
            return
        pares[clave] = [equipo["sku"], equipo["nombre"], equipo["marca"],
                        acc["sku"], acc["nombre"], tipo_accesorio(acc["nombre"], acc["subcategoria"]), acc["marca"],
                        acc["proveedor"], fuente, nota]

    for r in cat:
        textos = [("nombre", r["nombre"]), ("descripcion", r["descripcion"])]
        lado_acc, lado_eq = es_accesorio(r), es_equipo(r)
        if not (lado_acc or lado_eq):
            continue
        for campo, texto in textos:
            if not texto:
                continue
            # 1a. numeros de parte dentro de las frases "for/compatible with"
            for frase, ini in frases(texto):
                for otro_sku in skus_en(frase, por_sku):
                    otro = por_sku[otro_sku]
                    pos = texto.upper().find(otro_sku, ini)
                    pos = pos if pos >= 0 else ini
                    nota = 'El %s de %s dice: "%s"' % (campo, r["sku"], evidencia(texto, pos, pos + len(otro_sku)))
                    if lado_acc and es_equipo(otro):
                        agregar(otro, r, FUENTE_EXACTA, nota)
                    elif lado_eq and es_accesorio(otro):
                        agregar(r, otro, FUENTE_EXACTA, nota)
            # 1b. modelos de Axis por nombre (solo desde el lado accesorio)
            if lado_acc and r["marca"] == "Axis":
                for mod, mk, a, b in menciones_axis(texto):
                    if not any(ini <= a <= ini + len(fr) + 1 for fr, ini in frases(texto)):
                        continue
                    # "...A1214 Network Door Controller Kit. AXIS TA1601 Mounting
                    # Plate is included in...": ya viene adentro, no se ofrece.
                    if re.search(r"is included in|included with", texto[b:b + 90], re.I):
                        continue
                    # "I7010-VE Safety" e "I7010-VE" son dos intercomunicadores
                    # con placas distintas: la palabra tiene que coincidir.
                    safety = bool(re.match(r"\s*Safety\b", texto[b:b + 12], re.I))
                    for equipo, mk_eq in axis_por_modelo.get(mod, []):
                        if mk and mk_eq != mk:
                            continue
                        if safety != bool(re.search(r"\bSafety\b", equipo["nombre"], re.I)):
                            continue
                        nota = 'El %s de %s dice: "%s"' % (campo, r["sku"], evidencia(texto, a, b))
                        if mk_eq and not mk:
                            nota += " (no dice si es Mk; el equipo es Mk %s)" % ("I" * mk_eq)
                        agregar(equipo, r, FUENTE_EXACTA, nota)

    # 2. familias revisadas a mano
    for acc_sku, regla, cita in FAMILIAS_VERIFICADAS:
        acc = por_sku.get(acc_sku.upper())
        if not acc:
            continue
        for r in cat:
            if r["marca"] != regla["marca"] or not es_equipo(r):
                continue
            if all(re.search(p, r["nombre"], re.I) for p in regla["nombre"]) and not any(re.search(p, r["nombre"], re.I) for p in regla["no"]):
                agregar(r, acc, FUENTE_FAMILIA, cita)

    # 3. cotizaciones reales (vacia, ver la nota)
    for eq_sku, acc_sku, nota in PARES_DE_COTIZACIONES:
        eq, acc = por_sku.get(eq_sku.upper()), por_sku.get(acc_sku.upper())
        if eq and acc:
            agregar(eq, acc, FUENTE_COTIZACION, nota)

    filas = sorted(pares.values(), key=lambda f: (str(f[2]), str(f[0]), str(f[5]), str(f[3])))
    return filas


# Lo que dice la "Guia de columnas" sobre esta pestana (lo escribe tambien
# escribir_matriz_accesorios.ps1, para que la guia no quede describiendo
# fuentes que ya no existen).
GUIA = {
    "descripcion": "Qué montura, base, lente o cubierta sirve para cada equipo (cámaras, intercomunicadores, "
                   "monitores). Una fila por par equipo–accesorio. La genera un script leyendo lo que el fabricante "
                   "escribe en su lista de precios: cada par trae en Notas la frase que lo respalda.",
    "Marca Accesorio": ["Marca del accesorio.",
                        "Casi siempre es la misma marca del equipo: los soportes rara vez sirven entre marcas."],
    "Fuente": ["De dónde salió el par: el fabricante nombra el modelo exacto, o nombra solo la familia "
               "(\"for Paramont PTZ Cameras\").",
               "DICE CUÁNTO CONFIAR. Si dice que nombra la familia, confirmá el encaje con el proveedor antes de cotizar."],
    "Notas": ["La frase del fabricante que respalda el par, y avisos (por ejemplo, si no dice la versión Mk).",
              "Para revisar el par sin abrir la lista de precios."],
}


def main(ruta, salida):
    cat = leer_catalogo(ruta)
    filas = construir(cat)
    json.dump({"encabezados": HEADERS, "filas": filas, "guia": GUIA}, open(salida, "w", encoding="utf-8"), ensure_ascii=False)
    print("filas del catalogo: %d" % len(cat))
    print("pares: %d | equipos distintos: %d | accesorios distintos: %d" % (
        len(filas), len({f[0] for f in filas}), len({f[3] for f in filas})))
    for clave, n in collections.Counter(f[8] for f in filas).most_common():
        print("  %5d  %s" % (n, clave))
    print("por marca del equipo:", dict(collections.Counter(f[2] for f in filas).most_common()))
    print("tipos:", dict(collections.Counter(f[5] for f in filas).most_common()))
    print("escrito: %s" % salida)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('Uso: python generar_matriz_accesorios.py "<catalogo.xlsx>" "<salida.json>"')
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
