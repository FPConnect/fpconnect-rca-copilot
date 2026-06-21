"""CRUD operations for RBAC models."""

from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_

from app.models.rbac import Role, Permission, RolePermission, UserPermission, AuditLog, AccessLevel
from app.models.user import User
from app.schemas.rbac import RoleCreate, RoleUpdate, PermissionCreate


# ============== Permission CRUD ==============

def get_permission(db: Session, permission_id: int) -> Optional[Permission]:
    """Retrieve a permission by ID."""
    return db.query(Permission).filter(Permission.id == permission_id).first()


def get_permission_by_name(db: Session, name: str) -> Optional[Permission]:
    """Retrieve a permission by name."""
    return db.query(Permission).filter(Permission.name == name).first()


def get_all_permissions(db: Session) -> List[Permission]:
    """Retrieve all permissions."""
    return db.query(Permission).order_by(Permission.category, Permission.name).all()


def create_permission(db: Session, permission_data: PermissionCreate) -> Permission:
    """Create a new permission."""
    db_permission = Permission(**permission_data.model_dump())
    db.add(db_permission)
    db.commit()
    db.refresh(db_permission)
    return db_permission


def delete_permission(db: Session, permission_id: int) -> bool:
    """Delete a permission."""
    db_permission = get_permission(db, permission_id)
    if db_permission:
        db.delete(db_permission)
        db.commit()
        return True
    return False


# ============== Role CRUD ==============

def get_role(db: Session, role_id: int) -> Optional[Role]:
    """Retrieve a role by ID."""
    return db.query(Role).options(joinedload(Role.permissions)).filter(Role.id == role_id).first()


def get_role_by_name(db: Session, name: str) -> Optional[Role]:
    """Retrieve a role by name."""
    return db.query(Role).filter(Role.name == name).first()


def get_all_roles(db: Session) -> List[Role]:
    """Retrieve all roles ordered by access level."""
    return db.query(Role).options(joinedload(Role.permissions)).order_by(Role.access_level).all()


def create_role(db: Session, role_data: RoleCreate) -> Role:
    """Create a new role with optional permissions."""
    db_role = Role(
        name=role_data.name,
        description=role_data.description,
        access_level=AccessLevel(role_data.access_level),
        is_system_role=role_data.is_system_role,
    )
    db.add(db_role)
    db.flush()
    
    # Assign permissions if provided
    if role_data.permission_ids:
        for perm_id in role_data.permission_ids:
            role_perm = RolePermission(role_id=db_role.id, permission_id=perm_id)
            db.add(role_perm)
    
    db.commit()
    db.refresh(db_role)
    return db.query(Role).options(joinedload(Role.permissions)).get(db_role.id)


def update_role(db: Session, role_id: int, role_data: RoleUpdate) -> Optional[Role]:
    """Update a role."""
    db_role = get_role(db, role_id)
    if not db_role:
        return None
    
    update_data = role_data.model_dump(exclude_unset=True)
    
    if "access_level" in update_data:
        update_data["access_level"] = AccessLevel(update_data["access_level"])
    
    # Handle permissions separately
    permission_ids = update_data.pop("permission_ids", None)
    
    for field, value in update_data.items():
        if value is not None:
            setattr(db_role, field, value)
    
    if permission_ids is not None:
        # Remove existing permissions and add new ones
        db.query(RolePermission).filter(RolePermission.role_id == role_id).delete()
        for perm_id in permission_ids:
            role_perm = RolePermission(role_id=role_id, permission_id=perm_id)
            db.add(role_perm)
    
    db.commit()
    db.refresh(db_role)
    return db.query(Role).options(joinedload(Role.permissions)).get(role_id)


def delete_role(db: Session, role_id: int) -> bool:
    """Delete a role (cannot delete system roles)."""
    db_role = get_role(db, role_id)
    if db_role and not db_role.is_system_role:
        db.delete(db_role)
        db.commit()
        return True
    return False


# ============== User Permission CRUD ==============

def get_user_permissions(db: Session, user_id: int) -> List[UserPermission]:
    """Get all custom permissions for a user."""
    return db.query(UserPermission).filter(UserPermission.user_id == user_id).all()


