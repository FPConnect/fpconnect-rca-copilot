from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi.responses import HTMLResponse
from pathlib import Path

from app.core.config import settings
from app.db.base import Base
from app.db.session import make_engine, make_session_factory
from app.db.models import ContentItem
from app.db.schema import ensure_content_items_columns

engine = make_engine(settings.database_url)
SessionLocal = make_session_factory(engine)
Base.metadata.create_all(bind=engine)
ensure_content_items_columns(engine)

app = FastAPI(title='FPConnect Intel Engine', version='0.1.0')


# --- Simple built-in UI (no frontend build needed) ---
APP_DIR = Path(__file__).resolve().parents[1]  # .../app
INDEX_HTML_PATH = APP_DIR / 'web' / 'index.html'


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get('/health')
def health():
    return {'status': 'ok'}


@app.get('/', response_class=HTMLResponse)
def home():
    """Minimal UI to test ingestion and browse items."""
    if not INDEX_HTML_PATH.exists():
        return HTMLResponse(
            '<h1>FPConnect Intel Engine</h1><p>UI file not found.</p>',
            status_code=200,
        )
    return HTMLResponse(INDEX_HTML_PATH.read_text(encoding='utf-8'))


@app.get('/items')
def list_items(topic: str | None = None, limit: int = 50, db: Session = Depends(get_db)):
    stmt = select(ContentItem)
    if topic:
        stmt = stmt.where(ContentItem.topic == topic)
    stmt = stmt.order_by(ContentItem.fetched_at.desc()).limit(limit)
    items = db.execute(stmt).scalars().all()
    return [
        {
            'source': i.source,
            'title': i.title,
            'url': i.url,
            'published_at': i.published_at,
            'topic': i.topic,
            'severity': i.severity,
            'summary_pt': i.summary_pt,
            'summary_en': i.summary_en,
            'rca': i.rca,
            'tags': i.tags,
        }
        for i in items
    ]


@app.get('/topics')
def topics(db: Session = Depends(get_db)):
    # simple aggregation
    rows = db.query(ContentItem.topic).distinct().all()
    return {'topics': sorted([r[0] for r in rows if r[0]])}


@app.post('/ingest/once')
def ingest_once(db: Session = Depends(get_db)):
    # Runs ingestion once inside the API container.
    from app.scripts.ingest_once import run_once
    stats = run_once()
    return stats
