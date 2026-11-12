
import os
import subprocess
import sys

import pytest

from src import create_tables


def test_create_tables_calls_metadata_create_all(monkeypatch):
    monkeypatch.setenv("APP_ENV", "development")

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
    monkeypatch.setenv("APP_ENV", "development")

    monkeypatch.setattr(
        create_tables.Base.metadata,
        "create_all",
        lambda bind: None,
    )

    create_tables.create_tables()

    output = capsys.readouterr().out

    assert "Tabelas criadas ou já existentes." in output


def test_create_tables_prints_table_names(capsys, monkeypatch):
    monkeypatch.setenv("APP_ENV", "development")

    monkeypatch.setattr(
        create_tables.Base.metadata,
        "create_all",
        lambda bind: None,
    )

    create_tables.create_tables()

    output = capsys.readouterr().out

    for table_name in create_tables.Base.metadata.tables:
        assert f"- {table_name}" in output


def test_create_tables_rejects_production(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")

    with pytest.raises(RuntimeError):
        create_tables.create_tables()


def test_script_execution():
    test_database_url = os.getenv("TEST_DATABASE_URL")

    if not test_database_url:
        pytest.skip("TEST_DATABASE_URL n'est pas configurée.")

    env = os.environ.copy()
    env["DATABASE_URL"] = test_database_url
    env["APP_ENV"] = "test"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.create_tables",
        ],
        capture_output=True,
        text=True,
        timeout=30,
        env=env,
    )

    assert result.returncode == 0, result.stderr
    assert "Tabelas criadas ou já existentes." in result.stdout
