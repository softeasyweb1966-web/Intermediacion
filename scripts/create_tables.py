import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from app import create_app
from app.extensions import db


def main():
    app = create_app()
    with app.app_context():
        db.create_all()
        print("Tablas iniciales creadas o verificadas.")


if __name__ == "__main__":
    main()
