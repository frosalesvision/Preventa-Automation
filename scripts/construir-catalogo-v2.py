# -*- coding: utf-8 -*-
"""
Construye la propuesta v2 del catalogo sobre la COPIA de trabajo:
  - inserta la columna 'Subcategoria' junto a 'Categoria'
  - reclasifica las 2.552 filas con la taxonomia de 2 niveles
  - reescribe las formulas de colones (se corrieron al insertar la columna)
  - crea las pestanas LEEME, Guia de columnas y Glosario de categorias
  - deja todo con un formato legible y consistente

El original NO se toca. Salida:
  Desktop/AUTOMATIZACIONES_IA/_trabajo/Catalogo PROPUESTA v2.xlsx
"""
import openpyxl, warnings, os, sys
from collections import Counter, defaultdict, OrderedDict
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from taxonomia import clasificar, TAXONOMIA, CATEGORIAS
warnings.filterwarnings("ignore")

COPIA = os.path.join(os.environ["USERPROFILE"], "Desktop", "AUTOMATIZACIONES_IA",
                     "_trabajo", "Catalogo PROPUESTA v2.xlsx")

# ---------------- paleta ----------------
TINTA = "1F4E5F"      # titulos
BANDA = "2E7D8F"      # encabezados de tabla
SECCION = "DCEAEE"    # bandas de seccion
SUAVE = "F4F9FA"      # filas alternas
GRIS = "6B7B80"
BLANCO = "FFFFFF"

F_TITULO = Font(bold=True, size=18, color=TINTA)
F_SUB = Font(size=11, italic=True, color=GRIS)
F_SECCION = Font(bold=True, size=12, color=TINTA)
F_TH = Font(bold=True, size=10, color=BLANCO)
F_BODY = Font(size=10.5)
F_BODY_B = Font(size=10.5, bold=True)
F_MONO = Font(size=10, color=GRIS)
R_BANDA = PatternFill("solid", fgColor=BANDA)
R_SECCION = PatternFill("solid", fgColor=SECCION)
R_SUAVE = PatternFill("solid", fgColor=SUAVE)
BORDE = Border(bottom=Side(style="thin", color="C9D8DC"))
WRAP = Alignment(wrap_text=True, vertical="top")
TOP = Alignment(vertical="top")


def titulo(ws, texto, sub=None):
    ws["A1"] = texto
    ws["A1"].font = F_TITULO
    ws.row_dimensions[1].height = 30
    if sub:
        ws["A2"] = sub
        ws["A2"].font = F_SUB
        ws.row_dimensions[2].height = 18


def seccion(ws, fila, texto, ancho):
    ws.cell(fila, 1).value = texto
    ws.cell(fila, 1).font = F_SECCION
    for c in range(1, ancho + 1):
        ws.cell(fila, c).fill = R_SECCION
    ws.row_dimensions[fila].height = 22
    return fila + 1


def cabecera(ws, fila, cols):
    for i, t in enumerate(cols, start=1):
        c = ws.cell(fila, i)
        c.value = t
        c.font = F_TH
        c.fill = R_BANDA
        c.alignment = Alignment(wrap_text=True, vertical="center")
    ws.row_dimensions[fila].height = 26
    return fila + 1


def fila_datos(ws, fila, valores, alterna=False, negrita_primera=False):
    for i, v in enumerate(valores, start=1):
        c = ws.cell(fila, i)
        c.value = v
        c.font = F_BODY_B if (negrita_primera and i == 1) else F_BODY
        c.alignment = WRAP
        c.border = BORDE
        if alterna:
            c.fill = R_SUAVE
    return fila + 1


# ==========================================================================
print("abriendo la copia de trabajo...")
wb = openpyxl.load_workbook(COPIA)
ws = wb["Catalogo"]
n_filas = ws.max_row

