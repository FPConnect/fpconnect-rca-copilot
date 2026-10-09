"""Shared authentication and authorization dependencies."""

from dataclasses import dataclass
from typing import Optional

from fastapi import Depends, Header, HTTPException, status

from app.core.security import decode_access_token


@dataclass(frozen=True)
class AuthenticatedUser:
    id: int
    role: str
    access_level: int


def get_current_user(authorization: Optional[str] = Header(None)) -> AuthenticatedUser:
    """Validate a bearer token and return its signed authorization context."""
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
    try:
        user_id = int(payload["sub"])
        access_level = int(payload.get("access_level", 0))
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token claims",
        ) from exc
    if user_id <= 0 or access_level not in range(1, 6):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token claims")
    return AuthenticatedUser(id=user_id, role=str(payload.get("role", "user")), access_level=access_level)


def get_current_user_id(current_user: AuthenticatedUser = Depends(get_current_user)) -> int:
    return current_user.id


def require_access_level(minimum: int):
    """Build a dependency that enforces the signed RBAC access level."""
    def dependency(current_user: AuthenticatedUser = Depends(get_current_user)) -> AuthenticatedUser:
        if current_user.access_level < minimum:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return current_user

    return dependency
