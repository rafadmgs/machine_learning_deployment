import runpy
import os
import subprocess
import sys

import pytest

from src import create_tables


@pytest.fixture(autouse=True)
def development_environment(monkeypatch):
    """Configure l'environnement de test pour la création des tables."""
    monkeypatch.setenv("APP_ENV", "development")


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


def test_create_tables_rejects_production(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")

    with pytest.raises(RuntimeError):
        create_tables.create_tables()


def test_create_tables_rejects_missing_environment(monkeypatch):
    monkeypatch.delenv("APP_ENV", raising=False)

    with pytest.raises(RuntimeError):
        create_tables.create_tables()


def test_script_execution(monkeypatch):
    env = os.environ.copy()
    env["APP_ENV"] = "development"

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

def test_main_guard_executes_create_tables(monkeypatch):
    calls = []

    monkeypatch.setattr(
        create_tables.Base.metadata,
        "create_all",
        lambda bind: calls.append(bind),
    )

    runpy.run_path(
        "src/create_tables.py",
        run_name="__main__",
    )

    assert calls == [create_tables.engine]