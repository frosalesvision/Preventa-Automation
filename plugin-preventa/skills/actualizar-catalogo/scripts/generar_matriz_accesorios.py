"""Genera/actualiza la pestana "Compatibilidad de Accesorios" dentro del
propio Catalogo de productos por proveedor.xlsx, a partir de las filas de
categoria "accesorio" del catalogo.

Uso:
    python generar_matriz_accesorios.py "<ruta al Catalogo de productos por proveedor.xlsx>"

Escribe sobre el MISMO archivo (agrega/reemplaza la pestana, no toca
las demas). No lee ninguna cotizacion de cliente: toda la compatibilidad
de esta fuente sale del campo Descripcion que el propio fabricante (hoy,
Hanwha) ya escribe en su catalogo/pricelist (ej. "Wall mount compatible
with XNP-6120HW"). Pares que vengan de cotizaciones reales o de
investigacion web se agregan aparte (ver notas del skill buscar-equipo)
y se identifican por la columna "Fuente".
"""
import sys
import re
from collections import Counter

# =========================================================================
# AVISO (medido 2026-09-23): ESTE SCRIPT BORRA LOS DESPLEGABLES
#
# Guarda con openpyxl, que no soporta la extension x14 que usa la validacion
# de datos con rango en otra hoja. Al guardar la elimina SIN AVISAR: el
# archivo queda sano, los datos intactos, y los desplegables de Categoria y
# Subcategoria simplemente dejan de existir.
#
# Se comprobo: correr este script dejo las dos validaciones en cero.
#
# DESPUES DE CORRERLO, siempre:
#     powershell -File scripts/reparar-desplegables.ps1
# =========================================================================

import openpyxl
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.styles import Font, Alignment

ACC_CATS = {
    'Accessory', 'Accesorios / Power Supply', 'Explosion Proof - Accessory',
    'Accessories', 'Power Supply', 'Monitor Stand',
}

PREFIX_RE = re.compile(r'^([A-Z]{2,}-)')

TRIGGER_PATTERNS = [
    re.compile(r'[Cc]ompatible with:?\s+(.+?)(?:\s--\s|\n|\.\s|\.$|$)'),
    re.compile(r'[Ff]or(?: [Tt]he)?\s*\(([^)]+)\)'),
    re.compile(r'[Ff]or [Tt]he\s+([^.\n]+?)(?:\s--\s|\.\s|\.$|\n|$)'),
    # "for" suelto sin parentesis ni "the" (ej. "Ceiling Mount for PAR-ALLDRXIRBD",
    # o en mayusculas "JUNCTION BOX FOR SEC-P8DRXIR28NH")
    re.compile(r'\b[Ff][Oo][Rr]\s+([A-Za-z][A-Za-z0-9\-/:, &]*?)(?:\s--\s|\.\s|\.$|\n|$)'),
    re.compile(r'[Ss]upported cameras?\s*\(([^)]+)\)'),
    re.compile(r'[Uu]sed with\s+(.+?)(?:\s--\s|\.\s|\.$|\n|$)'),
    re.compile(r'[Cc]an be used with\s+(.+?)(?:\s--\s|\.\s|\.$|\n|$)'),
]

TIPO_KEYWORDS = [
    ('lens', 'Lente'),
    ('flush mount', 'Mount empotrado (flush)'),
    ('wall & pole mount', 'Mount pared/poste'),
    ('wall and pole mount', 'Mount pared/poste'),
    ('wall mount', 'Mount de pared'),
    ('pole mount', 'Mount de poste'),
    ('corner mount', 'Mount de esquina'),
    ('ceiling mount', 'Mount de cielo'),
    ('pendant mount', 'Mount pendant'),
    ('pendant back box', 'Back box (pendant)'),
    ('back box', 'Back box'),
    ('gangbox', 'Gangbox / caja de conexiones'),
    ('cap adapter', 'Adaptador tipo cap'),
    ('mounting converter', 'Convertidor de montaje'),
    ('mounting bracket', 'Bracket de montaje'),
    ('mounting hole cover', 'Tapa/placa de montaje'),
    ('mounting accessory', 'Accesorio de montaje'),
    ('mount plate', 'Placa de montaje'),
    ('junction box', 'Caja de conexiones'),
    ('protection kit', 'Kit de proteccion'),
    ('housing', 'Housing/carcasa'),
    ('power supply', 'Fuente de poder'),
    ('poe', 'Inyector/convertidor PoE'),
    ('converter', 'Convertidor'),
    ('nvr', 'NVR'),
    ('solar light', 'Iluminacion solar'),
    ('mount', 'Mount (generico)'),
]

