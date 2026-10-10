"""Service module for secure guest order tracking token management and verification."""

import hashlib
import logging
import os
import secrets
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.order import GuestOrderAccessToken, Order
from app.services.notification.service import EmailService

logger = logging.getLogger("sulocraft.guest_tracking")

DEFAULT_GUEST_TOKEN_EXPIRY_DAYS = 14
_IP_TRACKING_RATE_LIMIT_STORE: dict[str, list[float]] = {}
IP_TRACKING_RATE_LIMIT_WINDOW = 60.0
IP_TRACKING_MAX_REQUESTS_PER_WINDOW = 5


def hash_token(raw_token: str) -> str:
    """Compute SHA-256 hex digest of raw token."""
    return hashlib.sha256(raw_token.strip().encode("utf-8")).hexdigest()


def create_guest_order_token(
    db: Session,
    order_id: int,
    expires_days: int = DEFAULT_GUEST_TOKEN_EXPIRY_DAYS,
) -> tuple[str, GuestOrderAccessToken]:
    """Generate and persist a cryptographically random, order-scoped guest access token.

    The raw token is NEVER persisted in the database; only its SHA-256 digest is stored.
    Returns:
        tuple[str, GuestOrderAccessToken]: (raw_token, token_model)
    """
    raw_token = secrets.token_urlsafe(32)
    token_digest = hash_token(raw_token)
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(days=expires_days)

    token_record = GuestOrderAccessToken(
        order_id=order_id,
        token_hash=token_digest,
        created_at=now,
        expires_at=expires_at,
        is_revoked=False,
    )
    db.add(token_record)
    db.commit()
    db.refresh(token_record)
    return raw_token, token_record


def validate_guest_order_token(
    db: Session,
    order_id: int,
    raw_token: str | None,
) -> bool:
    """Validate that the provided guest token is valid, active, unexpired, and matches the given order."""
    if not raw_token or not raw_token.strip():
        return False

    token_digest = hash_token(raw_token)
    now = datetime.now(timezone.utc)

    record = (
        db.query(GuestOrderAccessToken)
        .filter(
            GuestOrderAccessToken.token_hash == token_digest,
            GuestOrderAccessToken.order_id == order_id,
            GuestOrderAccessToken.is_revoked.is_(False),
        )
        .first()
    )

    if not record:
        return False

    expires_at = record.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at <= now:
        return False

    return True


def revoke_guest_order_tokens(db: Session, order_id: int) -> None:
    """Explicitly revoke all active guest access tokens for a specific order."""
    now = datetime.now(timezone.utc)
    db.query(GuestOrderAccessToken).filter(
        GuestOrderAccessToken.order_id == order_id,
        GuestOrderAccessToken.is_revoked.is_(False),
    ).update(
        {"is_revoked": True, "revoked_at": now},
        synchronize_session=False,
    )
    db.commit()


def check_rate_limit(client_ip: str | None) -> bool:
    """Return True if request is allowed, False if client IP has exceeded the limit."""
    if not client_ip or client_ip == "unknown":
        return True

    is_test = os.getenv("TESTING", "false").lower() == "true"
    if is_test:
        return True

    import time
    current_time = time.time()
    ip_timestamps = _IP_TRACKING_RATE_LIMIT_STORE.get(client_ip, [])
    ip_timestamps = [t for t in ip_timestamps if current_time - t < IP_TRACKING_RATE_LIMIT_WINDOW]

    if len(ip_timestamps) >= IP_TRACKING_MAX_REQUESTS_PER_WINDOW:
        return False

    ip_timestamps.append(current_time)
    _IP_TRACKING_RATE_LIMIT_STORE[client_ip] = ip_timestamps
    return True
