"""Shared authentication and authorization dependencies."""

from dataclasses import dataclass
from typing import Optional

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.crud.user import get_user_by_id


@dataclass(frozen=True)
class AuthenticatedUser:
    id: int
    role: str
    access_level: int


def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> AuthenticatedUser:
    """Validate a token against the account's current server-side access state."""
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
        token_version = int(payload.get("ver", 0))
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token claims",
        ) from exc
    if user_id <= 0 or access_level not in range(1, 6):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token claims"
        )
    user = get_user_by_id(db, user_id)
    if (
        not user
        or not user.is_active
        or token_version != user.token_version
        or access_level != user.access_level
        or str(payload.get("role", "")) != user.role
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or revoked token",
        )
    return AuthenticatedUser(id=user.id, role=user.role, access_level=user.access_level)


def get_current_user_id(
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> int:
    return current_user.id


def require_access_level(minimum: int):
    """Build a dependency that enforces the signed RBAC access level."""

    def dependency(
        current_user: AuthenticatedUser = Depends(get_current_user),
    ) -> AuthenticatedUser:
        if current_user.access_level < minimum:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
            )
        return current_user

    return dependency
