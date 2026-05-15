"""Pydantic schemas for clinical engineering playbooks and contracts."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PlaybookBase(BaseModel):
    title: str = Field(..., min_length=3)
    equipment: str = Field(..., min_length=2)
    steps: str = Field(..., min_length=5)
    files: Optional[str] = None


class PlaybookCreate(PlaybookBase):
    pass


class PlaybookUpdate(BaseModel):
    title: Optional[str] = None
    equipment: Optional[str] = None
    steps: Optional[str] = None
    files: Optional[str] = None


class PlaybookResponse(PlaybookBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SLAContractBase(BaseModel):
    equipment: str
    vendor: str
    response_time_hours: int
    penalty: Optional[str] = None
    sla_compliance: float = 100.0
    expires_at: Optional[datetime] = None


class SLAContractCreate(SLAContractBase):
    pass


class SLAContractUpdate(BaseModel):
    equipment: Optional[str] = None
    vendor: Optional[str] = None
    response_time_hours: Optional[int] = None
    penalty: Optional[str] = None
    sla_compliance: Optional[float] = None
    expires_at: Optional[datetime] = None


class SLAContractResponse(SLAContractBase):
    id: int
    created_at: Optional[datetime] = None
    days_to_expire: Optional[int] = None
    alert: Optional[str] = None

    class Config:
        from_attributes = True
