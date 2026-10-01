"""User, UserIdentity, UserSession, and Magic Link token models conforming to docs/api-auth.md."""

from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class User(Base):
    """Unified user model across all identity providers (Google, Facebook, Email)."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=True)
    email = Column(String(255), unique=True, index=True, nullable=True)
    phone = Column(String(20), unique=True, index=True, nullable=True)  # delivery contact only
    role = Column(String(20), default="CUSTOMER", nullable=False, index=True)  # CUSTOMER, ADMIN
    status = Column(String(20), default="ACTIVE", index=True)  # ACTIVE, SUSPENDED
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_login_at = Column(DateTime, nullable=True)

    identities = relationship("UserIdentity", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    addresses = relationship("Address", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user")
    wishlist = relationship("Wishlist", back_populates="user", uselist=False, cascade="all, delete-orphan")


class UserIdentity(Base):
    """Authentication identity link (provider + provider_subject).

    Supported providers: google, facebook, email.
    Phone OTP is removed from V1 — phone column on User is delivery data only.
    """

    __tablename__ = "user_identities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    provider = Column(String(50), nullable=False)  # google, facebook, email
    provider_subject = Column(String(255), nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="identities")


class UserSession(Base):
    """Server-side session management for authenticated browser sessions."""

    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    session_token = Column(String(64), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, nullable=False)
    is_revoked = Column(Boolean, default=False)

    user = relationship("User", back_populates="sessions")


class OtpVerification(Base):
    """Historical phone OTP challenge records.

    DEPRECATED: Phone OTP authentication is removed from V1.
    This table is preserved strictly for backwards migration compatibility and will be
    dropped in a future database schema cleanup. Phone is retained on User and Order
    strictly as delivery contact data.
    """

    __tablename__ = "otp_verifications"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(20), index=True, nullable=False)
    otp_code = Column(String(6), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, nullable=False)
    attempts = Column(Integer, default=0)
    is_used = Column(Boolean, default=False)


class MagicLinkToken(Base):
    """Email magic link tokens for passwordless sign-in (V1 auth contract).

    Token is stored as SHA-256 hash; the raw token is NEVER persisted.
    Single-use, expires in 15 minutes.
    """

    __tablename__ = "magic_link_tokens"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False, index=True)  # normalized lowercase
    token_hash = Column(String(64), nullable=False, unique=True, index=True)  # SHA-256 hex
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, nullable=False)
    is_used = Column(Boolean, default=False, nullable=False)
    used_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("ix_magic_link_tokens_email_unused", "email", "is_used"),
    )
