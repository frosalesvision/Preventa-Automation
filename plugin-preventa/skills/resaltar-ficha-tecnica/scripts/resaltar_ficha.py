# -*- coding: utf-8 -*-
"""
Resalta en la ficha tecnica (PDF del fabricante) lo que pide el cartel, con
marcador amarillo y el numero de punto del cartel al margen.

    python -I resaltar_ficha.py texto    <ficha.pdf o cartel.docx> <salida.txt>
    python -I resaltar_ficha.py resaltar <ficha.pdf> <mapeo.json> <salida.pdf> [--sin-numeros]
    python -I resaltar_ficha.py vista    <resaltado.pdf> <carpeta> [--dpi 70] [--paginas 2 3] [--juntas]

texto     saca el texto pagina por pagina (o parrafo por parrafo si es un
          .docx). Leer asi gasta mucho menos que abrir el PDF como imagen.
resaltar  aplica el mapeo (formato en ../SKILL.md). Las marcas son anotaciones:
          se editan o borran en Acrobat o Edge, y salen al imprimir. Termina con
          codigo 1 si algun texto del mapeo no se encontro.
vista     guarda un PNG por pagina para revisar el resultado a ojo. Sin
          --paginas, solo las paginas que tienen marcas. Con --juntas, todas
          lado a lado en un solo PNG (una sola imagen que mirar).

Necesita PyMuPDF: python -m pip install pymupdf
"""
import argparse
import html
import json
import os
import re
import sys
import zipfile

import pymupdf

AMARILLO = (1.0, 0.93, 0.0)
ROJO = (0.75, 0.08, 0.08)
TAM_NUMERO = 7


def unir_por_linea(palabras):
    """Une las palabras de una misma linea en un rectangulo, para que el
    marcador quede continuo y no con huecos en los espacios."""
    lineas = {}
    for w in palabras:
        clave = round(w[1])
        r = pymupdf.Rect(w[:4])
        lineas[clave] = lineas[clave] | r if clave in lineas else r
    return list(lineas.values())


def buscar_por_palabras(pagina, texto, recorte):
    """Respaldo cuando search_for no encuentra la frase (espacios raros)."""
    palabras = pagina.get_text("words", clip=recorte)
    toks = texto.split()
    for i in range(len(palabras) - len(toks) + 1):
        seq = palabras[i:i + len(toks)]
        if all(w[4].rstrip(",;").lower() == t.rstrip(",;").lower() for w, t in zip(seq, toks)):
            return unir_por_linea(seq)
    return None


def agrupar(quads):
    """search_for parte una misma coincidencia en varios pedazos cuando una
    letra con tilde viene en otra fuente ("Compresi" + "ó" + "n de v"...).
    Se juntan los pedazos pegados en la misma linea: un rectangulo por
    coincidencia."""
    grupos = []
    for q in quads:
        r = q.rect
        if grupos:
            ult = grupos[-1][-1]
            if abs(r.x0 - ult.x1) < 1.5 and abs((r.y0 + r.y1) - (ult.y0 + ult.y1)) < 6:
                grupos[-1].append(r)
                continue
        grupos.append([r])
    return [caja(g) for g in grupos]


def buscar(pagina, texto, ocurrencia=1, recorte=None):
    """Devuelve la lista de rects de la ocurrencia pedida, o None."""
    hits = agrupar(pagina.search_for(texto, clip=recorte, quads=True))
    if len(hits) >= ocurrencia:
        return [hits[ocurrencia - 1]]
    if ocurrencia == 1:
        return buscar_por_palabras(pagina, texto, recorte)
    return None


def caja(marcas):
    r = pymupdf.Rect(getattr(marcas[0], "rect", marcas[0]))
    for m in marcas[1:]:
        r |= getattr(m, "rect", m)
    return r


def resaltar_en(pagina, marcas, nota):
    a = pagina.add_highlight_annot(marcas)
    a.set_colors(stroke=AMARILLO)
    a.set_info(title="Resaltado", content=nota)
    a.set_flags(a.flags | pymupdf.PDF_ANNOT_IS_PRINT)
    a.update()


