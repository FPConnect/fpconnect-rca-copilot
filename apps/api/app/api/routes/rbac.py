"""RBAC management API routes for Master users."""

from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.models.rbac import AccessLevel
from app.schemas.rbac import (
    RoleCreate,
    RoleUpdate,
    RoleResponse,
    PermissionResponse,
    UserPermissionResponse,
    UserPermissionGrant,
    UserRoleChange,
    UserPermissionsBulkUpdate,
    AuditLogResponse,
    AuditLogFilter,
    UserRBACResponse,
)
from app.crud.rbac import (
    get_all_permissions,
    create_permission,
    delete_permission,
    get_all_roles,
    get_role,
    create_role,
    update_role,
    delete_role,
    get_user_permissions,
    grant_user_permission,
    revoke_user_permission,
    get_effective_permissions,
    log_audit_action,
    get_audit_logs,
    initialize_default_roles_and_permissions,
)
from app.api.rbac_deps import (
    get_current_user_with_role,
    get_user_access_level,
    can_modify_user,
    require_master,
)


router = APIRouter()


# ============== Permission Management (Master Only) ==============

@router.get("/permissions", response_model=List[PermissionResponse])
def list_permissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_master()),
):
    """List all available permissions (Master only)."""
    return get_all_permissions(db)


@router.post("/permissions", response_model=PermissionResponse, status_code=status.HTTP_201_CREATED)
def create_new_permission(
    permission_data: RoleCreate,  # Reusing schema for simplicity
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_master()),
):
    """Create a new custom permission (Master only)."""
    from app.schemas.rbac import PermissionCreate
    perm_create = PermissionCreate(
        name=permission_data.name,
        description=permission_data.description,
        category=getattr(permission_data, 'category', 'custom'),
    )
    permission = create_permission(db, perm_create)
    
    # Log audit
    log_audit_action(
        db=db,
        action="permission_created",
        actor_id=current_user.id,
        target_permission_id=permission.id,
        new_value=permission.name,
        ip_address=request.client.host if request.client else None,
    )
    
    return permission


@router.delete("/permissions/{permission_id}")
def delete_existing_permission(
    permission_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_master()),
):
    """Delete a permission (Master only)."""
    permission = db.query(type(current_user)).filter(type(current_user).id == permission_id).first()
    if not delete_permission(db, permission_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found or cannot be deleted",
        )
    
    # Log audit
    log_audit_action(
        db=db,
        action="permission_deleted",
        actor_id=current_user.id,
        target_permission_id=permission_id,
        ip_address=request.client.host if request.client else None,
    )
    
    return {"message": "Permission deleted successfully"}


# ============== Role Management (Master Only) ==============

@router.get("/roles", response_model=List[RoleResponse])
def list_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_master()),
):
    """List all roles with their permissions (Master only)."""
    return get_all_roles(db)


@router.post("/roles", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
def create_new_role(
    role_data: RoleCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_master()),
):
    """Create a new role (Master only)."""
    role = create_role(db, role_data)
    
    # Log audit
    log_audit_action(
        db=db,
        action="role_created",
        actor_id=current_user.id,
        target_role_id=role.id,
        new_value=role.name,
        ip_address=request.client.host if request.client else None,
    )
    
    return role


@router.put("/roles/{role_id}", response_model=RoleResponse)
def update_existing_role(
    role_id: int,
    role_data: RoleUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_master()),
):
    """Update a role (Master only)."""
    old_role = get_role(db, role_id)
    if not old_role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    
    if old_role.is_system_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="System roles cannot be modified",
        )
    
    role = update_role(db, role_id, role_data)
    
    # Log audit
    log_audit_action(
        db=db,
        action="role_updated",
        actor_id=current_user.id,
        target_role_id=role_id,
        old_value=old_role.name,
        new_value=role.name,
        ip_address=request.client.host if request.client else None,
    )
    
    return role


@router.delete("/roles/{role_id}")
def delete_existing_role(
    role_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_master()),
):
    """Delete a role (Master only). Cannot delete system roles."""
    role = get_role(db, role_id)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    
    if not delete_role(db, role_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete system role",
        )
    
    # Log audit
    log_audit_action(
        db=db,
        action="role_deleted",
        actor_id=current_user.id,
        target_role_id=role_id,
        old_value=role.name,
        ip_address=request.client.host if request.client else None,
    )
    
    return {"message": "Role deleted successfully"}


# ============== User Permission Management (Master Only) ==============

