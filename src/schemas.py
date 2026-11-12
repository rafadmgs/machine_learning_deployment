
from pydantic import BaseModel, ConfigDict, Field


class PredictionRequest(BaseModel):
    """Identifiant de l'employé pour demander une prédiction."""

    model_config = ConfigDict(extra="forbid")

    id_employee: int = Field(gt=0)
