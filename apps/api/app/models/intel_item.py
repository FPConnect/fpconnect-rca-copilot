"""Intel/Radar content item model.

Stores public information ingested from RSS/APIs and summarized for the FPConnect app.
"""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text

from app.core.database import Base


class IntelItem(Base):
    __tablename__ = "intel_items"

    id = Column(Integer, primary_key=True, index=True)

    source = Column(String(200), nullable=False)
    url = Column(Text, nullable=False)
    title = Column(Text, nullable=False)

    published_at = Column(DateTime, nullable=True)
    fetched_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    content_text = Column(Text, nullable=True)
    content_hash = Column(String(64), nullable=False, index=True)

    topic = Column(String(120), nullable=True)

    summary_pt = Column(Text, nullable=True)
    summary_en = Column(Text, nullable=True)

    processed = Column(Boolean, default=True, nullable=False)
