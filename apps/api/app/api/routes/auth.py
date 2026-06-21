"""Authentication routes: register and login."""

from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.api.deps import get_current_user_id
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    validate_password,
    verify_password,
)
from app.crud.user import create_user, get_user_by_email, get_user_by_id, update_user
from app.schemas.user import (
    ROLE_ACCESS_LEVELS,
    RefreshTokenRequest,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
)

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user account."""
    if user_data.role == "technician":
        user_data.role = "user"
    if user_data.role not in ROLE_ACCESS_LEVELS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"role": ["invalid role"]},
        )

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
    return create_user(db, user_data)


@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Authenticate a user and return a JWT token."""
    user = get_user_by_email(db, credentials.email)
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    payload = {"sub": str(user.id), "role": user.role, "access_level": user.access_level}
    token = create_access_token(payload)
    refresh_token = create_refresh_token(payload)
    return TokenResponse(access_token=token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(payload: RefreshTokenRequest):
    """Exchange a valid refresh token for a new access token."""
    token = payload.refresh_token
    try:
        decoded = decode_token(token, settings.refresh_secret_key)
    except JWTError as exc:
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
