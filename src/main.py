
import json
import os
import secrets
from contextlib import asynccontextmanager
from pathlib import Path

import joblib
import pandas as pd
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session

from src.database import get_db
from src.models import Employee, PredictionInput, PredictionOutput
from src.schemas import PredictionRequest


PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_DIR = PROJECT_ROOT / "output" / "models"

API_KEY = os.getenv("API_KEY")

api_key_header = APIKeyHeader(
    name="X-API-Key",
    auto_error=False,
)


def verify_api_key(api_key: str = Depends(api_key_header)):
    """Vérifie la clé API envoyée dans la requête."""

    if not API_KEY:
        raise HTTPException(
            status_code=500,
            detail="La clé API n'est pas configurée.",
        )

    if not api_key or not secrets.compare_digest(api_key, API_KEY):
        raise HTTPException(
            status_code=401,
            detail="Clé API invalide ou manquante.",
        )

    return api_key


def load_artifacts():
    """Charge le modèle et le préprocesseur."""

    model = joblib.load(MODEL_DIR / "lr_optimise.joblib")
    preprocessor = joblib.load(MODEL_DIR / "preprocessor.joblib")

    return model, preprocessor


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Charge les artefacts au démarrage de l'API."""

    app.state.model, app.state.preprocessor = load_artifacts()

    yield


app = FastAPI(
    title="HR Analytics - Employee Attrition Prediction",
    description=(
        "API de prédiction de l'attrition des employés "
        "à partir d'un modèle de Machine Learning."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
def root():
    return {
        "message": "HR Analytics API opérationnelle",
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/predict")
def predict(
    request: PredictionRequest,
    request_api: Request,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key),
):
    try:
        # Rechercher l'employé dans la base de données
        employee = db.get(Employee, request.id_employee)

        if employee is None:
            raise HTTPException(
                status_code=404,
                detail="Employé introuvable.",
            )

        # Réutiliser les artefacts chargés au démarrage de l'API
        model = request_api.app.state.model
        preprocessor = request_api.app.state.preprocessor

        # Récupérer uniquement les variables attendues par le P4
        input_data = {
            column: getattr(employee, column)
            for column in preprocessor.feature_names_in_
        }

        input_df = pd.DataFrame([input_data])
        transformed_data = preprocessor.transform(input_df)

        # Conserver les noms des variables après le prétraitement
        transformed_df = pd.DataFrame(
            transformed_data,
            columns=preprocessor.get_feature_names_out(),
        )

        # Prédiction avec le modèle entraîné
        prediction = str(model.predict(transformed_df)[0])

        # Probabilité associée à la classe prédite
        probabilities = model.predict_proba(transformed_df)[0]
        classes = list(model.classes_)
        probability = float(
            probabilities[classes.index(prediction)]
        )

        # Enregistrer les données d'entrée liées à l'employé
        prediction_input = PredictionInput(
            employee_id=employee.id_employee,
            input_data=json.dumps(input_data, ensure_ascii=False),
        )
        db.add(prediction_input)
        db.flush()

        # Enregistrer le résultat de la prédiction
        prediction_output = PredictionOutput(
            prediction_input_id=prediction_input.id,
            prediction=prediction,
            probability=probability,
        )
        db.add(prediction_output)
        db.commit()

        return {
            "employee_id": employee.id_employee,
            "prediction_id": prediction_output.id,
            "prediction": prediction,
            "probability": probability,
            "message": (
                "Le modèle prédit un départ."
                if prediction == "Oui"
                else "Le modèle prédit un maintien."
            ),
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Une erreur interne est survenue lors de la prédiction.",
        ) from exc
