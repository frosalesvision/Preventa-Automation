# -*- coding: utf-8 -*-
"""
Pasa a imagen las páginas de un PDF escaneado (sin texto) para poder leerlas,
recortando los márgenes en blanco. No hace OCR: las imágenes se leen con Read.

    python -I paginas_a_imagen.py "<documento.pdf>" "<carpeta de salida>" [--zoom 1.8] [--paginas 1-10,12]

Deja c01.png, c02.png... en la carpeta y dice, por página, si ya traía texto
(esas conviene leerlas con `resaltar_ficha.py texto`, que cuesta mucho menos).

Por qué recortar: en el primer caso real (2026-11-17, 45 páginas escaneadas)
cada página era una captura de una tabla en la mitad de arriba de la hoja; a
tamaño completo la letra quedaba chica, y recortada al contenido se lee bien
con zoom 1.8 sin gastar más.
"""
import argparse
import os
import sys

try:
    import pymupdf
except ImportError:
    sys.exit("Falta PyMuPDF: python -m pip install pymupdf")
from PIL import Image, ImageOps


def rango(texto, total):
    if not texto:
        return list(range(1, total + 1))
    paginas = set()
    for parte in texto.split(","):
        parte = parte.strip()
        if "-" in parte:
            a, b = parte.split("-", 1)
            paginas.update(range(int(a), int(b) + 1))
        elif parte:
            paginas.add(int(parte))
    return sorted(p for p in paginas if 1 <= p <= total)


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("salida")
    ap.add_argument("--zoom", type=float, default=1.8)
    ap.add_argument("--paginas", help="ej. 1-10,12 (por defecto todas)")
    ap.add_argument("--margen", type=int, default=10, help="píxeles que se dejan alrededor del contenido")
    a = ap.parse_args()

    os.makedirs(a.salida, exist_ok=True)
    doc = pymupdf.open(a.pdf)
    con_texto = []
    for n in rango(a.paginas, doc.page_count):
        pagina = doc[n - 1]
        if len(pagina.get_text().strip()) > 40:
            con_texto.append(n)
        pix = pagina.get_pixmap(matrix=pymupdf.Matrix(a.zoom, a.zoom))
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        tinta = ImageOps.invert(img.convert("L")).point(lambda v: 255 if v > 40 else 0)
        caja = tinta.getbbox()
        if caja:
            l, t, r, b = caja
            m = a.margen
            img = img.crop((max(0, l - m), max(0, t - m), min(img.width, r + m), min(img.height, b + m)))
        ruta = os.path.join(a.salida, f"c{n:02d}.png")
        img.save(ruta)
        print(f"{n}: {ruta} ({img.width}x{img.height})" if caja else f"{n}: {ruta} (página en blanco)")
    print(f"\n{doc.page_count} páginas en el PDF.")
    if con_texto:
        print("Ya traen texto (mejor con resaltar_ficha.py texto):", con_texto)
    else:
        print("Ninguna trae texto: todo es escaneado.")


if __name__ == "__main__":
    main()
