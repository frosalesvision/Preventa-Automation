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

## Caso patrón #2: una licitación con marca obligatoria (2026-09-24)

Se eligió una categoría distinta a la del caso #1 para no medir siempre
lo mismo. **Resultado: acierto en el comportamiento, fallo en los
números.**

### La entrada

Un pliego de condiciones de 23 páginas. Lo técnico son **dos párrafos en
la página 8**; el resto es legal. Pide:

> **10 unidades** de botón de pánico inalámbrico, **marca y modelo
> obligatorios**, *"se requiere esta marca debido a que debe ser
> compatible con el sistema de alarma de seguridad con el que cuenta la
> oficina"*. IVA 13%.

### Lo que el plugin habría hecho

| | |
|---|---|
| El modelo exacto | **No está en el catálogo** |
| La marca | 1 solo producto, y no es este |
| Botones de pánico de cualquier marca | 1 fila |

**Y la respuesta correcta es no proponer nada.** El pliego **no admite
equivalentes**: pide esa marca por compatibilidad con un sistema
instalado. Ofrecer el único botón que hay en el catálogo, de otra marca,
habría sido peor que decir "no lo tengo".

Esto es lo que el plugin **sí** debe hacer bien: reconocer cuándo la
marca está amarrada y **no sustituir**.

### Lo que no habría acertado: los porcentajes

| | Machote | Lo que usaron |
|---|---|---|
| Transporte | 10% | **3%** |
| Imprevistos | 3% | **0%** |
| IVA de línea | 0% | **13%** |
| DAI | 15% | **1%** |
| Administración | 3% | **0%** |
| Margen | 27,4% | **22%** |

El margen cae dentro del rango de licitación que ya habíamos medido
(20,8–30%, mediana 23%). **El resto no lo habría acertado ninguna regla
que tengamos.**

### Una hipótesis que duró diez minutos

Los dos casos patrón medidos —este y el de unas tarjetas— bajaron
**imprevistos y administración a cero**. Parecía un patrón de licitación.
Se midió contra el censo:

| Tipo | n | Imprevistos en 0 | Administración en 0 |
|---|---|---|---|
| Licitación | 14 | **14%** | **14%** |
| Otro / privado | 346 | 9% | 9% |

**No se sostiene.** 14% contra 9% no es un patrón, y con n=14 menos. Los
dos casos coinciden por ser **compras de commodity sin instalación**, no
por ser licitaciones. Se descarta y no se escribe como regla.

### Lo que esto suma al caso #1

Dos casos, dos lecciones distintas:

- El **catálogo es el techo**: si el producto no está, no hay
  automatización que lo arregle.
- Los **porcentajes del machote son un punto de partida**, no una
  predicción. En trabajos chicos de reventa pura, el equipo los baja
  casi todos, y no hay regla que diga cuándo.

### Un error propio que este caso destapó

Buscando botones de pánico aparecieron **dos filas del mismo producto**:
una que ya existía y otra que yo había cargado el día anterior. La
comparación de duplicados usaba el **SKU exacto**, y un guion bastó para
colar la repetida.

Pasó dos veces, y la segunda es peor: un producto que había cargado
"porque no estaba en el catálogo" **sí estaba**, sin guiones, y a un
precio bastante distinto. Sobre eso se había escrito además que la carga
de ese proveedor podía haber dejado productos afuera — **también era
falso**.

