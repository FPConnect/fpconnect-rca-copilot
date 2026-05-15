"""CRUD helpers for clinical playbooks and SLA contracts."""

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.playbook import Playbook, SLAContract
from app.schemas.playbook import (
    PlaybookCreate,
    PlaybookUpdate,
    SLAContractCreate,
    SLAContractUpdate,
)


def get_playbooks(db: Session, search: Optional[str] = None) -> List[Playbook]:
    query = db.query(Playbook)
    if search:
        pattern = f"%{search}%"
        query = query.filter(
            (Playbook.title.ilike(pattern)) | (Playbook.equipment.ilike(pattern))
        )
    return query.order_by(Playbook.title.asc()).all()


def get_playbook(db: Session, playbook_id: int) -> Optional[Playbook]:
    return db.query(Playbook).filter(Playbook.id == playbook_id).first()


def create_playbook(db: Session, payload: PlaybookCreate) -> Playbook:
    playbook = Playbook(**payload.model_dump())
    db.add(playbook)
    db.commit()
    db.refresh(playbook)
    return playbook


def update_playbook(db: Session, playbook_id: int, payload: PlaybookUpdate) -> Optional[Playbook]:
    playbook = get_playbook(db, playbook_id)
    if not playbook:
        return None
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(playbook, field, value)
    db.commit()
    db.refresh(playbook)
    return playbook


def delete_playbook(db: Session, playbook_id: int) -> bool:
    playbook = get_playbook(db, playbook_id)
    if not playbook:
        return False
    db.delete(playbook)
    db.commit()
    return True


def get_contracts(db: Session) -> List[SLAContract]:
    return db.query(SLAContract).order_by(SLAContract.expires_at.asc()).all()


def get_contract(db: Session, contract_id: int) -> Optional[SLAContract]:
    return db.query(SLAContract).filter(SLAContract.id == contract_id).first()


def create_contract(db: Session, payload: SLAContractCreate) -> SLAContract:
    contract = SLAContract(**payload.model_dump())
    db.add(contract)
    db.commit()
    db.refresh(contract)
    return contract


def update_contract(
    db: Session, contract_id: int, payload: SLAContractUpdate
) -> Optional[SLAContract]:
    contract = get_contract(db, contract_id)
    if not contract:
        return None
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(contract, field, value)
    db.commit()
    db.refresh(contract)
    return contract


def delete_contract(db: Session, contract_id: int) -> bool:
    contract = get_contract(db, contract_id)
    if not contract:
        return False
    db.delete(contract)
    db.commit()
    return True


def contract_alert(contract: SLAContract) -> tuple[Optional[int], Optional[str]]:
    if not contract.expires_at:
        return None, None
    expires_at = contract.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    days = (expires_at - datetime.now(timezone.utc)).days
    if days < 0:
        return days, "Contrato vencido"
    if days <= 30:
        return days, "Contrato vence em até 30 dias"
    if contract.sla_compliance < 95:
        return days, "SLA abaixo da meta"
    return days, None