# ---------------- 1. clasificar antes de mover nada ----------------
print("clasificando...")
clasif = {}
orig_por_destino = defaultdict(Counter)
ejemplo_por_par = {}
for r in range(2, n_filas + 1):
    nombre = ws.cell(r, 1).value
    cat_orig = ws.cell(r, 24).value
    if nombre is None and cat_orig is None:
        continue
    cat, sub, _ = clasificar(nombre, cat_orig)
    clasif[r] = (cat, sub)
    if cat_orig:
        orig_por_destino[cat][str(cat_orig)] += 1
    if (cat, sub) not in ejemplo_por_par and nombre:
        ejemplo_por_par[(cat, sub)] = str(nombre)[:70]
print("  filas clasificadas:", len(clasif))

# ---------------- 2. insertar la columna Subcategoria ----------------
print("insertando columna Subcategoria en la posicion 5...")
ws.insert_cols(5)
ws.cell(1, 5).value = "Subcategoria"
ws.cell(1, 5).font = ws.cell(1, 4).font.copy()
ws.cell(1, 5).fill = ws.cell(1, 4).fill.copy()

for r, (cat, sub) in clasif.items():
    ws.cell(r, 4).value = cat
    ws.cell(r, 5).value = sub

# las formulas de colones se corrieron: Precio USD ahora es G, especial es I
print("reescribiendo las formulas de colones...")
F_CRC = '=IF({0}{1}="","",IF(TipoCambioVenta="","Actualizar TC",ROUND({0}{1}*TipoCambioVenta,2)))'
for r in range(2, n_filas + 1):
    ws.cell(r, 8).value = F_CRC.format("G", r)    # Precio CRC   <- Precio USD (G)
    ws.cell(r, 10).value = F_CRC.format("I", r)   # Especial CRC <- Especial USD (I)

# encabezado mas explicito para la columna de trazabilidad (ahora la 25)
ws.cell(1, 25).value = "Categoria original del proveedor (referencia, NO filtrar por aqui)"

ws.tables["TablaCatalogo"].ref = "A1:Y%d" % n_filas
ws.column_dimensions["E"].width = 26
ws.column_dimensions["D"].width = 24
ws.column_dimensions["Y"].width = 38
ws.freeze_panes = "F2"   # deja visibles nombre, marca, SKU, categoria y subcategoria

# validacion de categoria para quien agregue filas a mano
dv = DataValidation(type="list", formula1='"%s"' % ",".join(CATEGORIAS), allow_blank=True)
dv.error = "Usá una de las categorías de la pestaña Glosario de categorias."
dv.errorTitle = "Categoría no válida"
dv.prompt = "Elegí una categoría de la lista. Ver la pestaña Glosario de categorias."
ws.add_data_validation(dv)
dv.add("D2:D%d" % n_filas)

# ---------------- 3. pestana LEEME ----------------
print("creando LEEME...")
if "LEEME" in wb.sheetnames:
    del wb["LEEME"]
le = wb.create_sheet("LEEME", 0)
le.sheet_view.showGridLines = False
le.sheet_properties.tabColor = TINTA
titulo(le, "Catálogo de productos por proveedor",
       "Todos los equipos y materiales que Grupo Visión puede cotizar, con su precio y su proveedor, en un solo lugar.")
for col, w in zip("ABCD", (30, 52, 26, 30)):
    le.column_dimensions[col].width = w

f = 4
f = seccion(le, f, "Empezá por acá", 4)
f = cabecera(le, f, ["Si querés…", "Hacé esto", "", ""])
pasos = [
    ("Buscar un equipo para cotizar",
     "Andá a la pestaña Catalogo y filtrá por Categoria y Subcategoria. Si no sabés qué categoría buscar, mirá el Glosario de categorias.", "", ""),
    ("Saber qué significa una columna",
     "Pestaña Guia de columnas: explica las 25 columnas, una por una.", "", ""),
    ("Agregar productos de un proveedor nuevo",
     "No los escribas a mano. Dejá el PDF o el Excel del proveedor en la carpeta Catalogos Proveedor y pedile a la IA que actualice el catálogo.", "", ""),
    ("Actualizar el tipo de cambio",
     "Pestaña Tipo de Cambio, celdas B3 y B4. Todos los precios en colones se recalculan solos.", "", ""),
]
alt = False
for p in pasos:
    f = fila_datos(le, f, p, alt, True)
    le.row_dimensions[f - 1].height = 30
    alt = not alt

