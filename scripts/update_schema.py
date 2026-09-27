import sys
from pathlib import Path

from sqlalchemy import text

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from app import create_app
from app.extensions import db


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
        add_column_if_missing("productos", "maneja_lotes", "boolean not null default false")
        add_column_if_missing(
            "productos", "maneja_presentaciones", "boolean not null default false"
        )
        db.session.commit()
        print("Esquema actualizado.")


if __name__ == "__main__":
    main()
