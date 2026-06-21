"""SLA contract routes and alert projection."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_id
from app.core.database import get_db
from app.crud.playbook import (
    contract_alert,
    create_contract,
    delete_contract,
    get_contracts,
    update_contract,
)
from app.schemas.playbook import SLAContractCreate, SLAContractResponse, SLAContractUpdate

router = APIRouter()


def _response(contract) -> SLAContractResponse:
    days, alert = contract_alert(contract)
    return SLAContractResponse(
        id=contract.id,
        equipment=contract.equipment,
        vendor=contract.vendor,
        response_time_hours=contract.response_time_hours,
        penalty=contract.penalty,
        sla_compliance=contract.sla_compliance,
        expires_at=contract.expires_at,
        created_at=contract.created_at,
        days_to_expire=days,
        alert=alert,
    )


@router.get("/", response_model=List[SLAContractResponse])
def list_contracts(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return [_response(contract) for contract in get_contracts(db)]


@router.get("/alerts", response_model=List[SLAContractResponse])
def list_contract_alerts(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return [item for item in (_response(contract) for contract in get_contracts(db)) if item.alert]


@router.post("/", response_model=SLAContractResponse, status_code=status.HTTP_201_CREATED)
def create_new_contract(
    payload: SLAContractCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return _response(create_contract(db, payload))


@router.put("/{contract_id}", response_model=SLAContractResponse)
def update_existing_contract(
    contract_id: int,
    payload: SLAContractUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    contract = update_contract(db, contract_id, payload)
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")
    return _response(contract)


@router.delete("/{contract_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_contract(
    contract_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    if not delete_contract(db, contract_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")
