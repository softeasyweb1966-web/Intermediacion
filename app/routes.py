from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from sqlalchemy import or_

from .extensions import db
from .models import (
    Auditoria,
    Cliente,
    Producto,
    ProductoLote,
    ProductoPresentacion,
    Proveedor,
    Unidad,
)

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
        {"nombre": "Unidades", "detalle": "Medidas y equivalencias", "icono": "ruler", "url": "main.unidades"},
        {"nombre": "Presentaciones", "detalle": "Empaques, tallas y colores", "icono": "layers", "url": "main.presentaciones"},
        {"nombre": "Proveedores", "detalle": "Precios y condiciones", "icono": "truck"},
        {"nombre": "Lotes", "detalle": "Vencimientos y trazabilidad", "icono": "calendar", "url": "main.lotes"},
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
        codigo = request.form.get("codigo", "").strip()
        if Producto.query.filter_by(codigo=codigo).first():
            flash("Ya existe un producto con ese código.", "error")
            return render_template(
                "productos/form.html",
                producto=producto,
                modo="Crear",
                unidades=obtener_unidades(),
            )
        guardar_producto(producto)
        db.session.add(producto)
        db.session.commit()
        registrar_auditoria("productos", producto.id, "crear", f"Producto creado: {producto.nombre}")
        flash("Producto creado correctamente.", "success")
        return redirect(url_for("main.productos_catalogo"))

    return render_template(
        "productos/form.html",
        producto=producto,
        modo="Crear",
        unidades=obtener_unidades(),
    )


@main_bp.route("/productos/<int:producto_id>/editar", methods=["GET", "POST"])
def producto_editar(producto_id):
    producto = Producto.query.get_or_404(producto_id)
    if request.method == "POST":
        codigo = request.form.get("codigo", "").strip()
        existe = Producto.query.filter(
            Producto.codigo == codigo,
            Producto.id != producto.id,
        ).first()
        if existe:
            flash("Ya existe otro producto con ese código.", "error")
            return render_template(
                "productos/form.html",
                producto=producto,
                modo="Editar",
                unidades=obtener_unidades(),
            )
        guardar_producto(producto)
        db.session.commit()
        registrar_auditoria("productos", producto.id, "editar", f"Producto editado: {producto.nombre}")
        flash("Producto actualizado correctamente.", "success")
        return redirect(url_for("main.productos_catalogo"))

    return render_template(
        "productos/form.html",
        producto=producto,
        modo="Editar",
        unidades=obtener_unidades(),
    )


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


@main_bp.route("/productos/unidades")
def unidades():
    busqueda = request.args.get("q", "").strip()
    estado = request.args.get("estado", "activos")

    consulta = Unidad.query
    if estado == "anulados":
        consulta = consulta.filter_by(activo=False)
    elif estado != "todos":
        consulta = consulta.filter_by(activo=True)

    if busqueda:
        patron = f"%{busqueda}%"
        consulta = consulta.filter(
            or_(Unidad.nombre.ilike(patron), Unidad.abreviatura.ilike(patron))
        )

    unidades_lista = consulta.order_by(Unidad.nombre.asc()).all()
    return render_template(
        "productos/unidades/index.html",
        unidades=unidades_lista,
        busqueda=busqueda,
        estado=estado,
    )


@main_bp.route("/productos/unidades/nueva", methods=["GET", "POST"])
def unidad_nueva():
    unidad = Unidad()
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        abreviatura = request.form.get("abreviatura", "").strip()
        if unidad_duplicada(nombre, abreviatura):
            flash("Ya existe una unidad con ese nombre o abreviatura.", "error")
            return render_template("productos/unidades/form.html", unidad=unidad, modo="Crear")
        guardar_unidad(unidad)
        db.session.add(unidad)
        db.session.commit()
        registrar_auditoria("unidades", unidad.id, "crear", f"Unidad creada: {unidad.nombre}")
        flash("Unidad creada correctamente.", "success")
        return redirect(url_for("main.unidades"))

    return render_template("productos/unidades/form.html", unidad=unidad, modo="Crear")


