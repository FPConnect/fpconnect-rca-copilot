"""Disposable in-memory FastAPI bridge for the mobile contract test."""
import contextlib
import io
import json
import sys

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.core.database import Base, get_db
from app.core.security import hash_password
from app.main import app
from app.models.organization import Organization, OrganizationMembership
from app.models.ticket import Ticket
from app.models.user import User

engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
Base.metadata.create_all(engine)
sessions = sessionmaker(bind=engine)
with sessions.begin() as db:
    db.add_all([
        User(id=1, email="mobile@example.com", hashed_password=hash_password("SyntheticPass123!"), role="master", access_level=5),
        Organization(id=1, slug="one", name="One"),
        Organization(id=2, slug="two", name="Two"),
    ])
    db.flush()
    db.add_all([
        OrganizationMembership(user_id=1, organization_id=1, role="user"),
        OrganizationMembership(user_id=1, organization_id=2, role="visitor"),
        Ticket(id=1, organization_id=1, title="One ticket", creator_id=1),
        Ticket(id=2, organization_id=2, title="Two ticket", creator_id=1),
    ])


def override_db():
    with sessions() as db:
        yield db


app.dependency_overrides[get_db] = override_db
with TestClient(app) as client:
    for line in sys.stdin:
        try:
            request = json.loads(line)
            with contextlib.redirect_stdout(io.StringIO()):
                result = client.request(request["method"], request["path"], headers=request["headers"], content=request.get("body"))
            print(json.dumps({"status": result.status_code, "body": result.text}), flush=True)
        except Exception:
            print(json.dumps({"error": "Disposable API bridge failed"}), flush=True)