@router.get("/users/{user_id}/permissions", response_model=List[UserPermissionResponse])
def get_user_custom_permissions(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_master()),
):
    """Get custom permissions for a specific user (Master only)."""
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    custom_perms = get_user_permissions(db, user_id)
    
    # Build response with permission names
    result = []
    for cp in custom_perms:
        result.append(UserPermissionResponse(
            id=cp.id,
            user_id=cp.user_id,
            permission_id=cp.permission_id,
            permission_name=cp.permission.name,
            is_granted=cp.is_granted,
            granted_by=cp.granted_by,
            granted_at=cp.granted_at,
            expires_at=cp.expires_at,
        ))
    
    return result


@router.post("/users/{user_id}/permissions/grant", response_model=UserPermissionResponse)
def grant_permission_to_user(
    user_id: int,
    grant_data: UserPermissionGrant,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_master()),
):
    """Grant or revoke a permission to/from a user (Master only)."""
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    permission = db.query(type(target_user)).filter(type(target_user).id == grant_data.permission_id).first()
    if not permission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found")
    
    user_perm = grant_user_permission(
        db=db,
        user_id=user_id,
        permission_id=grant_data.permission_id,
        granted_by=current_user.id,
        is_granted=grant_data.is_granted,
        expires_at=grant_data.expires_at,
    )
    
    # Log audit
    log_audit_action(
        db=db,
        action="permission_granted" if grant_data.is_granted else "permission_revoked",
        actor_id=current_user.id,
        target_user_id=user_id,
        target_permission_id=grant_data.permission_id,
        new_value=f"granted={grant_data.is_granted}",
        ip_address=request.client.host if request.client else None,
    )
    
    return UserPermissionResponse(
        id=user_perm.id,
        user_id=user_perm.user_id,
        permission_id=user_perm.permission_id,
        permission_name=permission.name,
        is_granted=user_perm.is_granted,
        granted_by=user_perm.granted_by,
        granted_at=user_perm.granted_at,
        expires_at=user_perm.expires_at,
    )


@router.get("/users/{user_id}/effective-permissions", response_model=List[str])
def get_user_effective_permissions(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_master()),
):
    """Get all effective permissions for a user (combined role + custom) (Master only)."""
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return get_effective_permissions(db, user_id)


# ============== User Role Management (Master Only) ==============

@router.put("/users/{user_id}/role")
def change_user_role(
    user_id: int,
    role_change: UserRoleChange,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_master()),
):
    """Change a user's role (Master only)."""
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    new_role = get_role(db, role_change.new_role_id)
    if not new_role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    
    # Check if Master is modifying themselves
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Users cannot modify their own role",
        )
    
    old_role_id = target_user.role_id
    old_role_name = target_user.role
    
    # Update user's role
    target_user.role_id = role_change.new_role_id
    db.commit()
    db.refresh(target_user)
    
    # Log audit
    log_audit_action(
        db=db,
        action="role_changed",
        actor_id=current_user.id,
        target_user_id=user_id,
        target_role_id=role_change.new_role_id,
        old_value=str(old_role_id),
        new_value=str(role_change.new_role_id),
        ip_address=request.client.host if request.client else None,
    )
    
    return {"message": f"User role updated to {new_role.name}"}


# ============== Audit Logs (Master Only) ==============

@router.get("/audit-logs", response_model=List[AuditLogResponse])
def get_system_audit_logs(
    action: Optional[str] = None,
    target_user_id: Optional[int] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_master()),
):
    """Get audit logs for permission and role changes (Master only)."""
    logs = get_audit_logs(
        db=db,
        action=action,
        target_user_id=target_user_id,
        limit=limit,
        offset=offset,
    )
    
    # Build response with related info
    result = []
    for log in logs:
        result.append(AuditLogResponse(
            id=log.id,
            action=log.action,
            actor_id=log.actor_id,
            actor_email=log.actor.email if log.actor else None,
            target_user_id=log.target_user_id,
            target_user_email=log.target_user.email if log.target_user else None,
            target_role_name=log.target_role.name if log.target_role else None,
            target_permission_name=log.target_permission.name if log.target_permission else None,
            old_value=log.old_value,
            new_value=log.new_value,
            ip_address=log.ip_address,
            created_at=log.created_at,
        ))
    
    return result


# ============== RBAC Initialization ==============

@router.post("/initialize")
def initialize_rbac(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_master()),
):
    """Initialize default roles and permissions (Master only)."""
    initialize_default_roles_and_permissions(db)
    
    log_audit_action(
        db=db,
        action="rbac_initialized",
        actor_id=current_user.id,
        ip_address=request.client.host if request.client else None,
    )
    
    return {"message": "RBAC system initialized with default roles and permissions"}
