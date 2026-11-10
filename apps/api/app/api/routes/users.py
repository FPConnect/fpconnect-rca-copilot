"""Hierarchical user administration routes."""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
import structlog

from app.api.deps import AuthenticatedUser, require_access_level
from app.api.tenant import TenantContext, get_tenant_context
from app.core.database import get_db
from app.core.security import limiter, validate_password
from app.models.organization import OrganizationMembership
from app.models.user import User
from app.crud.user import (
    create_managed_user,
    get_user_by_email,
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


def _membership_response(user: User, membership: OrganizationMembership) -> UserResponse:
    return UserResponse.model_validate(user).model_copy(update={
        "role": membership.role,
        "access_level": ROLE_ACCESS_LEVELS[membership.role],
        "is_active": membership.is_active and user.is_active,
    })


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
    tenant: TenantContext = Depends(get_tenant_context),
):
    """List real accounts for administrators and masters."""
    return [_membership_response(user, membership) for user, membership in list_users(db, tenant.organization_id)]


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("20/minute")
def create_user_account(
    request: Request,
    payload: ManagedUserCreate,
    db: Session = Depends(get_db),
    actor: AuthenticatedUser = Depends(require_access_level(4)),
    tenant: TenantContext = Depends(get_tenant_context),
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
        created = create_managed_user(db, payload, tenant.organization_id)
        log.info(
            "user_account_created",
            actor_id=actor.id,
            target_id=created.id,
            assigned_role=created.role,
        )
        membership = db.query(OrganizationMembership).filter_by(
            user_id=created.id, organization_id=tenant.organization_id
        ).one()
        return _membership_response(created, membership)
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
    tenant: TenantContext = Depends(get_tenant_context),
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
    result = (
        db.query(User, OrganizationMembership)
        .join(OrganizationMembership, OrganizationMembership.user_id == User.id)
        .filter(
            User.id == user_id,
            OrganizationMembership.organization_id == tenant.organization_id,
        )
        .with_for_update(of=User)
        .first()
    )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    target, membership = result
    _ensure_subordinate(actor, ROLE_ACCESS_LEVELS[membership.role])
    if payload.role is not None:
        _ensure_subordinate(actor, ROLE_ACCESS_LEVELS[payload.role])
    previous_role = membership.role
    previous_status = membership.is_active
    updated = update_managed_user(db, membership, payload)
    log.info(
        "user_account_access_updated",
        actor_id=actor.id,
        target_id=target.id,
        organization_id=tenant.organization_id,
        previous_role=previous_role,
        assigned_role=updated.role,
        previous_active=previous_status,
        active=updated.is_active,
    )
    return _membership_response(target, updated)
