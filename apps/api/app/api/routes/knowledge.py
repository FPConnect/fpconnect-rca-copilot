"""Governed knowledge articles, organizations, and review lifecycle.

Every read applies authorization before category/tag/text filtering.
No client-provided user/workspace ID can grant access to an article.
"""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, func, literal, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import AuthenticatedUser, get_current_user, require_access_level
from app.core.database import get_db
from app.crud.user import get_user_by_id
from app.models.knowledge import KnowledgeAudit, KnowledgeMembership, KnowledgeWorkspace
from app.models.ticket import KBArticle
from app.schemas.knowledge import (
    Category, KnowledgeArticleCreate, KnowledgeArticleOut, KnowledgeArticleUpdate,
    KnowledgeLegacyClassify, KnowledgeLegacySummary, KnowledgeMemberCreate,
    KnowledgeReviewAction, KnowledgeWorkspaceCreate, KnowledgeWorkspaceOut,
    ReviewStatus, Visibility,
)

router = APIRouter()

CATEGORIES = [
    "operations", "equipment", "connectivity", "software",
    "quality", "documentation", "other",
]
STATUSES = ["draft", "in_review", "approved", "rejected", "archived"]


def _workspaces_subquery(user_id: int):
    return select(KnowledgeMembership.workspace_id).where(
        KnowledgeMembership.user_id == user_id
    )


def _is_member(db: Session, workspace_id: int, user_id: int) -> bool:
    return db.query(KnowledgeMembership.id).filter(
        KnowledgeMembership.workspace_id == workspace_id,
        KnowledgeMembership.user_id == user_id,
    ).first() is not None


def _visible_articles(db: Session, actor: AuthenticatedUser):
    """Only own or explicitly authorized, approved shared KB content.

    A removed member cannot retain access to workspace articles just because
    they originally authored an article. Quarantined records never appear here.
    """
    member_ids = _workspaces_subquery(actor.id)
    own_private = and_(
        KBArticle.visibility == "private",
        KBArticle.owner_id == actor.id,
    )
    workspace_visible = and_(
        KBArticle.visibility == "workspace",
        KBArticle.workspace_id.in_(member_ids),
        or_(
            KBArticle.review_status == "approved",
            KBArticle.owner_id == actor.id,
        ),
    )
    global_visible = and_(
        KBArticle.visibility == "global",
        or_(
            KBArticle.review_status == "approved",
            KBArticle.owner_id == actor.id,
        ),
    )
    return db.query(KBArticle).filter(
        KBArticle.review_status != "legacy_quarantine",
        or_(own_private, workspace_visible, global_visible),
    )


def _get_visible(db: Session, actor: AuthenticatedUser, article_id: int) -> KBArticle:
    result = _visible_articles(db, actor).filter(KBArticle.id == article_id).first()
    if result is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return result


def _serialize(article: KBArticle) -> KnowledgeArticleOut:
    return KnowledgeArticleOut(
        id=article.id,
        title=article.title,
        content=article.content,
        category=article.category,
        tags=[tag for tag in (article.tags or "").split(",") if tag],
        visibility=article.visibility,
        review_status=article.review_status,
        owner_id=article.owner_id,
        workspace_id=article.workspace_id,
        equipment_family=article.equipment_family,
        manufacturer=article.manufacturer,
        model_code=article.model_code,
        failure_code=article.failure_code,
        source_ref=article.source_ref,
        reviewed_by=article.reviewed_by,
        reviewed_at=article.reviewed_at,
        created_at=article.created_at,
        updated_at=article.updated_at,
        version=article.version or 1,
    )


def _audit(db: Session, article: KBArticle, actor_id: int, event: str):
    db.add(KnowledgeAudit(
        article_id=article.id, actor_id=actor_id, event_type=event,
        version=article.version,
    ))


def _validate_scope(db: Session, user_id: int, visibility: str, workspace_id: int | None):
    if visibility == "workspace":
        if workspace_id is None or not _is_member(db, workspace_id, user_id):
            raise HTTPException(
                status_code=403, detail="An active workspace membership is required"
            )
    elif workspace_id is not None:
        raise HTTPException(
            status_code=422, detail="Only workspace-scoped articles may set workspace_id"
        )


