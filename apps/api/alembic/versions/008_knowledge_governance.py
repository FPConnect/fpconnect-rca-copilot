"""Segment and govern the legacy technical knowledge base.

Revision ID: 008
Revises: 007
Create Date: 2026-11-04

Preserves ALL legacy article text, tags and vectors. Prior articles have no
proven owner or consent and stay invisible in 'legacy_quarantine'.
"""
from alembic import op
import sqlalchemy as sa

revision = "008"
down_revision = "007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    tables = set(sa.inspect(bind).get_table_names())

    if "knowledge_workspaces" not in tables:
        op.create_table(
            "knowledge_workspaces",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("slug", sa.String(64), nullable=False, unique=True),
            sa.Column("name", sa.String(160), nullable=False),
            sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True),
                      server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        )
    if "knowledge_memberships" not in tables:
        op.create_table(
            "knowledge_memberships",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("workspace_id", sa.Integer(),
                      sa.ForeignKey("knowledge_workspaces.id"), nullable=False),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
            sa.Column("membership_role", sa.String(20), nullable=False,
                      server_default="member"),
            sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True),
                      server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
            sa.UniqueConstraint("workspace_id", "user_id", name="uq_kb_workspace_membership"),
            sa.CheckConstraint("membership_role IN ('member','manager')",
                               name="ck_kb_membership_role"),
        )

    if "knowledge_audit" not in tables:
        op.create_table(
            "knowledge_audit",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("article_id", sa.Integer(), sa.ForeignKey("kb_articles.id"), nullable=False),
            sa.Column("actor_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
            sa.Column("event_type", sa.String(32), nullable=False),
            sa.Column("version", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        )

    if "knowledge_membership_audit" not in tables:
        op.create_table(
            "knowledge_membership_audit",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("workspace_id", sa.Integer(), sa.ForeignKey("knowledge_workspaces.id"), nullable=False),
            sa.Column("affected_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
            sa.Column("actor_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
            sa.Column("action", sa.String(16), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        )

    columns = {column["name"] for column in sa.inspect(bind).get_columns("kb_articles")}
    # These safe defaults ensure no pre-migration article is ever globally visible.
    additions = [
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id", name="fk_kb_articles_owner_id_users"), nullable=True),
        sa.Column("workspace_id", sa.Integer(),
                  sa.ForeignKey("knowledge_workspaces.id", name="fk_kb_articles_workspace_id_workspaces"), nullable=True),
        sa.Column("visibility", sa.String(16), nullable=False, server_default="private"),
        sa.Column("review_status", sa.String(24), nullable=False,
                  server_default="legacy_quarantine"),
        sa.Column("category", sa.String(40), nullable=False,
                  server_default="unclassified"),
        sa.Column("equipment_family", sa.String(100), nullable=True),
        sa.Column("manufacturer", sa.String(100), nullable=True),
        sa.Column("model_code", sa.String(100), nullable=True),
        sa.Column("failure_code", sa.String(100), nullable=True),
        sa.Column("source_ref", sa.String(240), nullable=True),
        sa.Column("reviewed_by", sa.Integer(), sa.ForeignKey("users.id", name="fk_kb_articles_reviewed_by_users"), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
    ]
    # SQLite cannot add foreign-key constraints with a plain ALTER TABLE.
    # Alembic batch mode uses a safe copy-and-move reconstruction; PostgreSQL
    # retains its native in-place ALTER TABLE operations.
    pending = [column for column in additions if column.name not in columns]
    if bind.dialect.name == "sqlite" and pending:
        with op.batch_alter_table("kb_articles", recreate="always") as batch_op:
            for column in pending:
                batch_op.add_column(column)
    else:
        for column in pending:
            op.add_column("kb_articles", column)

    # Reconcile any older rows explicitly instead of inferring permissions.
    op.execute(sa.text("""
        UPDATE kb_articles SET
          visibility = 'private',
          review_status = 'legacy_quarantine',
          owner_id = NULL,
          workspace_id = NULL,
          reviewed_by = NULL,
          reviewed_at = NULL
        WHERE owner_id IS NULL AND review_status = 'legacy_quarantine'
    """))

    for table, index_name, fields in [
        ("knowledge_workspaces", "ix_knowledge_workspaces_slug", ["slug"]),
        ("knowledge_memberships", "ix_knowledge_memberships_workspace_id", ["workspace_id"]),
        ("knowledge_memberships", "ix_knowledge_memberships_user_id", ["user_id"]),
        ("knowledge_membership_audit", "ix_knowledge_membership_audit_workspace_id", ["workspace_id"]),
        ("kb_articles", "ix_kb_articles_owner_id", ["owner_id"]),
        ("kb_articles", "ix_kb_articles_workspace_id", ["workspace_id"]),
        ("kb_articles", "ix_kb_articles_filters", ["review_status", "visibility", "category"]),
        ("kb_articles", "ix_kb_articles_equipment", ["equipment_family", "manufacturer"]),
    ]:
        indexes = {index["name"] for index in sa.inspect(bind).get_indexes(table)}
        if index_name not in indexes:
            op.create_index(index_name, table, fields)


def downgrade() -> None:
    # Deliberately refuse a destructive downgrade that would discard access
    # labels and potentially restore unsafe cross-workspace retrieval.
    raise RuntimeError("Knowledge governance migration is not safely reversible; restore from a reviewed backup.")
