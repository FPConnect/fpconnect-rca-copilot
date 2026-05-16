"""Playbook and SLA/contract ORM models for clinical engineering workflows."""

from sqlalchemy import Column, DateTime, Float, Integer, String, Text, func

from app.core.database import Base


class Playbook(Base):
    """Repair or diagnostic procedure maintained by clinical engineering."""

    __tablename__ = "playbooks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    equipment = Column(String, nullable=False)
    steps = Column(Text, nullable=False)
    files = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class SLAContract(Base):
    """Contract/SLA parameters for an equipment family or installed asset."""

    __tablename__ = "sla_contracts"

    id = Column(Integer, primary_key=True, index=True)
    equipment = Column(String, nullable=False)
    vendor = Column(String, nullable=False)
    response_time_hours = Column(Integer, nullable=False)
    penalty = Column(Text, nullable=True)
    sla_compliance = Column(Float, default=100.0, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
