from datetime import datetime
from decimal import Decimal
from pathlib import Path

from flask import Blueprint, flash, redirect, render_template, request, url_for
from sqlalchemy import or_
from werkzeug.utils import secure_filename

from .extensions import db
from .models import (
    Auditoria,
    Cliente,
    CompraCotizacion,
    CompraCotizacionDetalle,
    CompraPedido,
    CompraPedidoDetalle,
    CompraRecepcion,
    CompraRecepcionDetalle,
    CompraSolicitud,
    CompraSolicitudDetalle,
    CompraSolicitudProveedor,
    InventarioMovimiento,
    Producto,
    ProductoLote,
    ProductoPresentacion,
    ProductoProveedor,
    Proveedor,
    Unidad,
)

main_bp = Blueprint("main", __name__)
UPLOAD_DIR = Path(__file__).resolve().parent / "static" / "uploads" / "cotizaciones"


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
        {"nombre": "Despachos y recibos", "icono": "warehouse", "clase": "inventory", "url": "main.inventario_movimientos"},
        {"nombre": "Compras", "icono": "truck", "clase": "suppliers", "url": "main.compras"},
        {"nombre": "Cotizaciones", "icono": "quote", "clase": "quotes"},
        {"nombre": "Cartera", "icono": "wallet", "clase": "wallet"},
    ]

    return render_template("dashboard.html", indicadores=indicadores, accesos=accesos)


@main_bp.route("/compras")
def compras():
    opciones = [
        {"nombre": "Solicitudes", "detalle": "Pedir precio a varios proveedores", "icono": "history", "url": "main.compra_solicitudes"},
        {"nombre": "Cotizaciones", "detalle": "Respuestas de proveedores", "icono": "history", "url": "main.compra_cotizaciones"},
        {"nombre": "Pedidos", "detalle": "Solicitudes a proveedor", "icono": "truck", "url": "main.compra_pedidos"},
        {"nombre": "Recepciones", "detalle": "Entradas parciales o directas", "icono": "warehouse", "url": "main.compra_recepciones"},
        {"nombre": "Manual", "detalle": "Pendiente para pruebas", "icono": "history"},
    ]
    return render_template("compras/modulo.html", opciones=opciones)


@main_bp.route("/login")
def login():
    return render_template("login.html")


@main_bp.route("/compras/solicitudes")
def compra_solicitudes():
    busqueda = request.args.get("q", "").strip()
    estado = request.args.get("estado", "todos")

    consulta = CompraSolicitud.query
    if estado != "todos":
        consulta = consulta.filter(CompraSolicitud.estado == estado)
    if busqueda:
        patron = f"%{busqueda}%"
        consulta = consulta.filter(
            or_(
                CompraSolicitud.numero.ilike(patron),
                CompraSolicitud.observaciones.ilike(patron),
            )
        )

    solicitudes = consulta.order_by(CompraSolicitud.fecha.desc(), CompraSolicitud.id.desc()).all()
    return render_template(
        "compras/solicitudes/index.html",
        solicitudes=solicitudes,
        busqueda=busqueda,
        estado=estado,
    )


@main_bp.route("/compras/solicitudes/nueva", methods=["GET", "POST"])
def compra_solicitud_nueva():
    solicitud = CompraSolicitud(numero=siguiente_numero("SOL-C", CompraSolicitud), fecha=datetime.utcnow().date())
    if request.method == "POST":
        guardar_solicitud_compra(solicitud)
        if not solicitud.detalles:
            flash("Agregue al menos un producto a la solicitud.", "error")
            return render_template_solicitud(solicitud, "Crear")
        if not solicitud.proveedores:
            flash("Seleccione al menos un proveedor.", "error")
            return render_template_solicitud(solicitud, "Crear")
        db.session.add(solicitud)
        db.session.commit()
        registrar_auditoria("compra_solicitudes", solicitud.id, "crear", f"Solicitud creada: {solicitud.numero}")
        flash("Solicitud creada en borrador. Envie la solicitud para generar cotizaciones.", "success")
        return redirect(url_for("main.compra_solicitudes"))

    return render_template_solicitud(solicitud, "Crear")


@main_bp.route("/compras/solicitudes/<int:solicitud_id>/enviar", methods=["POST"])
def compra_solicitud_enviar(solicitud_id):
    solicitud = CompraSolicitud.query.get_or_404(solicitud_id)
    if solicitud.estado != "BORRADOR":
        flash("Solo se pueden enviar solicitudes en borrador.", "error")
        return redirect(url_for("main.compra_solicitudes"))

    generar_cotizaciones_desde_solicitud(solicitud)
    solicitud.estado = "ENVIADA"
    db.session.commit()
    registrar_auditoria("compra_solicitudes", solicitud.id, "enviar", f"Solicitud enviada: {solicitud.numero}")
    flash("Solicitud enviada y cotizaciones generadas.", "success")
    return redirect(url_for("main.compra_solicitud_comparativo", solicitud_id=solicitud.id))


@main_bp.route("/compras/solicitudes/<int:solicitud_id>/finalizar", methods=["POST"])
def compra_solicitud_finalizar(solicitud_id):
    solicitud = CompraSolicitud.query.get_or_404(solicitud_id)
    solicitud.estado = "FINALIZADA"
    db.session.commit()
    registrar_auditoria("compra_solicitudes", solicitud.id, "finalizar", f"Solicitud finalizada: {solicitud.numero}")
    flash("Solicitud finalizada.", "success")
    return redirect(url_for("main.compra_solicitudes"))


