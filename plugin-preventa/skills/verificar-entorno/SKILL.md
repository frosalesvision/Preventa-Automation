---
name: verificar-entorno
description: Revisa qué accesos y conexiones están listos para trabajar con el plugin de preventa (carpeta compartida de cotizaciones, Excels de referencia, configuración de Bitrix24, los dos Excels de control de cotizaciones) y entrega un checklist de qué falta; también explica la instalación inicial completa (Claude Code, el plugin, la cuenta de OneDrive de la empresa, la extensión de Chrome) para alguien que recién empieza. Usar como primer paso al iniciar una sesión de preventa, cuando el usuario pregunta "qué me falta configurar", "está todo listo", "revisá el entorno", "qué necesito instalar", "cómo empiezo", o cuando otro skill del plugin (armar-cotizacion, sync-bitrix) falla por falta de acceso a algo.
---

# Verificar entorno de preventa

## 0. Instalación inicial (primera vez que alguien usa este plugin)

Si el usuario recién está empezando (primera conversación, o pregunta
"qué necesito instalar"), explicale estos pasos **en este orden**, en
lenguaje simple — no asumas que sabe qué es un plugin o un MCP:

1. **Tener Claude Code instalado y abierto.** Si ya está viendo esta
   conversación, este paso ya está listo — no hace falta nada más acá.
2. **Instalar el plugin `preventa`** (una sola vez por computadora):
   ```
   /plugin marketplace add frosalesvision/Preventa-Automation
   /plugin install preventa@preventa-automation
   ```
   (Repo privado — necesita acceso de lectura en GitHub, con `gh auth
   login` ya configurado. Si no sabe qué es esto, pedirle ayuda a quien
   le dio el acceso.)
3. **Tener la cuenta de Grupo Visión conectada a OneDrive en Windows**
   — así sincroniza `CLIENTES` automáticamente. Si ya usa Outlook/Teams
   con su cuenta de la empresa en esta computadora, normalmente esto ya
   está. Se confirma en el paso 2 del checklist de abajo.
4. **Agregar los dos accesos directos de Excel de control de
   cotizaciones** — ver paso 4 del checklist de abajo, son pasos
   puntuales de un solo uso.
5. **(Recomendado, no obligatorio) Instalar la extensión "Claude for
   Chrome"** e iniciar sesión con la misma cuenta que usa acá, en el
   Chrome donde también tiene abierta su cuenta de Grupo Visión
   (Outlook/SharePoint). Esto permite que Claude ayude con tareas que
   necesitan navegador (ej. revisar un archivo compartido puntual) —
   no es necesario para el día a día, pero conviene tenerlo listo.

Después de esto, decile a Claude **"revisá el entorno"** — corre el
checklist de abajo y confirma qué quedó bien y qué falta.

Ejecutá estas 5 verificaciones en orden y compilá un checklist final. No
asumas nada que no hayas comprobado con una herramienta (Read/Glob/Bash) —
si no podés comprobar algo, repórtalo como "❌ No se pudo verificar" con el
motivo, no como si estuviera listo.

## 1. Configuración de Bitrix24

Leé el archivo `.mcp.json` que está en la raíz de este plugin (dos niveles
arriba de este SKILL.md, es decir `../../.mcp.json` relativo a esta carpeta).

- Si el archivo no existe, o existe pero `mcpServers` está vacío (`{}`):
  marcalo como **no configurado**.
- Si `mcpServers` tiene una entrada (buscá una clave que contenga
  "bitrix"): marcalo como **configurado** y mostrá el nombre de la entrada
  (nunca muestres el valor de `url`, `env` u otros campos si contienen un
  webhook o API key real).
- Revisá también si existe `../../.env` con `BITRIX24_WEBHOOK_URL` con
  valor no vacío, como señal adicional.

## 2. Carpeta compartida de cotizaciones (CLIENTES)

