"""Ticket CRUD routes and RCA analysis endpoint."""

from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_id
from app.core.config import settings
from app.core.database import get_db
from app.crud.ticket import (
    create_ticket,
    create_ticket_attachment,
    delete_ticket,
    get_ticket_by_id,
    get_ticket_attachments,
    get_tickets,
    update_ticket,
)
from app.schemas.ticket import (
    AnalyzeTicketRequest,
    AnalyzeTicketResponse,
    TicketAttachmentResponse,
    TicketCreate,
    TicketResponse,
    TicketUpdate,
)
from app.services.analyze_service import analyze_ticket
from app.services.object_storage import (
    build_ticket_attachment_key,
    create_presigned_get_url,
    upload_file_object,
)

router = APIRouter()


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
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Create a new support ticket."""
    return create_ticket(db, ticket_data, creator_id=user_id)


@router.patch("/{ticket_id}", response_model=TicketResponse)
def update_existing_ticket(
    ticket_id: int,
    ticket_data: TicketUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Update an existing ticket's fields."""
    ticket = update_ticket(db, ticket_id, ticket_data)
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
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


ALLOWED_IMAGE_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}


def _detect_image_mime_from_signature(body: bytes) -> str:
    """Detect supported image MIME types without external shared libraries."""
    if body.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if body.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if len(body) >= 12 and body[:4] == b"RIFF" and body[8:12] == b"WEBP":
        return "image/webp"
    return "application/octet-stream"


async def validate_image_real_type(body: bytes) -> str:
    """Validate the actual MIME type detected from the uploaded bytes."""
    mime = _detect_image_mime_from_signature(body)

    if mime not in ALLOWED_IMAGE_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Real file type {mime} is not supported",
        )
    return mime


def _attachment_response(attachment) -> TicketAttachmentResponse:
    """Build an API response with a short-lived attachment URL."""
    return TicketAttachmentResponse(
        id=attachment.id,
        ticket_id=attachment.ticket_id,
        filename=attachment.filename,
        content_type=attachment.content_type,
        size_bytes=attachment.size_bytes,
        download_url=create_presigned_get_url(attachment.object_key),
    )


@router.get(
    "/{ticket_id}/attachments",
    response_model=List[TicketAttachmentResponse],
)
def list_ticket_attachments(
    ticket_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Return image attachments for a ticket with temporary download URLs."""
    ticket = get_ticket_by_id(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    return [
        _attachment_response(attachment) for attachment in get_ticket_attachments(db, ticket_id)
    ]


@router.post(
    "/{ticket_id}/attachments/images",
    response_model=TicketAttachmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_ticket_image(
    ticket_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Upload a ticket image to MinIO/S3 and persist its metadata."""
    ticket = get_ticket_by_id(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    content_type = file.content_type or "application/octet-stream"
    if content_type not in ALLOWED_IMAGE_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only JPEG, PNG, and WebP images are supported",
        )

    body = await file.read()
    if not body:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File is empty")
    real_content_type = await validate_image_real_type(body)
    if len(body) > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File exceeds the maximum upload size",
        )

    filename = file.filename or "ticket-image"
    object_key = build_ticket_attachment_key(ticket_id, filename)
    upload_file_object(object_key=object_key, body=body, content_type=real_content_type)
    attachment = create_ticket_attachment(
        db,
        ticket_id=ticket_id,
        uploader_id=user_id,
        object_key=object_key,
        filename=filename,
        content_type=real_content_type,
        size_bytes=len(body),
    )
    return _attachment_response(attachment)
