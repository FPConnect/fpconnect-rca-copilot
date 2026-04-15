"""Add ticket automation fields and logs.

Revision ID: 004
Revises: 003
Create Date: 2026-04-15 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("tickets", sa.Column("escalation_level", sa.Integer(), nullable=True))
    op.create_table(
        "ticket_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("ticket_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("detail", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["ticket_id"], ["tickets.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ticket_logs_id"), "ticket_logs", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_ticket_logs_id"), table_name="ticket_logs")
    op.drop_table("ticket_logs")
    op.drop_column("tickets", "escalation_level")