Los dos duplicados se resolvieron dejándole la fila a la que viene de una
**lista de precios del proveedor** (mejor origen y con proveedor), y
pasándole la categoría correcta que sí tenía la mía. De aquí en adelante
el cotejo de duplicados **normaliza el SKU** quitando guiones, espacios y
puntos.

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
| 2026-09-23 | **Productos cargados** | ✅ 21 | De 1.452 tokens a 101 por estabilidad de precio, y de ahí 21 curados a mano. Catálogo: 2.550 → 2.571 |
| 2026-09-24 | **Caso patrón #2** | ⚠️ Mixto | Comportamiento correcto (no sustituir marca amarrada), porcentajes muy lejos |
| 2026-09-24 | Duplicados por SKU | ✅ Corregido | Dos filas repetidas que el cotejo exacto no vio. Ahora se normaliza el SKU |
| 2026-09-24 | **Auditoria de duplicados** | ✅ Corregido | 13 filas de mas borradas (1 mia, 12 ajenas). Ver la seccion de abajo |
| 2026-09-24 | **Precio en colones corrido** | ✅ Corregido | 5.026 celdas mostraban el precio de otro producto. Lo destapo el borrado |
| 2026-09-24 | **Catalogo sin duplicados** | ✅ Sano | 2.569 → 2.524 filas. El verificador pasa los 6 chequeos |
| 2026-09-24 | **Caso patron #3** | ❌ Falla grave | El costo base no es el MSRP sino el precio dealer. Ver abajo |
| 2026-09-24 | **Medicion de la base de costo** | ✅ Concluyente | 1.119 matrices, 57.607 lineas. El MSRP no se usa como costo **ni una vez** |
| 2026-09-24 | **Caso patron #4** | ❌ 0 de 10 lineas | Los porcentajes salen bien; el catalogo no tiene **ninguno** de los equipos |
| 2026-09-24 | Fechas de los productos cargados | ✅ Corregido | Llevan la fecha de la cotización de origen. Tres tienen precio de 2024 |
| | C-01 a C-04, C-06, C-09 | ⬜ Sin correr | Requieren conversación con preventa, no script |
| | R-01 a R-10 | ⬜ Bloqueadas | Esperan datos del equipo comercial |
| | Caso patrón | ⬜ Bloqueado | Espera las cotizaciones cerradas |


## Auditoria de duplicados del catalogo (2026-09-24)

Salio de una pregunta de Fabian: si cargue un producto sin ver que ya estaba
con el SKU escrito de otra forma, cuantas veces mas paso? La respuesta corta
es **una mas**, pero al ir a buscarla aparecio un problema mayor que no viene
de las cargas nuevas.

Este documento no lleva precios ni nombres de proveedor: se sube a git. Los
numeros de fila permiten encontrar cada caso en el catalogo.

### Como se busco

El error original fue comparar el SKU como cadena exacta: un guion de
diferencia basto para colar una fila repetida. El barrido nuevo compara:

- el **SKU normalizado**, sin guiones, puntos ni espacios;
- el **nombre con los espacios colapsados** — doce filas repetidas se
  escondian nada mas detras de un espacio de mas en distinto lugar;
- **dentro de cada proveedor**, no entre todos. El catalogo es *por
  proveedor*: el mismo producto ofrecido por dos proveedores son dos filas
  legitimas, y es justo lo que se quiere poder comparar al cotizar.

Ese ultimo punto importa. La fila que cargue mal decia `NO SE RECONOCE
PROVEEDOR` y la vieja traia el proveedor real, asi que comparando proveedor
contra proveedor **no se habrian cruzado nunca**. El chequeo 5 de
`verificar-catalogo.py` tenia las dos fallas y quedo reescrito.

### Lo que era mio

Tres de las 16 cargas nuevas chocaban con una fila que ya existia:

| Como se colo | Estado |
|---|---|
| un guion de diferencia | corregido el 2026-09-23 |
| guiones de diferencia, y ademas con un precio bastante menor al real | corregido el 2026-09-23 |
| el catalogo lo tenia **sin la letra inicial** del modelo | pendiente de aplicar |

En los tres el criterio fue el que dio Fabian: **queda la fila vieja, la del
precio mas alto**, que ademas viene de lista de precios y no de una
cotizacion. Si la mia traia mejor categoria o mejor grafia del SKU, eso se le
pasa a la que se queda.

Las otras 13 cargas estan limpias. Dos parejas que parecian duplicados
(`WV-S1136` / `WV-S1136A` y `WV-S3131L` / `WV-S3531L`) son modelos de verdad
distintos.

