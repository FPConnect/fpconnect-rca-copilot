"""FPConnect RCA Copilot — FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, tickets
from app.core.database import Base, engine

# Create database tables on startup
Base.metadata.create_all(bind=engine)

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


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
