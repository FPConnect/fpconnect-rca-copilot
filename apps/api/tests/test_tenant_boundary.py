"""API-level tests for enabled equipment access and disabled unsafe routers."""

import importlib.util
from io import BytesIO
import os
from pathlib import Path
import subprocess
import sys

import pytest
from alembic.migration import MigrationContext
from alembic.operations import Operations
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient
from PIL import Image
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.core.security import create_access_token, hash_password
from app.main import app
from app.models.machine import Machine
from app.models.organization import Organization, OrganizationMembership, TenantProvisionAudit
from app.models.ticket import KBArticle, RCASuggestion, Ticket, TicketAttachment, TicketLog
from app.models.playbook import Playbook, SLAContract
from app.models.user import User
from scripts.provision_organization import bootstrap
from scripts.grant_membership import grant


@pytest.fixture
def api():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    sessions = sessionmaker(bind=engine)
    with sessions.begin() as db:
        db.add_all([
            User(id=1, email="a@example.com", hashed_password=hash_password("SecurePass123!"), role="master", access_level=5, phone_number="+15551234567"),
            User(id=2, email="b@example.test", hashed_password="unused", role="user", access_level=2),
            User(id=3, email="c@example.test", hashed_password="unused", role="user", access_level=2),
            Organization(id=1, slug="a", name="A"),
            Organization(id=2, slug="b", name="B"),
        ])
        db.flush()
        db.add_all([
            OrganizationMembership(user_id=1, organization_id=1, role="master"),
            OrganizationMembership(user_id=2, organization_id=2, role="user"),
            Machine(id=1, organization_id=1, code="A", name="A", location="A", type="x"),
            Machine(id=2, organization_id=2, code="B", name="B", location="B", type="x"),
            Machine(id=3, organization_id=None, code="unmapped", name="U", location="U", type="x"),
            Ticket(id=1, organization_id=1, title="Tenant A", creator_id=1),
            Ticket(id=2, organization_id=2, title="Tenant B", creator_id=2),
            Ticket(id=3, organization_id=None, title="Unmapped", creator_id=1),
            Playbook(id=10, organization_id=None, title="Unmapped", equipment="xx", steps="steps"),
            SLAContract(id=10, organization_id=None, equipment="xx", vendor="V", response_time_hours=1),
            KBArticle(id=10, organization_id=None, title="Unmapped", content="Unknown"),
        ])
    def override_db():
        with sessions() as db:
            yield db
    old = app.dependency_overrides.get(get_db)
    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as client:
        yield client, sessions
    if old is None:
        app.dependency_overrides.pop(get_db, None)
    else:
        app.dependency_overrides[get_db] = old
    engine.dispose()


def headers(user_id=1, org=1, role="master", level=5):
    claims = {"sub": str(user_id), "role": role, "access_level": level, "ver": 0}
    result = {"Authorization": f"Bearer {create_access_token(claims)}"}
    if org is not None:
        result["X-Organization-Id"] = str(org)
    return result


def test_equipment_list_and_discovery_are_membership_scoped(api):
    client, sessions = api
    assert client.get("/auth/organizations", headers=headers()).json() == [
        {"id": 1, "slug": "a", "name": "A"}
    ]
    assert client.get("/auth/organizations", headers=headers(3, None, "user", 2)).json() == []
    assert [m["code"] for m in client.get("/machines/", headers=headers()).json()] == ["A"]
    assert [m["code"] for m in client.get("/machines/", headers=headers(2, 2, "user", 2)).json()] == ["B"]
    assert client.get("/machines/", headers=headers(org=2)).status_code == 403
    assert client.get("/machines/", headers=headers(org=None)).status_code == 422
    assert client.get("/machines/", headers=headers(3, 1, "user", 2)).status_code == 403
    with sessions.begin() as db:
        db.query(OrganizationMembership).filter_by(user_id=1).one().is_active = False
    assert client.get("/machines/", headers=headers()).status_code == 403


