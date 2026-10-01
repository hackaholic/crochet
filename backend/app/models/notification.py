"""Notification audit log model for tracking outbound SMS and Email messages."""

from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Integer, String, Text

from app.db.base import Base


class NotificationLog(Base):
    """Audit log for all outgoing customer notifications (SMS and Email)."""

    __tablename__ = "notification_logs"

    id = Column(Integer, primary_key=True, index=True)
    channel = Column(String(20), nullable=False, index=True)  # SMS, EMAIL
    recipient = Column(String(255), nullable=False, index=True)  # phone number or email
    event_type = Column(String(50), nullable=False, index=True)  # OTP, ORDER_CONFIRMED, ORDER_STATUS_UPDATE, ORDER_CANCELLED
    status = Column(String(20), nullable=False, default="SENT", index=True)  # SENT, FAILED, MOCK
    provider = Column(String(50), nullable=False)  # mock, fast2sms, twilio, smtp, resend
    subject = Column(String(255), nullable=True)  # Email subject line
    body = Column(Text, nullable=False)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