f += 1
f = seccion(le, f, "Qué hay en cada pestaña", 4)
f = cabecera(le, f, ["Pestaña", "Para qué sirve", "Quién la llena", "¿Se edita a mano?"])
pestanas = [
    ("LEEME", "Esta hoja. El punto de entrada para alguien que recién llega.", "Nadie, es fija", "No"),
    ("Catalogo", "El catálogo en sí: un producto por fila, con precio, proveedor y categoría.", "La IA, leyendo los documentos de los proveedores", "No. Si hay que corregir algo, pedirlo por chat"),
    ("Guia de columnas", "Qué significa cada una de las 25 columnas del catálogo.", "Nadie, es fija", "No"),
    ("Glosario de categorias", "Las categorías y subcategorías, qué incluye cada una y cómo las llama el proveedor en inglés.", "Nadie, es fija", "No"),
    ("Compatibilidad de Accesorios", "Qué montura, base o housing sirve para cada modelo de cámara.", "La IA, con un script", "No"),
    ("Tipo de Cambio", "El tipo de cambio colones/dólar que usan todas las fórmulas.", "Preventa", "SÍ — celdas B3 y B4"),
    ("Reglas de Descuento", "Qué descuento da cada proveedor y de qué depende. Determina el costo real de Grupo Visión.", "Preventa / compras", "SÍ"),
    ("Regimen Fiscal Clientes", "Qué clientes son exentos de impuesto y qué porcentaje se le cobra a cada uno.", "Preventa", "SÍ"),
    ("Tarifario Mano de Obra", "Precios fijos de instalación por unidad: por cámara, por poste, programación, capacitación.", "Preventa / operaciones", "SÍ"),
    ("Proporciones Instalacion", "Cuánto material lleva cada unidad instalada: metros de tubo, gazas, cable.", "Preventa / operaciones", "SÍ"),
]
alt = False
for p in pestanas:
    f = fila_datos(le, f, p, alt, True)
    le.row_dimensions[f - 1].height = 30
    alt = not alt

f += 1
f = seccion(le, f, "Reglas de oro", 4)
reglas = [
    "El precio del catálogo es PRECIO DE LISTA. No es lo que Grupo Visión paga. El costo real depende del descuento del proveedor y del registro del proyecto.",
    "Mirá siempre la Fecha de última actualización. Si tiene más de 2 meses, confirmá el precio con el proveedor antes de cotizar.",
    "Las columnas de precio en colones son fórmulas. No escribas un número encima: cambiá el tipo de cambio en su pestaña.",
    "No hay filas repetidas: un producto es el mismo si coinciden Modelo/SKU y Proveedor. El mismo equipo de dos proveedores son dos filas válidas.",
    "Si una categoría dice Sin clasificar, es que el producto no se pudo clasificar automáticamente. Avisá y se corrige; no lo dejes así en una cotización.",
]
for i, t in enumerate(reglas, 1):
    le.cell(f, 1).value = "%d." % i
    le.cell(f, 1).font = F_BODY_B
    le.cell(f, 1).alignment = TOP
    le.cell(f, 2).value = t
    le.cell(f, 2).font = F_BODY
    le.cell(f, 2).alignment = WRAP
    le.merge_cells(start_row=f, start_column=2, end_row=f, end_column=4)
    le.row_dimensions[f].height = 30
    f += 1

f += 1
le.cell(f, 1).value = "¿Dudas? Preguntá por chat a la IA de preventa: puede buscar en el catálogo, explicar una columna y armar la cotización."
le.cell(f, 1).font = F_SUB
le.merge_cells(start_row=f, start_column=1, end_row=f, end_column=4)

# ---------------- 4. Glosario de categorias ----------------
print("creando Glosario de categorias...")
if "Glosario de categorias" in wb.sheetnames:
    del wb["Glosario de categorias"]
gl = wb.create_sheet("Glosario de categorias")
gl.sheet_view.showGridLines = False
titulo(gl, "Glosario de categorías",
       "Las 16 categorías del catálogo, qué entra en cada una, y cómo las llama el proveedor en sus documentos en inglés.")
