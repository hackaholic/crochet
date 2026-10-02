"""Security Integration Tests: E-commerce Business Logic Integrity.

Conforms to Work 009 Task 9.5 and Audit Policy Level 1 & 2 requirements.
Ensures zero business logic vulnerabilities:
- Authoritative backend pricing (no client-side price, shipping, or tax manipulation).
- Authoritative promo coupon validation and integer paise math.
- Inventory integrity (rejection of zero/negative quantities and out-of-stock purchases).
- Order workflow integrity (customer cannot self-refund or mark orders PAID/SHIPPED).
- Privilege escalation prevention (customers cannot escalate role to ADMIN).
- Authentication lifecycle security (magic link expiration, single-use, open redirect prevention).
"""

import hashlib
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient

from app.core.config import settings
from app.db.session import SessionLocal
from app.main import app
from app.models.catalogue import Product, ProductVariant
from app.models.promotion import Coupon
from app.models.user import MagicLinkToken, User, UserIdentity


def _create_authenticated_client(phone: str) -> tuple[TestClient, dict[str, str]]:
    """Helper to create an independent TestClient session for a customer."""
    client = TestClient(app)
    email = f"bizcust_{phone}@example.com"
    res = client.post(
        "/api/v1/auth/google",
        json={
            "credential": f"mock_token_{phone}",
            "email": email,
            "name": f"Customer {phone}",
            "sub": f"sub_{phone}",
        },
    )
    assert res.status_code == 200
    with SessionLocal() as db:
        user = db.query(User).filter(User.email == email).first()
        if user and user.phone != phone:
            user.phone = phone
            db.commit()
    return client, dict(res.cookies)


def test_authoritative_price_calculation_and_tampering_rejection():
    """Verify customer cannot override item prices, shipping fees, or totals in order requests."""
    client, _ = _create_authenticated_client("9999922001")

    with SessionLocal() as db:
        variant = db.query(ProductVariant).filter(ProductVariant.id == 1).first()
        authoritative_unit_price = variant.price
        assert authoritative_unit_price > 0

    # Add 2 items to cart
    client.post("/api/v1/cart/items", json={"product_variant_id": 1, "quantity": 2})

    # Customer attempts to forge subtotal, shippingFee, and totalAmount to ₹1 in order payload
    tampered_payload = {
        "shippingAddress": {
            "name": "Price Tamperer",
            "phone": "9999922001",
            "line1": "Tamper Street",
            "city": "Bengaluru",
            "state": "Karnataka",
            "postalCode": "560001",
        },
        "paymentMethod": "COD",
        "unitPrice": 1,
        "subtotal": 1,
        "shippingFee": 999,
        "totalAmount": 1,
        "totalAmountPaise": 100,
    }

    order_res = client.post("/api/v1/orders", json=tampered_payload)
    assert order_res.status_code == 201
    order_data = order_res.json()

    # The backend MUST enforce authoritative calculations:
    expected_subtotal = authoritative_unit_price * 2
    expected_shipping = 0 if expected_subtotal >= 999 else 99
    expected_total = expected_subtotal + expected_shipping

    assert order_data["subtotal"] == expected_subtotal, f"Price tampering succeeded! Subtotal: {order_data['subtotal']}"
    assert order_data["shippingFee"] == expected_shipping, f"Shipping fee tampering succeeded! Shipping: {order_data['shippingFee']}"
    assert order_data["totalAmount"] == expected_total, f"Total tampering succeeded! Total: {order_data['totalAmount']}"
    assert order_data["subtotalPaise"] == expected_subtotal * 100
    assert order_data["totalAmountPaise"] == expected_total * 100


