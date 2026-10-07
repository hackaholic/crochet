"""Search service for telemetry management, retention, and maintenance."""

import logging
import time
from datetime import datetime, timedelta, timezone
from fastapi import BackgroundTasks
from sqlalchemy.orm import Session

from app.models.search import SearchEvent

logger = logging.getLogger("sulocraft.search")

DEFAULT_RETENTION_DAYS: int = 30
PRUNE_INTERVAL_SECONDS: float = 3600.0  # Run opportunistic cleanup at most once per hour

_LAST_PRUNE_TIMESTAMP: float = 0.0


def prune_expired_search_events(
    db: Session, retention_days: int = DEFAULT_RETENTION_DAYS
) -> int:
    """Purge search event telemetry older than the specified retention window.

    According to the Work 009 retention policy, search suggestions only consider
    events within a rolling 30-day window. Events older than 30 days are purged
    to prevent unbounded table growth.

    Returns:
        int: Number of deleted search event records.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)
    try:
        deleted_count = (
            db.query(SearchEvent)
            .filter(SearchEvent.created_at < cutoff)
            .delete(synchronize_session=False)
        )
        db.commit()
        if deleted_count > 0:
            logger.info(
                "Pruned %d expired search event(s) older than %s (retention=%d days).",
                deleted_count,
                cutoff.isoformat(),
                retention_days,
            )
        return deleted_count
    except Exception as exc:
        db.rollback()
        logger.error("Failed to prune expired search events: %s", exc)
        raise


def run_background_prune(retention_days: int = DEFAULT_RETENTION_DAYS) -> None:
    """Run retention pruning in an isolated database session for background tasks."""
    from app.db.session import SessionLocal

    with SessionLocal() as db:
        try:
            prune_expired_search_events(db, retention_days=retention_days)
        except Exception as exc:
            logger.warning("Background search event pruning encountered an error: %s", exc)


def maybe_schedule_opportunistic_pruning(
    background_tasks: BackgroundTasks,
    retention_days: int = DEFAULT_RETENTION_DAYS,
    interval_seconds: float = PRUNE_INTERVAL_SECONDS,
) -> bool:
    """Check if pruning interval has elapsed and schedule background prune.

    Returns:
        bool: True if background prune task was scheduled, False otherwise.
    """
    global _LAST_PRUNE_TIMESTAMP
    now = time.time()
    if now - _LAST_PRUNE_TIMESTAMP >= interval_seconds:
        _LAST_PRUNE_TIMESTAMP = now
        background_tasks.add_task(run_background_prune, retention_days)
        return True
    return False


def reset_prune_timestamp() -> None:
    """Reset last prune timestamp to 0.0 for test isolation."""
    global _LAST_PRUNE_TIMESTAMP
    _LAST_PRUNE_TIMESTAMP = 0.0
