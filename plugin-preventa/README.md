# Plugin preventa

Plugin de Claude Code para automatizar el flujo de trabajo del equipo de
preventa de Grupo Visión (cotizaciones de sistemas de seguridad/cámaras).

## Qué hace

| Skill | Qué hace | Estado |
|---|---|---|
| `nueva-cotizacion` | Punto de entrada recomendado: recibe el pedido de un cliente en lenguaje natural (ej. "necesito 15 cámaras para X, presupuesto ₡5M"), detecta qué datos faltan y pregunta solo eso, y orquesta `buscar-equipo` + `armar-cotizacion` en el orden correcto sin que el asesor tenga que llamar cada skill a mano. | Diseñado (2026-09-08); todavía sin probar en una conversación real |
| `verificar-entorno` | Revisa qué accesos están listos (carpeta compartida `CLIENTES`, Excels de referencia, los dos Excels de control de cotizaciones, config de Bitrix24) y da un checklist de qué falta; también explica paso a paso la instalación inicial completa para alguien que recién empieza. | Funcional — checklist ampliado 2026-09-07 con los dos Excels de control y la guía de instalación inicial |
| `armar-cotizacion` | Organiza archivos/carpetas de una cotización (numeración de carpeta, número de oferta, versionado), copia el machote oficial, llena la pestaña "Equipos" con el equipo/accesorios encontrados (vía `buscar-equipo`) — modelo, descripción, cantidad y costo unitario, las fórmulas de margen/precio de venta calculan el resto solas — y registra la cotización en los dos Excels de control compartidos. | Organización de carpetas funcional y probada en `sandbox-pruebas/`; el llenado de "Equipos" y el registro en los dos Excels de control se probaron de punta a punta el 2026-09-07/08 con una cotización de prueba real (spec de una licitación real, cliente inventado) — funcionando correctamente, incluida verificación de que las fórmulas del machote quedan intactas |
| `seguimiento-correo` | Redacta (nunca envía) un borrador de correo de seguimiento a clientes según la etapa de la cotización. | Pendiente — placeholder sin conector de correo |
| `sync-bitrix` | Actualiza la tarjeta en el Kanban de Bitrix24 al cerrar una cotización. | Pendiente — placeholder sin webhook de Bitrix |
| `actualizar-catalogo` | Mantiene el catálogo unificado de proveedores en `CLIENTES/00_IA_PREVENTAS/Preventas/Catalogo/` a partir de los PDFs que el equipo agrega. | Catálogo real cargado con 2,358 productos (Hanwha + InVid/Milesight/Paramont/Vision/Secure); falta probar actualización de filas existentes y datos pegados en chat |
| `buscar-equipo` | Busca marca/modelo de equipo que cumpla una especificación técnica dada, consultando el catálogo de `actualizar-catalogo`; también identifica accesorios de instalación (bases/soportes/lentes) compatibles y pregunta si incluirlos. | Diseñado (2026-09-01); pestaña "Compatibilidad de Accesorios" generada sobre el catálogo real (793 pares, 264 modelos de cámara, 3 fuentes: catálogo, categoría genérica, cotizaciones reales); probado 2026-09-07 con la especificación técnica real de una licitación municipal real contra el catálogo real, con buenos resultados — todavía falta probarlo en vivo con el equipo de preventa |

Ver [`docs/notas-proceso.md`](../docs/notas-proceso.md) (en la raíz del
repo) para el contexto completo del proceso de negocio, y el `SKILL.md`
de cada skill (enlazado abajo) para el detalle exacto de qué hace paso a
paso.

## Instalación (primera vez en una computadora nueva)

Esto se hace **una sola vez por computadora**. Son 5 pasos, ninguno
requiere programar ni copiar archivos a mano:

1. **Tener Claude Code instalado y abierto.** Si estás leyendo esto desde
   ahí, este paso ya está listo.
2. **Instalar el plugin:**
   ```
   /plugin marketplace add frosalesvision/Preventa-Automation
   /plugin install preventa@preventa-automation
   ```
   El repo es privado — hace falta acceso de lectura en GitHub. Si el
   comando falla por permisos, correr `gh auth login` primero (o pedirle
   a quien te dio el acceso que confirme que tu usuario de GitHub está
   agregado al repo `frosalesvision/Preventa-Automation`).
3. **Tener la cuenta de Grupo Visión conectada a OneDrive en Windows.**
   Si ya usás Outlook/Teams con tu cuenta de la empresa en esa
   computadora, normalmente esto ya está resuelto — es lo que sincroniza
   la carpeta compartida `CLIENTES` automáticamente. Se confirma en el
   paso siguiente.
4. **Agregar los dos accesos directos de Excel de control de
   cotizaciones** (`Cotizaciones en Preventa.xlsx` y `Control de
   cotizaciones 2026.xlsx`, ambos dentro de la carpeta compartida
   `COMERCIAL 2024`):
   - Entrar a <https://grupovisionorg-my.sharepoint.com/> con tu cuenta
     de Grupo Visión.
   - En el menú izquierdo, "Compartido" → buscar la carpeta `COMERCIAL
     2024` (si no aparece, alguien con acceso tiene que compartírtela
     primero — hoy: María Fernanda Loria).
   - Click derecho sobre la **carpeta** `COMERCIAL 2024` (nunca sobre un
     archivo suelto — un acceso directo a un archivo individual no trae
     contenido real, solo un puntero web) → "Agregar acceso directo" →
     "Mis archivos".
   - Esperar unos minutos a que sincronice (trae bastante contenido).