@pytest.mark.parametrize(
    "method,path",
    [
        (method, route.path.replace("{ticket_id}", "2").replace("{user_id}", "2")
         .replace("{contract_id}", "2").replace("{playbook_id}", "2")
         .replace("{equipment_code}", "B"))
        for route in app.routes
        if isinstance(route, APIRoute)
        and route.path.startswith(("/tickets", "/users", "/contracts", "/playbooks",
                                   "/analyze", "/notifications", "/enterprise", "/machines"))
        for method in route.methods
    ],
)
def test_each_customer_route_rejects_foreign_org_selection(api, method, path):
    client, _ = api
    assert client.request(method, path, headers=headers(org=2), json={}).status_code == 403


def test_login_discovery_select_switch_and_refresh(api):
    client, sessions = api
    login = client.post("/auth/login", json={"email": "a@example.com", "password": "SecurePass123!"})
    assert login.status_code == 200
    tokens = login.json()
    bearer = {"Authorization": f"Bearer {tokens['access_token']}"}
    assert client.get("/auth/organizations", headers=bearer).json()[0]["id"] == 1
    assert client.post("/auth/select-organization", headers={**bearer, "X-Organization-Id": "2"}).status_code == 403
    selection = client.post("/auth/select-organization", headers={**bearer, "X-Organization-Id": "1"})
    assert selection.json() == {"organization_id": 1, "role": "master", "access_level": 5}
    refresh = client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert refresh.status_code == 200
    renewed = {"Authorization": f"Bearer {refresh.json()['access_token']}", "X-Organization-Id": "1"}
    assert client.get("/machines/", headers=renewed).status_code == 200
    with sessions.begin() as db:
        db.query(OrganizationMembership).filter_by(user_id=1).one().is_active = False
    assert client.get("/machines/", headers=renewed).status_code == 403


def test_ticket_crud_is_tenant_scoped_and_unmapped_rows_are_invisible(api):
    client, sessions = api
    a = headers()
    b = headers(2, 2, "user", 2)
    created = client.post("/tickets/", headers=b, json={"title": "B ticket", "device_id": "B"})
    assert created.status_code == 201
    ticket_id = created.json()["id"]
    assert client.post("/tickets/", headers=b, json={"title": "Bad", "device_id": "A"}).status_code == 404
    assert client.post("/tickets/", headers=b, json={"title": "Bad", "device_id": "unmapped"}).status_code == 404
    assert client.get("/tickets/", headers=a).json()[0]["id"] == 1
    assert {item["id"] for item in client.get("/tickets/", headers=b).json()} == {2, ticket_id}
    for ticket in (2, 3, ticket_id):
        assert client.get(f"/tickets/{ticket}", headers=a).status_code == 404
        assert client.patch(f"/tickets/{ticket}", headers=a, json={"title": "stolen"}).status_code == 404
        assert client.delete(f"/tickets/{ticket}", headers=a).status_code == 404
    assert client.patch("/tickets/1", headers=a, json={"assignee_id": 2}).status_code == 404
    assert client.patch("/tickets/1", headers=a, json={"assignee_id": 1}).status_code == 200
    assert client.patch(f"/tickets/{ticket_id}", headers=b, json={"title": "updated"}).status_code == 200
    assert client.delete(f"/tickets/{ticket_id}", headers=b).status_code == 204
    with sessions() as db:
        assert db.query(Ticket).filter_by(id=3).one().title == "Unmapped"


def test_admin_user_management_is_scoped_and_multi_membership_change_is_local(api):
    client, sessions = api
    a = headers()
    assert {u["id"] for u in client.get("/users", headers=a).json()} == {1}
    assert client.patch("/users/2", headers=a, json={"is_active": False}).status_code == 404
    assert client.patch("/users/3", headers=a, json={"is_active": False}).status_code == 404
    created = client.post("/users", headers=a, json={
        "email": "new@example.com", "password": "SecurePass123!", "role": "user",
        "organization_id": 2,
    })
    assert created.status_code == 422
    created = client.post("/users", headers=a, json={
        "email": "new@example.com", "password": "SecurePass123!", "role": "user",
    })
    assert created.status_code == 201
    target_id = created.json()["id"]
    with sessions.begin() as db:
        membership = db.query(OrganizationMembership).filter_by(user_id=target_id).one()
        assert membership.organization_id == 1
        db.add(OrganizationMembership(user_id=target_id, organization_id=2, role="manager"))
    assert client.patch(f"/users/{target_id}", headers=a, json={"is_active": False}).status_code == 200
    with sessions() as db:
        assert db.query(OrganizationMembership).filter_by(user_id=target_id, organization_id=2).one().is_active
        assert db.query(OrganizationMembership).filter_by(user_id=target_id, organization_id=2).one().role == "manager"
    assert client.get("/users", headers=headers(org=2)).status_code == 403


