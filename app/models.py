from datetime import datetime

from .extensions import db


class TimestampMixin:
    creado_en = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    actualizado_en = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class EstadoMixin:
    activo = db.Column(db.Boolean, default=True, nullable=False)
    anulado_en = db.Column(db.DateTime)
    motivo_anulacion = db.Column(db.Text)


class Usuario(db.Model, TimestampMixin, EstadoMixin):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(160), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(60), nullable=False, default="operador")


class Proveedor(db.Model, TimestampMixin, EstadoMixin):
    __tablename__ = "proveedores"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(160), nullable=False, index=True)
    nit = db.Column(db.String(40), unique=True)
    contacto = db.Column(db.String(120))
    telefono = db.Column(db.String(60))
    email = db.Column(db.String(160))
    ciudad = db.Column(db.String(100))
    notas = db.Column(db.Text)


class Cliente(db.Model, TimestampMixin, EstadoMixin):
    __tablename__ = "clientes"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(160), nullable=False, index=True)
    documento = db.Column(db.String(40), unique=True)
    contacto = db.Column(db.String(120))
    telefono = db.Column(db.String(60))
    email = db.Column(db.String(160))
    ciudad = db.Column(db.String(100))
    direccion = db.Column(db.String(180))
    notas = db.Column(db.Text)


class Unidad(db.Model, TimestampMixin, EstadoMixin):
    __tablename__ = "unidades"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), unique=True, nullable=False, index=True)
    abreviatura = db.Column(db.String(20), unique=True, nullable=False)


class Producto(db.Model, TimestampMixin, EstadoMixin):
    __tablename__ = "productos"

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(60), unique=True, nullable=False, index=True)
    nombre = db.Column(db.String(180), nullable=False, index=True)
    unidad_id = db.Column(db.Integer, db.ForeignKey("unidades.id"))
    unidad = db.Column(db.String(40), nullable=False, default="unidad")
    maneja_vencimiento = db.Column(db.Boolean, default=False, nullable=False)
    maneja_lotes = db.Column(db.Boolean, default=False, nullable=False)
    maneja_presentaciones = db.Column(db.Boolean, default=False, nullable=False)
    stock_minimo = db.Column(db.Numeric(12, 2), default=0, nullable=False)

    unidad_principal = db.relationship("Unidad")


class ProductoProveedor(db.Model, TimestampMixin, EstadoMixin):
    __tablename__ = "producto_proveedores"

    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey("productos.id"), nullable=False, index=True)
    proveedor_id = db.Column(db.Integer, db.ForeignKey("proveedores.id"), nullable=False, index=True)
    referencia_proveedor = db.Column(db.String(100))
    codigo_proveedor = db.Column(db.String(100), index=True)
    descripcion_proveedor = db.Column(db.String(180))
    marca_proveedor = db.Column(db.String(120))
    unidad_compra_id = db.Column(db.Integer, db.ForeignKey("unidades.id"))
    presentacion = db.Column(db.String(120))
    factor_conversion = db.Column(db.Numeric(14, 4), default=1, nullable=False)
    codigo_barras = db.Column(db.String(80))
    documento_origen = db.Column(db.String(100))
    vigente_desde = db.Column(db.Date)
    precio_compra = db.Column(db.Numeric(14, 2))
    forma_pago = db.Column(db.String(20))
    dias_credito = db.Column(db.Integer, default=0, nullable=False)
    tiempo_entrega_dias = db.Column(db.Integer, default=0, nullable=False)
    es_frecuente = db.Column(db.Boolean, default=False, nullable=False)
    ultima_compra_en = db.Column(db.Date)
    ultimo_precio_compra = db.Column(db.Numeric(14, 2))
    origen = db.Column(db.String(30), default="manual", nullable=False)

    producto = db.relationship("Producto")
    proveedor = db.relationship("Proveedor")
    unidad_compra = db.relationship("Unidad")


