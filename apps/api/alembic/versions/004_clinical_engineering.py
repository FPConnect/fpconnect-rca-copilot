"""Add clinical engineering product entities.

Revision ID: 004
Revises: 003
Create Date: 2026-05-15 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("machines", sa.Column("model", sa.String(), nullable=True))
    op.add_column("machines", sa.Column("criticality", sa.String(), server_default="Média", nullable=False))
    op.add_column("machines", sa.Column("last_failure", sa.String(), nullable=True))
    op.add_column("machines", sa.Column("recurrent_failures", sa.Integer(), server_default="0", nullable=False))
    op.add_column("tickets", sa.Column("root_cause", sa.Text(), nullable=True))
    op.add_column("tickets", sa.Column("recommendation", sa.Text(), nullable=True))
    op.add_column("tickets", sa.Column("analysis_completed", sa.DateTime(timezone=True), nullable=True))

    op.create_table(
        "playbooks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("equipment", sa.String(), nullable=False),
        sa.Column("steps", sa.Text(), nullable=False),
        sa.Column("files", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_playbooks_id"), "playbooks", ["id"], unique=False)

    op.create_table(
        "sla_contracts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("equipment", sa.String(), nullable=False),
        sa.Column("vendor", sa.String(), nullable=False),
        sa.Column("response_time_hours", sa.Integer(), nullable=False),
        sa.Column("penalty", sa.Text(), nullable=True),
        sa.Column("sla_compliance", sa.Float(), server_default="100", nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_sla_contracts_id"), "sla_contracts", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_sla_contracts_id"), table_name="sla_contracts")
    op.drop_table("sla_contracts")
    op.drop_index(op.f("ix_playbooks_id"), table_name="playbooks")
    op.drop_table("playbooks")
    op.drop_column("tickets", "analysis_completed")
    op.drop_column("tickets", "recommendation")
    op.drop_column("tickets", "root_cause")
    op.drop_column("machines", "recurrent_failures")
    op.drop_column("machines", "last_failure")
    op.drop_column("machines", "criticality")
    op.drop_column("machines", "model")
