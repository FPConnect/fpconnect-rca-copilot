"""Quarantine legacy tickets pending explicit ownership mapping.

Revision ID: 010
Revises: 009
"""

from alembic import op
import sqlalchemy as sa

revision = "010"
down_revision = "009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("tickets") as batch:
        batch.add_column(sa.Column("organization_id", sa.Integer(), nullable=True))
        batch.create_foreign_key(
            "fk_tickets_organization", "organizations", ["organization_id"], ["id"]
        )
        batch.create_index("ix_tickets_organization_id", ["organization_id"])


def downgrade() -> None:
    with op.batch_alter_table("tickets") as batch:
        batch.drop_index("ix_tickets_organization_id")
        batch.drop_constraint("fk_tickets_organization", type_="foreignkey")
        batch.drop_column("organization_id")
