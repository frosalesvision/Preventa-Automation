# -*- coding: utf-8 -*-
"""Linea base de los casos patron: que tan cerca queda el plugin de 10 cotizaciones reales.

Existe porque Fabian pidio (2026-09-25) al menos 10 casos patron, la mayoria
de camaras, y los cinco primeros se hicieron a mano: sirvieron para
encontrar problemas, pero no se pueden repetir igual. Esto si. Elige los 10
casos con una regla fija, guarda cuales eligio, y la proxima corrida los
reusa con --rehacer. La diferencia entre dos corridas es cuanto mejoro el
plugin.

QUE MIDE, por cada linea de equipo de cada cotizacion:

  ENCONTRADO        el modelo esta en el catalogo, exacto o con la busqueda
                    tolerante de buscar-equipo (sin prefijo de marca, o por
                    prefijo). Se compara ademas el costo.
  FALTA, CONOCIDA   el modelo no esta, pero su marca ya figura en la pestana
                    "Marcas por cargar". Es un hueco sabido: NO es un error.
                    i-PRO, la marca mas cotizada, esta en este grupo.
  FALTA, NUEVA      el modelo no esta y su marca tampoco esta en la lista.
                    Esto es lo que hay que mirar.

Y aparte, de lo que falta: cuanto tiene un EQUIVALENTE en la misma
subcategoria del catalogo, que el plugin podria ofrecer como alternativa si
el asesor lo acepta (R18).

Por cotizacion mide tambien los porcentajes contra los defaults del machote,
y el impuesto al cliente contra lo que el plugin propondria.

Se compara contra TODAS las versiones guardadas y se reporta la mejor: el
propio equipo cotiza alternativas (caso #5), asi que acertarle a cualquiera
de sus versiones es acertar (R18).

Lo que NO mide: si el plugin leeria bien la solicitud del cliente. Eso exige
correr el plugin sobre los documentos del cliente, con una persona al lado.

Solo lee. La seleccion se guarda en medicion-casos-patron.json, que lleva
rutas con nombres de clientes y esta en .gitignore.

Uso:
    python scripts/casos-patron-linea-base.py            elige y mide
    python scripts/casos-patron-linea-base.py --rehacer  mide los mismos 10
"""

import collections
import importlib.util
import json
import os
import re
import sys
import warnings

warnings.filterwarnings("ignore")

try:
    import openpyxl
except ImportError:
    sys.exit("Falta openpyxl.  Instalalo con:  pip install openpyxl")

AQUI = os.path.dirname(os.path.abspath(__file__))


def _cargar(nombre, archivo):
    spec = importlib.util.spec_from_file_location(nombre, os.path.join(AQUI, archivo))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


mm = _cargar("marcas", "medir-marcas-faltantes.py")
mi = _cargar("impuesto", "medir-impuesto-al-cliente.py")
ma = _cargar("accesorios", "medir-accesorios-requeridos.py")
sys.path.insert(0, AQUI)
import taxonomia  # noqa: E402

SALIDA = os.path.join(AQUI, "..", "medicion-casos-patron.json")

# Los defaults del machote. Que una cotizacion use otro valor NO es un error
# del plugin (R17: son celdas editables); se mide para saber cuantas celdas
# tiene que tocar el asesor.
DEFAULTS = {"transporte": 0.10, "imprevistos": 0.03, "iva": 0.13,
            "dai": 0.15, "administracion": 0.03, "margen": 0.274}
ETIQUETAS = {"transporte": "transporte", "imprevistos": "imprevistos",
             "iva": "iva", "dai": "dai", "administracion": "administracion",
             "margen gv": "margen", "margen": "margen"}

CUANTOS = {"video": 7, "acceso": 1, "intrusion": 1, "incendio": 1}

# Los cinco casos patron ya hechos a mano, para no repetirlos. Se reconocen
# por el nombre de su carpeta (sin nombre de cliente).
YA_HECHOS = [r"#\s*6\s*-\s*2026\s*cctv\s*-\s*etapa\s*1", r"#\s*3-2026\s*smart\s*city",
             r"#\s*10-2026\s*incendio\s*escuelas"]

RX_CARPETA = re.compile(r"cotizaci.n\s*#?\s*\d+\s*-\s*2026", re.I)
RX_ENTRADA = re.compile(r"visita t.cnica|requerimiento|especificaci|pliego|solicitud|"
                        r"licitaci|cartel", re.I)
