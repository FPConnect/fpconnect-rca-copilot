"""Notification routes with explicit delivery status."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_id
from app.core.config import settings
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
    """Return a preview response only when running in development."""
    if settings.app_env != "development":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="SMS delivery is not configured for this deployment",
        )

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
        status="preview",
        to=phone_number,
        provider="development-mock",
        delivered=False,
    )
