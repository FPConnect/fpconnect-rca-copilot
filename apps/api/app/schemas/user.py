"""Pydantic schemas for user-related endpoints."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

ROLE_ACCESS_LEVELS = {"visitor": 1, "user": 2, "manager": 3, "admin": 4, "master": 5}


class UserCreate(BaseModel):
    """Public account-registration payload.

    Roles are deliberately absent: public callers can only create regular users.
    """

    email: EmailStr
    password: str = Field(..., min_length=12, max_length=128)
    full_name: Optional[str] = Field(default=None, max_length=120)
    phone_number: Optional[str] = Field(default=None, max_length=32)


class VerificationCodeRequest(BaseModel):
    """Schema for requesting a registration verification code."""

    email: EmailStr
    phone_number: str = Field(..., min_length=10, max_length=32)


class VerificationCodeResponse(BaseModel):
    """Schema returned after a verification code is generated/sent."""

    status: str
    to: str
    provider: str
    expires_in_seconds: int
    verification_code: Optional[str] = None


class UserCreateVerified(UserCreate):
    """Schema for creating a user after phone verification."""

    verification_code: str = Field(..., min_length=4, max_length=8)


class UserLogin(BaseModel):
    """Schema for user login."""

    email: EmailStr
    password: str = Field(..., min_length=1, max_length=128)


class UserResponse(BaseModel):
    """Schema for user response (no password)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    role: str
    access_level: int

class UserUpdate(BaseModel):
    """Schema for updating the current user profile."""

    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone_number: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    """Schema for refreshing an access token."""

    refresh_token: str


class TokenResponse(BaseModel):
    """Schema for JWT token response."""

    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
