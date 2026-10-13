"""Apply the idempotent production schema repair required by authentication."""

from __future__ import annotations

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


if __name__ == "__main__":
    migrate()
    print("authentication schema migration: ok")
