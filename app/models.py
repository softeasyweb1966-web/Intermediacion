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


class Producto(db.Model, TimestampMixin, EstadoMixin):
    __tablename__ = "productos"

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(60), unique=True, nullable=False, index=True)
    nombre = db.Column(db.String(180), nullable=False, index=True)
    unidad = db.Column(db.String(40), nullable=False, default="unidad")
    maneja_vencimiento = db.Column(db.Boolean, default=False, nullable=False)
    maneja_lotes = db.Column(db.Boolean, default=False, nullable=False)
    maneja_presentaciones = db.Column(db.Boolean, default=False, nullable=False)
    stock_minimo = db.Column(db.Numeric(12, 2), default=0, nullable=False)


class Auditoria(db.Model):
    __tablename__ = "auditoria"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"))
    tabla = db.Column(db.String(80), nullable=False)
    registro_id = db.Column(db.Integer, nullable=False)
    accion = db.Column(db.String(40), nullable=False)
    detalle = db.Column(db.Text)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
