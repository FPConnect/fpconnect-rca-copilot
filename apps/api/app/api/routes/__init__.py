"""API route modules."""

from fastapi import APIRouter

from . import auth, intel, tickets  # noqa: F401


api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(tickets.router, prefix="/tickets", tags=["tickets"])
api_router.include_router(intel.router, prefix="/intel", tags=["intel"])

