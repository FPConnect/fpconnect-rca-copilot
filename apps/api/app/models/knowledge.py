"""Isolated, reviewable knowledge workspaces for OPSPECTA.

These workspaces scope the *knowledge base only*. They are not a blanket
claim of tenant isolation for tickets, attachments or other app resources.
"""
from sqlalchemy import (
    CheckConstraint, Column, DateTime, ForeignKey, Integer, String,
    UniqueConstraint, func,
)

from app.core.base import Base


class KnowledgeWorkspace(Base):
    __tablename__ = "knowledge_workspaces"

    id = Column(Integer, primary_key=True)
    slug = Column(String(64), nullable=False, unique=True, index=True)
    name = Column(String(160), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class KnowledgeMembership(Base):
    __tablename__ = "knowledge_memberships"

    id = Column(Integer, primary_key=True)
    workspace_id = Column(Integer, ForeignKey("knowledge_workspaces.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    # A membership is explicitly administered, never self-declared.
    membership_role = Column(String(20), nullable=False, default="member")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("workspace_id", "user_id", name="uq_kb_workspace_membership"),
        CheckConstraint("membership_role IN ('member', 'manager')", name="ck_kb_membership_role"),
    )


class KnowledgeAudit(Base):
    """Metadata-only trail of article classification and access decisions."""

    __tablename__ = "knowledge_audit"

    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey("kb_articles.id"), nullable=False, index=True)
    actor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_type = Column(String(32), nullable=False)
    version = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class KnowledgeMembershipAudit(Base):
    """Immutable metadata for membership grant/revocation accountability."""

    __tablename__ = "knowledge_membership_audit"

    id = Column(Integer, primary_key=True)
    workspace_id = Column(Integer, ForeignKey("knowledge_workspaces.id"), nullable=False, index=True)
    affected_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    actor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String(16), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