@main_bp.route("/compras/solicitudes/<int:solicitud_id>/cancelar", methods=["POST"])
def compra_solicitud_cancelar(solicitud_id):
    solicitud = CompraSolicitud.query.get_or_404(solicitud_id)
    solicitud.estado = "CANCELADA"
    solicitud.activo = False
    solicitud.anulado_en = datetime.utcnow()
    solicitud.motivo_anulacion = request.form.get("motivo_anulacion", "").strip() or "Solicitud cancelada"
    db.session.commit()
    registrar_auditoria("compra_solicitudes", solicitud.id, "cancelar", solicitud.motivo_anulacion)
    flash("Solicitud cancelada.", "success")
    return redirect(url_for("main.compra_solicitudes"))


@main_bp.route("/compras/solicitudes/<int:solicitud_id>/eliminar", methods=["POST"])
def compra_solicitud_eliminar(solicitud_id):
    solicitud = CompraSolicitud.query.get_or_404(solicitud_id)
    cotizacion_ids = [
        item.cotizacion_id for item in solicitud.proveedores if item.cotizacion_id
    ]
    pedidos_asociados = 0
    if cotizacion_ids:
        pedidos_asociados = CompraPedido.query.filter(
            CompraPedido.cotizacion_id.in_(cotizacion_ids)
        ).count()

    if pedidos_asociados:
        flash("No se puede eliminar la solicitud porque ya tiene pedidos asociados.", "error")
        return redirect(url_for("main.compra_solicitudes"))

    numero = solicitud.numero
    cotizaciones = [item.cotizacion for item in solicitud.proveedores if item.cotizacion]
    for item in list(solicitud.proveedores):
        db.session.delete(item)
    db.session.flush()
    for cotizacion in cotizaciones:
        db.session.delete(cotizacion)
    db.session.delete(solicitud)
    db.session.commit()
    registrar_auditoria("compra_solicitudes", solicitud_id, "eliminar", f"Solicitud eliminada: {numero}")
    flash("Solicitud eliminada correctamente.", "success")
    return redirect(url_for("main.compra_solicitudes"))


@main_bp.route("/compras/solicitudes/<int:solicitud_id>/comparativo")
def compra_solicitud_comparativo(solicitud_id):
    solicitud = CompraSolicitud.query.get_or_404(solicitud_id)
    return render_template(
        "compras/solicitudes/comparativo.html",
        solicitud=solicitud,
    )


@main_bp.route("/compras/cotizaciones")
def compra_cotizaciones():
    busqueda = request.args.get("q", "").strip()
    estado = request.args.get("estado", "todos")

    consulta = CompraCotizacion.query.join(Proveedor)
    if estado != "todos":
        consulta = consulta.filter(CompraCotizacion.estado == estado)
    if busqueda:
        patron = f"%{busqueda}%"
        consulta = consulta.filter(
            or_(
                CompraCotizacion.numero.ilike(patron),
                Proveedor.nombre.ilike(patron),
                CompraCotizacion.observaciones.ilike(patron),
            )
        )

    cotizaciones = consulta.order_by(CompraCotizacion.fecha.desc(), CompraCotizacion.id.desc()).all()
    return render_template(
        "compras/cotizaciones/index.html",
        cotizaciones=cotizaciones,
        busqueda=busqueda,
        estado=estado,
    )


@main_bp.route("/compras/cotizaciones/nueva", methods=["GET", "POST"])
def compra_cotizacion_nueva():
    cotizacion = CompraCotizacion(numero=siguiente_numero("COT-P", CompraCotizacion), fecha=datetime.utcnow().date())
    if request.method == "POST":
        try:
            guardar_cotizacion_compra(cotizacion)
        except ValueError as error:
            flash(str(error), "error")
            return render_template_cotizacion(cotizacion, "Crear")
        if not cotizacion.detalles:
            flash("Agregue al menos un producto a la cotizacion.", "error")
            return render_template_cotizacion(cotizacion, "Crear")
        db.session.add(cotizacion)
        db.session.commit()
        registrar_auditoria("compra_cotizaciones", cotizacion.id, "crear", f"Cotizacion creada: {cotizacion.numero}")
        flash("Cotizacion registrada correctamente.", "success")
        return redirect(url_for("main.compra_cotizaciones"))

    return render_template_cotizacion(cotizacion, "Crear")


@main_bp.route("/compras/cotizaciones/<int:cotizacion_id>/editar", methods=["GET", "POST"])
def compra_cotizacion_editar(cotizacion_id):
    cotizacion = CompraCotizacion.query.get_or_404(cotizacion_id)
    if request.method == "POST":
        try:
            guardar_cotizacion_compra(cotizacion)
        except ValueError as error:
            db.session.rollback()
            flash(str(error), "error")
            return render_template_cotizacion(cotizacion, "Ver / Actualizar")
        if not cotizacion.detalles:
            flash("Agregue al menos un producto a la cotizacion.", "error")
            return render_template_cotizacion(cotizacion, "Ver / Actualizar")
        actualizar_estado_respuesta_cotizacion(cotizacion)
        db.session.commit()
        actualizar_estado_cotizacion(cotizacion)
        if cotizacion.solicitud:
            actualizar_estado_solicitud(cotizacion.solicitud)
            db.session.commit()
        registrar_auditoria("compra_cotizaciones", cotizacion.id, "editar", f"Cotizacion editada: {cotizacion.numero}")
        flash("Cotizacion actualizada correctamente.", "success")
        return redirect(url_for("main.compra_cotizaciones"))

    return render_template_cotizacion(cotizacion, "Ver / Actualizar")


