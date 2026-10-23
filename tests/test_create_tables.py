
from src import create_tables


def test_create_tables_calls_metadata_create_all(monkeypatch):
    calls = []

    def fake_create_all(bind):
        calls.append(bind)

    monkeypatch.setattr(
        create_tables.Base.metadata,
        "create_all",
        fake_create_all,
    )

    create_tables.create_tables()

    assert calls == [create_tables.engine]


def test_create_tables_prints_confirmation(capsys, monkeypatch):
    monkeypatch.setattr(
        create_tables.Base.metadata,
        "create_all",
        lambda bind: None,
    )

    create_tables.create_tables()

    output = capsys.readouterr().out

    assert "Tabelas criadas ou já existentes." in output


def test_create_tables_prints_table_names(capsys, monkeypatch):
    monkeypatch.setattr(
        create_tables.Base.metadata,
        "create_all",
        lambda bind: None,
    )

    create_tables.create_tables()

    output = capsys.readouterr().out

    for table_name in create_tables.Base.metadata.tables:
        assert f"- {table_name}" in output
