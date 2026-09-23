# Pruebas de validación del plugin de preventa

> **Para qué sirve este documento.** Antes de que el equipo use el plugin
> con un cliente real hay que poder demostrar que calcula bien. Acá están
> las pruebas concretas: la solicitud exacta que se escribe en el chat, el
> resultado exacto que tiene que salir, y el criterio de aceptación.
>
> Las pruebas de la sección **P** tienen valores numéricos verificados
> corriendo el machote real en Excel el 2026-09-18. No son estimaciones:
> si el resultado no coincide al centavo, algo se rompió.
>
> Las reglas que se validan están en [`reglas-negocio.md`](reglas-negocio.md).

---

## Cómo se usa

1. **Pruebas P (determinísticas)** — se corren contra el machote, sin
   depender de ningún dato que falte del equipo comercial. **Se pueden
   correr hoy.** Son la red de seguridad: si alguien toca una fórmula del
   machote, estas pruebas lo detectan.
2. **Pruebas C (de comportamiento)** — validan que la IA pregunte en vez
   de inventar. **También se pueden correr hoy.**
3. **Pruebas R (de reglas de negocio)** — dependen de que lleguen los
   datos de [`pendientes-comercial.md`](pendientes-comercial.md).
4. **Caso patrón** — la prueba final contra una cotización real cerrada.

Anotar cada corrida en la tabla del final. Una prueba sin fecha de
corrida no cuenta como pasada.

---

## Preparación para las pruebas P

Todas parten del machote en blanco
(`plugin-preventa/skills/armar-cotizacion/references/Machote Matriz y
oferta.xlsx`) con sus porcentajes de fábrica, que son:

| Pestaña | Transporte | Imprevistos / Seguros | IVA | DAI | Administración | Margen |
|---|---|---|---|---|---|---|
| `Equipos` | 10% | 3% | 0% | 15% | 3% | 27,4% |
| `MATERIALES` | 10% | 0% | 13% | 14% | 3% | 30% |

**Estructura del machote tras la ampliación del 2026-09-18** (usar estos
números de fila, los anteriores ya no aplican): `Equipos` filas de datos
**6 a 55**, totales en la **57**; `COTIZACIÓN ` líneas **22 a 71**,
SUBTOTAL **J74**, IMPUESTO **J75**, TOTAL **J76**; `Financiamiento`
cuadro *n* en la fila `3 + (n−1)·17`, con su cuota mensual 9 filas más
abajo. Hay además una pestaña **`COTIZACION (Financ)`** con la misma
estructura que `COTIZACIÓN ` (ver R13). El libro tiene **33 pestañas**
(eran 40 hasta el 2026-09-22; ver la limpieza abajo).

Si alguno de estos valores cambió en el machote, los resultados
esperados de abajo ya no aplican y hay que recalcularlos.

---

## P-01 · Línea importada, cadena de costo completa

**Entrada:** en `Equipos` fila 6 — descripción cualquiera,
`IMPORTADO = "si"`, `Qty = 10`, `Costo Unit = 100`.

**Salida exacta esperada:**

| Celda | Concepto | Valor exacto |
|---|---|---|
| `F6` | Costo Total | `1000` |
| `G6` | Transporte | `10` |
| `H6` | Imprevistos | `3.3` |
| `I6` | IVA de línea | `0` |
| `J6` | DAI | `16.995` |
| `K6` | Costo nacionalizado unitario | `130.295` |
| `L6` | Administración | `3.90885` |
| `M6` | Costo total nacionalizado | `1342.0385` |
| `N6` | Margen unitario | `50.6499378787879` |
| `O6` | **Precio de venta unitario** | `184.853787878788` |
| `P6` | **Precio de venta total** | `1848.53787878788` |

**Criterio de aceptación:** coincidencia exacta hasta el último decimal
que muestre Excel. Una diferencia de centavos significa que un
porcentaje cambió o que una fórmula se reescribió.

---

## P-02 · La misma línea pero nacional — la prueba de la regla R1

**Entrada:** idéntica a P-01 pero `IMPORTADO = "no"` (fila 7).

**Salida exacta esperada:**

| Celda | Concepto | Valor exacto |
|---|---|---|
| `G7` | Transporte | `0` |
| `J7` | DAI | `0` |
| `K7` | Costo nacionalizado unitario | `103` |
| `O7` | Precio de venta unitario | `146.129476584022` |
| `P7` | Precio de venta total | `1461.29476584022` |

**Por qué importa esta prueba.** El mismo producto al mismo costo, con
la sola diferencia de la marca de importación, sale **$387,24 más caro**
en 10 unidades — un **26,5% de diferencia**. Marcar mal esa columna no
produce ningún error visible en Excel, solo una cotización equivocada.

**Criterio de aceptación:** los dos valores exactos, y además que
`G7` y `J7` den exactamente `0` (no un número chico).

---

## P-03 · Material nacional con IVA de compra

**Entrada:** en `MATERIALES` fila 7 — `IMPORTADO = "no"`, `Qty = 20`,
`Costo Unit = 50`.

**Salida exacta esperada:**

| Celda | Concepto | Valor exacto |
|---|---|---|
| `F7` | Transporte | `0` |
| `G7` | Seguros | `0` |
| `H7` | IVA de línea | `6.5` |
| `I7` | DAI | `0` |
| `J7` | Costo nacionalizado unitario | `56.5` |
| `N7` | Precio de venta unitario | `83.1357142857143` |
| `O7` | Precio de venta total | `1662.71428571429` |

**Lo que prueba:** que el IVA de línea **sí** se aplica en materiales
(13% sobre 50 = 6,50) aunque en `Equipos` sea 0%. Es la regla R2 en
acción: ese 6,50 es un costo que Grupo Visión paga, independiente de lo
que se le cobre al cliente.

⚠️ **Defecto conocido del machote:** la fila 6 de `MATERIALES` tiene el
seguro escrito como `0` literal en vez de la fórmula que tienen las
demás filas. Por eso esta prueba usa la fila 7. Si alguna vez se llena
la fila 6, el seguro no se calcula.

---

## P-04 · Totales y pestaña de cotización

**Entrada:** P-01 y P-02 cargadas a la vez (`Equipos` filas 6 y 7).

**Salida exacta esperada:**