# Lineas que no son equipo: servicios, mano de obra, materiales genericos.
RX_SERVICIO = re.compile(r"^\s*(mano de obra|instalaci|configuraci|programaci|transporte|"
                         r"imprevist|materiales?\b|vi[aá]tic|servicio|soporte t[eé]cnico|"
                         r"mantenimiento|garant[ií]a|capacitaci|puesta en marcha|ingenier|"
                         r"dise[nñ]o|visita|flete|env[ií]o|cableado|canalizaci|horas?\b|"
                         r"alimentaci[oó]n|hospedaje|combustible|gvcr)", re.I)
NO_EQUIPO = re.compile(mm.NO_EQUIPO.pattern + r"|materiales", re.I)

# Tipo de cotizacion por las lineas que trae
FAMILIA = {
    "video": {"Camara", "NVR", "DVR"},
    "acceso": {"Cerradura magnetica", "Lectora", "Controladora de acceso", "Boton de salida"},
    "incendio": {"Panel de incendio", "Detector de incendio", "Estacion manual"},
}
RX_INTRUSION = re.compile(r"sensor de movimiento|detector de movimiento|contacto magn|"
                          r"teclado|keypad|\bpir\b|power\s*g|\bhs2\d|\bpg9\d|panel de alarma|"
                          r"paradox|\bdsc\b", re.I)


def matrices_y_entrada(carpeta):
    mats, docs = [], []
    for r2, d2, f2 in os.walk(carpeta):
        es_entrada = RX_ENTRADA.search(os.path.relpath(r2, carpeta))
        for f in f2:
            p = os.path.join(r2, f)
            try:
                sz = os.path.getsize(p)
            except OSError:
                continue
            lf = f.lower()
            if f.startswith("~$"):
                continue
            if lf.endswith((".xlsx", ".xlsm")) and re.search(r"matriz|oferta", lf) and sz > 40000:
                mats.append(p)
            elif es_entrada and sz > 15000 and lf.endswith(
                    (".pdf", ".docx", ".doc", ".xlsx", ".jpg", ".png", ".msg")):
                docs.append(p)
    return sorted(mats), docs


def leer_version(p):
    """Lineas de equipo, porcentajes e impuesto de UNA version de la matriz."""
    try:
        wb = openpyxl.load_workbook(p, read_only=True, data_only=True)
    except Exception:
        return None
    lineas, pct, sub, imp = [], {}, None, None
    try:
        for nombre in wb.sheetnames:
            try:
                filas = list(wb[nombre].iter_rows(min_row=1, max_row=260, values_only=True))
            except Exception:
                continue
            if re.search(r"cotiza", nombre, re.I) and "financ" not in nombre.lower() and sub is None:
                s_, i_ = mi.totales_de(filas[:90])
                if s_:
                    sub, imp = s_, i_
                continue
            if mm.PLANTILLA.search(nombre) or NO_EQUIPO.search(nombre):
                continue
            cab = mm.encabezado(filas)
            if not cab:
                continue
            n0, cd, cq, cc = cab
            if not pct:
                for fila in filas[:n0 + 1]:
                    for c, v in enumerate(fila[:24]):
                        k = ETIQUETAS.get(mm.norm(v))
                        if not k or k in pct:
                            continue
                        for fila2 in filas[filas.index(fila) + 1: filas.index(fila) + 3]:
                            w = fila2[c] if len(fila2) > c else None
                            if isinstance(w, (int, float)) and 0 <= w < 1.5:
                                pct[k] = float(w)
                                break
            vacias = 0
            for fila in filas[n0 + 1:]:
                desc = fila[cd] if len(fila) > cd else None
                costo = fila[cc] if len(fila) > cc else None
                if not desc or not isinstance(costo, (int, float)) or costo <= 0:
                    vacias += 1
                    if vacias > 14:
                        break
                    continue
                vacias = 0
                texto = str(desc).strip()
                if mm.norm(texto).startswith(("total", "subtotal", "seccion")):
                    continue
                if RX_SERVICIO.search(texto):
                    continue
                qty = fila[cq] if (cq is not None and len(fila) > cq) else 1
                lineas.append((texto, float(costo),
                               float(qty) if isinstance(qty, (int, float)) and qty > 0 else 1.0))
    finally:
        wb.close()
    return {"lineas": lineas, "pct": pct, "sub": sub, "imp": imp}


