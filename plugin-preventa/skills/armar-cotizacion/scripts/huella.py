r"""Huella de lo que escribio el plugin en una cotizacion (regla R28): sirve para saber, antes de
cambiar algo, si una persona lo toco despues.

  python -I huella.py anotar "<carpeta de la cotizacion>" "<archivo>" ["<archivo>" ...]
  python -I huella.py revisar "<carpeta de la cotizacion>"

anotar: guarda en <carpeta>\registro-preventa.json (oculto) el SHA-256, el tamano, la fecha y quien
lo guardo de cada archivo que el plugin acaba de crear (la matriz copiada, el PDF, una V2). Se corre
solo sobre lo que escribio el plugin, nunca sobre un archivo que ya estaba.

revisar: compara cada archivo de la carpeta contra el registro y dice, por archivo:
  IGUAL           esta como lo dejo el plugin
  CAMBIADO        el plugin lo creo y despues alguien lo guardo distinto (quien y cuando)
  NO ES DEL PLUGIN  no esta en el registro: lo creo una persona, o es de antes del registro
  RENOMBRADO      el plugin lo creo y alguien le cambio el nombre (mismo contenido)
  FALTA           el plugin lo creo y ya no esta (lo movieron o borraron)
Sale con 0 solo si todo esta IGUAL. Con cualquier otra cosa, el plugin no cambia nada: avisa y
propone una V2 (R28).
"""
import ctypes, datetime, hashlib, json, os, re, sys, zipfile

REGISTRO = "registro-preventa.json"
FUERA = {REGISTRO.lower(), "desktop.ini"}


def L(p):  # mas de 259: la carpeta en nombre corto 8.3, como en el resto de los scripts
    if len(p) <= 259:
        return p
    buf = ctypes.create_unicode_buffer(1024)
    ctypes.windll.kernel32.GetShortPathNameW(os.path.dirname(p), buf, 1024)
    return os.path.join(buf.value, os.path.basename(p))


def datos(p):
    """sha, tamano, fecha de modificacion y, en un Excel, quien lo guardo por ultima vez."""
    q = L(p)
    h = hashlib.sha256()
    with open(q, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    d = {"sha256": h.hexdigest(), "tamano": os.path.getsize(q),
         "modificado": datetime.datetime.fromtimestamp(os.path.getmtime(q)).strftime("%Y-%m-%d %H:%M:%S")}
    if p.lower().endswith((".xlsx", ".xlsm")):
        try:
            core = zipfile.ZipFile(q).read("docProps/core.xml").decode("utf-8", "replace")
            m = re.search(r"<cp:lastModifiedBy>(.*?)</cp:lastModifiedBy>", core)
            d["guardado_por"] = m.group(1).strip() if m else ""
        except (KeyError, zipfile.BadZipFile):
            pass
    return d


def leer(carpeta):
    r = os.path.join(carpeta, REGISTRO)
    if os.path.exists(r):
        return json.load(open(r, encoding="utf-8"))
    return {"archivos": {}}


def anotar(carpeta, archivos):
    reg = leer(carpeta)
    for a in archivos:
        rel = os.path.relpath(os.path.abspath(a), os.path.abspath(carpeta))
        if rel.startswith(".."):
            sys.exit("no esta dentro de la carpeta de la cotizacion: %s" % a)
        d = datos(os.path.abspath(a))
        d["anotado"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        reg["archivos"][rel] = d
        print("ANOTADO  %s" % rel)
    r = os.path.join(carpeta, REGISTRO)
    if os.path.exists(r):
        ctypes.windll.kernel32.SetFileAttributesW(r, 0x80)  # normal, para poder reescribirlo
    json.dump(reg, open(r, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    ctypes.windll.kernel32.SetFileAttributesW(r, 0x02)  # oculto: no es para el equipo


def revisar(carpeta):
    reg = leer(carpeta)["archivos"]
    por_sha = {v["sha256"]: k for k, v in reg.items()}
    vistos, todo_igual = set(), True
    for raiz, _, nombres in os.walk(carpeta):
        for n in sorted(nombres):
            if n.lower() in FUERA or n.startswith("~$"):
                if n.startswith("~$"):
                    print("ABIERTO       %s (alguien lo tiene abierto)" % os.path.relpath(os.path.join(raiz, n), carpeta))
                    todo_igual = False
                continue
            p = os.path.join(raiz, n)
            rel = os.path.relpath(p, carpeta)
            vistos.add(rel)
            try:
                d = datos(p)
            except OSError as e:
                print("NO SE PUEDE LEER  %s (%d caracteres de ruta: %s)" % (rel, len(p), e))
                todo_igual = False
                continue
            quien = " por %s" % d["guardado_por"] if d.get("guardado_por") else ""
            if rel not in reg and d["sha256"] in por_sha:
                print("RENOMBRADO    %s: es %s, que dejo el plugin, con otro nombre o en otra carpeta" % (rel, por_sha[d["sha256"]]))
                vistos.add(por_sha[d["sha256"]])
                todo_igual = False
            elif rel not in reg:
                print("NO ES DEL PLUGIN  %s (guardado%s el %s)" % (rel, quien, d["modificado"]))
                todo_igual = False
            elif reg[rel]["sha256"] == d["sha256"]:
                print("IGUAL         %s" % rel)
            else:
                print("CAMBIADO      %s: el plugin lo dejo el %s; despues lo guardaron%s el %s" % (
                    rel, reg[rel]["anotado"], quien, d["modificado"]))
                todo_igual = False
    for rel in reg:
        if rel not in vistos:
            print("FALTA         %s (el plugin lo dejo el %s)" % (rel, reg[rel]["anotado"]))
            todo_igual = False
    if not reg:
        print("SIN REGISTRO: la cotizacion es de antes del registro (R28) o la armo una persona; todo cuenta como de una persona")
    print("TODO COMO LO DEJO EL PLUGIN" if todo_igual else "HAY CAMBIOS O ARCHIVOS AJENOS: no cambiar nada; avisar y proponer una V2 (R28)")
    return 0 if todo_igual else 1


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if len(sys.argv) >= 4 and sys.argv[1] == "anotar":
        anotar(sys.argv[2], sys.argv[3:])
    elif len(sys.argv) == 3 and sys.argv[1] == "revisar":
        sys.exit(revisar(sys.argv[2]))
    else:
        sys.exit(__doc__)


main()
