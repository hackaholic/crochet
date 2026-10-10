"""Service functions for admin tag discovery, creation, and product association validation."""

from __future__ import annotations

import logging
import threading
from typing import Sequence

from fastapi import HTTPException, status
import sqlalchemy as sa
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.catalogue import Tag

logger = logging.getLogger(__name__)

# Process-level mutex for concurrent in-process requests
_tag_creation_lock = threading.Lock()


def list_admin_tags(db: Session) -> Sequence[Tag]:
    """Retrieve all persisted tags ordered by name and id."""
    return db.query(Tag).order_by(Tag.name.asc(), Tag.id.asc()).all()


def get_or_create_admin_tag(db: Session, name: str) -> tuple[Tag, bool]:
    """Retrieve an existing tag (case-insensitive) or create a new one safely.

    Provides multi-layered concurrency serialization:
    1. Process-level thread lock (_tag_creation_lock).
    2. Database-level transaction advisory lock on PostgreSQL (pg_advisory_xact_lock).
    3. Database functional unique index (uq_tags_name_lower).
    4. Savepoint IntegrityError recovery returning canonical existing tag.

    Returns:
        tuple[Tag, bool]: (tag, is_newly_created)
    """
    clean_name = name.strip()
    if not clean_name:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Tag name cannot be empty or whitespace only",
        )
    if len(clean_name) > 50:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Tag name cannot exceed 50 characters",
        )

    # 1. Quick read check
    existing = db.query(Tag).filter(func.lower(Tag.name) == func.lower(clean_name)).first()
    if existing:
        return existing, False

    with _tag_creation_lock:
        # Re-check inside lock
        existing = db.query(Tag).filter(func.lower(Tag.name) == func.lower(clean_name)).first()
        if existing:
            return existing, False

        # Acquire PostgreSQL advisory transaction lock if running on PostgreSQL
        bind = db.get_bind()
        if bind and bind.dialect.name == "postgresql":
            try:
                db.execute(sa.text("SELECT pg_advisory_xact_lock(hashtext('admin_tag_creation'))"))
            except Exception:
                pass

        new_tag = Tag(name=clean_name)
        try:
            with db.begin_nested():
                db.add(new_tag)
                db.flush()
            db.commit()
            db.refresh(new_tag)
            return new_tag, True
        except IntegrityError:
            db.rollback()
            # Concurrent insert resolved by database unique index: fetch existing tag
            existing = db.query(Tag).filter(func.lower(Tag.name) == func.lower(clean_name)).first()
            if existing:
                return existing, False
            logger.exception("Failed to create or fetch tag with name '%s'", clean_name)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not save tag",
            )


def validate_and_get_tags_by_ids(db: Session, tag_ids: Sequence[int] | None) -> list[Tag]:
    """Validate that all provided tag IDs exist in the database and return their Tag instances.

    Raises:
        HTTPException(400): If any of the requested tag IDs do not exist.
    """
    if not tag_ids:
        return []

    unique_requested_ids = set(tag_ids)
    tags = db.query(Tag).filter(Tag.id.in_(unique_requested_ids)).all()
    found_ids = {t.id for t in tags}
    missing_ids = sorted(list(unique_requested_ids - found_ids))

    if missing_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid tagIds: {missing_ids}",
        )

    return tags
