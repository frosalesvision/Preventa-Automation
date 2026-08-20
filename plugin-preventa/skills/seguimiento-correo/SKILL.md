---
name: seguimiento-correo
description: Redacta un borrador de correo de seguimiento a un cliente según la etapa de su cotización (enviada, sin respuesta, cambios solicitados, cerrada). NUNCA envía el correo, solo redacta el texto para que el usuario lo revise y lo envíe a mano. Usar cuando el usuario pide redactar, escribir o dar seguimiento por correo a un cliente sobre una cotización.
---

# Seguimiento por correo — PENDIENTE

Este skill todavía no tiene lógica real. Es un placeholder: hoy no hay
conector de correo (ni de envío ni de lectura de bandeja), así que el
resultado siempre es texto para copiar/pegar a mano, nunca un envío
automático.

**Regla dura que no cambia aunque se agregue un conector de correo más
adelante:** este skill redacta, nunca envía. El envío siempre lo hace la
persona, a mano.

Falta información real para completarlo:

- ¿Cuáles son las etapas reales de una cotización desde el punto de vista
  del cliente (ej. enviada / sin respuesta en X días / cambios
  solicitados / aprobada / cerrada)? ¿Coinciden con el campo "estado" del
  Excel maestro (ver [`docs/notas-proceso.md`](../../../docs/notas-proceso.md))?
- ¿Hay una plantilla o tono de casa ya usado (formal, "usted", con
  membrete, firma estándar del asesor)? ¿Algún ejemplo real de correo
  enviado antes?
- ¿El correo debe incluir el número de oferta (T00XX) y el monto, o eso
  se maneja aparte en el PDF adjunto?
- ¿Se necesita un borrador distinto por proveedor/marca, o el texto es
  genérico y solo cambia el estado?

Cuando haya un conector de correo real (lectura/envío), este skill sigue
sin enviar por sí mismo — la parte de envío queda fuera de su alcance a
menos que el usuario decida explícitamente lo contrario más adelante.
