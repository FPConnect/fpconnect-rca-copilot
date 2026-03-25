import hashlib
import feedparser
from dateutil.parser import parse as dtparse


def _hash(text: str) -> str:
    return hashlib.sha256((text or '').encode('utf-8')).hexdigest()


def fetch_rss(url: str, source_name: str, tags: list[str] | None = None):
    feed = feedparser.parse(url)
    items = []
    for e in (feed.entries or [])[:50]:
        title = getattr(e, 'title', '') or ''
        link = getattr(e, 'link', '') or ''
        summary = getattr(e, 'summary', '') or getattr(e, 'description', '') or ''
        published_at = None
        if getattr(e, 'published', None):
            try:
                published_at = dtparse(e.published)
            except Exception:
                published_at = None

        content_text = (title + '\n' + summary).strip()
        content_hash = _hash(link + '||' + content_text)

        items.append({
            'source': source_name,
            'url': link,
            'title': title,
            'published_at': published_at,
            'content_text': content_text,
            'content_hash': content_hash,
            'tags': tags or [],
        })

    return items