@main_bp.route("/productos/unidades/<int:unidad_id>/editar", methods=["GET", "POST"])
def unidad_editar(unidad_id):
    unidad = Unidad.query.get_or_404(unidad_id)
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        abreviatura = request.form.get("abreviatura", "").strip()
        if unidad_duplicada(nombre, abreviatura, unidad.id):
            flash("Ya existe otra unidad con ese nombre o abreviatura.", "error")
            return render_template("productos/unidades/form.html", unidad=unidad, modo="Editar")
        guardar_unidad(unidad)
        db.session.commit()
        registrar_auditoria("unidades", unidad.id, "editar", f"Unidad editada: {unidad.nombre}")
        flash("Unidad actualizada correctamente.", "success")
        return redirect(url_for("main.unidades"))

    return render_template("productos/unidades/form.html", unidad=unidad, modo="Editar")


@main_bp.route("/productos/unidades/<int:unidad_id>/anular", methods=["POST"])
def unidad_anular(unidad_id):
    unidad = Unidad.query.get_or_404(unidad_id)
    productos_asociados = Producto.query.filter_by(unidad_id=unidad.id, activo=True).count()
    if productos_asociados:
        flash("No se puede anular la unidad porque tiene productos activos asociados.", "error")
        return redirect(url_for("main.unidades"))

    motivo = request.form.get("motivo_anulacion", "").strip() or "Anulacion desde modulo de unidades"

    unidad.activo = False
    unidad.anulado_en = datetime.utcnow()
    unidad.motivo_anulacion = motivo
    db.session.commit()
    registrar_auditoria("unidades", unidad.id, "anular", motivo)
    flash("Unidad anulada correctamente.", "success")
    return redirect(url_for("main.unidades"))


@main_bp.route("/productos/presentaciones")
def presentaciones():
    busqueda = request.args.get("q", "").strip()
    estado = request.args.get("estado", "activos")

    consulta = ProductoPresentacion.query.join(Producto)
    if estado == "anulados":
        consulta = consulta.filter(ProductoPresentacion.activo.is_(False))
    elif estado != "todos":
        consulta = consulta.filter(ProductoPresentacion.activo.is_(True))

    if busqueda:
        patron = f"%{busqueda}%"
        consulta = consulta.filter(
            or_(
                ProductoPresentacion.nombre.ilike(patron),
                ProductoPresentacion.talla.ilike(patron),
                ProductoPresentacion.color.ilike(patron),
                ProductoPresentacion.referencia_interna.ilike(patron),
                Producto.nombre.ilike(patron),
                Producto.codigo.ilike(patron),
            )
        )

    presentaciones_lista = consulta.order_by(Producto.nombre.asc(), ProductoPresentacion.nombre.asc()).all()
    return render_template(
        "productos/presentaciones/index.html",
        presentaciones=presentaciones_lista,
        busqueda=busqueda,
        estado=estado,
    )


@main_bp.route("/productos/presentaciones/nueva", methods=["GET", "POST"])
def presentacion_nueva():
    presentacion = ProductoPresentacion()
    if request.method == "POST":
        guardar_presentacion(presentacion)
        db.session.add(presentacion)
        db.session.commit()
        registrar_auditoria(
            "producto_presentaciones",
            presentacion.id,
            "crear",
            f"Presentacion creada: {presentacion.nombre}",
        )
        flash("Presentación creada correctamente.", "success")
        return redirect(url_for("main.presentaciones"))

    return render_template(
        "productos/presentaciones/form.html",
        presentacion=presentacion,
        productos=obtener_productos(),
        unidades=obtener_unidades(),
        modo="Crear",
    )


