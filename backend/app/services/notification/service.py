"""Transactional email and notification service orchestrating SMS, Email, templates, and database audit logs."""

import logging
from typing import Any
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.notification import NotificationLog
from app.models.order import Order
from app.models.payment import Payment
from app.services.notification.factory import get_email_provider, get_sms_provider
from app.services.notification.templates import (
    render_magic_link_email,
    render_order_confirmation_email,
    render_order_confirmation_sms,
    render_order_delivery_email,
    render_order_shipping_email,
    render_order_status_email,
    render_order_status_sms,
    render_payment_confirmation_email,
    render_refund_notification_email,
)

logger = logging.getLogger("sulocraft.notifications")


def _extract_order_email(order: Order) -> str | None:
    """Extract customer email from order snapshot, user relation, or shipping address."""
    if order.customer_email:
        return order.customer_email
    addr = order.shipping_address_json or {}
    email = addr.get("email")
    if not email and order.user:
        email = order.user.email
    return email


def _build_order_data(order: Order) -> dict:
    """Build standardized dictionary payload for order templates."""
    addr = order.shipping_address_json or {}
    return {
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


def _is_email_already_sent(db: Session, recipient: str, event_type: str, order_number: str) -> bool:
    """Check if an email for this recipient, event type, and order has already been sent/mocked."""
    existing = (
        db.query(NotificationLog)
        .filter(
            NotificationLog.recipient == recipient,
            NotificationLog.event_type == event_type,
            NotificationLog.status.in_(["SENT", "MOCK"]),
            NotificationLog.subject.like(f"%{order_number}%"),
        )
        .first()
    )
    return existing is not None


class EmailService:
    """Canonical transactional email service for Sulocraft.

    All outbound transactional email must go through this service rather than
    calling the Resend or SMTP provider directly.
    """

    @staticmethod
    def send_magic_link(
        db: Session,
        to_email: str,
        magic_link: str,
        expires_minutes: int = 15,
    ) -> tuple[bool, str | None]:
        """Send a single-use magic login link via email.

        The raw token / link is strictly redacted from audit logs.
        """
        html_body, text_body = render_magic_link_email(to_email, magic_link, expires_minutes)
        subject = "Sign in to Sulocraft"
        email_provider = get_email_provider()
        success, err = email_provider.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_body,
            text_content=text_body,
            from_email=settings.email_from_orders,
        )

        provider_name = settings.email_provider or "mock"
        status = "SENT" if success else "FAILED"
        if provider_name.lower() == "mock":
            status = "MOCK"

        log_entry = NotificationLog(
            channel="EMAIL",
            recipient=to_email,
            event_type="MAGIC_LINK",
            status=status,
            provider=provider_name,
            subject=subject,
            body="[magic link dispatched — URL redacted]",
            error_message=err,
        )
        try:
            db.add(log_entry)
            db.commit()
        except Exception as e:
            logger.error("Failed to persist magic link notification log: %s", e)
            db.rollback()

        return success, err

    @staticmethod
    def send_order_confirmation(db: Session, order: Order) -> tuple[bool, str | None]:
        """Send order confirmation email to the customer with idempotency check."""
        email = _extract_order_email(order)
        if not email:
            logger.warning("Cannot send order confirmation: no email found for order %s", order.order_number)
            return False, "Recipient email missing"

        if _is_email_already_sent(db, email, "ORDER_CONFIRMED", order.order_number):
            logger.info("Idempotent skip: ORDER_CONFIRMED email already sent to %s for order %s", email, order.order_number)
            return True, None

        order_data = _build_order_data(order)
        html_body, text_body = render_order_confirmation_email(order_data)
        subject = f"Sulocraft - Order Confirmed #{order.order_number}"

        email_provider = get_email_provider()
        success, err = email_provider.send_email(
            to_email=email,
            subject=subject,
            html_content=html_body,
            text_content=text_body,
            from_email=settings.email_from_orders,
        )

        provider_name = settings.email_provider or "mock"
        status = "SENT" if success else "FAILED"
        if provider_name.lower() == "mock":
            status = "MOCK"

        log_entry = NotificationLog(
            channel="EMAIL",
            recipient=email,
            event_type="ORDER_CONFIRMED",
            status=status,
            provider=provider_name,
            subject=subject,
            body=text_body,
            error_message=err,
        )
        try:
            db.add(log_entry)
            db.commit()
        except Exception as e:
            logger.error("Failed to persist order confirmation log: %s", e)
            db.rollback()

        return success, err

    @staticmethod
    def send_payment_confirmation(
        db: Session,
        order: Order,
        payment: Any = None,
    ) -> tuple[bool, str | None]:
        """Send payment received confirmation email with idempotency check."""
        email = _extract_order_email(order)
        if not email:
            logger.warning("Cannot send payment confirmation: no email for order %s", order.order_number)
            return False, "Recipient email missing"

        if _is_email_already_sent(db, email, "ORDER_PAYMENT_CONFIRMED", order.order_number):
            logger.info("Idempotent skip: ORDER_PAYMENT_CONFIRMED already sent to %s for order %s", email, order.order_number)
            return True, None

        order_data = _build_order_data(order)
        payment_data = {
            "provider": getattr(payment, "provider", "ONLINE") if payment else "ONLINE",
            "provider_payment_id": getattr(payment, "provider_payment_id", "Confirmed") if payment else "Confirmed",
        }

        html_body, text_body = render_payment_confirmation_email(order_data, payment_data)
        subject = f"Sulocraft - Payment Confirmed #{order.order_number}"

        email_provider = get_email_provider()
        success, err = email_provider.send_email(
            to_email=email,
            subject=subject,
            html_content=html_body,
            text_content=text_body,
            from_email=settings.email_from_orders,
        )

        provider_name = settings.email_provider or "mock"
        status = "SENT" if success else "FAILED"
        if provider_name.lower() == "mock":
            status = "MOCK"

        log_entry = NotificationLog(
            channel="EMAIL",
            recipient=email,
            event_type="ORDER_PAYMENT_CONFIRMED",
            status=status,
            provider=provider_name,
            subject=subject,
            body=text_body,
            error_message=err,
        )
        try:
            db.add(log_entry)
            db.commit()
        except Exception as e:
            logger.error("Failed to persist payment confirmation log: %s", e)
            db.rollback()

        return success, err

    @staticmethod
    def send_shipping_update(
        db: Session,
        order: Order,
        carrier: str | None = None,
        tracking_number: str | None = None,
        tracking_url: str | None = None,
        event_type: str = "ORDER_SHIPPED",
    ) -> tuple[bool, str | None]:
        """Send order dispatched / tracking update email with idempotency check."""
        email = _extract_order_email(order)
        if not email:
            logger.warning("Cannot send shipping update: no email for order %s", order.order_number)
            return False, "Recipient email missing"

        if _is_email_already_sent(db, email, event_type, order.order_number):
            logger.info("Idempotent skip: %s already sent to %s for order %s", event_type, email, order.order_number)
            return True, None

        order_data = _build_order_data(order)
        resolved_carrier = carrier or order.courier_name or "Sulocraft Express"
        resolved_tracking = tracking_number or order.tracking_number or "SLC-TRACK"

        html_body, text_body = render_order_shipping_email(
            order_data=order_data,
            carrier=resolved_carrier,
            tracking_number=resolved_tracking,
            tracking_url=tracking_url,
        )
        subject = f"Sulocraft - Order #{order.order_number} Has Shipped!"

        email_provider = get_email_provider()
        success, err = email_provider.send_email(
            to_email=email,
            subject=subject,
            html_content=html_body,
            text_content=text_body,
            from_email=settings.email_from_orders,
        )

        provider_name = settings.email_provider or "mock"
        status = "SENT" if success else "FAILED"
        if provider_name.lower() == "mock":
            status = "MOCK"

        log_entry = NotificationLog(
            channel="EMAIL",
            recipient=email,
            event_type=event_type,
            status=status,
            provider=provider_name,
            subject=subject,
            body=text_body,
            error_message=err,
        )
        try:
            db.add(log_entry)
            db.commit()
        except Exception as e:
            logger.error("Failed to persist shipping update log: %s", e)
            db.rollback()

        return success, err

    @staticmethod
    def send_delivery_update(
        db: Session,
        order: Order,
        event_type: str = "ORDER_DELIVERED",
    ) -> tuple[bool, str | None]:
        """Send order delivered update email with idempotency check."""
        email = _extract_order_email(order)
        if not email:
            logger.warning("Cannot send delivery update: no email for order %s", order.order_number)
            return False, "Recipient email missing"

        if _is_email_already_sent(db, email, event_type, order.order_number):
            logger.info("Idempotent skip: %s already sent to %s for order %s", event_type, email, order.order_number)
            return True, None

        order_data = _build_order_data(order)
        html_body, text_body = render_order_delivery_email(order_data)
        subject = f"Sulocraft - Order #{order.order_number} Delivered!"

        email_provider = get_email_provider()
        success, err = email_provider.send_email(
            to_email=email,
            subject=subject,
            html_content=html_body,
            text_content=text_body,
            from_email=settings.email_from_orders,
        )

        provider_name = settings.email_provider or "mock"
        status = "SENT" if success else "FAILED"
        if provider_name.lower() == "mock":
            status = "MOCK"

        log_entry = NotificationLog(
            channel="EMAIL",
            recipient=email,
            event_type=event_type,
            status=status,
            provider=provider_name,
            subject=subject,
            body=text_body,
            error_message=err,
        )
        try:
            db.add(log_entry)
            db.commit()
        except Exception as e:
            logger.error("Failed to persist delivery update log: %s", e)
            db.rollback()

        return success, err

    @staticmethod
    def send_refund_notification(
        db: Session,
        order: Order,
        refund_amount: float | None = None,
        reason: str | None = None,
        event_type: str = "ORDER_REFUND",
    ) -> tuple[bool, str | None]:
        """Send refund notification email to customer with idempotency check."""
        email = _extract_order_email(order)
        if not email:
            logger.warning("Cannot send refund notification: no email for order %s", order.order_number)
            return False, "Recipient email missing"

        if _is_email_already_sent(db, email, event_type, order.order_number):
            logger.info("Idempotent skip: %s already sent to %s for order %s", event_type, email, order.order_number)
            return True, None

        order_data = _build_order_data(order)
        amount = refund_amount if refund_amount is not None else order.total_amount

        html_body, text_body = render_refund_notification_email(
            order_data=order_data,
            refund_amount=amount,
            reason=reason,
        )
        subject = f"Sulocraft - Refund Issued #{order.order_number}"

        email_provider = get_email_provider()
        success, err = email_provider.send_email(
            to_email=email,
            subject=subject,
            html_content=html_body,
            text_content=text_body,
            from_email=settings.email_from_support,
        )

        provider_name = settings.email_provider or "mock"
        status = "SENT" if success else "FAILED"
        if provider_name.lower() == "mock":
            status = "MOCK"

        log_entry = NotificationLog(
            channel="EMAIL",
            recipient=email,
            event_type=event_type,
            status=status,
            provider=provider_name,
            subject=subject,
            body=text_body,
            error_message=err,
        )
        try:
            db.add(log_entry)
            db.commit()
        except Exception as e:
            logger.error("Failed to persist refund notification log: %s", e)
            db.rollback()

        return success, err


