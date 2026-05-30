"""Authentication, password policy, JWT, and rate-limit utilities."""

from datetime import datetime, timedelta, timezone
import re
from typing import Optional

import bcrypt
from jose import JWTError, jwt
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings

limiter = Limiter(key_func=get_remote_address)

ALGORITHM = settings.algorithm
ACCESS_TTL_MINUTES = settings.access_token_expire_minutes
REFRESH_TTL_DAYS = settings.refresh_token_expire_days


def hash_password(password: str) -> str:
    """Hash a plain-text password using bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plain-text password against its hash."""
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def validate_password(password: str) -> tuple[bool, list[str]]:
    """Validate enterprise password complexity requirements."""
    errors: list[str] = []
    if len(password) < 12:
        errors.append("min 12 chars")
    if not re.search(r"[A-Z]", password):
        errors.append("1 uppercase")
    if not re.search(r"[a-z]", password):
        errors.append("1 lowercase")
    if not re.search(r"\d", password):
        errors.append("1 digit")
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?]", password):
        errors.append("1 special")
    return len(errors) == 0, errors


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
    expires: Optional[timedelta] = None,
) -> str:
    """Create a signed JWT access token."""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    ttl = expires_delta or expires or timedelta(minutes=ACCESS_TTL_MINUTES)
    to_encode.update({"exp": now + ttl, "iat": now, "nbf": now, "type": "access"})
    return jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """Create a signed JWT refresh token with a separate secret."""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    to_encode.update(
        {
            "exp": now + timedelta(days=REFRESH_TTL_DAYS),
            "iat": now,
            "nbf": now,
            "type": "refresh",
        }
    )
    return jwt.encode(to_encode, settings.refresh_secret_key, algorithm=ALGORITHM)


def decode_token(token: str, secret: str) -> dict:
    """Decode a JWT token with the supplied secret."""
    return jwt.decode(token, secret, algorithms=[ALGORITHM])


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and verify an access token, returning the payload or None."""
    try:
        payload = decode_token(token, settings.secret_key)
    except JWTError:
        return None
    if payload.get("type") not in (None, "access"):
        return None
    return payload
