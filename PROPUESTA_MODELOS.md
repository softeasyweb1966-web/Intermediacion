# Propuesta de modelos de datos

## Criterio

Se conservan los modelos actuales que representan datos maestros y se agregan documentos comerciales separados de los movimientos de inventario.

Los cruces parciales o de muchos documentos se manejan mediante tablas de detalle o tablas de relación, no con un único campo de texto.

## Modelos que se conservan

- `Producto`
- `Unidad`
- `ProductoPresentacion`
- `ProductoLote`
- `Proveedor`
- `Cliente`
- `ProductoProveedor`
- `InventarioMovimiento`
- `Auditoria`

Estos modelos requieren ajustes, pero no deben reemplazarse sin necesidad.

## Compras

### `CompraCotizacion`

Se conserva como cotización de proveedor. Puede tener origen en una solicitud opcional.

### `CompraPedido`

Se conserva como pedido de compra. Puede ser directo o provenir de una cotización.

### `CompraFactura`

Nuevo modelo para la factura recibida del proveedor.

Campos principales:

- Número interno.
- Número de factura del proveedor.
- Proveedor.
- Fecha de factura.
- Fecha de vencimiento.
- Estado.
- Subtotal, descuentos, impuestos y total.
- Observaciones.
- Fecha y usuario de registro.

### `CompraFacturaDetalle`

Nuevo modelo para las líneas de la factura.

Campos principales:

- Factura.
- Producto.
- Presentación.
- Cantidad facturada.
- Costo unitario.
- Descuento e impuesto.
- Cantidad recibida.

### `CompraFacturaPedido`

Tabla de relación entre factura de compra y pedido de compra. Permite que una factura cubra varios pedidos y que un pedido se facture en varias facturas.

Debe guardar también la cantidad relacionada por producto o, preferiblemente, relacionar las líneas correspondientes.

### `CompraFacturaPedidoDetalle`

Tabla de relación entre líneas de factura y líneas de pedido. Guarda la cantidad facturada contra cada línea del pedido y permite calcular cantidades pendientes sin depender únicamente del encabezado.

### Recepciones

Se conserva `CompraRecepcion`, pero debe permitir relacionarse con:

- Pedido de compra.
- Factura de compra.
- Ambos.
- Ninguno, únicamente cuando se autorice una recepción directa.

La recepción debe generar los movimientos de entrada de inventario.

## Ventas

### `VentaCotizacion`

Nuevo modelo para cotizaciones de clientes.

Debe guardar cliente, fechas, estado, observaciones, totales y condiciones comerciales.

### `VentaCotizacionDetalle`

Nuevo modelo para productos, presentaciones, cantidades y precios cotizados.

### `VentaPedido`

Nuevo modelo para pedidos de clientes. Puede originarse en una cotización o ser directo.

### `VentaPedidoDetalle`

Nuevo modelo para controlar cantidades solicitadas, prefacturadas, despachadas y pendientes.

### `VentaPrefactura`

Nuevo modelo para el documento final interno del aplicativo antes de la facturación externa.

Puede ser directo o cruzarse con cotización y pedido.

### `VentaPrefacturaDetalle`

Nuevo modelo para controlar productos, precios, descuentos, cantidades y saldos pendientes de despacho.

### Relaciones de ventas

Para permitir cruces parciales y múltiples documentos se usarán relaciones de muchos a muchos:

- `VentaPedidoCotizacion` para relacionar pedidos con una o varias cotizaciones.
- `VentaPrefacturaPedidoDetalle` para relacionar líneas de prefactura con líneas de pedido.
- `VentaPrefacturaCotizacionDetalle` para relacionar líneas de prefactura con líneas de cotización.

Regla aprobada: una prefactura puede relacionarse con uno o varios pedidos y con una o varias cotizaciones. Estas relaciones pueden ser parciales y deben registrarse por línea para controlar cantidades y saldos pendientes.

### `VentaDespacho`

Nuevo modelo para la salida física de mercancía.

Puede relacionarse con prefactura, pedido o ambos. Debe permitir varios despachos para una misma prefactura.

### `VentaDespachoDetalle`

Nuevo modelo para producto, presentación, lote, cantidad despachada y documentos de origen.

Cada detalle genera un movimiento de salida en `InventarioMovimiento`.

## Ajustes a inventario

`InventarioMovimiento` debe incorporar, como mínimo:

- Tipo de movimiento.
- Documento origen.
- Tipo de documento origen.
- Usuario responsable.
- Fecha y hora.
- Producto, presentación y lote.
- Cantidad.
- Costo unitario cuando corresponda.

El documento origen debe ser trazable sin depender únicamente del campo libre `documento`.

## Indicadores de proveedores

La información inicial puede mantenerse en `ProductoProveedor`. Para indicadores históricos se recomienda agregar posteriormente:

- `CompraProveedorEvaluacion`, para registrar cumplimiento, calidad e incidencias.
- Historial de precios derivado de facturas de compra, evitando duplicar datos manualmente.

## Equivalencia de productos por proveedor

La relación `ProductoProveedor` debe funcionar como una ficha de equivalencia entre el producto interno y la forma en que cada proveedor lo identifica.

Debe conservar, como mínimo:

- Código del producto según el proveedor.
- Descripción o nombre usado por el proveedor.
- Marca o referencia comercial.
- Presentación y unidad de compra del proveedor.
- Factor de conversión hacia la unidad interna.
- Código de barras, si existe.
- Último documento donde fue identificado.
- Estado activo o inactivo de la equivalencia.

Cuando se registre una factura, despacho o cotización de proveedor, el usuario debe poder buscar por el código o descripción del proveedor y relacionarlo con el producto interno correspondiente.

En futuras cotizaciones y pedidos al mismo proveedor, el documento debe poder mostrar automáticamente:

- Código del proveedor.
- Descripción del proveedor.
- Presentación negociada.
- Unidad y cantidad en términos del proveedor.
- Equivalencia con el producto interno.

Esto evita confusiones entre nombres, códigos, empaques y unidades diferentes para el mismo producto.

No se debe sobrescribir la información anterior cuando el proveedor cambie un código o presentación. Debe conservarse un historial de equivalencias para mantener la trazabilidad de documentos antiguos.

El porcentaje de cumplimiento debe calcularse con entregas reales contra fechas y cantidades pactadas, no capturarse como un valor fijo.

## Orden recomendado de implementación

1. Factura de compra y sus detalles.
2. Relaciones entre factura, pedido y recepción.
3. Cotización y pedido de venta.
4. Prefactura de venta.
5. Despacho y salida de inventario.
6. Cantidades pendientes y estados automáticos.
7. Indicadores de proveedores.
8. Pantallas responsive y reorganización de navegación.