def test_membership_roles_enforced_per_org_with_live_revocation(api):
    client, sessions = api
    with sessions.begin() as db:
        db.add(OrganizationMembership(user_id=1, organization_id=2, role="visitor"))
    assert client.get("/users", headers=headers()).status_code == 200
    assert client.get("/users", headers=headers(org=2)).status_code == 403
    assert client.post("/tickets/", headers=headers(org=2), json={"title": "not permitted"}).status_code == 403
    assert client.get("/tickets/2", headers=headers(org=2)).status_code == 404
    assert client.get("/tickets/2/attachments", headers=headers(org=2)).status_code == 404
    with sessions.begin() as db:
        db.query(OrganizationMembership).filter_by(user_id=1, organization_id=2).one().role = "manager"
    assert client.get("/tickets/2", headers=headers(org=2)).status_code == 200
    assert client.get("/users", headers=headers(org=2)).status_code == 403


def test_operator_grant_membership_is_explicit_atomic_and_audited(api):
    _, sessions = api
    with sessions.begin() as db:
        grant(db, organization_id=2, user_id=1, role="visitor",
              operator="operator", change_reference="CHG-7")
    with sessions() as db:
        assert db.query(OrganizationMembership).filter_by(user_id=1, organization_id=2).one().role == "visitor"
        assert '"grant_membership"' in db.query(TenantProvisionAudit).one().other_resource_ids
    with pytest.raises(ValueError):
        with sessions.begin() as db:
            grant(db, organization_id=2, user_id=1, role="master",
                  operator="operator", change_reference="CHG-8")
    with sessions() as db:
        assert db.query(OrganizationMembership).filter_by(user_id=1, organization_id=2).one().role == "visitor"
        assert db.query(TenantProvisionAudit).count() == 1


def test_attachments_require_scoped_parent_and_exclude_unmapped_metadata(api, monkeypatch):
    from app.api.routes import tickets as routes
    client, sessions = api
    uploaded = []
    monkeypatch.setattr(routes, "upload_file_object", lambda **kw: uploaded.append(kw["object_key"]))
    monkeypatch.setattr(routes, "create_presigned_get_url", lambda key: f"https://storage.test/{key}")
    with sessions.begin() as db:
        db.add(TicketAttachment(ticket_id=1, organization_id=None, uploader_id=1,
                                object_key="legacy", filename="old.png", content_type="image/png", size_bytes=1))
    data = BytesIO()
    Image.new("RGB", (1, 1)).save(data, format="PNG")
    files = {"file": ("safe.png", data.getvalue(), "image/png")}
    assert client.post("/tickets/2/attachments/images", headers=headers(), files=files).status_code == 404
    assert client.post("/tickets/3/attachments/images", headers=headers(), files=files).status_code == 404
    assert uploaded == []
    response = client.post("/tickets/1/attachments/images", headers=headers(), files=files)
    assert response.status_code == 201
    assert response.headers["cache-control"] == "private, no-store"
    assert uploaded[0].startswith("organizations/1/tickets/1/")
    listed = client.get("/tickets/1/attachments", headers=headers())
    assert listed.headers["cache-control"] == "private, no-store"
    result = listed.json()
    assert len(result) == 1 and result[0]["filename"] == "safe.png"
    assert client.delete("/tickets/1", headers=headers()).status_code == 409
    assert client.get("/tickets/1/attachments", headers=headers(2, 2, "user", 2)).status_code == 404
    assert client.get("/tickets/3/attachments", headers=headers()).status_code == 404


