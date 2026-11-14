
import os
import subprocess
import sys
from pathlib import Path


def test_database_url_missing_raises_runtime_error():
    project_root = Path(__file__).resolve().parent.parent

    # Simula a ausência da variável, sem alterar o ambiente principal.
    env = os.environ.copy()
    env["DATABASE_URL"] = ""

    result = subprocess.run(
        [sys.executable, "-c", "import src.database"],
        cwd=project_root,
        env=env,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "RuntimeError" in result.stderr
    assert "DATABASE_URL" in result.stderr

def test_database_url_missing_is_covered(monkeypatch):
    import importlib
    import os
    import pytest
    import src.database as database

    monkeypatch.setenv("DATABASE_URL", "")

    with pytest.raises(
        RuntimeError,
        match="DATABASE_URL não encontrada"
    ):
        importlib.reload(database)

def test_get_db_creates_and_closes_session():
    """Vérifie la création et la fermeture de la session DB."""

    from unittest.mock import MagicMock, patch

    from src.database import get_db

    mock_session = MagicMock()

    with patch(
        "src.database.SessionLocal",
        return_value=mock_session,
    ):
        db_generator = get_db()

        db = next(db_generator)

        assert db is mock_session

        try:
            next(db_generator)
        except StopIteration:
            pass

        mock_session.close.assert_called_once()