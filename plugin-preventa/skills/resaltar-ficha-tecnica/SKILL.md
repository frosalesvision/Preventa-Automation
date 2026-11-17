---
name: resaltar-ficha-tecnica
description: Resalta en amarillo, en la ficha técnica del fabricante (PDF), cada especificación que pide el cartel o pliego de una licitación, con el número de punto del cartel al margen, y dice qué puntos la ficha no respalda. Usar cuando el asesor pide subrayar, resaltar, marcar o "identificar con color" en la ficha técnica lo que solicita el cartel, o cuando el cartel exige aportar la ficha con lo solicitado identificado.
---

# Resaltar la ficha técnica contra el cartel

Los carteles suelen pedir *"aportar ficha técnica, donde se identifique
con color o subrayado lo solicitado"*. Este skill lo hace sobre el PDF
del fabricante y devuelve dos cosas: la ficha resaltada y la lista de lo
que la ficha **no** respalda, que es lo que de verdad le importa a quien
arma la oferta.

Probado el 2026-10-19 con 8 fichas de una misma licitación: cuatro
cámaras y dos grabadores Hanwha (en inglés y en español, tabla y
folleto), un monitor Dell y uno LG (impresión de la página web). **Falta
que lo use el equipo.**

## Lo que se entrega

- **Marcador amarillo** (no subrayado): la etiqueta de la fila y el valor
  que demuestra que se cumple. Así lo pidió preventa y se lee mejor.
- **Número rojo al margen** con el punto del cartel que cubre esa fila
  (`2·5·11` si cubre varios). En una portada con viñetas, va junto a la
  viñeta.
- Todo son **anotaciones**: se mueven o se borran en Acrobat o Edge, y
  salen al imprimir. El PDF original no se toca nunca.

## Los pasos

El script es [`scripts/resaltar_ficha.py`](scripts/resaltar_ficha.py).
Necesita PyMuPDF; si `import pymupdf` falla, instalalo con
`python -m pip install pymupdf` y decilo.

### 0. Si piden buscar la ficha

Bajala del sitio del fabricante, nunca de un distribuidor, y en español
si existe (probado el 2026-11-03):

- **Hanwha:** `https://supportportal.hanwhavision.com/global/products/<MODELO>-es`.
  La pestaña DataSheet lista los idiomas publicados; el PDF se baja
  directo (`DataSheet_<MODELO>_<fecha>_ES_....pdf`). **No todos los
  modelos tienen la ficha en español** (el QNO-C8083R solo la tiene en
  inglés, aunque su hermano QNV-C8083R sí). Si no hay, usá la de inglés
  y avisá: los carteles suelen exigir traducción oficial de lo que no
  esté en español. La ficha de un modelo hermano no sirve como reemplazo.
- **Hikvision:** la página de Latinoamérica (`hikvision.com/es-la/...`)
  trae el botón "Ficha Técnica", pero la descarga directa pide una
  verificación anti-bots. No la saltes: pedile a la persona que dé el
  clic en el navegador y decí dónde quedó el archivo.

### 1. Copiar los PDF a una carpeta aparte

La ficha y el cartel casi siempre llegan por Descargas o por correo.
Copiá cada uno a su propia carpeta nueva y vacía en tu carpeta temporal
de la sesión, y trabajá sobre las copias.

### 2. Leer los dos como texto, no como PDF

```
python -I scripts/resaltar_ficha.py texto "<ficha.pdf>" "<ficha.txt>"
python -I scripts/resaltar_ficha.py texto "<cartel.pdf o .docx>" "<cartel.txt>"
```

Leé los `.txt`. **No abras los PDF enteros con Read:** así cada página
entra como imagen además del texto y cuesta varias veces más. En la
prueba, el texto de los dos (ficha de 7 páginas y cartel de 3) fue unos
4.000 tokens. Si el script avisa de páginas sin texto (ficha
escaneada), decilo: este skill no hace OCR.

**Un solo cartel con varias líneas** ("LINEA 2. Cámara tipo bullet…")
es lo normal: emparejá cada línea con su ficha por el tipo de equipo y
sus números, no solo por el modelo que trae el cartel. En la prueba el
cartel nombraba el modelo equivocado en tres líneas (la PTZ decía el
modelo del ojo de pez; los dos grabadores, el mismo modelo). Si el
emparejamiento no es obvio, preguntá; si lo es, decí cuál usaste.

### 3. Armar el mapeo

Por cada punto del cartel, buscá en el texto de la ficha la fila que lo
respalda y anotala en un JSON (formato abajo). Criterio:

- **Se resalta lo que respalda el punto, no lo que se le parece.** Si la
  ficha dice "Appear/Disappear" y el cartel pide "objeto abandonado", se
  puede marcar como lo más cercano, pero va a la lista de brechas como
  equivalencia por confirmar.
- **Si la ficha dice algo distinto a lo pedido, la fila se resalta igual
  y va a la lista de brechas, primero.** El evaluador la va a buscar de
  todos modos. Ejemplo real: el cartel pedía PoE IEEE 802.3at y la ficha
  dice 802.3af Class 3.