def borde_numero(pagina, ancla):
    """Donde termina (a la derecha) el numero de punto: justo a la izquierda
    de la fila, o de la viñeta si la linea empieza con una. Si lo resaltado
    esta a mitad de linea, el numero taparia el texto: va donde empieza ese
    renglon de texto (sin saltar a otra columna ni a un titulo)."""
    misma_linea = [w for w in pagina.get_text("words") if w[1] < ancla.y1 and w[3] > ancla.y0]
    inicio = ancla.x0
    while True:
        antes = [w for w in misma_linea if inicio - 20 < w[2] <= inicio + 0.5 and w[0] < inicio - 0.5]
        if not antes:
            break
        inicio = min(w[0] for w in antes)
    ancla = pymupdf.Rect(inicio, ancla.y0, ancla.x1, ancla.y1)
    derecha = ancla.x0 - 3
    for d in pagina.get_drawings():
        r = d["rect"]
        if r.width < 6 and r.height < 6 and ancla.x0 - 20 < r.x0 < ancla.x0 \
                and r.y0 < ancla.y1 and r.y1 > ancla.y0:
            derecha = min(derecha, r.x0 - 3)
    return derecha


def poner_numero(pagina, ancla, texto):
    # holgura: el recuadro tiene margen interno y si no cabe corta el texto
    ancho = pymupdf.get_text_length(texto, fontname="helv", fontsize=TAM_NUMERO) + 10
    derecha = borde_numero(pagina, ancla)
    izquierda = max(1, derecha - ancho)
    # el texto se dibuja pegado arriba del recuadro: se baja para alinearlo
    y = ancla.y0 + (ancla.height - (TAM_NUMERO + 3)) / 2 + 1.5
    r = pymupdf.Rect(izquierda, y, max(derecha, izquierda + ancho), y + TAM_NUMERO + 3)
    a = pagina.add_freetext_annot(
        r, texto, fontsize=TAM_NUMERO, fontname="helv", text_color=ROJO,
        fill_color=None, border_width=0, align=pymupdf.TEXT_ALIGN_RIGHT,
    )
    a.set_info(title="Punto del cartel")
    a.set_flags(a.flags | pymupdf.PDF_ANNOT_IS_PRINT)
    a.update()


def parrafos_docx(ruta):
    """Texto de un .docx sin dependencias extra (el cartel suele venir en Word)."""
    with zipfile.ZipFile(ruta) as z:
        xml = z.read("word/document.xml").decode("utf-8")
    salida = []
    for par in re.findall(r"<w:p[ >].*?</w:p>", xml, flags=re.S):
        par = par.replace("<w:tab/>", "\t").replace("<w:br/>", "\n")
        # Solo <w:t> o <w:t xml:space=...>: <w:t[^>]*> tambien agarra <w:tab>, <w:tabs> y <w:tc>,
        # y metia XML al texto (72% del archivo en un cartel con tabuladores).
        texto = html.unescape("".join(re.findall(r"<w:t(?: [^>]*)?>(.*?)</w:t>", par, flags=re.S)))
        if texto.strip():
            salida.append(texto)
    return salida


def cmd_texto(args):
    if args.ficha.lower().endswith(".docx"):
        parrafos = parrafos_docx(args.ficha)
        with open(args.salida, "w", encoding="utf-8") as f:
            f.write("\n".join(parrafos))
        print(f"{len(parrafos)} parrafos -> {args.salida}")
        return
    doc = pymupdf.open(args.ficha)
    with open(args.salida, "w", encoding="utf-8") as f:
        for i, pagina in enumerate(doc, 1):
            f.write(f"===== pagina {i} de {doc.page_count} =====\n")
            f.write(pagina.get_text("text"))
            f.write("\n")
    vacias = [i for i, p in enumerate(doc, 1) if not p.get_text("text").strip()]
    print(f"{doc.page_count} paginas -> {args.salida}")
    if vacias:
        print(f"OJO: paginas sin texto (escaneadas o solo imagen): {vacias}")