@main_bp.route("/compras/cotizaciones/<int:cotizacion_id>/convertir", methods=["GET", "POST"])
def compra_cotizacion_convertir(cotizacion_id):
    cotizacion = CompraCotizacion.query.get_or_404(cotizacion_id)
    pedido = CompraPedido(
        numero=siguiente_numero("PED", CompraPedido),
        cotizacion=cotizacion,
        proveedor=cotizacion.proveedor,
        fecha=datetime.utcnow().date(),
    )
    if request.method == "POST":
        try:
            convertir_cotizacion_a_pedido(cotizacion, pedido)
        except ValueError as error:
            db.session.rollback()
            flash(str(error), "error")
            return render_template_convertir_cotizacion(cotizacion, pedido)
        if not pedido.detalles:
            flash("Seleccione al menos una cantidad para pedir.", "error")
            return render_template_convertir_cotizacion(cotizacion, pedido)
        db.session.add(pedido)
        db.session.commit()
        actualizar_estado_cotizacion(cotizacion)
        if cotizacion.solicitud:
            actualizar_estado_solicitud(cotizacion.solicitud)
        db.session.commit()
        registrar_auditoria("compra_pedidos", pedido.id, "crear", f"Pedido creado desde {cotizacion.numero}: {pedido.numero}")
        flash("Pedido creado desde cotizacion correctamente.", "success")
        return redirect(url_for("main.compra_pedidos"))

    return render_template_convertir_cotizacion(cotizacion, pedido)


@main_bp.route("/compras/pedidos")
def compra_pedidos():
    busqueda = request.args.get("q", "").strip()
    estado = request.args.get("estado", "todos")

    consulta = CompraPedido.query.join(Proveedor)
    if estado != "todos":
        consulta = consulta.filter(CompraPedido.estado == estado)
    if busqueda:
        patron = f"%{busqueda}%"
        consulta = consulta.filter(
            or_(
                CompraPedido.numero.ilike(patron),
                Proveedor.nombre.ilike(patron),
                CompraPedido.observaciones.ilike(patron),
            )
        )

    pedidos = consulta.order_by(CompraPedido.fecha.desc(), CompraPedido.id.desc()).all()
    return render_template("compras/pedidos/index.html", pedidos=pedidos, busqueda=busqueda, estado=estado)


@main_bp.route("/compras/pedidos/nuevo", methods=["GET", "POST"])
def compra_pedido_nuevo():
    pedido = CompraPedido(numero=siguiente_numero("PED", CompraPedido), fecha=datetime.utcnow().date())
    if request.method == "POST":
        guardar_pedido_compra(pedido)
        if not pedido.detalles:
            flash("Agregue al menos un producto al pedido.", "error")
            return render_template_pedido(pedido, "Crear")
        db.session.add(pedido)
        db.session.commit()
        registrar_auditoria("compra_pedidos", pedido.id, "crear", f"Pedido creado: {pedido.numero}")
        flash("Pedido creado correctamente.", "success")
        return redirect(url_for("main.compra_pedidos"))

    return render_template_pedido(pedido, "Crear")


@main_bp.route("/compras/pedidos/<int:pedido_id>/editar", methods=["GET", "POST"])
def compra_pedido_editar(pedido_id):
    pedido = CompraPedido.query.get_or_404(pedido_id)
    if request.method == "POST":
        guardar_pedido_compra(pedido)
        if not pedido.detalles:
            flash("Agregue al menos un producto al pedido.", "error")
            return render_template_pedido(pedido, "Editar")
        db.session.commit()
        actualizar_estado_pedido(pedido)
        registrar_auditoria("compra_pedidos", pedido.id, "editar", f"Pedido editado: {pedido.numero}")
        flash("Pedido actualizado correctamente.", "success")
        return redirect(url_for("main.compra_pedidos"))

    return render_template_pedido(pedido, "Editar")


@main_bp.route("/compras/pedidos/<int:pedido_id>/eliminar", methods=["POST"])
def compra_pedido_eliminar(pedido_id):
    pedido = CompraPedido.query.get_or_404(pedido_id)
    tiene_recepciones = CompraRecepcion.query.filter_by(pedido_id=pedido.id).count() > 0
    tiene_cantidades_recibidas = any(Decimal(detalle.cantidad_recibida or 0) > 0 for detalle in pedido.detalles)
    if tiene_recepciones or tiene_cantidades_recibidas:
        flash("No se puede eliminar el pedido porque ya tiene recepciones asociadas.", "error")
        return redirect(url_for("main.compra_pedidos"))

    numero = pedido.numero
    cotizacion = pedido.cotizacion
    for detalle in pedido.detalles:
        if detalle.cotizacion_detalle:
            detalle.cotizacion_detalle.cantidad_pedida = max(
                Decimal(detalle.cotizacion_detalle.cantidad_pedida or 0) - Decimal(detalle.cantidad_pedida or 0),
                Decimal("0"),
            )
            actualizar_estado_detalle_cotizacion(detalle.cotizacion_detalle)

    db.session.delete(pedido)
    db.session.commit()
    if cotizacion:
        actualizar_estado_cotizacion(cotizacion)
        if cotizacion.solicitud:
            actualizar_estado_solicitud(cotizacion.solicitud)
        db.session.commit()
    registrar_auditoria("compra_pedidos", pedido_id, "eliminar", f"Pedido eliminado: {numero}")
    flash("Pedido eliminado correctamente.", "success")
    return redirect(url_for("main.compra_pedidos"))