- **Etiqueta y valor**, no la fila entera ni párrafos completos.
- **Números cortos.** Si una celda cubre muchos subpuntos (las
  analíticas 14.1 a 14.12), poné el número padre (`14`) una vez; el
  margen tiene unos 40 puntos de ancho.
- Copiá el texto **tal como sale en el `.txt`**, con sus paréntesis y
  símbolos (`Hallway view(90°/270°)`).

### 4. Resaltar

```
python -I scripts/resaltar_ficha.py resaltar "<ficha.pdf>" "<mapeo.json>" "<salida.pdf>"
```

Si dice **NO ENCONTRADOS**, corregí esas entradas (casi siempre es un
espacio, una coma o la `ocurrencia`) y volvé a correr hasta que no
falte nada. `--sin-numeros` lo genera sin los números rojos.

### 5. Revisarlo a ojo

```
python -I scripts/resaltar_ficha.py vista "<salida.pdf>" "<carpeta>" --juntas --dpi 55
```

Guarda las páginas con marcas lado a lado en un solo PNG: una imagen que
mirar en vez de una por página. Si algo no se lee, mirá esa página sola
(sin `--juntas`, con `--paginas N`). Que cada marca caiga en la fila
correcta y que ningún número quede cortado o encima de otro.

Lo que pasó en la prueba y cómo se arregla:

- **Una marca cayó en otra fila con el mismo texto** (`Support`, o
  `Según motor de` que también aparece dentro de "según motor de IA"
  más arriba, porque las mayúsculas no cuentan): agregale `fila`, o
  `ocurrencia` a la que ya tiene.
- **La celda `"*"` agarró la etiqueta de abajo**: en fichas web la
  etiqueta va arriba y el valor abajo; usá `valor_abajo`.

### 6. Entregar

Guardalo junto a la ficha original con el mismo nombre más
` - RESALTADO.pdf`, salvo que el asesor diga otra ruta; nunca encima del
original. Mandáselo y, en el mismo mensaje, la **tabla de brechas**:
punto del cartel, qué pide, qué dice la ficha (o "no aparece") y qué
hace falta. Lo que casi nunca está en una ficha y siempre hay que
avisar:

- NDAA, TAA y otras certificaciones de origen: carta del fabricante.
- Garantía, licenciamiento y accesorios incluidos: carta del fabricante.
- Especificaciones de un accesorio que el cartel exige junto al equipo
  (la tarjeta microSD de la cámara, por ejemplo): van en la ficha del
  accesorio, no en esta.
- Una versión distinta de la pedida (FIPS 140-3 cuando piden 140-2): se
  dice tal cual; decidir si basta es de preventa.

## Formato del mapeo

Dos ejemplos reales: una ficha de tabla
([`references/ejemplo-hanwha-xnv-a8084r.json`](references/ejemplo-hanwha-xnv-a8084r.json))
y una impresión de página web con la etiqueta arriba y el valor abajo
([`references/ejemplo-lg-65uh5f-b.json`](references/ejemplo-lg-65uh5f-b.json)).

```json
{
  "columna_valor_x": 240,
  "marcas": [
    {"pagina": 1, "valores": ["5MP Image Resolution"], "punto": "1"},
    {"pagina": 2, "fila": "Max. Framerate", "valores": ["H.265/H.264", "30fps/25fps(60Hz/50Hz)"], "punto": "2·5·11"},
    {"pagina": 3, "fila": "Digital Noise Reduction", "valores": ["*"], "punto": "8"},
    {"pagina": 4, "fila": "Based on AI Engine", "ocurrencia": 2, "valores": ["People counting"]}
  ]
}
```

| Campo | Qué es |
|---|---|
| `pagina` | página de la ficha, desde 1 |
| `fila` | la etiqueta de la fila de la tabla. Se resalta, y los `valores` se buscan **solo en esa franja horizontal**. Sin `fila`, cada valor se busca en toda la página y se marca la primera vez que aparece. Si la etiqueta ocupa dos renglones, poné solo el primero (`"Máx. Frecuencia de"`) |
| `ocurrencia` | si la etiqueta sale varias veces en la página, cuál (1 = la primera) |
| `valor_abajo` | `true` cuando el valor va debajo de la etiqueta y no a la derecha (fichas impresas de una página web). Los `valores` se buscan en los renglones de abajo, en la misma columna |
| `valores` | los textos a resaltar. `"*"` = toda la celda de valor de la fila (con `valor_abajo`, el primer renglón de abajo), útil cuando el texto trae símbolos raros (`WiseNRⅡ`) |
| `punto` | el número de punto del cartel que va al margen. Vacío o ausente = sin número |
| `columna_valor_x` | dónde empieza la columna de valores, en puntos; solo lo usa `"*"`. Si no está, la celda empieza justo después de la etiqueta |

Las mayúsculas no importan al buscar.
