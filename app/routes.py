from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from sqlalchemy import or_

from .extensions import db
from .models import Auditoria, Cliente

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
        {"nombre": "Productos", "icono": "box", "clase": "products"},
        {"nombre": "Clientes", "icono": "client", "clase": "clients", "url": "main.clientes"},
        {"nombre": "Proveedores", "icono": "truck", "clase": "suppliers"},
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


def guardar_cliente(cliente):
    cliente.nombre = request.form.get("nombre", "").strip()
    cliente.documento = request.form.get("documento", "").strip() or None
    cliente.contacto = request.form.get("contacto", "").strip() or None
    cliente.telefono = request.form.get("telefono", "").strip() or None
    cliente.email = request.form.get("email", "").strip() or None
    cliente.ciudad = request.form.get("ciudad", "").strip() or None
    cliente.direccion = request.form.get("direccion", "").strip() or None
    cliente.notas = request.form.get("notas", "").strip() or None


def registrar_auditoria(tabla, registro_id, accion, detalle):
    db.session.add(
        Auditoria(tabla=tabla, registro_id=registro_id, accion=accion, detalle=detalle)
    )
    db.session.commit()
