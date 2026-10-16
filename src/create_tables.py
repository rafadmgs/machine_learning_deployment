
from src.database import Base, engine
from src import models


def create_tables():
    Base.metadata.create_all(bind=engine)
    print("Tabelas criadas ou já existentes.")

    for table_name in Base.metadata.tables:
        print(f"- {table_name}")


if __name__ == "__main__":
    create_tables()
