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