def grant_user_permission(
    db: Session,
    user_id: int,
    permission_id: int,
    granted_by: int,
    is_granted: bool = True,
    expires_at: Optional[datetime] = None,
) -> UserPermission:
    """Grant or revoke a permission for a user."""
    existing = db.query(UserPermission).filter(
        and_(UserPermission.user_id == user_id, UserPermission.permission_id == permission_id)
    ).first()
    
    if existing:
        existing.is_granted = is_granted
        existing.granted_by = granted_by
        existing.granted_at = datetime.now(timezone.utc)
        existing.expires_at = expires_at
    else:
        existing = UserPermission(
            user_id=user_id,
            permission_id=permission_id,
            is_granted=is_granted,
            granted_by=granted_by,
            expires_at=expires_at,
        )
        db.add(existing)
    
    db.commit()
    db.refresh(existing)
    return existing


def revoke_user_permission(db: Session, user_id: int, permission_id: int) -> bool:
    """Revoke a custom permission from a user."""
    db_permission = db.query(UserPermission).filter(
        and_(UserPermission.user_id == user_id, UserPermission.permission_id == permission_id)
    ).first()
    if db_permission:
        db.delete(db_permission)
        db.commit()
        return True
    return False


def get_effective_permissions(db: Session, user_id: int) -> List[str]:
    """
    Get all effective permissions for a user.
    Combines role permissions and custom user permissions.
    Custom permissions override role permissions.
    """
    user = db.query(User).options(joinedload(User.custom_permissions)).filter(User.id == user_id).first()
    if not user:
        return []
    
    permission_names = set()
    
    # Get permissions from role
    if user.role_id:
        role = db.query(Role).options(joinedload(Role.permissions)).filter(Role.id == user.role_id).first()
        if role:
            for perm in role.permissions:
                permission_names.add(perm.name)
    
    # Apply custom permissions (overrides)
    for user_perm in user.custom_permissions:
        if user_perm.is_granted:
            # Check if not expired
            if user_perm.expires_at is None or user_perm.expires_at > datetime.now(timezone.utc):
                permission_names.add(user_perm.permission.name)
        else:
            # Explicitly denied
            permission_names.discard(user_perm.permission.name)
    
    return list(permission_names)


# ============== Audit Log CRUD ==============

def log_audit_action(
    db: Session,
    action: str,
    actor_id: int,
    target_user_id: Optional[int] = None,
    target_role_id: Optional[int] = None,
    target_permission_id: Optional[int] = None,
    old_value: Optional[str] = None,
    new_value: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> AuditLog:
    """Log an audit action."""
    audit_log = AuditLog(
        action=action,
        actor_id=actor_id,
        target_user_id=target_user_id,
        target_role_id=target_role_id,
        target_permission_id=target_permission_id,
        old_value=old_value,
        new_value=new_value,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)
    return audit_log


def get_audit_logs(
    db: Session,
    action: Optional[str] = None,
    actor_id: Optional[int] = None,
    target_user_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 100,
    offset: int = 0,
) -> List[AuditLog]:
    """Get audit logs with filters."""
    query = db.query(AuditLog).options(
        joinedload(AuditLog.actor),
        joinedload(AuditLog.target_user),
        joinedload(AuditLog.target_role),
        joinedload(AuditLog.target_permission),
    )
    
    if action:
        query = query.filter(AuditLog.action == action)
    if actor_id:
        query = query.filter(AuditLog.actor_id == actor_id)
    if target_user_id:
        query = query.filter(AuditLog.target_user_id == target_user_id)
    if start_date:
        query = query.filter(AuditLog.created_at >= start_date)
    if end_date:
        query = query.filter(AuditLog.created_at <= end_date)
    
    return query.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit).all()


# ============== Helper Functions ==============

def get_access_level_value(access_level: AccessLevel) -> int:
    """Get the numeric value of an access level."""
    return access_level.value


def can_user_modify_target(actor_level: int, target_level: int) -> bool:
    """Check if an actor can modify a target based on access levels."""
    return actor_level > target_level


