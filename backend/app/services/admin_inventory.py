"""Service functions for atomic admin inventory adjustments (Task 1.8.4)."""

from __future__ import annotations

from datetime import datetime, timezone
import logging
import threading

from fastapi import HTTPException, status
import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.models.catalogue import ProductVariant
from app.schemas.admin import AdminInventoryAdjustRequest

logger = logging.getLogger(__name__)

# In-process mutex for serializing concurrent adjustments within the same process (e.g. SQLite test runners)
_inventory_adjust_lock = threading.Lock()


def adjust_variant_inventory_atomic(
    db: Session,
    variant_id: int,
    payload: AdminInventoryAdjustRequest,
) -> ProductVariant:
    """Adjust a variant's inventory level atomically.

    Guarantees:
    1. Rejects requests with neither stock_quantity nor adjustment (400).
    2. Rejects negative stock quantities (400) or adjustments that would result in negative stock (400).
    3. Rejects non-existent variant IDs (404).
    4. Multi-tier concurrency safety:
       - Process-level mutex (_inventory_adjust_lock) for thread safety.
       - Row-level pessimistic locking (with_for_update()) on supported databases.
       - PostgreSQL transaction-level advisory xact lock per variant ID (pg_advisory_xact_lock).
    5. Leaves stock unchanged on validation or transactional failure.
    """
    if payload.stock_quantity is None and payload.adjustment is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide stock_quantity or adjustment",
        )

    if payload.stock_quantity is not None and payload.stock_quantity < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resulting stock quantity cannot be negative",
        )

    with _inventory_adjust_lock:
        # 1. Acquire PostgreSQL advisory transaction lock if running on PostgreSQL
        bind = db.get_bind()
        if bind and bind.dialect.name == "postgresql":
            try:
                db.execute(
                    sa.text("SELECT pg_advisory_xact_lock(hashtext('admin_variant_inventory'), :var_id)"),
                    {"var_id": variant_id},
                )
            except Exception as e:
                logger.debug("PostgreSQL advisory lock note: %s", e)

        # 2. Row-level lock via with_for_update()
        try:
            variant = (
                db.query(ProductVariant)
                .filter(ProductVariant.id == variant_id)
                .with_for_update()
                .first()
            )
            if not variant:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Variant not found",
                )

            if payload.stock_quantity is not None:
                new_quantity = payload.stock_quantity
            else:
                assert payload.adjustment is not None
                new_quantity = variant.stock_quantity + payload.adjustment
                if new_quantity < 0:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Resulting stock quantity cannot be negative",
                    )

            variant.stock_quantity = new_quantity
            variant.updated_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(variant)
            return variant
        except HTTPException:
            db.rollback()
            raise
        except Exception:
            db.rollback()
            logger.exception("Failed to adjust inventory for variant %d", variant_id)
            raise
