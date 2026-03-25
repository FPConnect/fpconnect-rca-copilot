from sqlalchemy import inspect, text


def ensure_content_items_columns(engine) -> None:
    """Best-effort runtime schema patch for existing databases."""
    with engine.begin() as conn:
        inspector = inspect(conn)
        table_names = set(inspector.get_table_names())
        if 'content_items' not in table_names:
            return

        existing_cols = {c['name'] for c in inspector.get_columns('content_items')}

        if 'severity' not in existing_cols:
            conn.execute(text('ALTER TABLE content_items ADD COLUMN severity VARCHAR(32)'))
        if 'rca' not in existing_cols:
            conn.execute(text('ALTER TABLE content_items ADD COLUMN rca TEXT'))