class ProductoProveedorHistorial(db.Model, TimestampMixin):
    __tablename__ = "producto_proveedor_historial"

    id = db.Column(db.Integer, primary_key=True)
    producto_proveedor_id = db.Column(
        db.Integer,
        db.ForeignKey("producto_proveedores.id"),
        nullable=False,
        index=True,
    )
    codigo_proveedor = db.Column(db.String(100))
    descripcion_proveedor = db.Column(db.String(180))
    marca_proveedor = db.Column(db.String(120))
    presentacion = db.Column(db.String(120))
    unidad_compra_id = db.Column(db.Integer, db.ForeignKey("unidades.id"))
    factor_conversion = db.Column(db.Numeric(14, 4), default=1, nullable=False)
    codigo_barras = db.Column(db.String(80))
    documento_origen = db.Column(db.String(100))
    vigente_desde = db.Column(db.Date)
    vigente_hasta = db.Column(db.Date)

    producto_proveedor = db.relationship("ProductoProveedor")
    unidad_compra = db.relationship("Unidad")


class CompraSolicitud(db.Model, TimestampMixin, EstadoMixin):
    __tablename__ = "compra_solicitudes"

    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(40), unique=True, nullable=False, index=True)
    fecha = db.Column(db.Date, default=datetime.utcnow, nullable=False, index=True)
    fecha_limite = db.Column(db.Date)
    estado = db.Column(db.String(20), default="BORRADOR", nullable=False, index=True)
    observaciones = db.Column(db.Text)

    detalles = db.relationship(
        "CompraSolicitudDetalle",
        cascade="all, delete-orphan",
        back_populates="solicitud",
        order_by="CompraSolicitudDetalle.id",
    )
    proveedores = db.relationship(
        "CompraSolicitudProveedor",
        cascade="all, delete-orphan",
        back_populates="solicitud",
        order_by="CompraSolicitudProveedor.id",
    )


class CompraSolicitudDetalle(db.Model, TimestampMixin, EstadoMixin):
    __tablename__ = "compra_solicitud_detalles"

    id = db.Column(db.Integer, primary_key=True)
    solicitud_id = db.Column(db.Integer, db.ForeignKey("compra_solicitudes.id"), nullable=False, index=True)
    producto_id = db.Column(db.Integer, db.ForeignKey("productos.id"), nullable=False, index=True)
    presentacion_id = db.Column(db.Integer, db.ForeignKey("producto_presentaciones.id"))
    cantidad_solicitada = db.Column(db.Numeric(14, 4), nullable=False)
    observaciones = db.Column(db.Text)

    solicitud = db.relationship("CompraSolicitud", back_populates="detalles")
    producto = db.relationship("Producto")
    presentacion = db.relationship("ProductoPresentacion")


class CompraSolicitudProveedor(db.Model, TimestampMixin, EstadoMixin):
    __tablename__ = "compra_solicitud_proveedores"

    id = db.Column(db.Integer, primary_key=True)
    solicitud_id = db.Column(db.Integer, db.ForeignKey("compra_solicitudes.id"), nullable=False, index=True)
    proveedor_id = db.Column(db.Integer, db.ForeignKey("proveedores.id"), nullable=False, index=True)
    cotizacion_id = db.Column(db.Integer, db.ForeignKey("compra_cotizaciones.id"))
    estado = db.Column(db.String(20), default="PENDIENTE", nullable=False, index=True)

    solicitud = db.relationship("CompraSolicitud", back_populates="proveedores")
    proveedor = db.relationship("Proveedor")
    cotizacion = db.relationship("CompraCotizacion")


class CompraCotizacion(db.Model, TimestampMixin, EstadoMixin):
    __tablename__ = "compra_cotizaciones"

    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(40), unique=True, nullable=False, index=True)
    solicitud_id = db.Column(db.Integer, db.ForeignKey("compra_solicitudes.id"), index=True)
    proveedor_id = db.Column(db.Integer, db.ForeignKey("proveedores.id"), nullable=False, index=True)
    fecha = db.Column(db.Date, default=datetime.utcnow, nullable=False, index=True)
    vigencia_hasta = db.Column(db.Date)
    estado = db.Column(db.String(20), default="BORRADOR", nullable=False, index=True)
    forma_pago = db.Column(db.String(20))
    dias_credito = db.Column(db.Integer, default=0, nullable=False)
    tiempo_entrega_dias = db.Column(db.Integer, default=0, nullable=False)
    archivo_nombre = db.Column(db.String(255))
    archivo_ruta = db.Column(db.String(255))
    observaciones = db.Column(db.Text)

    solicitud = db.relationship("CompraSolicitud")
    proveedor = db.relationship("Proveedor")
    detalles = db.relationship(
        "CompraCotizacionDetalle",
        cascade="all, delete-orphan",
        back_populates="cotizacion",
        order_by="CompraCotizacionDetalle.id",
    )


