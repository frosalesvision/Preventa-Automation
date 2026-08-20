---
name: verificar-entorno
description: Revisa qué accesos y conexiones están listos para trabajar con el plugin de preventa (carpeta compartida de cotizaciones, Excels de referencia, configuración de Bitrix24) y entrega un checklist de qué falta. Usar como primer paso al iniciar una sesión de preventa, cuando el usuario pregunta "qué me falta configurar", "está todo listo", "revisá el entorno", o cuando otro skill del plugin (armar-cotizacion, sync-bitrix) falla por falta de acceso a algo.
---

# Verificar entorno de preventa

Ejecutá estas 4 verificaciones en orden y compilá un checklist final. No
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

## 2. Carpeta compartida de cotizaciones

- Si el usuario ya mencionó la ruta en la conversación, usala. Si no,
  **preguntale** la ruta local de la carpeta compartida en la nube
  (OneDrive/SharePoint/Drive sincronizado en su computadora).
- Intentá listar esa ruta (Glob o Bash `ls`). Si falla (no existe, sin
  permisos, ruta mal escrita), reportalo como **no accesible** con el
  motivo exacto del error — no reintentes rutas inventadas ni asumas una
  ubicación por defecto.

## 3. Excels de referencia en la carpeta compartida

Una vez confirmado el acceso del paso 2, buscá archivos `.xlsx`/`.xlsm`
dentro de esa carpeta (primer nivel y subcarpetas razonables, sin bajar
más de 2-3 niveles). Reportá:

- Cuántos se encontraron en total.
- Cuáles parecen ser el Excel maestro (nombre contiene "maestro",
  "master", "seguimiento") o una matriz de cotización (nombre contiene
  "cotiz", "matriz", "oferta", o un patrón tipo `T0010`).
- Si no se encontró ninguno, decilo explícitamente — no lo des por hecho.

## 4. Recursos originales locales (para desarrollo de `armar-cotizacion`)

Revisá si existe la carpeta `recursos-originales/` en el proyecto actual
(raíz del repo donde se está trabajando, no la del plugin) y listá qué
archivos tiene. Esta carpeta es local y nunca se sube a git — si está
vacía o no existe, es normal en una instalación nueva del plugin.

## Checklist final

Presentá el resultado como una lista clara, por ejemplo:

```
✅ Bitrix24 configurado en .mcp.json (entrada: "bitrix24")
❌ Carpeta compartida no accesible: la ruta "C:\...\Cotizaciones" no existe
❌ Excels de referencia: no se pudo revisar (depende del punto anterior)
⚠️  recursos-originales/: vacía (normal si es la primera vez)

Qué falta:
- Confirmar la ruta correcta de la carpeta compartida.
```

Si TODO está en ✅, decilo con una sola línea y no agregues relleno.