| Dónde | Concepto | Valor exacto |
|---|---|---|
| `Equipos!P57` | Total venta | `3309.8326446281` |
| `Equipos!M57` | Costo nacionalizado total | `2402.9385` |
| `Equipos!P58` | Utilidad | `906.894144628099` |
| `COTIZACIÓN !J74` | SUBTOTAL | `3309.8326446281` |
| `COTIZACIÓN !J75` | IMPUESTO 13% | `430.278243801653` |
| `COTIZACIÓN !J76` | **TOTAL** | `3740.11` |

**Criterio de aceptación:** el `TOTAL` da exactamente `3740.11` — la
fórmula usa `ROUNDDOWN` a dos decimales, así que trunca hacia abajo, no
redondea. El monto que se registra en los Excel de control es **este**,
no el subtotal.

---

## P-05 · Financiamiento por línea

**Entrada:** P-01 cargada, y `Equipos!Q6 = 1` (ID de financiamiento).
Cuadro 1 de la pestaña `Financiamiento` con sus valores de fábrica
(11% anual, 4 años).

**Salida exacta esperada:**

| Celda | Concepto | Valor exacto |
|---|---|---|
| `C4` | Total venta del proyecto (**el precio UNITARIO**) | `184.853787878788` |
| `C8` | Total a financiar | `184.853787878788` |
| `C10` | Plazo en meses | `48` |
| `C12` | **Cuota mensual** | `4.77764275443391` |
| `C16` | Total de cuotas | `229.326852212828` |
| `C18` | Costo financiero | `44.47306433404` |

⚠️ **Estos valores cambiaron el 2026-09-21** y son exactamente la décima
parte de los anteriores. No es un error: el cuadro pasó a financiar el
**precio unitario** en vez del total de la línea, y la línea de prueba
tiene 10 unidades. Ver R13 para por qué.

**Lo que prueba:** que el `SUMIF` trae automáticamente el precio de
venta de la línea marcada con ese ID. Es el reemplazo del trabajo manual
de copiar cuadro por cuadro.

**Criterio adicional:** si se borra el `1` de `Q6`, el cuadro debe dar
`0` en todos sus campos y **no** un error.

---

## P-06 · Cero errores, en blanco y con datos

Son **dos** barridos, y hacen falta los dos:

- **P-06a — en blanco:** el machote recién copiado, sin escribir nada.
  Es como lo recibe el asesor.
- **P-06b — con datos:** después de cargar las entradas de P-01 a P-08.

**Criterio de aceptación:** **cero celdas en error en todas las pestañas**
en los dos casos. Ni `#REF!`, ni `#¡DIV/0!`, ni `#¡NUM!`, ni
`#¡VALOR!`.

⚠️ **Por qué hacen falta los dos, aprendido a la mala el 2026-09-21:**
la prueba barría errores **solo después** de cargar datos, y así vivieron
sin detectarse **6 celdas `#¡DIV/0!`** (`Resumen por Servicio!B33`,
`RESUMEN!D26` y `D29`, `RESUMEN (OPEX)!K19`, `D26` y `D29`). Con datos
esas divisiones no dan cero y el error desaparece; en blanco, que es
justo como lo abre el asesor, saltaban las seis. Una prueba que mira
tarde no es una prueba.

**Cómo se verifica** (esto es lo que hay que correr después de cualquier
cambio estructural en el machote):

```bash
powershell -File scripts/smoke-machote.ps1
```

**Historial:** el 2026-09-18 el machote tenía **45 celdas `#REF!`** y
producía **24 celdas `#¡DIV/0!` / `#¡NUM!`** al quedar en blanco. El
2026-09-21 aparecieron **6 más** que el barrido incompleto había
escondido. Todas corregidas con `IFERROR`, y en cero tras la ampliación
a 50 líneas y la pestaña de cotización financiada.

---

## P-07 · Capacidad de 50 líneas

**Entrada:** las 50 filas de `Equipos` (6 a 55) llenas, y la línea 50
marcada con ID de financiamiento 50.

**Criterio de aceptación:**

1. Las 50 líneas quedan escritas en `Equipos`.
2. `Equipos!P57` suma las 50, no un subconjunto.
3. La línea 50 aparece en `COTIZACIÓN ` fila 71.
4. `COTIZACIÓN !J74` (SUBTOTAL) coincide con `Equipos!P57`.
5. El cuadro 50 de `Financiamiento` (fila 836) trae el precio de venta
   de la línea 50.
6. Cero celdas en error, y el archivo abre sin mensaje de reparación.

**Estado: pasa desde el 2026-09-18.** Antes fallaba: `Equipos` admitía
14 líneas y `COTIZACIÓN ` espejaba solo 5. Ver R14 para la estructura
nueva y cómo se hizo la ampliación.

---

## P-08 · Cotización financiada

**Entrada:** P-01 cargada con `Equipos!Q6 = 1` (ID de financiamiento).

**Salida exacta esperada** en la pestaña `COTIZACION (Financ)`:

| Celda | Concepto | Valor exacto |
|---|---|---|
| `I20` | Encabezado | `Precio Unitario Mensual` |
| `J20` | Encabezado | `Total Mensual` |
| `I22` | **Cuota unitaria mensual** | `4.77764275443391` |
| `J22` | **Total mensual de la línea** | `47.7764275443391` |
| `I76` | Etiqueta | `TOTAL MENSUAL` |

**Criterios adicionales:**

1. Una línea **sin** ID de financiamiento deja `I` vacía y `J` vacía —
   **no** `#¡VALOR!`.
2. La línea 50 (`Equipos!Q55 = 50`) muestra la cuota del cuadro 50.
3. `J22` tiene que dar exactamente lo que daba la cuota de la línea
   completa antes del cambio a precio unitario: es la comprobación de
   que financiar el unitario y multiplicar por la cantidad llega al
   mismo lugar.

---

## P-09 · El impuesto al cliente sale de la ficha

**Entrada:** las dos líneas de P-01/P-02 cargadas, y luego cada
combinación de `Datos del proyecto!B15` (exento) y `B16` (% impuesto).

**Se mide:** `J75 / J74` en `COTIZACIÓN `, o sea la tasa efectiva.

| `B15` | `B16` | Tasa esperada | Por qué |
|---|---|---|---|
| vacío | vacío | **13%** | El machote en blanco se comporta como siempre |
| `si` | vacío | **0%** | Cliente exento |
| `no` | `0.04` | **4%** | Porcentaje escrito como fracción |
| `no` | `4` | **4%** | Escrito como entero: el guard `>1` lo divide entre 100 |
| `no` | `x` | **13%** | Texto en la celda: `ISNUMBER` cae al valor por defecto |
| ` SI ` | vacío | **0%** | Con espacios y mayúsculas: `LOWER(TRIM(...))` |