# Pares confirmados a mano revisando cotizaciones reales (2026-09-01,
# autorizado por el usuario para este analisis puntual -- ver notas-proceso.md).
# No se re-generan solos corriendo este script: si se encuentra un caso nuevo
# util revisando otra cotizacion, agregarlo aca a mano. Cada tupla:
# (sku_camara, sku_accesorio, nombre_accesorio, marca_accesorio, nota).
PARES_VERIFICADOS_MANUALMENTE = [
    ('PAR-P8PTZXIR32NH-AI', 'WV-QWL502-W', 'i-PRO Wall or Pole Mount Bracket', 'Panasonic i-PRO',
     'Visto en una cotizacion real de un proyecto municipal de ciudad segura (2026) -- Paramont no tenia mount propio para esta PTZ, se uso un bracket universal de Panasonic i-PRO. No esta en nuestro catalogo de proveedores todavia, hay que cotizarlo aparte.'),
    ('PAR-P8PTZXIR32NH-AI', 'WV-QPL500-W', 'i-PRO Pole Mount Bracket', 'Panasonic i-PRO',
     'Visto en una cotizacion real de ese mismo proyecto (2026) -- mismo caso que WV-QWL502-W, no esta en nuestro catalogo todavia.'),
    ('PAR-P8PTZXIR32NH-AI', 'WV-QSR503-W', 'i-PRO Shroud Bracket (4 holes)', 'Panasonic i-PRO',
     'Visto en una cotizacion real de ese mismo proyecto (2026). No esta en nuestro catalogo todavia.'),
    ('PAR-P8PTZXIR32NH-AI', 'WV-QWL501-W', 'i-PRO Wall Mount Bracket, White', 'Panasonic i-PRO',
     'Visto en una cotizacion real de ese mismo proyecto (2026). No esta en nuestro catalogo todavia.'),
    ('PAR-P8PTZXIR32NH-AI', 'SBD-180PMW', 'Pole Mount', 'Hanwha',
     'Visto en una cotizacion real de ese mismo proyecto (2026) -- OJO: la ficha de Hanwha de este mount NO lista modelos Paramont como compatibles, el equipo lo uso igual en la practica. Verificar que encaje fisicamente antes de repetirlo.'),
    ('PAR-P6BIRA2812-LC3', 'WV-QWL502-W', 'i-PRO Wall or Pole Mount Bracket', 'Panasonic i-PRO',
     'Visto en una cotizacion real de ese mismo proyecto (2026). No esta en nuestro catalogo todavia.'),
    ('PAR-P6BIRA2812-LC3', 'WV-QPL500-W', 'i-PRO Pole Mount Bracket', 'Panasonic i-PRO',
     'Visto en una cotizacion real de ese mismo proyecto (2026). No esta en nuestro catalogo todavia.'),
    ('PAR-P6BIRA2812-LC3', 'WV-QSR503-W', 'i-PRO Shroud Bracket (4 holes)', 'Panasonic i-PRO',
     'Visto en una cotizacion real de ese mismo proyecto (2026). No esta en nuestro catalogo todavia.'),
    ('PAR-P6BIRA2812-LC3', 'WV-QWL501-W', 'i-PRO Wall Mount Bracket, White', 'Panasonic i-PRO',
     'Visto en una cotizacion real de ese mismo proyecto (2026). No esta en nuestro catalogo todavia.'),
    ('PAR-P6BIRA2812-LC3', 'SBD-180PMW', 'Pole Mount', 'Hanwha',
     'Visto en una cotizacion real de ese mismo proyecto (2026) -- OJO: la ficha de Hanwha de este mount NO lista modelos Paramont como compatibles, el equipo lo uso igual en la practica. Verificar que encaje fisicamente antes de repetirlo.'),
]
FUENTE_COTIZACION_REAL = 'Cotizacion real (patron usado por el equipo, no documentado por el fabricante) - verificar antes de usar'

SHEET_NAME = 'Compatibilidad de Accesorios'
HEADERS = [
    'Modelo Camara', 'Nombre Camara', 'Marca Camara',
    'Modelo Accesorio', 'Nombre Accesorio', 'Tipo Accesorio', 'Marca Accesorio',
    'Proveedor', 'Fuente', 'Notas',
]


