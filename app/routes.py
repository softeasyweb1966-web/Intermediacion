from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from sqlalchemy import or_

from .extensions import db
from .models import Auditoria, Cliente, Producto, Proveedor

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def dashboard():
    indicadores = [
        {"titulo": "Cotizaciones abiertas", "valor": "0"},
        {"titulo": "Cuentas por cobrar", "valor": "$0"},
        {"titulo": "Cuentas por pagar", "valor": "$0"},
        {"titulo": "Inventario critico", "valor": "0"},
    ]

    accesos = [
        {"nombre": "Productos", "icono": "box", "clase": "products", "url": "main.productos"},
        {"nombre": "Clientes", "icono": "client", "clase": "clients", "url": "main.clientes"},
        {"nombre": "Proveedores", "icono": "truck", "clase": "suppliers", "url": "main.proveedores"},
        {"nombre": "Cotizaciones", "icono": "quote", "clase": "quotes"},
        {"nombre": "Cartera", "icono": "wallet", "clase": "wallet"},
    ]

    return render_template("dashboard.html", indicadores=indicadores, accesos=accesos)


@main_bp.route("/login")
def login():
    return render_template("login.html")


@main_bp.route("/clientes")
def clientes():
    busqueda = request.args.get("q", "").strip()
    estado = request.args.get("estado", "activos")

    consulta = Cliente.query
    if estado == "anulados":
        consulta = consulta.filter_by(activo=False)
    elif estado != "todos":
        consulta = consulta.filter_by(activo=True)

    if busqueda:
        patron = f"%{busqueda}%"
        consulta = consulta.filter(
            or_(
                Cliente.nombre.ilike(patron),
                Cliente.documento.ilike(patron),
                Cliente.contacto.ilike(patron),
                Cliente.telefono.ilike(patron),
                Cliente.email.ilike(patron),
                Cliente.ciudad.ilike(patron),
            )
        )

    clientes_lista = consulta.order_by(Cliente.nombre.asc()).all()
    return render_template(
        "clientes/index.html",
        clientes=clientes_lista,
        busqueda=busqueda,
        estado=estado,
    )


@main_bp.route("/clientes/nuevo", methods=["GET", "POST"])
def cliente_nuevo():
    cliente = Cliente()
    if request.method == "POST":
        guardar_cliente(cliente)
        db.session.add(cliente)
        db.session.commit()
        registrar_auditoria("clientes", cliente.id, "crear", f"Cliente creado: {cliente.nombre}")
        flash("Cliente creado correctamente.", "success")
        return redirect(url_for("main.clientes"))

    return render_template("clientes/form.html", cliente=cliente, modo="Crear")


@main_bp.route("/clientes/<int:cliente_id>/editar", methods=["GET", "POST"])
def cliente_editar(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)
    if request.method == "POST":
        guardar_cliente(cliente)
        db.session.commit()
        registrar_auditoria("clientes", cliente.id, "editar", f"Cliente editado: {cliente.nombre}")
        flash("Cliente actualizado correctamente.", "success")
        return redirect(url_for("main.clientes"))

    return render_template("clientes/form.html", cliente=cliente, modo="Editar")


@main_bp.route("/clientes/<int:cliente_id>/anular", methods=["POST"])
def cliente_anular(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)
    motivo = request.form.get("motivo_anulacion", "").strip() or "Anulacion desde modulo de clientes"

    cliente.activo = False
    cliente.anulado_en = datetime.utcnow()
    cliente.motivo_anulacion = motivo
    db.session.commit()
    registrar_auditoria("clientes", cliente.id, "anular", motivo)
    flash("Cliente anulado correctamente.", "success")
    return redirect(url_for("main.clientes"))


