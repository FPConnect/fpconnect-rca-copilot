"""Object storage helpers for ticket attachments."""

from functools import lru_cache
from uuid import uuid4

import boto3
from botocore.client import Config

from app.core.config import settings


@lru_cache
def get_s3_client():
    """Return a cached S3-compatible client for MinIO or AWS S3."""
    return boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint_url,
        aws_access_key_id=settings.s3_access_key_id,
        aws_secret_access_key=settings.s3_secret_access_key,
        region_name=settings.s3_region,
        config=Config(signature_version="s3v4"),
    )


def ensure_bucket_exists() -> None:
    """Create the attachment bucket when it is missing."""
    client = get_s3_client()
    try:
        client.head_bucket(Bucket=settings.s3_bucket_name)
    except Exception:
        client.create_bucket(Bucket=settings.s3_bucket_name)


def build_ticket_attachment_key(ticket_id: int, filename: str) -> str:
    """Build a collision-resistant object key for a ticket attachment."""
    safe_filename = filename.replace("/", "_").replace("\\", "_") or "attachment"
    return f"tickets/{ticket_id}/images/{uuid4().hex}-{safe_filename}"


def upload_file_object(*, object_key: str, body: bytes, content_type: str) -> str:
    """Upload bytes to object storage and return the object key."""
    ensure_bucket_exists()
    get_s3_client().put_object(
        Bucket=settings.s3_bucket_name,
        Key=object_key,
        Body=body,
        ContentType=content_type,
    )
    return object_key


def create_presigned_get_url(object_key: str) -> str:
    """Create a temporary URL for downloading an attachment."""
    return get_s3_client().generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.s3_bucket_name, "Key": object_key},
        ExpiresIn=settings.s3_presigned_url_expire_seconds,
    )
