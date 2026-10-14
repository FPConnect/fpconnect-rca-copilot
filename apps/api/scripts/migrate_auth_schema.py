"""Apply the idempotent production schema repair required by authentication."""

from __future__ import annotations

import argparse
import os

from sqlalchemy import create_engine, inspect, text


EXPECTED_ROLES = ("master", "user", "visitor")


def migrate() -> None:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is required")

    engine = create_engine(database_url, pool_pre_ping=True)
    if engine.dialect.name != "postgresql":
        raise RuntimeError("This production migration requires PostgreSQL")

    with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as connection:
        tables = set(inspect(connection).get_table_names())
        if "users" not in tables:
            raise RuntimeError("The users table does not exist")

        for role in EXPECTED_ROLES:
            connection.execute(text(f"ALTER TYPE user_role ADD VALUE IF NOT EXISTS '{role}'"))

        connection.execute(
            text(
                "ALTER TABLE users "
                "ADD COLUMN IF NOT EXISTS phone_number VARCHAR"
            )
        )
        connection.execute(
            text(
                "ALTER TABLE users "
                "ADD COLUMN IF NOT EXISTS access_level INTEGER DEFAULT 2"
            )
        )
        connection.execute(
            text("UPDATE users SET role = 'user' WHERE role::text = 'technician'")
        )
        connection.execute(
            text(
                "UPDATE users SET access_level = CASE role::text "
                "WHEN 'master' THEN 5 WHEN 'admin' THEN 4 "
                "WHEN 'manager' THEN 3 WHEN 'visitor' THEN 1 ELSE 2 END"
            )
        )
        connection.execute(text("ALTER TABLE users ALTER COLUMN access_level SET DEFAULT 2"))
        connection.execute(text("ALTER TABLE users ALTER COLUMN access_level SET NOT NULL"))

    engine.dispose()


def remove_empty_regular_account(email: str) -> bool:
    """Remove a stale regular account only when it has no operational records."""
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is required")

    engine = create_engine(database_url, pool_pre_ping=True)
    statement = text(
        """
        DELETE FROM users AS u
        WHERE lower(u.email) = :email
          AND u.role::text = 'user'
          AND u.access_level = 2
          AND NOT EXISTS (
            SELECT 1 FROM tickets AS t
            WHERE t.creator_id = u.id OR t.assignee_id = u.id
          )
          AND NOT EXISTS (
            SELECT 1 FROM ticket_attachments AS a WHERE a.uploader_id = u.id
          )
          AND NOT EXISTS (
            SELECT 1 FROM ticket_logs AS l WHERE l.user_id = u.id
          )
        RETURNING u.id
        """
    )
    with engine.begin() as connection:
        removed = connection.execute(
            statement,
            {"email": email.strip().lower()},
        ).scalar()
    engine.dispose()
    return removed is not None


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--remove-empty-account")
    args = parser.parse_args()
    migrate()
    print("authentication schema migration: ok")
    if args.remove_empty_account:
        removed = remove_empty_regular_account(args.remove_empty_account)
        print("stale account removed:", removed)
