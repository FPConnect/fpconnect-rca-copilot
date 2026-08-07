from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from datetime import datetime
from app.db.base import Base


class ContentItem(Base):
    __tablename__ = 'content_items'

    id = Column(Integer, primary_key=True)
    source = Column(String(200), nullable=False)
    url = Column(Text, nullable=False)
    title = Column(Text, nullable=False)
    published_at = Column(DateTime, nullable=True)
    fetched_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    content_text = Column(Text, nullable=True)
    content_hash = Column(String(64), nullable=False, index=True)

    # Processing outputs
    topic = Column(String(120), nullable=True, index=True)
    severity = Column(String(32), nullable=True, index=True)
    summary_en = Column(Text, nullable=True)
    summary_pt = Column(Text, nullable=True)
    rca = Column(Text, nullable=True)

    tags = Column(String(400), nullable=True)
    processed = Column(Boolean, default=False, nullable=False)