En Windows, la carpeta compartida real de SharePoint/OneDrive Business
**no siempre está bajo la carpeta `OneDrive` normal del usuario** — puede
sincronizar en una ruta separada con el nombre del tenant/librería (ej.
`C:\Users\<usuario>\<Nombre Tenant>\<Nombre Librería>`). Antes de
preguntarle nada al usuario, intentá auto-detectarla:

1. Con PowerShell, leé el registro en
   `HKCU:\Software\Microsoft\OneDrive\Accounts\Business1\Tenants` (y
   `Business2`, etc. si existe más de una cuenta configurada) — cada
   valor bajo esa clave es `<ruta local completa> : <id>`. Ahí está la
   ruta real de cada librería sincronizada, sin adivinar.
2. Buscá entre esos valores una ruta cuyo nombre final contenga algo
   como "CLIENTES" (puede variar). Si la encontrás, listala (Bash `ls`
   o Glob) para confirmar que es legible.
3. Si no hay cuenta de OneDrive Business configurada, o ninguna ruta
   coincide, recién ahí **preguntale al usuario** la ruta local exacta.

Si falla el acceso (no existe, sin permisos, cuenta no firmada),
reportalo como **no accesible** con el motivo exacto — no reintentes
rutas inventadas ni asumas una ubicación por defecto. Si el registro
no tiene nada todavía (cuenta recién agregada), puede ser que OneDrive
esté en su primera sincronización — decilo explícitamente, no lo trates
como error permanente.

## 3. Excels de referencia en la carpeta compartida

Una vez confirmado el acceso del paso 2, buscá archivos `.xlsx`/`.xlsm`
dentro de esa carpeta (primer nivel y subcarpetas razonables, sin bajar
más de 2-3 niveles). Reportá:

- Cuántos se encontraron en total.
- Cuáles parecen ser una matriz de cotización real (están dentro de una
  carpeta `Matriz-Oferta/`, o el nombre contiene "matriz"/"oferta").
- Si no se encontró ninguno, decilo explícitamente — no lo des por hecho.

## 4. Excels de control de cotizaciones (agregado 2026-09-01, ruta confirmada 2026-09-07)

