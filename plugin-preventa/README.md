# Plugin preventa

Plugin de Claude Code para automatizar el flujo de trabajo del equipo de
preventa de Grupo Visión (cotizaciones de sistemas de seguridad/cámaras).

## Qué hace

| Skill | Qué hace | Estado (2026-09-25) |
|---|---|---|
| `nueva-cotizacion` | **El punto de entrada.** Recibe el pedido tal como te llegó, pregunta solo lo que falta —tipo de cotización, impuesto del cliente, si va la marca exacta o se acepta un equivalente, financiamiento, tipo de cambio, y si se cotiza con el precio con descuento de GV o el de lista— y encadena los demás skills en orden. | Funcional. Probado en corridas de prueba; **falta que lo use el equipo** |
| `buscar-equipo` | Busca en el catálogo el equipo que cumple la especificación. Muestra el **precio de lista** y el **precio con descuento de GV** de cada línea, pregunta una vez con cuál se arma y avisa qué descuentos no están confirmados; tolera variantes del modelo (prefijo de marca, sufijos) y **sugiere** los accesorios que suelen hacer falta, con su frecuencia. | Funcional. Limitado por lo que hay en el catálogo (ver línea base) |
| `armar-cotizacion` | Crea la carpeta de la cotización, copia el machote, llena `Equipos` (descripción, IMPORTADO, cantidad, costo) y registra la oferta en los dos Excels de control. | Funcional, probado de punta a punta |
| `generar-pdf-cotizacion` | Exporta a PDF **solo** la pestaña de cotización que ve el cliente, después de revisar errores, impuesto y total, y de confirmar nombre y ruta. | Funcional desde 2026-09-25; falta usarlo con una cotización real |
| `seguimiento-correo` | Redacta (nunca envía) el borrador del correo de seguimiento al cliente. | Funcional; faltan ejemplos reales de algunos estados |
| `actualizar-catalogo` | Carga las listas de precios de los proveedores al catálogo tal cual vienen: el precio de lista y, si la lista lo trae, el dealer. El `Precio de compra GV` lo calcula el catálogo solo, con el dealer o con el descuento del proveedor. | Funcional. Catálogo: 4.091 productos (desde el 2026-09-30 con Axis, 2N, APC y Aruba), 28 columnas, 7 chequeos automáticos |
| `verificar-entorno` | Revisa qué accesos están listos y explica la instalación a quien empieza. | Funcional |
| `sync-bitrix` | Actualiza la tarjeta del Kanban de Bitrix24 al cerrar una cotización. | En espera: falta que Operaciones genere el webhook |

Ver [`docs/notas-proceso.md`](../docs/notas-proceso.md) (en la raíz del
repo) para el contexto completo del proceso de negocio, y el `SKILL.md`
de cada skill (enlazado abajo) para el detalle exacto de qué hace paso a
paso.

## Instalación (primera vez en una computadora nueva)

Esto se hace **una sola vez por computadora**. Nadie del equipo necesita
saber programar ni crear ninguna cuenta nueva (ni siquiera de GitHub —
ver Opción A abajo).

1. **Tener Claude Code instalado y abierto.** Si estás leyendo esto desde
   ahí, este paso ya está listo.
2. **Tener la cuenta de Grupo Visión conectada a OneDrive en Windows.**
   Si ya usás Outlook/Teams con tu cuenta de la empresa en esa
   computadora, normalmente esto ya está resuelto — es lo que va a
   sincronizar todas las carpetas compartidas de los pasos siguientes
   (`CLIENTES`, `COMERCIAL 2024`, y la del plugin).
