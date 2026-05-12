"""CRUD operations for Ticket model."""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.ticket import Ticket, TicketAttachment
from app.schemas.ticket import TicketCreate, TicketUpdate


def get_tickets(db: Session, skip: int = 0, limit: int = 100) -> List[Ticket]:
    """Retrieve a paginated list of tickets."""
    return db.query(Ticket).offset(skip).limit(limit).all()


def get_ticket_by_id(db: Session, ticket_id: int) -> Optional[Ticket]:
    """Retrieve a single ticket by ID."""
    return db.query(Ticket).filter(Ticket.id == ticket_id).first()


def create_ticket(db: Session, ticket_data: TicketCreate, creator_id: int) -> Ticket:
    """Create a new ticket."""
    db_ticket = Ticket(
        title=ticket_data.title,
        description=ticket_data.description,
        priority=ticket_data.priority,
        device_id=ticket_data.device_id,
        location=ticket_data.location,
        creator_id=creator_id,
    )
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket


def update_ticket(
    db: Session, ticket_id: int, ticket_data: TicketUpdate
) -> Optional[Ticket]:
    """Update an existing ticket."""
    db_ticket = get_ticket_by_id(db, ticket_id)
    if not db_ticket:
        return None
    update_data = ticket_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_ticket, field, value)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket


def delete_ticket(db: Session, ticket_id: int) -> bool:
    """Delete a ticket by ID. Returns True if deleted, False if not found."""
    db_ticket = get_ticket_by_id(db, ticket_id)
    if not db_ticket:
        return False
    db.delete(db_ticket)
    db.commit()
    return True


def create_ticket_attachment(
    db: Session,
    *,
    ticket_id: int,
    uploader_id: int,
    object_key: str,
    filename: str,
    content_type: str,
    size_bytes: int,
) -> TicketAttachment:
    """Persist metadata for an uploaded ticket attachment."""
    db_attachment = TicketAttachment(
        ticket_id=ticket_id,
        uploader_id=uploader_id,
        object_key=object_key,
        filename=filename,
        content_type=content_type,
        size_bytes=size_bytes,
    )
    db.add(db_attachment)
    db.commit()
    db.refresh(db_attachment)
    return db_attachment


def get_ticket_attachments(db: Session, ticket_id: int) -> List[TicketAttachment]:
    """Retrieve all attachments for a ticket."""
    return db.query(TicketAttachment).filter(TicketAttachment.ticket_id == ticket_id).all()
