# Comparación entre el mapa funcional y el aplicativo actual

## Resumen

La aplicación actual tiene una base reutilizable para productos, proveedores, clientes, compras básicas e inventario. Sin embargo, su estructura todavía no representa el ciclo comercial completo definido en `MAPA_FUNCIONAL.md`.

La mayor diferencia es que el código actual está construido alrededor de la solicitud de compra y todavía no cuenta con documentos de ventas ni facturas de compra.

## Estado actual por área

| Área | Situación actual | Evaluación |
|---|---|---|
| Productos | Productos, unidades, presentaciones y lotes | Reutilizable |
| Proveedores | Datos básicos y relación producto-proveedor | Reutilizable, requiere ampliar indicadores |
| Clientes | Datos básicos | Reutilizable |
| Solicitud de compra | Implementada | Debe pasar a ser opcional |
| Cotización de compra | Implementada | Reutilizable con ajustes |
| Pedido de compra | Implementado | Reutilizable con ajustes |
| Factura de compra | No existe como documento | Falta desarrollar |
| Recepción de compra | Existe | Requiere relación formal con factura y control más claro |
| Cotización de venta | No existe | Falta desarrollar |
| Pedido de venta | No existe | Falta desarrollar |
| Prefactura de venta | No existe | Falta desarrollar |
| Despacho de venta | Existe como movimiento básico | Requiere convertirse en documento operativo |
| Inventario | Movimientos, lotes y cantidades | Base reutilizable, requiere reglas de origen y saldos |
| Auditoría | Existe registro básico | Reutilizable y debe ampliarse a los nuevos documentos |
| Dashboard | Indicadores fijos en cero | Requiere datos reales y pendientes de trabajo |
| Responsive | CSS con adaptación inicial | Requiere revisión de tablas y formularios |

## Diferencias estructurales principales

### 1. Compras

El flujo actual es principalmente:

```text
Solicitud -> Cotización -> Pedido -> Recepción
```

El flujo requerido debe ser:

```text
Cotización opcional -> Pedido opcional -> Factura de compra -> Recepción
```

La solicitud de precios debe conservarse como una herramienta opcional para comparar proveedores, pero no debe obligar a iniciar todas las compras desde allí.

### 2. Ventas

Actualmente no existen modelos ni pantallas para:

- Cotización de cliente.
- Pedido de cliente.
- Prefactura de venta.
- Despacho relacionado con una prefactura.

Esta es la brecha funcional más grande.

### 3. Inventario

Existe una base de movimientos y lotes, pero el inventario todavía debe relacionarse formalmente con:

- Factura de compra.
- Recepción.
- Prefactura de venta.
- Despacho.
- Cantidades originales, procesadas y pendientes.

Un movimiento no debería ser solamente una entrada o salida aislada; debe indicar claramente qué documento lo originó.

### 4. Proveedores

Existe la relación entre productos y proveedores con precio, crédito, tiempo de entrega y proveedor frecuente. Faltan datos calculados e históricos para:

- Porcentaje de cumplimiento.
- Tiempo real promedio de entrega.
- Historial de precios.
- Descuentos históricos.
- Cantidad de compras por producto y proveedor.
- Comparación de proveedores alternativos.

## Reorganización recomendada

La reorganización debería hacerse en este orden:

1. Separar conceptualmente documentos comerciales de movimientos de inventario.
2. Crear las entidades de factura de compra y documentos de venta.
3. Definir relaciones y cantidades pendientes.
4. Convertir recepción y despacho en operaciones vinculadas a documentos.
5. Reorganizar navegación y menús.
6. Ajustar formularios para uso responsive.
7. Construir indicadores reales del dashboard.

## Elementos que no deben desarrollarse todavía

- Facturación electrónica o factura definitiva de venta.
- Cartera completa, si no está definida la integración contable.
- Funciones avanzadas de informes antes de tener documentos y saldos confiables.
- Más opciones en el menú sin que exista su flujo completo.
