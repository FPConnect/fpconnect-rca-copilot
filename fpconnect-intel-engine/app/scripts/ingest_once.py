import yaml
from sqlalchemy.orm import Session

from app.core.config import settings
from app.ingest.rss import fetch_rss
from app.process.pipeline import upsert_items
from app.db.base import Base
from app.db.session import make_engine, make_session_factory
from app.db.schema import ensure_content_items_columns


def load_sources(path: str):
    with open(path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f) or {}
    return data.get('sources', [])


def run_ingestion(db: Session) -> dict:
    """Run ingestion using an existing SQLAlchemy session."""
    sources = load_sources(settings.sources_yaml)
    total_inserted = 0
    total_skipped = 0

    for src in sources:
        if src.get('type') != 'rss':
            continue
        items = fetch_rss(src['url'], src['name'], src.get('tags'))
        res = upsert_items(
            db,
            items,
            openai_api_key=settings.openai_api_key,
            bilingual=(settings.app_lang == 'bilingual'),
        )
        total_inserted += res['inserted']
        total_skipped += res['skipped']

    return {'inserted': total_inserted, 'skipped': total_skipped}


def run_once() -> dict:
    """Run ingestion end-to-end (creates its own DB session)."""
    engine = make_engine(settings.database_url)
    Base.metadata.create_all(bind=engine)
    ensure_content_items_columns(engine)
    SessionLocal = make_session_factory(engine)
    with SessionLocal() as db:  # type: ignore
        return run_ingestion(db)


def main():
    print(run_once())


if __name__ == '__main__':
    main()
