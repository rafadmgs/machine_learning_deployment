
import json

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from src.main import app
from src.models import Employee, PredictionInput, PredictionOutput


@pytest.fixture
def api_key(monkeypatch):
    """Configure une clé API de test."""
    from src import main

    monkeypatch.setattr(main, "API_KEY", "test-api-key")

    return {"X-API-Key": "test-api-key"}


@pytest.fixture
def client(api_key):
    """Initialise l'API avec les vrais artefacts du modèle."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def test_employee(test_db):
    """Récupère un employé réel dans la base PostgreSQL de test."""

    employee = test_db.execute(
        select(Employee).limit(1)
    ).scalars().first()

    if employee is None:
        pytest.skip("Aucun employé disponible dans la base de test.")

    return employee.id_employee


def test_root_endpoint(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["docs"] == "/docs"
    assert "HR Analytics API" in response.json()["message"]


def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_predict_rejects_missing_api_key(client, test_employee):
    response = client.post(
        "/predict",
        json={"id_employee": test_employee},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == (
        "Clé API invalide ou manquante."
    )


def test_predict_rejects_invalid_api_key(client, test_employee):
    response = client.post(
        "/predict",
        json={"id_employee": test_employee},
        headers={"X-API-Key": "wrong-api-key"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == (
        "Clé API invalide ou manquante."
    )


def test_predict_rejects_unconfigured_api_key(
    client,
    test_employee,
    monkeypatch,
):
    from src import main

    monkeypatch.setattr(main, "API_KEY", None)

    response = client.post(
        "/predict",
        json={"id_employee": test_employee},
        headers={"X-API-Key": "test-api-key"},
    )

    assert response.status_code == 500
    assert response.json()["detail"] == (
        "La clé API n'est pas configurée."
    )


def test_predict_rejects_empty_body(client, api_key):
    response = client.post(
        "/predict",
        json={},
        headers=api_key,
    )

    assert response.status_code == 422


def test_predict_rejects_invalid_employee_id(client, api_key):
    response = client.post(
        "/predict",
        json={"id_employee": "identifiant_invalide"},
        headers=api_key,
    )

    assert response.status_code == 422


def test_predict_rejects_non_positive_employee_id(client, api_key):
    response = client.post(
        "/predict",
        json={"id_employee": 0},
        headers=api_key,
    )

    assert response.status_code == 422


def test_predict_rejects_unknown_employee(client, api_key, test_db):
    """Vérifie le comportement pour un employé inexistant."""

    employee_id = (
        test_db.query(Employee.id_employee)
        .order_by(Employee.id_employee.desc())
        .first()[0] + 1000000
    )

    response = client.post(
        "/predict",
        json={"id_employee": employee_id},
        headers=api_key,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Employé introuvable."


def test_predict_success(client, test_employee, api_key, test_db):
    """Teste une prédiction réelle avec PostgreSQL et le modèle P4."""

    response = client.post(
        "/predict",
        json={"id_employee": test_employee},
        headers=api_key,
    )

    assert response.status_code == 200, response.text

    result = response.json()

    assert result["employee_id"] == test_employee
    assert isinstance(result["prediction_id"], int)
    assert result["prediction"] in ["Oui", "Non"]
    assert 0 <= result["probability"] <= 100

    assert result["message"] in [
        "Le modèle prédit un départ.",
        "Le modèle prédit un maintien.",
    ]

    assert result["inference_time_ms"] >= 0
    assert result["model_version"] == "1.0.0"

    explainability = result["explainability"]

    assert explainability["method"] == (
        "Régression logistique - contributions locales des coefficients"
    )

    factors = explainability["top_factors"]

    assert len(factors) <= 3

    for factor in factors:
        assert isinstance(factor["feature"], str)
        assert factor["impact"] in ["positive", "negative"]
        assert isinstance(factor["contribution"], (int, float))

    prediction_output = None

    try:
        prediction_output = test_db.execute(
            select(PredictionOutput).where(
                PredictionOutput.id == result["prediction_id"]
            )
        ).scalars().first()

        assert prediction_output is not None
        assert prediction_output.prediction in ["Oui", "Non"]

        prediction_input = test_db.execute(
            select(PredictionInput).where(
                PredictionInput.id == prediction_output.prediction_input_id
            )
        ).scalars().first()

        assert prediction_input is not None
        assert prediction_input.employee_id == test_employee

        saved_data = json.loads(prediction_input.input_data)

        assert len(saved_data) == 25
        assert "age" in saved_data
        assert "genre" in saved_data
        assert "a_quitte_l_entreprise" not in saved_data

        assert prediction_output.probability == pytest.approx(
            result["probability"] / 100
        )

    finally:
        # Suppression dans l'ordre des dépendances de clés étrangères.
        if prediction_output is not None:
            test_db.execute(
                delete(PredictionOutput).where(
                    PredictionOutput.id == result["prediction_id"]
                )
            )

            test_db.execute(
                delete(PredictionInput).where(
                    PredictionInput.id == prediction_output.prediction_input_id
                )
            )

            test_db.commit()


def test_predict_handles_unexpected_error(
    client,
    test_employee,
    api_key,
    monkeypatch,
):
    def fake_transform(*args, **kwargs):
        raise RuntimeError("Erreur simulée pour le test.")

    monkeypatch.setattr(
        client.app.state.preprocessor,
        "transform",
        fake_transform,
    )

    response = client.post(
        "/predict",
        json={"id_employee": test_employee},
        headers=api_key,
    )

    assert response.status_code == 500
    assert response.json()["detail"] == (
        "Une erreur interne est survenue lors de la prédiction."
    )


def test_lifespan_loads_artifacts_only_once(monkeypatch):
    from src import main

    fake_model = object()
    fake_preprocessor = object()
    load_calls = []

    def fake_load_artifacts():
        load_calls.append(1)
        return fake_model, fake_preprocessor

    monkeypatch.setattr(
        main,
        "load_artifacts",
        fake_load_artifacts,
    )

    with TestClient(app):
        assert app.state.model is fake_model
        assert app.state.preprocessor is fake_preprocessor

    assert len(load_calls) == 1


def test_load_artifacts(monkeypatch):
    from src import main

    fake_model = object()
    fake_preprocessor = object()
    loaded_paths = []

    def fake_joblib_load(path):
        loaded_paths.append(path)

        if path.name == "lr_optimise.joblib":
            return fake_model

        if path.name == "preprocessor.joblib":
            return fake_preprocessor

        raise AssertionError(f"Chemin inattendu : {path}")

    monkeypatch.setattr(main.joblib, "load", fake_joblib_load)

    model, preprocessor = main.load_artifacts()

    assert model is fake_model
    assert preprocessor is fake_preprocessor

    assert loaded_paths == [
        main.MODEL_DIR / "lr_optimise.joblib",
        main.MODEL_DIR / "preprocessor.joblib",
    ]
