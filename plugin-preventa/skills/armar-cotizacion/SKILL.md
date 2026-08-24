---
name: armar-cotizacion
description: Organiza los archivos y carpetas de una cotización de preventa dentro de la carpeta compartida del cliente (crear la carpeta "Cotización #N-AAAA <descripción>" con sus subcarpetas estándar, ubicar los archivos en la subcarpeta correcta, manejar numeración de carpeta y versionado de nombres de archivo). NO calcula precios ni toca el contenido de la matriz de costos — eso lo hace el asesor con sus propias fórmulas. Usar cuando el usuario pide crear/organizar la carpeta de una cotización nueva, agregar una versión a una cotización existente, o pide el siguiente número de "Cotización #N" para un cliente.
---

# Armar cotización — PENDIENTE

**Alcance corregido (importante):** este skill es sobre **organización de
archivos y carpetas** en `CLIENTES/<Cliente>/.../Cotización #N-AAAA
<descripción>/`, no sobre el contenido de la cotización en sí. **Nunca
abre, lee celdas, ni calcula nada dentro del Excel de la matriz de
costos** (`Matriz-Oferta/*.xlsx`) — esa matriz contiene costos de
proveedor y fórmulas de margen internas, es información sensible que
maneja el asesor con su propio criterio. Este skill como mucho **mueve o
nombra** el archivo, nunca lee ni escribe sus celdas.

Ver [`docs/notas-proceso.md`](../../../docs/notas-proceso.md) para la
estructura real de carpetas confirmada ("Estructura real de las carpetas
compartidas") y las reglas de numeración/versionado.

Nota: la búsqueda automática del accesorio de montaje correcto según
marca de cámara y tipo de instalación (pared/techo) queda **fuera de
alcance** de este skill por ahora — es trabajo futuro explícito, no
inventar una solución parcial acá.

Preguntas abiertas que hay que resolver con el usuario antes de
implementar (nada de esto requiere abrir el contenido de ningún Excel
de costos):

- ¿"Cotización #N" (numeración de carpeta) lo asigna el asesor a mano
  mirando la última carpeta del cliente? ¿Este skill debe proponer el
  siguiente número automáticamente listando las carpetas existentes?
- ¿Qué determina si un cambio es "menor" (nueva versión de archivo,
  misma carpeta) vs "grande" (copia nueva)? ¿Lo decide siempre el
  asesor a mano, o hay alguna señal que se pueda preguntar?
- La carpeta de año bajo cada cliente no sigue un nombre fijo (a veces
  `<Cliente> -AAAA`, a veces `Cotizaciones AAAA`, a veces no existe) —
  ¿este skill debe detectar el patrón existente del cliente, o siempre
  hay que preguntar dónde crear la carpeta nueva?
- ¿Qué archivos necesita crear/mover el skill exactamente en cada
  subcarpeta (`Cotizaciones/`, `Fichas Técnicas/`, `Matriz-Oferta/`,
  `Visita técnica/`) al iniciar una cotización nueva? ¿Alguna plantilla
  vacía que copiar, o el asesor las va llenando manualmente después?
- El número de oferta real (`T{prefijo}-...`) que termina en el nombre
  del PDF final — ¿quién/cómo lo asigna? ¿Es un dato que este skill solo
  usa para **nombrar** el archivo final una vez que el asesor lo tiene,
  o necesita generarlo también?

references/ está vacía por ahora — ahí va cualquier catálogo, tabla de
precios o plantilla pesada una vez que exista una versión sanitizada
(sin datos reales de clientes).