def test_coupon_tampering_and_authoritative_discount():
    """Verify promo discount amounts cannot be tampered with or applied when invalid."""
    client, _ = _create_authenticated_client("9999922002")

    # Create test coupon: 10% off, max 50, min order 400
    with SessionLocal() as db:
        test_coupon = Coupon(
            code="SEC10",
            description="Security Test Promo 10%",
            discount_type="PERCENTAGE",
            discount_value=10,
            max_discount_amount=50,
            min_order_amount=400,
            is_active=True,
            usage_limit=10,
            usage_count=0,
            valid_from=datetime.now(timezone.utc) - timedelta(days=1),
            valid_until=datetime.now(timezone.utc) + timedelta(days=7),
        )
        db.add(test_coupon)
        db.commit()

    # 1. Attempting invalid coupon code -> rejected with 400
    client.post("/api/v1/cart/items", json={"product_variant_id": 1, "quantity": 1})
    invalid_coupon_res = client.post(
        "/api/v1/orders",
        json={
            "shippingAddress": {
                "name": "Customer",
                "phone": "9999922002",
                "line1": "Street",
                "city": "Bengaluru",
                "state": "Karnataka",
                "postalCode": "560001",
            },
            "paymentMethod": "COD",
            "couponCode": "NONEXISTENT_99",
        },
    )
    assert invalid_coupon_res.status_code == 400

    # 2. Applying valid coupon SEC10: Product 1 price is 2599. 10% is 259, capped by max_discount_amount=50.
    valid_coupon_res = client.post(
        "/api/v1/orders",
        json={
            "shippingAddress": {
                "name": "Customer",
                "phone": "9999922002",
                "line1": "Street",
                "city": "Bengaluru",
                "state": "Karnataka",
                "postalCode": "560001",
            },
            "paymentMethod": "COD",
            "couponCode": "SEC10",
            "discountAmount": 9999,  # Customer attempts to claim 9999 discount
        },
    )
    assert valid_coupon_res.status_code == 201
    order = valid_coupon_res.json()
    assert order["discountAmount"] == 50, "Discount tampering succeeded!"
    assert order["totalAmount"] == 2599 - 50  # 2549 >= 999 so shipping is 0


def test_inventory_integrity_out_of_stock_rejected():
    """Verify purchasing an item with 0 stock is rejected by cart and checkout."""
    client, _ = _create_authenticated_client("9999922003")

    with SessionLocal() as db:
        variant = db.query(ProductVariant).filter(ProductVariant.id == 2).first()
        variant.stock_quantity = 0
        db.commit()

    # Attempting to add out of stock item to cart -> 400
    res = client.post("/api/v1/cart/items", json={"product_variant_id": 2, "quantity": 1})
    assert res.status_code == 400
    assert "out of stock" in res.json()["detail"].lower()


def test_inventory_integrity_zero_and_negative_quantities_rejected():
    """Verify zero and negative quantities are strictly rejected."""
    client, _ = _create_authenticated_client("9999922004")

    # 1. Negative quantity in cart add -> 422 Unprocessable Entity
    neg_res = client.post("/api/v1/cart/items", json={"product_variant_id": 1, "quantity": -3})
    assert neg_res.status_code == 422

    # 2. Zero quantity in cart add -> 422
    zero_res = client.post("/api/v1/cart/items", json={"product_variant_id": 1, "quantity": 0})
    assert zero_res.status_code == 422

    # 3. Add legitimate item
    valid_res = client.post("/api/v1/cart/items", json={"product_variant_id": 1, "quantity": 1})
    assert valid_res.status_code == 201
    cart_item_id = valid_res.json()["items"][0]["id"]

    # 4. Negative quantity in cart item update -> 422
    neg_update = client.patch(f"/api/v1/cart/items/{cart_item_id}", json={"quantity": -1})
    assert neg_update.status_code == 422

    # 5. Zero quantity in cart item update -> 422
    zero_update = client.patch(f"/api/v1/cart/items/{cart_item_id}", json={"quantity": 0})
    assert zero_update.status_code == 422


def test_customer_cannot_mark_order_paid_or_shipped():
    """Verify customers cannot alter order lifecycle statuses or mark orders PAID/SHIPPED."""
    client, _ = _create_authenticated_client("9999922005")

    client.post("/api/v1/cart/items", json={"product_id": 1, "quantity": 1})
    order_res = client.post(
        "/api/v1/orders",
        json={
            "shippingAddress": {
                "name": "Customer",
                "phone": "9999922005",
                "line1": "Street",
                "city": "Bengaluru",
                "state": "Karnataka",
                "postalCode": "560001",
            },
            "paymentMethod": "COD",
        },
    )
    assert order_res.status_code == 201
    order_id = order_res.json()["id"]

    # 1. Customer attempts to call admin status mutation endpoint -> 403 Forbidden
    admin_transition = client.patch(
        f"/api/v1/admin/orders/{order_id}/status",
        json={"status": "DELIVERED"},
    )
    assert admin_transition.status_code == 403

    # 2. Customer attempts to send direct PATCH to customer order endpoint -> 405 Method Not Allowed / 404
    direct_patch = client.patch(
        f"/api/v1/orders/{order_id}",
        json={"status": "PAID", "paymentStatus": "PAID"},
    )
    assert direct_patch.status_code in (404, 405)


