"""SQLAlchemy ORM models.

Import models here so metadata is populated when the application starts.
"""

from app.models.ticket import Ticket  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.intel_item import IntelItem  # noqa: F401
