"""Intel/Radar routes.

These endpoints expose curated public intelligence to the FPConnect app.

For MVP, authentication is optional (settings.intel_require_auth=False).
In production, enable auth and restrict access to admin/manager roles.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import decode_access_token, get_current_user_payload
from app.models.intel_item import IntelItem
from app.schemas.intel import IntelIngestResponse, IntelItemResponse, IntelTopicsResponse
from app.services.intel_service import ingest_once, list_topics

router = APIRouter()


def _require_user_if_enabled(authorization: Optional[str] = Header(None)) -> Optional[dict]:
    if not settings.intel_require_auth:
        return None
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    token = authorization.split(" ", 1)[1]
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    return payload


@router.get("/items", response_model=List[IntelItemResponse])
def get_items(
    topic: Optional[str] = None,
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    _payload: Optional[dict] = Depends(_require_user_if_enabled),
):
    q = db.query(IntelItem)
    if topic:
        q = q.filter(IntelItem.topic == topic)
    items = q.order_by(IntelItem.fetched_at.desc()).limit(min(limit, 200)).all()
    return items


@router.get("/topics", response_model=IntelTopicsResponse)
def get_topics(
    db: Session = Depends(get_db),
    _payload: Optional[dict] = Depends(_require_user_if_enabled),
):
    return IntelTopicsResponse(topics=list_topics(db))


@router.post("/ingest/once", response_model=IntelIngestResponse)
def run_ingest_once(
    db: Session = Depends(get_db),
    _payload: dict = Depends(get_current_user_payload),
):
    result = ingest_once(db)
    return IntelIngestResponse(**result)
