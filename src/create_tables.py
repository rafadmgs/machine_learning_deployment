
import os

from src.database import Base, engine
from src import models


def create_tables():
    """Crée les tables uniquement dans les environnements DEV et TEST."""
    app_env = os.getenv("APP_ENV", "").lower()

    if app_env not in {"development", "test"}:
        raise RuntimeError(
            "La création des tables est interdite dans cet environnement."
        )

    Base.metadata.create_all(bind=engine)
    print("Tabelas criadas ou já existentes.")

    for table_name in Base.metadata.tables:
        print(f"- {table_name}")


if __name__ == "__main__":
    create_tables()
