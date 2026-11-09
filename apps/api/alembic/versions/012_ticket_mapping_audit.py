"""Extend operator audit records to cover explicit ticket mapping.

Revision ID: 012
Revises: 011
"""
from alembic import op
import sqlalchemy as sa

revision = "012"
down_revision = "011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "tenant_provision_audit",
        sa.Column("ticket_ids", sa.Text(), nullable=False, server_default="[]"),
    )


def downgrade() -> None:
    op.drop_column("tenant_provision_audit", "ticket_ids")
