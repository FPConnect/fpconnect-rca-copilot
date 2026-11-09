"""CRUD operations for User model."""

from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User
from app.models.organization import OrganizationMembership
from app.schemas.user import (
    ROLE_ACCESS_LEVELS,
    ManagedUserCreate,
    ManagedUserUpdate,
    UserCreate,
    UserUpdate,
)


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Retrieve a user by email address."""
    normalized = str(email).strip().lower()
    return db.query(User).filter(func.lower(User.email) == normalized).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Retrieve a user by ID."""
    return db.query(User).filter(User.id == user_id).first()


def list_users(db: Session, organization_id: int):
    """Return accounts in a stable order for access administration."""
    return (
        db.query(User, OrganizationMembership)
        .join(OrganizationMembership, OrganizationMembership.user_id == User.id)
        .filter(
            OrganizationMembership.organization_id == organization_id,
        )
        .order_by(User.created_at.desc(), User.id.desc())
        .all()
    )


def create_user(db: Session, user_data: UserCreate) -> User:
    """Create a new user with a hashed password."""
    db_user = User(
        email=str(user_data.email).strip().lower(),
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name,
        phone_number=user_data.phone_number,
        role="user",
        access_level=ROLE_ACCESS_LEVELS["user"],
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_managed_user(db: Session, user_data: ManagedUserCreate, organization_id: int) -> User:
    """Create an account with a server-derived access level."""
    db_user = User(
        email=str(user_data.email).strip().lower(),
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name,
        phone_number=user_data.phone_number,
        role=user_data.role,
        access_level=ROLE_ACCESS_LEVELS[user_data.role],
        is_active=True,
    )
    db.add(db_user)
    db.flush()
    db.add(OrganizationMembership(user_id=db_user.id, organization_id=organization_id, role=user_data.role))
    db.commit()
    db.refresh(db_user)
    return db_user


def update_managed_user(db: Session, membership: OrganizationMembership, user_data: ManagedUserUpdate):
    """Update only this organization; authorization rechecks it on every request."""
    if user_data.role is not None:
        membership.role = user_data.role
    if user_data.is_active is not None:
        membership.is_active = user_data.is_active
    db.commit()
    db.refresh(membership)
    return membership


def update_user(db: Session, user: User, user_data: UserUpdate) -> User:
    """Update editable profile fields for an existing user."""
    if user_data.email is not None:
        user.email = str(user_data.email)
    if user_data.full_name is not None:
        user.full_name = user_data.full_name
    if user_data.phone_number is not None:
        user.phone_number = user_data.phone_number
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