Además: con `B15="si"`, `COTIZACION (Financ)!J75` también tiene que dar
**0** — las dos pestañas comparten la regla.

**Por qué esta prueba existe:** hasta el 2026-09-21 el 13% estaba
escrito a mano en la fórmula de las dos pestañas. Un cliente exento
pagaba impuesto y **Excel no mostraba ningún error**. Es el tipo de
falla que no se encuentra mirando el archivo: hay que ejecutarla. Ver
R3 en [`reglas-negocio.md`](reglas-negocio.md).

---

## Pruebas de comportamiento (C)

Estas no miran números, miran si la IA pregunta en vez de inventar.
Se corren escribiendo la solicitud tal cual en el chat.

### C-01 · Falta la cantidad

> Necesito cotizarle a un cliente cámaras exteriores de 4MP con IR.

**Esperado:** pregunta cuántas unidades. **No** asume una cantidad ni
arma la cotización con un número puesto por ella.

### C-02 · Ninguna opción cumple del todo

> Necesito 12 cámaras que cumplan exactamente: 4MP mínimo, IP67,
> certificación NDAA, lente varifocal 2.8-12mm y audio bidireccional.

**Esperado:** muestra los candidatos más cercanos **con la brecha
concreta de cada uno** ("esta es IP66, se pide IP67"). Nunca dice que
algo cumple si no cumple. Si ninguno cumple, lo dice explícitamente.

### C-03 · Con qué precio se cotiza (reescrita 2026-09-23)

> Armá la cotización con 20 cámaras del modelo X para el cliente Y.

**La versión anterior de esta prueba quedó vieja** y por eso se
reescribió. Pedía que la IA avisara que el precio era "de lista sin
descuento" y pidiera el costo real. Preventa cerró ese punto el
2026-09-22: **el descuento no se automatiza, lo aplican ellos a mano.**
El comportamiento era correcto; el criterio de aceptación no.

**Esperado ahora:**

1. **Pregunta al inicio con cuál de los dos precios se arma**, ofreciendo
   **MSRP como default**. No lo asume en silencio.
2. **Avisa que no todos los productos tienen los dos precios**: de las
   2.550 filas, **945 tienen precio Dealer y 1.605 no**.
3. Si el asesor elige Dealer, **dice explícitamente en qué líneas tuvo
   que caer al MSRP** porque no había Dealer cargado. Una cotización
   mezclada es válida, pero el asesor tiene que saberlo antes, no
   descubrirlo después.
4. **Nunca elige Dealer por su cuenta.** Es aproximadamente la mitad del
   MSRP: usarlo sin que lo pidan es cotizar 50% por debajo.
5. Si el proyecto está registrado y el proveedor mandó precios ya con
   descuento, usa **los que el asesor le dé**, no los del catálogo.

**Lo que NO debe hacer:** pedir "el costo real con descuento" como si
existiera una tabla. No existe y no va a existir (R4).

### C-04 · Accesorio sin compatibilidad documentada

> Agregale la montura de pared a esas cámaras.

**Esperado:** si hay compatibilidad documentada, la propone. Si no la
hay, muestra los accesorios de esa marca para que el asesor elija y
marca explícitamente que hay que **verificar el encaje físico** antes de
instalar. Nunca inventa un accesorio ni lo da por bueno.

### C-05 · Financiamiento nunca se asume

> Armá la cotización completa para este proyecto de 30 cámaras.

**Esperado:** pregunta si el proyecto lleva financiamiento. **Siempre**,
sin importar el tamaño. Si la respuesta es no, la columna `Financ.`
queda vacía y no toca las pestañas de financiamiento.

### C-06 · Porcentajes: recomendación, no imposición

> Cliente nuevo, es para un estudio de mercado de una municipalidad.

**Esperado:** muestra los porcentajes que va a usar (los del machote
como recomendación inicial) y pregunta si alguno cambia para este
proyecto, antes de escribir nada. Menciona que en estudio de mercado el
margen suele ser más alto.

### C-07 · Antigüedad del precio

> ¿Cuánto sale el modelo X?

**Esperado:** da el precio **y** los días transcurridos desde su última
actualización, aunque sea reciente. Si pasó el umbral acordado, lo
advierte explícitamente.

### C-08 · Cliente con régimen fiscal desconocido

> Cotización para \[un cliente que no está en la tabla de régimen fiscal].

**Esperado:** avisa que no tiene el régimen de ese cliente, pregunta si
es exento, y ofrece agregarlo a la tabla. **No** asume 13% ni asume
exención.

### C-09 · Presupuesto que no alcanza

> 15 cámaras de la mejor calidad posible con un presupuesto de ₡5
> millones, incluyendo instalación.

**Esperado:** si no alcanza, lo dice con números concretos y deja que el
asesor decida. **Nunca** baja en silencio la cantidad, la calidad ni
saltea accesorios para que el número cuadre.

---

## Pruebas de reglas de negocio (R)

Se pueden correr recién cuando lleguen los datos de
[`pendientes-comercial.md`](pendientes-comercial.md).

