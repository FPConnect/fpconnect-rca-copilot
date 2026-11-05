"""Regression checks for non-destructive KB migration 008.

Uses synthetic data and a temporary SQLite database; production must still
have a verified backup and migration rehearsal on its actual database engine.
"""
from pathlib import Path
import importlib.util

from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine, inspect, text


def test_migration_preserves_legacy_records_and_quarantines_them(tmp_path):
    db_path = tmp_path / "kb_migration.sqlite"
    engine = create_engine(f"sqlite:///{db_path}")
    with engine.begin() as conn:
        conn.execute(text("PRAGMA foreign_keys = ON"))
        conn.execute(text("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY, email VARCHAR(255)
            )
        """))
        conn.execute(text("""
            CREATE TABLE kb_articles (
                id INTEGER PRIMARY KEY,
                title VARCHAR NOT NULL,
                content TEXT NOT NULL,
                tags VARCHAR,
                embedding TEXT,
                created_at DATETIME
            )
        """))
        conn.execute(text("""
            INSERT INTO users(id,email) VALUES (1,'synthetic@example.test')
        """))
        conn.execute(text("""
            INSERT INTO kb_articles(id,title,content,tags,embedding)
            VALUES (42,'Historical restricted sample',
                    'Synthetic confidential technical record',
                    'old-tag','[0.1,0.2]')
        """))

    migration_file = (
        Path(__file__).resolve().parents[1] / "alembic" / "versions" /
        "008_knowledge_governance.py"
    )
    spec = importlib.util.spec_from_file_location("kb_migration_008", migration_file)
    assert spec is not None and spec.loader is not None
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)

    with engine.begin() as conn:
        context = MigrationContext.configure(conn)
        operations = Operations(context)
        original_op = migration.op
        try:
            migration.op = operations
            migration.upgrade()
        finally:
            migration.op = original_op

        columns = {x["name"] for x in inspect(conn).get_columns("kb_articles")}
        assert {"owner_id", "workspace_id", "visibility", "review_status",
                "category", "manufacturer", "failure_code", "version"} <= columns
        record = conn.execute(text("""
            SELECT id, title, content, tags, embedding, owner_id,
                   workspace_id, visibility, review_status
            FROM kb_articles WHERE id = 42
        """)).mappings().one()
        assert record["id"] == 42
        assert record["content"] == "Synthetic confidential technical record"
        assert record["tags"] == "old-tag"
        assert record["embedding"] == "[0.1,0.2]"
        assert record["owner_id"] is None
        assert record["workspace_id"] is None
        assert record["visibility"] == "private"
        assert record["review_status"] == "legacy_quarantine"
        for table in (
            "knowledge_workspaces", "knowledge_memberships",
            "knowledge_audit", "knowledge_membership_audit",
        ):
            assert table in inspect(conn).get_table_names()