@main_bp.route("/productos/presentaciones/<int:presentacion_id>/editar", methods=["GET", "POST"])
def presentacion_editar(presentacion_id):
    presentacion = ProductoPresentacion.query.get_or_404(presentacion_id)
    if request.method == "POST":
        guardar_presentacion(presentacion)
        db.session.commit()
        registrar_auditoria(
            "producto_presentaciones",
            presentacion.id,
            "editar",
            f"Presentacion editada: {presentacion.nombre}",
        )
        flash("Presentación actualizada correctamente.", "success")
        return redirect(url_for("main.presentaciones"))

    return render_template(
        "productos/presentaciones/form.html",
        presentacion=presentacion,
        productos=obtener_productos(),
        unidades=obtener_unidades(),
        modo="Editar",
    )


@main_bp.route("/productos/presentaciones/<int:presentacion_id>/anular", methods=["POST"])
def presentacion_anular(presentacion_id):
    presentacion = ProductoPresentacion.query.get_or_404(presentacion_id)
    motivo = request.form.get("motivo_anulacion", "").strip() or "Anulacion desde modulo de presentaciones"

    presentacion.activo = False
    presentacion.anulado_en = datetime.utcnow()
    presentacion.motivo_anulacion = motivo
    db.session.commit()
    registrar_auditoria("producto_presentaciones", presentacion.id, "anular", motivo)
    flash("Presentación anulada correctamente.", "success")
    return redirect(url_for("main.presentaciones"))


@main_bp.route("/productos/lotes")
def lotes():
    busqueda = request.args.get("q", "").strip()
    estado = request.args.get("estado", "activos")

    consulta = ProductoLote.query.join(Producto)
    if estado == "anulados":
        consulta = consulta.filter(ProductoLote.activo.is_(False))
    elif estado != "todos":
        consulta = consulta.filter(ProductoLote.activo.is_(True))

    if busqueda:
        patron = f"%{busqueda}%"
        consulta = consulta.outerjoin(ProductoPresentacion).outerjoin(Proveedor).filter(
            or_(
                ProductoLote.numero_lote.ilike(patron),
                Producto.nombre.ilike(patron),
                Producto.codigo.ilike(patron),
                ProductoPresentacion.nombre.ilike(patron),
                Proveedor.nombre.ilike(patron),
            )
        )

    lotes_lista = consulta.order_by(Producto.nombre.asc(), ProductoLote.numero_lote.asc()).all()
    return render_template(
        "productos/lotes/index.html",
        lotes=lotes_lista,
        busqueda=busqueda,
        estado=estado,
    )


@main_bp.route("/productos/lotes/nuevo", methods=["GET", "POST"])
def lote_nuevo():
    lote = ProductoLote()
    if request.method == "POST":
        guardar_lote(lote)
        db.session.add(lote)
        db.session.commit()
        registrar_auditoria("producto_lotes", lote.id, "crear", f"Lote creado: {lote.numero_lote}")
        flash("Lote creado correctamente.", "success")
        return redirect(url_for("main.lotes"))

    return render_template(
        "productos/lotes/form.html",
        lote=lote,
        productos=obtener_productos(),
        presentaciones=obtener_presentaciones(),
        proveedores=obtener_proveedores(),
        modo="Crear",
    )


@main_bp.route("/productos/lotes/<int:lote_id>/editar", methods=["GET", "POST"])
def lote_editar(lote_id):
    lote = ProductoLote.query.get_or_404(lote_id)
    if request.method == "POST":
        guardar_lote(lote)
        db.session.commit()
        registrar_auditoria("producto_lotes", lote.id, "editar", f"Lote editado: {lote.numero_lote}")
        flash("Lote actualizado correctamente.", "success")
        return redirect(url_for("main.lotes"))

    return render_template(
        "productos/lotes/form.html",
        lote=lote,
        productos=obtener_productos(),
        presentaciones=obtener_presentaciones(),
        proveedores=obtener_proveedores(),
        modo="Editar",
    )


@main_bp.route("/productos/lotes/<int:lote_id>/anular", methods=["POST"])
def lote_anular(lote_id):
    lote = ProductoLote.query.get_or_404(lote_id)
    motivo = request.form.get("motivo_anulacion", "").strip() or "Anulacion desde modulo de lotes"

    lote.activo = False
    lote.anulado_en = datetime.utcnow()
    lote.motivo_anulacion = motivo
    db.session.commit()
    registrar_auditoria("producto_lotes", lote.id, "anular", motivo)
    flash("Lote anulado correctamente.", "success")
    return redirect(url_for("main.lotes"))


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
    unidad_id = request.form.get("unidad_id", "").strip()
    producto.unidad_id = int(unidad_id) if unidad_id else None
    if producto.unidad_id:
        unidad = Unidad.query.get(producto.unidad_id)
        producto.unidad = unidad.nombre if unidad else "unidad"
    else:
        producto.unidad = "unidad"
    producto.maneja_vencimiento = request.form.get("maneja_vencimiento") == "on"
    producto.maneja_lotes = request.form.get("maneja_lotes") == "on"
    producto.maneja_presentaciones = request.form.get("maneja_presentaciones") == "on"
    producto.stock_minimo = request.form.get("stock_minimo", "0").strip() or 0


def guardar_unidad(unidad):
    unidad.nombre = request.form.get("nombre", "").strip()
    unidad.abreviatura = request.form.get("abreviatura", "").strip()


def guardar_presentacion(presentacion):
    presentacion.producto_id = int(request.form.get("producto_id"))
    presentacion.nombre = request.form.get("nombre", "").strip()
    unidad_id = request.form.get("unidad_id", "").strip()
    presentacion.unidad_id = int(unidad_id) if unidad_id else None
    presentacion.factor = request.form.get("factor", "1").strip() or 1
    presentacion.talla = request.form.get("talla", "").strip() or None
    presentacion.color = request.form.get("color", "").strip() or None
    presentacion.referencia_interna = request.form.get("referencia_interna", "").strip() or None


def guardar_lote(lote):
    lote.producto_id = int(request.form.get("producto_id"))
    presentacion_id = request.form.get("presentacion_id", "").strip()
    proveedor_id = request.form.get("proveedor_id", "").strip()
    fecha_vencimiento = request.form.get("fecha_vencimiento", "").strip()

    lote.presentacion_id = int(presentacion_id) if presentacion_id else None
    lote.proveedor_id = int(proveedor_id) if proveedor_id else None
    lote.numero_lote = request.form.get("numero_lote", "").strip()
    lote.fecha_vencimiento = datetime.strptime(fecha_vencimiento, "%Y-%m-%d").date() if fecha_vencimiento else None
    lote.cantidad_actual = request.form.get("cantidad_actual", "0").strip() or 0
    lote.observaciones = request.form.get("observaciones", "").strip() or None


def obtener_unidades():
    return Unidad.query.filter_by(activo=True).order_by(Unidad.nombre.asc()).all()


def obtener_productos():
    return Producto.query.filter_by(activo=True).order_by(Producto.nombre.asc()).all()


def obtener_presentaciones():
    return ProductoPresentacion.query.filter_by(activo=True).order_by(
        ProductoPresentacion.nombre.asc()
    ).all()


def obtener_proveedores():
    return Proveedor.query.filter_by(activo=True).order_by(Proveedor.nombre.asc()).all()


def unidad_duplicada(nombre, abreviatura, unidad_id=None):
    consulta = Unidad.query.filter(
        or_(Unidad.nombre == nombre, Unidad.abreviatura == abreviatura)
    )
    if unidad_id:
        consulta = consulta.filter(Unidad.id != unidad_id)
    return consulta.first() is not None


def registrar_auditoria(tabla, registro_id, accion, detalle):
    db.session.add(
        Auditoria(tabla=tabla, registro_id=registro_id, accion=accion, detalle=detalle)
    )
    db.session.commit()