class CompraCotizacionDetalle(db.Model, TimestampMixin, EstadoMixin):
    __tablename__ = "compra_cotizacion_detalles"

    id = db.Column(db.Integer, primary_key=True)
    cotizacion_id = db.Column(db.Integer, db.ForeignKey("compra_cotizaciones.id"), nullable=False, index=True)
    producto_id = db.Column(db.Integer, db.ForeignKey("productos.id"), nullable=False, index=True)
    presentacion_id = db.Column(db.Integer, db.ForeignKey("producto_presentaciones.id"))
    cantidad_cotizada = db.Column(db.Numeric(14, 4), nullable=False)
    cantidad_pedida = db.Column(db.Numeric(14, 4), default=0, nullable=False)
    costo_unitario = db.Column(db.Numeric(14, 2))
    referencia_proveedor = db.Column(db.String(100))
    observaciones = db.Column(db.Text)
    estado = db.Column(db.String(20), default="ABIERTA", nullable=False, index=True)

    cotizacion = db.relationship("CompraCotizacion", back_populates="detalles")
    producto = db.relationship("Producto")
    presentacion = db.relationship("ProductoPresentacion")


class CompraPedido(db.Model, TimestampMixin, EstadoMixin):
    __tablename__ = "compra_pedidos"

    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(40), unique=True, nullable=False, index=True)
    cotizacion_id = db.Column(db.Integer, db.ForeignKey("compra_cotizaciones.id"), index=True)
    proveedor_id = db.Column(db.Integer, db.ForeignKey("proveedores.id"), nullable=False, index=True)
    fecha = db.Column(db.Date, default=datetime.utcnow, nullable=False, index=True)
    fecha_estimada = db.Column(db.Date)
    estado = db.Column(db.String(20), default="BORRADOR", nullable=False, index=True)
    observaciones = db.Column(db.Text)

    cotizacion = db.relationship("CompraCotizacion")
    proveedor = db.relationship("Proveedor")
    detalles = db.relationship(
        "CompraPedidoDetalle",
        cascade="all, delete-orphan",
        back_populates="pedido",
        order_by="CompraPedidoDetalle.id",
    )


class CompraPedidoDetalle(db.Model, TimestampMixin, EstadoMixin):
    __tablename__ = "compra_pedido_detalles"

    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey("compra_pedidos.id"), nullable=False, index=True)
    cotizacion_detalle_id = db.Column(db.Integer, db.ForeignKey("compra_cotizacion_detalles.id"))
    producto_id = db.Column(db.Integer, db.ForeignKey("productos.id"), nullable=False, index=True)
    presentacion_id = db.Column(db.Integer, db.ForeignKey("producto_presentaciones.id"))
    cantidad_pedida = db.Column(db.Numeric(14, 4), nullable=False)
    cantidad_recibida = db.Column(db.Numeric(14, 4), default=0, nullable=False)
    costo_unitario = db.Column(db.Numeric(14, 2))
    referencia_proveedor = db.Column(db.String(100))
    observaciones = db.Column(db.Text)
    estado = db.Column(db.String(20), default="ABIERTA", nullable=False, index=True)

    pedido = db.relationship("CompraPedido", back_populates="detalles")
    cotizacion_detalle = db.relationship("CompraCotizacionDetalle")
    producto = db.relationship("Producto")
    presentacion = db.relationship("ProductoPresentacion")


class CompraRecepcion(db.Model, TimestampMixin, EstadoMixin):
    __tablename__ = "compra_recepciones"

    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(40), unique=True, nullable=False, index=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey("compra_pedidos.id"), index=True)
    proveedor_id = db.Column(db.Integer, db.ForeignKey("proveedores.id"), nullable=False, index=True)
    fecha = db.Column(db.Date, default=datetime.utcnow, nullable=False, index=True)
    documento = db.Column(db.String(100))
    responsable = db.Column(db.String(120))
    observaciones = db.Column(db.Text)

    pedido = db.relationship("CompraPedido")
    proveedor = db.relationship("Proveedor")
    detalles = db.relationship(
        "CompraRecepcionDetalle",
        cascade="all, delete-orphan",
        back_populates="recepcion",
        order_by="CompraRecepcionDetalle.id",
    )


