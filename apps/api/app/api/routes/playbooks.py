"""Playbook CRUD routes."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import AuthenticatedUser, get_current_user_id, require_access_level
from app.api.tenant import TenantContext, get_tenant_context
from app.core.database import get_db
from app.crud.playbook import (
    create_playbook,
    delete_playbook,
    get_playbooks,
    update_playbook,
)
from app.schemas.playbook import PlaybookCreate, PlaybookResponse, PlaybookUpdate

router = APIRouter()


@router.get("/", response_model=List[PlaybookResponse])
def list_playbooks(
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
    tenant: TenantContext = Depends(get_tenant_context),
):
    return get_playbooks(db, tenant.organization_id, search=search)


@router.post("/", response_model=PlaybookResponse, status_code=status.HTTP_201_CREATED)
def create_new_playbook(
    payload: PlaybookCreate,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(require_access_level(3)),
    tenant: TenantContext = Depends(get_tenant_context),
):
    return create_playbook(db, payload, tenant.organization_id)


@router.put("/{playbook_id}", response_model=PlaybookResponse)
def update_existing_playbook(
    playbook_id: int,
    payload: PlaybookUpdate,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(require_access_level(3)),
    tenant: TenantContext = Depends(get_tenant_context),
):
    playbook = update_playbook(db, playbook_id, payload, tenant.organization_id)
    if not playbook:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playbook not found")
    return playbook


@router.delete("/{playbook_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_playbook(
    playbook_id: int,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(require_access_level(3)),
    tenant: TenantContext = Depends(get_tenant_context),
):
    if not delete_playbook(db, playbook_id, tenant.organization_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playbook not found")