@main_bp.route("/compras/pedidos/<int:pedido_id>/recibir", methods=["GET", "POST"])
def compra_pedido_recibir(pedido_id):
    pedido = CompraPedido.query.get_or_404(pedido_id)
    recepcion = CompraRecepcion(
        numero=siguiente_numero("REC", CompraRecepcion),
        pedido=pedido,
        proveedor=pedido.proveedor,
        fecha=datetime.utcnow().date(),
    )
    if request.method == "POST":
        try:
            guardar_recepcion_compra(recepcion, pedido)
        except ValueError as error:
            db.session.rollback()
            flash(str(error), "error")
            return render_template_recepcion(recepcion, "Recibir pedido", pedido)
        if not recepcion.detalles:
            flash("Registre al menos una cantidad recibida.", "error")
            return render_template_recepcion(recepcion, "Recibir pedido", pedido)
        db.session.add(recepcion)
        db.session.commit()
        actualizar_estado_pedido(pedido)
        db.session.commit()
        registrar_auditoria("compra_recepciones", recepcion.id, "crear", f"Recepcion creada: {recepcion.numero}")
        flash("Recepcion registrada correctamente.", "success")
        return redirect(url_for("main.compra_pedidos"))

    return render_template_recepcion(recepcion, "Recibir pedido", pedido)


@main_bp.route("/compras/recepciones")
def compra_recepciones():
    busqueda = request.args.get("q", "").strip()
    consulta = CompraRecepcion.query.join(Proveedor)
    if busqueda:
        patron = f"%{busqueda}%"
        consulta = consulta.outerjoin(CompraPedido).filter(
            or_(
                CompraRecepcion.numero.ilike(patron),
                CompraRecepcion.documento.ilike(patron),
                Proveedor.nombre.ilike(patron),
                CompraPedido.numero.ilike(patron),
            )
        )
    recepciones = consulta.order_by(CompraRecepcion.fecha.desc(), CompraRecepcion.id.desc()).all()
    return render_template("compras/recepciones/index.html", recepciones=recepciones, busqueda=busqueda)


@main_bp.route("/compras/recepciones/nueva", methods=["GET", "POST"])
def compra_recepcion_nueva():
    recepcion = CompraRecepcion(numero=siguiente_numero("REC", CompraRecepcion), fecha=datetime.utcnow().date())
    if request.method == "POST":
        try:
            guardar_recepcion_compra(recepcion)
        except ValueError as error:
            db.session.rollback()
            flash(str(error), "error")
            return render_template_recepcion(recepcion, "Compra directa")
        if not recepcion.detalles:
            flash("Registre al menos una cantidad recibida.", "error")
            return render_template_recepcion(recepcion, "Compra directa")
        db.session.add(recepcion)
        db.session.commit()
        registrar_auditoria("compra_recepciones", recepcion.id, "crear", f"Recepcion creada: {recepcion.numero}")
        flash("Compra recibida correctamente.", "success")
        return redirect(url_for("main.compra_recepciones"))

    return render_template_recepcion(recepcion, "Compra directa")


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
        {"nombre": "Inventario", "detalle": "Saldos y movimientos", "icono": "warehouse", "url": "main.inventario_movimientos"},
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


@main_bp.route("/inventario/movimientos")
def inventario_movimientos():
    busqueda = request.args.get("q", "").strip()
    tipo = request.args.get("tipo", "todos")

    consulta = InventarioMovimiento.query.join(
        Producto, InventarioMovimiento.producto_id == Producto.id
    ).join(
        ProductoLote, InventarioMovimiento.lote_id == ProductoLote.id
    )
    if tipo != "todos":
        consulta = consulta.filter(InventarioMovimiento.tipo == tipo)

    if busqueda:
        patron = f"%{busqueda}%"
        consulta = consulta.outerjoin(
            Cliente, InventarioMovimiento.cliente_id == Cliente.id
        ).outerjoin(
            Proveedor, InventarioMovimiento.proveedor_id == Proveedor.id
        ).filter(
            or_(
                Producto.nombre.ilike(patron),
                Producto.codigo.ilike(patron),
                ProductoLote.numero_lote.ilike(patron),
                InventarioMovimiento.documento.ilike(patron),
                InventarioMovimiento.responsable.ilike(patron),
                Cliente.nombre.ilike(patron),
                Proveedor.nombre.ilike(patron),
            )
        )

    movimientos = consulta.order_by(
        InventarioMovimiento.fecha.desc(),
        InventarioMovimiento.id.desc(),
    ).all()
    return render_template(
        "inventario/index.html",
        movimientos=movimientos,
        busqueda=busqueda,
        tipo=tipo,
    )


@main_bp.route("/inventario/recibo", methods=["GET", "POST"])
def inventario_recibo():
    movimiento = InventarioMovimiento(tipo="RECIBO")
    if request.method == "POST":
        lote = ProductoLote.query.get_or_404(int(request.form.get("lote_id")))
        cantidad = obtener_decimal("cantidad")
        if cantidad <= 0:
            flash("La cantidad recibida debe ser mayor que cero.", "error")
            return render_template_movimiento(movimiento, "Recibo de mercancia")

        guardar_movimiento(movimiento, lote, "RECIBO", cantidad)
        lote.cantidad_actual = Decimal(lote.cantidad_actual or 0) + cantidad
        db.session.add(movimiento)
        db.session.commit()
        registrar_auditoria(
            "inventario_movimientos",
            movimiento.id,
            "recibo",
            f"Recibo {movimiento.documento or ''} - {lote.numero_lote}",
        )
        flash("Recibo registrado correctamente.", "success")
        return redirect(url_for("main.inventario_movimientos"))

    return render_template_movimiento(movimiento, "Recibo de mercancia")


