"""Comprehensive tests for EmailService, multi-sender identities, idempotency, and startup validation."""

from datetime import datetime, timezone
import pytest
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.notification import NotificationLog
from app.models.order import Order, OrderStatus, PaymentStatus
from app.models.payment import Payment, PaymentRecordStatus
from app.services.notification.email import MockEmailProvider
from app.services.notification.factory import get_email_provider
from app.services.notification.service import (
    EmailService,
    dispatch_delivery_background,
    dispatch_payment_confirmed_background,
    dispatch_refund_background,
)


@pytest.fixture
def db_session():
    """Yield a database session and clean up created test records afterwards."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def mock_email():
    """Provide a clean MockEmailProvider."""
    provider = get_email_provider()
    if isinstance(provider, MockEmailProvider):
        provider.clear()
    return provider


@pytest.fixture
def sample_order(db_session: Session) -> Order:
    """Create a sample order for email testing."""
    now = datetime.now(timezone.utc)
    order_num = f"SLC-TEST-{int(now.timestamp() * 1000)}"
    order = Order(
        order_number=order_num,
        customer_name="Aarav Sharma",
        customer_phone="9876543210",
        customer_email="aarav@example.com",
        status=OrderStatus.CONFIRMED.value,
        payment_status=PaymentStatus.PAID.value,
        payment_method="ONLINE",
        total_amount=2599.0,
        subtotal=2599.0,
        shipping_address_json={
            "name": "Aarav Sharma",
            "email": "aarav@example.com",
            "phone": "9876543210",
            "addressLine1": "123 Artisan Lane",
            "city": "Bengaluru",
            "state": "Karnataka",
            "pincode": "560001",
        },
        tracking_number="BLUEDART-88221",
        courier_name="Bluedart Express",
        created_at=now,
        updated_at=now,
    )
    db_session.add(order)
    db_session.commit()
    db_session.refresh(order)
    return order


def test_email_service_send_magic_link_redaction(db_session: Session, mock_email: MockEmailProvider):
    """Verify magic link delivery, sender identity, and strict token redaction in logs."""
    recipient = "customer-magic@example.com"
    raw_token = "secret_single_use_token_abc123"
    magic_link = f"https://sulocraft.com/auth/email/verify?token={raw_token}&returnTo=%2Fadmin"

    success, err = EmailService.send_magic_link(
        db=db_session,
        to_email=recipient,
        magic_link=magic_link,
        expires_minutes=15,
    )

    assert success is True
    assert err is None

    # Check mock email capture
    assert len(mock_email.sent_emails) >= 1
    sent = mock_email.sent_emails[-1]
    assert sent["to"] == recipient
    assert sent["from"] == settings.email_from_welcome
    assert raw_token in sent["html"]
    assert raw_token in sent["text"]

    # Check DB notification log — RAW TOKEN MUST BE REDACTED
    log = (
        db_session.query(NotificationLog)
        .filter(NotificationLog.recipient == recipient, NotificationLog.event_type == "MAGIC_LINK")
        .first()
    )
    assert log is not None
    assert log.status in ("SENT", "MOCK")
    assert raw_token not in log.body
    assert "https://" not in log.body
    assert "[magic link dispatched — URL redacted]" in log.body


def test_email_service_order_confirmation_and_idempotency(
    db_session: Session, mock_email: MockEmailProvider, sample_order: Order
):
    """Verify order confirmation email sending and duplicate prevention (idempotency)."""
    # 1. First send
    success, err = EmailService.send_order_confirmation(db=db_session, order=sample_order)
    assert success is True
    assert err is None
    assert len(mock_email.sent_emails) == 1
    sent = mock_email.sent_emails[0]
    assert sent["to"] == sample_order.customer_email
    assert sample_order.order_number in sent["subject"]
    assert sent["from"] == settings.email_from_orders

    log_count_before = (
        db_session.query(NotificationLog)
        .filter(
            NotificationLog.recipient == sample_order.customer_email,
            NotificationLog.event_type == "ORDER_CONFIRMED",
        )
        .count()
    )
    assert log_count_before == 1

    # 2. Second send (should be idempotent skip)
    success2, err2 = EmailService.send_order_confirmation(db=db_session, order=sample_order)
    assert success2 is True
    assert err2 is None
    # No new email appended to mock_email.sent_emails
    assert len(mock_email.sent_emails) == 1

    log_count_after = (
        db_session.query(NotificationLog)
        .filter(
            NotificationLog.recipient == sample_order.customer_email,
            NotificationLog.event_type == "ORDER_CONFIRMED",
        )
        .count()
    )
    assert log_count_after == log_count_before


def test_email_service_payment_confirmation_and_idempotency(
    db_session: Session, mock_email: MockEmailProvider, sample_order: Order
):
    """Verify payment confirmation email and duplicate prevention."""
    now = datetime.now(timezone.utc)
    payment = Payment(
        order_id=sample_order.id,
        provider="RAZORPAY",
        provider_payment_id="pay_Kj98127391823",
        amount=sample_order.total_amount,
        amount_paise=sample_order.total_amount * 100,
        currency="INR",
        status=PaymentRecordStatus.SUCCESS.value,
        created_at=now,
        updated_at=now,
    )
    db_session.add(payment)
    db_session.commit()

    success, err = EmailService.send_payment_confirmation(db=db_session, order=sample_order, payment=payment)
    assert success is True
    assert err is None
    assert len(mock_email.sent_emails) == 1
    sent = mock_email.sent_emails[0]
    assert sent["to"] == sample_order.customer_email
    assert "Payment Confirmed" in sent["subject"]
    assert "pay_Kj98127391823" in sent["html"]
    assert sent["from"] == settings.email_from_orders

    # Repeat call - must be skipped idempotently
    success2, err2 = EmailService.send_payment_confirmation(db=db_session, order=sample_order, payment=payment)
    assert success2 is True
    assert len(mock_email.sent_emails) == 1


def test_email_service_shipping_update_and_idempotency(
    db_session: Session, mock_email: MockEmailProvider, sample_order: Order
):
    """Verify shipping dispatch update email with tracking information."""
    success, err = EmailService.send_shipping_update(
        db=db_session,
        order=sample_order,
        carrier="Bluedart Express",
        tracking_number="BLUEDART-88221",
    )
    assert success is True
    assert err is None
    assert len(mock_email.sent_emails) == 1
    sent = mock_email.sent_emails[0]
    assert sent["to"] == sample_order.customer_email
    assert "Has Shipped" in sent["subject"]
    assert "BLUEDART-88221" in sent["html"]
    assert "Bluedart Express" in sent["html"]
    assert sent["from"] == settings.email_from_orders

    # Idempotent retry
    success2, _ = EmailService.send_shipping_update(db=db_session, order=sample_order)
    assert success2 is True
    assert len(mock_email.sent_emails) == 1


def test_email_service_delivery_update_and_idempotency(
    db_session: Session, mock_email: MockEmailProvider, sample_order: Order
):
    """Verify delivery confirmation update email."""
    success, err = EmailService.send_delivery_update(db=db_session, order=sample_order)
    assert success is True
    assert err is None
    assert len(mock_email.sent_emails) == 1
    sent = mock_email.sent_emails[0]
    assert sent["to"] == sample_order.customer_email
    assert "Delivered" in sent["subject"]
    assert sent["from"] == settings.email_from_orders

    # Idempotent retry
    success2, _ = EmailService.send_delivery_update(db=db_session, order=sample_order)
    assert success2 is True
    assert len(mock_email.sent_emails) == 1


def test_email_service_refund_notification_and_idempotency(
    db_session: Session, mock_email: MockEmailProvider, sample_order: Order
):
    """Verify refund notification email is sent from support identity."""
    success, err = EmailService.send_refund_notification(
        db=db_session,
        order=sample_order,
        refund_amount=2599.0,
        reason="Customer cancellation request approved",
    )
    assert success is True
    assert err is None
    assert len(mock_email.sent_emails) == 1
    sent = mock_email.sent_emails[0]
    assert sent["to"] == sample_order.customer_email
    assert "Refund Issued" in sent["subject"]
    assert sent["from"] == settings.email_from_support
    assert "Customer cancellation request approved" in sent["html"]

    # Idempotent retry
    success2, _ = EmailService.send_refund_notification(db=db_session, order=sample_order)
    assert success2 is True
    assert len(mock_email.sent_emails) == 1


def test_background_dispatchers(db_session: Session, mock_email: MockEmailProvider, sample_order: Order):
    """Verify decoupled background dispatch helper functions execute cleanly."""
    dispatch_payment_confirmed_background(sample_order.id)
    dispatch_delivery_background(sample_order.id)
    dispatch_refund_background(sample_order.id, refund_amount=1500.0, reason="Partial return")

    assert len(mock_email.sent_emails) == 3


def test_resend_production_fail_closed_validation():
    """Verify startup validation fails closed in production if Resend config is missing or invalid."""
    from app.main import lifespan
    import asyncio

    # Test 1: Production with Resend but missing API key
    orig_env = settings.app_env
    orig_provider = settings.email_provider
    orig_key = settings.resend_api_key
    orig_sender = settings.email_from_orders

    try:
        settings.app_env = "production"
        settings.email_provider = "resend"
        settings.resend_api_key = ""

        dummy_app = None
        with pytest.raises(RuntimeError, match="Production EMAIL_PROVIDER=resend requires RESEND_API_KEY"):
            async def run():
                async with lifespan(dummy_app):
                    pass
            asyncio.run(run())

        # Test 2: Production with invalid sender domain (not @sulocraft.com)
        settings.resend_api_key = "re_live_secret_key"
        settings.email_from_orders = "Sulocraft <orders@gmail.com>"
        with pytest.raises(RuntimeError, match="must be on the @sulocraft.com domain"):
            async def run2():
                async with lifespan(dummy_app):
                    pass
            asyncio.run(run2())

    finally:
        settings.app_env = orig_env
        settings.email_provider = orig_provider
        settings.resend_api_key = orig_key
        settings.email_from_orders = orig_sender


def test_render_welcome_email():
    """Verify render_welcome_email generates rich HTML and plain text with and without custom note."""
    from app.services.notification.templates import render_welcome_email

    # 1. Default greeting
    html, text = render_welcome_email(customer_name="Pooja", storefront_url="https://sulocraft.com")
    assert "We're so glad you're here, Pooja!" in html
    assert "Pooja!" in text
    assert "SULOCRAFT" in html
    assert "100% Handcrafted" in html
    assert "Anupama Sharma" in html
    assert "https://sulocraft.com/shop" in html
    assert "welcome@sulocraft.com" in html

    # 2. Custom welcome message from founder
    custom_msg = "Thank you for joining our launch party! Enjoy 10% off your first order."
    html_custom, text_custom = render_welcome_email(
        customer_name="Rohan",
        custom_message=custom_msg,
        storefront_url="https://sulocraft.com",
    )
    assert "We're so glad you're here, Rohan!" in html_custom
    assert custom_msg in html_custom
    assert custom_msg in text_custom


def test_send_welcome_email_service(db_session: Session, mock_email: MockEmailProvider):
    """Verify EmailService.send_welcome_email dispatches from welcome@sulocraft.com and logs to DB."""
    recipient = "newcustomer@example.com"
    custom_note = "A special welcome to our handcrafted crochet world."

    success, err = EmailService.send_welcome_email(
        db=db_session,
        to_email=recipient,
        customer_name="Aarohi",
        custom_message=custom_note,
    )

    assert success is True
    assert err is None

    # Check mock email capture
    assert len(mock_email.sent_emails) >= 1
    sent = mock_email.sent_emails[-1]
    assert sent["to"] == recipient
    assert sent["from"] == settings.email_from_welcome
    assert "Aarohi" in sent["html"]
    assert custom_note in sent["html"]

    # Check DB notification log
    log = (
        db_session.query(NotificationLog)
        .filter(NotificationLog.recipient == recipient, NotificationLog.event_type == "WELCOME_EMAIL")
        .first()
    )
    assert log is not None
    assert log.status in ("SENT", "MOCK")
    assert log.channel == "EMAIL"
    assert "welcome" in log.subject.lower()
