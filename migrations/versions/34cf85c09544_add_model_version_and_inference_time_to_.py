
"""add model version and inference time to prediction outputs

Revision ID: 34cf85c09544
Revises: 5e817b511ec1
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "34cf85c09544"
down_revision: Union[str, Sequence[str], None] = "5e817b511ec1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add model version and inference time columns."""

    # Add the model version with a temporary default
    # to preserve existing prediction records.
    op.add_column(
        "prediction_outputs",
        sa.Column(
            "model_version",
            sa.String(),
            nullable=False,
            server_default="unknown",
        ),
    )

    # Remove the server default for future records.
    op.alter_column(
        "prediction_outputs",
        "model_version",
        server_default=None,
    )

    # Existing records can have an unknown inference time.
    op.add_column(
        "prediction_outputs",
        sa.Column(
            "inference_time_ms",
            sa.Float(),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Remove model version and inference time columns."""

    op.drop_column(
        "prediction_outputs",
        "inference_time_ms",
    )

    op.drop_column(
        "prediction_outputs",
        "model_version",
    )
