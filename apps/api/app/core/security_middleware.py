"""Enhanced security middleware for production hardening."""

from __future__ import annotations

import secrets
import time
from typing import Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
import structlog

from app.core.config import settings

log = structlog.get_logger()


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add essential security headers to all responses."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)

        # Prevent clickjacking attacks
        response.headers["X-Frame-Options"] = "DENY"

        # Enable XSS filter in browsers
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Referrer policy for privacy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Content Security Policy (adjust based on your needs)
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' https://api.openai.com; "
            "frame-ancestors 'none';"
        )
        response.headers["Content-Security-Policy"] = csp_policy

        # Permissions Policy (formerly Feature Policy)
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=(), payment=()"
        )

        # HSTS (only in production)
        if settings.app_env == "production":
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )

        return response


class RequestTimingMiddleware(BaseHTTPMiddleware):
    """Track and log request timing for performance monitoring."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.perf_counter()

        # Add unique request ID for tracing
        request_id = request.headers.get("X-Request-ID", secrets.token_hex(8))
        request.state.request_id = request_id

        response = await call_next(request)

        # Calculate duration
        duration_ms = (time.perf_counter() - start_time) * 1000

        # Add timing header
        response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"
        response.headers["X-Request-ID"] = request_id

        # Log slow requests
        if duration_ms > 1000:  # More than 1 second
            log.warning(
                "slow_request",
                request_id=request_id,
                path=request.url.path,
                method=request.method,
                duration_ms=round(duration_ms, 2),
            )
        else:
            log.debug(
                "request_timing",
                request_id=request_id,
                path=request.url.path,
                duration_ms=round(duration_ms, 2),
            )

        return response


class IPWhitelistMiddleware(BaseHTTPMiddleware):
    """Restrict access to sensitive endpoints by IP address."""

    # Endpoints that require IP whitelisting
    PROTECTED_PATHS = {"/enterprise", "/contracts"}

    def __init__(self, app, allowed_ips: Optional[list[str]] = None):
        super().__init__(app)
        self.allowed_ips = allowed_ips or []

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Check if the path requires IP restriction
        if any(request.url.path.startswith(path) for path in self.PROTECTED_PATHS):
            if not self.allowed_ips:
                # No IPs configured, allow all (development mode)
                pass
            else:
                client_ip = self._get_client_ip(request)
                if client_ip not in self.allowed_ips:
                    log.warning(
                        "ip_blocked",
                        path=request.url.path,
                        client_ip=client_ip,
                        allowed_ips=self.allowed_ips,
                    )
                    return Response(
                        content='{"error": "Access denied: IP not whitelisted"}',
                        status_code=403,
                        media_type="application/json",
                    )

        return await call_next(request)

    @staticmethod
    def _get_client_ip(request: Request) -> str:
        """Extract client IP from request, considering proxies."""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"


class AuditLogMiddleware(BaseHTTPMiddleware):
    """Log all requests for audit and compliance purposes."""

    SENSITIVE_PATHS = {"/auth/login", "/auth/register", "/auth/me"}

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Skip logging for health checks
        if request.url.path in ["/health", "/docs", "/openapi.json"]:
            return await call_next(request)

        # Determine if this is a sensitive operation
        is_sensitive = any(
            request.url.path.startswith(path) for path in self.SENSITIVE_PATHS
        )

        # Log the request (anonymize sensitive data)
        log_info = {
            "method": request.method,
            "path": request.url.path,
            "timestamp": time.time(),
            "has_auth": "Authorization" in request.headers,
        }

        if not is_sensitive:
            log_info["client_ip"] = request.client.host if request.client else "unknown"

        log.info("audit_request", **log_info)

        response = await call_next(request)

        # Log response status
        log.info(
            "audit_response",
            path=request.url.path,
            status_code=response.status_code,
            method=request.method,
        )

        return response
