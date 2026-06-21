"""Seed script for RBAC system with test users.

Run from apps/api:
    python scripts/seed_rbac.py
"""

from datetime import datetime, timedelta, timezone

from app.core.database import Base, SessionLocal, engine
from app.core.security import hash_password
from app.models.user import User
from app.models.rbac import Role, Permission, AccessLevel
from app.crud.rbac import (
    initialize_default_roles_and_permissions,
    get_role_by_name,
    get_permission_by_name,
)


def create_test_users(db):
    """Create master and visitante_teste users for validation."""
    
    # Get Master role
    master_role = get_role_by_name(db, "Master")
    if not master_role:
        print("ERROR: Master role not found. Run initialize_default_roles_and_permissions first.")
        return
    
    # Get Visitante role
    visitante_role = get_role_by_name(db, "Visitante")
    if not visitante_role:
        print("ERROR: Visitante role not found. Run initialize_default_roles_and_permissions first.")
        return
    
    # Create or update Master user
    master_email = "master@fpconnect.com"
    master_user = db.query(User).filter(User.email == master_email).first()
    
    if master_user:
        # Update existing user
        master_user.role_id = master_role.id
        master_user.full_name = "Administrador Master"
        master_user.hashed_password = hash_password("Master@2024Secure!")
        db.commit()
        db.refresh(master_user)
        print(f"Updated master user: {master_email}")
    else:
        master_user = User(
            email=master_email,
            hashed_password=hash_password("Master@2024Secure!"),
            full_name="Administrador Master",
            role_id=master_role.id,
            role="admin",  # Legacy field for backward compatibility
        )
        db.add(master_user)
        db.commit()
        db.refresh(master_user)
        print(f"Created master user: {master_email}")
    
    # Create or update Visitante Test user
    visitante_email = "visitante_teste@fpconnect.com"
    visitante_user = db.query(User).filter(User.email == visitante_email).first()
    
    if visitante_user:
        # Update existing user
        visitante_user.role_id = visitante_role.id
        visitante_user.full_name = "Visitante Teste"
        visitante_user.hashed_password = hash_password("Visitante@123")
        db.commit()
        db.refresh(visitante_user)
        print(f"Updated visitante test user: {visitante_email}")
    else:
        visitante_user = User(
            email=visitante_email,
            hashed_password=hash_password("Visitante@123"),
            full_name="Visitante Teste",
            role_id=visitante_role.id,
            role="technician",  # Legacy field for backward compatibility
        )
        db.add(visitante_user)
        db.commit()
        db.refresh(visitante_user)
        print(f"Created visitante test user: {visitante_email}")
    
    # Create additional test users for each level
    test_users = [
        ("usuario_teste@fpconnect.com", "Usuário Teste", "Usuario@123", "Usuário"),
        ("gerente_teste@fpconnect.com", "Gerente Teste", "Gerente@123", "Gerente"),
        ("admin_teste@fpconnect.com", "Administrador Teste", "Admin@123", "Administrador"),
    ]
    
    for email, full_name, password, role_name in test_users:
        role = get_role_by_name(db, role_name)
        if not role:
            print(f"WARNING: Role {role_name} not found, skipping {email}")
            continue
        
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            existing_user.role_id = role.id
            existing_user.full_name = full_name
            existing_user.hashed_password = hash_password(password)
            db.commit()
            print(f"Updated test user: {email} ({role_name})")
        else:
            test_user = User(
                email=email,
                hashed_password=hash_password(password),
                full_name=full_name,
                role_id=role.id,
                role="technician",  # Legacy field
            )
            db.add(test_user)
            db.commit()
            print(f"Created test user: {email} ({role_name})")
    
    # Print summary
    print("\n" + "="*60)
    print("RBAC TEST USERS CREATED SUCCESSFULLY")
    print("="*60)
    print(f"\nMaster User:")
    print(f"  Email: {master_email}")
    print(f"  Password: Master@2024Secure!")
    print(f"  Access Level: 5 (Master)")
    print(f"  Permissions: ALL ({len(master_role.permissions)} permissions)")
    
    print(f"\nVisitante Test User:")
    print(f"  Email: {visitante_email}")
    print(f"  Password: Visitante@123")
    print(f"  Access Level: 1 (Visitante)")
    print(f"  Permissions: view_public_content only")
    
    print(f"\nAdditional Test Users:")
    for email, full_name, password, role_name in test_users:
        role = get_role_by_name(db, role_name)
        if role:
            print(f"  - {email} ({role_name}): {password}")
    
    print("\n" + "="*60)
    print("IMPORTANT: Change these passwords in production!")
    print("="*60)


def seed():
    """Main seed function."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Initialize default roles and permissions
        print("Initializing default roles and permissions...")
        initialize_default_roles_and_permissions(db)
        print("Default roles and permissions created.\n")
        
        # Create test users
        create_test_users(db)
        
    finally:
        db.close()


if __name__ == "__main__":
    seed()
    print("\nRBAC seed data loaded successfully.")
