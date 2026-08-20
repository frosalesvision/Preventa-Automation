---
name: armar-cotizacion
description: Genera o actualiza una cotización de sistemas de seguridad/cámaras para un cliente, respetando el formato de la matriz de Excel (cámaras, productos, materiales, OPEX/mano de obra, hoja final), la numeración consecutiva por cliente (formato T0010) y las reglas de versionado (v1/v2/v3 para cambios menores, copia nueva para cambios grandes). Usar cuando el usuario pide armar, generar, actualizar o versionar una cotización, o pide el número de oferta siguiente para un cliente.
---

# Armar cotización — PENDIENTE

Este skill todavía no tiene lógica real. Antes de escribirla hace falta
ver la estructura exacta de:

1. El Excel maestro compartido (columnas reales, tipos de dato, cómo se
   calcula/busca el siguiente consecutivo `T00XX` por cliente).
2. Al menos una matriz de cotización real ya completada (pestañas de
   cámaras, productos, materiales, OPEX/mano de obra, hoja final que se
   exporta a PDF) — nombres exactos de columnas, fórmulas, formato.

Ver [`docs/notas-proceso.md`](../../../docs/notas-proceso.md) para el
resumen del proceso de negocio y qué copiar a `recursos-originales/`
antes de continuar.

Nota: la búsqueda automática del accesorio de montaje correcto según
marca de cámara y tipo de instalación (pared/techo) queda **fuera de
alcance** de este skill por ahora — es trabajo futuro explícito, no
inventar una solución parcial acá.

Preguntas abiertas que hay que resolver con datos reales antes de
implementar:

- ¿Dónde vive el último consecutivo usado por cliente? ¿En el Excel
  maestro, en el nombre del archivo, en ambos?
- ¿Qué determina si un cambio es "menor" (nueva versión, mismo archivo)
  vs "grande" (copia nueva)? ¿Lo decide siempre el asesor a mano, o hay
  alguna regla que se pueda inferir?
- ¿De dónde salen los precios cuando no están en ningún catálogo local
  (se consultan por correo/WhatsApp)? ¿Este skill debe pedirlos al
  usuario en esos casos, o dejar la celda pendiente marcada de alguna
  forma?
- ¿El archivo de salida final (Excel + PDF) sigue una convención de
  nombre/carpeta específica, o varía?

references/ está vacía por ahora — ahí va cualquier catálogo, tabla de
precios o plantilla pesada una vez que exista una versión sanitizada
(sin datos reales de clientes).
