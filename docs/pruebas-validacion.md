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
estructura que `COTIZACIÓN ` (ver R13). El libro tiene **40 pestañas**.

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

**Criterio de aceptación:** **cero celdas en error en las 40 pestañas**
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

### C-03 · Costo no confirmado

> Armá la cotización con 20 cámaras del modelo X para el cliente Y.

**Esperado:** antes de escribir el costo unitario avisa que el precio
del catálogo es **precio de lista sin descuento** y pide el costo real,
o confirma que se use el de lista. Nunca escribe un costo en silencio.
Si el catálogo trae un precio especial para esa fila, lo muestra y dice
de qué nivel de precio del proveedor salió (R4.2).

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
| Necesario | El monto registrado en los Excel de control es el TOTAL con impuesto, en dólares, con el símbolo correcto visible en pantalla |
| Deseable | Los accesorios propuestos coinciden con los que se usaron de verdad |
| Deseable | El total final difiere menos del 1% del real |

**Regla de despliegue:** el equipo usa el plugin **en paralelo** a su
método actual —no en lugar de él— hasta que dos o tres casos patrón
salgan idénticos. Es más lento por unas semanas y es la única forma de
que confíen en el resultado el día que dejen de revisarlo línea por
línea.

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
| | C-01 a C-09 | ⬜ Sin correr | Se pueden correr ya |
| | R-01 a R-10 | ⬜ Bloqueadas | Esperan datos del equipo comercial |
| | Caso patrón | ⬜ Bloqueado | Espera las cotizaciones cerradas |
