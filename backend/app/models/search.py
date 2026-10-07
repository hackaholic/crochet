"""Search telemetry models for anonymous aggregate search frequency tracking."""

from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Integer, String

from app.db.base import Base


class SearchEvent(Base):
    """Anonymous search query telemetry event for aggregate trend discovery.

    Zero-PII compliance: Does NOT store user IDs, IP addresses, session tokens,
    or browser fingerprints. Stores only normalized query string and timestamp.
    """

    __tablename__ = "search_events"

    id = Column(Integer, primary_key=True, index=True)
    query = Column(String(255), nullable=False, index=True)
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        index=True,
        nullable=False,
    )
