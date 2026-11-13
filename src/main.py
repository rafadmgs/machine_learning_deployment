
import json
import logging
import os
import secrets
from contextlib import asynccontextmanager
from pathlib import Path
from time import perf_counter

import joblib
import pandas as pd
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session

from src.database import get_db
from src.models import Employee, PredictionInput, PredictionOutput
from src.schemas import PredictionRequest, PredictionResponse


PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_DIR = PROJECT_ROOT / "output" / "models"

API_KEY = os.getenv("API_KEY")
MODEL_VERSION = "1.0.0"
TOP_FACTORS_COUNT = 3

# La documentation interactive reste disponible en développement,
# mais elle est désactivée en production.
APP_ENV = os.getenv("APP_ENV", "development").lower()
DOCS_URL = "/docs" if APP_ENV != "production" else None
REDOC_URL = "/redoc" if APP_ENV != "production" else None
OPENAPI_URL = "/openapi.json" if APP_ENV != "production" else None

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


def get_top_factors(model, preprocessor, transformed_data):
    """
    Calcule les principales contributions individuelles
    à partir des coefficients de la régression logistique.

    Une contribution positive favorise la classe Oui.
    Une contribution négative favorise la classe Non.
    """

    scaler = model.named_steps["standardscaler"]
    logistic_model = model.named_steps["logisticregression"]

    scaled_data = scaler.transform(transformed_data)

    coefficients = logistic_model.coef_[0]
    contributions = scaled_data[0] * coefficients

    feature_names = preprocessor.get_feature_names_out()

    factors = []

    for feature, contribution in zip(feature_names, contributions):
        feature_name = (
            feature.replace("nominal__", "")
            .replace("remainder__", "")
        )

        factors.append(
            {
                "feature": feature_name,
                "impact": (
                    "positive" if contribution >= 0 else "negative"
                ),
                "contribution": round(float(contribution), 4),
            }
        )

    factors.sort(
        key=lambda item: abs(item["contribution"]),
        reverse=True,
    )

    return factors[:TOP_FACTORS_COUNT]


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
    version=MODEL_VERSION,
    lifespan=lifespan,
    docs_url=DOCS_URL,
    redoc_url=REDOC_URL,
    openapi_url=OPENAPI_URL,
)


@app.get("/")
def root():
    response = {
        "message": "HR Analytics API opérationnelle",
    }

    if app.docs_url:
        response["docs"] = app.docs_url

    return response


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post(
    "/predict",
    response_model=PredictionResponse,
)
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

        # Récupérer les artefacts chargés au démarrage de l'API
        model = request_api.app.state.model
        preprocessor = request_api.app.state.preprocessor

        # Mesurer le temps de prétraitement et d'inférence
        inference_start = perf_counter()

        # Récupérer uniquement les variables attendues par le P4
        input_data = {
            column: getattr(employee, column)
            for column in preprocessor.feature_names_in_
        }

        input_df = pd.DataFrame([input_data])

        transformed_data = preprocessor.transform(input_df)

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

        # Explicabilité individuelle de la prédiction
        top_factors = get_top_factors(
            model,
            preprocessor,
            transformed_df,
        )

        # Temps total du prétraitement, de la prédiction
        # et du calcul des contributions
        inference_time_ms = (
            perf_counter() - inference_start
        ) * 1000

        # Enregistrer les données d'entrée liées à l'employé
        prediction_input = PredictionInput(
            employee_id=employee.id_employee,
            input_data=json.dumps(
                input_data,
                ensure_ascii=False,
            ),
        )

        db.add(prediction_input)
        db.flush()

        # Enregistrer le résultat, la version du modèle
        # et le temps d'inférence
        prediction_output = PredictionOutput(
            prediction_input_id=prediction_input.id,
            prediction=prediction,
            probability=probability,
            model_version=MODEL_VERSION,
            inference_time_ms=round(inference_time_ms, 2),
        )

        db.add(prediction_output)
        db.commit()

        return {
            "employee_id": employee.id_employee,
            "prediction_id": prediction_output.id,
            "prediction": prediction,
            "probability": round(probability * 100, 2),
            "message": (
                "Le modèle prédit un départ."
                if prediction == "Oui"
                else "Le modèle prédit un maintien."
            ),
            "inference_time_ms": round(inference_time_ms, 2),
            "model_version": MODEL_VERSION,
            "explainability": {
                "method": "Régression logistique - contributions locales des coefficients",
                "top_factors": top_factors,
            },
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        logging.exception(
            "Erreur détaillée lors de la prédiction"
        )
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "Une erreur interne est survenue "
                "lors de la prédiction."
            ),
        )