class CompraRecepcionDetalle(db.Model, TimestampMixin, EstadoMixin):
    __tablename__ = "compra_recepcion_detalles"

    id = db.Column(db.Integer, primary_key=True)
    recepcion_id = db.Column(db.Integer, db.ForeignKey("compra_recepciones.id"), nullable=False, index=True)
    pedido_detalle_id = db.Column(db.Integer, db.ForeignKey("compra_pedido_detalles.id"))
    producto_id = db.Column(db.Integer, db.ForeignKey("productos.id"), nullable=False, index=True)
    lote_id = db.Column(db.Integer, db.ForeignKey("producto_lotes.id"), nullable=False, index=True)
    presentacion_id = db.Column(db.Integer, db.ForeignKey("producto_presentaciones.id"))
    cantidad = db.Column(db.Numeric(14, 4), nullable=False)
    costo_unitario = db.Column(db.Numeric(14, 2))

    recepcion = db.relationship("CompraRecepcion", back_populates="detalles")
    pedido_detalle = db.relationship("CompraPedidoDetalle")
    producto = db.relationship("Producto")
    lote = db.relationship("ProductoLote")
    presentacion = db.relationship("ProductoPresentacion")


class ProductoPresentacion(db.Model, TimestampMixin, EstadoMixin):
    __tablename__ = "producto_presentaciones"

    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey("productos.id"), nullable=False, index=True)
    nombre = db.Column(db.String(120), nullable=False, index=True)
    unidad_id = db.Column(db.Integer, db.ForeignKey("unidades.id"))
    factor = db.Column(db.Numeric(14, 4), default=1, nullable=False)
    talla = db.Column(db.String(60))
    color = db.Column(db.String(60))
    referencia_interna = db.Column(db.String(80))

    producto = db.relationship("Producto")
    unidad = db.relationship("Unidad")


class ProductoLote(db.Model, TimestampMixin, EstadoMixin):
    __tablename__ = "producto_lotes"

    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey("productos.id"), nullable=False, index=True)
    presentacion_id = db.Column(db.Integer, db.ForeignKey("producto_presentaciones.id"))
    proveedor_id = db.Column(db.Integer, db.ForeignKey("proveedores.id"))
    numero_lote = db.Column(db.String(100), nullable=False, index=True)
    fecha_vencimiento = db.Column(db.Date)
    cantidad_actual = db.Column(db.Numeric(14, 4), default=0, nullable=False)
    observaciones = db.Column(db.Text)

    producto = db.relationship("Producto")
    presentacion = db.relationship("ProductoPresentacion")
    proveedor = db.relationship("Proveedor")


class InventarioMovimiento(db.Model, TimestampMixin, EstadoMixin):
    __tablename__ = "inventario_movimientos"

    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(30), nullable=False, index=True)
    fecha = db.Column(db.Date, default=datetime.utcnow, nullable=False, index=True)
    producto_id = db.Column(db.Integer, db.ForeignKey("productos.id"), nullable=False, index=True)
    lote_id = db.Column(db.Integer, db.ForeignKey("producto_lotes.id"), nullable=False, index=True)
    presentacion_id = db.Column(db.Integer, db.ForeignKey("producto_presentaciones.id"))
    proveedor_id = db.Column(db.Integer, db.ForeignKey("proveedores.id"))
    cliente_id = db.Column(db.Integer, db.ForeignKey("clientes.id"))
    cantidad = db.Column(db.Numeric(14, 4), nullable=False)
    costo_unitario = db.Column(db.Numeric(14, 2))
    documento = db.Column(db.String(100))
    responsable = db.Column(db.String(120))
    observaciones = db.Column(db.Text)

    producto = db.relationship("Producto")
    lote = db.relationship("ProductoLote")
    presentacion = db.relationship("ProductoPresentacion")
    proveedor = db.relationship("Proveedor")
    cliente = db.relationship("Cliente")


