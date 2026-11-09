"""Use membership-specific roles; never infer privilege for existing mappings.

Revision ID: 016
Revises: 015
"""
from alembic import op
import sqlalchemy as sa

revision = "016"
down_revision = "015"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("organization_memberships") as batch:
        batch.add_column(sa.Column("role", sa.String(16), nullable=False, server_default="visitor"))
        batch.create_check_constraint(
            "ck_membership_role",
            "role IN ('master', 'admin', 'manager', 'user', 'visitor')",
        )


def downgrade() -> None:
    with op.batch_alter_table("organization_memberships") as batch:
        batch.drop_constraint("ck_membership_role", type_="check")
        batch.drop_column("role")
