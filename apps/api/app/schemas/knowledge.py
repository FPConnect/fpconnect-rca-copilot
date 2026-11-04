"""Validation and public contracts for governed MedTech service knowledge."""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

Category = Literal[
    "operations", "equipment", "connectivity", "software",
    "quality", "documentation", "other"
]
Visibility = Literal["private", "workspace", "global"]
ReviewStatus = Literal[
    "draft", "in_review", "approved", "rejected", "archived", "legacy_quarantine"
]


def normalize_tags(tags: list[str]) -> list[str]:
    """Keep bounded, easily filterable tags without personal data or URLs."""
    import re

    if len(tags) > 12:
        raise ValueError("At most 12 tags per article")
    values: list[str] = []
    for tag in tags:
        item = tag.strip().lower()
        if not re.fullmatch(r"[\w-]{2,32}", item, flags=re.UNICODE):
            raise ValueError("Tags must contain 2-32 word characters or hyphens")
        if item not in values:
            values.append(item)
    return values


class KnowledgeWorkspaceCreate(BaseModel):
    slug: str = Field(min_length=3, max_length=64, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    name: str = Field(min_length=3, max_length=160)


class KnowledgeMemberCreate(BaseModel):
    user_id: int = Field(gt=0)
    membership_role: Literal["member", "manager"] = "member"


class KnowledgeWorkspaceOut(BaseModel):
    id: int
    slug: str
    name: str
    membership_role: str | None = None


class KnowledgeArticleCreate(BaseModel):
    title: str = Field(min_length=5, max_length=220)
    content: str = Field(min_length=15, max_length=20000)
    category: Category
    tags: list[str] = Field(default_factory=list, max_length=12)
    visibility: Visibility = "private"
    workspace_id: int | None = Field(default=None, gt=0)
    equipment_family: str | None = Field(default=None, max_length=100)
    manufacturer: str | None = Field(default=None, max_length=100)
    model_code: str | None = Field(default=None, max_length=100)
    failure_code: str | None = Field(default=None, max_length=100)
    source_ref: str | None = Field(default=None, max_length=240)

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, value: list[str]) -> list[str]:
        return normalize_tags(value)


class KnowledgeArticleUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=5, max_length=220)
    content: str | None = Field(default=None, min_length=15, max_length=20000)
    category: Category | None = None
    tags: list[str] | None = Field(default=None, max_length=12)
    visibility: Visibility | None = None
    workspace_id: int | None = Field(default=None, gt=0)
    equipment_family: str | None = Field(default=None, max_length=100)
    manufacturer: str | None = Field(default=None, max_length=100)
    model_code: str | None = Field(default=None, max_length=100)
    failure_code: str | None = Field(default=None, max_length=100)
    source_ref: str | None = Field(default=None, max_length=240)

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, value: list[str] | None) -> list[str] | None:
        return None if value is None else normalize_tags(value)


class KnowledgeArticleOut(BaseModel):
    id: int
    title: str
    content: str
    category: str
    tags: list[str]
    visibility: str
    review_status: str
    owner_id: int | None
    workspace_id: int | None
    equipment_family: str | None
    manufacturer: str | None
    model_code: str | None
    failure_code: str | None
    source_ref: str | None
    reviewed_by: int | None
    reviewed_at: datetime | None
    created_at: datetime | None
    updated_at: datetime | None
    version: int


class KnowledgeLegacySummary(BaseModel):
    id: int
    title: str
    tags: str | None
    created_at: datetime | None
    # No content / embedding in legacy listing.


class KnowledgeLegacyClassify(BaseModel):
    owner_id: int = Field(gt=0)
    category: Category
    workspace_id: int | None = Field(default=None, gt=0)


class KnowledgeReviewAction(BaseModel):
    decision: Literal["approve", "reject"]
    # A human reviewer must attest that applicable sharing permissions,
    # confidentiality and evidentiary limits were independently checked.
    sharing_authorized: Literal[True]
