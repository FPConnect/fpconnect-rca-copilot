"""Schemas for notification delivery endpoints."""

from pydantic import BaseModel


class SmsRequest(BaseModel):
    """SMS notification request body."""

    message: str


class SmsResponse(BaseModel):
    """SMS notification delivery status."""

    status: str
    to: str
    provider: str
    delivered: bool