### Lo que no era mio

Todo lo de abajo viene de la lista de precios general y es anterior a las
cargas nuevas.

**12 filas que sobran.** Mismo proveedor, mismo SKU, mismo nombre y el mismo
precio: la misma fila cargada dos veces. Estan todas entre las filas 2.387 y
2.457. Dos productos aparecen **tres veces** cada uno. Borrarlas no pierde
nada.

**Un codigo que no es un SKU.** El mismo codigo de tres letras esta puesto en
tres productos que no tienen nada que ver entre si, con precios de tres
ordenes distintos (filas 2.452, 2.453 y 2.454). Es lo mas peligroso de todo
lo encontrado, porque `buscar-equipo` busca por codigo: quien pida uno puede
llevarse cualquiera de los otros dos. Hay que decidir a mano que codigo lleva
cada uno.

**4 articulos del mismo proveedor a dos precios** (filas 2.387/2.396,
2.388/2.397, 2.414/2.446 y 2.513/2.539). En uno de ellos la diferencia es
casi del doble. O una fila quedo vieja, o son articulos distintos con el
codigo mal puesto.

Los otros 30 de ese grupo **si** son el caso ya conocido y documentado: un
proveedor publica el mismo articulo en dos listas, una con descuento por
stock limitado. Esos no se tocan.

**2 productos los ofrecen dos proveedores** (filas 2.462/2.468 y
2.510/2.541). Eso no es un error: es exactamente para lo que sirve un
catalogo por proveedor.

### Como quedo

Se borraron 13 filas (1 mia y las 12 ajenas) con respaldo previo. El catalogo
paso de 2.569 a 2.556 filas. Los desplegables de Categoria y Subcategoria
siguen conectados y no quedaron celdas en error.

Quedan sin tocar, a proposito, los 34 casos de "mismo proveedor y mismo SKU a
dos precios": 30 son el caso ya conocido y legitimo, y los otros 4 hay que
verlos a mano. Tambien queda por decidir el codigo de tres letras puesto en
tres productos distintos.


## El precio en colones estaba corrido (2026-09-24)

Esto aparecio de rebote, al borrar los duplicados: el borrado dejo 18 celdas
en `#REF!` y al ir a ver por que, se destapo algo mucho mas grande.

**2.534 de 2.569 filas mostraban el precio en colones de OTRO producto.**

### Por que nadie lo noto

Porque no falla. La celda no da error ni queda vacia: muestra un numero
perfectamente creible, con su simbolo de colones y sus dos decimales, que
resulta ser el de otro producto. La unica forma de verlo es comparar la
formula contra la fila en la que esta.

### La causa

Una trampa de `openpyxl`: **al borrar filas no reajusta las formulas**. Una
que decia `G500` en la fila 500 se mueve a la 499 y sigue diciendo `G500`.
Cada borrado corre el desfase una fila mas. Excel por COM si las reajusta
bien; la trampa es solo de `openpyxl`.

El reparto del desfase lo confirma:

| Corrimiento | Celdas |
|---|---|
| correcto | 34 |
| +1 fila | 4.838 |
| +2 filas | 184 |
| +20 filas | 4 |
| `#REF!` | 18 |

`scripts/construir-catalogo-v2.py`, que fue quien escribio estas formulas en
su momento, las escribe **bien**: cada fila mira su propia fila. El dano vino
despues, de borrados hechos con `openpyxl`.

### Lo que NO estaba afectado

**El precio que se cotiza.** La columna de Precio USD (MSRP) tiene cero
formulas: es un dato fijo. Las afectadas eran solo las dos columnas
*derivadas* de colones. Ninguna cotizacion salio mal por esto, porque
`armar-cotizacion` trabaja en dolares y tiene instruccion expresa de no
convertir a colones por su cuenta.

### Como se arreglo

Reescribiendo las dos columnas con Excel por COM para que cada fila mire su
propia fila, que es lo que ya documentaba `construir-catalogo-v2.py`.
Resultado: 0 formulas corridas, 0 `#REF!`, 0 celdas en error.

