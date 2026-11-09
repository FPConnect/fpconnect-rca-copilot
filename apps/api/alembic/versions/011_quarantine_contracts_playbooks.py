"""Quarantine unmapped contracts and playbooks.

Revision ID: 011
Revises: 010
"""
from alembic import op
import sqlalchemy as sa

revision = "011"
down_revision = "010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    for table in ("playbooks", "sla_contracts"):
        with op.batch_alter_table(table) as batch:
            batch.add_column(sa.Column("organization_id", sa.Integer(), nullable=True))
            batch.create_foreign_key(
                f"fk_{table}_organization", "organizations", ["organization_id"], ["id"]
            )
            batch.create_index(f"ix_{table}_organization_id", ["organization_id"])


def downgrade() -> None:
    for table in ("sla_contracts", "playbooks"):
        with op.batch_alter_table(table) as batch:
            batch.drop_index(f"ix_{table}_organization_id")
            batch.drop_constraint(f"fk_{table}_organization", type_="foreignkey")
            batch.drop_column("organization_id")
