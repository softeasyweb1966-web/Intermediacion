import sys
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from app.config import Config


def main():
    target_url = make_url(Config.SQLALCHEMY_DATABASE_URI)
    db_name = target_url.database
    admin_url = target_url.set(database="postgres")

    engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
    with engine.connect() as conn:
        exists = conn.execute(
            text("select 1 from pg_database where datname = :name"), {"name": db_name}
        ).scalar()
        if not exists:
            conn.execute(text(f'create database "{db_name}" encoding \'UTF8\''))
            print(f"Base de datos creada: {db_name}")
        else:
            print(f"La base de datos ya existe: {db_name}")


if __name__ == "__main__":
    main()
