"""Quarantine legacy attachment metadata until explicit ownership mapping.

Revision ID: 013
Revises: 012
"""
from alembic import op
import sqlalchemy as sa

revision = "013"
down_revision = "012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("ticket_attachments") as batch:
        batch.add_column(sa.Column("organization_id", sa.Integer(), nullable=True))
        batch.create_foreign_key(
            "fk_ticket_attachments_organization", "organizations", ["organization_id"], ["id"]
        )
        batch.create_index("ix_ticket_attachments_organization_id", ["organization_id"])


def downgrade() -> None:
    with op.batch_alter_table("ticket_attachments") as batch:
        batch.drop_index("ix_ticket_attachments_organization_id")
        batch.drop_constraint("fk_ticket_attachments_organization", type_="foreignkey")
        batch.drop_column("organization_id")
