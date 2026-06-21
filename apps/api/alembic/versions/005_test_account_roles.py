"""Add test account roles and profile fields.

Revision ID: 005
Revises: 004
Create Date: 2026-06-21 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("phone_number", sa.String(), nullable=True))
    op.add_column("users", sa.Column("access_level", sa.Integer(), nullable=False, server_default="2"))
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("ALTER TYPE user_role ADD VALUE IF NOT EXISTS 'master'")
        op.execute("ALTER TYPE user_role ADD VALUE IF NOT EXISTS 'user'")
        op.execute("ALTER TYPE user_role ADD VALUE IF NOT EXISTS 'visitor'")
        op.execute("UPDATE users SET role = 'user' WHERE role = 'technician'")
        op.execute("UPDATE users SET access_level = CASE role WHEN 'admin' THEN 4 WHEN 'manager' THEN 3 ELSE 2 END")
    else:
        op.execute("UPDATE users SET access_level = 2 WHERE access_level IS NULL")


def downgrade() -> None:
    op.drop_column("users", "access_level")
    op.drop_column("users", "phone_number")