def test_analysis_is_scoped_and_confirmation_is_not_cross_tenant(api, monkeypatch):
    from app.api.routes import analyze as routes
    from app.schemas.ticket import RCASuggestionResponse
    client, sessions = api
    seen = []
    def fake_analysis(db, ticket, request):
        seen.append(ticket.organization_id)
        return [RCASuggestionResponse(cause="suggestion", confidence=0.1, resolution="review")]
    monkeypatch.setattr(routes, "analyze_ticket", fake_analysis)
    for ticket_id in (2, 3):
        assert client.post("/analyze", headers=headers(), json={"ticket_id": ticket_id}).status_code == 404
        assert client.post(f"/analyze/{ticket_id}/confirm", headers=headers(), json={
            "root_cause": "root cause", "recommendation": "review equipment",
            "evidence_refs": ["REF-1"], "confirmed": True,
        }).status_code == 404
    assert seen == []
    assert client.post("/analyze", headers=headers(), json={"ticket_id": 1}).status_code == 200
    assert seen == [1]
    assert client.post("/analyze/1/confirm", headers=headers(), json={
        "root_cause": "root cause", "recommendation": "review equipment",
        "evidence_refs": ["REF-1"], "confirmed": True,
    }).status_code == 200
    from app.models.ticket import TicketLog
    with sessions() as db:
        assert {log.organization_id for log in db.query(TicketLog).all()} == {1}
        assert db.query(Ticket).filter_by(id=2).one().root_cause is None


def test_knowledge_query_filters_before_ranking(monkeypatch):
    from app.services import analyze_service
    class Model:
        def encode(self, description):
            class Vector:
                def tolist(self):
                    return [0.0, 0.1]
            return Vector()
    class DB:
        def execute(self, query, params):
            assert "WHERE organization_id = :organization_id" in str(query)
            assert params["organization_id"] == 2
            class Result:
                def fetchall(self):
                    return []
            return Result()
    monkeypatch.setattr(analyze_service, "get_model", lambda: Model())
    assert analyze_service.get_root_cause_analysis(DB(), "test", 2) == []


def test_notification_preview_requires_selected_membership(api, monkeypatch):
    from app.core.config import settings
    client, _ = api
    monkeypatch.setattr(settings, "app_env", "development")
    response = client.post("/notifications/sms", headers=headers(), json={"message": "Test"})
    assert response.status_code == 200
    assert response.json()["delivered"] is False
    assert client.post("/notifications/sms", headers=headers(org=2), json={"message": "Test"}).status_code == 403
    assert client.post("/notifications/sms", headers=headers(org=None), json={"message": "Test"}).status_code == 422


def test_stateless_enterprise_calculations_require_active_membership(api):
    client, _ = api
    assert client.get("/enterprise/rca/methods", headers=headers()).status_code == 200
    assert client.get("/enterprise/rca/methods", headers=headers(org=2)).status_code == 403
    assert client.get("/enterprise/rca/methods", headers=headers(org=None)).status_code == 422


def test_equipment_report_rejects_foreign_and_unmapped_machines(api, monkeypatch):
    from app.api.routes import enterprise
    client, sessions = api
    with sessions.begin() as db:
        db.add(Ticket(id=30, organization_id=1, title="own report ticket", creator_id=1, device_id="A"))
        db.add(Ticket(id=31, organization_id=2, title="foreign report ticket", creator_id=1, device_id="A"))
        db.add(Ticket(id=32, organization_id=None, title="legacy report ticket", creator_id=1, device_id="A"))
    seen = []
    def fake_pdf(equipment, tickets, **kwargs):
        seen.extend(record.ticket_id for record in tickets)
        return b"%PDF-test", "report.pdf"
    monkeypatch.setattr(enterprise, "generate_equipment_pdf", fake_pdf)
    assert client.get("/enterprise/reports/equipment/A", headers=headers()).status_code == 200
    assert seen == [30]
    assert client.get("/enterprise/reports/equipment/B", headers=headers()).status_code == 404
    assert client.get("/enterprise/reports/equipment/unmapped", headers=headers()).status_code == 404
    assert client.get("/enterprise/reports/equipment/A", headers=headers(org=2)).status_code == 403


