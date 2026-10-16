
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class PredictionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    age: int = Field(ge=18, le=60)
    genre: Literal["F", "M"]
    revenu_mensuel: int = Field(ge=1009, le=19999)
    statut_marital: Literal["Célibataire", "Divorcé(e)", "Marié(e)"]
    departement: Literal[
        "Commercial",
        "Consulting",
        "Ressources Humaines",
    ]
    poste: Literal[
        "Assistant de Direction",
        "Cadre Commercial",
        "Consultant",
        "Directeur Technique",
        "Manager",
        "Représentant Commercial",
        "Ressources Humaines",
        "Senior Manager",
        "Tech Lead",
    ]

    nombre_experiences_precedentes: int = Field(ge=0, le=9)
    annee_experience_totale: int = Field(ge=0, le=40)
    annees_dans_l_entreprise: int = Field(ge=0, le=40)
    satisfaction_employee_environnement: int = Field(ge=1, le=4)
    note_evaluation_precedente: int = Field(ge=1, le=4)
    niveau_hierarchique_poste: int = Field(ge=1, le=5)
    satisfaction_employee_nature_travail: int = Field(ge=1, le=4)
    satisfaction_employee_equipe: int = Field(ge=1, le=4)
    satisfaction_employee_equilibre_pro_perso: int = Field(ge=1, le=4)
    note_evaluation_actuelle: int = Field(ge=3, le=4)

    heure_supplementaires: Literal["Non", "Oui"]
    augementation_salaire_precedente: int = Field(ge=11, le=25)
    nombre_participation_pee: int = Field(ge=0, le=3)
    nb_formations_suivies: int = Field(ge=0, le=6)
    distance_domicile_travail: int = Field(ge=1, le=29)
    niveau_education: int = Field(ge=1, le=5)
    domaine_etude: Literal[
        "Autre",
        "Entrepreunariat",
        "Infra & Cloud",
        "Marketing",
        "Ressources Humaines",
        "Transformation Digitale",
    ]
    frequence_deplacement: Literal[
        "Aucun",
        "Frequent",
        "Occasionnel",
    ]
    annees_depuis_la_derniere_promotion: int = Field(ge=0, le=15)
