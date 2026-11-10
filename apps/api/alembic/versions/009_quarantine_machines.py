"""Quarantine unmapped machines using a nullable organization foreign key.

Revision ID: 009
Revises: 008
"""

from alembic import op
import sqlalchemy as sa

revision = "009"
down_revision = "008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tenant_provision_audit",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("organization_id", sa.Integer(), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("operator", sa.String(255), nullable=False),
        sa.Column("change_reference", sa.String(255), nullable=False),
        sa.Column("machine_ids", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    with op.batch_alter_table("machines") as batch:
        batch.add_column(sa.Column("organization_id", sa.Integer(), nullable=True))
        batch.create_foreign_key(
            "fk_machines_organization", "organizations", ["organization_id"], ["id"]
        )
        batch.create_index("ix_machines_organization_id", ["organization_id"])


def downgrade() -> None:
    with op.batch_alter_table("machines") as batch:
        batch.drop_index("ix_machines_organization_id")
        batch.drop_constraint("fk_machines_organization", type_="foreignkey")
        batch.drop_column("organization_id")
    op.drop_table("tenant_provision_audit")
