"""RBAC models for role-based access control with hierarchy."""

from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Boolean, Text, UniqueConstraint, func, Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.core.database import Base


class AccessLevel:
    """Hierarchical access levels from 1 (lowest) to 5 (highest)."""
    visitante = 1      # Level 1: Read-only public content
    usuario = 2        # Level 2: Own profile and content management
    gerente = 3        # Level 3: User management (levels 1-2), content approval
    administrador = 4  # Level 4: System config, audit logs, full user management
    master = 5         # Level 5: Unrestricted access, can modify any permissions
    
    @classmethod
    def names(cls):
        return [cls.visitante, cls.usuario, cls.gerente, cls.administrador, cls.master]
    
    @classmethod
    def name_of(cls, value):
        mapping = {
            1: "visitante",
            2: "usuario",
            3: "gerente",
            4: "administrador",
            5: "master",
        }
        return mapping.get(value, "unknown")


class Role(Base):
    """Represents a role that can be assigned to users."""
    
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    access_level = Column(Integer, nullable=False, default=AccessLevel.visitante)
    is_system_role = Column(Boolean, default=False)  # System roles cannot be deleted
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    permissions = relationship("Permission", secondary="role_permissions", back_populates="roles")
    users = relationship("User", back_populates="role_obj")


class Permission(Base):
    """Represents a granular permission that can be granted."""
    
    __tablename__ = "permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=True)  # e.g., 'users', 'tickets', 'reports', 'settings'
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    roles = relationship("Role", secondary="role_permissions", back_populates="permissions")
    user_permissions = relationship("UserPermission", back_populates="permission")


class RolePermission(Base):
    """Association table between roles and permissions."""
    
    __tablename__ = "role_permissions"
    
    role_id = Column(Integer, ForeignKey("roles.id"), primary_key=True)
    permission_id = Column(Integer, ForeignKey("permissions.id"), primary_key=True)
    granted_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        UniqueConstraint('role_id', 'permission_id', name='uq_role_permission'),
    )


class UserPermission(Base):
    """Custom permissions granted directly to individual users (overrides role)."""
    
    __tablename__ = "user_permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    permission_id = Column(Integer, ForeignKey("permissions.id"), nullable=False)
    is_granted = Column(Boolean, default=True)  # True = grant, False = explicitly deny
    granted_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    granted_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="custom_permissions")
    grantor = relationship("User", foreign_keys=[granted_by])
    permission = relationship("Permission", back_populates="user_permissions")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'permission_id', name='uq_user_permission'),
    )


class AuditLog(Base):
    """Audit trail for permission and role changes."""
    
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    action = Column(String(50), nullable=False)  # e.g., 'role_change', 'permission_grant', 'permission_revoke'
    actor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    target_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    target_role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)
    target_permission_id = Column(Integer, ForeignKey("permissions.id"), nullable=True)
    old_value = Column(Text, nullable=True)  # JSON string of previous state
    new_value = Column(Text, nullable=True)  # JSON string of new state
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    actor = relationship("User", foreign_keys=[actor_id])
    target_user = relationship("User", foreign_keys=[target_user_id])
    target_role = relationship("Role")
    target_permission = relationship("Permission")
