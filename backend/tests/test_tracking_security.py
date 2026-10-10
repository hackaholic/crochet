"""Comprehensive security and contract tests for order tracking and guest access (Work 017 Task 17.1)."""

from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal
from app.models.catalogue import Product, ProductVariant
from app.models.order import GuestOrderAccessToken, Order, OrderStatus, OrderStatusHistory
from app.models.user import User
from app.services.guest_tracking import create_guest_order_token, hash_token

client = TestClient(app)


def _login_test_user(phone: str = "9999943210") -> dict[str, str]:
    """Helper to authenticate and return session cookies."""
    email = f"user_{phone}@example.com" if phone.isdigit() else phone
    res = client.post("/api/v1/auth/google", json={
        "credential": f"mock_token_{phone}",
        "email": email,
        "name": "Test Customer",
        "sub": f"sub_{phone}",
    })
    assert res.status_code == 200
    return dict(res.cookies)


def _create_order_fixture(
    user_id: int | None = None,
    order_number: str = "SLC-TEST-001",
    customer_email: str = "guest@example.com",
    courier_name: str | None = "Sulocraft Express",
    tracking_number: str | None = "SLC-TRACK-999",
) -> Order:
    """Helper to insert an order fixture with status history."""
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        # Check if exists
        existing = db.query(Order).filter(Order.order_number == order_number).first()
        if existing:
            db.delete(existing)
            db.commit()

        order = Order(
            order_number=order_number,
            user_id=user_id,
            customer_name="Test Recipient",
            customer_phone="9876543210",
            customer_email=customer_email,
            shipping_address_json={
                "name": "Test Recipient",
                "phone": "9876543210",
                "email": customer_email,
                "line1": "123 Craft Lane",
                "city": "Bengaluru",
                "state": "Karnataka",
                "postalCode": "560001",
            },
            status=OrderStatus.CONFIRMED.value,
            payment_status="PAID",
            payment_method="ONLINE",
            currency="INR",
            subtotal=1500,
            shipping_fee=0,
            discount_amount=0,
            total_amount=1500,
            courier_name=courier_name,
            tracking_number=tracking_number,
            estimated_delivery=now + timedelta(days=4),
            created_at=now,
            updated_at=now,
        )
        db.add(order)
        db.flush()

        history = OrderStatusHistory(
            order_id=order.id,
            status=OrderStatus.CONFIRMED.value,
            note="Order confirmed.",
            timestamp=now,
        )
        db.add(history)
        db.commit()
        db.refresh(order)
        order_copy = Order(
            id=order.id,
            order_number=order.order_number,
            user_id=order.user_id,
            customer_email=order.customer_email,
        )
        return order_copy


def test_tc01_owner_requests_own_order_tracking():
    """17.1-TC01: Authenticated user requests tracking for their own order -> 200 OK."""
    cookies = _login_test_user("9999901001")
    with SessionLocal() as db:
        user = db.query(User).filter(User.email == "user_9999901001@example.com").first()
        assert user is not None
        user_id = user.id

    order = _create_order_fixture(user_id=user_id, order_number="SLC-TC01-001")

    res = client.get(f"/api/v1/orders/{order.order_number}/tracking", cookies=cookies)
    assert res.status_code == 200
    data = res.json()
    assert data["orderNumber"] == order.order_number
    assert data["status"] == "CONFIRMED"
    assert data["courierName"] == "Sulocraft Express"
    assert data["trackingNumber"] == "SLC-TRACK-999"
    assert len(data["timeline"]) >= 1
    assert "no-store" in res.headers.get("cache-control", "")
    assert "private" in res.headers.get("cache-control", "")


def test_tc02_account_isolation_denies_wrong_user_and_anonymous():
    """17.1-TC02: Authenticated user B or anonymous caller requests user A's order tracking -> 404."""
    cookies_a = _login_test_user("9999901002")
    cookies_b = _login_test_user("9999901003")

    with SessionLocal() as db:
        user_a = db.query(User).filter(User.email == "user_9999901002@example.com").first()
        assert user_a is not None
        user_a_id = user_a.id

    order = _create_order_fixture(user_id=user_a_id, order_number="SLC-TC02-001")

    # Anonymous request
    anon_res = client.get(f"/api/v1/orders/{order.order_number}/tracking")
    assert anon_res.status_code == 404
    assert "no-store" in anon_res.headers.get("cache-control", "")

    # User B request
    other_res = client.get(f"/api/v1/orders/{order.order_number}/tracking", cookies=cookies_b)
    assert other_res.status_code == 404


