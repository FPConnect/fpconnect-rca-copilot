"""Ticket CRUD routes and RCA analysis endpoint."""

from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.crud.ticket import (
    create_ticket,
    delete_ticket,
    get_ticket_by_id,
    get_tickets,
    update_ticket,
)
from app.crud.user import get_user_by_id
from app.schemas.ticket import (
    AnalyzeTicketRequest,
    AnalyzeTicketResponse,
    TicketCreate,
    TicketResponse,
    TicketUpdate,
)
from app.services.analyze_service import analyze_ticket
from app.services.n8n_service import notify_sla_workflow

router = APIRouter()


def get_current_user_id(authorization: Optional[str] = Header(None)) -> int:
    """Extract and validate the current user ID from the Authorization header."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    token = authorization.split(" ", 1)[1]
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    return int(payload["sub"])


@router.get("/", response_model=List[TicketResponse])
def list_tickets(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Return a paginated list of tickets."""
    return get_tickets(db, skip=skip, limit=limit)


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Return a single ticket by ID."""
    ticket = get_ticket_by_id(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    return ticket


@router.post("/", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
def create_new_ticket(
    ticket_data: TicketCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Create a new support ticket."""
    ticket = create_ticket(db, ticket_data, creator_id=user_id)
    background_tasks.add_task(notify_sla_workflow, ticket, "ticket.created", user_id)
    return ticket


@router.patch("/{ticket_id}", response_model=TicketResponse)
def update_existing_ticket(
    ticket_id: int,
    ticket_data: TicketUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Update an existing ticket's fields."""
    ticket = update_ticket(db, ticket_id, ticket_data)
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    background_tasks.add_task(notify_sla_workflow, ticket, "ticket.updated", user_id)
    return ticket


@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Delete a ticket by ID."""
    if not delete_ticket(db, ticket_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")


@router.post("/{ticket_id}/analyze", response_model=AnalyzeTicketResponse)
def analyze_existing_ticket(
    ticket_id: int,
    request: AnalyzeTicketRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Run RCA analysis on a ticket and return suggestions."""
    ticket = get_ticket_by_id(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    suggestions = analyze_ticket(db, ticket, request)
    return AnalyzeTicketResponse(ticket_id=ticket_id, suggestions=suggestions)
