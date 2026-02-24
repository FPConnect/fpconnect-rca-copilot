"""Ticket-related ORM models."""

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)

from app.core.database import Base


class Ticket(Base):
    """Support ticket for a device or system issue."""

    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(
        Enum("open", "in_progress", "resolved", "closed", name="ticket_status"),
        default="open",
        nullable=False,
    )
    priority = Column(
        Enum("low", "medium", "high", "critical", name="ticket_priority"),
        default="medium",
        nullable=False,
    )
    device_id = Column(String, nullable=True)
    location = Column(String, nullable=True)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)


class TicketLog(Base):
    """Audit log entry for ticket changes."""

    __tablename__ = "ticket_logs"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String, nullable=False)
    detail = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class RCASuggestion(Base):
    """RCA suggestion generated for a ticket."""

    __tablename__ = "rca_suggestions"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False)
    cause = Column(Text, nullable=False)
    confidence = Column(Float, default=0.0)
    resolution = Column(Text, nullable=True)
    similar_incidents = Column(Text, nullable=True)  # comma-separated ticket IDs
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class KBArticle(Base):
    """Knowledge base article for known issues and resolutions."""

    __tablename__ = "kb_articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    tags = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
