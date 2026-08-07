"""Intel/Radar ingestion & processing service.

MVP scope:
- Read a YAML file listing RSS feeds.
- Fetch entries, normalize, deduplicate.
- Classify by simple keyword heuristics.
- Generate bilingual summaries (PT/EN) with a safe fallback.

This intentionally avoids scraping or login automation for third-party platforms.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import feedparser
import yaml
from dateutil.parser import parse as dtparse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.intel_item import IntelItem


TOPIC_KEYWORDS: dict[str, list[str]] = {
    "downtime": ["downtime", "mttr", "availability", "uptime", "sla"],
    "predictive_maintenance": ["predictive", "pdm", "anomaly", "condition monitoring"],
    "health_interop": ["hl7", "dicom", "fhir", "lis", "his"],
    "cybersecurity": ["ransomware", "cve", "breach", "cisa", "phishing", "vulnerability"],
    "ai_agents": ["llm", "agent", "rag", "embeddings", "copilot"],
}


def _hash_text(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


def _classify_topic(text: str) -> Optional[str]:
    t = (text or "").lower()
    for topic, kws in TOPIC_KEYWORDS.items():
        if any(k in t for k in kws):
            return topic
    return None


def _summarize_heuristic(text: str, max_len: int = 320) -> str:
    if not text:
        return ""
    clean = " ".join(text.strip().split())
    return clean[:max_len] + ("…" if len(clean) > max_len else "")


def _translate_fallback(text: str, target_lang: str) -> str:
    """MVP: safe fallback without external calls.

    If you later add a translation provider, swap this implementation.
    """
    return text


@dataclass
class Source:
    name: str
    type: str
    url: str
    tags: list[str]


def load_sources(path_str: str) -> list[Source]:
    path = Path(path_str)
    if not path.exists():
        # Resolve relative to the API working directory
        path = Path.cwd() / path_str
    data: dict[str, Any] = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    out: list[Source] = []
    for s in data.get("sources", []):
        out.append(
            Source(
                name=str(s.get("name", "Unknown")),
                type=str(s.get("type", "rss")),
                url=str(s.get("url", "")),
                tags=list(s.get("tags", [])),
            )
        )
    return [s for s in out if s.url]


def fetch_rss(source: Source, limit: int = 50) -> list[dict[str, Any]]:
    feed = feedparser.parse(source.url)
    items: list[dict[str, Any]] = []
    for e in feed.entries[:limit]:
        title = getattr(e, "title", "") or ""
        link = getattr(e, "link", "") or ""
        summary = getattr(e, "summary", "") or getattr(e, "description", "") or ""
        published = None
        if getattr(e, "published", None):
            try:
                published = dtparse(e.published)
            except Exception:
                published = None

        content_text = f"{title}\n{summary}".strip()
        items.append(
            {
                "source": source.name,
                "url": link,
                "title": title,
                "published_at": published,
                "content_text": content_text,
                "content_hash": _hash_text(link + "||" + content_text),
                "topic": _classify_topic(content_text),
            }
        )
    return items


def ingest_once(db: Session, limit_per_source: int | None = None) -> dict[str, int]:
    sources = load_sources(settings.intel_sources_path)
    inserted = 0
    skipped = 0
    lim = limit_per_source or settings.intel_default_limit

    for src in sources:
        if src.type.lower() != "rss":
            continue
        for it in fetch_rss(src, limit=lim):
            exists = (
                db.query(IntelItem)
                .filter(IntelItem.content_hash == it["content_hash"])
                .first()
            )
            if exists:
                skipped += 1
                continue

            summary_base = _summarize_heuristic(it.get("content_text") or "")
            summary_pt = summary_base
            summary_en = _translate_fallback(summary_base, target_lang="en")

            db.add(
                IntelItem(
                    source=it["source"],
                    url=it["url"],
                    title=it["title"],
                    published_at=it.get("published_at"),
                    fetched_at=datetime.utcnow(),
                    content_text=it.get("content_text"),
                    content_hash=it["content_hash"],
                    topic=it.get("topic"),
                    summary_pt=summary_pt,
                    summary_en=summary_en,
                    processed=True,
                )
            )
            inserted += 1

    db.commit()
    return {"inserted": inserted, "skipped": skipped, "sources": len(sources)}


def list_topics(db: Session) -> list[str]:
    rows = db.query(IntelItem.topic).distinct().all()
    topics = sorted({r[0] for r in rows if r[0]})
    return topics
