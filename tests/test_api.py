
from urllib import response

from fastapi.testclient import TestClient

from src.database import get_db
from src.main import app
from src.models import PredictionInput, PredictionOutput


class FakeDB:
    """Simule une session SQLAlchemy sans accès à Neon."""

    def __init__(self):
        self.added_objects = []
        self.next_input_id = 1
        self.next_output_id = 1
        self.committed = False
        self.rolled_back = False

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


client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["docs"] == "/docs"
    assert "HR Analytics API" in response.json()["message"]


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_predict_rejects_empty_body():
    response = client.post("/predict", json={})

    assert response.status_code == 422


def test_predict_rejects_invalid_field_type():
    response = client.post(
        "/predict",
        json={"age": "idade_invalida"},
    )

    assert response.status_code == 422


def test_predict_success():
    fake_db = FakeDB()

    def override_get_db():
        yield fake_db

    app.dependency_overrides[get_db] = override_get_db

    payload = {
        "age": 35,
        "genre": "M",
        "revenu_mensuel": 5000,
        "statut_marital": "Célibataire",
        "departement": "Consulting",
        "poste": "Consultant",
        "nombre_experiences_precedentes": 2,
        "annee_experience_totale": 10,
        "annees_dans_l_entreprise": 4,
        "satisfaction_employee_environnement": 3,
        "note_evaluation_precedente": 3,
        "niveau_hierarchique_poste": 2,
        "satisfaction_employee_nature_travail": 3,
        "satisfaction_employee_equipe": 3,
        "satisfaction_employee_equilibre_pro_perso": 3,
        "note_evaluation_actuelle": 3,
        "heure_supplementaires": "Non",
        "augementation_salaire_precedente": 15,
        "nombre_participation_pee": 1,
        "nb_formations_suivies": 2,
        "distance_domicile_travail": 10,
        "niveau_education": 3,
        "domaine_etude": "Marketing",
        "frequence_deplacement": "Occasionnel",
        "annees_depuis_la_derniere_promotion": 1,
    }

    try:
        response = client.post("/predict", json=payload)
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200, response.text

    result = response.json()

    assert result["prediction_id"] == 1
    assert result["prediction"] in ["Oui", "Non"]
    assert 0 <= result["probability"] <= 1
    assert "message" in result

    assert fake_db.committed is True
    assert fake_db.rolled_back is False
    assert len(fake_db.added_objects) == 2

    saved_input = fake_db.added_objects[0]
    saved_output = fake_db.added_objects[1]

    assert isinstance(saved_input, PredictionInput)
    assert isinstance(saved_output, PredictionOutput)
    assert saved_output.prediction_input_id == saved_input.id


def test_predict_rolls_back_on_database_error():
    fake_db = FakeDB()

    def failing_commit():
        raise RuntimeError("database failure")

    fake_db.commit = failing_commit

    def override_get_db():
        yield fake_db

    app.dependency_overrides[get_db] = override_get_db

    payload = {
        "age": 35,
        "genre": "M",
        "revenu_mensuel": 5000,
        "statut_marital": "Célibataire",
        "departement": "Consulting",
        "poste": "Consultant",
        "nombre_experiences_precedentes": 2,
        "annee_experience_totale": 10,
        "annees_dans_l_entreprise": 4,
        "satisfaction_employee_environnement": 3,
        "note_evaluation_precedente": 3,
        "niveau_hierarchique_poste": 2,
        "satisfaction_employee_nature_travail": 3,
        "satisfaction_employee_equipe": 3,
        "satisfaction_employee_equilibre_pro_perso": 3,
        "note_evaluation_actuelle": 3,
        "heure_supplementaires": "Non",
        "augementation_salaire_precedente": 15,
        "nombre_participation_pee": 1,
        "nb_formations_suivies": 2,
        "distance_domicile_travail": 10,
        "niveau_education": 3,
        "domaine_etude": "Marketing",
        "frequence_deplacement": "Occasionnel",
        "annees_depuis_la_derniere_promotion": 1,
    }

    try:
        response = client.post("/predict", json=payload)
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 500
    assert response.json()["detail"] == (
        "Une erreur interne est survenue lors de la prédiction."
    )
    assert fake_db.rolled_back is True