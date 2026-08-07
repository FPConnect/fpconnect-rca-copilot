"""JWT token creation and password hashing utilities."""

import hmac
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Header, HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plain-text password."""
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plain-text password against its hash."""
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a signed JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT token, returning the payload or None."""
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError:
        return None


def get_current_user_payload(authorization: Optional[str] = Header(None)) -> dict:
    """Extract and validate the current user payload from a Bearer token."""

    if settings.app_env == "development" and settings.allow_dev_anonymous_access and not authorization:
        return {"sub": "1", "role": "admin", "dev_anonymous": True}

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    token = authorization.split(" ", 1)[1]
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    return payload


def get_current_user_id(authorization: Optional[str] = Header(None)) -> int:
    """Extract the authenticated user id from the current request."""

    payload = get_current_user_payload(authorization)
    return int(payload["sub"])


def secrets_match(expected: Optional[str], provided: Optional[str]) -> bool:
    """Compare shared secrets in constant time when both values exist."""

    if not expected or not provided:
        return False
    return hmac.compare_digest(expected, provided)
