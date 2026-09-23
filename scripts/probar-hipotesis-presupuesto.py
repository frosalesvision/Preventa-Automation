# -*- coding: utf-8 -*-
"""Prueba si las cotizaciones a licitacion se arman contra el presupuesto
publicado en el pliego, en vez de aplicar un margen elegido.

La hipotesis
------------
Preventa dice que el margen "varia" y que no tienen nada establecido. El
censo de 2026 confirmo que varia: de 8% a 42%. Pero al leer el pliego de
un caso atipico (margen 20%, imprevistos 0%, administracion 0%) aparecio
que el documento publicaba un presupuesto de CRC 2.084.380 y la
cotizacion sumo CRC 2.019.571: el 96,9% del techo.

Eso sugiere que en licitacion **el margen no se elige, se deduce**: se
parte del precio al que se quiere llegar y el margen sale de ahi. Si es
cierto, explica el rango completo sin necesidad de ninguna tabla.

Que hace este script
--------------------
Para cada cotizacion que tenga a la vez un pliego/estudio en
`Visita tecnica/` y una matriz en `Matriz-Oferta/`:
  1. saca del PDF los montos que aparecen cerca de la palabra
     "presupuesto" (colones o dolares),
  2. saca de la matriz el TOTAL de la hoja de cotizacion,
  3. calcula que porcentaje del presupuesto representa la oferta.

Si la mayoria cae entre 90% y 100%, la hipotesis se sostiene.

SOLO LECTURA. No modifica ninguna cotizacion y no copia contenido a
ningun archivo del repositorio: la salida son porcentajes.

Uso:
    python scripts/probar-hipotesis-presupuesto.py
"""

import os
import re
import sys
import unicodedata
import warnings

warnings.filterwarnings("ignore")

try:
    import openpyxl
except ImportError:
    sys.exit("Falta openpyxl.")
try:
    import pdfplumber
except ImportError:
    sys.exit("Falta pdfplumber.  pip install pdfplumber")

CLIENTES = os.path.expandvars(
    r"%USERPROFILE%\OneDrive - GRUPO VISION - DYNAMIC\Accesos directos"
    r"\Archivos de Info Costa Rica - CLIENTES"
)
CLAVES_DOC = ("pliego", "especificacion", "cartel", "terminos",
              "condiciones", "estudio de mercado")


def norm(s):
    return unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower()


def ls(p):
    try:
        return os.listdir(p)
    except Exception:
        return []


def pares():
    """Cotizaciones con pliego y matriz a la vez."""
    out = []
    for root, dirs, files in os.walk(CLIENTES):
        b = os.path.basename(root)
        if not b.startswith("Cotizaci"):
            continue
        anio = next((a for a in ("2026", "2025") if ("-" + a) in b), None)
        if not anio:
            continue
        docs = []
        for v in ls(root):
            if not norm(v).startswith("visita"):
                continue
            for f in ls(os.path.join(root, v)):
                if f.lower().endswith(".pdf") and any(k in norm(f) for k in CLAVES_DOC):
                    docs.append(os.path.join(root, v, f))
        mats = [os.path.join(root, "Matriz-Oferta", f)
                for f in ls(os.path.join(root, "Matriz-Oferta"))
                if f.lower().endswith((".xlsx", ".xlsm")) and not f.startswith("~$")]
        if docs and mats:
            out.append((anio, b, docs, mats))
    return out


# Un monto en colones: 2.084.380,00 / 2,084,380.00 / 2084380
MONTO = re.compile(r"(\d{1,3}(?:[.,]\d{3}){1,4}(?:[.,]\d{2})?|\d{6,10})")


def a_numero(s):
    s = s.strip()
    # el ultimo separador con 2 digitos detras son decimales
    if re.search(r"[.,]\d{2}$", s):
        ent, dec = s[:-3], s[-2:]
        ent = re.sub(r"[.,]", "", ent)
        return float(ent + "." + dec)
    return float(re.sub(r"[.,]", "", s))


def presupuesto(pdf_path, max_pag=8):
    """Montos que aparecen en una linea que menciona presupuesto."""
    encontrados = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for p in pdf.pages[:max_pag]:
                t = p.extract_text() or ""
                for linea in t.split("\n"):
                    n = norm(linea)
                    if "presupuesto" not in n and "monto estimado" not in n:
                        continue
                    moneda = "CRC" if ("colon" in n or "₡" in linea) else (
                        "USD" if ("dolar" in n or "$" in linea) else "?")
                    for m in MONTO.findall(linea):
                        try:
                            v = a_numero(m)
                        except Exception:
                            continue
                        if v >= 100000:
                            encontrados.append((v, moneda))
    except Exception:
        return []
    return encontrados


def total_matriz(xlsx):
    """El TOTAL de la hoja de cotizacion, en la moneda que este."""
    try:
        wb = openpyxl.load_workbook(xlsx, read_only=True, data_only=True)
    except Exception:
        return None
    mejor = None
    for nom in wb.sheetnames:
        if not norm(nom).startswith("cotizaci"):
            continue
        ws = wb[nom]
        for fila in ws.iter_rows(min_row=1, max_row=min(ws.max_row or 1, 120)):
            etiqueta = any(isinstance(c.value, str) and norm(c.value).strip() == "total"
                           for c in fila)
            if not etiqueta:
                continue
            nums = [c.value for c in fila if isinstance(c.value, (int, float)) and c.value > 0]
            if nums:
                cand = max(nums)
                if mejor is None or cand > mejor:
                    mejor = cand
    wb.close()
    return mejor


def main():
    ps = pares()
    print("=" * 74)
    print(" HIPOTESIS: la oferta se arma contra el presupuesto publicado")
    print("=" * 74)
    print("pares pliego <-> matriz: %d\n" % len(ps))
    print("%-38s %12s %12s %7s" % ("cotizacion", "presupuesto", "oferta", "%"))
    print("-" * 74)
    ratios = []
    for anio, carpeta, docs, mats in ps:
        pres = []
        for d in docs:
            pres += presupuesto(d)
        if not pres:
            continue
        tot = None
        for m in mats:
            tot = total_matriz(m)
            if tot:
                break
        if not tot:
            continue
        # se prueba contra el presupuesto mas cercano al total, en su moneda
        cands = [v for v, mon in pres]
        elegido = min(cands, key=lambda v: abs((tot / v) - 0.95) if v else 9)
        r = tot / elegido if elegido else 0
        if not (0.3 <= r <= 3.0):
            continue
        ratios.append(r)
        print("%-38s %12s %12s %6.1f%%" % (carpeta[:38], format(elegido, ",.0f"),
                                           format(tot, ",.0f"), r * 100))
    print("-" * 74)
    if ratios:
        import statistics
        dentro = sum(1 for r in ratios if 0.85 <= r <= 1.0)
        print("casos comparables: %d" % len(ratios))
        print("mediana de oferta/presupuesto: %.1f%%" % (statistics.median(ratios) * 100))
        print("entre 85%% y 100%% del presupuesto: %d de %d (%.0f%%)"
              % (dentro, len(ratios), 100.0 * dentro / len(ratios)))
        print()
        if dentro >= len(ratios) * 0.6:
            print("-> La hipotesis SE SOSTIENE: la oferta se arma contra el techo.")
        else:
            print("-> La hipotesis NO se sostiene con estos datos.")
    else:
        print("no se pudo comparar ningun caso")
    return 0


if __name__ == "__main__":
    sys.exit(main())