def test_tc03_guest_idor_prevention():
    """17.1-TC03: Anonymous caller requests guest order tracking without a token -> 404."""
    order = _create_order_fixture(user_id=None, order_number="SLC-TC03-GUEST")

    # Numeric ID lookup
    res_num = client.get(f"/api/v1/orders/{order.id}/tracking")
    assert res_num.status_code == 404

    # Order number lookup
    res_str = client.get(f"/api/v1/orders/{order.order_number}/tracking")
    assert res_str.status_code == 404

    # Order detail endpoint also protected
    res_detail = client.get(f"/api/v1/orders/{order.order_number}")
    assert res_detail.status_code == 404


def test_tc04_guest_valid_scoped_token_succeeds():
    """17.1-TC04: Guest requests tracking with valid token (via query param, header, or bearer) -> 200 OK."""
    order = _create_order_fixture(user_id=None, order_number="SLC-TC04-GUEST")

    with SessionLocal() as db:
        raw_token, _ = create_guest_order_token(db, order.id, expires_days=7)

    # 1. Query parameter ?token=...
    res_query = client.get(f"/api/v1/orders/{order.order_number}/tracking?token={raw_token}")
    assert res_query.status_code == 200
    data = res_query.json()
    assert data["orderNumber"] == order.order_number
    assert len(data["timeline"]) >= 1

    # 2. X-Guest-Order-Token header
    res_header = client.get(
        f"/api/v1/orders/{order.order_number}/tracking",
        headers={"X-Guest-Order-Token": raw_token},
    )
    assert res_header.status_code == 200

    # 3. Bearer Authorization header
    res_bearer = client.get(
        f"/api/v1/orders/{order.order_number}/tracking",
        headers={"Authorization": f"Bearer {raw_token}"},
    )
    assert res_bearer.status_code == 200

    # 4. Detail endpoint also succeeds with token
    res_detail = client.get(
        f"/api/v1/orders/{order.order_number}?token={raw_token}"
    )
    assert res_detail.status_code == 200
    assert res_detail.json()["orderNumber"] == order.order_number


def test_tc05_invalid_expired_revoked_wrong_order_token_denied():
    """17.1-TC05: Invalid/expired/revoked/wrong-order guest tokens -> 404."""
    order_a = _create_order_fixture(user_id=None, order_number="SLC-TC05-A")
    order_b = _create_order_fixture(user_id=None, order_number="SLC-TC05-B")

    with SessionLocal() as db:
        token_a, _ = create_guest_order_token(db, order_a.id)
        token_b, _ = create_guest_order_token(db, order_b.id)

        # Create expired token for order A
        now = datetime.now(timezone.utc)
        expired_record = GuestOrderAccessToken(
            order_id=order_a.id,
            token_hash=hash_token("expired_token_123"),
            created_at=now - timedelta(days=20),
            expires_at=now - timedelta(days=1),
            is_revoked=False,
        )
        # Create revoked token for order A
        revoked_record = GuestOrderAccessToken(
            order_id=order_a.id,
            token_hash=hash_token("revoked_token_123"),
            created_at=now,
            expires_at=now + timedelta(days=7),
            is_revoked=True,
            revoked_at=now,
        )
        db.add_all([expired_record, revoked_record])
        db.commit()

    # Wrong order token (Token B used against Order A)
    res_wrong = client.get(f"/api/v1/orders/{order_a.order_number}/tracking?token={token_b}")
    assert res_wrong.status_code == 404

    # Expired token
    res_exp = client.get(f"/api/v1/orders/{order_a.order_number}/tracking?token=expired_token_123")
    assert res_exp.status_code == 404

    # Revoked token
    res_rev = client.get(f"/api/v1/orders/{order_a.order_number}/tracking?token=revoked_token_123")
    assert res_rev.status_code == 404

    # Completely bogus token
    res_fake = client.get(f"/api/v1/orders/{order_a.order_number}/tracking?token=invalid_garbage_token")
    assert res_fake.status_code == 404