class Auditoria(db.Model):
    __tablename__ = "auditoria"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"))
    tabla = db.Column(db.String(80), nullable=False)
    registro_id = db.Column(db.Integer, nullable=False)
    accion = db.Column(db.String(40), nullable=False)
    detalle = db.Column(db.Text)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class CompraFactura(db.Model, TimestampMixin, EstadoMixin):
    __tablename__ = "compra_facturas"

    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(40), unique=True, nullable=False, index=True)
    numero_proveedor = db.Column(db.String(80), index=True)
    proveedor_id = db.Column(db.Integer, db.ForeignKey("proveedores.id"), nullable=False, index=True)
    fecha = db.Column(db.Date, default=datetime.utcnow, nullable=False, index=True)
    fecha_vencimiento = db.Column(db.Date)
    estado = db.Column(db.String(20), default="BORRADOR", nullable=False, index=True)
    subtotal = db.Column(db.Numeric(14, 2), default=0, nullable=False)
    descuentos = db.Column(db.Numeric(14, 2), default=0, nullable=False)
    impuestos = db.Column(db.Numeric(14, 2), default=0, nullable=False)
    total = db.Column(db.Numeric(14, 2), default=0, nullable=False)
    observaciones = db.Column(db.Text)

    proveedor = db.relationship("Proveedor")
    detalles = db.relationship(
        "CompraFacturaDetalle",
        cascade="all, delete-orphan",
        back_populates="factura",
        order_by="CompraFacturaDetalle.id",
    )
    pedidos = db.relationship(
        "CompraFacturaPedido",
        cascade="all, delete-orphan",
        back_populates="factura",
    )


class CompraFacturaDetalle(db.Model, TimestampMixin, EstadoMixin):
    __tablename__ = "compra_factura_detalles"

    id = db.Column(db.Integer, primary_key=True)
    factura_id = db.Column(db.Integer, db.ForeignKey("compra_facturas.id"), nullable=False, index=True)
    producto_id = db.Column(db.Integer, db.ForeignKey("productos.id"), nullable=False, index=True)
    presentacion_id = db.Column(db.Integer, db.ForeignKey("producto_presentaciones.id"))
    cantidad_facturada = db.Column(db.Numeric(14, 4), nullable=False)
    cantidad_recibida = db.Column(db.Numeric(14, 4), default=0, nullable=False)
    costo_unitario = db.Column(db.Numeric(14, 2), nullable=False)
    descuento = db.Column(db.Numeric(14, 2), default=0, nullable=False)
    impuesto = db.Column(db.Numeric(14, 2), default=0, nullable=False)
    referencia_proveedor = db.Column(db.String(100))
    descripcion_proveedor = db.Column(db.String(180))

    factura = db.relationship("CompraFactura", back_populates="detalles")
    producto = db.relationship("Producto")
    presentacion = db.relationship("ProductoPresentacion")


class CompraFacturaPedido(db.Model, TimestampMixin):
    __tablename__ = "compra_factura_pedidos"

    id = db.Column(db.Integer, primary_key=True)
    factura_id = db.Column(db.Integer, db.ForeignKey("compra_facturas.id"), nullable=False, index=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey("compra_pedidos.id"), nullable=False, index=True)
    observaciones = db.Column(db.Text)

    factura = db.relationship("CompraFactura", back_populates="pedidos")
    pedido = db.relationship("CompraPedido")


class VentaCotizacion(db.Model, TimestampMixin, EstadoMixin):
    __tablename__ = "venta_cotizaciones"

    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(40), unique=True, nullable=False, index=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey("clientes.id"), nullable=False, index=True)
    fecha = db.Column(db.Date, default=datetime.utcnow, nullable=False, index=True)
    vigencia_hasta = db.Column(db.Date)
    estado = db.Column(db.String(20), default="BORRADOR", nullable=False, index=True)
    subtotal = db.Column(db.Numeric(14, 2), default=0, nullable=False)
    descuentos = db.Column(db.Numeric(14, 2), default=0, nullable=False)
    impuestos = db.Column(db.Numeric(14, 2), default=0, nullable=False)
    total = db.Column(db.Numeric(14, 2), default=0, nullable=False)
    observaciones = db.Column(db.Text)

    cliente = db.relationship("Cliente")
    detalles = db.relationship(
        "VentaCotizacionDetalle",
        cascade="all, delete-orphan",
        back_populates="cotizacion",
        order_by="VentaCotizacionDetalle.id",
    )


