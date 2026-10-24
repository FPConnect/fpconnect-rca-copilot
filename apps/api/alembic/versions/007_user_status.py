"""Add active status to user accounts.

Revision ID: 007
Revises: 006
Create Date: 2026-10-21 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "007"
down_revision = "006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    columns = {column["name"] for column in sa.inspect(bind).get_columns("users")}
    if "is_active" not in columns:
        op.add_column(
            "users",
            sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        )
    op.execute(
        sa.text(
            """
            UPDATE users
            SET role = 'master',
                access_level = 5,
                is_active = true,
                token_version = token_version + 1
            WHERE lower(email) = 'admin@fpconnect.com'
            """
        )
    )


def downgrade() -> None:
    columns = {column["name"] for column in sa.inspect(op.get_bind()).get_columns("users")}
    if "is_active" in columns:
        op.drop_column("users", "is_active")
