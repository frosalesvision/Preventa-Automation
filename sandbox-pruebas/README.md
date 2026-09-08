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
- `Catalogo de productos por proveedor.xlsx` — **actualizado 2026-09-01:
  ya no es solo encabezados** — es un espejo completo del catálogo real
  (2,358 productos + la pestaña "Compatibilidad de Accesorios"), a
  propósito, para poder probar `buscar-equipo` y el llenado de
  `Equipos` de `armar-cotizacion` con datos reales de producto. Para
  probar el flujo de "actualizar una fila que ya existe" de
  `actualizar-catalogo`, usá cualquier producto real ya presente en
  vez de necesitar un catálogo vacío.
- `Catalogos Proveedor/ProveedorPrueba/Lista de precios (ejemplo,
  datos falsos).txt` — un documento de ejemplo con 3 productos
  inventados, para probar el flujo de "hay un documento en la
  carpeta" (agregar filas nuevas).

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
- Al final, si agregaste filas de prueba (`TEST-123` y similares), o si
  el catálogo de sandbox quedó desactualizado frente al real, lo más
  simple es volver a copiar el `.xlsx` real de producción encima
  (`CLIENTES/00_IA_PREVENTAS/Preventas/Catalogo/Catalogo de productos
  por proveedor.xlsx`) — no uses `git checkout` para este archivo, está
  en `.gitignore` y no lo va a tocar.

## Cómo probar `buscar-equipo`

Usa el mismo catálogo de sandbox de arriba (ya tiene datos reales, no
hace falta prepararle nada). Ejemplos de prompt para probar:

- **Por especificación:** "necesito una cámara PTZ de al menos 8MP para
  exteriores, zoom óptico de 25x o más" — debería proponer candidatos
  reales del catálogo (ej. `PAR-P8PTZXIR32NH-AI`), explicando por qué
  cumplen.
- **Con accesorios:** después de elegir un modelo, pedile "¿qué
  accesorios de instalación tiene?" — debería preguntar primero si
  hacen falta, y si hay varios tipos de mount, mostrarlos todos y
  preguntar cuál aplica.
- **Sin match documentado:** probá con un modelo Milesight/Secure (poca
  cobertura a propósito, ver `buscar-equipo/SKILL.md`) — debería
  ofrecer la lista buscable de accesorios de esa marca en vez de
  simplemente decir "no hay".
- **Cambio de marca:** pedile que recalcule el mismo equipo pero en
  otra marca — debería repetir la búsqueda de equipo y de accesorios
  desde cero, sin reusar el accesorio de la marca anterior.

## Cómo probar el llenado de `Equipos` en `armar-cotizacion` (nuevo, 2026-09-01)

1. Primero encontrá equipo con `buscar-equipo` (ver arriba).
2. Pedile que arme una cotización nueva para uno de los clientes de
   prueba de este sandbox, y que cargue ese equipo en la matriz.
3. Verificá que **muestre la tabla completa antes de escribir**
   (Modelo | Descripción | Importado | Cantidad | Costo Unit) y espere
   confirmación.
4. Abrí el `.xlsx` resultante y confirmá que solo se llenaron las
   columnas B-E de la pestaña `Equipos`, y que las fórmulas de margen/
   transporte/impuestos siguen intactas y calculando (compará contra
   `references/Machote Matriz y oferta.xlsx` sin tocar).
5. Limpiá con `git checkout -- sandbox-pruebas/` + `git clean -fd
   sandbox-pruebas/` igual que con cualquier otra prueba de
   `armar-cotizacion`.