### Para que no vuelva

`verificar-catalogo.py` tiene un chequeo 6 nuevo que compara cada formula de
colones contra la fila donde esta. Es la clase de error que solo se ve
midiendo, asi que ahora se mide en cada corrida.

**Regla que deja esto:** despues de cualquier borrado de filas con `openpyxl`,
correr el verificador. Ya sabiamos que `openpyxl` borra los desplegables sin
avisar (por eso existe `reparar-desplegables.ps1`); ahora sabemos que tambien
descuadra las formulas.


## Un producto, una fila (2026-09-24)

Cierre de lo que quedaba abierto de la auditoria de duplicados. Regla que
pidio Fabian: **ninguno debe estar duplicado**.

### Por que NO se dejo el monto mas alto

Era la idea inicial, y medirla la desarmo: **en 25 de 30 pares el precio menor
resulto ser el MAS RECIENTE**. No eran dos precios del mismo momento sino un
precio viejo y uno nuevo, cargados de hojas de origen distintas. Dejar el
mayor habria dejado el precio desactualizado en 25 de 30 casos.

Quedo entonces: **gana la fila mas reciente**, y con la fecha empatada, la de
mayor monto.

### Lo que se habria perdido borrando a secas

La fila que se borra no es una copia de la otra. Midiendo las 33 parejas:

| Columna que difiere | En cuantas parejas |
|---|---|
| Descripcion | 30 de 33 |
| Hoja de origen | 28 de 33 |
| Fecha de actualizacion | 27 de 33 |
| Pais de origen | 21 de 33 |
| **Codigo HTS** | 19 de 33 |
| **Codigo ECCN** | 19 de 33 |
| **Tiempo de entrega** | 17 de 33 |

El HTS es el que determina el DAI, asi que borrarlo sin mirar se habria
sentido despues, al cotizar un importado. Por eso la fila que se queda
**hereda todo campo que tenga vacio** y la otra tenga lleno: 90 campos
rescatados en 31 parejas.

### Los tres casos que no eran duplicados

No se podian borrar a ciegas y se resolvieron aparte:

- **Un codigo de tres letras que no era un modelo, sino la MARCA.** Estaba en
  la columna "Modelo / SKU" de tres partes de torniquete sin relacion entre
  si --un software, una placa y un motor-- y la columna Marca estaba vacia en
  las tres. Quien buscara ese codigo se llevaba cualquiera de los tres. Se
  movio a Marca y a cada fila se le puso el modelo que trae su propio nombre,
  anotado como **pendiente de confirmar con el proveedor**, porque se dedujo
  del nombre y no de una lista de modelos.
- **Una pieza cargada dos veces con dos nombres distintos.** Las dos
  descripciones decian lo mismo, con la misma marca, proveedor, archivo de
  origen y fecha. Ademas la fila que sobrevivia tenia la categoria mal
  (decia camara siendo un accesorio) y la que se borraba la tenia bien, asi
  que se le paso antes de borrar.
- **Dos productos que ofrecen dos proveedores distintos.** Esos se dejan: es
  exactamente para lo que sirve un catalogo por proveedor.

### Como quedo

2.569 → **2.524 filas**. El verificador pasa los seis chequeos y dice que el
catalogo esta sano: ninguna fila repetida, ningun precio en colones corrido,
cero celdas en error y los desplegables conectados.

### Una trampa de PowerShell que volvio a aparecer

Al copiar campos de una fila a otra reventaba con `InvalidCastException`:
PowerShell **cachea el tipo del setter de `.Value2` por sitio de llamada**, y
si en la misma linea se le pasa primero un numero y despues un texto, falla.
Se resuelve asignando cada tipo en una linea distinta. Vale la pena saberlo
antes de escribir el proximo script que copie celdas.


## Caso patron #3: un CCTV ganado, y el costo base estaba al reves (2026-09-24)

