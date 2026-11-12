
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class PredictionRequest(BaseModel):
    """Identifiant de l'employé pour demander une prédiction."""

    model_config = ConfigDict(extra="forbid")

    id_employee: int = Field(gt=0)


class FeatureContribution(BaseModel):
    """Contribution d'une variable à la prédiction."""

    feature: str
    impact: Literal["positive", "negative"]
    contribution: float


class Explainability(BaseModel):
    """Explication des principaux facteurs de la prédiction."""

    method: str
    top_factors: list[FeatureContribution]


class PredictionResponse(BaseModel):
    """Réponse détaillée de l'API de prédiction."""

    employee_id: int
    prediction_id: int
    prediction: Literal["Oui", "Non"]
    probability: float = Field(ge=0, le=100)
    message: str
    inference_time_ms: float = Field(ge=0)
    model_version: str
    explainability: Explainability