class VentaCotizacionDetalle(db.Model, TimestampMixin, EstadoMixin):
    __tablename__ = "venta_cotizacion_detalles"

    id = db.Column(db.Integer, primary_key=True)
    cotizacion_id = db.Column(db.Integer, db.ForeignKey("venta_cotizaciones.id"), nullable=False, index=True)
    producto_id = db.Column(db.Integer, db.ForeignKey("productos.id"), nullable=False, index=True)
    presentacion_id = db.Column(db.Integer, db.ForeignKey("producto_presentaciones.id"))
    cantidad_cotizada = db.Column(db.Numeric(14, 4), nullable=False)
    precio_unitario = db.Column(db.Numeric(14, 2), nullable=False)
    descuento = db.Column(db.Numeric(14, 2), default=0, nullable=False)
    impuesto = db.Column(db.Numeric(14, 2), default=0, nullable=False)
    observaciones = db.Column(db.Text)

    cotizacion = db.relationship("VentaCotizacion", back_populates="detalles")
    producto = db.relationship("Producto")
    presentacion = db.relationship("ProductoPresentacion")


class VentaPedido(db.Model, TimestampMixin, EstadoMixin):
    __tablename__ = "venta_pedidos"

    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(40), unique=True, nullable=False, index=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey("clientes.id"), nullable=False, index=True)
    fecha = db.Column(db.Date, default=datetime.utcnow, nullable=False, index=True)
    fecha_entrega = db.Column(db.Date)
    estado = db.Column(db.String(20), default="BORRADOR", nullable=False, index=True)
    observaciones = db.Column(db.Text)

    cliente = db.relationship("Cliente")
    detalles = db.relationship(
        "VentaPedidoDetalle",
        cascade="all, delete-orphan",
        back_populates="pedido",
        order_by="VentaPedidoDetalle.id",
    )
    cotizaciones = db.relationship(
        "VentaPedidoCotizacion",
        cascade="all, delete-orphan",
        back_populates="pedido",
    )


class VentaPedidoDetalle(db.Model, TimestampMixin, EstadoMixin):
    __tablename__ = "venta_pedido_detalles"

    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey("venta_pedidos.id"), nullable=False, index=True)
    producto_id = db.Column(db.Integer, db.ForeignKey("productos.id"), nullable=False, index=True)
    presentacion_id = db.Column(db.Integer, db.ForeignKey("producto_presentaciones.id"))
    cantidad_pedida = db.Column(db.Numeric(14, 4), nullable=False)
    cantidad_prefacturada = db.Column(db.Numeric(14, 4), default=0, nullable=False)
    cantidad_despachada = db.Column(db.Numeric(14, 4), default=0, nullable=False)
    precio_unitario = db.Column(db.Numeric(14, 2), nullable=False)
    observaciones = db.Column(db.Text)

    pedido = db.relationship("VentaPedido", back_populates="detalles")
    producto = db.relationship("Producto")
    presentacion = db.relationship("ProductoPresentacion")


class VentaPedidoCotizacion(db.Model, TimestampMixin):
    __tablename__ = "venta_pedido_cotizaciones"

    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey("venta_pedidos.id"), nullable=False, index=True)
    cotizacion_id = db.Column(db.Integer, db.ForeignKey("venta_cotizaciones.id"), nullable=False, index=True)

    pedido = db.relationship("VentaPedido", back_populates="cotizaciones")
    cotizacion = db.relationship("VentaCotizacion")


class VentaPrefactura(db.Model, TimestampMixin, EstadoMixin):
    __tablename__ = "venta_prefacturas"

    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(40), unique=True, nullable=False, index=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey("clientes.id"), nullable=False, index=True)
    fecha = db.Column(db.Date, default=datetime.utcnow, nullable=False, index=True)
    estado = db.Column(db.String(20), default="BORRADOR", nullable=False, index=True)
    subtotal = db.Column(db.Numeric(14, 2), default=0, nullable=False)
    descuentos = db.Column(db.Numeric(14, 2), default=0, nullable=False)
    impuestos = db.Column(db.Numeric(14, 2), default=0, nullable=False)
    total = db.Column(db.Numeric(14, 2), default=0, nullable=False)
    observaciones = db.Column(db.Text)

    cliente = db.relationship("Cliente")
    detalles = db.relationship(
        "VentaPrefacturaDetalle",
        cascade="all, delete-orphan",
        back_populates="prefactura",
        order_by="VentaPrefacturaDetalle.id",
    )


