# -*- coding: utf-8 -*-
"""Lee las matrices de cotizaciones REALES y saca los porcentajes que de
verdad se usaron, en vez de preguntarselos al equipo.

Por que existe
--------------
Preventa contesto que no tienen porcentajes establecidos: "jugamos con
muchos margenes diferentes". Es cierto que no hay nada escrito, pero su
comportamiento si tiene patron, y el patron esta en las matrices que ya
armaron. Este script lo saca de ahi.

Que hace
--------
Recorre CLIENTES/<cliente>/.../Cotizacion #N-AAAA .../Matriz-Oferta/ y de
cada Excel lee la fila de porcentajes de la hoja de equipo (transporte,
imprevistos, IVA, DAI, administracion, margen), las tarifas de mano de
obra, los viaticos y el costo por kilometro.

Busca la hoja por CONTENIDO y no por nombre: los archivos no siguen una
convencion (hay "Equipos", "Camaras", "MATRIZ PROVEEDOR"...). Y descarta
solo los que no tienen esa fila, porque no todo archivo llamado "MATRIZ"
es una matriz de costo: algunos son cuestionarios a fabricantes.

Uso
---
    python scripts/analizar-matrices.py 2026        # censo de un anio
    python scripts/analizar-matrices.py 2026,2025 400

Deja un JSON en %TEMP%/matrices_<anios>.json con un registro por archivo.

SOLO LECTURA. No escribe en ninguna cotizacion, y el JSON no sale de la
maquina: nada de esto se sube al repositorio.

Limitaciones medidas (2026-09-23)
---------------------------------
- El 76% de las matrices son marcadores de OneDrive, no estan descargadas.
  Abrirlas las baja, y eso hace la corrida lenta. Algunas no logran
  bajarse y salen como FileNotFoundError (58 de 249 en la primera corrida).
- Un valor que aparece en el 99% de los archivos NO prueba que sea una
  tarifa acordada: puede ser un default del machote que nadie toco. Hay
  que mirar si alguien lo movio alguna vez para distinguir una cosa de la
  otra."""
import openpyxl, os, re, sys, unicodedata, warnings, json, io
warnings.filterwarnings("ignore")

def norm(s):
    if s is None: return ""
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii","ignore").decode()
    return re.sub(r"\s+", " ", s.lower()).strip()

ETIQUETAS = {
    "transporte": "transporte", "imprevistos": "imprevistos", "seguros": "seguros",
    "iva": "iva", "dai": "dai", "administracion": "administracion",
    "margen gv": "margen", "margen": "margen",
}

def pct_de_hoja(ws):
    """Busca las etiquetas en las primeras filas y toma el valor de abajo."""
    out = {}
    maxr = min(ws.max_row or 1, 8)
    maxc = min(ws.max_column or 1, 24)
    for r in range(1, maxr + 1):
        for c in range(1, maxc + 1):
            t = norm(ws.cell(r, c).value)
            if not t or len(t) > 18: continue
            k = ETIQUETAS.get(t)
            if not k or k in out: continue
            for dr in (1, 2):
                v = ws.cell(r + dr, c).value
                if isinstance(v, (int, float)) and 0 <= v < 1.5:
                    out[k] = round(float(v), 5); break
    return out

def analizar(path):
    d = {"archivo": os.path.basename(path)}
    try:
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    except Exception as e:
        return {"archivo": os.path.basename(path), "error": type(e).__name__}
    hojas = {norm(n): n for n in wb.sheetnames}
    d["n_hojas"] = len(wb.sheetnames)
    for clave, patron in (("equipos", "equipos"), ("materiales", "materiales"),
                          ("opexgv", "opex gv"), ("opexproy", "opex proyecto")):
        real = next((v for k, v in hojas.items() if k == patron), None)
        if real:
            try: d[clave] = pct_de_hoja(wb[real])
            except Exception: pass
    # Si la hoja de equipo no se llama "Equipos", buscar por CONTENIDO: la
    # primera hoja que tenga a la vez transporte, DAI y margen es la matriz
    # de producto principal. Los archivos no siguen una convencion de
    # nombres (MATRIZ PROVEEDOR, Estudio Mercado, etc.).
    if not d.get("equipos"):
        for k, real in hojas.items():
            try: pc = pct_de_hoja(wb[real])
            except Exception: continue
            if pc.get("margen") is not None and ("dai" in pc or "transporte" in pc):
                d["equipos"] = pc
                d["hoja_equipos"] = real
                break
    # mano de obra: hora hombre y precio por dia de la primera fila con datos
    mo = next((v for k, v in hojas.items() if k.startswith("mano de obra")), None)
    if mo:
        try:
            ws = wb[mo]
            filas = []
            for r in range(4, 12):
                c3 = ws.cell(r, 3).value; c4 = ws.cell(r, 4).value
                if isinstance(c3, (int, float)) and c3 > 0:
                    filas.append({"hora": round(float(c3), 2),
                                  "dia": round(float(c4), 2) if isinstance(c4, (int, float)) else None})
            if filas: d["mano_obra"] = filas
            # viaticos: alimentacion (H) y hospedaje (J)
            v = []
            for r in range(4, 12):
                h = ws.cell(r, 8).value; j = ws.cell(r, 10).value
                if isinstance(h, (int, float)) and h > 0: v.append({"alim": round(float(h),2),
                    "hosp": round(float(j),2) if isinstance(j,(int,float)) else None})
            if v: d["viaticos"] = v
        except Exception: pass
    tr = next((v for k, v in hojas.items() if k == "transporte"), None)
    if tr:
        try:
            ws = wb[tr]
            for r in range(2, 8):
                km = ws.cell(r, 8).value
                if isinstance(km, (int, float)) and 0 < km < 20:
                    d["costo_km"] = round(float(km), 3); break
        except Exception: pass
    wb.close()
    return d

if __name__ == "__main__":
    cli = os.path.expandvars(r"%USERPROFILE%\OneDrive - GRUPO VISION - DYNAMIC\Accesos directos\Archivos de Info Costa Rica - CLIENTES")
    anios = sys.argv[1].split(",") if len(sys.argv) > 1 else ["2026"]
    lim = int(sys.argv[2]) if len(sys.argv) > 2 else 15
    mats = []
    for root, dirs, files in os.walk(cli):
        if os.path.basename(root) != "Matriz-Oferta": continue
        padre = os.path.basename(os.path.dirname(root))
        if not any(("-" + a) in padre for a in anios): continue
        for f in files:
            if f.lower().endswith((".xlsx", ".xlsm")) and not f.startswith("~$"):
                mats.append(os.path.join(root, f))
    print("matrices candidatas: %d   (se analizan %d)" % (len(mats), min(lim, len(mats))), file=sys.stderr)
    res = []
    for i, p in enumerate(mats[:lim]):
        r = analizar(p)
        res.append(r)
        print("  %3d/%d  %s" % (i+1, min(lim,len(mats)), r.get("archivo","")[:52]), file=sys.stderr)
    salida = os.path.join(os.environ["TEMP"], "matrices_%s.json" % "_".join(anios))
    with io.open(salida, "w", encoding="utf-8") as f:
        f.write(json.dumps(res, ensure_ascii=False, indent=1))
    print("guardado: %s" % salida, file=sys.stderr)