Se eligio a proposito un caso distinto de los dos anteriores. El #1 y el #2
midieron **seleccion de modelo**; este mide lo que ahi quedo sin probar: la
**cobertura del catalogo y la cadena de precio**.

Es una cotizacion de CCTV de enero 2026, de cuatro lineas de equipo mas una
de instalacion. Se sabe que **se gano** porque la carpeta guarda la orden de
compra del cliente.

### Un detalle del metodo

La carpeta **no tiene la especificacion original del cliente**. `Visita
tecnica` esta vacia y lo unico en la carpeta de entrada es la cotizacion del
proveedor hacia Grupo Vision. Asi que la entrada fueron las fichas tecnicas
guardadas, que son los modelos que se terminaron cotizando. Eso hace que este
caso **no mida seleccion**, y esta bien: mide la parte que nunca se habia
medido.

### El hallazgo: el costo base estaba al reves

El "Costo Unit" de la matriz real **es el precio dealer del proveedor**, no el
MSRP. Comparado contra el catalogo, coincide **al centavo** en dos de los tres
modelos que se pudieron cotejar:

| Modelo | En el catalogo | Lo que uso la matriz |
|---|---|---|
| NVR | dealer | **el dealer, exacto** |
| Camara bullet | dealer | **el dealer, exacto** |
| Switch | dealer | ninguno de los dos: un valor 1,6x el dealer |

El problema es que el catalogo dice, literalmente, que la columna de MSRP es
"**el que se cotiza**" y que la de dealer es "REFERENCIA - **NO** cotizar con
este". Para llenar el "Costo Unit" de la matriz **es exactamente al reves**.

El MSRP de estos productos es el **doble** del dealer. Si `armar-cotizacion`
hubiera llenado el costo con MSRP, la linea de camaras habria salido **un 93%
por encima** de la real, y la cotizacion completa cerca del doble.

Esto no invalida el MSRP: sirve como precio de lista de referencia. Lo que no
puede es entrar en la columna de **costo**, que es donde arranca toda la
cadena de margen.

### Los porcentajes

| Concepto | Machote / default | Este caso |
|---|---|---|
| Transporte | 10% | **10%** ✓ |
| Imprevistos | 3% | **0%** |
| DAI | 15% | **14%** |
| Administracion | 3% | **3%** ✓ |
| Margen GV | 27,4% | **30%** |
| Impuesto al cliente | 13% | **13%** ✓ |

El margen resulto ser el menor de los problemas: con el 27,4% por defecto la
linea de camaras quedaba a **3,3%** de la real. Los imprevistos en cero vuelven
a aparecer, igual que en el caso #2 --van dos de tres casos patron donde el
default de 3% no se uso--. Y el DAI de 14% confirma lo ya medido: cambio a 15%
entre anos, y esta cotizacion es de enero.

### Lo que si funciono

- **Los cuatro modelos estan en el catalogo**, incluido el disco duro.
- El **impuesto al cliente de 13%** coincide.
- La **relacion costo-a-precio de venta** del caso real es 1,84x, la misma que
  ya habia aparecido midiendo las 649 matrices.

### Lo que hay que arreglar

1. **El costo base.** Es el hallazgo de este caso y el mas caro de todos los
   encontrados hasta ahora.
2. **La busqueda por modelo es demasiado estricta.** Dos de los cuatro modelos
   solo aparecieron por coincidencia parcial, porque el SKU real lleva un
   sufijo que el nombre del archivo de la ficha no trae. `buscar-equipo`
   necesita buscar por prefijo, no solo exacto.

### Una hipotesis que se cayo por el camino

Al ver que dos modelos no aparecian por busqueda exacta, la sospecha fue que
el catalogo les habia pegado un digito al final, como un marcador de nota al
pie. **Era falso.** La lista de precios del proveedor trae las dos versiones
--una "Special Order" y otra "Available, No Audio in/out"--: el digito final
es una **variante real del modelo**. Los 240 SKU que encajaban en ese patron
estan bien. Verificar contra la lista original costo dos minutos y evito
"arreglar" 240 filas que no tenian nada roto.


