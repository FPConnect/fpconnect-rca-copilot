"""SMS delivery integration."""

import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class SmsDeliveryError(RuntimeError):
    """Raised when the configured SMS provider fails."""


def normalize_phone(phone_number: str) -> str:
    """Normalize a phone number into E.164-ish format for provider delivery."""
    digits = "".join(ch for ch in phone_number if ch.isdigit())
    if len(digits) == 11:
        digits = f"55{digits}"
    if len(digits) < 12:
        raise ValueError("A valid mobile phone number is required")
    return f"+{digits}"


def send_sms(phone_number: str, message: str) -> dict:
    """Send an SMS through the configured provider.

    When SMS_ENABLED is false, the message is logged and reported as queued. This
    keeps staging/demo environments honest without pretending that a carrier sent it.
    """
    to_number = normalize_phone(phone_number)
    provider = settings.sms_provider.lower()

    if not settings.sms_enabled:
        logger.info("SMS disabled; queued message to %s: %s", to_number, message)
        return {"status": "queued", "to": to_number, "provider": provider, "delivered": False}

    if provider != "twilio":
        raise SmsDeliveryError(f"Unsupported SMS provider: {settings.sms_provider}")
    if not all([settings.twilio_account_sid, settings.twilio_auth_token, settings.twilio_from_number]):
        raise SmsDeliveryError("Twilio credentials are not configured")

    url = f"https://api.twilio.com/2010-04-01/Accounts/{settings.twilio_account_sid}/Messages.json"
    try:
        response = httpx.post(
            url,
            data={"From": settings.twilio_from_number, "To": to_number, "Body": message},
            auth=(settings.twilio_account_sid, settings.twilio_auth_token),
            timeout=10,
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise SmsDeliveryError("SMS provider request failed") from exc

    payload = response.json()
    return {
        "status": payload.get("status", "sent"),
        "to": to_number,
        "provider": provider,
        "delivered": True,
    }