def tipo_de_cotizacion(lineas, nombre_carpeta):
    n = mm.norm(nombre_carpeta)
    if "incendio" in n:
        return "incendio"
    if "acceso" in n:
        return "acceso"
    if re.search(r"alarma|intrusi", n):
        return "intrusion"
    cuenta = collections.Counter()
    for texto, _, _ in lineas:
        t = ma.tipo_de(texto)
        for fam, tipos in FAMILIA.items():
            if t in tipos:
                cuenta[fam] += 1
        if RX_INTRUSION.search(texto):
            cuenta["intrusion"] += 1
    if re.search(r"cctv|c[aá]mara|video", n):
        cuenta["video"] += 3
    return cuenta.most_common(1)[0][0] if cuenta else None


def seleccionar():
    cands = []
    for root, dirs, files in os.walk(mm.CLIENTES):
        if "00_IA_PREVENTAS" in root:
            continue
        b = os.path.basename(root)
        if not RX_CARPETA.search(b):
            continue
        if any(re.search(x, b, re.I) for x in YA_HECHOS):
            continue
        mats, docs = matrices_y_entrada(root)
        if not mats or not docs:
            continue
        versiones = [v for v in (leer_version(p) for p in mats) if v]
        if not versiones:
            continue
        mejor = max(versiones, key=lambda v: len(v["lineas"]))
        if len(mejor["lineas"]) < 5:
            continue
        tipo = tipo_de_cotizacion(mejor["lineas"], b)
        if not tipo:
            continue
        cands.append({"carpeta": root, "tipo": tipo, "lineas": len(mejor["lineas"]),
                      "versiones": len(mats), "documentos": len(docs)})
    elegidos = []
    for tipo, n in CUANTOS.items():
        del_tipo = sorted([c for c in cands if c["tipo"] == tipo], key=lambda c: -c["lineas"])
        elegidos += del_tipo[:n]
    # Si algun tipo no tiene casos (el 2026-09-25 no hubo NINGUNA cotizacion de
    # intrusion con documentos del cliente), se completa con las mas grandes
    # que queden, de cualquier tipo: primero video, que es lo que mas se cotiza.
    faltan = sum(CUANTOS.values()) - len(elegidos)
    if faltan > 0:
        ya = {c["carpeta"] for c in elegidos}
        resto = [c for c in cands if c["carpeta"] not in ya]
        resto.sort(key=lambda c: (c["tipo"] != "video", -c["lineas"]))
        elegidos += resto[:faltan]
    resumen = collections.Counter(c["tipo"] for c in cands)
    return elegidos, dict(resumen)


def leer_catalogo():
    wb = openpyxl.load_workbook(mm.CATALOGO, read_only=True, data_only=True)
    filas = list(wb["Catalogo"].iter_rows(min_row=2, values_only=True))
    conocidas_marca, conocidas_pref = set(), set()
    if "Marcas por cargar" in wb.sheetnames:
        for f in wb["Marcas por cargar"].iter_rows(min_row=6, values_only=True):
            if not f or not f[1]:
                continue
            if str(f[2] or "").startswith("Marca"):
                conocidas_marca.add(str(f[1]))
            else:
                conocidas_pref.add(str(f[1]).upper())
            if f[3]:
                conocidas_marca.add(str(f[3]))
    regimen = {}
    # "Clientes" desde el 2026-10-06; las columnas A..F no cambiaron
    hoja_reg = next((n for n in ("Clientes", "Regimen Fiscal Clientes") if n in wb.sheetnames), None)
    if hoja_reg:
        for f in wb[hoja_reg].iter_rows(min_row=5, values_only=True):
            if not f or not f[0]:
                break
            regimen[mm.norm(f[0])] = (f[2], str(f[4] or ""))
    wb.close()
    idx, cubos, por_sub = {}, collections.defaultdict(list), collections.Counter()
    for r in filas:
        k = mm.clave(r[2])
        # Una fila cuyo "modelo" es una palabra (LICENCIA, COMPACT) emparejaba
        # con cualquier linea que dijera "licencia" o "compacto": en la primera
        # corrida de esta linea base fueron 12 de 31 coincidencias. No se usa.
        if k and not es_modelo(str(r[2])):
            por_sub[(r[3], r[4])] += 1
            continue
        # Desde el 2026-09-28: col. 9 (r[8]) = Precio de compra GV, formula que
        # ya es "el precio con que se cotiza"; col. 11 (r[10]) = Precio dealer;
        # col. 12 (r[11]) = Descuento del proveedor. Es COSTO de verdad si hay
        # dealer o si el descuento del proveedor es un numero (tambien 0%).
        num = lambda v: isinstance(v, (int, float))
        es_costo = (len(r) > 10 and num(r[10])) or (len(r) > 11 and num(r[11]))
        costo = r[8] if len(r) > 8 and num(r[8]) else (r[6] if num(r[6]) else None)
        if k and k not in idx:
            # (precio con que se cotizaria, si ese precio es un COSTO de verdad)
            idx[k] = (costo, es_costo)
            if len(k) >= 6:
                cubos[k[:5]].append(k)
        por_sub[(r[3], r[4])] += 1
    return idx, cubos, por_sub, conocidas_marca, conocidas_pref, regimen


