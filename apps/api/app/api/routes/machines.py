"""Machine routes."""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_id
from app.core.database import get_db
from app.crud.machine import get_machines
from app.schemas.machine import MachineResponse

router = APIRouter()


@router.get("/", response_model=List[MachineResponse])
def list_machines(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return get_machines(db)
