import sys
from pathlib import Path

from sqlalchemy import text

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from app import create_app
from app.extensions import db
from app.models import Unidad


def add_column_if_missing(table_name, column_name, definition):
    exists_sql = text(
        """
        select 1
        from information_schema.columns
        where table_name = :table_name
          and column_name = :column_name
        """
    )
    alter_sql = text(f"alter table {table_name} add column {column_name} {definition}")

    exists = db.session.execute(
        exists_sql, {"table_name": table_name, "column_name": column_name}
    ).scalar()
    if not exists:
        db.session.execute(alter_sql)
        print(f"Columna agregada: {table_name}.{column_name}")


def main():
    app = create_app()
    with app.app_context():
        db.create_all()
        add_column_if_missing("productos", "maneja_lotes", "boolean not null default false")
        add_column_if_missing(
            "productos", "maneja_presentaciones", "boolean not null default false"
        )
        add_column_if_missing("productos", "unidad_id", "integer references unidades(id)")
        add_column_if_missing("producto_proveedores", "ultima_compra_en", "date")
        add_column_if_missing("producto_proveedores", "ultimo_precio_compra", "numeric(14, 2)")
        add_column_if_missing("producto_proveedores", "origen", "varchar(30) not null default 'manual'")
        seed_unidades()
        db.session.commit()
        print("Esquema actualizado.")


def seed_unidades():
    unidades = [
        ("Unidad", "und"),
        ("Caja", "cja"),
        ("Paquete", "paq"),
        ("Kilogramo", "kg"),
        ("Gramo", "g"),
        ("Litro", "l"),
        ("Mililitro", "ml"),
        ("Metro", "m"),
        ("Centimetro", "cm"),
        ("Docena", "doc"),
    ]
    for nombre, abreviatura in unidades:
        existe = Unidad.query.filter_by(abreviatura=abreviatura).first()
        if not existe:
            db.session.add(Unidad(nombre=nombre, abreviatura=abreviatura))
            print(f"Unidad creada: {nombre}")


if __name__ == "__main__":
    main()
