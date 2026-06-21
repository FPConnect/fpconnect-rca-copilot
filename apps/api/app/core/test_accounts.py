"""Development test account provisioning utilities."""

from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import ROLE_ACCESS_LEVELS

TEST_ACCOUNTS = [
    {
        "email": "master@fpconnect.com",
        "password": "Master@2024Secure!",
        "full_name": "Master",
        "role": "master",
        "access_level": 5,
    },
    {
        "email": "admin_teste@fpconnect.com",
        "password": "Admin@123",
        "full_name": "Administrador",
        "role": "admin",
        "access_level": 4,
    },
    {
        "email": "gerente_teste@fpconnect.com",
        "password": "Gerente@123",
        "full_name": "Gerente",
        "role": "manager",
        "access_level": 3,
    },
    {
        "email": "usuario_teste@fpconnect.com",
        "password": "Usuario@123",
        "full_name": "Usuário",
        "role": "user",
        "access_level": 2,
    },
    {
        "email": "visitante_teste@fpconnect.com",
        "password": "Visitante@123",
        "full_name": "Visitante",
        "role": "visitor",
        "access_level": 1,
    },
]

LEGACY_TEST_EMAILS = {"admin@fpconnect.com"}
TEST_EMAILS = {account["email"] for account in TEST_ACCOUNTS}


def reset_test_accounts(db: Session) -> None:
    """Remove legacy/demo users and recreate the approved development test users."""
    db.query(User).filter(User.email.in_(TEST_EMAILS | LEGACY_TEST_EMAILS)).delete(synchronize_session=False)
    for account in TEST_ACCOUNTS:
        role = account["role"]
        db.add(
            User(
                email=account["email"],
                hashed_password=hash_password(account["password"]),
                full_name=account["full_name"],
                role=role,
                access_level=ROLE_ACCESS_LEVELS[role],
            )
        )
    db.commit()
