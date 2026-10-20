# Verificación del flujo comercial

## Compras

- Registrar compra directa.
- Registrar compra desde cotización y pedido.
- Relacionar una factura con varios pedidos.
- Recibir parcialmente.
- Recibir completamente.
- Confirmar cantidades pendientes y estados.
- Intentar recibir más de lo facturado y verificar bloqueo.
- Anular factura sin recepción.
- Intentar anular factura recibida y verificar bloqueo.

## Ventas

- Crear cotización de cliente.
- Crear pedido directo.
- Crear pedido desde una cotización.
- Crear prefactura directa.
- Crear prefactura desde uno o varios pedidos.
- Crear prefactura desde una o varias cotizaciones.
- Generar despacho parcial.
- Completar despacho.
- Verificar salida de inventario.
- Intentar despachar más de lo pendiente y verificar bloqueo.

## Experiencia de usuario

- Verificar barra superior de acciones.
- Verificar botón Regresar.
- Verificar que no existan botones dispersos.
- Probar celular y tablet.
- Probar ayuda dinámica.
- Verificar que eliminar solo aparezca sin dependencias.
- Verificar anulación y auditoría.

## Alcance ampliado de la primera prueba

La prueba no se realizará únicamente hasta el despacho. Debe cubrir también:

- Devolución de mercancía de un cliente.
- Devolución de mercancía a un proveedor.
- Ajuste autorizado de entrada.
- Ajuste autorizado de salida.
- Conversión entre la unidad del proveedor y la unidad interna.
- Verificación de cantidades y saldos después de cada operación.

Flujo completo esperado:

```text
Cotización -> Pedido -> Prefactura -> Despacho -> Salida de inventario
                                      -> Devolución o ajuste
Compra -> Factura -> Recepción -> Entrada de inventario
                   -> Devolución a proveedor o ajuste
```
