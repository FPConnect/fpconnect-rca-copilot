"""User ORM model."""

from sqlalchemy import Column, DateTime, Enum, Integer, String, func

from app.core.database import Base


class User(Base):
    """Represents a system user (technician, manager, admin)."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    role = Column(
        Enum("admin", "manager", "technician", name="user_role"),
        default="technician",
        nullable=False,
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