@main_bp.route("/inventario/despacho", methods=["GET", "POST"])
def inventario_despacho():
    movimiento = InventarioMovimiento(tipo="DESPACHO")
    if request.method == "POST":
        lote = ProductoLote.query.get_or_404(int(request.form.get("lote_id")))
        cantidad = obtener_decimal("cantidad")
        disponible = Decimal(lote.cantidad_actual or 0)
        if cantidad <= 0:
            flash("La cantidad despachada debe ser mayor que cero.", "error")
            return render_template_movimiento(movimiento, "Despacho de mercancia")
        if cantidad > disponible:
            flash("No hay saldo suficiente en el lote seleccionado.", "error")
            return render_template_movimiento(movimiento, "Despacho de mercancia")

        guardar_movimiento(movimiento, lote, "DESPACHO", cantidad)
        lote.cantidad_actual = disponible - cantidad
        db.session.add(movimiento)
        db.session.commit()
        registrar_auditoria(
            "inventario_movimientos",
            movimiento.id,
            "despacho",
            f"Despacho {movimiento.documento or ''} - {lote.numero_lote}",
        )
        flash("Despacho registrado correctamente.", "success")
        return redirect(url_for("main.inventario_movimientos"))

    return render_template_movimiento(movimiento, "Despacho de mercancia")


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


def guardar_solicitud_compra(solicitud):
    solicitud.numero = request.form.get("numero", "").strip() or solicitud.numero
    solicitud.fecha = obtener_fecha("fecha") or datetime.utcnow().date()
    solicitud.fecha_limite = obtener_fecha("fecha_limite")
    solicitud.estado = request.form.get("estado", "BORRADOR")
    solicitud.observaciones = request.form.get("observaciones", "").strip() or None

    detalles = []
    for indice in range(1, 100):
        producto_id = request.form.get(f"producto_id_{indice}", "").strip()
        cantidad = obtener_decimal_form(f"cantidad_{indice}")
        if not producto_id or cantidad <= 0:
            continue
        presentacion_id = request.form.get(f"presentacion_id_{indice}", "").strip()
        detalles.append(
            CompraSolicitudDetalle(
                producto_id=int(producto_id),
                presentacion_id=int(presentacion_id) if presentacion_id else None,
                cantidad_solicitada=cantidad,
                observaciones=request.form.get(f"observaciones_{indice}", "").strip() or None,
            )
        )
    solicitud.detalles = detalles

    proveedores = []
    for proveedor_id in request.form.getlist("proveedor_ids"):
        if proveedor_id:
            proveedores.append(CompraSolicitudProveedor(proveedor_id=int(proveedor_id)))
    solicitud.proveedores = proveedores


def generar_cotizaciones_desde_solicitud(solicitud):
    for solicitud_proveedor in solicitud.proveedores:
        if solicitud_proveedor.cotizacion:
            continue
        cotizacion = CompraCotizacion(
            numero=siguiente_numero("COT-P", CompraCotizacion),
            solicitud=solicitud,
            proveedor=solicitud_proveedor.proveedor,
            fecha=solicitud.fecha,
            vigencia_hasta=solicitud.fecha_limite,
            estado="SOLICITADA",
            observaciones=f"Generada desde {solicitud.numero}",
        )
        for detalle in solicitud.detalles:
            cotizacion.detalles.append(
                CompraCotizacionDetalle(
                    producto_id=detalle.producto_id,
                    presentacion_id=detalle.presentacion_id,
                    cantidad_cotizada=detalle.cantidad_solicitada,
                    observaciones=detalle.observaciones,
                    estado="ABIERTA",
                )
            )
        solicitud_proveedor.cotizacion = cotizacion
        solicitud_proveedor.estado = "ENVIADA"
        db.session.add(cotizacion)


def guardar_cotizacion_compra(cotizacion):
    cotizacion.numero = request.form.get("numero", "").strip() or cotizacion.numero
    cotizacion.proveedor_id = int(request.form.get("proveedor_id"))
    solicitud_id = request.form.get("solicitud_id", "").strip()
    cotizacion.solicitud_id = int(solicitud_id) if solicitud_id else cotizacion.solicitud_id
    cotizacion.fecha = obtener_fecha("fecha") or datetime.utcnow().date()
    cotizacion.vigencia_hasta = obtener_fecha("vigencia_hasta")
    cotizacion.estado = request.form.get("estado", "BORRADOR")
    cotizacion.forma_pago = request.form.get("forma_pago", "").strip() or None
    cotizacion.dias_credito = int(request.form.get("dias_credito", "0").strip() or 0)
    cotizacion.tiempo_entrega_dias = int(request.form.get("tiempo_entrega_dias", "0").strip() or 0)
    cotizacion.observaciones = request.form.get("observaciones", "").strip() or None
    guardar_archivo_cotizacion(cotizacion)

    detalles_previos = {str(detalle.id): detalle for detalle in cotizacion.detalles if detalle.id}
    nuevos_detalles = []
    for indice in range(1, 100):
        producto_id = request.form.get(f"producto_id_{indice}", "").strip()
        cantidad = obtener_decimal_form(f"cantidad_{indice}")
        if not producto_id or cantidad <= 0:
            continue

        detalle_id = request.form.get(f"detalle_id_{indice}", "").strip()
        detalle = detalles_previos.get(detalle_id, CompraCotizacionDetalle())
        if Decimal(detalle.cantidad_pedida or 0) > cantidad:
            raise ValueError("No puede bajar una cantidad cotizada por debajo de lo ya pedido.")
        detalle.producto_id = int(producto_id)
        presentacion_id = request.form.get(f"presentacion_id_{indice}", "").strip()
        detalle.presentacion_id = int(presentacion_id) if presentacion_id else None
        detalle.cantidad_cotizada = cantidad
        detalle.costo_unitario = request.form.get(f"costo_unitario_{indice}", "").strip() or None
        detalle.referencia_proveedor = request.form.get(f"referencia_proveedor_{indice}", "").strip() or None
        detalle.observaciones = request.form.get(f"observaciones_{indice}", "").strip() or None
        actualizar_estado_detalle_cotizacion(detalle)
        nuevos_detalles.append(detalle)

    cotizacion.detalles = nuevos_detalles


