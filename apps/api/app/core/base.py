"""Shared SQLAlchemy declarative metadata without runtime side effects."""

from sqlalchemy.orm import declarative_base


Base = declarative_base()
