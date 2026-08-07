"""Pydantic schemas for machines."""

from datetime import datetime

from pydantic import BaseModel


class MachineResponse(BaseModel):
    id: int
    code: str
    name: str
    location: str
    type: str
    model: str | None = None
    criticality: str = "Média"
    last_failure: str | None = None
    recurrent_failures: int = 0
    status: str
    last_check: datetime

    class Config:
        from_attributes = True
