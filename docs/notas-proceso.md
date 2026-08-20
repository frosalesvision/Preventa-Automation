# Notas del proceso de negocio — Preventa (Grupo Visión)

> Documento de contexto interno, NO es un skill. Sirve para que cualquiera
> que mantenga este plugin entienda el proceso real sin tener que
> preguntarle a preventa de nuevo. Si el proceso cambia, actualizar acá
> primero y después revisar si algún SKILL.md quedó desalineado.

## Quién hace qué

El equipo de preventa arma cotizaciones de sistemas de seguridad/cámaras
para clientes. Hoy el proceso es 100% manual, en Excel, con trabajo
duplicado entre un Excel maestro compartido y el Excel personal de cada
asesor.

## Flujo actual (manual)

1. **Registro en Excel maestro compartido.** Columnas: letra de quién
   trabaja, cliente, descripción, fecha del proyecto, fecha de entrega,
   número de oferta, monto sin IVA, proveedor, estado, asesor comercial,
   notas.
2. **Duplicado en Excel personal.** Cada asesor replica la misma info en
   su propio archivo. Es trabajo repetido, no aporta nada nuevo — candidato
   claro a eliminar cuando haya una fuente única de verdad.
3. **Armado de la cotización** en una matriz de Excel con pestañas:
   cámaras, productos, materiales, OPEX/mano de obra, y una hoja final
   que se exporta a PDF como la cotización oficial para el cliente.
4. **Cierre y traspaso a Bitrix24.** Al cerrar la cotización se sube
   manualmente a un tablero Kanban en Bitrix24. De ahí Compras y luego
   Operaciones/Implementación continúan el flujo. **El proceso de
   preventa termina en este punto** — todo lo posterior (compras,
   implementación) está fuera del alcance de este plugin.

## Numeración de ofertas

- Es un **consecutivo por cliente**, no un número único global.
- Formato tipo `T0010`.
- Ese número lo usa el cliente en su orden de compra y **ancla el
  proyecto en Operaciones** — es un identificador crítico, no cosmético.
  No se puede reciclar ni generar mal.

## Versionado de cotizaciones

- **Cambio menor** (quitar/agregar un ítem): se genera una nueva versión
  del mismo Excel/PDF (v1, v2, v3...), **sin crear carpeta nueva**.
- **Cambio grande** (ej. cambiar de marca de cámara completa): se genera
  una **copia nueva** del Excel (no una versión del mismo archivo).
- La distinción entre "menor" y "grande" hoy la decide el criterio del
  asesor — no hay una regla dura escrita. Cualquier automatización debe
  preguntar o inferir con cautela, no asumir.

## El cuello de botella más grande

Para cada cámara hay que **buscar a mano el accesorio de montaje
correcto** según la marca del equipo y el tipo de instalación
(pared/techo). Si el cliente cambia de marca, hay que rehacer esa
búsqueda línea por línea en toda la cotización.

**Esto NO se automatiza en esta fase 1.** Queda registrado como trabajo
futuro explícito — no inventar una solución parcial para esto todavía.

## Precios de proveedores

Muchos precios no están en un catálogo centralizado: se consultan por
correo, WhatsApp o llamada. Esto significa que `armar-cotizacion` no
puede asumir que todos los precios están disponibles localmente; en
fase 1 probablemente dependa de que el usuario los tenga a mano o de un
catálogo parcial en `references/`.

## Integración con Bitrix24

- Tableros tipo Kanban.
- Preventa sube manualmente la cotización cerrada; de ahí sigue Compras
  y Operaciones/Implementación.
- **Fase 1 de este plugin NO tiene webhook/API key de Bitrix24 todavía.**
  Se va a pedir a nivel gerencial más adelante. Por eso `sync-bitrix` es
  un placeholder y `plugin-preventa/.mcp.json` tiene la config comentada,
  lista para activarse cuando llegue la credencial.

## Alcance de fase 1 (lo que SÍ se construye ahora)

- `verificar-entorno`: chequeo de accesos/conexiones disponibles.
- `armar-cotizacion`: generación de la cotización respetando formato,
  numeración y versionado de arriba (pendiente de ver Excels reales,
  ver más abajo).
- `seguimiento-correo`: redacción (no envío) de borradores de respuesta
  a clientes según etapa de la cotización.
- `sync-bitrix`: placeholder hasta tener credenciales de Bitrix24.

## Fuente de verdad para `armar-cotizacion`

Antes de implementar la lógica final de este skill, hace falta que el
usuario copie a `recursos-originales/` (ignorada por git, nunca se sube):

1. El Excel maestro compartido (o una copia con datos de ejemplo).
2. Al menos una matriz de cotización real ya hecha (con sus pestañas de
   cámaras, productos, materiales, OPEX/mano de obra y hoja final).

Esto es para construir el skill sobre la estructura real de columnas,
fórmulas y formato — no sobre suposiciones.
