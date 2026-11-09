"""Ticket CRUD routes and RCA analysis endpoint."""

from io import BytesIO
from pathlib import Path
import re
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile, status
from PIL import Image, UnidentifiedImageError
from sqlalchemy.orm import Session

from app.api.deps import AuthenticatedUser, get_current_user, require_access_level
from app.api.tenant import TenantContext, get_tenant_context
from app.core.config import settings
from app.core.database import get_db
from app.models.machine import Machine
from app.models.organization import OrganizationMembership
from app.models.ticket import RCASuggestion, TicketAttachment, TicketLog
from app.models.user import User
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


def _authorized_ticket(db: Session, ticket_id: int, current_user: AuthenticatedUser, organization_id: int):
    """Return a visible ticket without disclosing another user's ticket IDs."""
    ticket = get_ticket_by_id(db, ticket_id, organization_id)
    if not ticket or (
        current_user.access_level < 3 and ticket.creator_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found"
        )
    return ticket


@router.get("/", response_model=List[TicketResponse])
def list_tickets(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user),
    tenant: TenantContext = Depends(get_tenant_context),
):
    """Return a paginated list of tickets."""
    creator_id = None if tenant.user.access_level >= 3 else tenant.user.id
    return get_tickets(db, tenant.organization_id, skip=skip, limit=limit, creator_id=creator_id)


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user),
    tenant: TenantContext = Depends(get_tenant_context),
):
    """Return a single ticket by ID."""
    return _authorized_ticket(db, ticket_id, tenant.user, tenant.organization_id)


@router.post("/", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
def create_new_ticket(
    ticket_data: TicketCreate,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(require_access_level(2)),
    tenant: TenantContext = Depends(get_tenant_context),
):
    """Create a new support ticket."""
    if ticket_data.device_id is not None and not db.query(Machine.id).filter(
        Machine.code == ticket_data.device_id,
        Machine.organization_id == tenant.organization_id,
    ).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipment not found")
    return create_ticket(db, ticket_data, creator_id=current_user.id, organization_id=tenant.organization_id)


@router.patch("/{ticket_id}", response_model=TicketResponse)
def update_existing_ticket(
    ticket_id: int,
    ticket_data: TicketUpdate,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(require_access_level(2)),
    tenant: TenantContext = Depends(get_tenant_context),
):
    """Update ordinary ticket fields; confirmed analysis requires human sign-off."""
    _authorized_ticket(db, ticket_id, tenant.user, tenant.organization_id)
    # Do not permit users to bypass review with a generic PATCH, including nulls.
    if {"root_cause", "recommendation", "analysis_completed"} & ticket_data.model_fields_set:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Use the human confirmation workflow for technical conclusions",
        )
    if ticket_data.assignee_id is not None and not (
        db.query(OrganizationMembership.id)
        .join(User, User.id == OrganizationMembership.user_id)
        .filter(
            OrganizationMembership.user_id == ticket_data.assignee_id,
            OrganizationMembership.organization_id == tenant.organization_id,
            OrganizationMembership.is_active.is_(True),
            User.is_active.is_(True),
        ).first()
    ):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignee not found")
    ticket = update_ticket(db, ticket_id, ticket_data, tenant.organization_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found"
        )
    return ticket


@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(require_access_level(2)),
    tenant: TenantContext = Depends(get_tenant_context),
):
    """Delete a ticket by ID."""
    _authorized_ticket(db, ticket_id, tenant.user, tenant.organization_id)
    # Do not silently orphan blobs or erase audit history. Any child row,
    # including quarantined legacy metadata, requires a retention workflow.
    for model in (TicketAttachment, TicketLog, RCASuggestion):
        if db.query(model.id).filter(model.ticket_id == ticket_id).first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ticket has dependent records; retention workflow required",
            )
    if not delete_ticket(db, ticket_id, tenant.organization_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found"
        )


@router.post("/{ticket_id}/analyze", response_model=AnalyzeTicketResponse)
def analyze_existing_ticket(
    ticket_id: int,
    request: AnalyzeTicketRequest,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(require_access_level(2)),
    tenant: TenantContext = Depends(get_tenant_context),
):
    """Run RCA analysis on a ticket and return suggestions."""
    ticket = _authorized_ticket(db, ticket_id, current_user, tenant.organization_id)
    suggestions = analyze_ticket(db, ticket, request)
    return AnalyzeTicketResponse(ticket_id=ticket_id, suggestions=suggestions)


ALLOWED_IMAGE_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
IMAGE_FORMAT_TO_MIME = {"JPEG": "image/jpeg", "PNG": "image/png", "WEBP": "image/webp"}
Image.MAX_IMAGE_PIXELS = 40_000_000


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
    signature_mime = _detect_image_mime_from_signature(body)
    try:
        with Image.open(BytesIO(body)) as image:
            image.verify()
            mime = IMAGE_FORMAT_TO_MIME.get(
                image.format or "", "application/octet-stream"
            )
    except (
        UnidentifiedImageError,
        OSError,
        SyntaxError,
        Image.DecompressionBombError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Image data is invalid or unsafe",
        ) from exc
    if mime != signature_mime:
        mime = "application/octet-stream"
    if mime not in ALLOWED_IMAGE_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Real file type {mime} is not supported",
        )
    return mime


def _sanitize_filename(filename: str | None) -> str:
    name = Path((filename or "ticket-image").replace("\\", "/")).name
    safe = re.sub(r"[^A-Za-z0-9._-]", "_", name).strip("._")
    return (safe or "ticket-image")[:120]


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
    response: Response,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user),
    tenant: TenantContext = Depends(get_tenant_context),
):
    """Return image attachments for a ticket with temporary download URLs."""
    response.headers["Cache-Control"] = "private, no-store"
    _authorized_ticket(db, ticket_id, tenant.user, tenant.organization_id)
    return [
        _attachment_response(attachment)
        for attachment in get_ticket_attachments(db, ticket_id, tenant.organization_id)
    ]


@router.post(
    "/{ticket_id}/attachments/images",
    response_model=TicketAttachmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_ticket_image(
    ticket_id: int,
    response: Response,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(require_access_level(2)),
    tenant: TenantContext = Depends(get_tenant_context),
):
    """Upload a ticket image to MinIO/S3 and persist its metadata."""
    response.headers["Cache-Control"] = "private, no-store"
    _authorized_ticket(db, ticket_id, current_user, tenant.organization_id)

    content_type = file.content_type or "application/octet-stream"
    if content_type not in ALLOWED_IMAGE_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only JPEG, PNG, and WebP images are supported",
        )

    body = await file.read(settings.max_upload_size_bytes + 1)
    await file.close()
    if not body:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="File is empty"
        )
    if len(body) > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File exceeds the maximum upload size",
        )
    real_content_type = await validate_image_real_type(body)

    filename = _sanitize_filename(file.filename)
    object_key = build_ticket_attachment_key(tenant.organization_id, ticket_id, filename)
    upload_file_object(object_key=object_key, body=body, content_type=real_content_type)
    attachment = create_ticket_attachment(
        db,
        ticket_id=ticket_id,
        organization_id=tenant.organization_id,
        uploader_id=current_user.id,
        object_key=object_key,
        filename=filename,
        content_type=real_content_type,
        size_bytes=len(body),
    )
    return _attachment_response(attachment)