class VentaPrefacturaDetalle(db.Model, TimestampMixin, EstadoMixin):
    __tablename__ = "venta_prefactura_detalles"

    id = db.Column(db.Integer, primary_key=True)
    prefactura_id = db.Column(db.Integer, db.ForeignKey("venta_prefacturas.id"), nullable=False, index=True)
    producto_id = db.Column(db.Integer, db.ForeignKey("productos.id"), nullable=False, index=True)
    presentacion_id = db.Column(db.Integer, db.ForeignKey("producto_presentaciones.id"))
    cantidad_prefacturada = db.Column(db.Numeric(14, 4), nullable=False)
    cantidad_despachada = db.Column(db.Numeric(14, 4), default=0, nullable=False)
    precio_unitario = db.Column(db.Numeric(14, 2), nullable=False)
    descuento = db.Column(db.Numeric(14, 2), default=0, nullable=False)
    impuesto = db.Column(db.Numeric(14, 2), default=0, nullable=False)
    observaciones = db.Column(db.Text)

    prefactura = db.relationship("VentaPrefactura", back_populates="detalles")
    producto = db.relationship("Producto")
    presentacion = db.relationship("ProductoPresentacion")


class VentaDespacho(db.Model, TimestampMixin, EstadoMixin):
    __tablename__ = "venta_despachos"

    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(40), unique=True, nullable=False, index=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey("clientes.id"), nullable=False, index=True)
    fecha = db.Column(db.Date, default=datetime.utcnow, nullable=False, index=True)
    estado = db.Column(db.String(20), default="BORRADOR", nullable=False, index=True)
    responsable = db.Column(db.String(120))
    observaciones = db.Column(db.Text)

    cliente = db.relationship("Cliente")
    detalles = db.relationship(
        "VentaDespachoDetalle",
        cascade="all, delete-orphan",
        back_populates="despacho",
        order_by="VentaDespachoDetalle.id",
    )


class VentaDespachoDetalle(db.Model, TimestampMixin, EstadoMixin):
    __tablename__ = "venta_despacho_detalles"

    id = db.Column(db.Integer, primary_key=True)
    despacho_id = db.Column(db.Integer, db.ForeignKey("venta_despachos.id"), nullable=False, index=True)
    producto_id = db.Column(db.Integer, db.ForeignKey("productos.id"), nullable=False, index=True)
    lote_id = db.Column(db.Integer, db.ForeignKey("producto_lotes.id"), nullable=False, index=True)
    presentacion_id = db.Column(db.Integer, db.ForeignKey("producto_presentaciones.id"))
    prefactura_detalle_id = db.Column(db.Integer, db.ForeignKey("venta_prefactura_detalles.id"), index=True)
    pedido_detalle_id = db.Column(db.Integer, db.ForeignKey("venta_pedido_detalles.id"), index=True)
    cantidad = db.Column(db.Numeric(14, 4), nullable=False)

    despacho = db.relationship("VentaDespacho", back_populates="detalles")
    producto = db.relationship("Producto")
    lote = db.relationship("ProductoLote")
    presentacion = db.relationship("ProductoPresentacion")
    prefactura_detalle = db.relationship("VentaPrefacturaDetalle")
    pedido_detalle = db.relationship("VentaPedidoDetalle")


class VentaPrefacturaPedido(db.Model, TimestampMixin):
    __tablename__ = "venta_prefactura_pedidos"

    id = db.Column(db.Integer, primary_key=True)
    prefactura_id = db.Column(db.Integer, db.ForeignKey("venta_prefacturas.id"), nullable=False, index=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey("venta_pedidos.id"), nullable=False, index=True)

    prefactura = db.relationship("VentaPrefactura")
    pedido = db.relationship("VentaPedido")


class VentaPrefacturaCotizacion(db.Model, TimestampMixin):
    __tablename__ = "venta_prefactura_cotizaciones"

    id = db.Column(db.Integer, primary_key=True)
    prefactura_id = db.Column(db.Integer, db.ForeignKey("venta_prefacturas.id"), nullable=False, index=True)
    cotizacion_id = db.Column(db.Integer, db.ForeignKey("venta_cotizaciones.id"), nullable=False, index=True)

    prefactura = db.relationship("VentaPrefactura")
    cotizacion = db.relationship("VentaCotizacion")
