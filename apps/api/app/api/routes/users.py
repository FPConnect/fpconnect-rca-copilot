"""Hierarchical user administration routes."""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
import structlog

from app.api.deps import AuthenticatedUser, require_access_level
from app.core.database import get_db
from app.core.security import limiter, validate_password
from app.crud.user import (
    create_managed_user,
    get_user_by_email,
    get_user_by_id,
    list_users,
    update_managed_user,
)
from app.schemas.user import (
    ROLE_ACCESS_LEVELS,
    ManagedUserCreate,
    ManagedUserUpdate,
    UserResponse,
)

router = APIRouter()
log = structlog.get_logger()


def _ensure_subordinate(actor: AuthenticatedUser, target_level: int) -> None:
    if target_level >= actor.access_level:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only manage users below your access level",
        )


@router.get("", response_model=list[UserResponse])
def get_users(
    db: Session = Depends(get_db),
    _: AuthenticatedUser = Depends(require_access_level(4)),
):
    """List real accounts for administrators and masters."""
    return list_users(db)


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("20/minute")
def create_user_account(
    request: Request,
    payload: ManagedUserCreate,
    db: Session = Depends(get_db),
    actor: AuthenticatedUser = Depends(require_access_level(4)),
):
    """Create a subordinate account with a canonical server-side access level."""
    del request
    _ensure_subordinate(actor, ROLE_ACCESS_LEVELS[payload.role])
    is_valid, password_errors = validate_password(payload.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"password": password_errors},
        )
    if get_user_by_email(db, str(payload.email)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )
    try:
        created = create_managed_user(db, payload)
        log.info(
            "user_account_created",
            actor_id=actor.id,
            target_id=created.id,
            assigned_role=created.role,
        )
        return created
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        ) from exc


@router.patch("/{user_id}", response_model=UserResponse)
@limiter.limit("60/minute")
def update_user_account(
    request: Request,
    user_id: int,
    payload: ManagedUserUpdate,
    db: Session = Depends(get_db),
    actor: AuthenticatedUser = Depends(require_access_level(4)),
):
    """Change a subordinate account's role or active status and revoke its sessions."""
    del request
    if payload.role is None and payload.is_active is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="At least one access field is required",
        )
    if user_id == actor.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot change your own access",
        )
    target = get_user_by_id(db, user_id)
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    _ensure_subordinate(actor, target.access_level)
    if payload.role is not None:
        _ensure_subordinate(actor, ROLE_ACCESS_LEVELS[payload.role])
    previous_role = target.role
    previous_status = target.is_active
    updated = update_managed_user(db, target, payload)
    log.info(
        "user_account_access_updated",
        actor_id=actor.id,
        target_id=updated.id,
        previous_role=previous_role,
        assigned_role=updated.role,
        previous_active=previous_status,
        active=updated.is_active,
    )
    return updated