# Lo que parece modelo pero es una especificacion: 5MP, IP67, 4K, CAT6, 12V...
RX_ESPEC = re.compile(r"^(\d+(\.\d+)?(MP|K|TB|GB|MB|MM|V|W|A|VA|KVA|HZ|FPS|MTS?|M|CH|P)|"
                      r"IP-?\d+|IK-?\d+|CAT-?\d+E?|RJ-?\d+|H\.?26\d|POE\+*|\d+X\d+)$", re.I)


def es_modelo(tok):
    """Un modelo mezcla letras y numeros (WV-S1136), o es una sigla con guion
    y letras a los dos lados (KI-OSD). Una palabra suelta no es un modelo."""
    t = tok.strip(".-/[]()")
    if len(t) < 4 or RX_ESPEC.match(t):
        return False
    tiene_d = any(ch.isdigit() for ch in t)
    tiene_l = any(ch.isalpha() for ch in t)
    if tiene_d and tiene_l:
        return True
    # numero de parte solo con digitos y guion: Simplex 4098-9714
    if re.match(r"^\d{3,5}-\d{3,5}$", t):
        return True
    # siglas con guiones, sin digitos: KI-OSD, WRR-P-HDDCRDL (Hanwha)
    return bool(re.match(r"^[A-Z]{2,}(-[A-Z0-9]+)+$", t)) and len(t) >= 5


def buscar(texto, idx, cubos):
    """Como buscar-equipo: exacto, sin prefijo de marca, y por prefijo.

    Se usa SOLO EL PRIMER modelo de la linea. Un accesorio suele nombrar la
    camara para la que sirve ("cable ... for WV-S2536LNA"), y buscar en todos
    los tokens encontraba la camara en vez del accesorio: es el mismo error
    que H-14 tenia en el catalogo.
    """
    modelos = [t for t in mm.RX_TOKEN.findall(texto) if es_modelo(t)]
    if not modelos:
        return None, None
    t = mm.clave(modelos[0])
    if t in idx:
        return "exacto", t
    if t.startswith("ED") and t[2:] in idx:
        return "sin prefijo de marca", t[2:]
    if len(t) >= 6:
        for k in cubos.get(t[:5], ()):
            if t.startswith(k) or k.startswith(t):
                return "por prefijo", k
    return None, None


def marca_de(texto):
    for m, rx in mm.RX_MARCAS.items():
        if rx.search(texto):
            return m, None
    for tok in mm.RX_TOKEN.findall(texto):
        p = mm.prefijo(tok)
        if p:
            return None, p
    return None, None


