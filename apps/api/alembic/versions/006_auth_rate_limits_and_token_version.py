"""Add shared authentication limits and session versioning.

Revision ID: 006
Revises: 005
Create Date: 2026-10-15 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "006"
down_revision = "005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    user_columns = {column["name"] for column in inspector.get_columns("users")}
    if "token_version" not in user_columns:
        op.add_column(
            "users",
            sa.Column("token_version", sa.Integer(), server_default="0", nullable=False),
        )

    tables = set(inspector.get_table_names())
    if "auth_rate_limits" not in tables:
        op.create_table(
            "auth_rate_limits",
            sa.Column("bucket", sa.String(length=64), nullable=False),
            sa.Column("window_started_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("attempts", sa.Integer(), nullable=False),
            sa.PrimaryKeyConstraint("bucket"),
        )

    inspector = sa.inspect(bind)
    index_names = {
        index["name"] for index in inspector.get_indexes("auth_rate_limits")
    }
    if "ix_auth_rate_limits_window" not in index_names:
        op.create_index(
            "ix_auth_rate_limits_window",
            "auth_rate_limits",
            ["window_started_at"],
            unique=False,
        )


def downgrade() -> None:
    op.drop_index("ix_auth_rate_limits_window", table_name="auth_rate_limits")
    op.drop_table("auth_rate_limits")
    op.drop_column("users", "token_version")