@router.get("/filters")
def available_filters(
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(get_current_user),
):
    workspaces = db.query(KnowledgeWorkspace).join(
        KnowledgeMembership,
        KnowledgeMembership.workspace_id == KnowledgeWorkspace.id,
    ).filter(KnowledgeMembership.user_id == user.id).order_by(
        KnowledgeWorkspace.name
    ).all()
    return {
        "categories": CATEGORIES,
        "visibilities": ["private", "workspace", "global"],
        "review_statuses": STATUSES,
        "workspaces": [{"id": w.id, "name": w.name, "slug": w.slug} for w in workspaces],
    }


@router.get("/workspaces", response_model=list[KnowledgeWorkspaceOut])
def my_workspaces(
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(get_current_user),
):
    rows = db.query(KnowledgeWorkspace, KnowledgeMembership).join(
        KnowledgeMembership,
        KnowledgeMembership.workspace_id == KnowledgeWorkspace.id,
    ).filter(KnowledgeMembership.user_id == user.id).order_by(
        KnowledgeWorkspace.name
    ).all()
    return [
        KnowledgeWorkspaceOut(
            id=workspace.id, name=workspace.name, slug=workspace.slug,
            membership_role=membership.membership_role,
        )
        for workspace, membership in rows
    ]


@router.post("/workspaces", response_model=KnowledgeWorkspaceOut, status_code=201)
def create_workspace(
    payload: KnowledgeWorkspaceCreate,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_access_level(4)),
):
    space = KnowledgeWorkspace(
        slug=payload.slug, name=payload.name, created_by=user.id,
    )
    try:
        db.add(space)
        db.flush()
        db.add(KnowledgeMembership(
            workspace_id=space.id, user_id=user.id,
            membership_role="manager", created_by=user.id,
        ))
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Workspace already exists") from exc
    db.refresh(space)
    return KnowledgeWorkspaceOut(
        id=space.id, slug=space.slug, name=space.name, membership_role="manager"
    )


@router.post("/workspaces/{workspace_id}/members", status_code=201)
def add_member(
    workspace_id: int,
    payload: KnowledgeMemberCreate,
    db: Session = Depends(get_db),
    admin: AuthenticatedUser = Depends(require_access_level(4)),
):
    if not db.get(KnowledgeWorkspace, workspace_id):
        raise HTTPException(status_code=404, detail="Workspace not found")
    account = get_user_by_id(db, payload.user_id)
    if account is None or not account.is_active:
        raise HTTPException(status_code=404, detail="Active user not found")
    membership = KnowledgeMembership(
        workspace_id=workspace_id, user_id=payload.user_id,
        membership_role=payload.membership_role, created_by=admin.id,
    )
    try:
        db.add(membership)
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Membership already exists") from exc
    return {"workspace_id": workspace_id, "user_id": payload.user_id,
            "membership_role": payload.membership_role}


@router.get("/workspaces/{workspace_id}/members")
def list_members(
    workspace_id: int,
    db: Session = Depends(get_db),
    admin: AuthenticatedUser = Depends(require_access_level(4)),
):
    if not db.get(KnowledgeWorkspace, workspace_id):
        raise HTTPException(status_code=404, detail="Workspace not found")
    rows = db.query(KnowledgeMembership).filter(
        KnowledgeMembership.workspace_id == workspace_id,
    ).order_by(KnowledgeMembership.user_id).all()
    return [{"user_id": m.user_id, "membership_role": m.membership_role} for m in rows]


@router.delete("/workspaces/{workspace_id}/members/{user_id}", status_code=204)
def remove_member(
    workspace_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    admin: AuthenticatedUser = Depends(require_access_level(4)),
):
    membership = db.query(KnowledgeMembership).filter(
        KnowledgeMembership.workspace_id == workspace_id,
        KnowledgeMembership.user_id == user_id,
    ).first()
    if not membership:
        raise HTTPException(status_code=404, detail="Membership not found")
    if membership.membership_role == "manager":
        managers = db.query(KnowledgeMembership).filter(
            KnowledgeMembership.workspace_id == workspace_id,
            KnowledgeMembership.membership_role == "manager",
        ).count()
        if managers <= 1:
            raise HTTPException(status_code=409, detail="Cannot remove last workspace manager")
    db.delete(membership)
    db.commit()


