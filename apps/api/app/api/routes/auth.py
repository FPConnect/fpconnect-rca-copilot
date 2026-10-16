"""Authentication routes: register and login."""

from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import secrets

from fastapi import APIRouter, Depends, HTTPException, Request, status
from jwt import InvalidTokenError
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.api.deps import get_current_user_id
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    limiter,
    password_needs_rehash,
    validate_password,
    verify_password,
)
from app.crud.user import create_user, get_user_by_email, get_user_by_id, update_user
from app.schemas.user import (
    PasswordChange,
    RefreshTokenRequest,
    TokenResponse,
    UserCreate,
    UserCreateVerified,
    UserLogin,
    UserResponse,
    VerificationCodeRequest,
    VerificationCodeResponse,
    UserUpdate,
)

router = APIRouter()

VERIFICATION_TTL_SECONDS = 10 * 60
_verification_codes: dict[str, tuple[str, datetime]] = {}
LOGIN_RATE_LIMIT = "1000/minute" if settings.app_env == "development" else "5/minute"
REGISTRATION_RATE_LIMIT = "1000/minute" if settings.app_env == "development" else "3/minute"
REFRESH_RATE_LIMIT = "1000/minute" if settings.app_env == "development" else "20/minute"
PASSWORD_CHANGE_RATE_LIMIT = "1000/minute" if settings.app_env == "development" else "5/minute"


def _rate_limit_bucket(action: str, identifier: str) -> str:
    """Hash rate-limit subjects so addresses and tokens are never stored verbatim."""
    payload = f"{action}:{identifier.strip().lower()}".encode("utf-8")
    return hmac.new(settings.secret_key.encode("utf-8"), payload, hashlib.sha256).hexdigest()


def _client_identifier(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for", "").split(",", 1)[0].strip()
    if forwarded:
        return forwarded
    return request.client.host if request.client else "unknown"


def _enforce_shared_rate_limit(
    db: Session,
    action: str,
    identifier: str,
    max_attempts: int,
    window_seconds: int = 60,
) -> None:
    """Enforce a production-wide fixed window through the shared PostgreSQL database."""
    bind = db.get_bind()
    if settings.app_env == "development" or bind.dialect.name != "postgresql":
        return

    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(seconds=window_seconds)
    attempts = db.execute(
        text(
            """
            INSERT INTO auth_rate_limits (bucket, window_started_at, attempts)
            VALUES (:bucket, :now, 1)
            ON CONFLICT (bucket) DO UPDATE SET
                attempts = CASE
                    WHEN auth_rate_limits.window_started_at < :cutoff THEN 1
                    ELSE auth_rate_limits.attempts + 1
                END,
                window_started_at = CASE
                    WHEN auth_rate_limits.window_started_at < :cutoff THEN :now
                    ELSE auth_rate_limits.window_started_at
                END
            RETURNING attempts
            """
        ),
        {
            "bucket": _rate_limit_bucket(action, identifier),
            "now": now,
            "cutoff": cutoff,
        },
    ).scalar_one()
    db.commit()

    if attempts > max_attempts:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many attempts. Try again later.",
            headers={"Retry-After": str(window_seconds)},
        )


def _enforce_auth_limits(
    db: Session,
    request: Request,
    action: str,
    subject: str,
    subject_limit: int,
    client_limit: int,
) -> None:
    _enforce_shared_rate_limit(db, f"{action}:subject", subject, subject_limit)
    _enforce_shared_rate_limit(db, f"{action}:client", _client_identifier(request), client_limit)


def _verification_key(email: str) -> str:
    """Normalize the email key used to store a pending verification code."""
    return email.strip().lower()


def _mask_phone(phone_number: str) -> str:
    """Mask a phone number while keeping enough context for the UI."""
    digits = "".join(ch for ch in phone_number if ch.isdigit())
    if len(digits) <= 4:
        return phone_number
    return f"***{digits[-4:]}"


def _generate_verification_code() -> str:
    """Generate a six-digit registration code."""
    return f"{secrets.randbelow(1_000_000):06d}"


def _ensure_registration_allowed(email: str) -> None:
    """Allow self-registration only for explicitly approved production emails."""
    if not settings.public_registration_enabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Public registration is disabled",
        )
    allowed = set(settings.registration_allowed_emails)
    if allowed and str(email).strip().lower() not in allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Registration is not available for this email",
        )


