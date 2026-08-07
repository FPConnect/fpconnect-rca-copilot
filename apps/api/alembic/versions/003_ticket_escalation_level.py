"""Add escalation_level to tickets.

Revision ID: 003
Revises: 002
Create Date: 2026-03-05 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "tickets",
        sa.Column("escalation_level", sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("tickets", "escalation_level")
