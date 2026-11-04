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

from app.core.base import Base


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
    root_cause = Column(Text, nullable=True)
    recommendation = Column(Text, nullable=True)
    analysis_completed = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)


class TicketAttachment(Base):
    """Image or document attached to a support ticket."""

    __tablename__ = "ticket_attachments"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False)
    uploader_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    object_key = Column(String, nullable=False, unique=True)
    filename = Column(String, nullable=False)
    content_type = Column(String, nullable=False)
    size_bytes = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


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
    """Governed KB article with explicit authorship and visibility.

    Existing unclassified records are kept in legacy_quarantine and cannot
    be retrieved in semantic search until a human has safely classified them.
    """

    __tablename__ = "kb_articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    tags = Column(String, nullable=True)
    embedding = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    workspace_id = Column(Integer, ForeignKey("knowledge_workspaces.id"), nullable=True, index=True)
    visibility = Column(String(16), server_default="private", default="private", nullable=False)
    review_status = Column(String(24), server_default="legacy_quarantine", nullable=False)
    category = Column(String(40), server_default="unclassified", default="unclassified", nullable=False)
    equipment_family = Column(String(100), nullable=True)
    manufacturer = Column(String(100), nullable=True)
    model_code = Column(String(100), nullable=True)
    failure_code = Column(String(100), nullable=True)
    source_ref = Column(String(240), nullable=True)
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    version = Column(Integer, server_default="1", default=1, nullable=False)
