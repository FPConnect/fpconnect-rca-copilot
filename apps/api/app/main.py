"""FPConnect RCA Copilot — FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, intel, tickets, agent
from app.api.routes import n8n as n8n_routes
from app.core.database import Base, engine  # noqa: F401 — Base used by Alembic

# Tables are managed by Alembic migrations — do NOT call create_all here.

app = FastAPI(
    title="FPConnect RCA Copilot API",
    description="RCA Copilot & Availability Engine for Healthcare/MedTech",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(tickets.router, prefix="/tickets", tags=["tickets"])
app.include_router(intel.router, prefix="/intel", tags=["intel"])
app.include_router(n8n_routes.router)
app.include_router(agent.router)


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