def initialize_default_roles_and_permissions(db: Session) -> None:
    """Initialize default roles and permissions if they don't exist."""
    # Define standard permissions (14+ as required)
    default_permissions = [
        # Content/Ticket permissions
        ("view_public_content", "View public content", "content"),
        ("view_own_content", "View own content", "content"),
        ("create_content", "Create new content", "content"),
        ("edit_own_content", "Edit own content", "content"),
        ("delete_own_content", "Delete own content", "content"),
        
        # User management permissions
        ("view_users_basic", "View basic user list", "users"),
        ("manage_users_basic", "Manage basic users (levels 1-2)", "users"),
        ("manage_users_full", "Manage all users (except Master)", "users"),
        ("change_user_roles", "Change user roles", "users"),
        ("grant_custom_permissions", "Grant custom permissions", "users"),
        
        # Content approval permissions
        ("approve_content", "Approve content created by others", "content"),
        
        # Report permissions
        ("view_reports_standard", "View standard reports", "reports"),
        ("view_reports_advanced", "View advanced reports", "reports"),
        ("view_financial_reports", "View financial reports", "reports"),
        ("export_reports", "Export reports", "reports"),
        
        # System/admin permissions
        ("view_system_config", "View system configuration", "settings"),
        ("edit_system_config", "Edit system configuration", "settings"),
        ("view_audit_logs", "View audit logs", "settings"),
        ("manage_playbooks", "Manage playbooks", "content"),
        ("manage_machines", "Manage machines", "content"),
        ("manage_contracts", "Manage contracts", "content"),
    ]
    
    # Create permissions
    for name, description, category in default_permissions:
        if not get_permission_by_name(db, name):
            create_permission(db, PermissionCreate(name=name, description=description, category=category))
    
    # Define default roles with their permissions
    default_roles = [
        {
            "name": "Visitante",
            "description": "Nível 1 - Apenas leitura de conteúdo público",
            "access_level": 1,
            "permissions": ["view_public_content"],
            "is_system_role": True,
        },
        {
            "name": "Usuário",
            "description": "Nível 2 - Acesso ao próprio perfil e gestão de conteúdo próprio",
            "access_level": 2,
            "permissions": [
                "view_public_content",
                "view_own_content",
                "create_content",
                "edit_own_content",
                "delete_own_content",
            ],
            "is_system_role": True,
        },
        {
            "name": "Gerente",
            "description": "Nível 3 - Gestão de usuários básicos, aprovação de conteúdo e relatórios padrão",
            "access_level": 3,
            "permissions": [
                "view_public_content",
                "view_own_content",
                "create_content",
                "edit_own_content",
                "delete_own_content",
                "view_users_basic",
                "manage_users_basic",
                "approve_content",
                "view_reports_standard",
                "export_reports",
            ],
            "is_system_role": True,
        },
        {
            "name": "Administrador",
            "description": "Nível 4 - Configurações globais, logs de auditoria e gestão completa de usuários",
            "access_level": 4,
            "permissions": [
                "view_public_content",
                "view_own_content",
                "create_content",
                "edit_own_content",
                "delete_own_content",
                "view_users_basic",
                "manage_users_basic",
                "manage_users_full",
                "approve_content",
                "view_reports_standard",
                "view_reports_advanced",
                "export_reports",
                "view_system_config",
                "edit_system_config",
                "view_audit_logs",
                "manage_playbooks",
                "manage_machines",
                "manage_contracts",
            ],
            "is_system_role": True,
        },
        {
            "name": "Master",
            "description": "Nível 5 - Acesso irrestrito a todos os recursos",
            "access_level": 5,
            "permissions": [p[0] for p in default_permissions],  # All permissions
            "is_system_role": True,
        },
    ]
    
    # Create roles
    for role_data in default_roles:
        if not get_role_by_name(db, role_data["name"]):
            # Get permission IDs
            perm_ids = []
            for perm_name in role_data["permissions"]:
                perm = get_permission_by_name(db, perm_name)
                if perm:
                    perm_ids.append(perm.id)
            
            create_role(
                db,
                RoleCreate(
                    name=role_data["name"],
                    description=role_data["description"],
                    access_level=role_data["access_level"],
                    is_system_role=role_data["is_system_role"],
                    permission_ids=perm_ids,
                ),
            )
