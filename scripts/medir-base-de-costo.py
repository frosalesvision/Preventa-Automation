# -*- coding: utf-8 -*-
"""Mide con que precio se llena de verdad la columna de costo de las matrices.

Existe por el caso patron #3 (2026-09-24). Ahi aparecio que el "Costo Unit"
de una cotizacion ganada coincidia al centavo con el precio DEALER del
catalogo, no con el MSRP -- al reves de lo que dicen hoy los encabezados del
catalogo. Pero era UN caso, y una golondrina no hace verano.

Esto lo cuenta sobre todas las matrices legibles. Por cada linea de equipo
busca el modelo dentro de la descripcion, lo ubica en el catalogo y compara
el costo unitario contra las dos columnas de precio.

La pregunta que responde es una sola: cuando el equipo llena el costo de una
matriz, esta copiando el precio dealer o el MSRP?

Solo lee. No escribe en ninguna matriz ni en el catalogo.

Uso:
    python scripts/medir-base-de-costo.py
    python scripts/medir-base-de-costo.py --limite 80     (prueba rapida)
"""

import collections
import json
import os
import re
import sys
import unicodedata
import warnings

warnings.filterwarnings("ignore")

try:
    import openpyxl
except ImportError:
    sys.exit("Falta openpyxl.  Instalalo con:  pip install openpyxl")

CLIENTES = os.path.expandvars(
    r"%USERPROFILE%\OneDrive - GRUPO VISION - DYNAMIC\Accesos directos"
    r"\Archivos de Info Costa Rica - CLIENTES"
)
CATALOGO = os.path.join(CLIENTES, "00_IA_PREVENTAS", "Preventas", "Catalogo",
                        "Catalogo de productos por proveedor.xlsx")

COL_NOMBRE, COL_SKU, COL_PROVEEDOR = 0, 2, 5
COL_MSRP, COL_DEALER = 6, 8

# Un modelo mas corto que esto se confunde con cualquier cosa.
MIN_SKU = 5
# Dos precios se consideran el mismo si difieren menos que esto.
TOLERANCIA = 0.005

# Lo que en una descripcion tiene pinta de modelo: un token de letras, digitos
# y separadores.  Se exige despues que mezcle letra y numero.
RX_TOKEN = re.compile(r"[A-Za-z0-9][A-Za-z0-9\-\./]{3,}")


def norm(s):
    if s is None:
        return ""
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", s.lower()).strip()


def clave(s):
    return re.sub(r"[^A-Z0-9]", "", str(s or "").upper())


def es_modelo(k):
    """Un modelo de verdad mezcla letras y numeros.

    Sin esto, filas del catalogo cuyo "modelo" es una palabra --LICENCIA,
    ADAPTADOR-- cotejan contra cualquier descripcion.  En la prueba corta eso
    hizo comparar una licencia de $6.536 contra una fila de $138.
    """
    return (len(k) >= MIN_SKU
            and re.search(r"\d", k) is not None
            and re.search(r"[A-Z]", k) is not None)


def cargar_catalogo():
    """Indexa el catalogo por SKU exacto."""
    wb = openpyxl.load_workbook(CATALOGO, read_only=True, data_only=True)
    filas = list(wb["Catalogo"].iter_rows(min_row=2, values_only=True))
    wb.close()
    idx = {}
    for r in filas:
        k = clave(r[COL_SKU])
        if not es_modelo(k):
            continue
        msrp = r[COL_MSRP] if isinstance(r[COL_MSRP], (int, float)) else None
        dealer = r[COL_DEALER] if isinstance(r[COL_DEALER], (int, float)) else None
        if msrp is None and dealer is None:
            continue
        # si el mismo modelo esta dos veces, gana la que tenga los dos precios
        if k in idx and idx[k][0] is not None and idx[k][1] is not None:
            continue
        idx[k] = (msrp, dealer, str(r[COL_PROVEEDOR] or ""))
    return idx, len(idx)


