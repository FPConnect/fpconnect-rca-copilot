"""Extend mapping audit to playbooks, contracts and knowledge.

Revision ID: 015
Revises: 014
"""
from alembic import op
import sqlalchemy as sa

revision = "015"
down_revision = "014"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "tenant_provision_audit",
        sa.Column("other_resource_ids", sa.Text(), nullable=False, server_default="{}"),
    )


def downgrade() -> None:
    op.drop_column("tenant_provision_audit", "other_resource_ids")