def medir_caso(caso, cat):
    idx, cubos, por_sub, con_marca, con_pref, regimen = cat
    mats, docs = matrices_y_entrada(caso["carpeta"])
    versiones = [v for v in (leer_version(p) for p in mats) if v]
    resultados = []
    for v in versiones:
        c = collections.Counter()
        costos_ok = costos_n = 0
        for texto, costo, qty in v["lineas"]:
            c["lineas"] += 1
            modo, k = buscar(texto, idx, cubos)
            if modo:
                c["encontrado"] += 1
                c["enc_" + modo] += 1
                ref, es_costo = idx.get(k, (None, False))
                if isinstance(ref, (int, float)) and ref > 0:
                    # Solo se compara contra un COSTO de verdad. Contra un precio
                    # de lista el resultado ya se sabe: sale alrededor de la
                    # mitad (R4), y contarlo como fallo seria medir dos veces
                    # lo mismo.
                    if es_costo:
                        costos_n += 1
                        if abs(costo / ref - 1) <= 0.05:
                            costos_ok += 1
                    else:
                        c["solo_lista"] += 1
                        c["ratios_lista"] = c.get("ratios_lista", "") + "%.3f;" % (costo / ref)
                continue
            m, p = marca_de(texto)
            if (m and m in con_marca) or (p and p in con_pref):
                c["falta_conocida"] += 1
            elif m or p:
                c["falta_marca_fuera"] += 1
            else:
                # "Gabinete exterior IP66", "Breaker de 15 A", "patch cord": no
                # hay marca que buscar. Se ofrece por funcion o no se ofrece.
                c["falta_generica"] += 1
            try:
                ca, su, _ = taxonomia.clasificar(texto, None)
            except Exception:
                ca, su = "Sin clasificar", ""
            if ca != "Sin clasificar" and por_sub.get((ca, su), 0) > 0:
                c["con_equivalente"] += 1
        c["costos_n"], c["costos_ok"] = costos_n, costos_ok
        pct_ok = sum(1 for k, d in DEFAULTS.items()
                     if k in v["pct"] and abs(v["pct"][k] - d) <= 0.006)
        resultados.append((c, v, pct_ok))
    if not resultados:
        return None
    # la mejor version: la que mas lineas encontraria el plugin, en proporcion
    c, v, pct_ok = max(resultados, key=lambda x: (x[0]["encontrado"] / max(1, x[0]["lineas"]),
                                                  x[0]["lineas"]))
    tasa = round(100.0 * (v["imp"] or 0) / v["sub"], 2) if v["sub"] else None
    if tasa is not None and not (-1 <= tasa <= 40):
        # subtotal en dolares e impuesto en colones, o al reves: la cotizacion
        # trae el dato mal y no hay contra que comparar
        tasa = "invalido"
    cliente = os.path.relpath(caso["carpeta"], mm.CLIENTES).split(os.sep)[0]
    reg = regimen.get(mm.norm(cliente))
    # "13% ESTANDAR" (2026-10-12) es el 13% que se le pone a quien no se
    # pudo confirmar: el plugin lo propone y pregunta, como sin tabla.
    if reg and "NO CONFIRMADO" not in reg[1] and not reg[1].startswith("13% ESTANDAR") \
            and isinstance(reg[0], (int, float)):
        propone = round(reg[0] * 100, 2)
        fuente = "tabla de regimen"
    else:
        propone = 13.0
        fuente = "pregunta, 13% recomendado"
    return {"c": dict(c), "pct": v["pct"], "pct_ok": pct_ok, "tasa_real": tasa,
            "tasa_propuesta": propone, "fuente_tasa": fuente,
            "versiones": len(versiones), "documentos": len(docs)}


