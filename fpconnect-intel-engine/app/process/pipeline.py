import os
from sqlalchemy.orm import Session

from app.db.models import ContentItem
from app.process.agentic import run_agentic_workflow
from app.process.llm import summarize_bilingual, summarize_simple

TOPIC_KEYWORDS = {
    'downtime': ['downtime', 'mttr', 'availability', 'uptime', 'sla'],
    'predictive_maintenance': ['predictive', 'condition monitoring', 'anomaly', 'pdm'],
    'health_interop': ['hl7', 'dicom', 'fhir', 'lis', 'his'],
    'cybersecurity': ['ransomware', 'cve', 'breach', 'cisa', 'phishing'],
    'ai_agents': ['llm', 'agent', 'rag', 'embeddings', 'copilot'],
}


def classify_topic(text: str) -> str | None:
    t = (text or '').lower()
    for topic, kws in TOPIC_KEYWORDS.items():
        if any(k in t for k in kws):
            return topic
    return None


def upsert_items(
    db: Session,
    raw_items: list[dict],
    openai_api_key: str | None = None,
    bilingual: bool = True,
) -> dict:
    """Insert new content items. Dedup by content_hash.

    - If `openai_api_key` is provided (or OPENAI_API_KEY env is set),
      the pipeline will try to create bilingual summaries.
    - If not, it falls back to simple extractive summaries.
    """

    if openai_api_key:
        os.environ['OPENAI_API_KEY'] = openai_api_key

    inserted = 0
    skipped = 0

    for raw in raw_items:
        existing = db.query(ContentItem).filter(ContentItem.content_hash == raw['content_hash']).first()
        if existing:
            skipped += 1
            continue

        text = raw.get('content_text') or ''
        topic = classify_topic(text)
        triage_severity = None
        rca_text = None

        # Agentic workflow (best effort): enriches context and generates triage + RCA.
        try:
            agentic = run_agentic_workflow(raw.get('url', ''), text)
            text = agentic.get('enriched_text') or text
            triage = agentic.get('triage') or {}
            triage_topic = triage.get('topic')
            triage_severity = triage.get('severity')
            if triage_topic and str(triage_topic).strip().lower() not in {'general', 'unknown'}:
                topic = triage_topic
            rca_text = agentic.get('rca')
        except Exception:
            # Keep ingestion resilient if agentic path fails.
            pass

        if bilingual:
            summary_en, summary_pt = summarize_bilingual(text)
        else:
            summary_en = summarize_simple(text, limit=320)
            summary_pt = summary_en

        item = ContentItem(
            source=raw['source'],
            url=raw['url'],
            title=raw['title'],
            published_at=raw.get('published_at'),
            content_text=text,
            content_hash=raw['content_hash'],
            topic=topic,
            severity=triage_severity,
            summary_en=summary_en,
            summary_pt=summary_pt,
            rca=rca_text,
            tags=','.join(raw.get('tags') or []),
            processed=True,
        )
        db.add(item)
        inserted += 1

    db.commit()
    return {'inserted': inserted, 'skipped': skipped}