def cmd_resaltar(args):
    if os.path.abspath(args.ficha) == os.path.abspath(args.salida):
        sys.exit("La salida no puede ser la misma ficha: el original no se toca.")
    with open(args.mapeo, encoding="utf-8") as f:
        mapeo = json.load(f)
    col_valor = mapeo.get("columna_valor_x")
    doc = pymupdf.open(args.ficha)
    faltan, total = [], 0
    numeros = {}  # (pagina, y, x del numero) -> [texto, ancla]

    for m in mapeo["marcas"]:
        pno = m["pagina"]
        pagina = doc[pno - 1]
        fila, punto = m.get("fila"), str(m.get("punto", "")).strip()
        nota = f"Punto {punto} del cartel" if punto else "Resaltado"
        ancla = banda = None

        if fila:
            hit = buscar(pagina, fila, m.get("ocurrencia", 1))
            if not hit:
                faltan.append((pno, fila))
                continue
            ancla = caja(hit)
            resaltar_en(pagina, hit, nota)
            total += 1
            if m.get("valor_abajo"):
                # fichas web: la etiqueta arriba y el valor en las dos lineas de abajo
                banda = pymupdf.Rect(ancla.x0 - 2, ancla.y1 - 1, ancla.x0 + 250, ancla.y1 + 30)
            else:
                # los valores se buscan solo en la franja de esta fila
                banda = pymupdf.Rect(ancla.x0 - 2, ancla.y0 - 3, pagina.rect.x1, ancla.y1 + 3)

        for v in m.get("valores", []):
            if v == "*" and banda is None:
                faltan.append((pno, '"*" necesita "fila"'))
                continue
            if v == "*" and m.get("valor_abajo"):
                # solo la primera linea: mas abajo ya empieza la etiqueta siguiente
                linea = pymupdf.Rect(banda.x0, banda.y0, banda.x1, ancla.y1 + 18)
                hit = unir_por_linea(pagina.get_text("words", clip=linea)) or None
            elif v == "*":  # toda la celda de valor de la fila
                x0 = col_valor if col_valor is not None else ancla.x1 + 4
                celda = pymupdf.Rect(x0, banda.y0, pagina.rect.x1, banda.y1)
                hit = unir_por_linea(pagina.get_text("words", clip=celda)) or None
            else:
                hit = buscar(pagina, v, 1, banda)
            if not hit:
                faltan.append((pno, v))
                continue
            resaltar_en(pagina, hit, nota)
            total += 1
            if ancla is None:
                ancla = caja(hit)

        if punto and ancla is not None and not args.sin_numeros:
            # dos marcas en el mismo renglon y el mismo lugar comparten numero
            # ("2·5"); en otra columna, cada una lleva el suyo
            clave = (pno, round(ancla.y0), round(borde_numero(pagina, ancla) / 6))
            if clave in numeros:
                numeros[clave][0] += "·" + punto
            else:
                numeros[clave] = [punto, ancla]

    for (pno, _, _), (texto, ancla) in numeros.items():
        poner_numero(doc[pno - 1], ancla, texto)

    doc.save(args.salida, garbage=3, deflate=True)
    print(f"{total} resaltados, {len(numeros)} numeros de punto -> {args.salida}")
    if faltan:
        print("NO ENCONTRADOS (corregir el mapeo y volver a correr):")
        for pno, t in faltan:
            print(f"  pagina {pno}: {t!r}")
        sys.exit(1)


def cmd_vista(args):
    doc = pymupdf.open(args.pdf)
    os.makedirs(args.carpeta, exist_ok=True)
    paginas = args.paginas or [i for i, p in enumerate(doc, 1) if p.first_annot]
    base = os.path.splitext(os.path.basename(args.pdf))[0]
    if args.juntas:
        imagenes = [doc[n - 1].get_pixmap(dpi=args.dpi, annots=True) for n in paginas]
        alto = max(p.height for p in imagenes)
        hoja = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.IRect(0, 0, sum(p.width for p in imagenes), alto), False)
        hoja.clear_with(255)
        x = 0
        for p in imagenes:
            p.set_origin(x, 0)
            hoja.copy(p, p.irect)
            x += p.width
        ruta = os.path.join(args.carpeta, f"{base}_juntas.png")
        hoja.save(ruta)
        print(ruta)
        return
    for n in paginas:
        ruta = os.path.join(args.carpeta, f"{base}_p{n}.png")
        doc[n - 1].get_pixmap(dpi=args.dpi, annots=True).save(ruta)
        print(ruta)


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("texto")
    p.add_argument("ficha")
    p.add_argument("salida")
    p.set_defaults(fn=cmd_texto)

    p = sub.add_parser("resaltar")
    p.add_argument("ficha")
    p.add_argument("mapeo")
    p.add_argument("salida")
    p.add_argument("--sin-numeros", action="store_true")
    p.set_defaults(fn=cmd_resaltar)

    p = sub.add_parser("vista")
    p.add_argument("pdf")
    p.add_argument("carpeta")
    p.add_argument("--dpi", type=int, default=70)
    p.add_argument("--paginas", type=int, nargs="+")
    p.add_argument("--juntas", action="store_true")
    p.set_defaults(fn=cmd_vista)

    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
