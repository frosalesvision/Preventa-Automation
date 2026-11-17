---
name: comparar-especificaciones
description: Compara los productos del catálogo de Grupo Visión contra las especificaciones de un pliego, cartel, estudio de mercado o lista de equipos, línea por línea, y entrega una tabla con el porcentaje de match de cada modelo, qué cumple, qué le falta y qué no se pudo comprobar, con código, producto, precio de compra y proveedor, verificando contra la ficha oficial del fabricante (en internet si el catálogo no trae el dato). Tres modos - los más cercanos de cualquier marca, una sola marca, o una marca más los más cercanos de las demás. Usar cuando piden ver qué productos hacen match con lo que piden, el porcentaje de cumplimiento, qué tan cerca está una marca (ej. Hanwha) de las especificaciones, o lo más parecido que tenemos, incluso con un PDF escaneado.
---

# Comparar especificaciones con el catálogo

Toma un documento con especificaciones por línea y dice, por cada línea, qué
modelos del catálogo se acercan más y **en qué porcentaje**, con lo que cumplen,
lo que les falta y lo que no se pudo comprobar. La vista previa va **en el chat**;
un PDF o un Excel, solo si lo piden.

**Es análisis, no cotización.** No se crea nada en `CLIENTES` ni en los Excels
de control (R30). Si después piden cotizar, sigue
[`nueva-cotizacion`](../nueva-cotizacion/SKILL.md).

## Por qué existe

Fabián, 2026-11-17, con un pliego municipal de 45 páginas escaneadas: *"creo que
es la segunda vez que tenemos que hacer algo similar... poder poner si ocupamos
los productos más cercanos a nivel especificaciones, o si ocupamos solo una marca
para ver qué tan cercano está, o una marca y a su vez los más cercanos"*. La
primera vez fue el estudio de mercado de Alajuela (2026-11-05), que dio origen al
"Modo pliego" de [`buscar-equipo`](../buscar-equipo/SKILL.md) (R30). Este skill
sigue donde ese modo termina: le pone número a la cercanía y la verifica contra
la ficha de cada modelo (R33).

## Los tres modos

| Modo | Qué entrega | Cuándo |
|---|---|---|
| `cercanos` | una tabla, todas las marcas, las 2 mejores por línea | "lo más parecido que tenemos", sin marca |
| `marca` | una tabla, solo esa marca, la mejor por línea; si no tiene, "no hay" | "solo Hanwha", "qué tan cerca está Axis" |
| `marca+cercanos` | dos tablas: la mejor de la marca y la mejor de las demás | nombran una marca y además quieren ver lo más cercano |

Si el pedido ya lo dice, no preguntes. Si no, preguntá una sola vez y recomendá:
con una marca nombrada, `marca+cercanos` (R30: se mira en todas las marcas aunque
el pedido nombre una); sin marca, `cercanos`.

## Paso 1 — Leer el documento

Copiá el documento a una carpeta nueva y vacía de la carpeta temporal de la
sesión y trabajá sobre la copia.

- **Con texto** (`.docx` o PDF digital):
  `python -I ../resaltar-ficha-tecnica/scripts/resaltar_ficha.py texto "<doc>" "<doc.txt>"`
- **Escaneado** (el script anterior avisa "páginas sin texto"; no hace OCR):

  ```
  python -I scripts/paginas_a_imagen.py "<doc.pdf>" "<carpeta>" [--paginas 1-10]
  ```

  Deja una imagen por página recortada al contenido (`c01.png`…). Leelas con
  Read, varias por mensaje. En el caso real, 45 páginas se leyeron bien con el
  zoom por defecto. Si alguna página ya trae texto, el script lo dice: esas,
  con `resaltar_ficha.py texto`, que cuesta mucho menos.

Avisá al asesor por dónde vas si el documento es largo: leer 45 imágenes lleva
un rato.

## Paso 2 — Decir qué pide y armar `requisitos.json`

Primero el resumen que pide el Modo pliego (§2 de `buscar-equipo`): trámite,
cantidades (si no vienen, decilo), lo que pide sin línea de precio, lo que
excluye marcas con la página que lo dice, y lo que no cuadra. Si el texto parece
copiado de la ficha de una marca, decilo como impresión: el modelo que calza al
100 % puede no estar en el catálogo (Avigilon, R24).

Después armá `requisitos.json` en la carpeta de trabajo:

```json
{
  "documento": "Equipos.pdf (municipalidad), 45 págs.",
  "lineas": [
    {"id": "L4", "nombre": "Bullet 5 MP",
     "requisitos": [
       {"n": 1, "etiqueta": "bullet 5 MP", "texto": "Formato bullet, resolución ≥ 2592×1944"},
       {"n": 2, "etiqueta": "1/2,8\"", "texto": "CMOS 1/2,8\" (o mayor)"}
     ]}
  ],
  "generales": [{"texto": "NDAA 889", "fuente": "pág. 43"}],
  "excluidas": [{"marca": "Hikvision", "motivo": "NDAA 889", "fuente": "pág. 43"}]
}
```

- **Entre 6 y 20 requisitos por línea**, los que separan un modelo de otro. Lo
  que se repite igual en todas (la lista de protocolos, los eventos de analítica
  idénticos) va una vez en `generales`, salvo que una marca pueda fallarlo.
- **Agrupá lo que va junto** ("IP66, IP67, IK10, NEMA 4X" es un requisito: cumple
  solo si cumple todo). Así el porcentaje no se infla con renglones fáciles.
- **La `etiqueta` es lo que se ve en la tabla**: corta, con el número
  ("≤13 W PoE", "-40 a +60 °C").
- Un requisito general que aplica a la línea (NDAA, garantía de 5 años) también
  va como requisito numerado de esa línea, para que cuente.
- `excluidas`: las marcas que el documento deja fuera. NDAA 889 nombra a
  Hikvision y Dahua; EZVIZ es de Hikvision. Epcom vende equipo Hikvision con su
  marca: si aparece, avisá.

Mostrá el resumen y la lista de líneas antes de seguir. Si algo no se entiende
(una línea sin título, un tamaño que no se ve), preguntá.

## Paso 3 — Candidatos del catálogo

Con [`buscar_catalogo.py`](../buscar-equipo/scripts/buscar_catalogo.py), como en
el Modo pliego (§3 de `buscar-equipo`): `--regex`, `--cat`, `--por-marca`,
`--detalle`, `--marca`. Por línea, 1 o 2 candidatos de la marca pedida y 2 o 3
de las demás (en modo `marca`, solo de esa marca).

- Las descripciones del catálogo solo sirven para **elegir a quién verificar**,
  nunca para decir que cumple.
- `INVID-MS-xxxx` es el Milesight `MS-xxxx` que vende InVidTech; `INVID-TS…` es
  una Milesight de tráfico. La ficha es la de Milesight.
- "Mínimo 3 lentes" lo cumple una de 4. Lo de más cumple (más resolución, más
  zoom, sensor más grande); lo de menos no.
- Anotá el código del catálogo (columna `Modelo / SKU`) de cada candidato: la
  verificación lo lleva para cruzar el precio sin errores.

## Paso 4 — Verificar contra la ficha oficial

Por cada candidato y cada requisito: **`C`** cumple, **`N`** no cumple (con el
valor real), **`?`** no se pudo comprobar. Reglas:

- **Solo la ficha o la página oficial del fabricante** cuentan. Un distribuidor,
  únicamente si no hay oficial, y se anota "fuente no oficial".
- **Si la ficha no lo menciona, es `?`, no `N`.** Si la ficha trae la lista
  completa del dato y no está (las clases IP, los perfiles ONVIF, las entradas
  de energía), es `N`.
- **Capacidad útil, no bruta.** Calculala con las bahías y el RAID; si el
  fabricante dice el útil, vale el suyo.
- **Lo que viene en la caja** (inyector, tarjeta SD) se ve en el manual.
- **NDAA:** `C` si el fabricante lo declara, para el modelo o para toda su línea;
  decí cuál de las dos.

Con más de 6 o 7 modelos, encargalo a subagentes en paralelo, agrupados por marca
y familia (8 a 10 modelos cada uno). El encargo, listo para copiar, está en
[`references/encargo-verificacion.md`](references/encargo-verificacion.md). Cada
uno escribe un `verif_<n>.json` con este formato, una entrada por modelo y línea:

```json
[{"linea": "L4", "marca": "Pelco", "modelo": "SRXP4-5V10-EBT-IR",
  "codigo": "SRXP4-5V10-EBT-IR",
  "fuentes": ["https://www.pelco.com/..."],
  "items": [{"n": 1, "estado": "C", "dato": "bullet 2592x1944"},
            {"n": 2, "estado": "N", "dato": "IK08; piden IK10"}],
  "notas": "Caja incluida, gris Pantone 427C"}]
```

Un item por requisito, en el orden de `requisitos.json`. En el caso real, 6
subagentes verificaron 58 pares modelo-línea en 15 a 30 minutos cada uno. Decile
al asesor que va a tardar y seguí con lo que no dependa de eso.

## Paso 5 — Calcular y armar las tablas