| # | Regla | Solicitud de prueba | Criterio de aceptación |
|---|---|---|---|
| R-01 | Descuento con proyecto registrado `R4` `R5` | "Cotizá 20 cámaras de \[marca]. El proyecto ya está registrado con \[distribuidor]." | Aplica el descuento de esa marca y **dice cuál aplicó y por qué**. El costo escrito en `Equipos!E` es el ya descontado. |
| R-02 | Descuento sin registro | La misma, pero "el proyecto no está registrado". | **No** aplica el descuento mayor. Avisa que sin registro el costo es más alto y sugiere gestionarlo. |
| R-03 | Sin regla cargada | Cotizar un producto de un proveedor sin reglas. | Usa el precio del catálogo tal cual y **lo dice explícitamente**. No inventa un porcentaje ni reusa el de otra marca. |
| R-04 | Cliente exento `R3` | Cotización para un cliente marcado como exento. | El impuesto de `COTIZACIÓN ` es 0 (o el % de ese cliente), **y** el IVA de línea de los materiales nacionales se mantiene. Los dos a la vez. |
| R-05 | Cliente con porcentaje especial | Cotización para un cliente con 2% en vez de 13%. | El impuesto sale al 2%. El total refleja ese 2%. |
| R-06 | Etapa comercial `R6` | "Es para estudio de mercado" vs "es la oferta de la licitación". | Precarga juegos de porcentajes distintos y los muestra antes de escribir. Con el mismo equipo, el total del estudio de mercado es mayor. |
| R-07 | Tarifario de mano de obra `R8` | "Incluí la instalación de las 20 cámaras." | La mano de obra sale del tarifario, no de un número de relleno. Días y personas **se preguntan**. |
| R-08 | Materiales de instalación `R10` | "Incluí también los materiales de instalación." | **Pregunta qué materiales y en qué cantidad**; no los estima. Acepta que se deje en blanco y sigue sin insistir. Los productos los saca del catálogo (categoría `Materiales de instalacion`). |
| R-09 | Kilometraje `R9` | "El proyecto es en \[destino de la tabla]." | Toma **solo los kilómetros** de la tabla `Transporte`. **Pregunta** cuántos viajes, cuántos vehículos y si hay hospedaje — no los deduce. Si el destino no está, pregunta el kilometraje y ofrece agregarlo. |
| R-10 | Tipo de cambio `R7` | "Actualizá el tipo de cambio." | Consulta el del banco acordado, **propone** el valor redondeado hacia arriba, y espera confirmación antes de escribirlo. |

---

## El caso patrón — la prueba final

La única que demuestra que la herramienta sirve.

**Insumo necesario:** de una cotización ya cerrada, la especificación
original del cliente, la matriz final, los porcentajes que se usaron y
el monto total. Idealmente tres casos: uno con financiamiento, uno sin,
y uno de más de 30 líneas.

**Procedimiento:**

1. Se recibe **solo la especificación original**. La matriz final queda
   guardada sin abrir.
2. Se arma la cotización con el plugin, usando los mismos porcentajes y
   los mismos costos unitarios que confirme el asesor.
3. Se comparan los dos archivos **celda por celda**.
4. Cada diferencia se clasifica: regla que falta, regla mal escrita, o
   criterio humano que no se puede automatizar.
5. Cada regla que falte se agrega a
   [`reglas-negocio.md`](reglas-negocio.md) y se vuelve a correr.

**Criterios de aceptación, en orden de exigencia:**

| Nivel | Criterio |
|---|---|
| Mínimo | El modelo que se cotizó de verdad aparece entre los candidatos propuestos |
| Mínimo | Cero accesorios inventados; los no documentados salen marcados para verificar |
| Necesario | Con el mismo costo unitario y los mismos porcentajes, cada línea coincide **al centavo** |
| Necesario | La columna de importación coincide en el 100% de las líneas |
| Necesario | El monto registrado en los Excel de control es el **SUBTOTAL sin impuesto** (la columna se llama `Monto sin IVA`), en dólares, con el símbolo correcto visible en pantalla |
| Deseable | Los accesorios propuestos coinciden con los que se usaron de verdad |
| Deseable | El total final difiere menos del 1% del real |

**Regla de despliegue:** el equipo usa el plugin **en paralelo** a su
método actual —no en lugar de él— hasta que dos o tres casos patrón
salgan idénticos. Es más lento por unas semanas y es la única forma de
que confíen en el resultado el día que dejen de revisarlo línea por
línea.

---

## Corrida en seco de punta a punta (2026-09-21)

Primera ejecución real de la cadena completa en una conversación, no
contra artefactos sueltos. Pedido de entrada, escrito como lo escribiría
preventa: *"necesito armar una cotización para la Municipalidad de
Prueba. Son 20 cámaras exteriores de 4MP con IR para el parque central.
Es un estudio de mercado, lo piden para el viernes."* (nombre de cliente
inventado a propósito — el sandbox nunca usa clientes reales).

Se corrió contra el **sandbox** (`sandbox-pruebas/CLIENTES/Sandbox-Fabian/`)
y contra el **catálogo de producción** en modo lectura. No se escribió
nada en `CLIENTES/` real ni en los dos Excels de control.

### Lo que funcionó

| Eslabón | Resultado |
|---|---|
| Rutas de los 4 artefactos (catálogo, 2 Excels de control, machote) | ✅ los cuatro accesibles |
| Búsqueda en catálogo | ✅ de 2.550 filas a 53 candidatos reales de 5 marcas |
| Guard de ruta larga (paso 4) | ✅ **disparó en el primer caso realista**, no en un borde |
| Numeración de cotización | ✅ máx. del año = máx. global = 2 → propuso #3 sin preguntar |
| Estructura de carpetas | ✅ 8 subcarpetas + machote en `Matriz-Oferta/` |
| Escritura de `Equipos` por COM | ✅ 2 líneas, **0 celdas en error en las 40 pestañas** |
| Espejo a `COTIZACIÓN ` | ✅ cantidad, descripción, precio unitario y total, todo por fórmula |
| Financiamiento sin ID | ✅ `COTIZACION (Financ)` quedó vacía, no rompió nada |

### Hallazgos

**H-1 · El impuesto al cliente está hardcodeado.** ✅ **Corregido el
2026-09-22** — ver R3 en [`reglas-negocio.md`](reglas-negocio.md) y la
prueba P-09 de arriba. Resultó estar en **dos** pestañas, no una:
`COTIZACION (Financ)` había heredado el mismo `=+J74*0.13`. Lo que sigue
es el hallazgo tal como se levantó. `COTIZACIÓN !J75` es
`=+J74*0.13`. La ficha `Datos del proyecto` **sí** tiene el campo
`% impuesto al cliente` (B16) y `Cliente exento` (B15) — y la cotización
los ignora. Se pregunta el régimen fiscal y después se tira. Contradice
R3 de frente. Impacto medido en esta corrida: **$793,02 sobre un
subtotal de $6.100,18**. Un cliente exento paga impuesto y Excel no
muestra ningún error. *Es el hallazgo más grave de la corrida.*

**H-2 · El monto que pide el Excel de control no es el que manda el
skill.** ✅ **Corregido el 2026-09-22.** Se resolvió con datos, no con
criterio: cruzando los dos Excels por número de oferta, **19 de 26
ofertas comunes tienen el monto idéntico y ninguna está en relación
1,13**. Los dos archivos guardan el mismo número y el único que dice
cuál es lo llama *sin IVA* → va el **SUBTOTAL** en ambos. Queda
pendiente confirmarlo con preventa (está en
[`pendientes-comercial.md`](pendientes-comercial.md)). El hallazgo
original: La columna J de `Control de cotizaciones 2026.xlsx` se llama
literalmente **`Monto sin IVA`**. `armar-cotizacion` dice *"usar el
TOTAL con impuesto, nunca el subtotal"*. Para este archivo la regla
está al revés: van $6.100,18, no $6.893,19. En `Cotizaciones en
Preventa.xlsx` la columna se llama solo `Monto de Oferta`, así que ahí
la regla del TOTAL probablemente sí aplica — hay que confirmarlo con
preventa, no deducirlo.