def classify_tipo(nombre):
    n = (nombre or '').lower()
    for kw, tipo in TIPO_KEYWORDS:
        if kw in n:
            return tipo
    return 'Otro / sin clasificar'


# Palabras que indican que un producto ES el accesorio de instalacion (no la
# camara/equipo principal). Deliberadamente mas chico que TIPO_KEYWORDS: no
# incluye "nvr" (es equipo principal, no accesorio) para no confundir dirección.
ACCESSORY_HINT_WORDS = [
    'mount', 'bracket', 'adapter', 'adaptor', 'housing', 'cap adapter',
    'back box', 'backbox', 'junction box', 'gangbox', 'cover', 'protection kit',
    'converter', 'poe injector', 'lens', 'imager', 'extension cable',
    'wall&pole', 'pendant', 'flush', 'parapet', 'power supply',
    'bubble', 'smoked', 'tinted', 'gangplate', 'wall arm', 'mounting arm',
    'clamp', 'strap',
]


def looks_like_accessory(nombre):
    n = (nombre or '').lower()
    # "plate" solo (Cap Adapter Plate, Mount Plate, "Plate for Dome...") es
    # accesorio; "License Plate" (camaras LPR) no lo es -- se descarta ese caso
    # puntual en vez de sumar "plate" a la lista general.
    if 'plate' in n and 'license plate' not in n:
        return True
    return any(w in n for w in ACCESSORY_HINT_WORDS)


def split_group(text):
    return [p.strip(' ()') for p in re.split(r',| and ', text) if p.strip(' ()')]


EMBEDDED_SKU_RE = re.compile(r'\b[A-Z0-9]{2,}(?:-[A-Z0-9]+)+\b')


def build_expand_and_validate(real_skus):
    def expand_and_validate(group_text):
        # Hanwha agrupa familias como "XND-6010/6020R/8020R": el prefijo de
        # letras se hereda al siguiente token que sea solo numero/letra suelta.
        found = []
        last_prefix = None
        for chunk in split_group(group_text):
            for sub in chunk.split('/'):
                sub = sub.strip()
                if not sub:
                    continue
                pm = PREFIX_RE.match(sub)
                if pm:
                    last_prefix = pm.group(1)
                    candidate = sub
                elif last_prefix and re.match(r'^[A-Z0-9]+$', sub):
                    candidate = last_prefix + sub
                else:
                    candidate = sub
                if candidate.upper() in real_skus:
                    found.append(real_skus[candidate.upper()])
        if not found:
            # Rescate: frases como "Wall Mount for Paramont Series:
            # PAR-P4PTZXIR2812NH-AIWL" no se separan por coma/slash, pero el
            # SKU real igual esta ahi adentro -- se busca directo en el texto
            # crudo en vez de asumir que ocupa el chunk completo.
            for tok in EMBEDDED_SKU_RE.findall(group_text):
                if tok.upper() in real_skus and real_skus[tok.upper()] not in found:
                    found.append(real_skus[tok.upper()])
        return found
    return expand_and_validate


def extract_raw_phrases(text):
    if not text:
        return []
    return [m.group(1) for pat in TRIGGER_PATTERNS for m in pat.finditer(text)]


def extract_compatible_models(text, expand_and_validate):
    found = []
    for phrase in extract_raw_phrases(text):
        found += expand_and_validate(phrase)
    seen = []
    for f in found:
        if f not in seen:
            seen.append(f)
    return seen


# Palabras que, encontradas en una frase "for X"/"compatible with X" sin
# ningun SKU real detectable, alcanzan para intentar un match por categoria
# generica en vez de por modelo exacto (ver build_category_matches).
CATEGORY_KEYWORDS = [
    'vandal', 'ptz', 'thermal', 'explosion proof', 'panoramic', 'fisheye',
    'turret', 'intercom', 'body camera', 'box camera', 'bullet', 'dome',
    'mini dome', 'mini bullet', 'bodycam', 'elevator',
]


def find_category_hint(phrase, marcas_reales):
    """Si la frase nombra una marca real del catalogo mas una palabra de
    categoria reconocible (ej. "Paramont PTZ Cameras"), devuelve (marca,
    [keywords]). Si solo nombra la marca sin nada distintivo (ej. "Paramont
    Series Cameras", "Paramont Cameras") devuelve (None, []) -- no alcanza
    para acotar un match razonable, mejor no inventar uno."""
    phrase_l = phrase.lower()
    brand = next((b for b in marcas_reales if b and b.lower() in phrase_l), None)
    if not brand:
        return None, []
    keywords = [k for k in CATEGORY_KEYWORDS if k in phrase_l]
    return (brand, keywords) if keywords else (None, [])


