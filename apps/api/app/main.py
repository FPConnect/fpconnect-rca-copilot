"""FPConnect RCA Copilot — FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, intelligence, machines, n8n, notifications, tickets
from app.core.config import settings
from app.core.database import Base, engine
from app.models import machine, ticket, user  # noqa: F401

# Create database tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FPConnect RCA Copilot API",
    description="RCA Copilot & Availability Engine for Healthcare/MedTech",
    version="1.0.0",
)

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
app.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
app.include_router(n8n.router)
app.include_router(intelligence.router, prefix="/intelligence", tags=["intelligence"])


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
