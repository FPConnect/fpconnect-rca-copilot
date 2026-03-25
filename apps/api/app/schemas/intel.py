"""Pydantic schemas for the Intel/Radar feature."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class IntelItemResponse(BaseModel):
    id: int
    source: str
    url: str
    title: str
    published_at: Optional[datetime] = None
    fetched_at: datetime
    topic: Optional[str] = None
    summary_pt: Optional[str] = None
    summary_en: Optional[str] = None

    class Config:
        from_attributes = True


class IntelTopicsResponse(BaseModel):
    topics: list[str]


class IntelIngestResponse(BaseModel):
    inserted: int
    skipped: int
    sources: int
