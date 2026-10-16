
from pathlib import Path

import pandas as pd
from sqlalchemy import inspect, select, func
from sqlalchemy.orm import Session

from src.database import engine
from src.models import Employee


def main():
    project_root = Path(__file__).resolve().parent.parent
    csv_path = project_root / "data" / "processed" / "df_central.csv"

    if not csv_path.exists():
        raise FileNotFoundError(f"CSV introuvable : {csv_path}")

    df = pd.read_csv(csv_path)

    inspector = inspect(engine)
    database_columns = {
        column["name"]
        for column in inspector.get_columns("employees")
    }

    csv_columns = set(df.columns)

    missing_columns = database_columns - csv_columns
    extra_columns = csv_columns - database_columns

    if missing_columns or extra_columns:
        raise ValueError(
            f"Colonnes incompatibles. Manquantes : {missing_columns}; "
            f"supplémentaires : {extra_columns}"
        )

    if df["id_employee"].duplicated().any():
        raise ValueError("Le CSV contient des IDs employés en double.")

    if df["id_employee"].isna().any():
        raise ValueError("Le CSV contient des IDs employés manquants.")

    if df.isna().any().any():
        raise ValueError("Le CSV contient des valeurs manquantes.")

    with Session(engine) as session:
        existing_count = session.scalar(
            select(func.count()).select_from(Employee)
        )

        if existing_count > 0:
            print(
                f"Importation annulée : la table employees contient déjà "
                f"{existing_count} enregistrement(s)."
            )
            print("Aucune donnée n'a été modifiée.")
            return

        records = df.to_dict(orient="records")
        session.add_all([Employee(**record) for record in records])
        session.commit()

        final_count = session.scalar(
            select(func.count()).select_from(Employee)
        )

        print(f"Importation terminée : {final_count} employés dans employees.")


if __name__ == "__main__":
    main()
