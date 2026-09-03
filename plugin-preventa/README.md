# Plugin preventa

Plugin de Claude Code para automatizar el flujo de trabajo del equipo de
preventa de Grupo Visión (cotizaciones de sistemas de seguridad/cámaras).

## Qué hace

| Skill | Qué hace | Estado |
|---|---|---|
| `verificar-entorno` | Revisa qué accesos están listos (carpeta compartida, Excels de referencia, config de Bitrix24) y da un checklist de qué falta. | Funcional |
| `armar-cotizacion` | Organiza archivos/carpetas de una cotización (numeración de carpeta, número de oferta, versionado), copia el machote oficial, y llena la pestaña "Equipos" con el equipo/accesorios encontrados (vía `buscar-equipo`) — modelo, descripción, cantidad y costo unitario; las fórmulas de margen/precio de venta del machote calculan el resto solas. | Organización de carpetas funcional y probada en `sandbox-pruebas/`; el llenado de "Equipos" es nuevo (2026-09-01), todavía sin probar |
| `seguimiento-correo` | Redacta (nunca envía) un borrador de correo de seguimiento a clientes según la etapa de la cotización. | Pendiente — placeholder sin conector de correo |
| `sync-bitrix` | Actualiza la tarjeta en el Kanban de Bitrix24 al cerrar una cotización. | Pendiente — placeholder sin webhook de Bitrix |
| `actualizar-catalogo` | Mantiene el catálogo unificado de proveedores en `CLIENTES/00_IA_PREVENTAS/Preventas/Catalogo/` a partir de los PDFs que el equipo agrega. | Catálogo real cargado con 2,358 productos (Hanwha + InVid/Milesight/Paramont/Vision/Secure); falta probar actualización de filas existentes y datos pegados en chat |
| `buscar-equipo` | Busca marca/modelo de equipo que cumpla una especificación técnica dada, consultando el catálogo de `actualizar-catalogo`; también identifica accesorios de instalación (bases/soportes/lentes) compatibles y pregunta si incluirlos. | Diseñado (2026-09-01); pestaña "Compatibilidad de Accesorios" generada sobre el catálogo real (793 pares, 264 modelos de cámara, 3 fuentes: catálogo, categoría genérica, cotizaciones reales); falta probar en una conversación real |

Ver [`docs/notas-proceso.md`](../docs/notas-proceso.md) (en la raíz del
repo) para el contexto completo del proceso de negocio, y el `SKILL.md`
de cada skill (enlazado abajo) para el detalle exacto de qué hace paso a
paso.

## Flujo de trabajo de una cotización

**`verificar-entorno`** y **`actualizar-catalogo`** no son pasos de cada
cotización — son mantenimiento/prerequisito:

- [`verificar-entorno`](skills/verificar-entorno/SKILL.md): corré esto
  una vez al instalar el plugin en una máquina nueva, o si algo falla
  (no encuentra la carpeta compartida, etc.). No hace falta repetirlo en
  cada cotización.
- [`actualizar-catalogo`](skills/actualizar-catalogo/SKILL.md): se corre
  cada vez que llega un catálogo/pricelist nuevo de un proveedor — no
  está ligado a un cliente en particular, pero mantiene fresco el
  catálogo que `buscar-equipo` necesita para funcionar bien.

Con eso ya listo, **una cotización puntual sigue este orden**:

1. **Llega la solicitud** (fuera del plugin, por correo o Bitrix): cliente,
   fechas clave, y documentos con especificaciones técnicas y cantidades
   — ver "Cómo llega una solicitud de licitación" en `notas-proceso.md`.
2. **[`buscar-equipo`](skills/buscar-equipo/SKILL.md)** — **acá es donde
   el asesor le pasa a la IA lo que el cliente pide** (la especificación
   técnica, el pliego de licitación, o marca/modelo si el cliente ya lo
   indicó). El skill busca en el catálogo el equipo que cumple, y si
   hace falta, también los accesorios de instalación compatibles
   (bases, soportes, lentes) — siempre preguntando antes de asumir.
3. **[`armar-cotizacion`](skills/armar-cotizacion/SKILL.md)** — organiza
   la carpeta de la cotización (numeración, número de oferta, copia el
   machote de matriz oficial) y **escribe en la pestaña "Equipos"** el
   equipo/accesorios que salieron del paso 2 (modelo, descripción,
   cantidad, costo unitario), siempre mostrando la tabla antes de
   guardar y esperando confirmación. Las fórmulas de margen/precio de
   venta del machote quedan intactas y calculan solas.
4. **El asesor revisa/ajusta la matriz** (mano de obra, transporte,
   cualquier ítem que no salió de `buscar-equipo`) y la cierra para
   enviar — el costo/margen de cada línea de equipo ya lo calculó el
   machote automáticamente a partir del paso 3.
5. *(Pendiente)* **[`seguimiento-correo`](skills/seguimiento-correo/SKILL.md)**
   — redacta un borrador de seguimiento mientras se espera respuesta del
   cliente.
6. *(Pendiente)* **[`sync-bitrix`](skills/sync-bitrix/SKILL.md)** —
   actualiza la tarjeta del Kanban cuando la cotización se cierra.

## Instalación

Desde cualquier computadora con Claude Code, sin tener que programar ni
copiar archivos a mano:

```
/plugin marketplace add frosalesvision/Preventa-Automation
/plugin install preventa@preventa-automation
```

(El repo es privado — hace falta tener acceso de lectura en GitHub con
las credenciales de git ya configuradas, ej. `gh auth login`.)

## Configuración de Bitrix24 (cuando llegue el webhook)

1. Copiar `plugin-preventa/.mcp.json.example` como referencia.
2. Completar `plugin-preventa/.mcp.json` con la entrada real de Bitrix24
   (ver `verificar-entorno` para confirmar que quedó bien detectado).
3. Nunca pegar el webhook/API key en texto plano en un archivo que se
   vaya a commitear — usar variable de entorno.

## Para quien mantiene este plugin

- Todo el contenido (skills, docs) va en español.
- Cada `SKILL.md` debe quedarse corto; catálogos, tablas de precios o
  plantillas pesadas van en la subcarpeta `references/` del skill que
  corresponda.
- Ningún archivo con datos reales de clientes se commitea (ver
  `.gitignore` en la raíz del repo).
