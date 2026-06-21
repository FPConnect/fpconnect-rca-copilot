"""RBAC middleware and dependencies for permission checking."""

from datetime import datetime
from typing import List, Optional
from fastapi import Depends, Header, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.crud.rbac import (
    get_effective_permissions,
    get_role,
    get_access_level_value,
    can_user_modify_target,
)
from app.models.rbac import AccessLevel
from app.models.user import User


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


def get_current_user_with_role(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
) -> User:
    """Get the current user with their role information."""
    user = db.query(User).filter(User.id == current_user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


def get_user_access_level(user: User, db: Session) -> int:
    """
    Get the access level for a user.
    If user has a role_id, use that role's access level.
    Otherwise, fall back to legacy role enum mapping.
    """
    if user.role_id:
        role = get_role(db, user.role_id)
        if role:
            return get_access_level_value(role.access_level)
    
    # Fallback to legacy role enum
    role_mapping = {
        "technician": AccessLevel.usuario.value,
        "manager": AccessLevel.gerente.value,
        "admin": AccessLevel.administrador.value,
    }
    return role_mapping.get(user.role, AccessLevel.visitante.value)


def require_permission(permission_name: str):
    """
    Dependency factory that checks if the current user has a specific permission.
    Usage: @router.get("/endpoint", dependencies=[Depends(require_permission("view_reports"))])
    """
    async def check_permission(
        request: Request,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user_with_role),
    ):
        effective_permissions = get_effective_permissions(db, current_user.id)
        
        # Master level always has all permissions
        user_level = get_user_access_level(current_user, db)
        if user_level >= AccessLevel.master.value:
            return current_user
        
        if permission_name not in effective_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permission: {permission_name}",
            )
        return current_user
    
    return check_permission


def require_access_level(min_level: AccessLevel):
    """
    Dependency factory that checks if the current user has minimum access level.
    Usage: @router.get("/admin", dependencies=[Depends(require_access_level(AccessLevel.administrador))])
    """
    async def check_access_level(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user_with_role),
    ):
        user_level = get_user_access_level(current_user, db)
        required_level = get_access_level_value(min_level)
        
        if user_level < required_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient access level. Required: {min_level.name}, Current: {user_level}",
            )
        return current_user
    
    return check_access_level


def require_master():
    """Dependency that requires Master access level."""
    return require_access_level(AccessLevel.master)


def can_modify_user(actor: User, target_user: User, db: Session) -> bool:
    """
    Check if actor can modify target_user.
    Rules:
    - Users cannot modify themselves
    - Actor must have higher access level than target
    - Only Master can modify other Masters or Administrators
    """
    if actor.id == target_user.id:
        return False
    
    actor_level = get_user_access_level(actor, db)
    target_level = get_user_access_level(target_user, db)
    
    if not can_user_modify_target(actor_level, target_level):
        return False
    
    # Special protection for high-level users
    if target_level >= AccessLevel.administrador.value and actor_level < AccessLevel.master.value:
        return False
    
    return True


class RBACMiddleware:
    """
    Middleware for logging and additional RBAC checks.
    Can be used to add IP-based restrictions or other security layers.
    """
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        # Add request IP to state for audit logging
        if scope["type"] == "http":
            client = scope.get("client")
            if client:
                scope["state"]["client_ip"] = client[0]
        
        return await self.app(scope, receive, send)
