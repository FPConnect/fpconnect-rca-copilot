"""Machine ORM model."""

from sqlalchemy import Column, DateTime, Enum, Integer, String, func

from app.core.database import Base


class Machine(Base):
    """Medical machine monitored by the platform."""

    __tablename__ = "machines"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    type = Column(String, nullable=False)
    status = Column(
        Enum("online", "warning", "offline", name="machine_status"),
        default="online",
        nullable=False,
    )
    last_check = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
