"""Integration tests for Payments Abstraction and Gateway Flow conforming to Milestone 7."""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def _login_test_user(phone: str = "9999977001") -> dict[str, str]:
    """Helper to authenticate and return session cookies."""
    email = f"user_{phone}@example.com"
    res = client.post("/api/v1/auth/google", json={
        "credential": f"mock_token_{phone}",
        "email": email,
        "name": "Test Customer",
        "sub": f"sub_{phone}",
    })
    assert res.status_code == 200
    return dict(res.cookies)


def _create_test_order(cookies: dict[str, str], payment_method: str = "UPI") -> dict:
    """Helper to create an order in PENDING_PAYMENT status."""
    client.post(
        "/api/v1/cart/items",
        json={"product_id": 1, "quantity": 1},
        cookies=cookies,
    )
    order_res = client.post(
        "/api/v1/orders",
        json={
            "shippingAddress": {
                "name": "Dev Buyer",
                "phone": "9999977001",
                "line1": "Indiranagar 100ft Road",
                "city": "Bengaluru",
                "state": "Karnataka",
                "postalCode": "560038",
            },
            "paymentMethod": payment_method,
        },
        cookies=cookies,
    )
    assert order_res.status_code == 201
    return order_res.json()


def test_payment_intent_creation():
    """Verify creating a payment intent for an order in PENDING_PAYMENT status."""
    cookies = _login_test_user("9999977001")
    order = _create_test_order(cookies, payment_method="UPI")

    assert order["status"] == "PENDING_PAYMENT"
    assert order["paymentStatus"] == "PENDING"
    order_id = order["id"]
    order_number = order["orderNumber"]

    # 1. Create payment intent using orderId
    intent_res = client.post(
        "/api/v1/payments/intent",
        json={"orderId": order_id, "provider": "mock"},
        cookies=cookies,
    )
    assert intent_res.status_code == 201
    intent = intent_res.json()

    assert intent["orderId"] == order_id
    assert intent["orderNumber"] == order_number
    assert intent["provider"] == "mock"
    assert intent["providerOrderId"].startswith("mock_order_")
    assert intent["amount"] == order["totalAmount"]
    assert intent["amountPaise"] == order["totalAmountPaise"]
    assert intent["currency"] == "INR"
    assert intent["keyId"] is not None


def test_payment_verification_success():
    """Verify successful client payment callback transitions order to PAID and CONFIRMED."""
    cookies = _login_test_user("9999977002")
    order = _create_test_order(cookies, payment_method="CARD")

    # 1. Create intent
    intent_res = client.post(
        "/api/v1/payments/intent",
        json={"orderNumber": order["orderNumber"]},
        cookies=cookies,
    )
    assert intent_res.status_code == 201
    intent = intent_res.json()
    payment_id = intent["paymentId"]
    mock_order_id = intent["providerOrderId"]

    # 2. Verify payment callback
    verify_res = client.post(
        "/api/v1/payments/verify",
        json={
            "paymentId": payment_id,
            "providerPaymentId": "pay_mock_success_123",
            "providerOrderId": mock_order_id,
            "providerSignature": "mock_sig_valid",
            "paymentMethodDetail": "Visa ending in 4242",
        },
        cookies=cookies,
    )
    assert verify_res.status_code == 200
    payment_out = verify_res.json()
    assert payment_out["status"] == "SUCCESS"
    assert payment_out["providerPaymentId"] == "pay_mock_success_123"
    assert payment_out["paymentMethodDetail"] == "Visa ending in 4242"

    # 3. Check Order has transitioned to PAID / CONFIRMED
    order_res = client.get(f"/api/v1/orders/{order['orderNumber']}", cookies=cookies)
    assert order_res.status_code == 200
    updated_order = order_res.json()
    assert updated_order["paymentStatus"] == "PAID"
    assert updated_order["status"] == "CONFIRMED"

    # 4. Check Order status history has payment entry
    history = updated_order["statusHistory"]
    assert len(history) >= 2
    assert "verified via MOCK" in history[-1]["note"]


def test_payment_verification_failure():
    """Verify failed payment callback marks payment as FAILED and leaves order pending."""
    cookies = _login_test_user("9999977003")
    order = _create_test_order(cookies, payment_method="NETBANKING")

    intent_res = client.post(
        "/api/v1/payments/intent",
        json={"orderId": order["id"]},
        cookies=cookies,
    )
    intent = intent_res.json()

    # Fail provider payment
    fail_res = client.post(
        "/api/v1/payments/verify",
        json={
            "paymentId": intent["paymentId"],
            "providerPaymentId": "fail_mock_insufficient_funds",
        },
        cookies=cookies,
    )
    assert fail_res.status_code == 400

    # Inspect payment status
    payment_res = client.get(f"/api/v1/payments/{intent['paymentId']}", cookies=cookies)
    assert payment_res.status_code == 200
    assert payment_res.json()["status"] == "FAILED"

    # Order remains PENDING_PAYMENT
    order_res = client.get(f"/api/v1/orders/{order['id']}", cookies=cookies)
    assert order_res.json()["paymentStatus"] == "PENDING"
    assert order_res.json()["status"] == "PENDING_PAYMENT"


def test_payment_webhook():
    """Verify asynchronous gateway webhook updates payment and order status."""
    cookies = _login_test_user("9999977004")
    order = _create_test_order(cookies, payment_method="UPI")

    intent_res = client.post(
        "/api/v1/payments/intent",
        json={"orderId": order["id"]},
        cookies=cookies,
    )
    intent = intent_res.json()
    provider_order_id = intent["providerOrderId"]

    # Send webhook with valid signature
    webhook_res = client.post(
        "/api/v1/payments/webhook/mock",
        json={
            "event": "payment.captured",
            "provider_order_id": provider_order_id,
            "provider_payment_id": "pay_webhook_captured_999",
        },
        headers={"x-signature": "valid_mock_signature"},
    )
    assert webhook_res.status_code == 200
    assert webhook_res.json()["status"] == "ok"

    # Order should now be PAID
    order_res = client.get(f"/api/v1/orders/{order['id']}", cookies=cookies)
    assert order_res.json()["paymentStatus"] == "PAID"
    assert order_res.json()["status"] == "CONFIRMED"


def test_payment_security_authorization():
    """Verify user cannot initiate or inspect payment for another user's order."""
    user1_cookies = _login_test_user("9999977010")
    user2_cookies = _login_test_user("9999977020")

    order = _create_test_order(user1_cookies, payment_method="UPI")

    # User 2 attempts to create intent on User 1's order -> 404
    forbidden_intent = client.post(
        "/api/v1/payments/intent",
        json={"orderId": order["id"]},
        cookies=user2_cookies,
    )
    assert forbidden_intent.status_code == 404
