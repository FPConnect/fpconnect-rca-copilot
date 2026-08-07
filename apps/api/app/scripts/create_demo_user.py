"""Create a demo admin user directly in the SQLite database.

This version avoids importing the FastAPI app or password hashing
stack, so it is robust for local setup. Safe to run multiple times.
"""

from pathlib import Path
import sqlite3


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    db_path = root / "fpconnect.db"
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        # Simple fixed hash placeholder; not used for real auth in dev.
        cur.execute(
            """
            INSERT OR IGNORE INTO users (id, email, hashed_password, full_name, role)
            VALUES (1, 'demo@fpconnect.local', 'demo-password', 'Demo Admin', 'admin')
            """
        )
        conn.commit()
        print("Demo user ensured in DB (id=1, email=demo@fpconnect.local)")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
