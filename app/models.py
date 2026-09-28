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
    unidad_compra_id = db.Column(db.Integer, db.ForeignKey("unidades.id"))
    presentacion = db.Column(db.String(120))
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
