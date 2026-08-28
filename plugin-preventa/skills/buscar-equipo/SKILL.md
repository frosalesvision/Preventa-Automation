---
name: buscar-equipo
description: Busca marca y modelo específico de un equipo (cámara, control de acceso, alarma, etc.) que cumpla al 100% con una especificación técnica dada, usando el catálogo/precios de proveedores de Grupo Visión CR. Usar cuando el usuario pide encontrar un equipo que cumpla ciertas especificaciones, o pide ayuda para elegir marca/modelo para una licitación o cotización.
---

# Buscar equipo — PENDIENTE, no implementado en fase 1

Este skill **todavía no existe** — es un placeholder para dejar registrado
el pedido, no un skill funcional. No inventar lógica todavía.

## Por qué existe este placeholder

Confirmado por preventa y por ventas (2026-08-26) que este es **el
cuello de botella más grande del proceso completo**, más amplio de lo
que se pensó al inicio: no es solo "buscar el accesorio de montaje según
marca de cámara" (ver esa nota específica en
[`docs/notas-proceso.md`](../../../docs/notas-proceso.md)) — es, para
**cualquier equipo** (no solo cámaras), a partir de una especificación
técnica dada por el cliente/licitación, encontrar una marca y modelo
real que la cumpla al 100%. Hoy lo hacen "a pie" con ayuda de IA
genérica, sin certeza. Ventas lo pidió explícitamente: *"nos serviría
demasiado tener una IA que busque con más certeza para tener un norte
de cuáles equipos podrían ser."*

## Depende de `actualizar-catalogo` (decidido 2026-08-26)

Este skill **lee**, no mantiene, el catálogo de proveedores. La
carpeta/skill que lo escribe y lo mantiene al día es
[`actualizar-catalogo`](../actualizar-catalogo/SKILL.md) — el catálogo
vive en `CLIENTES/00_IA_PREVENTAS/Preventas/Catalogo/` (carpeta dentro
de `CLIENTES`). No tiene sentido construir
`buscar-equipo` antes de que exista ese catálogo estructurado; hoy la
info de proveedores solo existe como PDFs sueltos en carpetas
personales, no hay nada consultable todavía.

## Lo que hace falta antes de poder implementarlo

- Que `actualizar-catalogo` exista y el catálogo tenga datos reales
  cargados (ver ese skill para el diseño propuesto de columnas).
- Acceso confirmado y revisado a los catálogos/precios reales de
  proveedores de Grupo Visión (`BD Proveedores - Clientes.xltm` en
  `COMERCIAL 2024/PREVENTA 2026`, y la carpeta `PRECIOS EQUIPOS Y
  ACCESORIOS` — en revisión, ver notas-proceso.md).
- Definir qué formato tienen las especificaciones técnicas de entrada
  (vienen en PDFs de pliegos de condiciones, con requisitos tipo "mínimo
  X Mp, protección IP67, certificación NDAA", etc. — ver ejemplo real en
  notas-proceso.md).
- Decidir qué pasa cuando ningún equipo del catálogo cumple al 100%
  (¿proponer el más cercano? ¿avisar que no hay match?).
- Confirmar con el usuario si esto se construye como skill separado
  (como está planteado acá) o como parte de `armar-cotizacion` — por
  ahora se deja separado porque `armar-cotizacion` está limitado a
  organización de archivos, no a contenido técnico.

No avanzar en este skill sin antes confirmar alcance con el usuario,
igual que se hizo con `armar-cotizacion`.
