from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_project_structure():
    expected_directories = [
        "data",
        "data/raw",
        "data/processed",
        "notebooks",
        "output",
        "presentation",
        "src",
        "tests",
    ]

    for directory in expected_directories:
        assert (PROJECT_ROOT / directory).is_dir()