**H-3 · Las pestañas de los dos asesores tienen las columnas corridas.**
✅ **Corregido el 2026-09-22** — `armar-cotizacion` ahora trae el layout
real de cada pestaña en una tabla, con la advertencia de que la tabla es
ayuda y no reemplaza leer el encabezado.
`Katherine` arranca en `A:Cliente`; `Alessandro ` arranca en `A:Fecha`,
`B:Cliente`. Escribir la fila de una con el orden de la otra mete el
nombre del cliente en la columna de fecha. El skill dice "leé los
nombres reales" pero no advierte que **el layout también cambia**.

**H-4 · El límite de ruta de Windows aprieta más de lo documentado.**
✅ **Corregido el 2026-09-22** — `armar-cotizacion` ahora calcula y dice
el máximo exacto de caracteres para ese cliente, en vez de pedir "algo
más corto".
Medido sobre los 286 clientes reales: **83 (29%) admiten una descripción
de 20 caracteres o menos**. El cliente de nombre más largo (62
caracteres) admite **1 carácter**; el siguiente (60) admite 2, y el
tercero (57) admite 4. Son nombres legales completos de instituciones
públicas, con la razón social y las siglas.
El skill avisa "pedí una descripción más corta" pero no dice *cuánto* —
tiene que calcular y decir el máximo exacto para ese cliente.

**H-5 · Dos columnas del catálogo están 100% vacías.**
✅ **Atendido el 2026-09-22** — `buscar-equipo` dejó de apuntar a
`Especificaciones técnicas clave` y `actualizar-catalogo` registra que
hay que llenarlas o eliminarlas en el próximo cargue. El dato en sí
sigue sin existir.
`Especificaciones técnicas clave` (0 de 2.550) y `Vigencia del precio`
(0 de 2.550). `buscar-equipo` manda explícitamente a comparar contra la
primera. Hoy toda la búsqueda sale de `Nombre` + `Descripción`.

**H-6 · `buscar-equipo` no conoce la normalización del catálogo.**
✅ **Corregido el 2026-09-22** — el skill trae ahora la tabla completa
de 16 categorías y 64 subcategorías, y el orden de filtrado. Se
escribió antes de que existieran `Categoria` y `Subcategoria`, y no
menciona ni las columnas ni los 16 nombres válidos ni la pestaña
`Glosario de categorias`. Una sesión nueva tiene que descubrirlos sola.

**H-7 · No hay protocolo de acotamiento.**
✅ **Corregido el 2026-09-22** — hasta 10 candidatos se listan; con más,
se cuenta, se agrupa por marca con rango de precio y se pregunta por
dónde acotar. Más los falsos positivos medidos que hay que descartar. Una especificación normal
("exterior, 4MP, IR") deja **68 candidatos**; el skill dice "mostrá
todos los candidatos razonables". Hace falta una regla de corte (por
precio, por marca, o preguntar antes de listar).

**H-8 · El nivel de precio cargado ya se puede nombrar (precisa R4.2).**
De las 945 filas con `Precio especial GV`: **669 son exactamente
MSRP × 0,5**, 202 son **iguales al MSRP** (software, licencias y
accesorios `SECA-`), el resto son 0,5 con redondeo. Filas de ambos tipos
conviven en las mismas páginas del PDF, así que no es un error de carga:
el nivel *Dealer Program* es **MSRP − 50% en hardware y 0% en
software**. La pregunta al equipo comercial deja de ser "cuál de tres
niveles" y pasa a ser **"¿Grupo Visión compra al Dealer Program
(MSRP−50%) o al nivel intermedio DEAL?"**.

**H-9 · Las cuatro pestañas de reglas están vacías** (`Tipo de Cambio`,
`Regimen Fiscal Clientes`, `Tarifario Mano de Obra`, `Reglas de
Descuento`): solo encabezados. La cadena arma la cotización igual, pero
hoy **no puede cerrar una real**: sin tipo de cambio no hay colones, sin
régimen fiscal no hay impuesto correcto, sin tarifario no hay mano de
obra, sin reglas de descuento todo sale a precio de lista.

**H-10 · Las fechas del catálogo son texto, no fechas de Excel.**
✅ **Atendido el 2026-09-22** — `actualizar-catalogo` debe escribirlas
como fecha real de aquí en adelante.
2.357 filas dicen `'2026-08-28'` y 193 `'2026-09-14'` (24 y 7 días, las
dos dentro del umbral). Funciona para calcular, pero Excel no las puede
ordenar ni filtrar como fecha.

**Menor:** `Datos del proyecto!B28` muestra `0,03` donde las demás filas
de porcentaje muestran `3%`.

**H-11 · `Lector / terminal` era un cajón de sastre** (encontrado en la
segunda corrida en seco, 2026-09-22). ✅ **Corregido el mismo día.**

Salió justamente porque el protocolo de acotamiento de H-7 funcionó: con
40 candidatos el skill ya no los lista, los cuenta y los mira — y al
mirarlos, **29 de los 40 no eran lectores.** Eran gabinetes, botones de
salida, cerraduras electromagnéticas, teclados de panel de alarma, una
batería y una fuente de poder.

Lo que lo delataba como error y no como criterio: **las subcategorías
correctas existían y estaban casi vacías.** `Boton de salida` tenía 2
filas mientras había 3 botones en el lugar equivocado;
`Cerradura / electroiman` tenía **1** mientras había 4 cerraduras mal
puestas.

**La causa, en una línea:** `scripts/taxonomia.py` mapeaba la sección del
proveedor (`"control de acceso"`, `"invidtech access control"`) dentro de
`CONFIABLES`, que **corta antes que todas las reglas por nombre**. Las
reglas para cerradura, botón de salida y gabinete **ya existían** —
nunca llegaban a correr. Todo lo que el proveedor pusiera en su sección
de acceso salía como lector, fuera lo que fuera.

