"""Restricted operator CLI to grant an existing user an organization membership."""
import argparse
import getpass
import json
import os
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.models.organization import Organization, OrganizationMembership, TenantProvisionAudit
from app.models.user import User


def grant(db: Session, *, organization_id: int, user_id: int, role: str,
          operator: str, change_reference: str) -> None:
    if (organization_id <= 0 or user_id <= 0
            or role not in {"master", "admin", "manager", "user", "visitor"}
            or not operator.strip() or len(operator) > 255
            or not change_reference.strip() or len(change_reference) > 255):
        raise ValueError("Invalid grant details")
    user = db.query(User).filter_by(id=user_id, is_active=True).with_for_update().one_or_none()
    organization = db.query(Organization).filter_by(
        id=organization_id, is_active=True
    ).with_for_update().one_or_none()
    if not user or not organization:
        raise ValueError("Active user and organization required")
    if db.query(OrganizationMembership).filter_by(user_id=user_id, organization_id=organization_id).first():
        raise ValueError("Membership already exists")
    db.add(OrganizationMembership(user_id=user_id, organization_id=organization_id, role=role))
    db.add(TenantProvisionAudit(
        organization_id=organization_id,
        user_id=user_id,
        operator=operator,
        change_reference=change_reference,
        machine_ids="[]",
        ticket_ids="[]",
        other_resource_ids=json.dumps({"action": "grant_membership", "membership_role": role}),
    ))
    db.flush()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--organization-id", required=True, type=int)
    parser.add_argument("--user-id", required=True, type=int)
    parser.add_argument("--role", required=True, choices=["master", "admin", "manager", "user", "visitor"])
    parser.add_argument("--change-reference", required=True)
    parser.add_argument("--confirm", required=True, choices=["GRANT_MEMBERSHIP"])
    args = parser.parse_args()
    url = os.environ.get("TENANT_PROVISION_DATABASE_URL")
    if not url:
        print("TENANT_PROVISION_DATABASE_URL is required.", file=sys.stderr)
        return 2
    engine = create_engine(url)
    try:
        with Session(engine) as db, db.begin():
            grant(db, organization_id=args.organization_id, user_id=args.user_id, role=args.role,
                  operator=getpass.getuser(), change_reference=args.change_reference)
        print("Membership granted and audited.")
        return 0
    except Exception:
        print("Grant failed; no changes committed.", file=sys.stderr)
        return 1
    finally:
        engine.dispose()


if __name__ == "__main__":
    raise SystemExit(main())
