"""Operator-only bootstrap for a new organization and explicitly mapped machines.

Run only in a controlled maintenance environment with restricted OS and database
credentials. This command is not exposed as an API endpoint.
"""
import argparse
import getpass
import json
import os
import re
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.models.machine import Machine
from app.models.organization import Organization, OrganizationMembership, TenantProvisionAudit
from app.models.ticket import Ticket, TicketAttachment, TicketLog, RCASuggestion
from app.models.ticket import KBArticle
from app.models.playbook import Playbook, SLAContract
from app.models.user import User


def bootstrap(db: Session, *, slug: str, name: str, user_id: int,
              machine_ids: list[int], operator: str, change_reference: str,
              ticket_ids: list[int] | None = None,
              playbook_ids: list[int] | None = None,
              contract_ids: list[int] | None = None,
              article_ids: list[int] | None = None,
              attachment_ids: list[int] | None = None,
              log_ids: list[int] | None = None,
              suggestion_ids: list[int] | None = None,
              role: str = "visitor") -> int:
    """Caller provides a transaction; reject ambiguous or already-owned rows."""
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug) or len(slug) > 64:
        raise ValueError("Invalid organization slug")
    if not name.strip() or len(name) > 255 or not operator.strip() or len(operator) > 255:
        raise ValueError("Organization name and operator are required")
    if not change_reference.strip() or len(change_reference) > 255:
        raise ValueError("Approved change reference required")
    if role not in {"master", "admin", "manager", "user", "visitor"}:
        raise ValueError("Invalid organization role")
    ticket_ids = ticket_ids or []
    groups = {
        "playbooks": (Playbook, playbook_ids or []),
        "contracts": (SLAContract, contract_ids or []),
        "kb_articles": (KBArticle, article_ids or []),
    }
    children = {
        "attachments": (TicketAttachment, attachment_ids or []),
        "ticket_logs": (TicketLog, log_ids or []),
        "rca_suggestions": (RCASuggestion, suggestion_ids or []),
    }
    all_id_lists = ([machine_ids, ticket_ids] + [ids for _, ids in groups.values()]
                    + [ids for _, ids in children.values()])
    if (user_id <= 0 or any(i <= 0 for ids in all_id_lists for i in ids)
            or any(len(set(ids)) != len(ids) for ids in all_id_lists)):
        raise ValueError("IDs must be positive and machine IDs unique")
    user = db.query(User).filter(User.id == user_id, User.is_active.is_(True)).with_for_update().one_or_none()
    if user is None:
        raise ValueError("Active user not found")
    if db.query(Organization.id).filter_by(slug=slug).first():
        raise ValueError("Organization slug already exists")
    machines = (
        db.query(Machine).filter(Machine.id.in_(machine_ids)).with_for_update().all()
        if machine_ids else []
    )
    if len(machines) != len(machine_ids) or any(m.organization_id is not None for m in machines):
        raise ValueError("Machine missing or already mapped; nothing was changed")
    tickets = (
        db.query(Ticket).filter(Ticket.id.in_(ticket_ids)).with_for_update().all()
        if ticket_ids else []
    )
    if len(tickets) != len(ticket_ids):
        raise ValueError("Ticket missing; nothing was changed")
    machine_codes = {machine.code for machine in machines}
    for ticket in tickets:
        if (ticket.organization_id is not None or ticket.creator_id != user_id
                or ticket.assignee_id not in (None, user_id)
                or (ticket.device_id is not None and ticket.device_id not in machine_codes)):
            raise ValueError("Ticket ownership or references are ambiguous")
    child_rows = {}
    for kind, (model, ids) in children.items():
        rows = db.query(model).filter(model.id.in_(ids)).with_for_update().all() if ids else []
        if (len(rows) != len(ids)
                or any(row.organization_id is not None or row.ticket_id not in ticket_ids for row in rows)):
            raise ValueError(f"{kind} missing, already mapped, or not under selected tickets")
        # Require explicit approval of every existing child, not an inferred cascade.
        actual = db.query(model).filter(model.ticket_id.in_(ticket_ids)).with_for_update().all() if ticket_ids else []
        if {row.id for row in actual} != set(ids):
            raise ValueError(f"All {kind} of selected tickets must be explicitly mapped")
        if kind == "attachments" and any(row.uploader_id != user_id for row in rows):
            raise ValueError("Attachment uploader ownership is ambiguous")
        if kind == "ticket_logs" and any(row.user_id not in (None, user_id) for row in rows):
            raise ValueError("Ticket log actor ownership is ambiguous")
        if kind == "rca_suggestions" and any(row.similar_incidents for row in rows):
            raise ValueError("Suggestion references require manual review")
        child_rows[kind] = rows
    other_rows = {}
    for kind, (model, ids) in groups.items():
        rows = db.query(model).filter(model.id.in_(ids)).with_for_update().all() if ids else []
        if len(rows) != len(ids) or any(row.organization_id is not None for row in rows):
            raise ValueError(f"{kind} row missing or already mapped")
        other_rows[kind] = rows
    organization = Organization(slug=slug, name=name.strip(), is_active=True)
    db.add(organization)
    db.flush()
    db.add(OrganizationMembership(user_id=user.id, organization_id=organization.id, role=role))
    for machine in machines:
        machine.organization_id = organization.id
    for ticket in tickets:
        ticket.organization_id = organization.id
    for rows in other_rows.values():
        for row in rows:
            row.organization_id = organization.id
    for rows in child_rows.values():
        for row in rows:
            row.organization_id = organization.id
    db.add(TenantProvisionAudit(
        organization_id=organization.id, user_id=user.id, operator=operator,
        change_reference=change_reference, machine_ids=json.dumps(sorted(machine_ids)),
        ticket_ids=json.dumps(sorted(ticket_ids)),
        other_resource_ids=json.dumps(
            {**{kind: sorted(ids) for kind, (_, ids) in {**groups, **children}.items()},
             "membership_role": role},
            sort_keys=True,
        ),
    ))
    db.flush()
    return organization.id


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slug", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--user-id", required=True, type=int)
    parser.add_argument("--role", required=True, choices=["master", "admin", "manager", "user", "visitor"])
    parser.add_argument("--machine-id", type=int, action="append", default=[])
    parser.add_argument("--ticket-id", type=int, action="append", default=[])
    parser.add_argument("--playbook-id", type=int, action="append", default=[])
    parser.add_argument("--contract-id", type=int, action="append", default=[])
    parser.add_argument("--article-id", type=int, action="append", default=[])
    parser.add_argument("--attachment-id", type=int, action="append", default=[])
    parser.add_argument("--log-id", type=int, action="append", default=[])
    parser.add_argument("--suggestion-id", type=int, action="append", default=[])
    parser.add_argument("--change-reference", required=True)
    parser.add_argument("--confirm", required=True, choices=["CREATE_AND_MAP"])
    args = parser.parse_args()
    database_url = os.environ.get("TENANT_PROVISION_DATABASE_URL")
    if not database_url:
        print("TENANT_PROVISION_DATABASE_URL must be supplied by the operator environment.", file=sys.stderr)
        return 2
    engine = create_engine(database_url)
    try:
        with Session(engine) as db, db.begin():
            organization_id = bootstrap(
                db, slug=args.slug, name=args.name, user_id=args.user_id,
                machine_ids=args.machine_id, operator=getpass.getuser(),
                change_reference=args.change_reference, ticket_ids=args.ticket_id,
                playbook_ids=args.playbook_id, contract_ids=args.contract_id,
                article_ids=args.article_id,
                attachment_ids=args.attachment_id, log_ids=args.log_id,
                suggestion_ids=args.suggestion_id,
                role=args.role,
            )
        print(f"Created organization {organization_id}; explicit mapping committed.")
        return 0
    except Exception:
        # Do not log connection URLs, SQL parameters, or other sensitive details.
        print("Provisioning failed; no changes committed. Inspect mapping and database access.", file=sys.stderr)
        return 1
    finally:
        engine.dispose()


if __name__ == "__main__":
    raise SystemExit(main())