@pytest.mark.parametrize(
    "path,payload,update",
    [
        ("/playbooks", {"title": "Playbook", "equipment": "equipment", "steps": "step one"}, {"title": "Updated"}),
        ("/contracts", {"equipment": "equipment", "vendor": "vendor", "response_time_hours": 4}, {"vendor": "Updated"}),
    ],
)
def test_playbooks_and_contracts_are_scoped_for_master_and_quarantine(api, path, payload, update):
    client, sessions = api
    with sessions.begin() as db:
        db.add(OrganizationMembership(user_id=1, organization_id=2, role="master"))
    a, b = headers(), headers(org=2)
    created_a = client.post(path + "/", headers=a, json={**payload, "organization_id": 2})
    created_b = client.post(path + "/", headers=b, json=payload)
    assert created_a.status_code == created_b.status_code == 201
    id_a, id_b = created_a.json()["id"], created_b.json()["id"]
    assert {row["id"] for row in client.get(path + "/", headers=a).json()} == {id_a}
    assert {row["id"] for row in client.get(path + "/", headers=b).json()} == {id_b}
    for foreign_id in (id_b, 10):
        assert client.put(f"{path}/{foreign_id}", headers=a, json=update).status_code == 404
        assert client.delete(f"{path}/{foreign_id}", headers=a).status_code == 404
    assert client.put(f"{path}/{id_a}", headers=a, json=update).status_code == 200
    assert client.delete(f"{path}/{id_a}", headers=a).status_code == 204
    assert client.get(path + "/", headers=headers(org=None)).status_code == 422


def test_bootstrap_is_atomic_and_requires_explicit_unmapped_rows(api):
    _, sessions = api
    with sessions.begin() as db:
        org_id = bootstrap(db, slug="new", name="New", user_id=3, machine_ids=[3],
                           operator="operator", change_reference="CHG-1")
    with sessions() as db:
        assert db.query(Machine).filter_by(id=3).one().organization_id == org_id
        assert db.query(OrganizationMembership).filter_by(user_id=3, organization_id=org_id).count() == 1
        assert db.query(TenantProvisionAudit).filter_by(organization_id=org_id).one().machine_ids == "[3]"
    with pytest.raises(ValueError):
        with sessions.begin() as db:
            bootstrap(db, slug="other", name="Other", user_id=3, machine_ids=[1, 999],
                      operator="operator", change_reference="CHG-2")
    with sessions() as db:
        assert db.query(Organization).filter_by(slug="other").count() == 0
        assert db.query(TenantProvisionAudit).count() == 1
    with pytest.raises(ValueError):
        with sessions.begin() as db:
            bootstrap(db, slug="other", name="Other", user_id=3, machine_ids=[3],
                      operator="operator", change_reference="CHG-2")


def test_ticket_mapping_rejects_ambiguous_relationships_atomically(api):
    _, sessions = api
    with sessions.begin() as db:
        db.add(Ticket(id=20, organization_id=None, title="legacy", creator_id=3, device_id="unmapped"))
        db.add(Ticket(id=21, organization_id=None, title="ambiguous", creator_id=1))
    with pytest.raises(ValueError):
        with sessions.begin() as db:
            bootstrap(db, slug="mapping", name="Mapping", user_id=3, machine_ids=[3], ticket_ids=[20, 21],
                      operator="operator", change_reference="CHG-3")
    with sessions() as db:
        assert db.query(Organization).filter_by(slug="mapping").count() == 0
        assert db.query(Ticket).filter_by(id=20).one().organization_id is None
        assert db.query(Machine).filter_by(id=3).one().organization_id is None
    with sessions.begin() as db:
        org_id = bootstrap(db, slug="mapping", name="Mapping", user_id=3, machine_ids=[3], ticket_ids=[20],
                           operator="operator", change_reference="CHG-3")
    with sessions() as db:
        assert db.query(Ticket).filter_by(id=20).one().organization_id == org_id
        assert db.query(TenantProvisionAudit).one().ticket_ids == "[20]"


