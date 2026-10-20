# Pruebas ácidas del aplicativo

Estas pruebas buscan encontrar errores de lógica, cantidades incorrectas, relaciones incompletas, problemas de trazabilidad y fallos de uso en celular o tablet.

## Datos base de prueba

Crear como mínimo:

- Dos clientes.
- Dos proveedores.
- Un producto con presentación y lote.
- Un producto comprado en dos presentaciones diferentes.
- Un producto con vencimiento.
- Un producto con equivalencia de código para cada proveedor.
- Un pedido con varias líneas.
- Una cotización de venta con varias líneas.

## 1. Compras directas

### Caso 1.1: factura directa

1. Crear una factura de compra sin pedido.
2. Registrar dos productos.
3. Recibir parcialmente.
4. Verificar que la factura quede en estado `PARCIAL`.
5. Completar la recepción.
6. Verificar estado `COMPLETA` e inventario correcto.

### Caso 1.2: exceso de recepción

Intentar recibir más unidades que las facturadas.

Resultado esperado: el sistema debe bloquear la operación y no modificar inventario.

### Caso 1.3: factura sin productos

Intentar guardar una factura sin líneas.

Resultado esperado: debe impedirse el guardado.

## 2. Compras cruzadas

### Caso 2.1: varios pedidos en una factura

1. Crear dos pedidos al mismo proveedor.
2. Crear una factura relacionada con ambos.
3. Relacionar líneas de ambos pedidos.
4. Verificar cantidades facturadas y pendientes por cada línea.

### Caso 2.2: varias facturas para un pedido

1. Crear un pedido de 100 unidades.
2. Registrar una factura por 40.
3. Registrar otra factura por 60.

Resultado esperado: el pedido queda completo, sin permitir una tercera factura por unidades adicionales.

## 3. Recepciones

- Recibir antes de completar la factura.
- Recibir después de completar la factura.
- Recibir en tres entregas.
- Intentar recibir una cantidad superior al saldo.
- Registrar lote nuevo.
- Registrar lote existente.
- Registrar vencimiento.
- Verificar movimiento de inventario por cada recepción.

## 4. Anulación y trazabilidad

- Anular una factura sin recepción.
- Intentar anular una factura con recepción.
- Intentar eliminar un pedido con factura relacionada.
- Intentar eliminar un producto con movimientos.
- Verificar usuario, fecha, motivo y documento en auditoría.
- Confirmar que los documentos anulados no desaparezcan de las consultas históricas.

## 5. Ventas

### Caso 5.1: flujo completo

```text
Cotización -> Pedido -> Prefactura -> Despacho -> Inventario
```

Verificar que cada documento conserve su relación con el anterior.

### Caso 5.2: venta directa

Crear prefactura y despacho sin cotización ni pedido.

### Caso 5.3: conversión parcial

1. Cotizar 100 unidades.
2. Crear pedido por 40.
3. Crear prefactura por 25.
4. Despachar 10.

Verificar todos los saldos pendientes.

### Caso 5.4: varios documentos origen

Crear una prefactura relacionada con dos pedidos y varias cotizaciones.

Resultado esperado: las líneas y cantidades deben conservar el origen exacto.

## 6. Despachos

- Despacho total.
- Despacho parcial.
- Varios despachos para una prefactura.
- Despacho de lotes diferentes.
- Intentar despachar más inventario del disponible.
- Intentar despachar más de lo pendiente en la prefactura.
- Verificar salida de inventario.
- Verificar que el saldo del lote se actualice correctamente.

## 7. Devoluciones

- Devolución parcial de un cliente.
- Devolución total de un cliente.
- Devolución a proveedor.
- Devolución superior a lo originalmente entregado.
- Verificar movimiento inverso de inventario.
- Verificar relación con prefactura o factura de compra.

## 8. Ajustes

- Ajuste autorizado de entrada.
- Ajuste autorizado de salida.
- Ajuste sin motivo.
- Ajuste sin responsable autorizado.
- Ajuste superior al inventario disponible.
- Verificar auditoría y movimiento generado.

## 9. Conversiones de unidades

### Caso 9.1: conversión simple

Proveedor: 1 caja = 12 unidades internas.

Registrar 3 cajas.

Resultado esperado: inventario interno aumentado en 36 unidades.

### Caso 9.2: factor inválido

Intentar usar factor cero o negativo.

Resultado esperado: operación bloqueada.

### Caso 9.3: código y presentación del proveedor

Registrar una factura usando el código del proveedor y verificar que se relacione con el producto interno correcto.

## 10. Ayuda y navegación

- Buscar un producto por código interno.
- Buscar por código del proveedor.
- Buscar cliente, proveedor y documento.
- Abrir el resultado desde la ayuda.
- Verificar que no se muestren módulos inexistentes.
- Verificar que toda pantalla tenga barra superior y botón Regresar.

## 11. Pruebas responsive

Repetir las operaciones principales en:

- Computador.
- Tablet vertical.
- Tablet horizontal.
- Celular vertical.
- Celular horizontal.

Verificar que no haya desbordamiento horizontal inesperado, botones inaccesibles ni formularios imposibles de completar.

## 12. Criterio de aprobación

Una prueba se considera aprobada únicamente si:

- Los saldos son correctos.
- El inventario coincide con los movimientos.
- Las relaciones documentales se conservan.
- No se permiten cantidades superiores a las pendientes.
- Las anulaciones mantienen trazabilidad.
- Los errores no dejan registros incompletos.
- La operación se puede ejecutar desde celular o tablet.
