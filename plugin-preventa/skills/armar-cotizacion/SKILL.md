---
name: armar-cotizacion
description: Genera o actualiza una cotización de sistemas de seguridad/cámaras para un cliente, respetando el formato de la matriz de Excel (~35 pestañas: cámaras, productos, materiales, OPEX/mano de obra, evaluación financiera, hoja de cotización final), la numeración por cliente ("Cotización #N") y el número de oferta real (formato T{prefijo}-{7 dígitos}-{año}), y las reglas de versionado (sufijo v2/v3 para cambios menores dentro de la misma carpeta, copia nueva para cambios grandes). Usar cuando el usuario pide armar, generar, actualizar o versionar una cotización, o pide el número de oferta/cotización siguiente para un cliente.
---

# Armar cotización — PENDIENTE

Este skill todavía no tiene lógica real. Ya se confirmó la estructura de
carpetas y los nombres de pestañas de la matriz real (ver
[`docs/notas-proceso.md`](../../../docs/notas-proceso.md), secciones
"Numeración", "Versionado", "Estructura real de las carpetas
compartidas" y "La matriz de Excel es mucho más compleja..."). Falta
todavía revisar el **contenido interno** (columnas, fórmulas, qué
pestañas se usan siempre vs. cuáles son plantilla sin usar) de al menos
una matriz real antes de poder generar/editar una con confianza.

Nota: la búsqueda automática del accesorio de montaje correcto según
marca de cámara y tipo de instalación (pared/techo) queda **fuera de
alcance** de este skill por ahora — es trabajo futuro explícito, no
inventar una solución parcial acá.

Preguntas abiertas que hay que resolver con datos reales antes de
implementar:

- De las ~35 pestañas de la matriz, ¿cuáles se usan siempre y cuáles son
  plantilla que casi nunca se toca? ¿Cómo sabe el asesor cuáles borrar o
  dejar vacías en una cotización nueva?
- ¿Qué determina el prefijo del número de oferta real (`T1` vs `T4` vs
  `T5`)? No es por cliente — ver "Numeración" en notas-proceso.md.
- ¿"Cotización #N" (numeración de carpeta) lo asigna el asesor a mano
  mirando la última carpeta del cliente, o hay algún otro control?
- ¿Qué determina si un cambio es "menor" (nueva versión, mismo archivo)
  vs "grande" (copia nueva)? ¿Lo decide siempre el asesor a mano, o hay
  alguna regla que se pueda inferir?
- ¿De dónde salen los precios cuando no están en ningún catálogo local
  (se consultan por correo/WhatsApp)? ¿Este skill debe pedirlos al
  usuario en esos casos, o dejar la celda pendiente marcada de alguna
  forma?
- La carpeta de año bajo cada cliente no sigue un nombre fijo (a veces
  `<Cliente> -AAAA`, a veces `Cotizaciones AAAA`, a veces no existe) —
  ¿este skill debe detectar el patrón existente del cliente, o siempre
  hay que preguntar dónde crear la carpeta nueva?

references/ está vacía por ahora — ahí va cualquier catálogo, tabla de
precios o plantilla pesada una vez que exista una versión sanitizada
(sin datos reales de clientes).
