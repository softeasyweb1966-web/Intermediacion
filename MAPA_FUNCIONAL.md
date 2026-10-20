# Mapa funcional del aplicativo

## Alcance

El aplicativo administra el proceso comercial y operativo hasta la prefactura de venta. La facturación definitiva o electrónica queda fuera del alcance.

Debe funcionar correctamente en computador, tablet y celular.

## 1. Compras

### Flujo con cotización

```text
Cotización de proveedor -> Pedido de compra -> Factura de compra -> Recepción -> Inventario
```

### Flujo directo

```text
Factura de compra -> Recepción -> Inventario
```

También se permiten estos casos:

- Cotización de proveedor -> Factura de compra, sin pedido.
- Pedido de compra directo -> Factura de compra.
- Recepción total o varias recepciones parciales.
- Factura de compra relacionada con uno o varios pedidos.
- Factura de compra registrada antes o después de la recepción, según la operación real.

## 2. Ventas

### Flujo completo

```text
Cotización de cliente -> Pedido de cliente -> Prefactura de venta -> Despacho -> Inventario
```

### Flujos alternativos

```text
Cotización de cliente -> Prefactura de venta -> Despacho
Pedido de cliente -> Prefactura de venta -> Despacho
Prefactura de venta -> Despacho
```

También se permiten despachos totales o varias entregas parciales.

La prefactura puede relacionarse con una cotización, un pedido, ambos o ninguno. La factura definitiva no se genera en este aplicativo.

## 3. Inventario

### Entradas

- Recepción de compra.
- Devolución de cliente.
- Ajuste autorizado de entrada.

### Salidas

- Despacho de venta.
- Devolución a proveedor.
- Ajuste autorizado de salida.

Cada documento debe controlar cantidad total, cantidad procesada, cantidad pendiente y estado: pendiente, parcial, completo o anulado.

Los movimientos deben conservar producto, presentación, lote, vencimiento, documento de origen y responsable.

## 4. Productos y proveedores

Cada producto puede tener unidades, presentaciones, lotes y vencimientos. Al consultar un producto se deben poder comparar sus proveedores por:

- Precio actual e histórico.
- Descuento.
- Tiempo de entrega.
- Forma de pago y días de crédito.
- Porcentaje de cumplimiento.
- Disponibilidad y proveedor alternativo.
- Productos que se le compran a cada proveedor.

Además, cada proveedor puede manejar un código, nombre, marca, presentación o unidad diferente para el mismo producto interno. Esa equivalencia debe conservarse y utilizarse en futuras cotizaciones, pedidos y compras, mostrando al proveedor sus propios términos para evitar confusiones.

Esta información debe servir tanto para seleccionar proveedores de compra como para preparar cotizaciones de venta.

## 5. Módulos orientados al trabajo

- Inicio y pendientes.
- Cotizaciones de venta.
- Pedidos de venta.
- Prefacturas de venta.
- Despachos.
- Compras.
- Recepciones.
- Inventario.
- Productos y proveedores.
- Clientes.
- Informes.

La solicitud de precios a varios proveedores será una herramienta opcional dentro de compras, no el inicio obligatorio del proceso.

## 6. Reglas de usabilidad

- Las acciones principales deben poder realizarse desde celular y tablet.
- Las pantallas deben ser compactas; no se deben usar tarjetas excesivamente grandes que obliguen a desplazarse sin necesidad.
- Las tablas extensas deben adaptarse a bloques compactos, desplazamiento horizontal controlado o filas expandibles en pantallas pequeñas.
- Los formularios largos deben dividirse por secciones claras.
- No se usarán campos de ayuda permanentes que ocupen espacio dentro de los formularios.
- La ayuda se ofrecerá de forma dinámica desde el menú principal y podrá llevar al usuario a cualquier módulo, documento, producto, cliente, proveedor u otra opción disponible.
- Cada documento debe mostrar sus documentos relacionados y el siguiente paso sugerido.
- Las cantidades pendientes deben ser visibles antes de registrar una recepción o despacho.
- Las acciones destructivas deben validar relaciones, movimientos y documentos dependientes antes de mostrarse o ejecutarse.
- Si un registro tiene movimientos o información relacionada, no debe eliminarse físicamente: solo debe poder anularse, conservando la trazabilidad.
- La eliminación solo aparecerá cuando el registro no tenga dependencias y la operación sea segura.
- Todas las acciones principales estarán en una barra superior de acciones.
- No se utilizarán botones sueltos dispersos dentro del contenido.
- Toda pantalla debe incluir un botón visible de Regresar.
- No se deben mostrar módulos incompletos como si estuvieran disponibles.

## Ayuda dinámica central

El menú principal debe ofrecer una búsqueda o asistente dinámico que permita localizar y abrir directamente:

- Módulos y opciones.
- Cotizaciones, pedidos, facturas, prefacturas, recepciones y despachos.
- Productos y sus equivalencias por proveedor.
- Clientes y proveedores.
- Inventario, lotes y vencimientos.

La ayuda debe respetar permisos, mostrar resultados claros y llevar al usuario al documento o pantalla correspondiente.