def main():
    rehacer = "--rehacer" in sys.argv
    if rehacer and os.path.exists(SALIDA):
        previo = json.load(open(SALIDA, encoding="utf-8"))
        elegidos, resumen = previo["casos"], previo.get("candidatos_por_tipo", {})
        print("reusando los %d casos de la corrida del %s" % (len(elegidos), previo.get("fecha", "?")))
    else:
        print("eligiendo casos entre las cotizaciones 2026 con documentos del cliente...")
        elegidos, resumen = seleccionar()
        print("  candidatos por tipo: %s" % resumen)
    print("leyendo el catalogo...")
    cat = leer_catalogo()
    print("  modelos: %d   marcas conocidas por cargar: %d   prefijos: %d"
          % (len(cat[0]), len(cat[3]), len(cat[4])))

    filas, tot = [], collections.Counter()
    for i, caso in enumerate(elegidos, start=1):
        r = medir_caso(caso, cat)
        if not r:
            continue
        c = r["c"]
        for k, v in c.items():
            if k == "ratios_lista":
                tot_txt = tot.get("ratios_lista", "")
                tot["ratios_lista"] = tot_txt + v
            else:
                tot[k] += v
        tot["pct_ok"] += r["pct_ok"]
        tot["pct_n"] += 6
        if r["tasa_real"] == "invalido":
            tot["tasa_invalida"] += 1
        elif r["tasa_real"] is not None:
            tot["tasa_n"] += 1
            if abs(r["tasa_real"] - r["tasa_propuesta"]) < 0.5:
                tot["tasa_ok"] += 1
            elif r["fuente_tasa"].startswith("pregunta"):
                tot["tasa_preguntada"] += 1
        filas.append(("L%d" % i, caso["tipo"], c, r))

    print()
    print("=" * 96)
    print(" LINEA BASE DE LOS CASOS PATRON")
    print("=" * 96)
    print("%-4s %-9s %4s %6s %6s %6s %6s %6s %6s %6s %6s %s" % (
        "caso", "tipo", "vers", "lineas", "encont", "costo", "falta", "falta", "falta",
        "equiv", "% ok", "impuesto real / propuesto"))
    print("%-4s %-9s %4s %6s %6s %6s %6s %6s %6s %6s %6s" % (
        "", "", "", "", "", "=5%", "conoc", "fuera", "gener", "", "de 6"))
    print("-" * 96)
    for etq, tipo, c, r in filas:
        costo = "%d/%d" % (c.get("costos_ok", 0), c.get("costos_n", 0))
        if r["tasa_real"] == "invalido":
            tasa = "dato mal en la cotizacion (monedas mezcladas)"
        elif r["tasa_real"] is None:
            tasa = "sin dato"
        else:
            tasa = "%5.1f%% / %4.1f%% (%s)" % (r["tasa_real"], r["tasa_propuesta"],
                                              r["fuente_tasa"])
        print("%-4s %-9s %4d %6d %6d %6s %6d %6d %6d %6d %6s %s" % (
            etq, tipo, r["versiones"], c.get("lineas", 0), c.get("encontrado", 0), costo,
            c.get("falta_conocida", 0), c.get("falta_marca_fuera", 0),
            c.get("falta_generica", 0), c.get("con_equivalente", 0),
            "%d/6" % r["pct_ok"], tasa))
    print("-" * 96)
    L = tot["lineas"] or 1
    falta = tot["falta_conocida"] + tot["falta_marca_fuera"] + tot["falta_generica"]
    print()
    print("TOTAL sobre %d lineas de equipo en %d casos:" % (tot["lineas"], len(filas)))
    print("  encontradas por el plugin       : %4d   %5.1f%%" % (tot["encontrado"], 100.0 * tot["encontrado"] / L))
    for modo in ("exacto", "sin prefijo de marca", "por prefijo"):
        print("     %-28s: %4d" % (modo, tot["enc_" + modo]))
    print("     el catalogo trae un COSTO real: %d  -> coincide a +-5%%: %d"
          % (tot["costos_n"], tot["costos_ok"]))
    if tot["solo_lista"]:
        rs = sorted(float(x) for x in tot["ratios_lista"].split(";") if x)
        cerca = sum(1 for x in rs if abs(x - 1) <= 0.12)
        print("     el catalogo trae un solo precio sin tipo: %d  -> mediana %.2fx; a +-12%%: %d"
              % (tot["solo_lista"], rs[len(rs) // 2], cerca))
    print("  faltan, marca YA en la lista    : %4d   %5.1f%%   <- hueco conocido, no es error"
          % (tot["falta_conocida"], 100.0 * tot["falta_conocida"] / L))
    print("  faltan, marca FUERA de la lista : %4d   %5.1f%%   <- marca poco usada, revisar"
          % (tot["falta_marca_fuera"], 100.0 * tot["falta_marca_fuera"] / L))
    print("  faltan, linea GENERICA          : %4d   %5.1f%%   <- sin marca ni modelo"
          % (tot["falta_generica"], 100.0 * tot["falta_generica"] / L))
    print("  de lo que falta, con equivalente en la misma subcategoria: %d de %d"
          % (tot["con_equivalente"], falta))
    print("  porcentajes iguales al default  : %d de %d" % (tot["pct_ok"], tot["pct_n"]))
    print("  impuesto al cliente acertado    : %d de %d   (%d mas se preguntan y el asesor corrige)"
          % (tot["tasa_ok"], tot["tasa_n"], tot["tasa_preguntada"]))
    if tot["tasa_invalida"]:
        print("     con el dato mal en la cotizacion (monedas mezcladas): %d, no se cuentan"
              % tot["tasa_invalida"])

    import datetime
    json.dump({"fecha": datetime.date.today().isoformat(), "casos": elegidos,
               "candidatos_por_tipo": resumen,
               "resultados": [{"caso": e, "tipo": t, "conteo": c,
                               "porcentajes": r["pct"], "tasa_real": r["tasa_real"],
                               "tasa_propuesta": r["tasa_propuesta"]}
                              for e, t, c, r in filas],
               "totales": dict(tot)},
              open(SALIDA, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print()
    print("detalle y seleccion en medicion-casos-patron.json (no va a git: lleva rutas de clientes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
