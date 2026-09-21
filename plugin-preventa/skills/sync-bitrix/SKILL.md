---
name: sync-bitrix
description: Actualiza la tarjeta correspondiente en el tablero Kanban de Bitrix24 al cerrar una cotización de preventa. Requiere que el servidor MCP de Bitrix24 esté configurado en .mcp.json (todavía pendiente de webhook/API key a nivel gerencial). Usar cuando el usuario pide subir, sincronizar o actualizar una cotización cerrada en Bitrix24.
---

# Sync con Bitrix24 — PENDIENTE

Este skill es un placeholder hasta que exista el webhook/API key de
Bitrix24 (se va a pedir a nivel gerencial, ver
[`docs/notas-proceso.md`](../../../docs/notas-proceso.md)).

**Mientras `.mcp.json` no tenga configurado el servidor de Bitrix24:**
corré primero el skill `verificar-entorno`. Si confirma que Bitrix24 no
está configurado, explicá eso al usuario y no intentes ninguna llamada —
no inventes ni simules una actualización.

## Cómo conseguir el webhook (para pedirle a Operaciones/quien administre Bitrix24, agregado 2026-09-09)

Se necesita un **webhook entrante** ("Inbound webhook"), no una cuenta de
desarrollador aparte. Lo tiene que crear alguien con permisos de
administrador en el portal de Bitrix24 de la empresa:

1. En Bitrix24, ir a **Configuración** (ícono de engranaje) →
   **Recursos para desarrolladores** ("Developer resources") → **Otros**
   → **Webhook entrante** ("Inbound webhook"). En algunos portales
   también aparece dentro de "Aplicaciones" → "Desarrollador".
2. Crear un webhook nuevo, ponerle un nombre identificable (ej.
   "Preventa Automation"), y **seleccionar los permisos (scopes)**
   necesarios — como mínimo el módulo **CRM** (`crm`). El scope exacto
   depende de si el tablero Kanban de preventa está armado sobre
   **Negocios (Deals)**, **Leads**, o un objeto tipo SPA (Smart Process)
   — eso hay que confirmarlo con quien lo creó/administra.
3. El resultado es una **URL** con esta forma:
   `https://<portal>.bitrix24.com/rest/<user_id>/<código>/` — esa URL
   completa **es la credencial** (quien la tenga puede llamar la API con
   los permisos de esa persona). Tratarla como una contraseña: nunca
   pegarla en un archivo que se vaya a commitear, solo en `.mcp.json`
   local o variable de entorno (ver `.gitignore` en la raíz del repo).
4. Junto con la URL, pedir también (o confirmarlo aparte, ver la lista
   de abajo): **a qué tablero/pipeline corresponde preventa** (nombre o
   ID de la categoría/pipeline) y en qué etapa exacta debe caer una
   cotización cerrada.

**Sobre hacerlo por navegador mientras tanto:** técnicamente sí se
podría, usando el propio login normal de Bitrix24 de quien lo use (no
necesita el webhook ni permisos de administrador, solo su acceso normal
al tablero) para mover/editar tarjetas manualmente asistido por
navegador, en vez de por API. **No está diseñado ni probado todavía** —
antes de intentarlo, tener en cuenta que la automatización de navegador
sobre interfaces tipo SPA complejas (como Excel Online en esta misma
sesión) resultó inestable de verdad. Si se quiere este camino como
solución mientras se consigue el webhook, es un diseño aparte que hay
que armar con cuidado (qué tablero, qué campos, siempre confirmar antes
de mover una tarjeta) — no asumir que funciona igual de bien solo porque
la idea es parecida.

Falta información real para completarlo una vez haya credenciales:

- URL del webhook / API key y método de autenticación exacto.
- ID(s) del tablero Kanban y de las columnas/etapas relevantes para
  preventa (dónde entra una cotización cerrada, qué etapa le sigue en
  Compras).
- Mapeo de campos: qué campo de la tarjeta de Bitrix corresponde a
  cliente, número de oferta (T00XX), monto sin IVA, proveedor, asesor
  comercial, etc. (ver columnas del Excel maestro en
  [`docs/notas-proceso.md`](../../../docs/notas-proceso.md)).
- Si la tarjeta se crea desde cero acá, o si siempre ya existe (creada
  antes en el proceso) y este skill solo la actualiza.
- Qué debe pasar si ya existe una tarjeta para ese número de oferta
  (evitar duplicados en versionado v1/v2/v3).