@router.get("/articles", response_model=list[KnowledgeArticleOut])
def list_articles(
    q: str | None = Query(default=None, max_length=200),
    category: Category | None = None,
    workspace_id: int | None = Query(default=None, gt=0),
    visibility: Visibility | None = None,
    review_status: ReviewStatus | None = None,
    manufacturer: str | None = Query(default=None, max_length=100),
    equipment_family: str | None = Query(default=None, max_length=100),
    failure_code: str | None = Query(default=None, max_length=100),
    tag: str | None = Query(default=None, max_length=32),
    limit: int = Query(default=20, ge=1, le=50),
    offset: int = Query(default=0, ge=0, le=100000),
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(get_current_user),
):
    query = _visible_articles(db, user)
    if category is not None:
        query = query.filter(KBArticle.category == category)
    if workspace_id is not None:
        query = query.filter(KBArticle.workspace_id == workspace_id)
    if visibility is not None:
        query = query.filter(KBArticle.visibility == visibility)
    if review_status is not None:
        query = query.filter(KBArticle.review_status == review_status)
    if manufacturer:
        query = query.filter(KBArticle.manufacturer.ilike(_contains(manufacturer)))
    if equipment_family:
        query = query.filter(KBArticle.equipment_family.ilike(_contains(equipment_family)))
    if failure_code:
        query = query.filter(KBArticle.failure_code.ilike(_contains(failure_code)))
    if q:
        needle = _contains(q)
        query = query.filter(or_(
            KBArticle.title.ilike(needle), KBArticle.content.ilike(needle),
            KBArticle.tags.ilike(needle),
        ))
    if tag:
        from app.schemas.knowledge import normalize_tags
        try:
            token = normalize_tags([tag])[0]
        except (ValueError, IndexError) as exc:
            raise HTTPException(status_code=422, detail="Invalid tag") from exc
        # Comma-boundary search, rather than substring matches.
        query = query.filter(
            (literal(",") + func.coalesce(KBArticle.tags, "") + literal(",")).like(
                f"%,{token},%"
            )
        )
    return [
        _serialize(article)
        for article in query.order_by(KBArticle.id.desc()).offset(offset).limit(limit).all()
    ]


def _contains(value: str) -> str:
    # Escape LIKE metacharacters, so client search text is never a wildcard.
    return "%" + value.strip().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"


@router.get("/articles/{article_id}", response_model=KnowledgeArticleOut)
def get_article(
    article_id: int,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(get_current_user),
):
    return _serialize(_get_visible(db, user, article_id))


@router.post("/articles", response_model=KnowledgeArticleOut, status_code=201)
def create_article(
    payload: KnowledgeArticleCreate,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_access_level(2)),
):
    _validate_scope(db, user.id, payload.visibility, payload.workspace_id)
    data = payload.model_dump()
    data["tags"] = ",".join(payload.tags)
    article = KBArticle(
        **data,
        owner_id=user.id,
        review_status="draft",
        version=1,
        embedding=None,
    )
    db.add(article)
    db.flush()
    _audit(db, article, user.id, "created")
    db.commit()
    db.refresh(article)
    return _serialize(article)


@router.patch("/articles/{article_id}", response_model=KnowledgeArticleOut)
def edit_article(
    article_id: int,
    payload: KnowledgeArticleUpdate,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_access_level(2)),
):
    article = _get_visible(db, user, article_id)
    if article.owner_id != user.id or article.review_status == "archived":
        raise HTTPException(status_code=403, detail="Only the article owner can edit a non-archived article")
    data = payload.model_dump(exclude_unset=True)
    if not data:
        return _serialize(article)
    for key in ("title", "content", "category", "visibility"):
        if key in data and data[key] is None:
            raise HTTPException(status_code=422, detail=f"{key} may not be null")
    new_scope = data.get("visibility", article.visibility)
    new_workspace = data.get("workspace_id", article.workspace_id)
    _validate_scope(db, user.id, new_scope, new_workspace)
    if "tags" in data:
        data["tags"] = ",".join(data["tags"] or [])
    for key, value in data.items():
        setattr(article, key, value)
    # A material change invalidates the previous approval and vector.
    article.review_status = "draft"
    article.reviewed_by = None
    article.reviewed_at = None
    article.embedding = None
    article.updated_at = datetime.now(timezone.utc)
    article.version += 1
    _audit(db, article, user.id, "revised")
    db.commit()
    db.refresh(article)
    return _serialize(article)


@router.post("/articles/{article_id}/submit", response_model=KnowledgeArticleOut)
def submit_article(
    article_id: int,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_access_level(2)),
):
    article = _get_visible(db, user, article_id)
    if article.owner_id != user.id or article.review_status not in ("draft", "rejected"):
        raise HTTPException(status_code=409, detail="Only a draft or rejected article can be submitted")
    _validate_scope(db, user.id, article.visibility, article.workspace_id)
    article.review_status = "in_review"
    article.updated_at = datetime.now(timezone.utc)
    _audit(db, article, user.id, "submitted")
    db.commit()
    db.refresh(article)
    return _serialize(article)


