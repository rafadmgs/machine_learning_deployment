
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