@main_bp.route("/proveedores")
def proveedores():
    busqueda = request.args.get("q", "").strip()
    estado = request.args.get("estado", "activos")

    consulta = Proveedor.query
    if estado == "anulados":
        consulta = consulta.filter_by(activo=False)
    elif estado != "todos":
        consulta = consulta.filter_by(activo=True)

    if busqueda:
        patron = f"%{busqueda}%"
        consulta = consulta.filter(
            or_(
                Proveedor.nombre.ilike(patron),
                Proveedor.nit.ilike(patron),
                Proveedor.contacto.ilike(patron),
                Proveedor.telefono.ilike(patron),
                Proveedor.email.ilike(patron),
                Proveedor.ciudad.ilike(patron),
            )
        )

    proveedores_lista = consulta.order_by(Proveedor.nombre.asc()).all()
    return render_template(
        "proveedores/index.html",
        proveedores=proveedores_lista,
        busqueda=busqueda,
        estado=estado,
    )


@main_bp.route("/proveedores/nuevo", methods=["GET", "POST"])
def proveedor_nuevo():
    proveedor = Proveedor()
    if request.method == "POST":
        guardar_proveedor(proveedor)
        db.session.add(proveedor)
        db.session.commit()
        registrar_auditoria("proveedores", proveedor.id, "crear", f"Proveedor creado: {proveedor.nombre}")
        flash("Proveedor creado correctamente.", "success")
        return redirect(url_for("main.proveedores"))

    return render_template("proveedores/form.html", proveedor=proveedor, modo="Crear")


@main_bp.route("/proveedores/<int:proveedor_id>/editar", methods=["GET", "POST"])
def proveedor_editar(proveedor_id):
    proveedor = Proveedor.query.get_or_404(proveedor_id)
    if request.method == "POST":
        guardar_proveedor(proveedor)
        db.session.commit()
        registrar_auditoria("proveedores", proveedor.id, "editar", f"Proveedor editado: {proveedor.nombre}")
        flash("Proveedor actualizado correctamente.", "success")
        return redirect(url_for("main.proveedores"))

    return render_template("proveedores/form.html", proveedor=proveedor, modo="Editar")


@main_bp.route("/proveedores/<int:proveedor_id>/anular", methods=["POST"])
def proveedor_anular(proveedor_id):
    proveedor = Proveedor.query.get_or_404(proveedor_id)
    motivo = request.form.get("motivo_anulacion", "").strip() or "Anulacion desde modulo de proveedores"

    proveedor.activo = False
    proveedor.anulado_en = datetime.utcnow()
    proveedor.motivo_anulacion = motivo
    db.session.commit()
    registrar_auditoria("proveedores", proveedor.id, "anular", motivo)
    flash("Proveedor anulado correctamente.", "success")
    return redirect(url_for("main.proveedores"))


@main_bp.route("/productos")
def productos():
    opciones = [
        {"nombre": "Catalogo", "detalle": "Productos base", "icono": "box", "url": "main.productos_catalogo"},
        {"nombre": "Unidades", "detalle": "Medidas y equivalencias", "icono": "ruler"},
        {"nombre": "Presentaciones", "detalle": "Empaques, tallas y colores", "icono": "layers"},
        {"nombre": "Proveedores", "detalle": "Precios y condiciones", "icono": "truck"},
        {"nombre": "Lotes", "detalle": "Vencimientos y trazabilidad", "icono": "calendar"},
        {"nombre": "Inventario", "detalle": "Saldos y movimientos", "icono": "warehouse"},
        {"nombre": "Historial", "detalle": "Ultimas compras", "icono": "history"},
        {"nombre": "Alertas", "detalle": "Minimos y vencimientos", "icono": "alert"},
    ]
    return render_template("productos/modulo.html", opciones=opciones)


