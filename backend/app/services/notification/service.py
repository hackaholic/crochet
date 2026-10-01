"""Notification service orchestrating SMS, Email, templates, and database audit logs."""

import logging
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.notification import NotificationLog
from app.models.order import Order
from app.services.notification.factory import get_email_provider, get_sms_provider
from app.services.notification.templates import (
    render_order_confirmation_email,
    render_order_confirmation_sms,
    render_order_status_email,
    render_order_status_sms,
    render_otp_sms,
)

logger = logging.getLogger("sulocraft.notifications")


class NotificationService:
    """Central orchestrator for transactional customer notifications."""

    @staticmethod
    def send_otp(db: Session, phone: str, otp_code: str) -> tuple[bool, str | None]:
        """Dispatch OTP via configured SMS provider and log transaction."""
        sms_provider = get_sms_provider()
        success, err = sms_provider.send_otp(phone, otp_code)

        provider_name = settings.sms_provider or "mock"
        status = "SENT" if success else "FAILED"
        if provider_name.lower() == "mock":
            status = "MOCK"

        body = render_otp_sms(otp_code)
        log_entry = NotificationLog(
            channel="SMS",
            recipient=phone,
            event_type="OTP",
            status=status,
            provider=provider_name,
            subject=None,
            body=body,
            error_message=err,
        )
        try:
            db.add(log_entry)
            db.commit()
        except Exception as e:
            logger.error("Failed to persist OTP notification log: %s", e)
            db.rollback()

        return success, err

    @staticmethod
    def send_order_placed(db: Session, order: Order) -> None:
        """Send order confirmation SMS and Email to the customer."""
        addr = order.shipping_address_json or {}
        phone = addr.get("phone")
        email = addr.get("email")
        if not email and order.user:
            email = order.user.email

        order_data = {
            "orderNumber": order.order_number,
            "totalAmount": order.total_amount,
            "paymentMethod": order.payment_method,
            "shippingAddress": addr,
            "trackingUrl": f"{settings.frontend_url}/account/orders/{order.order_number}",
            "items": [
                {
                    "productName": item.product_name,
                    "variantName": item.variant_name,
                    "quantity": item.quantity,
                    "unitPrice": item.unit_price,
                    "lineTotal": item.line_total,
                }
                for item in order.items
            ],
        }

        # 1. Send SMS if phone available
        if phone:
            sms_body = render_order_confirmation_sms(
                order_number=order.order_number,
                total_amount=order.total_amount,
                tracking_url=order_data["trackingUrl"],
            )
            sms_provider = get_sms_provider()
            success, err = sms_provider.send_sms(phone, sms_body)

            provider_name = settings.sms_provider or "mock"
            status = "SENT" if success else "FAILED"
            if provider_name.lower() == "mock":
                status = "MOCK"

            db.add(
                NotificationLog(
                    channel="SMS",
                    recipient=phone,
                    event_type="ORDER_CONFIRMED",
                    status=status,
                    provider=provider_name,
                    subject=None,
                    body=sms_body,
                    error_message=err,
                )
            )

        # 2. Send Email if email available
        if email:
            html_body, text_body = render_order_confirmation_email(order_data)
            subject = f"Sulocraft - Order Confirmed #{order.order_number}"
            email_provider = get_email_provider()
            success, err = email_provider.send_email(
                to_email=email,
                subject=subject,
                html_content=html_body,
                text_content=text_body,
            )

            provider_name = settings.email_provider or "mock"
            status = "SENT" if success else "FAILED"
            if provider_name.lower() == "mock":
                status = "MOCK"

            db.add(
                NotificationLog(
                    channel="EMAIL",
                    recipient=email,
                    event_type="ORDER_CONFIRMED",
                    status=status,
                    provider=provider_name,
                    subject=subject,
                    body=text_body,
                    error_message=err,
                )
            )

        try:
            db.commit()
        except Exception as e:
            logger.error("Failed to commit order placement notification logs: %s", e)
            db.rollback()

    @staticmethod
    def send_order_status_update(
        db: Session,
        order: Order,
        new_status: str,
        carrier: str | None = None,
        tracking_number: str | None = None,
    ) -> None:
        """Send order status update notification (e.g. SHIPPED, DELIVERED) via SMS and Email."""
        addr = order.shipping_address_json or {}
        phone = addr.get("phone")
        email = addr.get("email")
        if not email and order.user:
            email = order.user.email

        tracking_url = f"{settings.frontend_url}/account/orders/{order.order_number}"
        order_data = {
            "orderNumber": order.order_number,
            "shippingAddress": addr,
            "trackingUrl": tracking_url,
        }

        # 1. Send SMS
        if phone:
            sms_body = render_order_status_sms(
                order_number=order.order_number,
                status=new_status,
                carrier=carrier,
                tracking_number=tracking_number,
                tracking_url=tracking_url,
            )
            sms_provider = get_sms_provider()
            success, err = sms_provider.send_sms(phone, sms_body)

            provider_name = settings.sms_provider or "mock"
            status = "SENT" if success else "FAILED"
            if provider_name.lower() == "mock":
                status = "MOCK"

            db.add(
                NotificationLog(
                    channel="SMS",
                    recipient=phone,
                    event_type="ORDER_STATUS_UPDATE",
                    status=status,
                    provider=provider_name,
                    subject=None,
                    body=sms_body,
                    error_message=err,
                )
            )

        # 2. Send Email
        if email:
            html_body, text_body = render_order_status_email(
                order_data=order_data,
                new_status=new_status,
                carrier=carrier,
                tracking_number=tracking_number,
            )
            status_clean = new_status.replace("_", " ").title()
            subject = f"Sulocraft - Order #{order.order_number} {status_clean}"
            email_provider = get_email_provider()
            success, err = email_provider.send_email(
                to_email=email,
                subject=subject,
                html_content=html_body,
                text_content=text_body,
            )

            provider_name = settings.email_provider or "mock"
            status = "SENT" if success else "FAILED"
            if provider_name.lower() == "mock":
                status = "MOCK"

            db.add(
                NotificationLog(
                    channel="EMAIL",
                    recipient=email,
                    event_type="ORDER_STATUS_UPDATE",
                    status=status,
                    provider=provider_name,
                    subject=subject,
                    body=text_body,
                    error_message=err,
                )
            )

        try:
            db.commit()
        except Exception as e:
            logger.error("Failed to commit order status notification logs: %s", e)
            db.rollback()


# -----------------------------------------------------------------------------
# Background Task Runners (Decoupled execution with independent DB sessions)
# -----------------------------------------------------------------------------

def dispatch_otp_background(phone: str, otp_code: str) -> None:
    """Run OTP notification in FastAPI background task."""
    with SessionLocal() as db:
        NotificationService.send_otp(db, phone, otp_code)


def dispatch_order_placed_background(order_id: int) -> None:
    """Run order confirmation notification in FastAPI background task."""
    with SessionLocal() as db:
        order = db.query(Order).filter(Order.id == order_id).first()
        if order:
            NotificationService.send_order_placed(db, order)


def dispatch_order_status_background(
    order_id: int,
    new_status: str,
    carrier: str | None = None,
    tracking_number: str | None = None,
) -> None:
    """Run order status update notification in FastAPI background task."""
    with SessionLocal() as db:
        order = db.query(Order).filter(Order.id == order_id).first()
        if order:
            NotificationService.send_order_status_update(
                db, order, new_status, carrier=carrier, tracking_number=tracking_number
            )
