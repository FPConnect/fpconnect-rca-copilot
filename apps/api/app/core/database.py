"""SQLAlchemy database setup."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.base import Base as Base
from app.core.config import settings

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False}
    if settings.database_url.startswith("sqlite")
    else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dependency that provides a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
