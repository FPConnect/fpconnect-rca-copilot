"""CRUD operations for User model."""

from typing import Optional

from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import ROLE_ACCESS_LEVELS, UserCreate, UserUpdate


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Retrieve a user by email address."""
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Retrieve a user by ID."""
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, user_data: UserCreate) -> User:
    """Create a new user with a hashed password."""
    db_user = User(
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name,
        phone_number=user_data.phone_number,
        role=user_data.role,
        access_level=ROLE_ACCESS_LEVELS.get(user_data.role, 2),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


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