def guardar_archivo_cotizacion(cotizacion):
    archivo = request.files.get("archivo_cotizacion")
    if not archivo or not archivo.filename:
        return

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    nombre_seguro = secure_filename(archivo.filename)
    destino_nombre = f"{cotizacion.numero.replace('/', '-')}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{nombre_seguro}"
    destino = UPLOAD_DIR / destino_nombre
    archivo.save(destino)
    cotizacion.archivo_nombre = archivo.filename
    cotizacion.archivo_ruta = f"uploads/cotizaciones/{destino_nombre}"


def convertir_cotizacion_a_pedido(cotizacion, pedido):
    pedido.numero = request.form.get("numero", "").strip() or pedido.numero
    pedido.proveedor = cotizacion.proveedor
    pedido.fecha = obtener_fecha("fecha") or datetime.utcnow().date()
    pedido.fecha_estimada = obtener_fecha("fecha_estimada")
    pedido.estado = request.form.get("estado", "CONFIRMADO")
    pedido.observaciones = request.form.get("observaciones", "").strip() or f"Pedido generado desde {cotizacion.numero}"

    for indice, detalle_cotizacion in enumerate(cotizacion.detalles, start=1):
        cantidad = obtener_decimal_form(f"cantidad_{indice}")
        if cantidad <= 0:
            continue
        pendiente = cantidad_pendiente_cotizacion(detalle_cotizacion)
        if cantidad > pendiente:
            raise ValueError(f"La cantidad solicitada de {detalle_cotizacion.producto.nombre} supera el pendiente cotizado.")

        detalle_cotizacion.cantidad_pedida = Decimal(detalle_cotizacion.cantidad_pedida or 0) + cantidad
        actualizar_estado_detalle_cotizacion(detalle_cotizacion)
        pedido.detalles.append(
            CompraPedidoDetalle(
                cotizacion_detalle=detalle_cotizacion,
                producto_id=detalle_cotizacion.producto_id,
                presentacion_id=detalle_cotizacion.presentacion_id,
                cantidad_pedida=cantidad,
                costo_unitario=request.form.get(f"costo_unitario_{indice}", "").strip() or detalle_cotizacion.costo_unitario,
                referencia_proveedor=detalle_cotizacion.referencia_proveedor,
                observaciones=request.form.get(f"observaciones_{indice}", "").strip() or detalle_cotizacion.observaciones,
                estado="ABIERTA",
            )
        )


def guardar_pedido_compra(pedido):
    pedido.numero = request.form.get("numero", "").strip() or pedido.numero
    pedido.proveedor_id = int(request.form.get("proveedor_id"))
    pedido.fecha = obtener_fecha("fecha") or datetime.utcnow().date()
    pedido.fecha_estimada = obtener_fecha("fecha_estimada")
    pedido.estado = request.form.get("estado", "BORRADOR")
    pedido.observaciones = request.form.get("observaciones", "").strip() or None

    detalles_previos = {str(detalle.id): detalle for detalle in pedido.detalles if detalle.id}
    nuevos_detalles = []
    for indice in range(1, 9):
        producto_id = request.form.get(f"producto_id_{indice}", "").strip()
        cantidad = obtener_decimal_form(f"cantidad_{indice}")
        if not producto_id or cantidad <= 0:
            continue

        detalle_id = request.form.get(f"detalle_id_{indice}", "").strip()
        detalle = detalles_previos.get(detalle_id, CompraPedidoDetalle())
        cotizacion_detalle_id = request.form.get(f"cotizacion_detalle_id_{indice}", "").strip()
        detalle.cotizacion_detalle_id = int(cotizacion_detalle_id) if cotizacion_detalle_id else detalle.cotizacion_detalle_id
        detalle.producto_id = int(producto_id)
        presentacion_id = request.form.get(f"presentacion_id_{indice}", "").strip()
        detalle.presentacion_id = int(presentacion_id) if presentacion_id else None
        detalle.cantidad_pedida = cantidad
        detalle.costo_unitario = request.form.get(f"costo_unitario_{indice}", "").strip() or None
        detalle.referencia_proveedor = request.form.get(f"referencia_proveedor_{indice}", "").strip() or None
        detalle.observaciones = request.form.get(f"observaciones_{indice}", "").strip() or None
        actualizar_estado_detalle(detalle)
        nuevos_detalles.append(detalle)

    pedido.detalles = nuevos_detalles