3. **Instalar el plugin** — elegí una de las dos formas:

   **Opción A — sin cuenta de GitHub (la que usa el equipo de preventa):**

   El plugin también vive copiado, ya listo para instalar, en una
   carpeta compartida de OneDrive — no hace falta git ni GitHub ni
   ninguna cuenta extra, solo tener esa carpeta sincronizada.

   1. Confirmá que ves la carpeta compartida `Automatizaciones IA` en tu
      OneDrive de Grupo Visión (mismo mecanismo que `CLIENTES` o
      `COMERCIAL 2024` — si no te aparece, pedile a Fabián que te la
      comparta primero).
   2. Andá hasta `Automatizaciones IA` → `Plugin_preventas_IA_automation`
      en el Explorador de archivos de Windows, y copiá la ruta completa
      de esa carpeta desde la barra de direcciones (click ahí arriba,
      `Ctrl+C`) — **esta ruta es distinta para cada persona** porque
      incluye tu propio usuario de Windows (`C:\Users\<tu usuario>\...`),
      no se puede compartir un solo comando copiar-y-pegar para todos.
   3. En Claude Code, corré (pegando tu ruta completa entre comillas
      donde dice `<TU RUTA>`):
      ```
      /plugin marketplace add "<TU RUTA>"
      ```
      **Este paso (`marketplace add`) siempre va antes del `install` de
      abajo — es obligatorio, no se puede saltar directo al `install`.**
   4. Después corré:
      ```
      /plugin install preventa@preventa-automation
      ```

   **Opción B — con cuenta de GitHub (alternativa, ej. para quien
   mantiene el plugin):**
   ```
   /plugin marketplace add frosalesvision/Preventa-Automation
   /plugin install preventa@preventa-automation
   ```
   El repo es privado — hace falta acceso de lectura en GitHub. Si el
   comando falla por permisos, correr `gh auth login` primero (o pedirle
   a quien te dio el acceso que confirme que tu usuario de GitHub está
   agregado al repo `frosalesvision/Preventa-Automation`).

   ⚠️ **Mantenimiento de la Opción A (nota para quien administra el
   plugin, no para quien lo instala):** la carpeta de OneDrive es una
   copia manual del repo de git, no se actualiza sola. Cada vez que se
   publique un cambio nuevo, hay que volver a copiar los archivos del
   repo (los que están trackeados en git, nunca `recursos-originales/`
   ni nada con datos reales de clientes) a esa carpeta compartida. No
   está confirmado todavía si `/plugin marketplace update` refresca solo
   una fuente local, o si cada persona necesita sacar y volver a agregar
   el marketplace (`/plugin marketplace remove` + `add` de nuevo) después
   de cada actualización — pendiente de confirmar en la práctica.

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
3. **Respondé las preguntas que te haga.** Pregunta solo lo que falte
   para trabajar —nunca inventa cantidades, características ni
   presupuesto—, y si ya lo dijiste en el pedido no te lo vuelve a
   preguntar. Hay cinco cosas que **pregunta siempre**, porque cambian
   la plata (la quinta, sobre el precio, en el paso 4):
   - **El impuesto del cliente.** Te propone 13%, pero casi un tercio de
     las cotizaciones van exentas y algunas universidades pagan 2%.
   - **Si va la marca exacta o se acepta un equivalente.** Depende del
     presupuesto y del cliente: no lo decide solo.
   - **Si la oferta lleva financiamiento.**
   - **El tipo de cambio.** Te propone el que está en el catálogo y te
     pregunta si lo mantenemos o lo cambiás para ese proyecto.
   - **Con qué precio se arma: con el descuento de GV o el de lista
     (MSRP).** Una sola vez, cuando ya está elegido el equipo, con los
     descuentos de cada marca a la vista. Lo recomendado es con descuento.
4. **Revisá la lista de equipo antes de que se escriba en ningún
   archivo.** Te va a mostrar marca, modelo, costo y cantidad de cada
   línea y va a esperar tu confirmación. Dos cosas para mirar:
   - Cada línea trae el **precio de lista** y el **precio con descuento
     de GV**. Te pregunta **una sola vez** con cuál armar la cotización,
     mostrando los descuentos que tiene cada marca de tu lista (por
     ejemplo, "Hanwha cámaras X%, medido; ISTC 0%"). Lo recomendado es
     el precio con descuento; si elegís el de lista, el precio al cliente
     sale alrededor de 1,85 veces el MSRP.
   - Te va a **sugerir accesorios** que suelen hacer falta y nadie pide
     —fuente de poder, batería, base del detector, disco del NVR—,
     diciendo en qué porcentaje de las cotizaciones aparecen. Vos
     decidís: nunca los agrega solo.
5. **Confirmá los datos administrativos que falten** (nombre legal del
   cliente, descripción corta para la carpeta, quién es el asesor
   responsable) si te los pregunta.
6. **Recibís el resumen final**: ruta completa de la carpeta creada,
   número de cotización/oferta usados, y en qué fila quedó registrada en
   cada uno de los dos Excels de control — con cualquier cosa pendiente
   de confirmar marcada explícitamente (nunca te va a decir que algo
   quedó listo si en realidad quedó a medias).
7. **Abrí la matriz** (`Matriz-Oferta/` dentro de la carpeta que se creó)
   para ajustar a mano lo que haga falta: mano de obra, transporte,
   cualquier ítem fuera de catálogo. Los porcentajes —transporte,
   imprevistos, administración, margen— vienen con los valores que más
   usa el equipo, y **se cambian a mano cuando el proyecto lo pide**: es
   lo esperado, no un error.
8. **Generá el PDF** cuando esté lista: *"la cotización ya quedó
   lista, generame el PDF"*. Exporta solo la pestaña que ve el cliente
   —la matriz nunca sale de la empresa— y te pregunta el nombre y la
   ruta antes de guardarlo.

