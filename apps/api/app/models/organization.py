"""Organization identity groundwork; operational resources are not yet scoped."""

from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func

from app.core.base import Base


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True)
    slug = Column(String(64), nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True, server_default="true")


class OrganizationMembership(Base):
    """An independently revocable membership of a user in an organization."""

    __tablename__ = "organization_memberships"
    __table_args__ = (
        UniqueConstraint("user_id", "organization_id", name="uq_membership_user_organization"),
        CheckConstraint(
            "role IN ('master', 'admin', 'manager', 'user', 'visitor')",
            name="ck_membership_role",
        ),
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    organization_id = Column(
        Integer, ForeignKey("organizations.id"), nullable=False, index=True
    )
    is_active = Column(Boolean, nullable=False, default=True, server_default="true")
    role = Column(String(16), nullable=False, default="visitor", server_default="visitor")


class TenantProvisionAudit(Base):
    """Transactional provisioning record; protect database writes and audit access."""

    __tablename__ = "tenant_provision_audit"

    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    operator = Column(String(255), nullable=False)
    change_reference = Column(String(255), nullable=False)
    machine_ids = Column(Text, nullable=False)
    ticket_ids = Column(Text, nullable=False, default="[]", server_default="[]")
    other_resource_ids = Column(Text, nullable=False, default="{}", server_default="{}")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