def buscar_modelo(desc, idx):
    """El modelo del catalogo que aparezca como TOKEN dentro de la descripcion.

    Se coteja token por token, no por subcadena: buscar el SKU como subcadena
    hacia que cualquier modelo corto apareciera dentro de numeros sueltos del
    texto.  Si hay varios, gana el mas largo, que es el mas especifico.
    """
    mejor = None
    for t in RX_TOKEN.findall(str(desc)):
        k = clave(t)
        if not es_modelo(k):
            continue
        hit = idx.get(k)
        if hit and (mejor is None or len(k) > len(mejor[0])):
            mejor = (k,) + hit
    return mejor


def encabezado_de_equipo(ws):
    """Ubica la fila de encabezado y las columnas de descripcion, qty y costo.

    No se busca por nombre de hoja: los archivos no siguen ninguna convencion
    (MATRIZ PROVEEDOR, Camaras, Productos 2, Estudio Mercado...).  Se busca
    por contenido.
    """
    maxr = min(ws.max_row or 1, 12)
    maxc = min(ws.max_column or 1, 24)
    for r in range(1, maxr + 1):
        cd = cq = cc = None
        for c in range(1, maxc + 1):
            t = norm(ws.cell(r, c).value)
            if not t or len(t) > 26:
                continue
            if cd is None and ("descripcion" in t or "description" in t):
                cd = c
            elif cq is None and t in ("qty", "cant", "cantidad", "cant."):
                cq = c
            elif cc is None and ("costo unit" in t or "costo unitario" in t
                                 or t in ("costo u.", "costo u")):
                cc = c
        if cd and cc:
            return r, cd, cq, cc
    return None


def lineas_de(ws, cabecera, limite=200):
    r0, cd, cq, cc = cabecera
    out = []
    vacias = 0
    for r in range(r0 + 1, min(ws.max_row or r0, r0 + limite) + 1):
        desc = ws.cell(r, cd).value
        costo = ws.cell(r, cc).value
        if not desc or not isinstance(costo, (int, float)) or costo <= 0:
            vacias += 1
            if vacias > 12:
                break
            continue
        vacias = 0
        t = norm(desc)
        if t.startswith(("total", "subtotal", "seccion", "sub total")):
            continue
        qty = ws.cell(r, cq).value if cq else None
        out.append((str(desc), float(costo),
                    float(qty) if isinstance(qty, (int, float)) else None))
    return out


