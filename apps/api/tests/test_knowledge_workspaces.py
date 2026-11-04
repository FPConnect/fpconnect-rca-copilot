"""Security regression tests for OPSPECTA knowledge-base separation.

The tests use synthetic articles only. No real customer records are accessed.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.core.security import hash_password
from app.main import app
from app.models.ticket import KBArticle
from app.models.knowledge import KnowledgeAudit
from app.models.user import User
from app.services.analyze_service import get_root_cause_analysis

engine = create_engine("sqlite:///./test_knowledge_governance.db", connect_args={"check_same_thread": False})
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
client = TestClient(app)


def db_override():
    db = Session()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def isolated_db():
    old = app.dependency_overrides.get(get_db)
    app.dependency_overrides[get_db] = db_override
    Base.metadata.create_all(bind=engine)
    with Session() as db:
        for email, role, level in [
            ("alice@sample.example", "user", 2),
            ("bob@sample.example", "user", 2),
            ("admin@sample.example", "admin", 4),
            ("reviewer@sample.example", "admin", 4),
        ]:
            db.add(User(
                email=email, role=role, access_level=level,
                hashed_password=hash_password("SamplePass12345!"),
            ))
        db.commit()
    yield
    Base.metadata.drop_all(bind=engine)
    if old is None:
        app.dependency_overrides.pop(get_db, None)
    else:
        app.dependency_overrides[get_db] = old


def headers(name: str) -> dict:
    login = client.post(
        "/auth/login",
        json={"email": f"{name}@sample.example", "password": "SamplePass12345!"},
    )
    assert login.status_code == 200, login.text
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def user_id(name: str) -> int:
    with Session() as db:
        return db.query(User.id).filter(User.email == f"{name}@sample.example").scalar()


def create_workspace(admin_headers: dict, slug: str = "clinic-a") -> int:
    response = client.post("/knowledge/workspaces", headers=admin_headers,
                           json={"slug": slug, "name": slug.title()})
    assert response.status_code == 201, response.text
    return response.json()["id"]


def add_member(admin_headers: dict, workspace_id: int, member_name: str, role: str = "member"):
    response = client.post(
        f"/knowledge/workspaces/{workspace_id}/members",
        headers=admin_headers,
        json={"user_id": user_id(member_name), "membership_role": role},
    )
    assert response.status_code == 201, response.text


def article_payload(**overrides):
    payload = {
        "title": "Synthetic analyzer network event code E24",
        "content": "This is a synthetic maintenance documentation reference, not a repair procedure.",
        "category": "connectivity",
        "tags": ["network", "error24"],
        "visibility": "private",
        "manufacturer": "Fictional Labs",
        "equipment_family": "Analyzer",
        "failure_code": "E24",
    }
    payload.update(overrides)
    return payload


def test_permission_boundaries_and_workspace_admin():
    assert client.get("/knowledge/articles").status_code == 401
    alice, admin, bob = headers("alice"), headers("admin"), headers("bob")
    assert client.post("/knowledge/workspaces", headers=alice,
                       json={"slug": "bad-test", "name": "Bad Test"}).status_code == 403
    workspace_id = create_workspace(admin)
    assert client.get("/knowledge/workspaces", headers=bob).json() == []
    add_member(admin, workspace_id, "alice")
    assert len(client.get("/knowledge/workspaces", headers=alice).json()) == 1
    assert client.post(
        f"/knowledge/workspaces/{workspace_id}/members", headers=alice,
        json={"user_id": user_id("bob")},
    ).status_code == 403
    assert client.post(
        f"/knowledge/workspaces/{workspace_id}/members", headers=bob,
        json={"user_id": user_id("bob")},
    ).status_code == 403


def test_global_article_requires_independent_approval_and_attestation():
    alice, bob, admin = headers("alice"), headers("bob"), headers("admin")
    created = client.post("/knowledge/articles", headers=alice,
                          json=article_payload(visibility="global")).json()
    aid = created["id"]
    assert created["review_status"] == "draft"
    assert client.get("/knowledge/articles", headers=bob).json() == []
    submitted = client.post(f"/knowledge/articles/{aid}/submit", headers=alice)
    assert submitted.status_code == 200
    assert len(client.get("/knowledge/review-queue", headers=admin).json()) == 1
    assert client.get("/knowledge/review-queue", headers=bob).status_code == 403
    assert client.post(
        f"/knowledge/articles/{aid}/review", headers=admin,
        json={"decision": "approve"},
    ).status_code == 422
    response = client.post(
        f"/knowledge/articles/{aid}/review", headers=admin,
        json={"decision": "approve", "sharing_authorized": True},
    )
    assert response.status_code == 200, response.text
    assert response.json()["review_status"] == "approved"
    allowed = client.get("/knowledge/articles", headers=bob)
    assert [x["id"] for x in allowed.json()] == [aid]
    assert client.get(f"/knowledge/articles/{aid}", headers=bob).status_code == 200


def test_owner_cannot_self_approve_even_when_admin():
    admin = headers("admin")
    article = client.post("/knowledge/articles", headers=admin,
                          json=article_payload(visibility="global")).json()
    aid = article["id"]
    client.post(f"/knowledge/articles/{aid}/submit", headers=admin)
    response = client.post(
        f"/knowledge/articles/{aid}/review", headers=admin,
        json={"decision": "approve", "sharing_authorized": True},
    )
    assert response.status_code == 403
    reviewer = headers("reviewer")
    response = client.post(
        f"/knowledge/articles/{aid}/review", headers=reviewer,
        json={"decision": "approve", "sharing_authorized": True},
    )
    assert response.status_code == 200


def test_private_articles_never_leak_to_other_users():
    alice, bob, admin = headers("alice"), headers("bob"), headers("admin")
    aid = client.post("/knowledge/articles", headers=alice,
                      json=article_payload()).json()["id"]
    for other in [bob, admin]:
        assert client.get(f"/knowledge/articles/{aid}", headers=other).status_code == 404
        assert client.get("/knowledge/articles", headers=other).json() == []
    assert client.get("/knowledge/articles", headers=alice).json()[0]["id"] == aid


def test_workspace_visibility_requires_membership_and_manager_approval():
    alice, bob, admin = headers("alice"), headers("bob"), headers("admin")
    w1 = create_workspace(admin, "hospital-alpha")
    w2 = create_workspace(admin, "hospital-beta")
    add_member(admin, w1, "alice")
    add_member(admin, w1, "bob")
    aid = client.post("/knowledge/articles", headers=alice,
                      json=article_payload(
                          visibility="workspace", workspace_id=w1)).json()["id"]
    assert client.get(f"/knowledge/articles/{aid}", headers=bob).status_code == 404
    client.post(f"/knowledge/articles/{aid}/submit", headers=alice)
    response = client.post(f"/knowledge/articles/{aid}/review", headers=admin,
                           json={"decision": "approve", "sharing_authorized": True})
    assert response.status_code == 200, response.text
    assert client.get(f"/knowledge/articles/{aid}", headers=bob).status_code == 200
    assert client.get("/knowledge/articles", headers=bob,
                      params={"workspace_id": w2}).json() == []
    revocation = client.delete(
        f"/knowledge/workspaces/{w1}/members/{user_id('bob')}", headers=admin
    )
    assert revocation.status_code == 204
    assert client.get(f"/knowledge/articles/{aid}", headers=bob).status_code == 404
    assert client.get("/knowledge/articles", headers=bob).json() == []


def test_rejected_workspace_creation_and_invalid_scopes():
    alice, admin = headers("alice"), headers("admin")
    workspace_id = create_workspace(admin)
    assert client.post(
        "/knowledge/articles", headers=alice,
        json=article_payload(visibility="workspace", workspace_id=workspace_id)
    ).status_code == 403
    assert client.post(
        "/knowledge/articles", headers=alice,
        json=article_payload(visibility="global", workspace_id=workspace_id)
    ).status_code == 422


def test_filters_lifecycle_and_audit():
    alice, bob, admin = headers("alice"), headers("bob"), headers("admin")
    created = client.post("/knowledge/articles", headers=alice,
                          json=article_payload()).json()
    aid = created["id"]
    assert client.get("/knowledge/articles", headers=alice,
                      params={"category": "connectivity", "tag": "network",
                              "manufacturer": "Fictional", "equipment_family": "Analyzer",
                              "failure_code": "E24", "q": "network"}).json()[0]["id"] == aid
    assert client.get("/knowledge/articles", headers=alice,
                      params={"tag": "not-there"}).json() == []
    assert client.get("/knowledge/articles", headers=alice,
                      params={"tag": "invalid%tag"}).status_code == 422
    assert client.patch(f"/knowledge/articles/{aid}", headers=bob,
                        json={"title": "Modified without approval"}).status_code == 404
    response = client.patch(f"/knowledge/articles/{aid}", headers=alice,
                            json={"title": "Revised analyzer network error code"})
    assert response.status_code == 200
    assert response.json()["version"] == 2
    client.post(f"/knowledge/articles/{aid}/submit", headers=alice)
    response = client.post(f"/knowledge/articles/{aid}/review", headers=admin,
                           json={"decision": "approve", "sharing_authorized": True})
    assert response.status_code == 200
    changed = client.patch(f"/knowledge/articles/{aid}", headers=alice,
                           json={"content": "Updated synthetic operational description with review required."})
    assert changed.status_code == 200
    assert changed.json()["review_status"] == "draft"
    with Session() as db:
        events = db.query(KnowledgeAudit).filter(KnowledgeAudit.article_id == aid).all()
        assert [e.event_type for e in events] == [
            "created", "revised", "submitted", "approved", "revised"
        ]


def test_legacy_records_quarantined_until_explicit_admin_classification():
    alice, bob, admin = headers("alice"), headers("bob"), headers("admin")
    with Session() as db:
        legacy = KBArticle(
            title="Historical example possibly confidential",
            content="SYNTHETIC-CONFIDENTIAL-BODY-DO-NOT-SHARE",
            tags="legacy",
            review_status="legacy_quarantine",
            visibility="private",
        )
        db.add(legacy)
        db.commit()
        aid = legacy.id
    assert client.get("/knowledge/legacy", headers=bob).status_code == 403
    assert client.get("/knowledge/articles", headers=alice).json() == []
    assert client.get("/knowledge/articles", headers=bob).json() == []
    inventory = client.get("/knowledge/legacy", headers=admin)
    assert inventory.status_code == 200
    assert "SYNTHETIC-CONFIDENTIAL-BODY-DO-NOT-SHARE" not in inventory.text
    assert client.get(f"/knowledge/articles/{aid}", headers=admin).status_code == 404
    classified = client.post(
        f"/knowledge/legacy/{aid}/classify", headers=admin,
        json={"owner_id": user_id("alice"), "category": "documentation"},
    )
    assert classified.status_code == 200, classified.text
    assert classified.json()["review_status"] == "draft"
    assert classified.json()["visibility"] == "private"
    assert client.get(f"/knowledge/articles/{aid}", headers=alice).status_code == 200
    assert client.get(f"/knowledge/articles/{aid}", headers=bob).status_code == 404


def test_approved_semantic_reference_is_scoped_to_access_authorized_to_server():
    alice, bob, admin = headers("alice"), headers("bob"), headers("admin")
    wid = create_workspace(admin)
    add_member(admin, wid, "alice")
    aid = client.post("/knowledge/articles", headers=alice,
                      json=article_payload(
                          visibility="workspace", workspace_id=wid
                      )).json()["id"]
    client.post(f"/knowledge/articles/{aid}/submit", headers=alice)
    client.post(f"/knowledge/articles/{aid}/review", headers=admin,
                json={"decision": "approve", "sharing_authorized": True})
    with Session() as db:
        alice_rows = get_root_cause_analysis(db, "analyzer network issue", user_id("alice"))
        bob_rows = get_root_cause_analysis(db, "analyzer network issue", user_id("bob"))
    assert len(alice_rows) == 1
    assert alice_rows[0].similarity == 0
    assert bob_rows == []