def _validate_user_create(user_data: UserCreate, db: Session) -> None:
    """Validate password policy and email uniqueness for a regular account."""
    is_valid, password_errors = validate_password(user_data.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"password": password_errors},
        )

    existing = get_user_by_email(db, user_data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(REGISTRATION_RATE_LIMIT)
def register(request: Request, user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a regular user only when self-registration is explicitly allowed."""
    _enforce_auth_limits(db, request, "registration", str(user_data.email), 3, 10)
    _ensure_registration_allowed(str(user_data.email))
    _validate_user_create(user_data, db)
    return create_user(db, user_data)


@router.post("/verification-code", response_model=VerificationCodeResponse)
@limiter.limit(REGISTRATION_RATE_LIMIT)
def send_verification_code(request: Request, payload: VerificationCodeRequest, db: Session = Depends(get_db)):
    """Generate a development verification code; no SMS is sent."""
    _enforce_auth_limits(db, request, "registration", str(payload.email), 3, 10)
    _ensure_registration_allowed(str(payload.email))
    if settings.app_env != "development":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="SMS verification is not configured for this deployment",
        )

    if get_user_by_email(db, payload.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    digits = "".join(ch for ch in payload.phone_number if ch.isdigit())
    if len(digits) < 10:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="A valid phone number is required to send the verification code",
        )

    code = _generate_verification_code()
    now = datetime.now(timezone.utc)
    for key, (_, expires_at) in list(_verification_codes.items()):
        if expires_at <= now:
            _verification_codes.pop(key, None)
    if len(_verification_codes) >= 1000:
        oldest_key = min(_verification_codes, key=lambda key: _verification_codes[key][1])
        _verification_codes.pop(oldest_key, None)
    expires_at = now + timedelta(seconds=VERIFICATION_TTL_SECONDS)
    _verification_codes[_verification_key(str(payload.email))] = (code, expires_at)
    return VerificationCodeResponse(
        status="generated",
        to=_mask_phone(payload.phone_number),
        provider="development-mock",
        expires_in_seconds=VERIFICATION_TTL_SECONDS,
        verification_code=code,
    )


@router.post("/register/verify", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(REGISTRATION_RATE_LIMIT)
def register_verified(request: Request, user_data: UserCreateVerified, db: Session = Depends(get_db)):
    """Register a new user only after validating the phone verification code."""
    _enforce_auth_limits(db, request, "registration", str(user_data.email), 3, 10)
    _ensure_registration_allowed(str(user_data.email))
    key = _verification_key(str(user_data.email))
    stored = _verification_codes.get(key)
    if not stored:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification code not requested")

    expected_code, expires_at = stored
    if datetime.now(timezone.utc) > expires_at:
        _verification_codes.pop(key, None)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification code expired")
    if not secrets.compare_digest(expected_code, user_data.verification_code):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification code")

    _validate_user_create(user_data, db)
    user = create_user(db, user_data)
    _verification_codes.pop(key, None)
    return user


@router.post("/login", response_model=TokenResponse)
@limiter.limit(LOGIN_RATE_LIMIT)
def login(request: Request, credentials: UserLogin, db: Session = Depends(get_db)):
    """Authenticate a user and return a JWT token."""
    _enforce_auth_limits(db, request, "login", str(credentials.email), 5, 30)
    user = get_user_by_email(db, credentials.email)
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    if password_needs_rehash(user.hashed_password) and len(credentials.password.encode("utf-8")) <= 72:
        user.hashed_password = hash_password(credentials.password)
        db.add(user)
        db.commit()
    payload = {"sub": str(user.id), "role": user.role, "access_level": user.access_level}
    token = create_access_token(payload)
    refresh_token = create_refresh_token(payload)
    return TokenResponse(access_token=token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse)
@limiter.limit(REFRESH_RATE_LIMIT)
def refresh_token(request: Request, payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Exchange a valid refresh token for a new access token."""
    token = payload.refresh_token
    _enforce_auth_limits(db, request, "refresh", token, 20, 60)
    try:
        decoded = decode_token(token, settings.refresh_secret_key)
    except InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        ) from exc
    if decoded.get("type") != "refresh" or "sub" not in decoded:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    access_payload = {
        "sub": decoded["sub"],
        "role": decoded.get("role", "user"),
        "access_level": decoded.get("access_level", 2),
    }
    return TokenResponse(access_token=create_access_token(access_payload), refresh_token=token)


@router.get("/me", response_model=UserResponse)
def get_me(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """Return the currently authenticated user profile."""
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.patch("/me", response_model=UserResponse)
def update_me(
    user_data: UserUpdate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Update the currently authenticated user profile."""
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user_data.email and user_data.email != user.email:
        existing = get_user_by_email(db, str(user_data.email))
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    return update_user(db, user, user_data)


@router.post("/password")
@limiter.limit(PASSWORD_CHANGE_RATE_LIMIT)
def change_password(
    request: Request,
    payload: PasswordChange,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Replace the authenticated user's password after checking the current one."""
    _enforce_auth_limits(db, request, "password", str(user_id), 5, 15)
    user = get_user_by_id(db, user_id)
    if not user or not verify_password(payload.current_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    if payload.current_password == payload.new_password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="New password must be different from the current password",
        )

    is_valid, password_errors = validate_password(payload.new_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"password": password_errors},
        )

    user.hashed_password = hash_password(payload.new_password)
    db.add(user)
    db.commit()
    return {"status": "updated"}
