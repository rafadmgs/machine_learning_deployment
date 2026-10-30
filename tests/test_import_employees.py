
import pandas as pd
import pytest

from src import import_employees
import runpy
import sys

from pathlib import Path

@pytest.fixture
def csv_environment(tmp_path, monkeypatch):
    project_root = tmp_path
    src_dir = project_root / "src"
    data_dir = project_root / "data" / "processed"

    src_dir.mkdir()
    data_dir.mkdir(parents=True)

    monkeypatch.setattr(
        import_employees,
        "__file__",
        str(src_dir / "import_employees.py"),
    )

    return data_dir / "df_central.csv"


def test_main_raises_error_when_csv_is_missing(csv_environment):
    with pytest.raises(FileNotFoundError, match="CSV introuvable"):
        import_employees.main()


def test_main_rejects_incompatible_columns(
    csv_environment, monkeypatch
):
    pd.DataFrame({
        "id_employee": [1],
        "wrong_column": [25],
    }).to_csv(csv_environment, index=False)

    monkeypatch.setattr(
        import_employees,
        "inspect",
        lambda engine: type(
            "FakeInspector",
            (),
            {
                "get_columns": lambda self, table: [
                    {"name": "id_employee"},
                    {"name": "age"},
                ]
            },
        )(),
    )

    with pytest.raises(ValueError, match="Colonnes incompatibles"):
        import_employees.main()


def test_main_rejects_duplicate_employee_ids(
    csv_environment, monkeypatch
):
    pd.DataFrame({
        "id_employee": [1, 1],
        "age": [25, 30],
    }).to_csv(csv_environment, index=False)

    monkeypatch.setattr(
        import_employees,
        "inspect",
        lambda engine: type(
            "FakeInspector",
            (),
            {
                "get_columns": lambda self, table: [
                    {"name": "id_employee"},
                    {"name": "age"},
                ]
            },
        )(),
    )

    with pytest.raises(
        ValueError,
        match="IDs employés en double",
    ):
        import_employees.main()


def test_main_rejects_missing_values(
    csv_environment, monkeypatch
):
    pd.DataFrame({
        "id_employee": [1],
        "age": [None],
    }).to_csv(csv_environment, index=False)

    monkeypatch.setattr(
        import_employees,
        "inspect",
        lambda engine: type(
            "FakeInspector",
            (),
            {
                "get_columns": lambda self, table: [
                    {"name": "id_employee"},
                    {"name": "age"},
                ]
            },
        )(),
    )

    with pytest.raises(
        ValueError,
        match="valeurs manquantes",
    ):
        import_employees.main()


def test_main_rejects_missing_employee_id(
    csv_environment, monkeypatch
):
    pd.DataFrame({
        "id_employee": [None],
        "age": [25],
    }).to_csv(csv_environment, index=False)

    monkeypatch.setattr(
        import_employees,
        "inspect",
        lambda engine: type(
            "FakeInspector",
            (),
            {
                "get_columns": lambda self, table: [
                    {"name": "id_employee"},
                    {"name": "age"},
                ]
            },
        )(),
    )

    with pytest.raises(
        ValueError,
        match="IDs employés manquants",
    ):
        import_employees.main()


def test_main_skips_import_when_employees_already_exist(
    csv_environment, monkeypatch, capsys
):
    pd.DataFrame({
        "id_employee": [1],
        "age": [25],
    }).to_csv(csv_environment, index=False)

    monkeypatch.setattr(
        import_employees,
        "inspect",
        lambda engine: type(
            "FakeInspector",
            (),
            {
                "get_columns": lambda self, table: [
                    {"name": "id_employee"},
                    {"name": "age"},
                ]
            },
        )(),
    )

    class FakeSession:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            return False

        def scalar(self, query):
            return 3

        def add_all(self, records):
            pytest.fail("A importação não deveria adicionar registros.")

        def commit(self):
            pytest.fail("A transação não deveria ser confirmada.")

    monkeypatch.setattr(import_employees, "Session", lambda engine: FakeSession())

    import_employees.main()

    output = capsys.readouterr().out
    assert "3" in output
    assert "Aucune donnée n'a été modifiée." in output


def test_main_imports_employees_successfully(
    csv_environment, monkeypatch
):
    pd.DataFrame({
        "id_employee": [1, 2],
        "age": [25, 30],
    }).to_csv(csv_environment, index=False)

    monkeypatch.setattr(
        import_employees,
        "inspect",
        lambda engine: type(
            "FakeInspector",
            (),
            {
                "get_columns": lambda self, table: [
                    {"name": "id_employee"},
                    {"name": "age"},
                ]
            },
        )(),
    )

    class FakeSession:
        def __init__(self):
            self.added_records = []
            self.committed = False

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            return False

        def scalar(self, query):
            if not self.committed:
                return 0
            return len(self.added_records)

        def add_all(self, records):
            self.added_records.extend(records)

        def commit(self):
            self.committed = True

    fake_session = FakeSession()

    monkeypatch.setattr(
        import_employees,
        "Session",
        lambda engine: fake_session,
    )

    import_employees.main()

    assert len(fake_session.added_records) == 2
    assert fake_session.committed is True



def test_script_execution_with_mocked_dependencies(
    monkeypatch
):
    import runpy
    import sqlalchemy
    import sqlalchemy.orm
    from pathlib import Path
    from src.models import Employee

    script_path = Path(import_employees.__file__)

    # Cria um DataFrame com as colunas reais do modelo.
    columns = [
        column.name
        for column in Employee.__table__.columns
    ]

    records = {
        column: [999999 if column == "id_employee" else 1]
        for column in columns
    }

    dataframe = pd.DataFrame(records)

    # Simula a leitura do CSV.
    monkeypatch.setattr(
        pd,
        "read_csv",
        lambda path: dataframe,
    )

    # Simula a existência do arquivo CSV.
    original_exists = Path.exists

    def fake_exists(path):
        if str(path).endswith("df_central.csv"):
            return True
        return original_exists(path)

    monkeypatch.setattr(Path, "exists", fake_exists)

    # Simula as colunas existentes no PostgreSQL.
    class FakeInspector:
        def get_columns(self, table):
            return [{"name": column} for column in columns]

    monkeypatch.setattr(
        sqlalchemy,
        "inspect",
        lambda engine: FakeInspector(),
    )

    # Simula a sessão do banco.
    class FakeSession:
        def __init__(self):
            self.added_records = []
            self.committed = False

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            return False

        def scalar(self, query):
            if not self.committed:
                return 0
            return len(self.added_records)

        def add_all(self, records):
            self.added_records.extend(records)

        def commit(self):
            self.committed = True

    fake_session = FakeSession()

    monkeypatch.setattr(
        sqlalchemy.orm,
        "Session",
        lambda engine: fake_session,
    )

    # Executa o arquivo original como script.
    runpy.run_path(
        str(script_path),
        run_name="__main__",
    )

    assert len(fake_session.added_records) == 1
    assert fake_session.committed is True
