"""Request/Response caching middleware for improved performance."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

from app.core.cache import get_cached, set_cached

log = structlog.get_logger()


class CacheControlMiddleware(BaseHTTPMiddleware):
    """Add cache control headers to responses based on endpoint type."""

    # Endpoints that should never be cached
    NO_CACHE_PATHS = {"/auth", "/enterprise", "/contracts"}

    # Default cache TTL for different endpoint types
    CACHE_TTLS = {
        "/tickets/": 300,  # 5 minutes
        "/machines/": 600,  # 10 minutes
        "/playbooks/": 3600,  # 1 hour
        "/notifications/": 60,  # 1 minute
    }

    async def dispatch(self, request: Request, call_next) -> Response:
        # Only cache GET requests
        if request.method != "GET":
            return await call_next(request)

        # Check if path should skip caching
        path = request.url.path
        if any(path.startswith(no_cache) for no_cache in self.NO_CACHE_PATHS):
            response = await call_next(request)
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            return response

        # Determine cache TTL based on path
        cache_ttl = 0
        for prefix, ttl in self.CACHE_TTLS.items():
            if path.startswith(prefix):
                cache_ttl = ttl
                break

        if cache_ttl == 0:
            # No caching configured for this path
            return await call_next(request)

        # Generate cache key from path and query params
        cache_key = self._generate_cache_key(request)

        # Try to get cached response
        cached_response = get_cached(cache_key)
        if cached_response:
            log.debug("cache_hit", path=path, cache_key=cache_key)
            response = Response(
                content=json.dumps(cached_response["body"]),
                status_code=cached_response["status_code"],
                media_type=cached_response.get("media_type", "application/json"),
            )
            response.headers["X-Cache"] = "HIT"
            response.headers["Cache-Control"] = f"public, max-age={cache_ttl}"
            response.headers["Age"] = str(
                int((datetime.now(timezone.utc) - cached_response["timestamp"]).total_seconds())
            )
            return response

        # Call the actual endpoint
        response = await call_next(request)

        # Cache successful responses
        if response.status_code == 200:
            body_bytes = b""
            async for chunk in response.body_iterator:
                body_bytes += chunk

            # Decode body for caching
            try:
                body_str = body_bytes.decode("utf-8")
                body_data = json.loads(body_str) if body_str else None
            except (json.JSONDecodeError, UnicodeDecodeError):
                body_data = None

            if body_data is not None:
                set_cached(
                    cache_key,
                    {
                        "body": body_data,
                        "status_code": response.status_code,
                        "media_type": response.media_type,
                        "timestamp": datetime.now(timezone.utc),
                    },
                    ttl=cache_ttl,
                )
                log.debug("cache_set", path=path, cache_key=cache_key, ttl=cache_ttl)

            # Rebuild response with body
            response = Response(
                content=body_bytes,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )

        response.headers["X-Cache"] = "MISS"
        response.headers["Cache-Control"] = f"public, max-age={cache_ttl}"

        return response

    def _generate_cache_key(self, request: Request) -> str:
        """Generate a unique cache key from request properties."""
        key_data = {
            "path": request.url.path,
            "query": str(request.url.query),
            "accept": request.headers.get("Accept", ""),
        }
        key_string = json.dumps(key_data, sort_keys=True)
        digest = hashlib.sha256(key_string.encode("utf-8")).hexdigest()
        return f"http_cache:{digest}"


class ResponseCompressionMiddleware(BaseHTTPMiddleware):
    """Compress large JSON responses using gzip."""

    MIN_SIZE_FOR_COMPRESSION = 1024  # Only compress responses > 1KB

    async def dispatch(self, request: Request, call_next) -> Response:
        import gzip

        response = await call_next(request)

        # Only compress JSON responses
        if response.media_type != "application/json":
            return response

        # Collect response body
        body_bytes = b""
        async for chunk in response.body_iterator:
            body_bytes += chunk

        # Only compress if large enough
        if len(body_bytes) < self.MIN_SIZE_FOR_COMPRESSION:
            return response

        # Check if client accepts gzip
        accept_encoding = request.headers.get("Accept-Encoding", "")
        if "gzip" not in accept_encoding:
            return response

        # Compress the response
        compressed_body = gzip.compress(body_bytes)

        # Only use compression if it actually reduces size
        if len(compressed_body) >= len(body_bytes):
            return response

        # Return compressed response
        new_response = Response(
            content=compressed_body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type,
        )
        new_response.headers["Content-Encoding"] = "gzip"
        new_response.headers["Vary"] = "Accept-Encoding"
        new_response.headers["Content-Length"] = str(len(compressed_body))

        return new_response
