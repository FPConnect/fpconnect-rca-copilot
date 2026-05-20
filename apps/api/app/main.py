"""FPConnect RCA Copilot — FastAPI application entry point."""

from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
import structlog
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.routes import (
    analyze,
    auth,
    contracts,
    enterprise,
    machines,
    playbooks,
    tickets,
)
from app.core.config import settings
from app.core.database import Base, engine
from app.core.security import limiter
from app.models import machine, playbook, ticket, user  # noqa: F401

structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ]
)
log = structlog.get_logger()


class LoggingMiddleware(BaseHTTPMiddleware):
    """Emit structured JSON logs for HTTP requests."""

    async def dispatch(self, request: Request, call_next):
        start = datetime.now(timezone.utc)
        response = await call_next(request)
        duration = (datetime.now(timezone.utc) - start).total_seconds()
        log.info(
            "http_request",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            duration=duration,
        )
        return response


from app.api.routes import (
    analyze,
    auth,
    contracts,
    enterprise,
    machines,
    playbooks,
    tickets,
)
from app.core.config import settings
from app.core.database import Base, engine
from app.core.security import limiter
from app.models import machine, playbook, ticket, user  # noqa: F401

structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ]
)
log = structlog.get_logger()


class LoggingMiddleware(BaseHTTPMiddleware):
    """Emit structured JSON logs for HTTP requests."""

    async def dispatch(self, request: Request, call_next):
        start = datetime.now(timezone.utc)
        response = await call_next(request)
        duration = (datetime.now(timezone.utc) - start).total_seconds()
        log.info(
            "http_request",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            duration=duration,
        )
        return response


from app.api.routes import (
    analyze,
    auth,
    contracts,
    enterprise,
    machines,
    playbooks,
    tickets,
)
from app.core.config import settings
from app.core.database import Base, engine
from app.core.security import limiter
from app.models import machine, playbook, ticket, user  # noqa: F401

structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ]
)
log = structlog.get_logger()


class LoggingMiddleware(BaseHTTPMiddleware):
    """Emit structured JSON logs for HTTP requests."""

    async def dispatch(self, request: Request, call_next):
        start = datetime.now(timezone.utc)
        response = await call_next(request)
        duration = (datetime.now(timezone.utc) - start).total_seconds()
        log.info(
            "http_request",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            duration=duration,
        )
        return response

from app.api.routes import analyze, auth, contracts, machines, playbooks, tickets
from app.core.config import settings
from app.core.database import Base, engine
from app.models import machine, playbook, ticket, user  # noqa: F401

# Create database tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FPConnect RCA Copilot API",
    description="RCA Copilot & Availability Engine for Healthcare/MedTech",
    version="1.0.0",
)
app.add_middleware(LoggingMiddleware)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware: explicit allowlist (required when credentials are enabled)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# Routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(tickets.router, prefix="/tickets", tags=["tickets"])
app.include_router(machines.router, prefix="/machines", tags=["machines"])
app.include_router(analyze.router, prefix="/analyze", tags=["clinical-diagnosis"])
app.include_router(playbooks.router, prefix="/playbooks", tags=["playbooks"])
app.include_router(contracts.router, prefix="/contracts", tags=["contracts"])
app.include_router(enterprise.router, prefix="/enterprise", tags=["enterprise"])


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
