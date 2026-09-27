from flask import Blueprint, render_template

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def dashboard():
    indicadores = [
        {"titulo": "Cotizaciones abiertas", "valor": "0", "detalle": "Pendientes por confirmar"},
        {"titulo": "Cuentas por cobrar", "valor": "$0", "detalle": "Cartera vigente y vencida"},
        {"titulo": "Cuentas por pagar", "valor": "$0", "detalle": "Compromisos con proveedores"},
        {"titulo": "Inventario crítico", "valor": "0", "detalle": "Productos bajo mínimo o por vencer"},
    ]

    accesos = [
        {"nombre": "Productos", "icono": "box", "clase": "products"},
        {"nombre": "Proveedores", "icono": "truck", "clase": "suppliers"},
        {"nombre": "Cotizaciones", "icono": "quote", "clase": "quotes"},
        {"nombre": "Cartera", "icono": "wallet", "clase": "wallet"},
    ]

    return render_template("dashboard.html", indicadores=indicadores, accesos=accesos)


@main_bp.route("/login")
def login():
    return render_template("login.html")