for col, w in zip("ABCDE", (26, 26, 44, 46, 52)):
    gl.column_dimensions[col].width = w

QUE_INCLUYE = {
    "Camara": "Todo lo que capta imagen. La subcategoría dice de qué tipo es.",
    "Grabacion y video": "Donde se graba y se procesa el video.",
    "Almacenamiento": "Discos y tarjetas donde queda guardado el video.",
    "Monitor y visualizacion": "Pantallas para ver el video o mostrar contenido.",
    "Optica": "Lentes que se montan sobre una cámara.",
    "Accesorio de instalacion": "Lo que sujeta, protege o adapta un equipo. No es el equipo en sí.",
    "Control de acceso": "Puertas, lectores, credenciales y torniquetes.",
    "Deteccion de incendio": "Paneles, detectores y avisadores de incendio.",
    "Alarma e intrusion": "Alarmas contra robo: paneles, sensores y botones de pánico.",
    "Audio": "Micrófonos, altavoces y audio sobre IP.",
    "Red y conectividad": "Lo que lleva la señal: switches, fibra, extensores.",
    "Energia": "Lo que da corriente: fuentes, UPS, baterías, inyectores PoE, solar.",
    "Materiales de instalacion": "Lo que se consume al instalar: tubería, cable, ferretería.",
    "Software y licencias": "Licencias de VMS, suscripciones en la nube e integraciones.",
    "Equipo de computo": "Computadoras y periféricos. Hoy vacía; reservada para cuando se carguen.",
    "Servicios": "Trabajo, no producto: instalación y capacitación.",
}

f = 4
f = cabecera(gl, f, ["Categoría", "Subcategoría", "Qué incluye", "Ejemplo real del catálogo",
                     "Cómo lo llama el proveedor (en sus documentos)"])
for cat, subs in TAXONOMIA:
    if cat == "Sin clasificar":
        continue
    gl.cell(f, 1).value = cat
    gl.cell(f, 1).font = Font(bold=True, size=11, color=TINTA)
    gl.cell(f, 3).value = QUE_INCLUYE.get(cat, "")
    gl.cell(f, 3).font = F_BODY
    gl.cell(f, 3).alignment = WRAP
    origs = [o for o, _ in orig_por_destino[cat].most_common(6)]
    gl.cell(f, 5).value = " · ".join(origs) if origs else "—"
    gl.cell(f, 5).font = F_MONO
    gl.cell(f, 5).alignment = WRAP
    for c in range(1, 6):
        gl.cell(f, c).fill = R_SECCION
    gl.row_dimensions[f].height = 32
    f += 1
    alt = False
    for sub in subs:
        ej = ejemplo_por_par.get((cat, sub))
        if not ej:
            continue
        f = fila_datos(gl, f, ["", sub, "", ej, ""], alt)
        alt = not alt
    f += 1

f += 1
gl.cell(f, 1).value = "Sin clasificar"
gl.cell(f, 1).font = Font(bold=True, size=11, color="963425")
gl.cell(f, 3).value = ("Productos que no se pudieron clasificar automáticamente (~2% del catálogo). "
                       "No es un error grave, pero conviene corregirlos: avisá y se reclasifican.")
gl.cell(f, 3).font = F_BODY
gl.cell(f, 3).alignment = WRAP
gl.row_dimensions[f].height = 32

f += 2
gl.cell(f, 1).value = ("Nota: la última columna del catálogo guarda la categoría original del proveedor, solo como referencia. "
                       "Los proveedores usan encabezados de sección como \"IP CAMERAS & NVR's\", \"HDD FOR TODAY\" o \"30-Day\", "
                       "o ponen la marca como si fuera categoría. Por eso se normalizó: para filtrar, usá siempre Categoria y Subcategoria.")
gl.cell(f, 1).font = F_SUB
gl.cell(f, 1).alignment = WRAP
gl.merge_cells(start_row=f, start_column=1, end_row=f, end_column=5)
gl.row_dimensions[f].height = 46

wb.save(COPIA)
print("")
print("GUARDADO:", COPIA)
print("pestanas:", wb.sheetnames)
