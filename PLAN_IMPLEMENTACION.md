# Plan de implementación por etapas

## Etapa 1: base común y equivalencias

- Revisar y normalizar `ProductoProveedor`.
- Agregar código, descripción, marca, presentación, unidad y factor del proveedor.
- Definir historial de cambios.
- Preparar búsquedas por código interno y código del proveedor.
- Mantener funcionando productos, proveedores, unidades, presentaciones y lotes.

## Etapa 2: compras

- Crear factura de compra y sus detalles.
- Permitir factura directa.
- Relacionar facturas con uno o varios pedidos.
- Relacionar recepciones con pedidos y facturas.
- Controlar cantidades facturadas, recibidas y pendientes.
- Mantener la solicitud de precios como opción complementaria.

## Etapa 3: ventas

- Crear cotización de cliente.
- Crear pedido de cliente.
- Crear prefactura de venta.
- Permitir relaciones con una o varias cotizaciones y pedidos.
- Controlar cantidades prefacturadas, despachadas y pendientes.

## Etapa 4: inventario operativo

- Crear documento de despacho.
- Relacionar despachos con prefacturas y pedidos.
- Permitir despachos directos autorizados.
- Registrar entradas y salidas desde documentos.
- Controlar lotes, vencimientos y conversiones de unidades.
- Evitar cantidades superiores a las pendientes.
- Incorporar devoluciones de clientes y proveedores.
- Incorporar ajustes autorizados de entrada y salida.
- Aplicar conversiones entre unidades del proveedor y unidades internas.

## Etapa 5: navegación y experiencia de usuario

- Reorganizar el menú según el flujo de trabajo.
- Ocultar o marcar funciones aún no disponibles.
- Mostrar documentos relacionados y siguiente acción sugerida.
- Simplificar formularios largos por secciones.
- Adaptar tablas a tarjetas o bloques desplazables en celular.
- Mantener botones grandes y accesibles para tablet y celular.

## Etapa 6: indicadores

- Sustituir indicadores fijos del dashboard por consultas reales.
- Mostrar pendientes de recepción y despacho.
- Mostrar cotizaciones abiertas.
- Mostrar inventario crítico.
- Mostrar proveedores y productos con información incompleta.
- Incorporar cumplimiento de proveedores cuando exista suficiente historial.

## Regla de trabajo

Cada etapa debe probarse antes de iniciar la siguiente. No se deben eliminar los modelos actuales hasta comprobar que los nuevos documentos cubren los procesos existentes y los nuevos.

## Diseño de interfaz y trazabilidad

- Las pantallas serán compactas y evitarán tarjetas visualmente grandes.
- No se usarán campos de ayuda permanentes dentro de los formularios.
- Se construirá una ayuda dinámica central desde el menú principal.
- Las acciones se ubicarán en una barra superior única.
- Todas las pantallas tendrán un botón de Regresar.
- Antes de eliminar se validarán movimientos, documentos relacionados y dependencias.
- Si existe cualquier relación que deba conservarse, se permitirá anular o desactivar, pero no eliminar físicamente.
- Toda anulación debe registrar fecha, usuario, motivo y documento afectado.

## Datos actuales

La información cargada actualmente es de prueba y puede eliminarse durante la reorganización. La eliminación o reinicialización se hará de forma controlada, después de definir los modelos y antes de las pruebas finales.
