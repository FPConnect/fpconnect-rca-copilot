"""Enhanced rate limiting with per-user and per-endpoint strategies."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Callable, Optional

from fastapi import Request, status
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
import structlog

from app.core.config import settings

log = structlog.get_logger()

# Enhanced limiter with configurable strategy
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[
        f"{settings.rate_limit_per_minute if hasattr(settings, 'rate_limit_per_minute') else 100}/minute",
        f"{settings.rate_limit_per_hour if hasattr(settings, 'rate_limit_per_hour') else 1000}/hour",
    ],
    storage_uri=settings.redis_url if settings.app_env != "development" else "memory://",
)


class TieredRateLimiter:
    """Apply different rate limits based on user role or subscription tier."""

    TIER_LIMITS = {
        "free": {"requests_per_minute": 30, "requests_per_hour": 500},
        "basic": {"requests_per_minute": 60, "requests_per_hour": 1000},
        "premium": {"requests_per_minute": 120, "requests_per_hour": 2000},
        "enterprise": {"requests_per_minute": 300, "requests_per_hour": 5000},
    }

    def __init__(self):
        self._request_counts: dict[str, list[datetime]] = defaultdict(list)

    def _cleanup_old_requests(self, key: str, window_seconds: int = 3600):
        """Remove requests older than the time window."""
        cutoff = datetime.now(timezone.utc) - timedelta(seconds=window_seconds)
        self._request_counts[key] = [
            ts for ts in self._request_counts[key] if ts > cutoff
        ]

    def is_allowed(
        self, identifier: str, tier: str = "free", endpoint: str = ""
    ) -> tuple[bool, dict]:
        """Check if request is allowed based on tier limits."""
        limits = self.TIER_LIMITS.get(tier, self.TIER_LIMITS["free"])
        now = datetime.now(timezone.utc)

        # Check per-minute limit
        minute_key = f"{identifier}:{endpoint}:minute"
        self._cleanup_old_requests(minute_key, 60)
        if len(self._request_counts[minute_key]) >= limits["requests_per_minute"]:
            return False, {
                "limit": limits["requests_per_minute"],
                "remaining": 0,
                "reset": int((now + timedelta(seconds=60)).timestamp()),
                "reason": "per_minute_limit",
            }

        # Check per-hour limit
        hour_key = f"{identifier}:{endpoint}:hour"
        self._cleanup_old_requests(hour_key, 3600)
        if len(self._request_counts[hour_key]) >= limits["requests_per_hour"]:
            return False, {
                "limit": limits["requests_per_hour"],
                "remaining": 0,
                "reset": int((now + timedelta(hours=1)).timestamp()),
                "reason": "per_hour_limit",
            }

        # Record the request
        self._request_counts[minute_key].append(now)
        self._request_counts[hour_key].append(now)

        return True, {
            "limit": limits["requests_per_minute"],
            "remaining": limits["requests_per_minute"] - len(self._request_counts[minute_key]),
            "reset": int((now + timedelta(seconds=60)).timestamp()),
        }


def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded) -> dict:
    """Enhanced error response for rate limit exceeded."""
    log.warning(
        "rate_limit_exceeded",
        path=request.url.path,
        method=request.method,
        client_ip=get_remote_address(request),
        detail=str(exc.detail),
    )

    return {
        "error": "rate_limit_exceeded",
        "detail": "Too many requests. Please try again later.",
        "retry_after": getattr(exc, "retry_after", 60),
        "documentation_url": "/docs/rate-limiting",
    }


def get_user_tier_from_role(role: str) -> str:
    """Map user role to rate limit tier."""
    tier_mapping = {
        "admin": "enterprise",
        "manager": "premium",
        "technician": "basic",
        "user": "free",
    }
    return tier_mapping.get(role, "free")


# Export enhanced handler
enhanced_rate_limit_handler = custom_rate_limit_handler
