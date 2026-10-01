"""
V1 Authentication & Purchase Regression Test Suite
===================================================
Covers the full V1 purchase lifecycle in a single session-consistent flow:

  1. Guest cart — add items without authentication.
  2. Email magic-link sign-in — session issued + guest cart merged.
  3. Address creation and checkout — order placed.
  4. Payment intent + mock verification — order transitions to PAID/CONFIRMED.
  5. Admin marks order PROCESSING -> SHIPPED with tracking number.
  6. Customer views order tracking timeline.

No phone-auth dependency. Follows docs/api-auth.md, docs/api-orders.md,
docs/api-payments.md, and the V1 authentication contract.
"""

import pytest
from fastapi.testclient import TestClient
from app.db.session import SessionLocal
from app.main import app
from app.models.user import User, UserIdentity


def _ensure_admin() -> None:
    admin_email = "admin@sulocraft.com"
    with SessionLocal() as db:
        admin = db.query(User).filter(User.email == admin_email).first()
        if not admin:
            admin = User(
                name="Store Admin",
                phone="9999900000",
                email=admin_email,
                role="ADMIN",
                status="ACTIVE",
            )
            db.add(admin)
            db.flush()
            db.add(UserIdentity(user_id=admin.id, provider="email", provider_subject=admin_email))
            db.commit()
        elif admin.role != "ADMIN":
            admin.role = "ADMIN"
            db.commit()


def _login_admin(tc: TestClient) -> dict:
    _ensure_admin()
    res = tc.post("/api/v1/auth/google", json={
        "credential": "mock_admin_token_regression",
        "email": "admin@sulocraft.com",
        "name": "Store Admin",
        "sub": "admin_sub_regression",
    })
    assert res.status_code == 200
    assert res.json()["user"]["role"] == "ADMIN"
    return dict(res.cookies)


def _first_variant(session: TestClient) -> tuple:
    prods = session.get("/api/v1/products").json()
    assert len(prods) > 0
    slug = prods[0]["slug"]
    variant = session.get(f"/api/v1/products/{slug}").json()["variants"][0]
    return slug, variant


def test_full_v1_purchase_flow_magic_link():
    """Guest cart -> magic-link login + merge -> checkout -> payment -> admin SHIPPED -> tracking."""
    session = TestClient(app)

    assert session.get("/api/v1/auth/me").status_code == 401

    slug, variant = _first_variant(session)
    variant_id = variant["id"]
    unit_price = variant["price"]
    initial_stock = variant["stockQuantity"]

    add_res = session.post("/api/v1/cart/items", json={"product_variant_id": variant_id, "quantity": 2})
    assert add_res.status_code == 201
    assert "guest_cart_token" in session.cookies
    assert session.get("/api/v1/cart").json()["itemCount"] == 2

    email = "regression.buyer@example.com"
    start_res = session.post("/api/v1/auth/email/start", json={"email": email})
    assert start_res.status_code == 202
    token = start_res.json()["devMagicLink"].split("token=")[1]

    verify_res = session.get(f"/api/v1/auth/email/verify?token={token}&returnTo=/account", follow_redirects=False)
    assert verify_res.status_code == 303
    assert "session_token" in session.cookies

    me = session.get("/api/v1/auth/me").json()
    assert me["email"] == email
    assert "email" in me["identities"]

    assert session.get("/api/v1/cart").json()["itemCount"] >= 2

    addr = session.post("/api/v1/addresses", json={
        "name": "Regression Buyer",
        "phone": "9988776655",
        "line1": "Plot 42, MG Road",
        "city": "Bengaluru",
        "state": "Karnataka",
        "postalCode": "560001",
        "country": "IN",
    })
    assert addr.status_code == 201
    address_id = addr.json()["id"]

    order_res = session.post("/api/v1/orders", json={
        "addressId": address_id,
        "paymentMethod": "UPI",
        "notes": "Regression test order",
    })
    assert order_res.status_code == 201
    order = order_res.json()
    order_id = order["id"]
    order_number = order["orderNumber"]
    assert order_number.startswith("CB-")
    assert order["status"] == "PENDING_PAYMENT"
    assert order["paymentStatus"] == "PENDING"
    assert order["totalAmount"] >= unit_price * 2

    assert session.get("/api/v1/cart").json()["items"] == []

    updated_variant = next(
        v for v in session.get(f"/api/v1/products/{slug}").json()["variants"] if v["id"] == variant_id
    )
    assert updated_variant["stockQuantity"] == initial_stock - 2

    intent_res = session.post("/api/v1/payments/intent", json={"orderId": order_id, "provider": "mock"})
    assert intent_res.status_code == 201
    intent = intent_res.json()
    payment_id = intent["paymentId"]
    provider_order_id = intent["providerOrderId"]
    assert provider_order_id.startswith("mock_order_")

    pay_verify = session.post("/api/v1/payments/verify", json={
        "paymentId": payment_id,
        "providerPaymentId": "pay_regression_success_001",
        "providerOrderId": provider_order_id,
        "providerSignature": "mock_sig_valid",
        "paymentMethodDetail": "UPI via Google Pay",
    })
    assert pay_verify.status_code == 200
    assert pay_verify.json()["status"] == "SUCCESS"

    order_paid = session.get(f"/api/v1/orders/{order_number}").json()
    assert order_paid["paymentStatus"] == "PAID"
    assert order_paid["status"] == "CONFIRMED"
    assert any("verified" in (h.get("note") or "").lower() for h in order_paid["statusHistory"])

    admin_session = TestClient(app)
    _login_admin(admin_session)

    proc_res = admin_session.patch(f"/api/v1/admin/orders/{order_number}/status",
        json={"status": "PROCESSING", "note": "Assigned to artisan workshop"})
    assert proc_res.status_code == 200
    assert proc_res.json()["status"] == "PROCESSING"

    ship_res = admin_session.patch(f"/api/v1/admin/orders/{order_number}/status",
        json={"status": "SHIPPED", "trackingNumber": "BLUEDART-REG-001",
              "courierName": "BlueDart Express", "note": "Dispatched from Bengaluru hub"})
    assert ship_res.status_code == 200
    shipped = ship_res.json()
    assert shipped["status"] == "SHIPPED"
    assert shipped["trackingNumber"] == "BLUEDART-REG-001"
    assert shipped["courierName"] == "BlueDart Express"

    track_res = session.get(f"/api/v1/orders/{order_number}/tracking")
    assert track_res.status_code == 200
    tracking = track_res.json()
    assert tracking["orderNumber"] == order_number
    timeline = tracking["timeline"]
    assert len(timeline) >= 3
    statuses = [t["status"] for t in timeline]
    assert "CONFIRMED" in statuses
    assert "PROCESSING" in statuses
    assert "SHIPPED" in statuses


