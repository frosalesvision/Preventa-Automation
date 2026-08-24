# Preventa-Automation

Repositorio de automatización de preventa de Grupo Visión (Costa Rica).
Es, a la vez, el **código fuente y el marketplace privado** de Claude Code
del plugin `preventa`: un solo repo, sin que nadie del equipo tenga que
copiar archivos a mano.

## Qué es esto

El equipo de preventa arma cotizaciones de sistemas de seguridad/cámaras
de forma manual, en Excel. Este repo contiene un plugin de Claude Code
(`plugin-preventa/`) que automatiza partes de ese flujo: verificar qué
accesos hay listos, armar cotizaciones, redactar seguimientos por correo
y (más adelante) sincronizar con Bitrix24.

Ver [`docs/notas-proceso.md`](docs/notas-proceso.md) para el detalle
completo del proceso de negocio, y [`plugin-preventa/README.md`](plugin-preventa/README.md)
para el detalle de cada skill.

## Cómo instalar el plugin (cualquier computadora, sin programar)

Con Claude Code instalado y acceso de lectura a este repo privado de
GitHub (credenciales de git ya configuradas, ej. `gh auth login`):

```
/plugin marketplace add frosalesvision/Preventa-Automation
/plugin install preventa@preventa-automation
```

Con eso alcanza — Claude Code descarga el plugin desde este repo y lo
deja disponible en esa computadora.

## Estructura del repo

```
.claude-plugin/marketplace.json   → define este repo como marketplace
plugin-preventa/                  → el plugin en sí (skills, .mcp.json)
docs/notas-proceso.md             → contexto del proceso de negocio
```

## Importante

- Este repo es **privado** y así debe quedarse: nunca se sube información
  real de clientes, precios ni credenciales (ver `.gitignore`).
- Todo el contenido del plugin está en español.
- **Permisos de GitHub:** solo el dueño del repo (Fabián) debe tener rol
  de **escritura**. Al agregar a los demás como colaboradores, dales rol
  **Read** (Settings → Collaborators and teams) — con eso alcanza para
  instalar el plugin (`/plugin marketplace add` solo necesita lectura),
  y nadie más puede hacer push de cambios al repo compartido.