## Con que precio se llena la columna de costo (2026-09-24)

El caso patron #3 dejo la sospecha de que el costo de las matrices sale del
precio dealer y no del MSRP, al reves de lo que decian los encabezados del
catalogo. Pero era **un** caso. Esto lo cuenta sobre todo lo que hay.

Lo mide `scripts/medir-base-de-costo.py`, que solo lee.

### El resultado

| | Lineas | |
|---|---|---|
| Matrices leidas | 1.119 | |
| Lineas de equipo | 57.607 | |
| Sin modelo reconocible en la descripcion | 56.456 | 98% |
| Con modelo, pero el catalogo trae un solo precio | 1.017 | |
| **Comparables** | **134** | |

De esas 134:

| El costo coincide con | Lineas | |
|---|---|---|
| **el precio dealer** | **94** | **70,1%** |
| **el MSRP** | **0** | **0,0%** |
| los dos (valen igual) | 5 | 3,7% |
| ninguno de los dos | 35 | 26,1% |

**Cero.** En 57.607 lineas de equipo no hay una sola donde el costo sea el
MSRP. Y las 35 que no pegan con ninguno tampoco se acercan al MSRP: son
**todas mas baratas**, con una mediana de 0,37x el MSRP y un maximo de 0,93x.
Varias quedan incluso por debajo del dealer, o sea que a veces se negocia mas
abajo del precio de programa.

La conclusion es la mas firme que hemos sacado de los datos: **el MSRP no es
el costo. Nunca lo fue.**

### El limite honesto de esta medicion

Las 134 lineas comparables son **todas del mismo proveedor**, y no por
casualidad: es el unico con precio dealer cargado en el catalogo. De 2.524
productos, solo **945** tienen los dos precios, y los 945 son de ese
proveedor.

Asi que lo demostrado es: para el proveedor del que tenemos las dos columnas,
el costo es el dealer y jamas el MSRP. Para el resto no se puede medir todavia
**porque no tenemos el dato**, no porque los datos digan otra cosa.

### Lo que reconcilia la confusion de preventa

La lista de ese proveedor no tiene dos precios sino **tres**, y asi se llaman
sus columnas: *Dealer Program*, *DEAL* y *MSRP*. El de programa es la mitad
del MSRP, y el intermedio tres cuartos.

En el caso patron, el costo fue el de programa y el precio final al cliente
aterrizo **cerca del MSRP**. Ahi esta el malentendido completo: el MSRP es
donde el numero **termina**, no de donde **arranca**. Cuando preventa dice
"usa el MSRP" estan describiendo bien el destino; se entendio como que va en
la casilla de costo. Puesto ahi, y con la cadena encima, la cotizacion sale
al doble del MSRP.

### Lo que hay que arreglar, en orden

1. **El costo sale del precio dealer cuando lo tenemos.** Los encabezados del
   catalogo dicen hoy lo contrario y hay que corregirlos.
2. **Registrar QUE precio es el que esta cargado.** Para 1.579 productos
   tenemos un solo numero y ninguna forma de saber si es de lista o ya
   negociado. Esto importa mas que la pregunta original: para la mayoria del
   catalogo hoy no hay nada que elegir.
3. **El 98% de las lineas no trae el modelo en la descripcion.** Limita
   cualquier cotejo automatico contra el historico, y explica por que solo
   134 de 57.607 lineas fueron comparables.

### Un error de parseo encontrado de paso

Un producto quedo con dealer de $2,50 contra un MSRP tres ordenes mayor: ese
valor es el precio del producto de la fila anterior del PDF. Solo hay 2 filas
con el dealer sospechosamente bajo, asi que la columna esta limpia en
general, pero conviene revisarlas.


## Caso patron #4: los porcentajes aciertan, el catalogo no tiene nada (2026-09-24)