```
python -I scripts/puntaje_match.py "<requisitos.json>" "<carpeta con verif_*.json>" --modo marca+cercanos --marca Hanwha --salida "<carpeta>"
```

- **Match** = requisitos con `C` ÷ requisitos de la línea. **"Hasta X %"** =
  si lo que quedó en `?` sale bien.
- Cruza cada modelo con el catálogo: código, producto, proveedor, **precio de
  compra** (el costo, no el precio al cliente) y días del precio, con ⚠ cuando
  pasa de 60 (R12). Si lo venden varios proveedores, toma el precio más reciente
  y lo dice.
- Ordena por match, después por "hasta" y después por precio. `--elegir
  L13=XNP-C9303RW` fuerza el elegido de la marca y `--elegir L13o=...` el de las
  otras (por ejemplo, el que tiene limpiaparabrisas cuando empatan).
- Se niega si a una verificación le falta un requisito, los trae en otro orden o
  usa otro estado que no sea C, N o ?. Lo de una marca excluida no entra.
- Deja `tablas.md` y `resultado.json` (todo, para un PDF después).

## Paso 6 — Mostrar la vista previa en el chat

Columnas: **Línea · Código · Producto · Proveedor · Compra (días) · Match ·
Cumple · Falta · Sin comprobar.** Marca y proveedor siempre (R30). Si todas las
filas de una tabla tienen el mismo proveedor, puede ir una vez arriba.

Antes de las tablas, el resumen del Paso 2 y cómo leer el porcentaje. Después:

- **Lo que se concluye:** las líneas más altas y las más flojas; por línea, si
  gana la marca pedida o otra.
- **Lo que hay que reconfirmar:** precios viejos, descontinuados, datos del
  catálogo que la ficha contradice.
- **Cómo se calificó lo dudoso** (NDAA por declaración general, analítica que la
  ficha no menciona).
- **Lo que no está en el catálogo** y calzaría mejor (la marca de la que se
  copió el pliego), con a quién pedirle precio.

Ninguna fila se presenta como "cumple" si no tiene 100 % verificado; aun así,
"calza con la ficha" no reemplaza la confirmación del fabricante.

## Paso 7 — Lo que sigue (solo si lo piden)

- **PDF o Excel:** desde `resultado.json`. Un modelo por renglón, con su línea
  repetida (R30). Preguntá dónde guardarlo; nunca en `CLIENTES` sin que lo pidan.
- **Fichas resaltadas** de los elegidos:
  [`resaltar-ficha-tecnica`](../resaltar-ficha-tecnica/SKILL.md).
- **Pedido de precio** de lo que no está en el catálogo: borrador en el chat, sin
  enviar.
- **Registro con un fabricante (R5):** la tabla del modo `marca`, con sus
  brechas; registrar igual lo decide preventa.
- **Cotizar:** `nueva-cotizacion`.

## Lo que se aprendió en el caso real (2026-11-17)

- **El catálogo se equivoca a veces.** Una cámara de placas decía "IR 590 ft" y
  su ficha dice 50 m. Por eso se verifica todo contra la ficha.
- **Descontinuados:** Axis P1467-LE y P1468-LE, la Arecont Omni G2 20 MP y la
  pantalla InVid IFP75 seguían en el catálogo. La ficha lo dice: anotalo.
- **Grabadores Hanwha XRN:** el RAID 6 va en arreglos de 8 discos, así que con
  16 discos se pierden 4. Los servidores WAVE y BLAZE anuncian la capacidad
  útil en RAID 5.
- **Hanwha Road AI** (sus cámaras de placas) publica los países soportados, y
  Costa Rica no está.
- **2560×1920 no es 2592×1944.** Varias "5 MP" no llegan a la resolución pedida.
- **Sensor:** 1/1,8" es más grande que 1/2,5", y este que 1/2,8". Más grande
  cumple.
- **Los accesorios que pide el pliego** (una caja RAL 9003, el inyector) se
  verifican en la ficha del accesorio o en el manual, no en la de la cámara.
- **El pliego se había copiado de Avigilon**, y una línea de una Pelco Sarix
  Pro 4: las dos marcas son de Motorola. Avigilon casi no está en el catálogo
  (R24) y Pelco solo con dos bullets de hace casi dos años.

## Estado

Probado el 2026-11-17 con un pliego real escaneado de 15 líneas, en modo
`marca+cercanos` con Hanwha: `puntaje_match.py` dio los mismos 58 resultados que
el análisis hecho a mano. También se probaron los otros dos modos, el rechazo de
verificaciones mal armadas y la marca excluida. **Falta que lo use el equipo** y
comprobar que se activa con el plugin instalado.