def main():
    limite = None
    if "--limite" in sys.argv:
        limite = int(sys.argv[sys.argv.index("--limite") + 1])

    print("indexando el catalogo...")
    idx, n_sku = cargar_catalogo()
    print("  %d modelos con precio utilizable" % n_sku)

    print("buscando matrices...")
    archivos = []
    for root, dirs, files in os.walk(CLIENTES):
        if "00_IA_PREVENTAS" in root:
            continue
        for f in files:
            if f.startswith("~$") or not f.lower().endswith((".xlsx", ".xlsm")):
                continue
            if not re.search(r"matriz|oferta", f, re.I):
                continue
            p = os.path.join(root, f)
            try:
                if os.path.getsize(p) < 40000:   # marcador de OneDrive
                    continue
            except OSError:
                continue
            archivos.append(p)
    if limite:
        archivos = archivos[:limite]
    print("  %d matrices descargadas" % len(archivos))

    cta = collections.Counter()
    ejemplos = collections.defaultdict(list)
    por_proveedor = collections.defaultdict(collections.Counter)
    ratios = []
    leidas = 0

    for i, p in enumerate(archivos, start=1):
        if i % 40 == 0:
            print("    %d/%d   lineas cotejadas: %d" % (i, len(archivos), cta["cotejadas"]))
        try:
            wb = openpyxl.load_workbook(p, read_only=True, data_only=True)
        except Exception:
            cta["ilegibles"] += 1
            continue
        leidas += 1
        try:
            for nombre in wb.sheetnames:
                try:
                    ws = wb[nombre]
                    cab = encabezado_de_equipo(ws)
                    if not cab:
                        continue
                    for desc, costo, qty in lineas_de(ws, cab):
                        cta["lineas"] += 1
                        hit = buscar_modelo(desc, idx)
                        if not hit:
                            cta["sin_modelo"] += 1
                            continue
                        sku, msrp, dealer, prov = hit
                        # Solo decide la comparacion cuando existen LOS DOS
                        # precios.  Si el proveedor no tiene dealer cargado,
                        # cualquier coincidencia es MSRP por descarte y el
                        # conteo saldria sesgado.
                        if msrp is None or dealer is None:
                            cta["un_solo_precio"] += 1
                            continue
                        cta["cotejadas"] += 1
                        es_d = abs(costo - dealer) <= TOLERANCIA * max(costo, dealer)
                        es_m = abs(costo - msrp) <= TOLERANCIA * max(costo, msrp)
                        if es_d and es_m:
                            k = "ambos_iguales"
                        elif es_d:
                            k = "DEALER"
                        elif es_m:
                            k = "MSRP"
                        else:
                            k = "ninguno"
                            ratios.append(costo / msrp)
                        cta[k] += 1
                        por_proveedor[prov][k] += 1
                        if len(ejemplos[k]) < 4:
                            ejemplos[k].append((sku, costo, msrp, dealer))
                except Exception:
                    continue
        finally:
            wb.close()

    print()
    print("=" * 68)
    print(" CON QUE PRECIO SE LLENA LA COLUMNA DE COSTO")
    print("=" * 68)
    print("matrices leidas: %d   ilegibles: %d" % (leidas, cta["ilegibles"]))
    print("lineas de equipo: %d" % cta["lineas"])
    print("  sin modelo reconocible en la descripcion: %d" % cta["sin_modelo"])
    print("  con modelo pero un solo precio en el catalogo: %d" % cta["un_solo_precio"])
    print("  COMPARABLES (el catalogo tiene los dos precios): %d" % cta["cotejadas"])
    print()
    tot = cta["cotejadas"] or 1
    for k in ("DEALER", "MSRP", "ambos_iguales", "ninguno"):
        print("  %-16s %6d   %5.1f%%" % (k, cta[k], 100.0 * cta[k] / tot))
    print()
    for k in ("DEALER", "MSRP", "ninguno"):
        if not ejemplos[k]:
            continue
        print("  ejemplos de '%s':" % k)
        for sku, costo, msrp, dealer in ejemplos[k]:
            print("     %-22s costo %-10s  msrp %-10s  dealer %s"
                  % (sku[:22], round(costo, 2), msrp, dealer))
    print()
    if ratios:
        ratios.sort()
        print("  cuando no pega ninguno, cuanto es el costo respecto al MSRP:")
        for etq, q in (("minimo", 0.0), ("cuartil 1", 0.25), ("mediana", 0.5),
                       ("cuartil 3", 0.75), ("maximo", 1.0)):
            print("     %-11s %.2fx" % (etq, ratios[int(q * (len(ratios) - 1))]))
    print()
    print("  por proveedor (los que mas lineas aportan):")
    orden = sorted(por_proveedor.items(), key=lambda x: -sum(x[1].values()))
    for prov, c in orden[:10]:
        n = sum(c.values())
        print("     %-26s %4d lineas   dealer %3d   msrp %3d   ninguno %3d"
              % (str(prov)[:26], n, c["DEALER"], c["MSRP"], c["ninguno"]))

    destino = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "..", "medicion-base-costo.json")
    with open(os.path.abspath(destino), "w", encoding="utf-8") as fh:
        json.dump({"conteo": dict(cta),
                   "por_proveedor": {k: dict(v) for k, v in por_proveedor.items()}},
                  fh, indent=2, ensure_ascii=False)
    print()
    print("detalle en medicion-base-costo.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
