"""Pydantic schemas for machines."""

from datetime import datetime

from pydantic import BaseModel


class MachineResponse(BaseModel):
    id: int
    code: str
    name: str
    location: str
    type: str
    status: str
    last_check: datetime

    class Config:
        from_attributes = True