def test_child_mapping_requires_explicit_complete_consistent_set(api, monkeypatch):
    from app.api.routes import tickets as routes
    client, sessions = api
    with sessions.begin() as db:
        db.add(Ticket(id=20, organization_id=None, title="legacy", creator_id=3))
        db.add(TicketAttachment(id=20, ticket_id=20, uploader_id=3, object_key="legacy-key",
                                filename="file.png", content_type="image/png", size_bytes=1))
        db.add(TicketLog(id=20, ticket_id=20, user_id=3, action="legacy"))
        db.add(RCASuggestion(id=20, ticket_id=20, cause="legacy"))
    with pytest.raises(ValueError):
        with sessions.begin() as db:
            bootstrap(db, slug="legacy-map", name="Legacy", user_id=3, machine_ids=[],
                      ticket_ids=[20], attachment_ids=[20], role="user",
                      operator="operator", change_reference="CHG-6")
    with sessions() as db:
        assert db.query(Ticket).filter_by(id=20).one().organization_id is None
        assert db.query(Organization).filter_by(slug="legacy-map").count() == 0
    with sessions.begin() as db:
        org_id = bootstrap(db, slug="legacy-map", name="Legacy", user_id=3, machine_ids=[],
                           ticket_ids=[20], attachment_ids=[20], log_ids=[20], suggestion_ids=[20],
                           role="user", operator="operator", change_reference="CHG-6")
    with sessions() as db:
        for model in (TicketAttachment, TicketLog, RCASuggestion):
            assert db.query(model).filter_by(id=20).one().organization_id == org_id
        audit = db.query(TenantProvisionAudit).one().other_resource_ids
        assert '"attachments": [20]' in audit and '"membership_role": "user"' in audit
    monkeypatch.setattr(routes, "create_presigned_get_url", lambda key: f"https://storage.test/{key}")
    legacy = headers(3, org_id, "user", 2)
    assert len(client.get("/tickets/20/attachments", headers=legacy).json()) == 1
    assert client.get("/tickets/20/attachments", headers=headers()).status_code == 404
    assert client.delete("/tickets/20", headers=legacy).status_code == 409


def test_explicit_mapping_of_independent_resource_types(api):
    _, sessions = api
    with sessions.begin() as db:
        org_id = bootstrap(
            db, slug="resource-map", name="Mapped", user_id=3, machine_ids=[],
            playbook_ids=[10], contract_ids=[10], article_ids=[10],
            operator="operator", change_reference="CHG-4",
        )
    with sessions() as db:
        assert db.query(Playbook).filter_by(id=10).one().organization_id == org_id
        assert db.query(SLAContract).filter_by(id=10).one().organization_id == org_id
        assert db.query(KBArticle).filter_by(id=10).one().organization_id == org_id
        assert '"kb_articles": [10]' in db.query(TenantProvisionAudit).one().other_resource_ids
    with pytest.raises(ValueError):
        with sessions.begin() as db:
            bootstrap(
                db, slug="duplicate-map", name="Duplicate", user_id=3, machine_ids=[],
                article_ids=[10], operator="operator", change_reference="CHG-5",
            )
    with sessions() as db:
        assert db.query(Organization).filter_by(slug="duplicate-map").count() == 0


def test_cli_requires_operator_database_and_commits_audited_mapping(tmp_path):
    database = tmp_path / "provision.db"
    url = f"sqlite:///{database.as_posix()}"
    engine = create_engine(url)
    Base.metadata.create_all(engine)
    sessions = sessionmaker(bind=engine)
    with sessions.begin() as db:
        db.add(User(id=1, email="cli@example.test", hashed_password="unused", role="user", access_level=2))
        db.add(Machine(id=1, code="legacy", name="Legacy", location="Unknown", type="x"))
    command = [
        sys.executable, "-m", "scripts.provision_organization", "--slug", "new", "--name", "New",
        "--user-id", "1", "--role", "user", "--machine-id", "1", "--change-reference", "CHG-1",
        "--confirm", "CREATE_AND_MAP",
    ]
    env = os.environ.copy()
    env.pop("TENANT_PROVISION_DATABASE_URL", None)
    cwd = str(Path(__file__).parents[1])
    denied = subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True, check=False)
    assert denied.returncode != 0
    with sessions() as db:
        assert db.query(Organization).count() == 0
    env["TENANT_PROVISION_DATABASE_URL"] = url
    result = subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
    with sessions() as db:
        assert db.query(Machine).one().organization_id == db.query(Organization).one().id
        assert db.query(TenantProvisionAudit).one().change_reference == "CHG-1"
    assert subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True, check=False).returncode != 0
    with sessions() as db:
        assert db.query(TenantProvisionAudit).count() == 1
    engine.dispose()


