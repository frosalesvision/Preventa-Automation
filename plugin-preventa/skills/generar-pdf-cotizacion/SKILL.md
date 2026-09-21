---
name: generar-pdf-cotizacion
description: Genera el PDF final de una cotización a partir de la matriz ya completa, después de confirmar con el asesor de preventa que todo está correcto (equipo, cantidades, precios, condiciones). Usar cuando el asesor dice que la cotización está lista/terminada y hay que generar el PDF para enviarlo al cliente.
---

# Generar PDF de cotización — PENDIENTE

Este skill todavía no tiene lógica real. Idea propuesta por el usuario
(2026-09-09): cuando una cotización queda terminada (matriz completa y
revisada), **antes de generar el PDF final preguntarle siempre al
asesor si todo está correcto** — nunca generar el PDF en silencio ni
asumir que está listo solo porque la matriz tiene datos cargados. Esto
es la misma disciplina de "mostrar antes de escribir/generar y esperar
confirmación" que ya usan
[`armar-cotizacion`](../armar-cotizacion/SKILL.md) y
[`buscar-equipo`](../buscar-equipo/SKILL.md).

Relacionado con [`seguimiento-correo`](../seguimiento-correo/SKILL.md):
ese skill asume que este PDF ya existe para adjuntarlo al correo de
seguimiento — sin este skill, el asesor sigue generando el PDF a mano
como hoy.

## Falta información real para completarlo

- ¿Cómo se genera hoy el PDF a mano? (¿Un rango de impresión específico
  de la matriz, un botón/macro de "Guardar como PDF", una pestaña
  aparte pensada para imprimir, portada o membrete distinto?)
- ¿El PDF sale directo de la pestaña `COTIZACIÓN ` del machote (existe
  en `Machote Matriz y oferta.xlsx`, ver
  [`armar-cotizacion`](../armar-cotizacion/SKILL.md)), o de otra
  pestaña/archivo?
- ¿Nombre de archivo y ubicación? ¿Mismo criterio que el número de
  oferta `T{prefijo}-{7 dígitos}-{año}` que ya usa `armar-cotizacion`
  dentro de `Matriz-Oferta/`?
- ¿Hay versionado del PDF igual que de la matriz (Caso 2 de
  `armar-cotizacion`, ej. `V2`, `V3`), o el PDF siempre se
  regenera/reemplaza?

No armar la lógica de este skill hasta tener estas respuestas — es fácil
generar un PDF con el formato equivocado o desde la pestaña equivocada
si se asume en vez de preguntar.
