# Diseño de documentos y relaciones

## Principio general

Los documentos comerciales y los movimientos físicos de inventario son conceptos distintos. Un documento puede estar creado, aprobado o pendiente sin que todavía exista una entrada o salida de inventario.

Cada documento debe conservar su origen, estado, cantidades y documentos relacionados.

## Documentos de compra

### Cotización de proveedor

Representa una propuesta de un proveedor para uno o varios productos.

Puede originarse desde una solicitud opcional de precios o registrarse directamente.

Puede convertirse total o parcialmente en uno o varios pedidos.

### Pedido de compra

Representa la decisión de comprar al proveedor.

Puede originarse desde una cotización o registrarse directamente.

Debe controlar por cada línea:

- Cantidad pedida.
- Cantidad facturada.
- Cantidad recibida.
- Cantidad pendiente.

Estados sugeridos: borrador, confirmado, parcial, completo, cancelado.

### Factura de compra

Representa el documento recibido del proveedor.

Puede registrarse directamente o relacionarse con uno o varios pedidos de compra. No genera por sí sola una entrada de inventario si la mercancía aún no ha sido recibida.

Debe controlar por cada línea:

- Producto y presentación.
- Cantidad facturada.
- Costo unitario.
- Descuento e impuestos, si aplican.
- Pedido relacionado.
- Cantidad recibida.

Estados sugeridos: borrador, registrada, parcial, completa, anulada.

### Recepción de compra

Representa la entrada física de mercancía.

Puede relacionarse con un pedido, una factura de compra, ambos o registrarse como recepción directa autorizada.

Una compra puede tener varias recepciones. Cada recepción genera los movimientos de entrada al inventario.

## Documentos de venta

### Cotización de cliente

Representa una propuesta comercial para un cliente.

Puede convertirse total o parcialmente en uno o varios pedidos o prefacturas, según las reglas del negocio.

Estados sugeridos: borrador, enviada, aprobada, rechazada, vencida, convertida, anulada.

### Pedido de cliente

Representa la aprobación o solicitud formal del cliente.

Puede originarse desde una cotización o registrarse directamente.

Debe controlar por línea:

- Cantidad solicitada.
- Cantidad prefacturada.
- Cantidad despachada.
- Cantidad pendiente.

Estados sugeridos: borrador, confirmado, parcial, completo, cancelado.

### Prefactura de venta

Es el documento final que administra este aplicativo antes de la facturación definitiva externa.

Puede originarse desde una cotización, un pedido, ambos o registrarse directamente.

Debe controlar por línea:

- Producto y presentación.
- Cantidad prefacturada.
- Precio de venta.
- Descuento e impuestos, si aplican.
- Cantidad despachada.
- Cantidad pendiente.

Estados sugeridos: borrador, aprobada, parcial, completa, anulada.

La factura definitiva o electrónica no pertenece a este sistema.

### Despacho de venta

Representa la salida física de mercancía hacia el cliente.

Puede relacionarse con una prefactura, un pedido, ambos o registrarse como despacho directo autorizado.

Una prefactura o pedido puede generar varios despachos parciales. Cada despacho genera movimientos de salida del inventario.

## Relaciones principales

```text
Cotización compra 1 --- N Pedido compra
Pedido compra      N --- N Factura compra
Factura compra     1 --- N Recepción
Pedido compra      1 --- N Recepción

Cotización venta   1 --- N Pedido venta
Pedido venta       N --- N Prefactura venta
Cotización venta   N --- N Prefactura venta
Prefactura venta   1 --- N Despacho
Pedido venta       1 --- N Despacho
```

La relación se debe guardar también en las líneas cuando una factura, prefactura o recepción pueda cubrir parcialmente varias fuentes.

## Reglas de cantidades

Para cada línea se debe calcular:

```text
pendiente = cantidad de origen - cantidad procesada
```

No se debe permitir registrar una cantidad superior a la pendiente, salvo que un usuario autorizado registre una excepción.

Cuando todas las líneas estén procesadas, el documento pasa a completo. Si solo algunas están procesadas, pasa a parcial.

## Inventario

Los movimientos deben guardar el tipo y el documento origen:

- Entrada por recepción de compra.
- Salida por despacho de venta.
- Entrada por devolución de cliente.
- Salida por devolución a proveedor.
- Ajuste autorizado.

Anular un documento que ya produjo movimientos debe generar una operación inversa o exigir un proceso de reversión autorizado. No debe eliminarse silenciosamente.
