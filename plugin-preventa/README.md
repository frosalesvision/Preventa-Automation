# Plugin preventa

Plugin de Claude Code para automatizar el flujo de trabajo del equipo de
preventa de Grupo Visión (cotizaciones de sistemas de seguridad/cámaras).

## Qué hace

| Skill | Qué hace | Estado |
|---|---|---|
| `verificar-entorno` | Revisa qué accesos están listos (carpeta compartida, Excels de referencia, config de Bitrix24) y da un checklist de qué falta. | Funcional |
| `armar-cotizacion` | Organiza archivos/carpetas de una cotización (numeración de carpeta, número de oferta, versionado), copia el machote oficial — nunca toca el contenido de la matriz de costos. | Funcional, probado en `sandbox-pruebas/` |
| `seguimiento-correo` | Redacta (nunca envía) un borrador de correo de seguimiento a clientes según la etapa de la cotización. | Pendiente — placeholder sin conector de correo |
| `sync-bitrix` | Actualiza la tarjeta en el Kanban de Bitrix24 al cerrar una cotización. | Pendiente — placeholder sin webhook de Bitrix |
| `buscar-equipo` | Busca marca/modelo de equipo que cumpla una especificación técnica dada. | Planeado, no implementado (fase futura) |

Ver [`docs/notas-proceso.md`](../docs/notas-proceso.md) (en la raíz del
repo) para el contexto completo del proceso de negocio.

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
