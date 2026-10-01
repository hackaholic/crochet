"""Comprehensive tests for SMS & Email notification providers, templates, and service."""

from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.main import app
from app.models.notification import NotificationLog
from app.models.order import Order
from app.services.notification.email import MockEmailProvider, ResendEmailProvider, SmtpEmailProvider
from app.services.notification.factory import get_email_provider, get_sms_provider
from app.services.notification.service import NotificationService
from app.services.notification.sms import Fast2SmsProvider, MockSmsProvider, TwilioSmsProvider

client = TestClient(app)


def test_mock_sms_provider():
    """Verify MockSmsProvider logs and stores sent messages."""
    provider = MockSmsProvider()
    provider.clear()

    success, err = provider.send_otp("9876543210", "654321")
    assert success is True
    assert err is None
    assert len(provider.sent_messages) == 1
    assert provider.sent_messages[0]["phone"] == "9876543210"
    assert "654321" in provider.sent_messages[0]["message"]


def test_fast2sms_provider_mocked():
    """Verify Fast2SmsProvider formats API request correctly."""
    provider = Fast2SmsProvider(api_key="test_fast2sms_key", route="otp")

    with patch("httpx.Client.post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"return": True, "message": ["OTP sent successfully"]}
        mock_post.return_value = mock_resp

        success, err = provider.send_otp("919876543210", "123456")
        assert success is True
        assert err is None

        # Check call arguments
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert kwargs["json"]["variables_values"] == "123456"
        assert kwargs["json"]["numbers"] == "9876543210"
        assert kwargs["headers"]["authorization"] == "test_fast2sms_key"


def test_twilio_sms_provider_mocked():
    """Verify TwilioSmsProvider sends proper HTTP request with basic auth."""
    provider = TwilioSmsProvider(
        account_sid="AC123456",
        auth_token="auth_secret",
        from_phone="+15550001",
    )

    with patch("httpx.Client.post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.status_code = 201
        mock_post.return_value = mock_resp

        success, err = provider.send_otp("9876543210", "998877")
        assert success is True
        assert err is None

        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert kwargs["data"]["To"] == "+919876543210"
        assert kwargs["data"]["From"] == "+15550001"
        assert "998877" in kwargs["data"]["Body"]
        assert kwargs["auth"] == ("AC123456", "auth_secret")


def test_mock_email_provider():
    """Verify MockEmailProvider captures sent emails in-memory."""
    provider = MockEmailProvider()
    provider.clear()

    success, err = provider.send_email(
        to_email="customer@example.com",
        subject="Order Confirmation",
        html_content="<p>Order confirmed</p>",
        text_content="Order confirmed",
    )
    assert success is True
    assert err is None
    assert len(provider.sent_emails) == 1
    assert provider.sent_emails[0]["to"] == "customer@example.com"
    assert provider.sent_emails[0]["subject"] == "Order Confirmation"


def test_resend_email_provider_mocked():
    """Verify ResendEmailProvider formats REST payload properly."""
    provider = ResendEmailProvider(api_key="re_12345", from_email="Sulocraft <orders@sulocraft.com>")

    with patch("httpx.Client.post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_post.return_value = mock_resp

        success, err = provider.send_email(
            to_email="buyer@example.com",
            subject="Sulocraft Order",
            html_content="<h1>Confirmed</h1>",
            text_content="Confirmed",
        )
        assert success is True
        assert err is None

        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert kwargs["json"]["to"] == ["buyer@example.com"]
        assert kwargs["json"]["subject"] == "Sulocraft Order"
        assert kwargs["headers"]["Authorization"] == "Bearer re_12345"


def test_notification_service_send_magic_link_logging():
    """Verify NotificationService.send_magic_link records a sanitized audit log entry."""
    email = "magic.audit@example.com"
    magic_link = "http://localhost:8000/api/v1/auth/email/verify?token=secret_token_123"

    with SessionLocal() as db_session:
        success, err = NotificationService.send_magic_link(db_session, email, magic_link)
        assert success is True
        assert err is None

        # Inspect NotificationLog record
        log = (
            db_session.query(NotificationLog)
            .filter(NotificationLog.recipient == email, NotificationLog.event_type == "MAGIC_LINK")
            .first()
        )
        assert log is not None
        assert log.channel == "EMAIL"
        assert log.status in ("SENT", "MOCK")
        assert "secret_token_123" not in log.body
        assert "[magic link dispatched" in log.body


def test_notification_service_send_order_notifications():
    """Verify order placed and status update dispatch SMS and Email logs."""
    from app.models.catalogue import Product, ProductVariant
    from app.models.order import OrderItem, OrderStatus

    with SessionLocal() as db_session:
        product = db_session.query(Product).first()
        variant = db_session.query(ProductVariant).filter(ProductVariant.product_id == product.id).first()

        order = Order(
            order_number="CB-TEST-NOTIF-01",
            customer_name="Aarav Sharma",
            customer_phone="9876500002",
            customer_email="aarav@example.com",
            shipping_address_json={
                "name": "Aarav Sharma",
                "phone": "9876500002",
                "email": "aarav@example.com",
                "line1": "100 MG Road",
                "city": "Bengaluru",
                "state": "Karnataka",
                "postalCode": "560001",
            },
            subtotal=1999,
            shipping_fee=0,
            discount_amount=0,
            total_amount=1999,
            payment_method="COD",
            payment_status="PENDING",
            status=OrderStatus.CONFIRMED.value,
        )
        db_session.add(order)
        db_session.flush()

        item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            product_variant_id=variant.id,
            product_name=product.name,
            product_slug=product.slug,
            sku=variant.sku,
            variant_name=variant.name,
            unit_price=1999,
            quantity=1,
            line_total=1999,
        )
        db_session.add(item)
        db_session.commit()

        # 1. Trigger Order Placed notifications
        NotificationService.send_order_placed(db_session, order)

        logs = (
            db_session.query(NotificationLog)
            .filter(NotificationLog.event_type == "ORDER_CONFIRMED")
            .all()
        )
        channels = {l.channel for l in logs}
        assert "SMS" in channels
        assert "EMAIL" in channels

        # 2. Trigger Order Status update (SHIPPED)
        NotificationService.send_order_status_update(
            db_session,
            order,
            OrderStatus.SHIPPED.value,
            carrier="Delhivery",
            tracking_number="DEL123456789",
        )

        update_logs = (
            db_session.query(NotificationLog)
            .filter(NotificationLog.event_type == "ORDER_STATUS_UPDATE")
            .all()
        )
        assert len(update_logs) >= 2


def test_auth_send_magic_link_background_execution():
    """Verify POST /api/v1/auth/email/start triggers background Email notification and logging."""
    test_email = "notify.test@example.com"
    resp = client.post("/api/v1/auth/email/start", json={"email": test_email})
    assert resp.status_code == 202

    # Verify notification log entry was created
    with SessionLocal() as db_session:
        log = (
            db_session.query(NotificationLog)
            .filter(NotificationLog.recipient == test_email, NotificationLog.event_type == "MAGIC_LINK")
            .first()
        )
        assert log is not None
        assert log.channel == "EMAIL"
        assert "[magic link dispatched" in log.body