Si en algún punto preferís hacerlo paso a paso vos mismo en vez de
describir el pedido completo de una — por ejemplo, solo buscar un equipo
puntual, o ya tenés el equipo decidido y solo querés armar la carpeta —
podés llamar directo a [`buscar-equipo`](skills/buscar-equipo/SKILL.md) o
[`armar-cotizacion`](skills/armar-cotizacion/SKILL.md), sin pasar por
`nueva-cotizacion`.

## Las reglas que sigue el plugin, en corto

Salen de lo que dijo preventa y de medir 1.119 cotizaciones reales. El
detalle y la evidencia de cada una están en
[`docs/reglas-negocio.md`](../docs/reglas-negocio.md), con un índice al
principio.

- **El costo recomendado es el `Precio de compra GV`**, lo que paga Grupo
  Visión: el precio dealer si la lista lo trae; si no, el precio de lista
  menos el descuento del proveedor, que vive en la pestaña `Descuentos
  por proveedor`. Se pregunta una vez por cotización si se usa ese o el
  precio de lista. El precio cargado nunca se reemplaza por el precio con
  descuento. El MSRP es donde suele *terminar* el precio al cliente, no
  de donde arranca el cálculo (R4, R15).
- **`IMPORTADO` dice a quién se le compra**, no dónde se fabrica. Con
  `no`, transporte y DAI quedan en cero. Una línea de flete va siempre
  como `no` (R1, R1.1).
- **El impuesto al cliente se pregunta siempre**, con 13% recomendado;
  hay una tabla de 46 clientes con régimen especial (R3).
- **Marca exacta o equivalente la decide el asesor.** En una licitación
  con marca obligatoria nunca se ofrece otra (R18).
- **Los accesorios que nadie pide se sugieren, nunca se agregan solos**
  (R19).
- **Solo dólares.** Si un proveedor cotiza en otra moneda, la convierte
  quien cotiza (R16).
- **Los porcentajes vienen con los valores más usados y se editan en el
  Excel.** La primera corrida apunta a quedar bien; siempre se puede
  corregir a mano (R17).
- **Nunca se escribe una fórmula del machote, nunca se manda la matriz al
  cliente y nunca se envía un correo**: se redacta y lo manda una
  persona.

## Dónde está cada cosa

| Qué | Dónde |
|---|---|
| El catálogo | `CLIENTES/00_IA_PREVENTAS/Preventas/Catalogo/Catalogo de productos por proveedor.xlsx`. Empezá por su pestaña `LEEME` |
| Qué significa cada columna del catálogo | Pestaña `Guia de columnas` del mismo archivo |
| El descuento de cada proveedor | Pestaña `Descuentos por proveedor`: el catálogo lo aplica solo; preventa lo confirma |
| A quién se le compra, su vendedor, teléfono y correo, si es importado | Pestaña `Proveedores` |
| Las marcas que faltan cargar | Pestaña `Marcas por cargar`: la completa preventa |
| Los accesorios que se sugieren | Pestaña `Accesorios Requeridos` |
| Los clientes: sus datos (cédula, contacto, teléfono, correo, dirección, asesor) y el impuesto de cada uno | Pestaña `Clientes` (antes `Regimen Fiscal Clientes`): la corrige y completa preventa |
| El machote de la matriz | `plugin-preventa/skills/armar-cotizacion/references/`. Trae su `LEEME` y tres guías al final: pestañas, fórmulas y skills |
| Las reglas de negocio | [`docs/reglas-negocio.md`](../docs/reglas-negocio.md) |
| Lo que falta que conteste preventa | [`docs/pendientes-comercial.md`](../docs/pendientes-comercial.md) |

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
6. **[`generar-pdf-cotizacion`](skills/generar-pdf-cotizacion/SKILL.md)**
   — exporta a PDF la pestaña de cotización que ve el cliente.
7. **[`seguimiento-correo`](skills/seguimiento-correo/SKILL.md)** —
   redacta un borrador de seguimiento mientras se espera respuesta del
   cliente. El PDF se adjunta a mano.
8. *(En espera)* **[`sync-bitrix`](skills/sync-bitrix/SKILL.md)** —
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
- **Después de cada carga o edición del catálogo**, correr
  `python scripts/verificar-catalogo.py`. Revisa siete cosas que Excel no
  avisa, entre ellas filas repetidas, fórmulas que apuntan a otra fila y
  un número escrito encima de la fórmula del precio de compra.
- **Nunca borrar filas del catálogo con `openpyxl`**: no reajusta las
  fórmulas. Y nunca guardar con `openpyxl` el machote ni los Excels de
  control: borra los dibujos y los desplegables sin avisar. Se escribe
  con Excel (COM).
- **Para medir si el plugin mejoró**, repetir la línea base sobre los
  mismos 10 casos: `python scripts/casos-patron-linea-base.py --rehacer`.