5. **(Recomendado, no obligatorio) Instalar la extensión "Claude for
   Chrome"** e iniciar sesión con la misma cuenta, en el Chrome donde
   también tenés tu cuenta de Grupo Visión. Ayuda para tareas puntuales
   que necesitan navegador — no es necesario para el día a día.

Después de esto, abrí una conversación nueva con el plugin y decile a
Claude **"revisá el entorno"** — corre
[`verificar-entorno`](skills/verificar-entorno/SKILL.md), que confirma
con evidencia real (no de memoria) qué quedó bien y qué falta todavía.
No sigas al siguiente paso hasta que ese checklist salga en ✅ completo.

## Cómo usar el plugin (tu primera cotización)

1. **Confirmá el entorno** (si no lo hiciste ya): "revisá el entorno".
2. **Describí el pedido tal cual te llegó**, en una sola frase, sin
   preocuparte por el nombre de ningún skill. Por ejemplo:

   > Necesito un proyecto para un cliente que se llama XClient, al menos
   > 15 cámaras para su establecimiento, presupuesto de 5 millones de
   > colones, las cámaras deben ser de la más alta calidad junto a su
   > match de extras como extensiones y demás.

   Esto activa [`nueva-cotizacion`](skills/nueva-cotizacion/SKILL.md).
3. **Respondé las preguntas que te haga.** Va a preguntar solo lo que
   falte para poder trabajar (nunca inventa cantidades, características
   ni presupuesto) — cosas como si las cámaras son todas iguales, si hace
   falta grabador/NVR, si el presupuesto incluye instalación, etc. Si ya
   contestaste algo en tu pedido inicial, no te lo vuelve a preguntar.
4. **Revisá la lista de equipo antes de que se escriba en ningún
   archivo.** Te va a mostrar marca/modelo/precio/cantidad de cada línea
   (equipo principal y accesorios) y va a esperar tu confirmación — es el
   momento de corregir algo si no es lo que buscabas.
5. **Confirmá los datos administrativos que falten** (nombre legal del
   cliente, descripción corta para la carpeta, quién es el asesor
   responsable) si te los pregunta.
6. **Recibís el resumen final**: ruta completa de la carpeta creada,
   número de cotización/oferta usados, y en qué fila quedó registrada en
   cada uno de los dos Excels de control — con cualquier cosa pendiente
   de confirmar marcada explícitamente (nunca te va a decir que algo
   quedó listo si en realidad quedó a medias).
7. **Abrí la matriz** (`Matriz-Oferta/` dentro de la carpeta que se creó)
   para ajustar a mano lo que el plugin no cubre todavía (mano de obra,
   transporte, cualquier ítem fuera de catálogo) antes de enviarla.

Si en algún punto preferís hacerlo paso a paso vos mismo en vez de
describir el pedido completo de una — por ejemplo, solo buscar un equipo
puntual, o ya tenés el equipo decidido y solo querés armar la carpeta —
podés llamar directo a [`buscar-equipo`](skills/buscar-equipo/SKILL.md) o
[`armar-cotizacion`](skills/armar-cotizacion/SKILL.md), sin pasar por
`nueva-cotizacion`.

## Flujo de trabajo de una cotización (referencia técnica)

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
2. **El asesor le describe el pedido a Claude tal cual le llegó** (en
   lenguaje natural, ej. "necesito una cotización para el cliente X, al
   menos 15 cámaras, presupuesto de ₡5 millones, la mejor calidad") — no
   hace falta que sepa el nombre de ningún skill.
   **[`nueva-cotizacion`](skills/nueva-cotizacion/SKILL.md)** es el punto
   de entrada que toma esto: detecta qué datos ya vinieron y cuáles
   faltan, pregunta solo lo que falta, y por dentro va llamando en orden
   a los dos skills siguientes — el asesor no tiene que invocarlos a
   mano.
3. **[`buscar-equipo`](skills/buscar-equipo/SKILL.md)** (llamado por
   `nueva-cotizacion`, o directo si el asesor ya sabe exactamente qué
   buscar) — busca en el catálogo el equipo que cumple la especificación,
   y si hace falta, también los accesorios de instalación compatibles
   (bases, soportes, lentes) — siempre preguntando antes de asumir.
4. **[`armar-cotizacion`](skills/armar-cotizacion/SKILL.md)** (llamado
   por `nueva-cotizacion`, o directo si el asesor ya tiene el equipo
   decidido) — organiza la carpeta de la cotización (numeración, número
   de oferta, copia el machote de matriz oficial), **escribe en la
   pestaña "Equipos"** el equipo/accesorios que salieron del paso
   anterior (modelo, descripción, cantidad, costo unitario) siempre
   mostrando la tabla antes de guardar y esperando confirmación, y
   **registra la cotización en los dos Excels de control**. Las fórmulas
   de margen/precio de venta del machote quedan intactas y calculan
   solas.
5. **El asesor revisa/ajusta la matriz** (mano de obra, transporte,
   cualquier ítem que no salió de `buscar-equipo`) y la cierra para
   enviar — el costo/margen de cada línea de equipo ya lo calculó el
   machote automáticamente a partir del paso anterior.
6. *(Pendiente)* **[`seguimiento-correo`](skills/seguimiento-correo/SKILL.md)**
   — redacta un borrador de seguimiento mientras se espera respuesta del
   cliente.
7. *(Pendiente)* **[`sync-bitrix`](skills/sync-bitrix/SKILL.md)** —
   actualiza la tarjeta del Kanban cuando la cotización se cierra.

Los pasos 3 y 4 siguen funcionando igual de forma independiente (por
ejemplo, si el asesor solo quiere buscar un equipo puntual, o ya tiene el
equipo decidido y solo quiere armar la carpeta) — `nueva-cotizacion` es
una capa de conveniencia encima, no un reemplazo.

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