Cada cotización nueva se registra en **dos** Excels compartidos (ver
`docs/notas-proceso.md`, "Flujo actual" y "La matriz de Excel") —
`armar-cotizacion` los usa para escribir una fila nueva por cotización.
**No viven dentro de la carpeta `CLIENTES`** — viven dentro de una
carpeta compartida distinta, `COMERCIAL 2024` (de la misma cuenta "Info
Costa Rica"):

- `Cotizaciones en Preventa.xlsx` — directo en la raíz de `COMERCIAL
  2024`. Una pestaña por asesor (`Katherine`, `Alessandro `, ambas con
  un espacio/variación en el nombre real — no asumas el nombre exacto,
  leelo del archivo) más una pestaña `IA` (agregada 2026-09-07, ver
  abajo).
- `Control de cotizaciones 2026.xlsx` — más adentro, en `COMERCIAL
  2024/PREVENTA 2026/Cotizaciones pendientes 2026/`. La pestaña real
  para cotizaciones nuevas es **`Cotizaciones Pendientes 2026`**
  (tiene otras pestañas viejas de años anteriores y de otros usos —
  `Hoja4`, `Cot. Pendientes 2024`, `Muni Desamp`, etc. — no tocarlas).
  También tiene una pestaña `IA` al final (ver abajo).

**Por qué está en `COMERCIAL 2024` y no en la raíz de OneDrive:**
originalmente se agregaron como acceso directo a los dos *archivos*
sueltos — eso en OneDrive crea solo un `.url` (un puntero web de 1 KB,
sin contenido real, inservible para leer/escribir). La solución real
fue conseguir que alguien con acceso (María Fernanda Loria, dueña
original) compartiera la **carpeta** `COMERCIAL 2024` completa, y
agregar el acceso directo a esa carpeta — ahí sí sincroniza contenido
real. **Moraleja para cualquier acceso directo nuevo de este tipo:
agregar siempre la carpeta contenedora, nunca el archivo suelto.**

**Cómo verificar:** tomá el `UserFolder` de la cuenta `Business1`
(mismo registro que el paso 2). Ahí, buscá (Bash `ls`/Glob, sin
asumir el nombre exacto del acceso directo — OneDrive le antepone algo
como `Archivos de Info Costa Rica - COMERCIAL 2024`, puede variar) una
carpeta cuyo nombre contenga **"COMERCIAL 2024"**. Adentro, confirmá
que existan los dos archivos de arriba (con su ruta relativa: uno en la
raíz, el otro dentro de `PREVENTA 2026/Cotizaciones pendientes 2026/`).

Esta misma carpeta `COMERCIAL 2024` también trae `PREVENTA 2026/Base
datos de proveedores/BD Proveedores - Clientes.xltm` (pendiente desde
hace tiempo para `actualizar-catalogo`) y varias carpetas de precios/
fichas técnicas de proveedores — útil a futuro, pero fuera del alcance
de este skill; no lo explores más allá de confirmar que existe, y
nunca toques archivos de otros asesores que están ahí (ej. carpeta
`Equipo Comercial/<nombre>/`).

**Si falta el acceso a `COMERCIAL 2024`**, explicale al usuario:

1. Entrar a <https://grupovisionorg-my.sharepoint.com/> con su cuenta de
   Grupo Visión.
2. En el menú izquierdo, **"Compartido"** — buscar `COMERCIAL 2024`. Si
   no aparece, alguien con acceso (hoy: María Fernanda Loria) tiene que
   compartirle la carpeta primero (compartir el archivo suelto no
   alcanza, ver arriba).
3. Click derecho sobre la **carpeta** `COMERCIAL 2024` (nunca sobre un
   archivo individual) → **"Agregar acceso directo"** → **"Mis
   archivos"**.
4. Esperar unos minutos — esta carpeta trae bastante contenido, puede
   tardar más que un archivo suelto.

Esto es igual de necesario que el acceso a `CLIENTES` del paso 2 — sin
esto, `armar-cotizacion` no puede registrar la cotización nueva en el
control de ofertas, aunque sí pueda crear la carpeta y llenar la
matriz.

**Sobre editar estos archivos por navegador (probado 2026-09-01):**
`Control de cotizaciones 2026.xlsx` es pesado (cientos de filas,
autoguardado, uso compartido en tiempo real) y la automatización de
navegador resultó inestable de verdad — pantallas en blanco, capturas
colgadas, atajos que no registran. **Con acceso local confirmado (como
ahora), esto ya no hace falta** — escribí siempre por archivo local
(`openpyxl`), nunca por navegador con datos reales. El navegador queda
solo como último recurso si el acceso local se cae — ver "Registrar la
cotización" en `armar-cotizacion/SKILL.md`.

**Prueba de acceso de escritura (hecha 2026-09-07):** se agregó una
pestaña `IA` al final de ambos archivos (en `Cotizaciones en
Preventa.xlsx` no existía, se creó; en `Control de cotizaciones
2026.xlsx` ya existía de una prueba anterior por navegador). Sirve como
zona de prueba segura — nunca escribir datos de cotizaciones reales
ahí, es solo para verificar que el acceso de escritura sigue
funcionando.

## Checklist final

Presentá el resultado como una lista clara, por ejemplo:

```
✅ Bitrix24 configurado en .mcp.json (entrada: "bitrix24")
❌ Carpeta compartida no accesible: la ruta "C:\...\Cotizaciones" no existe
❌ Excels de referencia: no se pudo revisar (depende del punto anterior)
❌ Excels de control de cotizaciones: no se encontró la carpeta
   "COMERCIAL 2024" en tu OneDrive — hay que pedir que te la compartan
   y agregarla como acceso directo (ver paso 4 de este skill)

Qué falta:
- Confirmar la ruta correcta de la carpeta compartida.
- Conseguir acceso a la carpeta "COMERCIAL 2024" y agregarla como
  acceso directo de OneDrive.
```

Si TODO está en ✅, decilo con una sola línea y no agregues relleno.