def build_rows_from_catalog(catalog_rows, idx):
    real_skus = {}
    nombre_marca_by_sku = {}
    marcas_reales = set()
    camera_candidates = []
    for r in catalog_rows:
        sku = r[idx['Modelo / SKU']]
        nombre_r = r[idx['Nombre de equipo/producto']]
        marca_r = r[idx['Marca']]
        if sku:
            key = str(sku).strip().upper()
            real_skus[key] = str(sku).strip()
            nombre_marca_by_sku[key] = (nombre_r, marca_r)
        if marca_r:
            marcas_reales.add(marca_r)
        if sku and not looks_like_accessory(nombre_r):
            searchable = ((nombre_r or '') + ' ' + (r[idx['Descripcion']] or '')).lower()
            camera_candidates.append((str(sku).strip(), nombre_r, marca_r, searchable))
    expand_and_validate = build_expand_and_validate(real_skus)

    # No confiar en "Categoria / tipo" para decidir que es un accesorio: se
    # confirmo que varias filas de Paramont/Vision quedaron categorizadas como
    # "CAMERAS..." (heredado del encabezado de seccion del PDF de origen) aun
    # siendo mounts reales con la compatibilidad escrita en el propio Nombre
    # (ej. "Ceiling Mount for PAR-ALLDRXIRBD"). Se escanean TODAS las filas,
    # tanto Nombre como Descripcion, y se descarta cualquier fila cuyo unico
    # "match" sea su propio SKU (autorreferencia, no es un accesorio real).
    out_rows = []
    considered = 0
    for r in catalog_rows:
        nombre = r[idx['Nombre de equipo/producto']]
        modelo = r[idx['Modelo / SKU']]
        if not modelo:
            continue
        marca = r[idx['Marca']]
        proveedor = r[idx['Proveedor']]
        desc = r[idx['Descripcion']]
        own_sku = str(modelo).strip().upper()
        compatibles = extract_compatible_models(nombre or '', expand_and_validate)
        compatibles += extract_compatible_models(desc or '', expand_and_validate)
        seen = []
        for c in compatibles:
            if c.upper() != own_sku and c not in seen:
                seen.append(c)
        compatibles = seen
        if not compatibles:
            # Sin SKU exacto: si la fila es claramente un accesorio, intentar
            # un match por categoria generica (ej. "Corner Mount for Paramont
            # PTZ Cameras" -> todas las camaras PTZ reales de Paramont), pero
            # solo cuando el texto nombra marca + una palabra distintiva --
            # "Junction Box for Paramont Series Cameras" no alcanza (no dice
            # cual serie) y se deja sin match en vez de inventar un alcance.
            if looks_like_accessory(nombre):
                ya_agregado = set()
                for phrase in extract_raw_phrases(nombre or '') + extract_raw_phrases(desc or ''):
                    brand, keywords = find_category_hint(phrase, marcas_reales)
                    if not brand:
                        continue
                    for cam_sku, cam_nombre, cam_marca, cam_text in camera_candidates:
                        if cam_marca != brand or cam_sku in ya_agregado:
                            continue
                        if all(kw in cam_text for kw in keywords):
                            ya_agregado.add(cam_sku)
                            out_rows.append([
                                cam_sku, cam_nombre, cam_marca,
                                modelo, nombre, classify_tipo(nombre), marca,
                                proveedor,
                                'Match por categoria generica (no por SKU exacto) - verificar antes de cotizar',
                                f'Coincide por: {", ".join(keywords)}',
                            ])
            continue
        considered += 1
        scanned_is_acc = looks_like_accessory(nombre)
        for other_sku in compatibles:
            other_nombre, other_marca = nombre_marca_by_sku.get(other_sku.upper(), ('', ''))
            other_is_acc = looks_like_accessory(other_nombre)
            # Solo se acepta el par si UN lado es claramente el accesorio y el
            # otro no lo es -- si los dos lo son (dos accesorios que se acoplan
            # entre si) o ninguno lo es (dos equipos principales relacionados,
            # ej. decoder+servidor) se descarta: no hay forma confiable de
            # decidir cual va en "Modelo Camara" sin inventar.
            if scanned_is_acc == other_is_acc:
                continue
            if scanned_is_acc:
                cam_sku, cam_nombre, cam_marca = other_sku, other_nombre, other_marca
                acc_sku, acc_nombre, acc_marca = modelo, nombre, marca
            else:
                cam_sku, cam_nombre, cam_marca = modelo, nombre, marca
                acc_sku, acc_nombre, acc_marca = other_sku, other_nombre, other_marca
            out_rows.append([
                cam_sku, cam_nombre, cam_marca,
                acc_sku, acc_nombre, classify_tipo(acc_nombre), acc_marca,
                proveedor, 'Catalogo de proveedor (descripcion/nombre del fabricante)', '',
            ])

    ya_en_out = {(r[0].upper(), r[3].upper()) for r in out_rows}
    for cam_sku, acc_sku, acc_nombre, acc_marca, nota in PARES_VERIFICADOS_MANUALMENTE:
        if (cam_sku.upper(), acc_sku.upper()) in ya_en_out:
            continue
        cam_nombre, cam_marca = nombre_marca_by_sku.get(cam_sku.upper(), (None, None))
        if cam_nombre is None:
            continue  # la camara ya no existe en el catalogo actual, no agregar el par
        out_rows.append([
            cam_sku, cam_nombre, cam_marca,
            acc_sku, acc_nombre, classify_tipo(acc_nombre), acc_marca,
            '', FUENTE_COTIZACION_REAL, nota,
        ])
    return out_rows, considered


