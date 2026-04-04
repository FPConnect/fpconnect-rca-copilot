"""Add pgvector support and machines table.

Revision ID: 002
Revises: 001
Create Date: 2026-04-04 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    op.execute("""
        CREATE TABLE IF NOT EXISTS kb_articles (
            id SERIAL PRIMARY KEY,
            title VARCHAR NOT NULL,
            content TEXT NOT NULL,
            tags VARCHAR,
            created_at TIMESTAMPTZ DEFAULT now()
        );
    """)
    op.execute("ALTER TABLE kb_articles ADD COLUMN IF NOT EXISTS embedding vector(384);")
    op.execute("ALTER TABLE tickets ADD COLUMN IF NOT EXISTS resolved_at TIMESTAMP;")

    op.create_table(
        "machines",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("location", sa.String(), nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("online", "warning", "offline", name="machine_status"),
            nullable=False,
        ),
        sa.Column("last_check", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index(op.f("ix_machines_id"), "machines", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_machines_id"), table_name="machines")
    op.drop_table("machines")
    op.execute("ALTER TABLE kb_articles DROP COLUMN IF EXISTS embedding;")
    op.execute("ALTER TABLE tickets DROP COLUMN IF EXISTS resolved_at;")
