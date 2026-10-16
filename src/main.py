
import json
from pathlib import Path

import joblib
import pandas as pd
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import exc
from sqlalchemy import exc
from sqlalchemy.orm import Session

from src.database import get_db
from src.models import PredictionInput, PredictionOutput
from src.schemas import PredictionRequest


PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_DIR = PROJECT_ROOT / "output" / "models"

model = joblib.load(MODEL_DIR / "lr_optimise.joblib")
preprocessor = joblib.load(MODEL_DIR / "preprocessor.joblib")

app = FastAPI(
    title="HR Analytics - Employee Attrition Prediction",
    description=(
        "API de prédiction de l'attrition des employés "
        "à partir d'un modèle de Machine Learning."
    ),
    version="1.0.0",
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
    db: Session = Depends(get_db),
):
    try:
        input_data = request.model_dump()

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

        # Enregistrer les données d'entrée
        prediction_input = PredictionInput(
            input_data=json.dumps(input_data, ensure_ascii=False)
        )
        db.add(prediction_input)
        db.flush()

        # Enregistrer le résultat
        prediction_output = PredictionOutput(
            prediction_input_id=prediction_input.id,
            prediction=prediction,
            probability=probability,
        )
        db.add(prediction_output)
        db.commit()

        return {
            "prediction_id": prediction_output.id,
            "prediction": prediction,
            "probability": probability,
            "message": (
                "Le modèle prédit un départ."
                if prediction == "Oui"
                else "Le modèle prédit un maintien."
            ),
        }

    except Exception as exc:
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail="Une erreur interne est survenue lors de la prédiction.",
            ) from exc