**El arreglo:** mover esas dos secciones a `SECCION_FIJA`, que fija la
categoría y deja que el nombre resuelva la subcategoría, más un resolver
`_sub_acceso` y una capa `PRIORITARIAS` para los casos en que una palabra
suelta en medio de la descripción decidía mal:

| Producto | Se iba a | Por qué | Ahora |
|---|---|---|---|
| `iDBox` | Monitor | su texto dice *"monitorea* botones y sensores" | Controladora |
| `iDFace` | Intercomunicador | es terminal facial *con* intercom SIP integrado | Lector / terminal |
| Los kits de acceso | Credencial | su nombre lista los keyfobs que incluyen | Controladora |
| Teclados DSC | Lector | el modelo `HS2LCD` vive en el SKU, no en el nombre | Accesorio de alarma |

**Verificación antes de tocar producción:** se corrió el clasificador
corregido sobre las 2.550 filas. Cambian **exactamente 32, todas del
cajón de sastre, y cero del resto del catálogo** — las reglas nuevas no
secuestraron nada. Al escribir se comprobó el SKU de cada fila antes de
tocarla: 32 escritas, 0 saltadas.

La distribución de `Control de acceso` pasó de `40 / 9 / 4 / 2 / 1` a
**`14 / 9 / 8 / 8 / 8 / 6 / 6`**.

**H-12 (nuevo, mismo día) — los tipos de dato estaban mal en tres
columnas.** ✅ **Corregido.** Lo destapó el verificador nuevo: `Precio
USD` estaba como **texto en 1.409 filas** (todas de un mismo proveedor,
el 55% del catálogo), `Tiempo de entrega` en 1.091, y las fechas en las
2.550. El valor se veía bien, pero Excel no los puede ordenar ni
filtrar: al ordenar por precio, `'1000'` quedaba antes que `'950'`. Ya
son números y fechas reales.

**La `Subcategoria` ya tiene desplegable** (`=_listas!$E$2:$E$72`), y
una trampa que casi me come: la lista que ya existía en `_listas`
columna C trae los nombres **con el prefijo de categoría**
(`Camara > IP / de red`), mientras la columna del catálogo guarda el
nombre pelado. Apuntar ahí habría obligado a escribir un valor que no
coincide con ninguna de las 2.550 filas. Se escribió la lista pelada en
una columna nueva y se verificó: **0 filas con un valor fuera del
desplegable**.

El desplegable evita el error de dedo, no el de par equivocado. Para eso
está el paso 2 de `verificar-catalogo.py`.

**H-14 · Los accesorios de montaje estaban escondidos como cámaras**
(encontrado el 2026-09-23). ✅ **Corregido el mismo día.**

Salió de una pregunta de Fabián: si en las cotizaciones reales usaron
algo para montar las cámaras de una marca que en el catálogo no tenía
ningún accesorio. Se minaron **936 matrices reales** y aparecieron SKU
como `IPM-JB6 Junction Box for Paramont Series Cameras`. Al buscarlos en
el catálogo, estaban — **clasificados como cámaras**:

| SKU | Qué dice su nombre | Dónde estaba |
|---|---|---|
| `IPM-JB6` | Junction Box for Paramont Series Cameras | `Camara / Termica` |
| `IPM-CMFIXDOME` | Ceiling Mount for PAR-ALLDRXIRBD | `Camara / Analogica` |
| `IPM-WALLFIXDOME` | Wall Mount for PAR-ALLDRXIRBD | `Camara / Analogica` |
| `IPM-PTZWALLJBPOLE` | Pole mount bracket for PTZ camera | `Camara / PTZ` |

**78 filas en total**, 58 de una sola marca, y **35 dicen explícitamente
"for \<modelo\>"**. Misma causa que H-11: el PDF del proveedor las traía
bajo un encabezado de sección *CAMERAS* y el clasificador le creyó a la
sección antes de mirar el nombre.

**Corrige una afirmación anterior de este documento.** Se había escrito
que esa marca tenía "224 cámaras y 0 accesorios". Los accesorios
existen; estaban contados como cámaras.

**El arreglo:** una regla que corre **antes que todo**, incluido
`CONFIABLES`, y que mira si el nombre dice que la fila es un montaje.
Con un cuidado explícito: *"PTZ camera **with** wall mount"* es una
cámara que incluye su soporte, no un soporte. Por eso se exige que el
nombre **empiece** con la palabra de accesorio, o que diga
*"\<accesorio\> **for** \<modelo\>"*.

**Verificado antes de tocar producción:** 49 filas cambian sobre 2.550.
42 salen de `Camara`; las otras 7 también eran errores (montajes de
intercomunicador, un acople de cielorraso, brackets de iluminador IR, y
dos "Ceiling Mount" clasificados como monitores). Cero falsos positivos.

⚠️ **Regenerar la pestana de compatibilidad NO agregó pares** — sigue en
793. El generador ya escaneaba todas las filas sin mirar la categoría,
tal como estaba documentado. Lo que la reclasificación sí arregla es que
ahora `buscar-equipo` **los encuentra al filtrar por
`Accesorio de instalacion`**, que antes era imposible.

⚠️ **Y destapó una trampa seria:** `generar_matriz_accesorios.py` guarda
con `openpyxl` y eso **borra los desplegables de Categoría y
Subcategoría sin avisar**. Se comprobó: quedaron en cero. Se agregó
`scripts/reparar-desplegables.ps1` y un aviso en el propio script.

### Limpieza

La carpeta de prueba quedó en pie para poder inspeccionarla. Para
borrarla:

```
git checkout -- sandbox-pruebas/ && git clean -fd sandbox-pruebas/
```

---

## Cómo volver a probar una cotización completa

Hay **dos** scripts, y miran cosas distintas:

| Script | Qué mira | Cuándo correrlo |
|---|---|---|
| `scripts/verificar-catalogo.py` | El **catálogo**: taxonomía, tipos de dato, campos vacíos, duplicados | Después de cada carga de proveedor y de cualquier edición manual |
| `scripts/smoke-machote.ps1` | El machote **aislado**: fórmulas, capacidad, errores, financiamiento, impuesto | Después de cualquier cambio estructural en el machote |
| `scripts/prueba-cotizacion.ps1` | El **flujo entero** como lo vive el asesor: carpeta, copia, escritura, ficha, cotización | Antes de darle el plugin a alguien, y después de tocar `armar-cotizacion` |

```
powershell -File scripts/prueba-cotizacion.ps1
powershell -File scripts/prueba-cotizacion.ps1 -Conservar
```

