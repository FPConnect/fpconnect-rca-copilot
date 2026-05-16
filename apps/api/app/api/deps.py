"""Shared FastAPI dependencies for API routes."""

from typing import Optional

from fastapi import Header, HTTPException, status

from app.core.security import decode_access_token


def get_current_user_id(authorization: Optional[str] = Header(None)) -> int:
    """Extract and validate the current user ID from the Authorization header."""
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
    return int(payload["sub"])
