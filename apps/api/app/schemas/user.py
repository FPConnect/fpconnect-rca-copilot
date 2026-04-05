"""Pydantic schemas for user-related endpoints."""

from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """Schema for creating a new user."""

    email: EmailStr
    password: str = Field(min_length=12, max_length=128)
    full_name: Optional[str] = None
    role: str = "technician"


class UserLogin(BaseModel):
    """Schema for user login."""

    email: EmailStr
    password: str = Field(max_length=128)


class UserResponse(BaseModel):
    """Schema for user response (no password)."""

    id: int
    email: str
    full_name: Optional[str] = None
    role: str

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Schema for JWT token response."""

    access_token: str
    token_type: str = "bearer"
