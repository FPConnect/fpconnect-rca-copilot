"""Redis-backed JSON cache helpers with safe no-cache fallback."""

from __future__ import annotations

import json
from typing import Any, Optional

import redis
from redis.exceptions import RedisError

from app.core.config import settings

_client: redis.Redis | None = None


def get_client() -> redis.Redis:
    """Return a lazily-created Redis client."""
    global _client
    if _client is None:
        _client = redis.Redis.from_url(settings.redis_url, decode_responses=True)
    return _client


def get_cached(key: str) -> Optional[Any]:
    """Read a JSON value from cache, returning None when Redis is unavailable or empty."""
    try:
        value = get_client().get(key)
    except RedisError:
        return None
    return json.loads(value) if value else None


def set_cached(key: str, data: Any, ttl: int = 3600) -> None:
    """Write a JSON value to cache and ignore transient Redis failures."""
    try:
        get_client().setex(key, ttl, json.dumps(data, default=str))
    except RedisError:
        return


def invalidate(key: str) -> None:
    """Delete a cache key and ignore transient Redis failures."""
    try:
        get_client().delete(key)
    except RedisError:
        return
