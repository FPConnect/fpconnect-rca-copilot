"""Development test account provisioning utilities."""

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import ROLE_ACCESS_LEVELS

TEST_ACCOUNTS = [
    {
        "email": "master@fpconnect.com",
        "full_name": "Master",
        "role": "master",
        "access_level": 5,
    },
    {
        "email": "admin_teste@fpconnect.com",
        "full_name": "Administrador",
        "role": "admin",
        "access_level": 4,
    },
    {
        "email": "gerente_teste@fpconnect.com",
        "full_name": "Gerente",
        "role": "manager",
        "access_level": 3,
    },
    {
        "email": "usuario_teste@fpconnect.com",
        "full_name": "Usuário",
        "role": "user",
        "access_level": 2,
    },
    {
        "email": "visitante_teste@fpconnect.com",
        "full_name": "Visitante",
        "role": "visitor",
        "access_level": 1,
    },
]

LEGACY_TEST_EMAILS = {"admin@fpconnect.com"}
TEST_EMAILS = {account["email"] for account in TEST_ACCOUNTS}


def reset_test_accounts(db: Session, password: str) -> None:
    """Recreate development test users using a password supplied outside the codebase."""
    if settings.app_env != "development" or not settings.seed_test_accounts:
        raise RuntimeError("Test account provisioning requires explicit development opt-in.")
    if len(password) < 12:
        raise ValueError("Test account passwords must be at least 12 characters long")
    db.query(User).filter(User.email.in_(TEST_EMAILS | LEGACY_TEST_EMAILS)).delete(synchronize_session=False)
    for account in TEST_ACCOUNTS:
        role = account["role"]
        db.add(
            User(
                email=account["email"],
                hashed_password=hash_password(password),
                full_name=account["full_name"],
                role=role,
                access_level=ROLE_ACCESS_LEVELS[role],
            )
        )
    db.commit()
