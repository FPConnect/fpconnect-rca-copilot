"""Isolated, reviewable knowledge workspaces for OPSPECTA.

These workspaces scope the *knowledge base only*. They are not a blanket
claim of tenant isolation for tickets, attachments or other app resources.
"""
from sqlalchemy import (
    CheckConstraint, Column, DateTime, ForeignKey, Integer, String,
    Text, UniqueConstraint, func,
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