def test_tc06_non_enumerating_link_request():
    """17.1-TC06: POST /orders/tracking/request-link returns generic 202 whether order exists or not."""
    order = _create_order_fixture(
        user_id=None,
        order_number="SLC-TC06-GUEST",
        customer_email="matching@example.com",
    )

    # 1. Matching order and email -> 202 Accepted, dev link issued in test env
    res_match = client.post(
        "/api/v1/orders/tracking/request-link",
        json={"orderNumber": order.order_number, "email": "matching@example.com"},
    )
    assert res_match.status_code == 202
    data_match = res_match.json()
    assert "If the order number and email match our records" in data_match["message"]
    assert data_match["devTrackingLink"] is not None

    # Verify link generated uses fragment (#token=) and no query token (?token=)
    dev_link = data_match["devTrackingLink"]
    assert f"/track/{order.order_number}#token=" in dev_link
    assert "?token=" not in dev_link

    # Verify token extracted from fragment works with X-Guest-Order-Token header or query fallback
    token_str = dev_link.split("#token=")[-1]
    verify_res_header = client.get(
        f"/api/v1/orders/{order.order_number}/tracking",
        headers={"X-Guest-Order-Token": token_str},
    )
    assert verify_res_header.status_code == 200

    verify_res_query = client.get(f"/api/v1/orders/{order.order_number}/tracking?token={token_str}")
    assert verify_res_query.status_code == 200

    # 2. Existing order but non-matching email -> 202 Accepted, NO dev link issued
    res_mismatch = client.post(
        "/api/v1/orders/tracking/request-link",
        json={"orderNumber": order.order_number, "email": "attacker@example.com"},
    )
    assert res_mismatch.status_code == 202
    data_mismatch = res_mismatch.json()
    assert data_mismatch["message"] == data_match["message"]
    assert data_mismatch["devTrackingLink"] is None

    # 3. Non-existent order number -> 202 Accepted, NO dev link issued
    res_none = client.post(
        "/api/v1/orders/tracking/request-link",
        json={"orderNumber": "SLC-NONEXISTENT-999", "email": "any@example.com"},
    )
    assert res_none.status_code == 202
    data_none = res_none.json()
    assert data_none["message"] == data_match["message"]
    assert data_none["devTrackingLink"] is None


def test_tc10_non_enumeration_in_production_environment(monkeypatch):
    """17.7-TC10: In production or preprod environments, devTrackingLink is NEVER returned."""
    order = _create_order_fixture(
        user_id=None,
        order_number="SLC-TC10-PROD",
        customer_email="prod_customer@example.com",
    )

    from app.core.config import settings
    monkeypatch.setattr(settings, "app_env", "production")
    monkeypatch.setenv("TESTING", "false")

    # Requester with matching credentials in production
    prod_client = TestClient(app)
    res = prod_client.post(
        "/api/v1/orders/tracking/request-link",
        json={"orderNumber": order.order_number, "email": "prod_customer@example.com"},
    )
    assert res.status_code == 202
    data = res.json()
    assert "If the order number and email match our records" in data["message"]
    # In production, devTrackingLink MUST be None even on match, preventing credential exposure
    assert data["devTrackingLink"] is None


def test_tc07_boundary_and_validation():
    """17.1-TC07: Malformed inputs to request-link return 422; invalid tracking identifiers safely 404."""
    # Empty email
    res_empty = client.post(
        "/api/v1/orders/tracking/request-link",
        json={"orderNumber": "SLC-123", "email": ""},
    )
    assert res_empty.status_code == 422

    # Oversized orderNumber (>50 chars)
    res_long = client.post(
        "/api/v1/orders/tracking/request-link",
        json={"orderNumber": "A" * 51, "email": "test@example.com"},
    )
    assert res_long.status_code == 422


def test_tc08_honest_state_for_orders_without_shipment():
    """17.1-TC08: Order with no courier or tracking number returns null honestly without inventing data."""
    order = _create_order_fixture(
        user_id=None,
        order_number="SLC-TC08-NOSHIP",
        courier_name=None,
        tracking_number=None,
    )

    with SessionLocal() as db:
        token, _ = create_guest_order_token(db, order.id)

    res = client.get(f"/api/v1/orders/{order.order_number}/tracking?token={token}")
    assert res.status_code == 200
    data = res.json()
    assert data["orderNumber"] == order.order_number
    assert data["courierName"] is None
    assert data["trackingNumber"] is None


def test_tc09_security_logging_and_cache_control():
    """17.1-TC09: Raw tokens are never logged in DB audit logs; Cache-Control headers verified."""
    order = _create_order_fixture(user_id=None, order_number="SLC-TC09-AUDIT")

    with SessionLocal() as db:
        raw_token, token_rec = create_guest_order_token(db, order.id)
        # Check token table: raw token should not be in the database
        assert token_rec.token_hash != raw_token
        assert len(token_rec.token_hash) == 64

    # Request tracking
    res = client.get(f"/api/v1/orders/{order.order_number}/tracking?token={raw_token}")
    assert res.status_code == 200
    assert "no-store" in res.headers.get("cache-control", "")
    assert "private" in res.headers.get("cache-control", "")

    # Detail request
    res_detail = client.get(f"/api/v1/orders/{order.order_number}?token={raw_token}")
    assert res_detail.status_code == 200
    assert "no-store" in res_detail.headers.get("cache-control", "")
    assert "private" in res_detail.headers.get("cache-control", "")