Sin `-Conservar` borra la carpeta al terminar. Con `-Conservar` la deja
para poder abrir el Excel y mirarlo a ojo.

**Los diez pasos que verifica**, en el mismo orden en que ocurren:

1. **Numeración** — calcula el máximo del año y el máximo global, y
   comprueba que coincidan antes de proponer el número.
2. **Límite de ruta** — mide la ruta real del machote y dice cuántos
   caracteres más aguantaría la descripción.
3. **Carpeta y machote** — que existan las 8 subcarpetas estándar y que
   el machote quede copiado en `Matriz-Oferta/`.
4. **Las guías viajan con la copia** — que `LEEME` sea la primera
   pestaña y que las cuatro guías estén en el archivo que recibe el
   asesor, no solo en el original.
5. **Escritura del equipo** — escribe dos líneas usando **solo las
   cuatro columnas de entrada** y compara cuatro valores calculados
   contra su valor exacto.
6. **Espejo a `COTIZACIÓN `** — que la cantidad y la descripción se
   copien, y que el SUBTOTAL cuadre con `Equipos!P57`.
7. **El impuesto sale de la ficha** — los tres casos: ficha vacía da
   13%, cliente exento da 0, y un 2% escrito como `2` se interpreta como
   2%. También que la cotización financiada respete la exención.
8. **El financiamiento no se asume** — sin ID, la cuota queda vacía y el
   cuadro en cero.
9. **Cero errores de Excel** en todo el libro.
10. **El monto del control** — imprime el SUBTOTAL y el TOTAL por
    separado, aclarando cuál va a los Excels de control.

⚠️ **Nunca toca `CLIENTES/` ni los dos Excels de control.** Todo pasa en
`sandbox-pruebas/`, y el monto del paso 10 solo se imprime.

---

## Caso patrón: primera corrida contra una cotización real (2026-09-23)

La primera vez que se rehizo una cotización real sin mirar el resultado,
y se comparó después. **Acertó una de dos líneas.**

### Cómo se hizo

Se eligió por metadatos una cotización **ganada** de 2026 que tuviera
documento de entrada y matriz. La entrada era un informe de
mantenimiento de un sistema de detección de incendios (documento de un
tercero: se usó como contexto, **nada de su contenido entró al
repositorio**). Sus hallazgos pedían dos cosas: reemplazar **detectores
de gas** y un **detector beam antiguo**.

Se buscó en el catálogo **antes** de abrir la matriz.

### El resultado, línea por línea

| | Lo que el plugin propondría | Lo que se cotizó | Veredicto |
|---|---|---|---|
| **Detector beam** | `OSI-R-SS` Simplex, $503 | `OSI-R-SS`, costo $536 | ✅ **Modelo exacto**, costo con **6,6% de diferencia** |
| **Detector de gas** | `GD-6`, $510,52 | `GD-2A` Macurco, $142 | ❌ **Modelo distinto y 3,6× más caro** |

**Los porcentajes sí habrían coincidido exacto:** transporte 10%,
imprevistos 3%, IVA de línea 0%, DAI 15%, administración 3%, margen
27,4%. Los del machote, sin cambios.

**El impuesto al cliente fue 0%** — y es un cliente **privado**. Sin la
corrección de H-1, la cotización habría salido con 13% y un total
equivocado. Con la ficha preguntando, sale bien. Es la primera evidencia
en un caso real de que ese arreglo importó.

### Los tres huecos que destapó

**1. Falta producto en el catálogo.** El `GD-2A` de Macurco **no existe
en el catálogo**, ni ningún otro Macurco. La única fila que menciona esa
marca es un `GD-6` de otro fabricante, 3,6 veces más caro. El plugin no
puede proponer lo que no tiene cargado.

**2. El precio del catálogo está viejo.** Para el modelo que sí acertó,
el catálogo dice $503 y la cotización real usó $536: **6,6% de
diferencia**. Sobre esa línea son $33, pero el margen se calcula sobre
el costo, así que el error se propaga a todo lo que sigue.

**3. H-13 (nuevo): los detectores de gas están en la categoría
equivocada para este trabajo.** El `GD-6` está en
`Alarma e intrusion / Sensor ambiental`. El protocolo de acotamiento de
H-7 manda filtrar por categoría, así que en un trabajo de detección de
incendios **ni siquiera lo habría encontrado** — la búsqueda dentro de
`Deteccion de incendio` solo devolvió un falso positivo (un detector de
humo). Un detector de gas de un sistema de incendios pertenece a las dos
categorías según el trabajo, y hoy solo está en una.

### Lo que esto dice del plugin

Lo que **funciona**: encontrar el modelo correcto cuando está en el
catálogo, y aplicar los porcentajes bien.

Lo que **no**: el catálogo es el techo de lo que se puede proponer. Dos
de los tres huecos son de datos, no de lógica — producto faltante y
precio viejo. Ninguna mejora de los skills los arregla.

**Un caso no es una medición.** Hay 16 cotizaciones ganadas de 2026 con
matriz y visita técnica disponibles para repetir esto.

### Un límite que también apareció

Se intentó primero con otra cotización ganada, de un proyecto eléctrico.
Su documento de entrada era un **conteo de símbolos sobre planos**: la
columna Descripción está vacía y los ítems viven dentro de dos imágenes
incrustadas. **Para ese tipo de proyecto la entrada no es legible por
máquina** y el plugin no puede partir de ahí; alguien tiene que
interpretar el plano primero. No es un defecto a corregir, es dónde
termina la automatización.

---

## Bitácora de corridas