def guardar_recepcion_compra(recepcion, pedido=None):
    recepcion.numero = request.form.get("numero", "").strip() or recepcion.numero
    recepcion.proveedor_id = int(request.form.get("proveedor_id"))
    recepcion.fecha = obtener_fecha("fecha") or datetime.utcnow().date()
    recepcion.documento = request.form.get("documento", "").strip() or None
    recepcion.responsable = request.form.get("responsable", "").strip() or None
    recepcion.observaciones = request.form.get("observaciones", "").strip() or None
    if pedido:
        recepcion.pedido = pedido

    filas = pedido.detalles if pedido else range(1, 9)
    for indice, item in enumerate(filas, start=1):
        detalle_pedido = item if pedido else None
        producto_id = request.form.get(f"producto_id_{indice}", "").strip()
        if detalle_pedido:
            producto_id = str(detalle_pedido.producto_id)
        cantidad = obtener_decimal_form(f"cantidad_{indice}")
        if not producto_id or cantidad <= 0:
            continue
        if detalle_pedido and cantidad > cantidad_pendiente(detalle_pedido):
            raise ValueError(f"La cantidad recibida de {detalle_pedido.producto.nombre} supera el pendiente.")

        costo = request.form.get(f"costo_unitario_{indice}", "").strip() or None
        presentacion_id = request.form.get(f"presentacion_id_{indice}", "").strip()
        numero_lote = request.form.get(f"numero_lote_{indice}", "").strip()
        fecha_vencimiento = obtener_fecha(f"fecha_vencimiento_{indice}")
        lote = obtener_o_crear_lote(
            int(producto_id),
            int(presentacion_id) if presentacion_id else (detalle_pedido.presentacion_id if detalle_pedido else None),
            recepcion.proveedor_id,
            numero_lote,
            fecha_vencimiento,
        )
        lote.cantidad_actual = Decimal(lote.cantidad_actual or 0) + cantidad

        recepcion.detalles.append(
            CompraRecepcionDetalle(
                pedido_detalle=detalle_pedido,
                producto_id=int(producto_id),
                lote=lote,
                presentacion_id=lote.presentacion_id,
                cantidad=cantidad,
                costo_unitario=costo,
            )
        )
        if detalle_pedido:
            detalle_pedido.cantidad_recibida = Decimal(detalle_pedido.cantidad_recibida or 0) + cantidad
            actualizar_estado_detalle(detalle_pedido)
        registrar_movimiento_recepcion(recepcion, lote, cantidad, costo)
        actualizar_producto_proveedor(int(producto_id), recepcion.proveedor_id, costo, detalle_pedido)


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


def guardar_movimiento(movimiento, lote, tipo, cantidad):
    fecha = request.form.get("fecha", "").strip()
    proveedor_id = request.form.get("proveedor_id", "").strip()
    cliente_id = request.form.get("cliente_id", "").strip()

    movimiento.tipo = tipo
    movimiento.fecha = datetime.strptime(fecha, "%Y-%m-%d").date() if fecha else datetime.utcnow().date()
    movimiento.producto_id = lote.producto_id
    movimiento.lote_id = lote.id
    movimiento.presentacion_id = lote.presentacion_id
    movimiento.proveedor_id = int(proveedor_id) if proveedor_id else lote.proveedor_id
    movimiento.cliente_id = int(cliente_id) if cliente_id else None
    movimiento.cantidad = cantidad
    movimiento.costo_unitario = request.form.get("costo_unitario", "").strip() or None
    movimiento.documento = request.form.get("documento", "").strip() or None
    movimiento.responsable = request.form.get("responsable", "").strip() or None
    movimiento.observaciones = request.form.get("observaciones", "").strip() or None


def obtener_decimal(campo):
    valor = request.form.get(campo, "0").strip() or "0"
    return Decimal(valor)


def obtener_decimal_form(campo):
    valor = request.form.get(campo, "0").strip() or "0"
    return Decimal(valor)


def obtener_fecha(campo):
    valor = request.form.get(campo, "").strip()
    return datetime.strptime(valor, "%Y-%m-%d").date() if valor else None


def siguiente_numero(prefijo, modelo):
    siguiente = (db.session.query(db.func.count(modelo.id)).scalar() or 0) + 1
    return f"{prefijo}-{siguiente:05d}"


def cantidad_pendiente(detalle):
    return Decimal(detalle.cantidad_pedida or 0) - Decimal(detalle.cantidad_recibida or 0)


def cantidad_pendiente_cotizacion(detalle):
    return Decimal(detalle.cantidad_cotizada or 0) - Decimal(detalle.cantidad_pedida or 0)


def actualizar_estado_respuesta_cotizacion(cotizacion):
    tiene_precios = any(detalle.costo_unitario is not None for detalle in cotizacion.detalles)
    if cotizacion.estado in {"BORRADOR", "SOLICITADA"} and tiene_precios:
        cotizacion.estado = "RECIBIDA"


def actualizar_estado_detalle_cotizacion(detalle):
    pendiente = cantidad_pendiente_cotizacion(detalle)
    if pendiente <= 0:
        detalle.estado = "CERRADA"
    elif Decimal(detalle.cantidad_pedida or 0) > 0:
        detalle.estado = "PARCIAL"
    else:
        detalle.estado = "ABIERTA"


def actualizar_estado_cotizacion(cotizacion):
    for detalle in cotizacion.detalles:
        actualizar_estado_detalle_cotizacion(detalle)
    if not cotizacion.detalles:
        cotizacion.estado = "BORRADOR"
        return
    cerradas = all(detalle.estado == "CERRADA" for detalle in cotizacion.detalles)
    parciales = any(detalle.estado == "PARCIAL" for detalle in cotizacion.detalles)
    pedidas = any(Decimal(detalle.cantidad_pedida or 0) > 0 for detalle in cotizacion.detalles)
    if cerradas:
        cotizacion.estado = "CERRADA"
    elif parciales or pedidas:
        cotizacion.estado = "PARCIAL"
    else:
        actualizar_estado_respuesta_cotizacion(cotizacion)


def actualizar_estado_solicitud(solicitud):
    cotizaciones = [item.cotizacion for item in solicitud.proveedores if item.cotizacion]
    if not cotizaciones:
        return
    if all(cotizacion.estado == "CERRADA" for cotizacion in cotizaciones):
        solicitud.estado = "FINALIZADA"
    elif any(cotizacion.estado in {"RECIBIDA", "PARCIAL", "CERRADA"} for cotizacion in cotizaciones):
        solicitud.estado = "RESPONDIDA"
    elif solicitud.estado == "BORRADOR":
        solicitud.estado = "ENVIADA"


