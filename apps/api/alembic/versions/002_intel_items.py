"""Add intel_items table.

Revision ID: 002
Revises: 001
Create Date: 2026-03-02 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "intel_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source", sa.String(length=200), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("published_at", sa.DateTime(), nullable=True),
        sa.Column(
            "fetched_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("content_text", sa.Text(), nullable=True),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("topic", sa.String(length=120), nullable=True),
        sa.Column("summary_pt", sa.Text(), nullable=True),
        sa.Column("summary_en", sa.Text(), nullable=True),
        sa.Column("processed", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_intel_items_id"), "intel_items", ["id"], unique=False)
    op.create_index(op.f("ix_intel_items_content_hash"), "intel_items", ["content_hash"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_intel_items_content_hash"), table_name="intel_items")
    op.drop_index(op.f("ix_intel_items_id"), table_name="intel_items")
    op.drop_table("intel_items")