@router.get("/review-queue", response_model=list[KnowledgeArticleOut])
def review_queue(
    db: Session = Depends(get_db),
    admin: AuthenticatedUser = Depends(require_access_level(4)),
):
    return [_serialize(article) for article in db.query(KBArticle).filter(
        KBArticle.review_status == "in_review"
    ).order_by(KBArticle.id).limit(100).all()]


@router.post("/articles/{article_id}/review", response_model=KnowledgeArticleOut)
def review_article(
    article_id: int,
    payload: KnowledgeReviewAction,
    db: Session = Depends(get_db),
    reviewer: AuthenticatedUser = Depends(require_access_level(4)),
):
    article = db.get(KBArticle, article_id)
    if not article or article.review_status != "in_review":
        raise HTTPException(status_code=404, detail="Pending article not found")
    if article.owner_id == reviewer.id:
        raise HTTPException(status_code=403, detail="Independent reviewer required")
    if article.visibility == "workspace":
        # An explicit workspace manager must review workspace content.
        manager = db.query(KnowledgeMembership.id).filter(
            KnowledgeMembership.workspace_id == article.workspace_id,
            KnowledgeMembership.user_id == reviewer.id,
            KnowledgeMembership.membership_role == "manager",
        ).first()
        if manager is None:
            raise HTTPException(status_code=403, detail="Workspace manager review required")
    if payload.decision == "approve":
        article.review_status = "approved"
    else:
        article.review_status = "rejected"
    article.reviewed_by = reviewer.id
    article.reviewed_at = datetime.now(timezone.utc)
    article.updated_at = article.reviewed_at
    _audit(db, article, reviewer.id, article.review_status)
    db.commit()
    db.refresh(article)
    return _serialize(article)


@router.post("/articles/{article_id}/archive", response_model=KnowledgeArticleOut)
def archive_article(
    article_id: int,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_access_level(2)),
):
    article = _get_visible(db, user, article_id)
    if article.owner_id != user.id and user.access_level < 4:
        raise HTTPException(status_code=403, detail="Not allowed to archive article")
    article.review_status = "archived"
    article.updated_at = datetime.now(timezone.utc)
    _audit(db, article, user.id, "archived")
    db.commit()
    db.refresh(article)
    return _serialize(article)


@router.get("/legacy", response_model=list[KnowledgeLegacySummary])
def legacy_inventory(
    db: Session = Depends(get_db),
    admin: AuthenticatedUser = Depends(require_access_level(4)),
    limit: int = Query(default=30, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    # Metadata only. No body, tag, patient identifiers, vector or contents.
    records = db.query(KBArticle).filter(
        KBArticle.review_status == "legacy_quarantine",
    ).order_by(KBArticle.id).offset(offset).limit(limit).all()
    return [
        KnowledgeLegacySummary(id=record.id, title=record.title,
                               tags=None, created_at=record.created_at)
        for record in records
    ]


@router.post("/legacy/{article_id}/classify", response_model=KnowledgeArticleOut)
def classify_legacy(
    article_id: int,
    payload: KnowledgeLegacyClassify,
    db: Session = Depends(get_db),
    admin: AuthenticatedUser = Depends(require_access_level(4)),
):
    article = db.get(KBArticle, article_id)
    if not article or article.review_status != "legacy_quarantine":
        raise HTTPException(status_code=404, detail="Quarantined article not found")
    owner = get_user_by_id(db, payload.owner_id)
    if owner is None or not owner.is_active:
        raise HTTPException(status_code=404, detail="Active intended owner not found")
    scope = "workspace" if payload.workspace_id else "private"
    _validate_scope(db, owner.id, scope, payload.workspace_id)
    # Never auto-approve or publish imported content; require the ordinary
    # owner submission and independent review cycle.
    article.owner_id = owner.id
    article.workspace_id = payload.workspace_id
    article.visibility = scope
    article.category = payload.category
    article.review_status = "draft"
    article.reviewed_by = None
    article.reviewed_at = None
    article.embedding = None
    article.updated_at = datetime.now(timezone.utc)
    article.version += 1
    _audit(db, article, admin.id, "legacy_classified")
    db.commit()
    db.refresh(article)
    return _serialize(article)