class NotificationService:
    """Central orchestrator for transactional customer notifications combining SMS and Email."""

    @staticmethod
    def send_order_placed(db: Session, order: Order) -> None:
        """Send order confirmation SMS and Email to the customer."""
        addr = order.shipping_address_json or {}
        phone = addr.get("phone")

        # 1. Send SMS if phone available
        if phone:
            tracking_url = f"{settings.frontend_url}/account/orders/{order.order_number}"
            sms_body = render_order_confirmation_sms(
                order_number=order.order_number,
                total_amount=order.total_amount,
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
                    event_type="ORDER_CONFIRMED",
                    status=status,
                    provider=provider_name,
                    subject=None,
                    body=sms_body,
                    error_message=err,
                )
            )
            try:
                db.commit()
            except Exception as e:
                logger.error("Failed to commit order placement SMS log: %s", e)
                db.rollback()

        # 2. Email delivery via EmailService
        EmailService.send_order_confirmation(db, order)

    @staticmethod
    def send_order_status_update(
        db: Session,
        order: Order,
        new_status: str,
        carrier: str | None = None,
        tracking_number: str | None = None,
    ) -> None:
        """Send order status update notification via SMS and Email."""
        addr = order.shipping_address_json or {}
        phone = addr.get("phone")
        tracking_url = f"{settings.frontend_url}/account/orders/{order.order_number}"

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
            try:
                db.commit()
            except Exception as e:
                logger.error("Failed to commit status update SMS log: %s", e)
                db.rollback()

        # 2. Send Email via specialized EmailService methods
        status_upper = new_status.upper()
        if status_upper == "SHIPPED":
            EmailService.send_shipping_update(
                db,
                order,
                carrier=carrier,
                tracking_number=tracking_number,
                tracking_url=tracking_url,
                event_type="ORDER_STATUS_UPDATE",
            )
        elif status_upper == "DELIVERED":
            EmailService.send_delivery_update(db, order, event_type="ORDER_STATUS_UPDATE")
        elif status_upper == "CANCELLED":
            if order.payment_status == "PAID":
                EmailService.send_refund_notification(
                    db, order, reason="Order cancelled", event_type="ORDER_STATUS_UPDATE"
                )
            else:
                email = _extract_order_email(order)
                if email:
                    order_data = _build_order_data(order)
                    html_body, text_body = render_order_status_email(order_data, new_status)
                    subject = f"Sulocraft - Order #{order.order_number} Cancelled"
                    email_provider = get_email_provider()
                    email_provider.send_email(
                        to_email=email,
                        subject=subject,
                        html_content=html_body,
                        text_content=text_body,
                        from_email=settings.email_from_orders,
                    )
                    db.add(
                        NotificationLog(
                            channel="EMAIL",
                            recipient=email,
                            event_type="ORDER_STATUS_UPDATE",
                            status="SENT" if settings.email_provider != "mock" else "MOCK",
                            provider=settings.email_provider or "mock",
                            subject=subject,
                            body=text_body,
                        )
                    )
                    try:
                        db.commit()
                    except Exception as e:
                        logger.error("Failed to commit cancellation email log: %s", e)
                        db.rollback()
        else:
            email = _extract_order_email(order)
            if email:
                order_data = _build_order_data(order)
                html_body, text_body = render_order_status_email(
                    order_data=order_data,
                    new_status=new_status,
                    carrier=carrier,
                    tracking_number=tracking_number,
                )
                status_clean = new_status.replace("_", " ").title()
                subject = f"Sulocraft - Order #{order.order_number} {status_clean}"
                email_provider = get_email_provider()
                email_provider.send_email(
                    to_email=email,
                    subject=subject,
                    html_content=html_body,
                    text_content=text_body,
                    from_email=settings.email_from_orders,
                )

    @staticmethod
    def send_magic_link(
        db: Session,
        to_email: str,
        magic_link: str,
        expires_minutes: int = 15,
    ) -> tuple[bool, str | None]:
        """Delegate magic link delivery to EmailService."""
        return EmailService.send_magic_link(db, to_email, magic_link, expires_minutes)


