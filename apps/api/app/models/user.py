"""User ORM model."""

from sqlalchemy import Boolean, Column, DateTime, Enum, Integer, String, func

from app.core.base import Base


class User(Base):
    """Represents a system user (technician, manager, admin)."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    role = Column(
        Enum("master", "admin", "manager", "user", "visitor", name="user_role"),
        default="user",
        nullable=False,
    )
    access_level = Column(Integer, default=2, nullable=False)
    is_active = Column(Boolean, default=True, server_default="true", nullable=False)
    token_version = Column(Integer, default=0, server_default="0", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
