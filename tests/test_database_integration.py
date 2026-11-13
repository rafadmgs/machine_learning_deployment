
import json
import os
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, delete, select
from sqlalchemy.orm import Session

from src.models import Employee, PredictionInput, PredictionOutput


@pytest.fixture
def postgres_session():
    """Crée une session avec la vraie base PostgreSQL de test."""

    database_url = os.getenv("TEST_DATABASE_URL")

    if not database_url:
        pytest.skip("TEST_DATABASE_URL n'est pas configurée.")

    engine = create_engine(database_url, pool_pre_ping=True)

    try:
        with Session(engine) as session:
            yield session
    finally:
        engine.dispose()


def test_postgres_insert_select_delete_and_relations(postgres_session):
    """Vérifie les opérations CRUD et les relations dans PostgreSQL."""

    session = postgres_session
    test_id = str(uuid4())
    input_id = None

    try:
        employee_id = session.scalar(
            select(Employee.id_employee).limit(1)
        )
        assert employee_id is not None

        prediction_input = PredictionInput(
            employee_id=employee_id,
            input_data=json.dumps({"test_id": test_id}),
        )

        session.add(prediction_input)
        session.flush()

        input_id = prediction_input.id

        prediction_output = PredictionOutput(
        prediction_input_id=input_id,
        prediction="Oui",
        probability=0.85,
        model_version="test-1.0.0",
        inference_time_ms=12.5,
    )

        session.add(prediction_output)
        session.commit()

        output_id = prediction_output.id

        result = session.execute(
            select(PredictionInput, PredictionOutput, Employee)
            .join(
                PredictionOutput,
                PredictionOutput.prediction_input_id == PredictionInput.id,
            )
            .join(
                Employee,
                Employee.id_employee == PredictionInput.employee_id,
            )
            .where(PredictionInput.id == input_id)
        ).one()

        saved_input, saved_output, saved_employee = result

        assert saved_input.id == input_id
        assert saved_input.employee_id == saved_employee.id_employee
        assert saved_output.id == output_id
        assert saved_output.prediction_input_id == saved_input.id
        assert saved_output.prediction == "Oui"
        assert saved_output.probability == pytest.approx(0.85)

        session.execute(
            delete(PredictionOutput).where(
                PredictionOutput.id == output_id
            )
        )
        session.execute(
            delete(PredictionInput).where(
                PredictionInput.id == input_id
            )
        )
        session.commit()

        assert session.get(PredictionInput, input_id) is None
        assert session.get(PredictionOutput, output_id) is None

    finally:
        session.rollback()

        if input_id is not None:
            session.execute(
                delete(PredictionOutput).where(
                    PredictionOutput.prediction_input_id == input_id
                )
            )
            session.execute(
                delete(PredictionInput).where(
                    PredictionInput.id == input_id
                )
            )
            session.commit()