def actualizar_estado_detalle(detalle):
    pendiente = cantidad_pendiente(detalle)
    if pendiente <= 0:
        detalle.estado = "CERRADA"
    elif Decimal(detalle.cantidad_recibida or 0) > 0:
        detalle.estado = "PARCIAL"
    else:
        detalle.estado = "ABIERTA"


def actualizar_estado_pedido(pedido):
    for detalle in pedido.detalles:
        actualizar_estado_detalle(detalle)
    if not pedido.detalles:
        pedido.estado = "BORRADOR"
        return
    cerradas = all(detalle.estado == "CERRADA" for detalle in pedido.detalles)
    parciales = any(detalle.estado == "PARCIAL" for detalle in pedido.detalles)
    recibidas = any(Decimal(detalle.cantidad_recibida or 0) > 0 for detalle in pedido.detalles)
    if cerradas:
        pedido.estado = "CERRADO"
    elif parciales or recibidas:
        pedido.estado = "PARCIAL"


def obtener_o_crear_lote(producto_id, presentacion_id, proveedor_id, numero_lote, fecha_vencimiento):
    numero = numero_lote or f"SIN-LOTE-{producto_id}"
    lote = ProductoLote.query.filter_by(
        producto_id=producto_id,
        numero_lote=numero,
        proveedor_id=proveedor_id,
    ).first()
    if not lote:
        lote = ProductoLote(
            producto_id=producto_id,
            presentacion_id=presentacion_id,
            proveedor_id=proveedor_id,
            numero_lote=numero,
            fecha_vencimiento=fecha_vencimiento,
            cantidad_actual=0,
        )
        db.session.add(lote)
    elif fecha_vencimiento and not lote.fecha_vencimiento:
        lote.fecha_vencimiento = fecha_vencimiento
    return lote


def registrar_movimiento_recepcion(recepcion, lote, cantidad, costo):
    movimiento = InventarioMovimiento(
        tipo="RECIBO",
        fecha=recepcion.fecha,
        producto_id=lote.producto_id,
        lote=lote,
        presentacion_id=lote.presentacion_id,
        proveedor_id=recepcion.proveedor_id,
        cantidad=cantidad,
        costo_unitario=costo,
        documento=recepcion.documento or recepcion.numero,
        responsable=recepcion.responsable,
        observaciones=recepcion.observaciones,
    )
    db.session.add(movimiento)


def actualizar_producto_proveedor(producto_id, proveedor_id, costo, detalle_pedido=None):
    relacion = ProductoProveedor.query.filter_by(
        producto_id=producto_id,
        proveedor_id=proveedor_id,
    ).first()
    if not relacion:
        relacion = ProductoProveedor(
            producto_id=producto_id,
            proveedor_id=proveedor_id,
            origen="compras",
        )
        db.session.add(relacion)
    if detalle_pedido and detalle_pedido.referencia_proveedor:
        relacion.referencia_proveedor = detalle_pedido.referencia_proveedor
    if detalle_pedido and detalle_pedido.presentacion:
        relacion.presentacion = detalle_pedido.presentacion.nombre
    if costo:
        relacion.precio_compra = costo
        relacion.ultimo_precio_compra = costo
    relacion.ultima_compra_en = datetime.utcnow().date()
    relacion.es_frecuente = True


def render_template_movimiento(movimiento, modo):
    return render_template(
        "inventario/form.html",
        movimiento=movimiento,
        modo=modo,
        lotes=obtener_lotes(),
        proveedores=obtener_proveedores(),
        clientes=obtener_clientes(),
    )


def render_template_pedido(pedido, modo):
    return render_template(
        "compras/pedidos/form.html",
        pedido=pedido,
        modo=modo,
        proveedores=obtener_proveedores(),
        productos=obtener_productos(),
        presentaciones=obtener_presentaciones(),
        estados=["BORRADOR", "CONFIRMADO", "PARCIAL", "CERRADO"],
    )


def render_template_solicitud(solicitud, modo):
    return render_template(
        "compras/solicitudes/form.html",
        solicitud=solicitud,
        modo=modo,
        proveedores=obtener_proveedores(),
        productos=obtener_productos(),
        presentaciones=obtener_presentaciones(),
        estados=["BORRADOR", "ENVIADA", "RESPONDIDA", "FINALIZADA", "CANCELADA"],
    )


def render_template_cotizacion(cotizacion, modo):
    return render_template(
        "compras/cotizaciones/form.html",
        cotizacion=cotizacion,
        modo=modo,
        proveedores=obtener_proveedores(),
        productos=obtener_productos(),
        presentaciones=obtener_presentaciones(),
        estados=["BORRADOR", "SOLICITADA", "RECIBIDA", "PARCIAL", "CERRADA", "CANCELADA"],
        cantidad_pendiente_cotizacion=cantidad_pendiente_cotizacion,
    )


def render_template_convertir_cotizacion(cotizacion, pedido):
    return render_template(
        "compras/cotizaciones/convertir.html",
        cotizacion=cotizacion,
        pedido=pedido,
        cantidad_pendiente_cotizacion=cantidad_pendiente_cotizacion,
    )


def render_template_recepcion(recepcion, modo, pedido=None):
    return render_template(
        "compras/recepciones/form.html",
        recepcion=recepcion,
        pedido=pedido,
        modo=modo,
        proveedores=obtener_proveedores(),
        productos=obtener_productos(),
        presentaciones=obtener_presentaciones(),
        cantidad_pendiente=cantidad_pendiente,
    )


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


def obtener_clientes():
    return Cliente.query.filter_by(activo=True).order_by(Cliente.nombre.asc()).all()


def obtener_lotes():
    return ProductoLote.query.filter_by(activo=True).join(Producto).order_by(
        Producto.nombre.asc(),
        ProductoLote.numero_lote.asc(),
    ).all()


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
