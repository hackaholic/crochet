"""Notification service package."""

from app.services.notification.base import BaseEmailProvider, BaseSmsProvider
from app.services.notification.factory import get_email_provider, get_sms_provider
from app.services.notification.service import (
    NotificationService,
    dispatch_order_placed_background,
    dispatch_order_status_background,
    dispatch_otp_background,
)

__all__ = [
    "BaseEmailProvider",
    "BaseSmsProvider",
    "NotificationService",
    "dispatch_order_placed_background",
    "dispatch_order_status_background",
    "dispatch_otp_background",
    "get_email_provider",
    "get_sms_provider",
]
