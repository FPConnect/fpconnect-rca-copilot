"""Schemas for notification delivery endpoints."""

from pydantic import BaseModel, Field


class SmsNotificationRequest(BaseModel):
    """Payload for sending an SMS notification to the current user."""

    message: str = Field(..., min_length=1, max_length=320)


class SmsNotificationResponse(BaseModel):
    """Delivery result returned by the SMS notification endpoint."""

    status: str
    to: str
    provider: str
    delivered: bool
