"""Notification routes for user communication preferences."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_id
from app.core.database import get_db
from app.crud.user import get_user_by_id
from app.schemas.notification import SmsNotificationRequest, SmsNotificationResponse

router = APIRouter()


def _normalize_phone(phone_number: str | None) -> str:
    """Return a trimmed phone number or an empty string when it is missing."""
    return phone_number.strip() if phone_number else ""


@router.post("/sms", response_model=SmsNotificationResponse)
def send_sms_notification(
    payload: SmsNotificationRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Send an SMS notification to the current user's registered phone number.

    The current implementation is a safe development/mock provider. It validates
    the authenticated user and phone number, then returns the delivery contract
    expected by the web client without storing SMS messages or credentials.
    """
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    phone_number = _normalize_phone(user.phone_number)
    if len("".join(ch for ch in phone_number if ch.isdigit())) < 10:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="A valid phone number is required to send SMS notifications",
        )

    return SmsNotificationResponse(
        status="sent",
        to=phone_number,
        provider="development-mock",
        delivered=True,
    )