Se busco a proposito el hueco que quedaba en el plan: una cotizacion de **mas
de 30 lineas**. Salio un proyecto de ciudad inteligente --paradas de autobus
con pantallas, camaras, video wall, sensores y mobiliario-- de **68 lineas
reales**, muy lejos de los casos chicos anteriores.

### El resultado: cero cobertura

De los 10 modelos de equipo que se pudieron cotejar, el catalogo tiene
**ninguno**. No es que estuvieran mal clasificados: no estan.

La razon se ve al contar el catalogo por proveedor: **2.329 de 2.524 filas
son de solo dos proveedores** (el 92%). Todo lo demas son restos de entre 3 y
46 filas. La marca de camaras de este proyecto --que el equipo claramente usa
mucho, porque es casi todo el proyecto-- tiene **7 modelos** cargados, y los
7 entraron minados de cotizaciones, sin proveedor reconocido.

**El plugin no habria podido armar ni una linea de este proyecto.** Y no por
un error de logica: por falta de datos.

### Lo que si acerto, y es la primera vez

Los porcentajes coinciden casi exactos con los defaults del machote:

| Concepto | Nuestro default | Este caso |
|---|---|---|
| Transporte | 10% | **10%** ✓ |
| Imprevistos | 3% | **3%** ✓ |
| DAI | 15% | **15%** ✓ |
| Impuesto | 13% | **13%** ✓ |
| Administracion | 3% | **3%** ✓ |
| Margen GV | 27,4% | **27%** |

Despues de que el caso #2 y el #3 se salieran de los defaults, este los
respeta enteros. Va uno de tres en imprevistos, asi que el 3% sigue siendo un
default razonable pero no una regla.

### Tres reglas nuevas que solo se ven en un proyecto grande

**1. El euro se convierte a 1,15.** Dos proveedores europeos cotizaron en
euros y la matriz entro los montos en dolares: 260 € → $299 y 280 € → $322,
las dos veces exactamente a 1,15 (una tercera quedo redondeada hacia arriba).
**No teniamos ninguna regla de euros**: toda la cadena asume USD → CRC.

**2. La columna IMPORTADO manda sobre dos porcentajes a la vez.** En las 12
lineas marcadas como nacionales, transporte y DAI quedan en **cero**, pero
imprevistos e impuesto se siguen aplicando. Estaba escrito como regla; aca se
confirma mecanicamente sobre lineas reales.

**3. Los costos recurrentes se aplanan.** Las cuotas mensuales --nube,
monitorizacion, mantenimiento por parada y por bus-- entran como una linea
con cantidad 1 al valor del mes. La matriz no tiene ninguna nocion de costo
recurrente, asi que el que cotiza lo resuelve a mano. Para un proyecto con
servicio mensual eso deja el total incompleto por construccion.

### Una rareza que conviene mirar

El proveedor cotizo el **flete aereo** como un articulo mas. Esa linea entra a
la matriz como cualquier equipo, y recibe encima el **10% de transporte**. O
sea, se le cobra transporte al transporte. Puede ser deliberado, pero vale la
pena preguntarlo.

### Y algo que aparece en todas las matrices

Al contar las lineas de siete cotizaciones distintas, **las siete traian
exactamente 32 lineas de plantilla**: las pestanas de ejemplo del machote
viejo (`Camara Antivandalica`, `BodyCam`, `Face Pro`, `LPR Patrullas`) con los
datos de **otro proyecto real** todavia adentro. Cada copia que hace el equipo
arrastra numeros que no son suyos.

Es el mismo antipatron que se limpio del machote el 2026-09-22 borrando 10
pestanas. Lo que se corrigio fue el machote nuevo; **las cotizaciones ya
hechas siguen cargando esos datos**.

### Lo que este caso cambia en las prioridades

Con el caso #3 corregido, la cadena de precio ya calcula bien. Este caso dice
que eso no alcanza: **el limite ahora es la cobertura del catalogo**, no la
logica. Ampliar el catalogo mas alla de los dos proveedores pesa hoy mas que
cualquier ajuste de formula.
