"""Notification delivery routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.routes.auth import get_current_user_id
from app.core.database import get_db
from app.crud.user import get_user_by_id
from app.schemas.notification import SmsRequest, SmsResponse
from app.services.sms_service import SmsDeliveryError, send_sms

router = APIRouter()


@router.post("/sms", response_model=SmsResponse)
def send_sms_notification(
    payload: SmsRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Send an SMS notification to the authenticated user's registered phone."""
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not user.phone_number:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Register a mobile phone before enabling SMS notifications",
        )
    try:
        return send_sms(user.phone_number, payload.message)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except SmsDeliveryError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
