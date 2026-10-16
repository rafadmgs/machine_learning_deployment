
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class Employee(Base):
    __tablename__ = "employees"

    id_employee: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    age: Mapped[int] = mapped_column(Integer, nullable=False)
    genre: Mapped[str] = mapped_column(String, nullable=False)
    revenu_mensuel: Mapped[int] = mapped_column(Integer, nullable=False)
    statut_marital: Mapped[str] = mapped_column(String, nullable=False)
    departement: Mapped[str] = mapped_column(String, nullable=False)
    poste: Mapped[str] = mapped_column(String, nullable=False)

    nombre_experiences_precedentes: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
    annee_experience_totale: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
    annees_dans_l_entreprise: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
    annees_dans_le_poste_actuel: Mapped[int] = mapped_column(
        Integer, nullable=False
    )

    satisfaction_employee_environnement: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
    note_evaluation_precedente: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
    niveau_hierarchique_poste: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
    satisfaction_employee_nature_travail: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
    satisfaction_employee_equipe: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
    satisfaction_employee_equilibre_pro_perso: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
    note_evaluation_actuelle: Mapped[int] = mapped_column(
        Integer, nullable=False
    )

    heure_supplementaires: Mapped[str] = mapped_column(
        String, nullable=False
    )
    augementation_salaire_precedente: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
    a_quitte_l_entreprise: Mapped[str] = mapped_column(
        String, nullable=False
    )
    nombre_participation_pee: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
    nb_formations_suivies: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
    distance_domicile_travail: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
    niveau_education: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
    domaine_etude: Mapped[str] = mapped_column(
        String, nullable=False
    )
    frequence_deplacement: Mapped[str] = mapped_column(
        String, nullable=False
    )
    annees_depuis_la_derniere_promotion: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
    annes_sous_responsable_actuel: Mapped[int] = mapped_column(
        Integer, nullable=False
    )


class PredictionInput(Base):
    __tablename__ = "prediction_inputs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    employee_id: Mapped[int | None] = mapped_column(
        ForeignKey("employees.id_employee"),
        nullable=True,
    )

    input_data: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )


class PredictionOutput(Base):
    __tablename__ = "prediction_outputs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    prediction_input_id: Mapped[int] = mapped_column(
        ForeignKey("prediction_inputs.id"),
        nullable=False,
    )

    prediction: Mapped[str] = mapped_column(String, nullable=False)

    probability: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )
