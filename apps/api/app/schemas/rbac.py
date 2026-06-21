"""Pydantic schemas for RBAC operations."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr


# ============== Role Schemas ==============

class PermissionBase(BaseModel):
    """Base schema for permissions."""
    name: str
    description: Optional[str] = None
    category: Optional[str] = None


class PermissionCreate(PermissionBase):
    """Schema for creating a permission."""
    pass


class PermissionResponse(PermissionBase):
    """Schema for permission response."""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class RoleBase(BaseModel):
    """Base schema for roles."""
    name: str
    description: Optional[str] = None
    access_level: int  # 1-5


class RoleCreate(RoleBase):
    """Schema for creating a role."""
    is_system_role: bool = False
    permission_ids: Optional[List[int]] = []


class RoleUpdate(BaseModel):
    """Schema for updating a role."""
    name: Optional[str] = None
    description: Optional[str] = None
    access_level: Optional[int] = None
    permission_ids: Optional[List[int]] = None


class RoleResponse(RoleBase):
    """Schema for role response."""
    id: int
    is_system_role: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    permissions: List[PermissionResponse] = []
    
    class Config:
        from_attributes = True


# ============== User Permission Schemas ==============

class UserPermissionGrant(BaseModel):
    """Schema for granting/revoking a permission to a user."""
    user_id: int
    permission_id: int
    is_granted: bool = True
    expires_at: Optional[datetime] = None


class UserPermissionResponse(BaseModel):
    """Schema for user permission response."""
    id: int
    user_id: int
    permission_id: int
    permission_name: str
    is_granted: bool
    granted_by: Optional[int] = None
    granted_at: datetime
    expires_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============== User Management Schemas (Master) ==============

class UserRoleChange(BaseModel):
    """Schema for changing a user's role (Master only)."""
    user_id: int
    new_role_id: int


class UserPermissionsBulkUpdate(BaseModel):
    """Schema for bulk updating user permissions."""
    user_id: int
    permission_ids: List[int]
    is_granted: bool = True


# ============== Audit Log Schemas ==============

class AuditLogResponse(BaseModel):
    """Schema for audit log response."""
    id: int
    action: str
    actor_id: int
    actor_email: Optional[str] = None
    target_user_id: Optional[int] = None
    target_user_email: Optional[str] = None
    target_role_name: Optional[str] = None
    target_permission_name: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class AuditLogFilter(BaseModel):
    """Schema for filtering audit logs."""
    action: Optional[str] = None
    actor_id: Optional[int] = None
    target_user_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = 100
    offset: int = 0


# ============== Access Level Enum for API ==============

class AccessLevelInfo(BaseModel):
    """Information about access levels."""
    level: int
    name: str
    description: str


# ============== User Response with RBAC info ==============

class UserRBACResponse(BaseModel):
    """Extended user response with RBAC information."""
    id: int
    email: str
    full_name: Optional[str] = None
    role: str
    role_id: Optional[int] = None
    role_name: Optional[str] = None
    access_level: int
    custom_permissions: List[str] = []
    created_at: datetime
    
    class Config:
        from_attributes = True
