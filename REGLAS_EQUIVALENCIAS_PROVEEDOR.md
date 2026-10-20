# Reglas para equivalencias de productos por proveedor

## Objetivo

Un mismo producto interno puede tener códigos, nombres, marcas, empaques y unidades diferentes según el proveedor. El aplicativo debe conservar esas diferencias y usarlas para evitar errores de comunicación y compra.

## Ejemplo

Producto interno:

```text
Producto: Guante de nitrilo talla M
Unidad interna: caja
```

Proveedor A:

```text
Código: GN-M-100
Descripción: Guante nitrilo azul M x 100
Unidad: caja x 100
```

Proveedor B:

```text
Código: NIT-M-AZ
Descripción: Guante azul nitrilo mediano
Unidad: paquete x 50
```

Ambos deben relacionarse con el mismo producto interno, pero conservar su información comercial independiente.

## Cuándo se crea o actualiza

La equivalencia puede crearse o confirmarse cuando:

- Se registra una cotización de proveedor.
- Se registra un pedido de compra.
- Se registra una factura de compra.
- Se recibe un documento de despacho del proveedor.
- El usuario relaciona manualmente un código desconocido con un producto interno.

Si el código ya existe para ese proveedor, se reutiliza la equivalencia. Si cambian la descripción, presentación o unidad, se conserva el historial y se crea una nueva versión o registro vigente.

## Búsqueda y validación

Al seleccionar un proveedor, el usuario debe poder buscar un producto por:

- Código interno.
- Código del proveedor.
- Nombre interno.
- Descripción del proveedor.
- Marca o referencia.

El sistema debe mostrar claramente ambas identidades:

```text
Producto interno: GUANTE-NIT-M
Proveedor: GN-M-100 - Guante nitrilo azul M x 100
```

No se debe asignar automáticamente un código desconocido únicamente por similitud de texto. La primera relación debe ser confirmada por el usuario.

## Uso en documentos

### Cotización al proveedor

Debe mostrar el código y descripción que el proveedor reconoce.

### Pedido al proveedor

Debe conservar los términos del proveedor y también el producto interno para inventario.

### Factura y recepción

Debe permitir capturar el código que aparece en el documento del proveedor y relacionarlo con la equivalencia existente.

### Cotización al cliente

Debe mostrar normalmente la descripción comercial propia de la empresa, pero conservar internamente qué proveedor y qué referencia se utilizarían para atenderla.

## Reglas de seguridad

- No se debe permitir que dos productos internos activos usen la misma combinación proveedor + código, salvo autorización.
- Una equivalencia usada en documentos históricos no debe eliminarse físicamente.
- Si cambia el factor de conversión, debe aplicarse a documentos nuevos y conservar el factor anterior en documentos históricos.
- La cantidad del proveedor y la cantidad interna deben ser visibles cuando las unidades sean diferentes.
- Antes de confirmar un pedido o recepción debe advertirse si existe una conversión de unidades.

## Trazabilidad y eliminación

Una equivalencia relacionada con cotizaciones, pedidos, facturas, recepciones o movimientos no debe eliminarse físicamente. Debe marcarse como inactiva o anularse, conservando los datos que fueron usados en documentos históricos.

## Información mínima recomendada

La ficha vigente de equivalencia debe incluir:

- Proveedor.
- Producto interno.
- Código del proveedor.
- Nombre del proveedor.
- Marca o referencia.
- Presentación del proveedor.
- Unidad del proveedor.
- Factor hacia la unidad interna.
- Precio y fecha del último precio.
- Documento de origen.
- Fecha de vigencia.
- Activa o inactiva.