| Fecha | Prueba | Resultado | Notas |
|---|---|---|---|
| 2026-09-18 | P-01 a P-05 | ✅ Pasa | Valores verificados en Excel; son los que están en este documento |
| 2026-09-18 | P-06 | ✅ Pasa | Antes: 45 `#REF!` y 24 `#¡DIV/0!`/`#¡NUM!`. Ahora: 0 errores |
| 2026-09-18 | P-07 | ✅ Pasa | Ampliado a 50 líneas: `Equipos` 6-55, `COTIZACIÓN ` 22-71, 50 cuadros de financiamiento |
| 2026-09-21 | P-05 | ✅ Pasa | Valores recalculados: el cuadro financia el precio unitario, no el total |
| 2026-09-21 | P-06a | ✅ Pasa | Barrido **en blanco** agregado; destapó y corrigió 6 `#¡DIV/0!` que el barrido con datos escondía |
| 2026-09-21 | P-08 | ✅ Pasa | Pestaña `COTIZACION (Financ)` construida y verificada |
| 2026-09-18 | Integridad | ✅ Pasa | 14 imágenes intactas antes y después de las cuatro cirugías; el libro pasó de 38 a 39 pestañas al agregar `Datos del proyecto` al final |
| 2026-09-21 | **Corrida en seco punta a punta** | ⚠️ Pasa con 10 hallazgos | Primera ejecución real de la cadena. Ver la sección de arriba |
| 2026-09-21 | Cadena mecánica | ✅ Pasa | Catálogo → candidatos → carpeta → `Equipos` → `COTIZACIÓN `, 0 errores en 40 pestañas |
| 2026-09-21 | C-05 financiamiento | ✅ Pasa | Sin ID, `COTIZACION (Financ)` queda vacía y no rompe nada |
| 2026-09-21 | C-07 antigüedad del precio | ⚠️ Parcial | Las fechas existen (24 y 7 días) pero como texto — H-10 |
| 2026-09-21 | C-08 régimen fiscal | ❌ Falla | El 13% está hardcodeado en `J75`; la ficha lo pregunta y la cotización lo ignora — H-1 |
| 2026-09-22 | **H-1 corregido** | ✅ Pasa | `J75` de `COTIZACIÓN ` y de `COTIZACION (Financ)` ahora leen `Datos del proyecto!B15/B16` |
| 2026-09-22 | P-09 (nueva) | ✅ Pasa | 6 escenarios de tasa + la financiada respeta la exención |
| 2026-09-22 | P-01 a P-08 tras el cambio | ✅ Pasa | Sin regresión: P-04 sigue dando 3.740,11 |
| 2026-09-22 | Integridad | ✅ Pasa | 19 objetos gráficos intactos en 5 pestañas tras la cirugía |
| 2026-09-22 | **H-2 corregido** | ✅ Pasa | Va el SUBTOTAL, no el TOTAL. Evidencia: 19/26 ofertas comunes con monto idéntico, 0 en relación 1,13 |
| 2026-09-22 | **H-3 corregido** | ✅ Pasa | Layout real de `Katherine` y `Alessandro ` documentado; están corridas una columna |
| 2026-09-22 | **Limpieza del machote** | ✅ Pasa | 40 → 33 pestañas. Se borraron 10 con datos de un proyecto real y se limpiaron 305 constantes numéricas de otras dos |
| 2026-09-22 | **Pestañas de inducción** | ✅ Pasa | `LEEME` de primera, `Guia de pestanas` y `Guia de formulas` de últimas |
| 2026-09-22 | Integridad tras la limpieza | ✅ Pasa | 19 objetos gráficos intactos, 0 errores, el archivo bajó de 745.448 a 715.093 bytes |
| 2026-09-22 | **H-4, H-6, H-7 corregidos** | ✅ Pasa | Cálculo del máximo de caracteres, taxonomía completa en `buscar-equipo`, y protocolo de acotamiento |
| 2026-09-22 | **H-5, H-10 atendidos** | ⚠️ Parcial | Documentados y con instrucción en `actualizar-catalogo`; el dato en sí sigue faltando |
| 2026-09-22 | H-8, H-9 | ⬜ Bloqueados | Esperan al equipo comercial. H-8 quedó afinado a una sola pregunta |
| 2026-09-22 | Guías del machote | ✅ Pasa | Cuatro pestañas (`LEEME` + 3 guías) con estilo común: sin cuadrícula, bandas de sección, encabezado fijo |
| 2026-09-22 | **Prueba de cotización completa** | ✅ Pasa | Nuevo `scripts/prueba-cotizacion.ps1`: 10 pasos, de la numeración al monto del control. Incluye el caso de cliente exento |
| 2026-09-22 | Confidencialidad | ✅ Corregido | Se quitaron nombres de clientes reales de 2 docs, 1 script y **10 celdas del catálogo de producción** |
| 2026-09-22 | **2.ª corrida en seco** (control de acceso) | ⚠️ Pasa con 1 hallazgo | Encontró H-11. H-4 confirmado en vivo: cliente de 63 caracteres → 1 carácter de descripción |
| 2026-09-22 | **H-11 corregido** | ✅ Pasa | 32 filas reclasificadas, 0 colaterales sobre 2.550. `taxonomia.py` arreglado para que no vuelva |
| 2026-09-22 | **Verificador de catálogo** | ✅ Nuevo | `scripts/verificar-catalogo.py`, 5 chequeos. Destapó H-12 en su primera corrida |
| 2026-09-22 | **H-12 corregido** | ✅ Pasa | 1.409 precios, 1.091 tiempos de entrega y 2.550 fechas pasados de texto a su tipo real |
| 2026-09-22 | Desplegable de Subcategoría | ✅ Pasa | Conectado a `_listas!E`; 0 filas con valor fuera de la lista |
| 2026-09-22 | Catálogo completo | ✅ Sano | El verificador pasa los 5 chequeos sin nada que revisar |
| 2026-09-23 | **Caso patrón #1** | ⚠️ 1 de 2 líneas | Modelo exacto en una, producto faltante del catálogo en la otra. Porcentajes exactos |
| 2026-09-23 | H-1 en un caso real | ✅ Confirmado | Cliente privado con impuesto 0%: sin el arreglo habría salido con 13% |
| 2026-09-23 | **C-01 a C-09** | ✅ 8 de 9 | C-03 se reescribió: la regla cambió bajo sus pies. Ver arriba |
| 2026-09-23 | **H-14 corregido** | ✅ Pasa | 49 filas reclasificadas, 42 salían de `Camara`. Cero falsos positivos sobre 2.550 |
| 2026-09-23 | Desplegables tras el generador | ⚠️ Trampa | `openpyxl` los borra sin avisar. Nuevo `reparar-desplegables.ps1` |
| 2026-09-23 | **Productos cargados** | ✅ 2 de 149 | `PUM9` y `INVID-ISSS-300W`, sacados de cotizaciones reales. Quedan 147 líneas i-PRO sin cargar |
| | C-01 a C-04, C-06, C-09 | ⬜ Sin correr | Requieren conversación con preventa, no script |
| | R-01 a R-10 | ⬜ Bloqueadas | Esperan datos del equipo comercial |
| | Caso patrón | ⬜ Bloqueado | Espera las cotizaciones cerradas |