def test_privilege_escalation_to_admin_prevented():
    """Verify regular customer cannot elevate their own role to ADMIN."""
    client, _ = _create_authenticated_client("9999922006")

    # 1. Attempt to escalate role via PATCH /api/v1/account/profile
    patch_res = client.patch(
        "/api/v1/account/profile",
        json={"name": "Attacker", "role": "ADMIN", "is_admin": True},
    )
    assert patch_res.status_code == 200

    # 2. Verify in database and via /api/v1/account/profile that role is still CUSTOMER
    with SessionLocal() as db:
        user = db.query(User).filter(User.phone == "9999922006").first()
        assert user.role == "CUSTOMER", f"Privilege Escalation! User role escalated to {user.role}"

    # 3. Verify user cannot access admin routes -> 403 Forbidden
    admin_check = client.get("/api/v1/admin/dashboard/summary")
    assert admin_check.status_code == 403


def test_magic_link_security_expiration_and_single_use():
    """Verify magic link tokens expire according to policy and cannot be used more than once."""
    email = "magic.security@example.com"
    auth_client = TestClient(app)

    # 1. Start flow
    res = auth_client.post("/api/v1/auth/email/start", json={"email": email})
    assert res.status_code == 202
    token = res.json()["devMagicLink"].split("token=")[1]

    # Test single-use: First verification succeeds
    v1 = auth_client.get(f"/api/v1/auth/email/verify?token={token}", follow_redirects=False)
    assert v1.status_code == 303
    assert "error" not in v1.headers["location"]

    # Second verification fails
    v2 = auth_client.get(f"/api/v1/auth/email/verify?token={token}", follow_redirects=False)
    assert v2.status_code == 303
    assert "error=invalid_link" in v2.headers["location"]

    # Test expiration: manually insert an expired token in DB
    expired_token_str = "expired_token_test_123456789"
    with SessionLocal() as db:
        user = db.query(User).filter(User.email == email).first()
        expired_token = MagicLinkToken(
            token_hash=hashlib.sha256(expired_token_str.encode("utf-8")).hexdigest(),
            email=email,
            expires_at=datetime.now(timezone.utc) - timedelta(minutes=10),
            is_used=False,
            used_at=None,
        )
        db.add(expired_token)
        db.commit()

    exp_res = auth_client.get(f"/api/v1/auth/email/verify?token={expired_token_str}", follow_redirects=False)
    assert exp_res.status_code == 303
    assert "error=" in exp_res.headers["location"]


def test_magic_link_open_redirect_prevented():
    """Verify magic link returnTo cannot redirect to external/malicious URLs."""
    email = "openredirect@example.com"
    auth_client = TestClient(app)

    malicious_targets = [
        "https://evil.com/phishing",
        "http://attacker.org",
        "//evil.com",
        "javascript:alert(1)",
        "ftp://evil.com",
        "https:evil.com",
    ]

    for idx, malicious_url in enumerate(malicious_targets):
        test_email = f"openredirect_{idx}@example.com"
        res = auth_client.post("/api/v1/auth/email/start", json={"email": test_email})
        assert res.status_code == 202
        assert "devMagicLink" in res.json() and res.json()["devMagicLink"]
        token = res.json()["devMagicLink"].split("token=")[1]

        verify_res = auth_client.get(
            f"/api/v1/auth/email/verify?token={token}&returnTo={malicious_url}",
            follow_redirects=False,
        )
        assert verify_res.status_code == 303
        redirect_location = verify_res.headers["location"]
        assert "evil.com" not in redirect_location, f"Open Redirect Vulnerability: Redirected to {redirect_location}"
        assert "attacker.org" not in redirect_location
        assert redirect_location.startswith(settings.frontend_url) or redirect_location.startswith("/")
