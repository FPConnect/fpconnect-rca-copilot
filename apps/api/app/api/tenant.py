"""Server-validated tenant selection."""

from dataclasses import dataclass

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import AuthenticatedUser, get_current_user
from app.core.database import get_db
from app.models.organization import Organization, OrganizationMembership
from app.schemas.user import ROLE_ACCESS_LEVELS


@dataclass(frozen=True)
class TenantContext:
    user: AuthenticatedUser
    organization_id: int


def get_tenant_context(
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
    organization_id: int = Header(..., alias="X-Organization-Id", gt=0),
) -> TenantContext:
    """Validate the selected organization against live server-side membership."""
    membership = (
        db.query(OrganizationMembership)
        .join(
            Organization,
            OrganizationMembership.organization_id == Organization.id,
        )
        .filter(
            OrganizationMembership.user_id == current_user.id,
            OrganizationMembership.is_active.is_(True),
            Organization.id == organization_id,
            Organization.is_active.is_(True),
        )
        .one_or_none()
    )
    if membership is None or membership.role not in ROLE_ACCESS_LEVELS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No active organization membership",
        )
    return TenantContext(
        user=AuthenticatedUser(
            id=current_user.id,
            role=membership.role,
            access_level=ROLE_ACCESS_LEVELS[membership.role],
        ),
        organization_id=membership.organization_id,
    )