# -----------------------------------------------------------------------------
# Background Task Runners (Decoupled execution with independent DB sessions)
# -----------------------------------------------------------------------------

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


def dispatch_magic_link_background(to_email: str, magic_link: str, expires_minutes: int = 15) -> None:
    """Send magic link email in FastAPI background task."""
    with SessionLocal() as db:
        EmailService.send_magic_link(db, to_email, magic_link, expires_minutes)


def dispatch_payment_confirmed_background(order_id: int, payment_id: int | None = None) -> None:
    """Send payment confirmation email in FastAPI background task."""
    with SessionLocal() as db:
        order = db.query(Order).filter(Order.id == order_id).first()
        payment = db.query(Payment).filter(Payment.id == payment_id).first() if payment_id else None
        if order:
            EmailService.send_payment_confirmation(db, order, payment)


def dispatch_delivery_background(order_id: int) -> None:
    """Send delivery confirmation email in FastAPI background task."""
    with SessionLocal() as db:
        order = db.query(Order).filter(Order.id == order_id).first()
        if order:
            EmailService.send_delivery_update(db, order)


def dispatch_refund_background(
    order_id: int,
    refund_amount: float | None = None,
    reason: str | None = None,
) -> None:
    """Send refund notification email in FastAPI background task."""
    with SessionLocal() as db:
        order = db.query(Order).filter(Order.id == order_id).first()
        if order:
            EmailService.send_refund_notification(db, order, refund_amount=refund_amount, reason=reason)
