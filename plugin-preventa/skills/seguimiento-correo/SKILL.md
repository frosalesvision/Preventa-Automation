---
name: seguimiento-correo
description: Redacta un borrador de correo de seguimiento a un cliente sobre una cotización (etapas reales del proceso — Pendiente, Enviada, Entregada, En espera, Descartada), en tono formal, sin mencionar número de oferta ni monto (esos datos van solo en el PDF adjunto). NUNCA envía el correo, solo redacta el texto para que el asesor lo revise, adjunte el PDF y lo envíe a mano. Usar cuando el usuario pide redactar, escribir o dar seguimiento por correo a un cliente sobre una cotización.
---

# Seguimiento por correo

## Regla dura (no cambia aunque se agregue un conector de correo real más adelante)

Este skill **redacta, nunca envía**. El resultado siempre es texto para
que el asesor revise, ajuste si hace falta, adjunte el PDF de la
cotización a mano, y lo envíe él mismo. Aunque en el futuro se agregue
un conector real de correo (lectura/envío), esta regla no cambia — enviar
queda fuera de alcance de este skill a menos que el usuario decida
explícitamente lo contrario más adelante.

## Estados reales (confirmados 2026-09-09)

Las etapas reales de una cotización, según el asesor: **Pendiente,
Enviada, Entregada, En espera, Descartada** — corresponden a la columna
"Estado" de `Control de cotizaciones 2026.xlsx` (ver `verificar-entorno`
paso 4).

**No asumas que cada cambio de estado implica mandar un correo.** Según
el propio asesor, el campo "Estado" es sobre todo informativo para el
seguimiento interno de la empresa, no necesariamente un disparador
automático de correo. **Preguntale siempre** para qué situación
específica necesita el borrador (ej. "quiero avisarle al cliente que ya
se la enviamos", "no me ha contestado en dos semanas", "nos avisaron que
no van a seguir") — no generes un correo solo porque una fila cambió de
estado en el Excel.

## Tono y formato

- **Formalidad siempre por delante.** No hay una plantilla de casa fija
  todavía, pero el registro es formal (de "usted"), profesional, cordial.
- **Genérico en estructura, pero que no se sienta genérico.** Evitá
  frases de relleno tipo plantilla robótica — adaptá el texto a lo que
  se sabe del proyecto/cliente en esta conversación (nombre del
  contacto, qué se cotizó, en qué quedó la conversación previa) en vez
  de repetir el mismo texto para cualquier caso.
- **Nunca incluir número de oferta ni monto en el cuerpo del correo** —
  esos datos van únicamente en el PDF adjunto, no se repiten en el
  texto.
- El correo **asume que ya existe el PDF final de la cotización** para
  adjuntar (ver [`generar-pdf-cotizacion`](../generar-pdf-cotizacion/SKILL.md)
  abajo) — si todavía no existe, decilo explícitamente en vez de
  redactar como si ya estuviera listo para enviar.

## Ejemplo — cotización terminada, se envía por primera vez ("Enviada")

Modelo base para cuando la cotización queda lista y se manda al cliente
por primera vez. Los corchetes son lo que el asesor completa antes de
enviar — **todavía faltan ejemplos reales de los otros estados** (en
espera/sin respuesta, cambios solicitados, descartada); el usuario va a
compartir más ejemplos reales para ajustar el tono exacto — no inventar
esos otros borradores todavía sin esos ejemplos.

```
Asunto: Cotización — [nombre del proyecto o cliente]

Estimado(a) [nombre del contacto],

Reciba un cordial saludo de parte de Grupo Visión.

Adjunto a este correo encontrará la cotización correspondiente a
[breve descripción del proyecto/solicitud], preparada de acuerdo con
los requerimientos que nos compartió.

Quedamos atentos a cualquier consulta, ajuste o aclaración que necesite
sobre la propuesta. Será un gusto conversar para resolver cualquier duda
y acompañarle en lo que necesite para avanzar con el proyecto.

Agradecemos la oportunidad de participar en este proceso y quedamos a la
espera de sus comentarios.

Saludos cordiales,

[Nombre del asesor]
Grupo Visión CR
[Teléfono / correo del asesor]
```

## Relacionado: `generar-pdf-cotizacion` (todavía no existe)

Este skill depende de que ya exista el PDF final de la cotización para
adjuntar. Hoy ese PDF lo genera el asesor a mano desde Excel. Se propuso
(2026-09-09) un skill nuevo para esto — ver
[`generar-pdf-cotizacion`](../generar-pdf-cotizacion/SKILL.md)
(placeholder, todavía sin lógica real).
