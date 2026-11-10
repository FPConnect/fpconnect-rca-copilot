"""Quarantine legacy ticket history, suggestions and knowledge articles.

Revision ID: 014
Revises: 013
"""
from alembic import op
import sqlalchemy as sa

revision = "014"
down_revision = "013"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Older revisions never created these ORM tables; some databases instead
    # received them via application create_all. Support both histories.
    tables = set(sa.inspect(op.get_bind()).get_table_names())
    if "ticket_logs" not in tables:
        op.create_table(
            "ticket_logs",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("ticket_id", sa.Integer(), sa.ForeignKey("tickets.id"), nullable=False),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
            sa.Column("action", sa.String(), nullable=False),
            sa.Column("detail", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        )
        op.create_index("ix_ticket_logs_id", "ticket_logs", ["id"])
    if "rca_suggestions" not in tables:
        op.create_table(
            "rca_suggestions",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("ticket_id", sa.Integer(), sa.ForeignKey("tickets.id"), nullable=False),
            sa.Column("cause", sa.Text(), nullable=False),
            sa.Column("confidence", sa.Float(), nullable=True),
            sa.Column("resolution", sa.Text(), nullable=True),
            sa.Column("similar_incidents", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        )
        op.create_index("ix_rca_suggestions_id", "rca_suggestions", ["id"])
    for table in ("ticket_logs", "rca_suggestions", "kb_articles"):
        with op.batch_alter_table(table) as batch:
            batch.add_column(sa.Column("organization_id", sa.Integer(), nullable=True))
            batch.create_foreign_key(
                f"fk_{table}_organization", "organizations", ["organization_id"], ["id"]
            )
            batch.create_index(f"ix_{table}_organization_id", ["organization_id"])


def downgrade() -> None:
    # Retain legacy-compatible tables, including ones created in this upgrade.
    for table in ("kb_articles", "rca_suggestions", "ticket_logs"):
        with op.batch_alter_table(table) as batch:
            batch.drop_index(f"ix_{table}_organization_id")
            batch.drop_constraint(f"fk_{table}_organization", type_="foreignkey")
            batch.drop_column("organization_id")
