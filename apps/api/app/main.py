"""FPConnect RCA Copilot — FastAPI application entry point."""

from datetime import datetime, timezone
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
import structlog
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.routes import analyze, auth, contracts, enterprise, machines, notifications, playbooks, tickets
from app.core.config import settings
from app.core.database import Base, SessionLocal, engine
from app.core.security import limiter
from app.core.test_accounts import reset_test_accounts
from app.models import machine, playbook, ticket, user  # noqa: F401
from app.core.rate_limiter import enhanced_rate_limit_handler
from app.core.middleware import CacheControlMiddleware, ResponseCompressionMiddleware
from app.core.security_middleware import (
    SecurityHeadersMiddleware,
    RequestTimingMiddleware,
    AuditLogMiddleware,
)
from app.services.metrics import collect_periodic_metrics, metrics, track_request

structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ]
)
log = structlog.get_logger()


class LoggingMiddleware(BaseHTTPMiddleware):
    """Emit structured JSON logs for HTTP requests with enhanced tracking."""

    async def dispatch(self, request: Request, call_next):
        start = datetime.now(timezone.utc)
        response = await call_next(request)
        duration = (datetime.now(timezone.utc) - start).total_seconds()
        
        log.info(
            "http_request",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            duration_ms=round(duration * 1000, 2),
        )
        
        # Track metrics
        track_request(response.status_code, duration * 1000)
        
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle events."""
    # Startup
    log.info("application_starting", version="1.0.0", env=settings.app_env)
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    # Reset test accounts in development
    if settings.app_env == "development":
        with SessionLocal() as seed_db:
            reset_test_accounts(seed_db)
    
    # Start background metrics collection
    metrics_task = asyncio.create_task(collect_periodic_metrics())
    
    yield
    
    # Shutdown
    log.info("application_shutting_down")
    metrics_task.cancel()
    try:
        await metrics_task
    except asyncio.CancelledError:
        pass


# Initialize app with lifespan
app = FastAPI(
    title="FPConnect RCA Copilot API",
    description="RCA Copilot & Availability Engine for Healthcare/MedTech - Enhanced with advanced monitoring, security, and predictive capabilities",
    version="1.1.0",
    lifespan=lifespan,
)

# Update rate limit handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, enhanced_rate_limit_handler)

# Core middleware (order matters - outermost first)
app.add_middleware(LoggingMiddleware)
app.add_middleware(RequestTimingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(AuditLogMiddleware)
app.add_middleware(CacheControlMiddleware)
app.add_middleware(ResponseCompressionMiddleware)

# CORS middleware: explicit allowlist (required when credentials are enabled)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)

# Routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(tickets.router, prefix="/tickets", tags=["tickets"])
app.include_router(machines.router, prefix="/machines", tags=["machines"])
app.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
app.include_router(analyze.router, prefix="/analyze", tags=["clinical-diagnosis"])
app.include_router(playbooks.router, prefix="/playbooks", tags=["playbooks"])
app.include_router(contracts.router, prefix="/contracts", tags=["contracts"])
app.include_router(enterprise.router, prefix="/enterprise", tags=["enterprise"])


@app.get("/health")
def health_check():
    """Enhanced health check with system metrics."""
    from app.services.metrics import get_system_health
    
    health = get_system_health()
    return {
        "status": "ok" if health["status"] in ["healthy", "warning"] else "degraded",
        "system_status": health["status"],
        "uptime_seconds": health.get("application", {}).get("uptime_seconds", 0),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/metrics")
def get_metrics():
    """Get application metrics for monitoring dashboards."""
    from app.services.metrics import get_api_metrics, get_system_health
    
    return {
        "application": get_api_metrics(),
        "system": get_system_health(),
        "collector": metrics.get_all_metrics(),
    }


@app.get("/ready")
def readiness_check():
    """Readiness probe for Kubernetes/load balancer."""
    return {"status": "ready"}