def test_guest_checkout_cod_no_auth():
    """Guest can complete COD checkout without authentication (inline shipping address)."""
    session = TestClient(app)
    assert session.get("/api/v1/auth/me").status_code == 401

    slug, variant = _first_variant(session)
    session.post("/api/v1/cart/items", json={"product_variant_id": variant["id"], "quantity": 1})

    order_res = session.post("/api/v1/orders", json={
        "customerName": "Priya Guest",
        "customerEmail": "priya.guest@example.com",
        "customerPhone": "9123456789",
        "paymentMethod": "COD",
        "shippingAddress": {
            "name": "Priya Guest",
            "phone": "9123456789",
            "line1": "22 Gandhi Nagar",
            "city": "Jaipur",
            "state": "Rajasthan",
            "postalCode": "302001",
            "country": "IN",
        },
    })
    assert order_res.status_code == 201
    order = order_res.json()
    assert order["orderNumber"].startswith("CB-")
    assert order["paymentMethod"] == "COD"
    assert order["status"] in ("CONFIRMED", "PENDING_PAYMENT")


def test_google_login_cart_merge_checkout():
    """Google social sign-in merges guest cart and allows checkout."""
    session = TestClient(app)
    slug, variant = _first_variant(session)
    session.post("/api/v1/cart/items", json={"product_variant_id": variant["id"], "quantity": 1})
    assert "guest_cart_token" in session.cookies

    g_res = session.post("/api/v1/auth/google", json={
        "credential": "mock_google_regression_checkout",
        "email": "google.checkout.regression@example.com",
        "name": "Google Regression Buyer",
        "sub": "google_sub_regression_checkout",
    })
    assert g_res.status_code == 200
    assert "session_token" in session.cookies
    assert "google" in g_res.json()["user"]["identities"]
    assert session.get("/api/v1/cart").json()["itemCount"] >= 1

    order_res = session.post("/api/v1/orders", json={
        "paymentMethod": "COD",
        "shippingAddress": {
            "name": "Google Regression Buyer",
            "phone": "9000000001",
            "line1": "Block A, Koramangala",
            "city": "Bengaluru",
            "state": "Karnataka",
            "postalCode": "560034",
            "country": "IN",
        },
    })
    assert order_res.status_code == 201
    assert order_res.json()["orderNumber"].startswith("CB-")


def test_phone_otp_endpoints_removed():
    """Legacy phone OTP routes must return 404 in V1."""
    tc = TestClient(app)
    assert tc.post("/api/v1/auth/phone/send-otp", json={"phone": "9999999999"}).status_code == 404
    assert tc.post("/api/v1/auth/phone/verify-otp", json={"phone": "9999999999", "otp": "123456"}).status_code == 404


def test_admin_order_routes_require_admin_role():
    """Admin order endpoints must reject unauthenticated and non-admin requests."""
    assert TestClient(app).get("/api/v1/admin/orders").status_code == 401

    customer = TestClient(app)
    customer.post("/api/v1/auth/google", json={
        "credential": "mock_customer_rbac_regression",
        "email": "rbac.customer.regression@example.com",
        "name": "RBAC Customer",
        "sub": "sub_rbac_regression",
    })
    res = customer.get("/api/v1/admin/orders")
    assert res.status_code == 403
    assert "Admin" in res.json().get("detail", "")


def test_magic_link_single_use_enforcement():
    """Magic link token consumed atomically on first use; second use must fail."""
    session = TestClient(app)
    start = session.post("/api/v1/auth/email/start", json={"email": "singleuse.regression@example.com"})
    assert start.status_code == 202
    token = start.json()["devMagicLink"].split("token=")[1]

    r1 = session.get(f"/api/v1/auth/email/verify?token={token}", follow_redirects=False)
    assert r1.status_code == 303
    assert "error" not in r1.headers["location"]

    r2 = TestClient(app).get(f"/api/v1/auth/email/verify?token={token}", follow_redirects=False)
    assert r2.status_code == 303
    assert "error=invalid_link" in r2.headers["location"]