@main_bp.route("/productos/catalogo")
def productos_catalogo():
    busqueda = request.args.get("q", "").strip()
    estado = request.args.get("estado", "activos")

    consulta = Producto.query
    if estado == "anulados":
        consulta = consulta.filter_by(activo=False)
    elif estado != "todos":
        consulta = consulta.filter_by(activo=True)

    if busqueda:
        patron = f"%{busqueda}%"
        consulta = consulta.filter(
            or_(
                Producto.codigo.ilike(patron),
                Producto.nombre.ilike(patron),
                Producto.unidad.ilike(patron),
            )
        )

    productos_lista = consulta.order_by(Producto.nombre.asc()).all()
    return render_template(
        "productos/index.html",
        productos=productos_lista,
        busqueda=busqueda,
        estado=estado,
    )


@main_bp.route("/productos/nuevo", methods=["GET", "POST"])
def producto_nuevo():
    producto = Producto()
    if request.method == "POST":
        guardar_producto(producto)
        db.session.add(producto)
        db.session.commit()
        registrar_auditoria("productos", producto.id, "crear", f"Producto creado: {producto.nombre}")
        flash("Producto creado correctamente.", "success")
        return redirect(url_for("main.productos_catalogo"))

    return render_template("productos/form.html", producto=producto, modo="Crear")


@main_bp.route("/productos/<int:producto_id>/editar", methods=["GET", "POST"])
def producto_editar(producto_id):
    producto = Producto.query.get_or_404(producto_id)
    if request.method == "POST":
        guardar_producto(producto)
        db.session.commit()
        registrar_auditoria("productos", producto.id, "editar", f"Producto editado: {producto.nombre}")
        flash("Producto actualizado correctamente.", "success")
        return redirect(url_for("main.productos_catalogo"))

    return render_template("productos/form.html", producto=producto, modo="Editar")


@main_bp.route("/productos/<int:producto_id>/anular", methods=["POST"])
def producto_anular(producto_id):
    producto = Producto.query.get_or_404(producto_id)
    motivo = request.form.get("motivo_anulacion", "").strip() or "Anulacion desde modulo de productos"

    producto.activo = False
    producto.anulado_en = datetime.utcnow()
    producto.motivo_anulacion = motivo
    db.session.commit()
    registrar_auditoria("productos", producto.id, "anular", motivo)
    flash("Producto anulado correctamente.", "success")
    return redirect(url_for("main.productos_catalogo"))


def guardar_cliente(cliente):
    cliente.nombre = request.form.get("nombre", "").strip()
    cliente.documento = request.form.get("documento", "").strip() or None
    cliente.contacto = request.form.get("contacto", "").strip() or None
    cliente.telefono = request.form.get("telefono", "").strip() or None
    cliente.email = request.form.get("email", "").strip() or None
    cliente.ciudad = request.form.get("ciudad", "").strip() or None
    cliente.direccion = request.form.get("direccion", "").strip() or None
    cliente.notas = request.form.get("notas", "").strip() or None


def guardar_proveedor(proveedor):
    proveedor.nombre = request.form.get("nombre", "").strip()
    proveedor.nit = request.form.get("nit", "").strip() or None
    proveedor.contacto = request.form.get("contacto", "").strip() or None
    proveedor.telefono = request.form.get("telefono", "").strip() or None
    proveedor.email = request.form.get("email", "").strip() or None
    proveedor.ciudad = request.form.get("ciudad", "").strip() or None
    proveedor.notas = request.form.get("notas", "").strip() or None


def guardar_producto(producto):
    producto.codigo = request.form.get("codigo", "").strip()
    producto.nombre = request.form.get("nombre", "").strip()
    producto.unidad = request.form.get("unidad", "").strip() or "unidad"
    producto.maneja_vencimiento = request.form.get("maneja_vencimiento") == "on"
    producto.maneja_lotes = request.form.get("maneja_lotes") == "on"
    producto.maneja_presentaciones = request.form.get("maneja_presentaciones") == "on"
    producto.stock_minimo = request.form.get("stock_minimo", "0").strip() or 0


def registrar_auditoria(tabla, registro_id, accion, detalle):
    db.session.add(
        Auditoria(tabla=tabla, registro_id=registro_id, accion=accion, detalle=detalle)
    )
    db.session.commit()