def test_machine_migration_quarantines_legacy_and_downgrade():
    path = Path(__file__).parents[1] / "alembic" / "versions" / "009_quarantine_machines.py"
    spec = importlib.util.spec_from_file_location("machine_migration", path)
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    engine = create_engine("sqlite://")
    with engine.begin() as connection:
        connection.execute(text("CREATE TABLE users (id INTEGER PRIMARY KEY)"))
        connection.execute(text("CREATE TABLE organizations (id INTEGER PRIMARY KEY)"))
        connection.execute(text("CREATE TABLE machines (id INTEGER PRIMARY KEY)"))
        connection.execute(text("INSERT INTO machines (id) VALUES (10)"))
        context = MigrationContext.configure(connection)
        with Operations.context(context):
            migration.upgrade()
        assert connection.execute(text("SELECT organization_id FROM machines WHERE id=10")).scalar_one() is None
        with Operations.context(context):
            migration.downgrade()
        assert connection.execute(text("SELECT id FROM machines")).scalar_one() == 10
    engine.dispose()


def test_membership_role_migration_does_not_infer_privilege():
    path = Path(__file__).parents[1] / "alembic" / "versions" / "016_membership_roles.py"
    spec = importlib.util.spec_from_file_location("membership_role_migration", path)
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    engine = create_engine("sqlite://")
    with engine.begin() as connection:
        connection.execute(text("CREATE TABLE organization_memberships (id INTEGER PRIMARY KEY)"))
        connection.execute(text("INSERT INTO organization_memberships (id) VALUES (10)"))
        context = MigrationContext.configure(connection)
        with Operations.context(context):
            migration.upgrade()
        assert connection.execute(text("SELECT role FROM organization_memberships")).scalar_one() == "visitor"
        with Operations.context(context):
            migration.downgrade()
        assert connection.execute(text("SELECT id FROM organization_memberships")).scalar_one() == 10
    engine.dispose()


@pytest.mark.parametrize("existing_history_tables", [False, True])
def test_resource_migrations_quarantine_existing_rows_and_reverse(existing_history_tables):
    root = Path(__file__).parents[1] / "alembic" / "versions"
    names = [
        "010_quarantine_tickets.py",
        "011_quarantine_contracts_playbooks.py",
        "012_ticket_mapping_audit.py",
        "013_quarantine_attachments.py",
        "014_quarantine_knowledge.py",
        "015_add_resource_mapping_audit.py",
    ]
    migrations = []
    for name in names:
        spec = importlib.util.spec_from_file_location(name[:-3], root / name)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        migrations.append(module)
    engine = create_engine("sqlite://")
    tables = ["tickets", "playbooks", "sla_contracts", "ticket_attachments", "kb_articles"]
    with engine.begin() as connection:
        for table in ["users", "organizations", "tenant_provision_audit", *tables]:
            connection.execute(text(f"CREATE TABLE {table} (id INTEGER PRIMARY KEY)"))
        for table in tables:
            connection.execute(text(f"INSERT INTO {table} (id) VALUES (10)"))
        if existing_history_tables:
            connection.execute(text("CREATE TABLE ticket_logs (id INTEGER PRIMARY KEY)"))
            connection.execute(text("CREATE TABLE rca_suggestions (id INTEGER PRIMARY KEY)"))
        context = MigrationContext.configure(connection)
        with Operations.context(context):
            for migration in migrations:
                migration.upgrade()
        for table in tables:
            assert connection.execute(
                text(f"SELECT organization_id FROM {table} WHERE id=10")
            ).scalar_one() is None
        with Operations.context(context):
            for migration in reversed(migrations):
                migration.downgrade()
        for table in tables:
            assert connection.execute(text(f"SELECT id FROM {table}")).scalar_one() == 10
    engine.dispose()
