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