def write_sheet(wb, rows):
    if SHEET_NAME in wb.sheetnames:
        del wb[SHEET_NAME]
    # Insertarla justo despues de "Catalogo" si existe, si no al final.
    idx_pos = wb.sheetnames.index('Catalogo') + 1 if 'Catalogo' in wb.sheetnames else len(wb.sheetnames)
    ws = wb.create_sheet(SHEET_NAME, idx_pos)

    ws.append(HEADERS)
    for row in rows:
        ws.append(row)

    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(wrap_text=False)

    last_row = len(rows) + 1
    last_col_letter = ws.cell(row=1, column=len(HEADERS)).column_letter
    ref = f'A1:{last_col_letter}{last_row}'
    if last_row > 1:
        table = Table(displayName='TablaCompatibilidadAccesorios', ref=ref)
        table.tableStyleInfo = TableStyleInfo(
            name='TableStyleMedium2', showFirstColumn=False,
            showLastColumn=False, showRowStripes=True, showColumnStripes=False,
        )
        ws.add_table(table)

    ws.freeze_panes = 'A2'
    widths = [16, 34, 16, 16, 34, 22, 16, 22, 34, 30]
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[ws.cell(row=1, column=i).column_letter].width = w
    for row_dim in ws.row_dimensions.values():
        row_dim.height = 18


def main(catalogo_path):
    wb = openpyxl.load_workbook(catalogo_path)
    ws_cat = wb['Catalogo']
    headers = [c.value for c in next(ws_cat.iter_rows(min_row=1, max_row=1))]
    idx = {h: i for i, h in enumerate(headers)}
    catalog_rows = [tuple(c.value for c in row) for row in ws_cat.iter_rows(min_row=2)]

    rows, con_match = build_rows_from_catalog(catalog_rows, idx)
    write_sheet(wb, rows)
    wb.save(catalogo_path)

    exactos = [r for r in rows if r[8].startswith('Catalogo de proveedor')]
    categoria = [r for r in rows if r[8].startswith('Match por categoria')]
    reales = [r for r in rows if r[8].startswith('Cotizacion real')]
    print(f'Total de filas del catalogo escaneadas: {len(catalog_rows)}')
    print(f'Filas con al menos una compatibilidad detectada: {con_match}')
    print(f'Pares camara-accesorio escritos: {len(rows)} (exactos por SKU: {len(exactos)}, por categoria generica: {len(categoria)}, de cotizacion real verificada a mano: {len(reales)})')
    print(f'Camaras distintas cubiertas: {len(set(r[0] for r in rows))}')
    print('Tipos de accesorio en los pares escritos:')
    for tipo, n in Counter(r[5] for r in rows).most_common():
        print(f'  {n:4d}  {tipo}')
    print(f'Pestana "{SHEET_NAME}" escrita en: {catalogo_path}')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Uso: python generar_matriz_accesorios.py <catalogo.xlsx>')
        sys.exit(1)
    main(sys.argv[1])
