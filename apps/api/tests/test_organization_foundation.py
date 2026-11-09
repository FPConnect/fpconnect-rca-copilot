"""Tests for the isolated identity foundation, not resource isolation."""

import importlib.util
from pathlib import Path

import pytest
from alembic.migration import MigrationContext
from alembic.operations import Operations
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.tenant import TenantContext, get_tenant_context
from app.core.database import Base, get_db
from app.core.security import create_access_token
from app.models.organization import Organization, OrganizationMembership
from app.models.user import User


@pytest.fixture
def identity_api():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(
        engine,
        tables=[
            User.__table__,
            Organization.__table__,
            OrganizationMembership.__table__,
        ],
    )
    sessions = sessionmaker(bind=engine)
    with sessions.begin() as db:
        db.add_all(
            [
                User(id=1, email="a@example.test", hashed_password="unused",
                     role="master", access_level=5),
                User(id=2, email="b@example.test", hashed_password="unused",
                     role="user", access_level=2),
                User(id=3, email="c@example.test", hashed_password="unused",
                     role="user", access_level=2),
                Organization(id=1, slug="a", name="A"),
                Organization(id=2, slug="b", name="B"),
            ]
        )
        db.flush()
        db.add_all(
            [
                OrganizationMembership(user_id=1, organization_id=1),
                OrganizationMembership(user_id=2, organization_id=2),
            ]
        )

    api = FastAPI()

    def override_db():
        with sessions() as db:
            yield db

    @api.get("/context")
    def context(tenant: TenantContext = Depends(get_tenant_context)):
        return {"organization_id": tenant.organization_id}

    api.dependency_overrides[get_db] = override_db
    with TestClient(api) as client:
        yield client, sessions
    engine.dispose()


def token(user_id, role, access_level, selected_org=None, **extra):
    claims = {"sub": str(user_id), "role": role, "access_level": access_level, "ver": 0}
    claims.update(extra)
    headers = {"Authorization": f"Bearer {create_access_token(claims)}"}
    if selected_org is not None:
        headers["X-Organization-Id"] = str(selected_org)
    return headers


def test_context_validates_selection_even_for_master(identity_api):
    client, _ = identity_api
    headers = token(1, "master", 5, selected_org=2, organization_id=2)
    assert client.get("/context", headers=headers).status_code == 403
    response = client.get(
        "/context?organization_id=2",
        headers=token(1, "master", 5, selected_org=1, organization_id=2),
    )
    assert response.status_code == 200
    assert response.json() == {"organization_id": 1}
    assert client.get("/context", headers=token(2, "user", 2, selected_org=2)).json() == {
        "organization_id": 2
    }
    assert client.get("/context", headers=token(1, "master", 5)).status_code == 422


def test_user_can_switch_only_to_an_active_membership(identity_api):
    client, sessions = identity_api
    with sessions.begin() as db:
        db.add(OrganizationMembership(user_id=1, organization_id=2))
    assert client.get("/context", headers=token(1, "master", 5, selected_org=1)).json() == {
        "organization_id": 1
    }
    assert client.get("/context", headers=token(1, "master", 5, selected_org=2)).json() == {
        "organization_id": 2
    }
    with sessions.begin() as db:
        db.query(OrganizationMembership).filter_by(user_id=1, organization_id=2).one().is_active = False
    assert client.get("/context", headers=token(1, "master", 5, selected_org=2)).status_code == 403
    assert client.get("/context", headers=token(1, "master", 5, selected_org=1)).status_code == 200


def test_missing_or_inactive_membership_and_org_fail_closed(identity_api):
    client, sessions = identity_api
    assert client.get("/context", headers=token(3, "user", 2, selected_org=1)).status_code == 403
    with sessions.begin() as db:
        db.query(OrganizationMembership).filter_by(user_id=1).one().is_active = False
    assert client.get("/context", headers=token(1, "master", 5, selected_org=1)).status_code == 403
    with sessions.begin() as db:
        db.query(Organization).filter_by(id=2).one().is_active = False
    assert client.get("/context", headers=token(2, "user", 2, selected_org=2)).status_code == 403
    assert client.get("/context").status_code == 401


def test_context_still_enforces_existing_user_and_token_state(identity_api):
    client, sessions = identity_api
    assert client.get("/context", headers=token(1, "user", 2, selected_org=1)).status_code == 401
    with sessions.begin() as db:
        db.query(User).filter_by(id=1).one().is_active = False
    assert client.get("/context", headers=token(1, "master", 5, selected_org=1)).status_code == 401


def test_membership_is_unique_per_user_and_organization(identity_api):
    _, sessions = identity_api
    with pytest.raises(IntegrityError):
        with sessions.begin() as db:
            db.add(OrganizationMembership(user_id=1, organization_id=1))
            db.flush()


def test_migration_does_not_infer_memberships_and_downgrade_preserves_users():
    path = Path(__file__).parents[1] / "alembic" / "versions" / "008_organization_identity.py"
    spec = importlib.util.spec_from_file_location("organization_migration", path)
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    engine = create_engine("sqlite://")
    with engine.begin() as connection:
        connection.execute(text("CREATE TABLE users (id INTEGER PRIMARY KEY)"))
        connection.execute(text("INSERT INTO users (id) VALUES (10), (20)"))
        context = MigrationContext.configure(connection)
        with Operations.context(context):
            migration.upgrade()
        assert connection.execute(text("SELECT count(*) FROM organizations")).scalar_one() == 0
        assert connection.execute(text("SELECT count(*) FROM organization_memberships")).scalar_one() == 0
        assert connection.execute(text("SELECT id FROM users ORDER BY id")).scalars().all() == [10, 20]
        with Operations.context(context):
            migration.downgrade()
        assert connection.execute(text("SELECT id FROM users ORDER BY id")).scalars().all() == [10, 20]
    engine.dispose()
