# Sandbox de pruebas — 100% datos falsos

Esta carpeta **no tiene ningún dato real de clientes**. Es una réplica
mínima de la estructura de `CLIENTES/` para poder probar `armar-
cotizacion` sin tocar la carpeta compartida real de la empresa.

## Casos que cubre

- `Cliente Numeracion Continua/` — numeración de "Cotización #N" que
  sigue subiendo entre años (`Cotizaciones 2025` llega a #2,
  `Cotizaciones 2026` sigue en #3). El skill debería proponer **#4**
  sin necesidad de preguntar, porque el máximo del año actual y el
  máximo global coinciden.
- `Cliente Numeracion Reinicia/` — numeración que se reinicia cada año
  (`-2025` llega a #3, `-2026` vuelve a empezar en #1). El máximo del
  año actual (1) y el máximo global (3) **no coinciden** — el skill
  debería mostrar ambos candidatos (2 vs. 4) y preguntar cuál aplica,
  no elegir uno solo.
- `Cliente Plano Sin Anio/` — sin carpeta de año, cotizaciones directo
  bajo el cliente (#1, #2). El skill debería seguir ese mismo patrón
  plano al crear la #3, no inventar una carpeta de año.
- `Cliente Nuevo Sin Cotizaciones/` — cliente sin ninguna cotización
  todavía. El skill debería usar la convención `Cotizaciones AAAA` y
  proponer la #1.
- `Sandbox-Fabian/` — cliente de prueba end-to-end (probado el
  2026-08-26), con `Cotización #1-2026 primer proyecto/` ya existente
  y `Cotización #2-2026 camaras/` creada durante la prueba (con el
  machote copiado adentro de `Matriz-Oferta/`). Junto con la fila falsa
  en `plugin-preventa/recursos-originales/Control de cotizaciones 2026
  - CON FILA SANDBOX FABIAN.csv` (copia del Excel maestro real +1 fila
  inventada, protegida por `.gitignore`), permite probar el flujo
  completo de 1 a 6, incluyendo el número de oferta real.

⚠️ **Usá nombres cortos para pruebas.** Se encontró en la práctica que
Excel no abre archivos cuya ruta completa pasa de ~259 caracteres
(límite de Windows). Como este repo ya vive en una ruta profunda del
Desktop, nombres de prueba muy descriptivos (como agregar "PRUEBA" en
cada nivel) pueden hacer que la ruta se pase del límite. `Sandbox-
Fabian` (sin espacios ni repetir "PRUEBA" en cada carpeta) es el nombre
corto a reutilizar de acá en adelante.

## Cómo probar `armar-cotizacion`

1. Instalá el plugin desde esta misma carpeta del repo (marketplace
   local) y probá el skill pidiéndole que arme una cotización nueva
   para alguno de estos clientes de prueba, apuntando a
   `sandbox-pruebas/CLIENTES/` en vez de la ruta real de SharePoint.
2. Fijate que **siempre pida confirmación antes de crear** cualquier
   carpeta — si no lo hace, es un bug de seguridad, no solo de lógica.
3. Después de cada prueba, para dejar todo como estaba:
   ```bash
   git checkout -- sandbox-pruebas/
   git clean -fd sandbox-pruebas/
   ```
   Esto borra cualquier carpeta nueva que el skill haya creado durante
   la prueba y vuelve a los 4 casos originales.

## Cómo probar `actualizar-catalogo`

Réplica en `sandbox-pruebas/CLIENTES/00_IA_PREVENTAS/Preventas/Catalogo/`
de la carpeta real (`CLIENTES/00_IA_PREVENTAS/Preventas/Catalogo/` en
SharePoint), con:
- `Catalogo de productos por proveedor.xlsx` — igual al real pero
  **solo con encabezados, sin ninguna fila de datos**.
- `Catalogos Proveedor/ProveedorPrueba/Lista de precios (ejemplo,
  datos falsos).txt` — un documento de ejemplo con 3 productos
  inventados, para probar el flujo de "hay un documento en la
  carpeta."

Dos formas de probar (el skill soporta ambas):

1. **Con documento**: pedile que actualice el catálogo a partir de
   `sandbox-pruebas/CLIENTES/00_IA_PREVENTAS/Preventas/Catalogo/Catalogos
   Proveedor/ProveedorPrueba/Lista de precios (ejemplo, datos
   falsos).txt`, dejando claro que es sobre el catálogo de **sandbox**,
   no el real.
2. **Sin documento**: pegale directo en el chat un producto o lista
   inventada (ej. "agregá esta cámara de prueba: marca X, modelo
   TEST-123, USD 50, unidad") y decile que lo cargue en el catálogo de
   sandbox.

Fijate que:
- Muestre un resumen claro (tipo tabla) de lo que va a agregar/cambiar
  **antes** de tocar el Excel, y espere confirmación — igual que
  `armar-cotizacion`.
- Complete "Archivo de origen" (nombre del archivo, o "Dato dado por
  \<vos\> en chat, DD/MM/AAAA" si fue pegado) y "Fecha de última
  actualización" en cada fila.
- Si volvés a pasarle el mismo producto (mismo Modelo/SKU + Proveedor),
  lo detecte como **actualización**, no como fila duplicada.
- Al final, después de probar, dejá el Excel de sandbox otra vez solo
  con encabezados (podés simplemente volver a copiarlo desde la carpeta
  real, o usar `git checkout -- sandbox-pruebas/` si no lo modificaste
  fuera del repo).
