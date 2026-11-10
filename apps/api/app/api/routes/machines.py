"""Machine routes."""

from typing import List

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.api.tenant import TenantContext, get_tenant_context
from app.core.database import get_db
from app.crud.machine import get_machines
from app.schemas.machine import MachineResponse

router = APIRouter()


@router.get("/", response_model=List[MachineResponse])
def list_machines(
    response: Response,
    db: Session = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    response.headers["Cache-Control"] = "private, no-store"
    return get_machines(db, tenant.organization_id)
