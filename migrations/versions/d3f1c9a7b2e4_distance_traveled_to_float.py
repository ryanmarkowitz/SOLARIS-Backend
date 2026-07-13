"""distance_traveled to float

Revision ID: d3f1c9a7b2e4
Revises: 6964ab93cc69
Create Date: 2026-07-13 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd3f1c9a7b2e4'
down_revision: Union[str, Sequence[str], None] = '6964ab93cc69'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        'telemetry',
        'distance_traveled',
        existing_type=sa.SmallInteger(),
        type_=sa.Float(),
        existing_nullable=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        'telemetry',
        'distance_traveled',
        existing_type=sa.Float(),
        type_=sa.SmallInteger(),
        existing_nullable=True,
    )
