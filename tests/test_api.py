
import json

import pytest
from fastapi.testclient import TestClient

from src.database import get_db
from src.main import app
from src.models import Employee, PredictionInput, PredictionOutput


FEATURE_NAMES = [
    "age",
    "genre",
    "revenu_mensuel",
    "statut_marital",
    "departement",
    "poste",
    "nombre_experiences_precedentes",
    "annee_experience_totale",
    "annees_dans_l_entreprise",
    "satisfaction_employee_environnement",
    "note_evaluation_precedente",
    "niveau_hierarchique_poste",
    "satisfaction_employee_nature_travail",
    "satisfaction_employee_equipe",
    "satisfaction_employee_equilibre_pro_perso",
    "note_evaluation_actuelle",
    "heure_supplementaires",
    "augementation_salaire_precedente",
    "nombre_participation_pee",
    "nb_formations_suivies",
    "distance_domicile_travail",
    "niveau_education",
    "domaine_etude",
    "frequence_deplacement",
    "annees_depuis_la_derniere_promotion",
]


class FakeEmployee:
    """Simule un employé enregistré dans la base de données."""

    id_employee = 123

    age = 35
    genre = "M"
    revenu_mensuel = 5000
    statut_marital = "Célibataire"
    departement = "Consulting"
    poste = "Consultant"
    nombre_experiences_precedentes = 2
    annee_experience_totale = 10
    annees_dans_l_entreprise = 4
    satisfaction_employee_environnement = 3
    note_evaluation_precedente = 3
    niveau_hierarchique_poste = 2
    satisfaction_employee_nature_travail = 3
    satisfaction_employee_equipe = 3
    satisfaction_employee_equilibre_pro_perso = 3
    note_evaluation_actuelle = 3
    heure_supplementaires = "Non"
    augementation_salaire_precedente = 15
    nombre_participation_pee = 1
    nb_formations_suivies = 2
    distance_domicile_travail = 10
    niveau_education = 3
    domaine_etude = "Marketing"
    frequence_deplacement = "Occasionnel"
    annees_depuis_la_derniere_promotion = 1


class FakePreprocessor:
    """Simule le prétraitement des données."""

    feature_names_in_ = FEATURE_NAMES

    def transform(self, input_df):
        assert list(input_df.columns) == FEATURE_NAMES
        return [[0]]

    def get_feature_names_out(self):
        return ["feature"]


class FakeModel:
    """Simule le modèle de prédiction."""

    classes_ = ["Non", "Oui"]

    def predict(self, transformed_df):
        return ["Oui"]

    def predict_proba(self, transformed_df):
        return [[0.2, 0.8]]


class FakeDB:
    """Simule une session SQLAlchemy sans accès à Neon."""

    def __init__(self):
        self.added_objects = []
        self.next_input_id = 1
        self.next_output_id = 1
        self.committed = False
        self.rolled_back = False
        self.employee = FakeEmployee()

    def get(self, model, employee_id):
        if model is Employee and employee_id == self.employee.id_employee:
            return self.employee

        return None

    def add(self, obj):
        self.added_objects.append(obj)

        if isinstance(obj, PredictionInput):
            obj.id = self.next_input_id
            self.next_input_id += 1

        elif isinstance(obj, PredictionOutput):
            obj.id = self.next_output_id
            self.next_output_id += 1

    def flush(self):
        pass

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True


@pytest.fixture
def payload():
    """Identifiant valide pour une demande de prédiction."""

    return {"id_employee": 123}


@pytest.fixture
def api_key(monkeypatch):
    """Configure une clé API de test."""

    from src import main

    monkeypatch.setattr(main, "API_KEY", "test-api-key")

    return {"X-API-Key": "test-api-key"}


@pytest.fixture
def fake_db():
    """Fournit une session de base de données simulée."""

    db = FakeDB()

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    yield db

    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def client(monkeypatch, api_key):
    """Initialise l'API avec des artefacts simulés."""

    from src import main

    monkeypatch.setattr(
        main,
        "load_artifacts",
        lambda: (FakeModel(), FakePreprocessor()),
    )

    with TestClient(app) as test_client:
        yield test_client


def test_root_endpoint(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["docs"] == "/docs"
    assert "HR Analytics API" in response.json()["message"]


def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_predict_rejects_missing_api_key(client, payload):
    response = client.post("/predict", json=payload)

    assert response.status_code == 401
    assert response.json()["detail"] == (
        "Clé API invalide ou manquante."
    )


def test_predict_rejects_invalid_api_key(client, payload):
    response = client.post(
        "/predict",
        json=payload,
        headers={"X-API-Key": "wrong-api-key"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == (
        "Clé API invalide ou manquante."
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


def test_predict_rejects_unknown_employee(
    client,
    fake_db,
    api_key,
):
    response = client.post(
        "/predict",
        json={"id_employee": 999},
        headers=api_key,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Employé introuvable."
    assert fake_db.rolled_back is True
    assert fake_db.added_objects == []


def test_predict_success(client, payload, fake_db, api_key):
    response = client.post(
        "/predict",
        json=payload,
        headers=api_key,
    )

    assert response.status_code == 200, response.text

    result = response.json()

    assert result["employee_id"] == 123
    assert result["prediction_id"] == 1
    assert result["prediction"] == "Oui"
    assert result["probability"] == pytest.approx(0.8)
    assert result["message"] == "Le modèle prédit un départ."

    assert fake_db.committed is True
    assert fake_db.rolled_back is False
    assert len(fake_db.added_objects) == 2

    saved_input = fake_db.added_objects[0]
    saved_output = fake_db.added_objects[1]

    assert isinstance(saved_input, PredictionInput)
    assert isinstance(saved_output, PredictionOutput)

    assert saved_input.employee_id == 123
    assert saved_output.prediction_input_id == saved_input.id

    saved_data = json.loads(saved_input.input_data)

    assert len(saved_data) == 25
    assert saved_data["age"] == 35
    assert saved_data["genre"] == "M"
    assert "a_quitte_l_entreprise" not in saved_data


def test_predict_rolls_back_on_database_error(
    client,
    payload,
    fake_db,
    api_key,
):
    def failing_commit():
        raise RuntimeError("database failure")

    fake_db.commit = failing_commit

    response = client.post(
        "/predict",
        json=payload,
        headers=api_key,
    )

    assert response.status_code == 500
    assert response.json()["detail"] == (
        "Une erreur interne est survenue lors de la prédiction."
    )
    assert fake_db.rolled_back is True
    assert fake_db.committed is False


def test_lifespan_loads_artifacts_only_once(monkeypatch):
    from src import main

    fake_model = FakeModel()
    fake_preprocessor = FakePreprocessor()
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
