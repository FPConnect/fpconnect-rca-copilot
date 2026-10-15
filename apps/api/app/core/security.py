"""Authentication, password policy, JWT, and rate-limit utilities."""

import base64
import binascii
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import re
from typing import Optional

import bcrypt
import jwt
from jwt import InvalidTokenError
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings

RATE_LIMIT_STORAGE_URI = "memory://" if settings.app_env == "development" else settings.redis_url
limiter = Limiter(key_func=get_remote_address, storage_uri=RATE_LIMIT_STORAGE_URI)

ALGORITHM = settings.algorithm
ACCESS_TTL_MINUTES = settings.access_token_expire_minutes
REFRESH_TTL_DAYS = settings.refresh_token_expire_days


def hash_password(password: str) -> str:
    """Hash a plain-text password using bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def _decode_adapted_base64(value: str) -> bytes:
    """Decode Passlib's unpadded base64 variant used by legacy hashes."""
    normalized = value.replace(".", "+")
    normalized += "=" * (-len(normalized) % 4)
    return base64.b64decode(normalized, validate=True)


def _verify_legacy_pbkdf2_sha256(plain: str, hashed: str) -> bool:
    """Verify hashes created by the former Passlib PBKDF2-SHA256 setup."""
    try:
        empty, scheme, rounds_value, salt_value, checksum_value = hashed.split("$")
        if empty or scheme != "pbkdf2-sha256":
            return False
        rounds = int(rounds_value)
        if rounds < 1_000 or rounds > 10_000_000:
            return False
        salt = _decode_adapted_base64(salt_value)
        expected = _decode_adapted_base64(checksum_value)
        actual = hashlib.pbkdf2_hmac(
            "sha256",
            plain.encode("utf-8"),
            salt,
            rounds,
            dklen=len(expected),
        )
        return hmac.compare_digest(actual, expected)
    except (TypeError, ValueError, binascii.Error):
        return False


def verify_password(plain: str, hashed: str) -> bool:
    """Verify current bcrypt hashes and supported legacy PBKDF2 hashes."""
    if hashed.startswith("$pbkdf2-sha256$"):
        return _verify_legacy_pbkdf2_sha256(plain, hashed)
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except (TypeError, ValueError):
        return False


def password_needs_rehash(hashed: str) -> bool:
    """Return whether a verified password should be upgraded to bcrypt."""
    return not hashed.startswith(("$2a$", "$2b$", "$2y$"))


def validate_password(password: str) -> tuple[bool, list[str]]:
    """Validate enterprise password complexity requirements."""
    errors: list[str] = []
    if len(password) < 12:
        errors.append("min 12 chars")
    if len(password.encode("utf-8")) > 72:
        errors.append("max 72 UTF-8 bytes")
    if not re.search(r"[A-Z]", password):
        errors.append("1 uppercase")
    if not re.search(r"[a-z]", password):
        errors.append("1 lowercase")
    if not re.search(r"\d", password):
        errors.append("1 digit")
    if not re.search(r"[^A-Za-z0-9]", password):
        errors.append("1 special character")
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
    to_encode.update(
        {
            "exp": now + ttl,
            "iat": now,
            "nbf": now,
            "iss": settings.jwt_issuer,
            "aud": settings.jwt_audience,
            "type": "access",
        }
    )
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
            "iss": settings.jwt_issuer,
            "aud": settings.jwt_audience,
            "type": "refresh",
        }
    )
    return jwt.encode(to_encode, settings.refresh_secret_key, algorithm=ALGORITHM)


def decode_token(token: str, secret: str) -> dict:
    """Decode a JWT token with the supplied secret."""
    return jwt.decode(
        token,
        secret,
        algorithms=[ALGORITHM],
        audience=settings.jwt_audience,
        issuer=settings.jwt_issuer,
    )


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and verify an access token, returning the payload or None."""
    try:
        payload = decode_token(token, settings.secret_key)
    except InvalidTokenError:
        return None
    if payload.get("type") not in (None, "access"):
        return None
    return payload
