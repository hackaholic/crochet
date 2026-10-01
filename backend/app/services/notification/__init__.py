"""Notification service package."""

from app.services.notification.base import BaseEmailProvider, BaseSmsProvider
from app.services.notification.factory import get_email_provider, get_sms_provider
from app.services.notification.service import (
    EmailService,
    NotificationService,
    dispatch_delivery_background,
    dispatch_magic_link_background,
    dispatch_order_placed_background,
    dispatch_order_status_background,
    dispatch_payment_confirmed_background,
    dispatch_refund_background,
)

__all__ = [
    "BaseEmailProvider",
    "BaseSmsProvider",
    "EmailService",
    "NotificationService",
    "dispatch_delivery_background",
    "dispatch_magic_link_background",
    "dispatch_order_placed_background",
    "dispatch_order_status_background",
    "dispatch_payment_confirmed_background",
    "dispatch_refund_background",
    "get_email_provider",
    "get_sms_provider",
]
