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

**No hay correos reales de la empresa que copiar** (confirmado por
Fabián el 2026-10-12): los modelos de abajo los escribimos nosotros, y
el criterio es que **se lean muy profesionales**. Eso significa:

- **De "usted", siempre.** Cordial, sin confianzas ni diminutivos, sin
  emojis, sin signos de exclamación de más.
- **Corto y con un propósito por correo.** Saludo, para qué se escribe,
  qué se necesita del cliente (si algo), cierre. Tres o cuatro párrafos
  breves como máximo.
- **Concreto, no genérico.** Adaptá cada borrador a lo que se sabe en la
  conversación: nombre del contacto, qué se cotizó, en qué quedó la
  última conversación, plazos que el cliente mencionó. Una frase concreta
  vale más que tres de cortesía.
- **Nunca número de oferta ni monto en el cuerpo del correo.** Van
  únicamente en el PDF adjunto.
- **Nunca presionar.** Ni "le recordamos que la oferta vence", ni
  "quedamos a la espera de su orden de compra". Si hay una fecha real
  (vigencia, cierre de una licitación), se menciona como dato útil para
  el cliente, no como urgencia.
- **El asunto dice de qué se trata** en pocas palabras, con el nombre
  del proyecto.
- **El correo asume que ya existe el PDF final** para adjuntar (lo arma
  [`generar-pdf-cotizacion`](../generar-pdf-cotizacion/SKILL.md)). Si
  todavía no existe, decilo en vez de redactar como si estuviera listo.

Los corchetes son lo que el asesor completa o el plugin rellena con lo
que ya se sabe. Si un dato no se sabe, se deja el corchete: **nunca se
inventa** un nombre, una fecha o un compromiso.

## Modelos, uno por situación

### Cotización lista, se envía por primera vez ("Enviada")

```
Asunto: Cotización — [nombre del proyecto]

Estimado(a) [nombre del contacto]:

Reciba un cordial saludo de parte de Grupo Visión.

Adjunto encontrará la cotización correspondiente a [breve descripción
del proyecto o solicitud], preparada de acuerdo con los requerimientos
que nos compartió.

Quedamos a su disposición para cualquier consulta, ajuste o aclaración
sobre la propuesta. Con gusto podemos coordinar una reunión para
revisarla juntos si le resulta útil.

Agradecemos la oportunidad de participar en este proceso.

Saludos cordiales,

[Nombre del asesor]
Grupo Visión CR
[Teléfono / correo del asesor]
```

### Seguimiento cuando no hay respuesta ("En espera")

Usarlo una vez, con al menos una semana desde el envío (o lo que el
asesor indique). Si el cliente ya respondió algo, no es este modelo.

```
Asunto: Seguimiento a la cotización — [nombre del proyecto]

Estimado(a) [nombre del contacto]:

Reciba un cordial saludo.

Le escribo para dar seguimiento a la cotización de [breve descripción]
que le enviamos el [fecha de envío]. Quisiera saber si tuvo oportunidad
de revisarla y si le surgió alguna consulta o necesita algún ajuste en
el alcance.

Si le resulta más sencillo, con gusto coordinamos una llamada breve para
revisar los detalles.

Saludos cordiales,

[Nombre del asesor]
Grupo Visión CR
[Teléfono / correo del asesor]
```

### Se envía una versión revisada (el cliente pidió cambios)

```
Asunto: Cotización actualizada — [nombre del proyecto]

Estimado(a) [nombre del contacto]:

Reciba un cordial saludo.

Conforme a lo conversado, adjunto la versión actualizada de la
cotización de [breve descripción]. Incorpora los cambios solicitados:
[resumen breve de los cambios, sin montos — por ejemplo: "se ajustó la
cantidad de cámaras exteriores y se incluyó el almacenamiento para 30
días"].

Quedamos atentos a sus comentarios.

Saludos cordiales,

[Nombre del asesor]
Grupo Visión CR
[Teléfono / correo del asesor]
```

### Confirmación de entrega formal ("Entregada")

Para cuando la oferta se entregó por un canal formal (una licitación,
una plataforma de compras, una entrega física) y conviene dejar
constancia por correo.

```
Asunto: Entrega de oferta — [nombre del proyecto o número de concurso]

Estimado(a) [nombre del contacto]:

Reciba un cordial saludo de parte de Grupo Visión.

Le confirmamos que el [fecha] entregamos nuestra oferta para [nombre del
proyecto o concurso] por medio de [canal: la plataforma, en sus
oficinas, etc.].

Quedamos a su disposición para cualquier aclaración que requiera
durante el proceso de evaluación.

Saludos cordiales,

[Nombre del asesor]
Grupo Visión CR
[Teléfono / correo del asesor]
```

### Hace falta información del cliente para terminar ("Pendiente")

```
Asunto: Información para completar la cotización — [nombre del proyecto]

Estimado(a) [nombre del contacto]:

Reciba un cordial saludo.

Estamos preparando la cotización de [breve descripción] y, para que
refleje con precisión lo que necesita, le agradeceríamos confirmarnos:

- [dato que falta — por ejemplo: cantidad de puntos de cámara por zona]
- [dato que falta — por ejemplo: días de grabación que requieren]

Con esa información le enviamos la propuesta a la mayor brevedad.

Saludos cordiales,

[Nombre del asesor]
Grupo Visión CR
[Teléfono / correo del asesor]
```

### El cliente avisó que no sigue ("Descartada")

Cierre cordial: agradecer, no insistir, dejar la puerta abierta. La
pregunta por retroalimentación es opcional; el asesor decide si va.

```
Asunto: Re: [asunto del correo del cliente]

Estimado(a) [nombre del contacto]:

Muchas gracias por informarnos su decisión y por habernos tomado en
cuenta para [nombre del proyecto].

[Opcional:] Si en algún momento puede compartirnos qué aspectos pesaron
en la decisión, nos ayudaría a mejorar nuestras propuestas.

Quedamos a su disposición para futuros proyectos.

Saludos cordiales,

[Nombre del asesor]
Grupo Visión CR
[Teléfono / correo del asesor]
```
