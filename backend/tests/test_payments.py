"""Integration tests for Payments Abstraction and Gateway Flow conforming to Milestone 7."""

import hashlib
import hmac
import json
from unittest.mock import MagicMock, patch

import httpx
from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app
from app.models.payment import Payment
from app.services.payment.razorpay import RazorpayPaymentProvider

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


def _mock_razorpay_post(mock_response_or_exc):
    mock_ctx = MagicMock()
    mock_client = MagicMock()
    mock_ctx.__enter__.return_value = mock_client
    mock_ctx.__exit__.return_value = None
    if isinstance(mock_response_or_exc, Exception):
        mock_client.post.side_effect = mock_response_or_exc
    else:
        mock_client.post.return_value = mock_response_or_exc
    return patch("app.services.payment.razorpay.httpx.Client", return_value=mock_ctx)


def test_7_2_1_tc01_security_razorpay_fail_closed():
    """TC01: Razorpay gateway boundary fails closed on missing secrets, bad signatures, or order mismatch."""
    cookies = _login_test_user("9999977031")
    order = _create_test_order(cookies, payment_method="UPI")

    # 1. Intent creation fails closed (HTTP 502) when credentials missing
    with patch.object(settings, "razorpay_key_id", None), patch.object(settings, "razorpay_key_secret", None):
        res = client.post(
            "/api/v1/payments/intent",
            json={"orderId": order["id"], "provider": "razorpay"},
            cookies=cookies,
        )
        assert res.status_code == 502
        assert "Payment gateway error" in res.json()["detail"]

    # Order remains PENDING_PAYMENT
    chk = client.get(f"/api/v1/orders/{order['id']}", cookies=cookies)
    assert chk.json()["status"] == "PENDING_PAYMENT"
    assert chk.json()["paymentStatus"] == "PENDING"

    # 2. Create valid intent with mocked gateway response
    mock_order_resp = httpx.Response(
        200,
        json={
            "id": "order_rzp_sec_test",
            "entity": "order",
            "amount": order["totalAmountPaise"],
            "currency": "INR",
            "status": "created",
        },
        request=httpx.Request("POST", "https://api.razorpay.com/v1/orders"),
    )
    with patch.object(settings, "razorpay_key_id", "rzp_test_k"), \
         patch.object(settings, "razorpay_key_secret", "rzp_test_sec"), \
         _mock_razorpay_post(mock_order_resp):
        intent_res = client.post(
            "/api/v1/payments/intent",
            json={"orderId": order["id"], "provider": "razorpay"},
            cookies=cookies,
        )
        assert intent_res.status_code == 201
        intent = intent_res.json()
        payment_id = intent["paymentId"]

    # 3. Verification fails closed if key_secret missing on server
    with patch.object(settings, "razorpay_key_secret", None):
        verify_fail_no_secret = client.post(
            "/api/v1/payments/verify",
            json={
                "paymentId": payment_id,
                "providerPaymentId": "pay_sec_123",
                "providerOrderId": "order_rzp_sec_test",
                "providerSignature": "any_sig",
            },
            cookies=cookies,
        )
        assert verify_fail_no_secret.status_code == 400

    # 4. Verification fails with tampered HMAC signature
    with patch.object(settings, "razorpay_key_secret", "rzp_test_sec"):
        verify_fail_bad_sig = client.post(
            "/api/v1/payments/verify",
            json={
                "paymentId": payment_id,
                "providerPaymentId": "pay_sec_123",
                "providerOrderId": "order_rzp_sec_test",
                "providerSignature": "0000000000000000000000000000000000000000000000000000000000000000",
            },
            cookies=cookies,
        )
        assert verify_fail_bad_sig.status_code == 400
        assert "Payment verification failed" in verify_fail_bad_sig.json()["detail"]

    # Payment record is marked FAILED and order is not confirmed
    pay_status = client.get(f"/api/v1/payments/{payment_id}", cookies=cookies).json()
    assert pay_status["status"] == "FAILED"
    order_status = client.get(f"/api/v1/orders/{order['id']}", cookies=cookies).json()
    assert order_status["status"] == "PENDING_PAYMENT"

    # 5. Order binding mismatch fails closed
    order2 = _create_test_order(cookies, payment_method="CARD")
    with patch.object(settings, "razorpay_key_id", "rzp_test_k"), \
         patch.object(settings, "razorpay_key_secret", "rzp_test_sec"), \
         _mock_razorpay_post(mock_order_resp):
        intent2 = client.post(
            "/api/v1/payments/intent",
            json={"orderId": order2["id"], "provider": "razorpay"},
            cookies=cookies,
        ).json()

    with patch.object(settings, "razorpay_key_secret", "rzp_test_sec"):
        mismatch_res = client.post(
            "/api/v1/payments/verify",
            json={
                "paymentId": intent2["paymentId"],
                "providerPaymentId": "pay_sec_999",
                "providerOrderId": "order_foreign_mismatch",
                "providerSignature": "irrelevant_sig",
            },
            cookies=cookies,
        )
        assert mismatch_res.status_code == 400
        assert "Mismatched order binding" in mismatch_res.json()["detail"]

    # 6. Webhook verification fails closed if missing webhook secret or invalid signature
    with patch.object(settings, "razorpay_webhook_secret", None):
        wh_no_secret = client.post(
            "/api/v1/payments/webhook/razorpay",
            json={"event": "payment.captured"},
            headers={"x-razorpay-signature": "some_sig"},
        )
        assert wh_no_secret.status_code == 400

    with patch.object(settings, "razorpay_webhook_secret", "whsec_live_123"):
        wh_bad_sig = client.post(
            "/api/v1/payments/webhook/razorpay",
            json={"event": "payment.captured"},
            headers={"x-razorpay-signature": "bad_signature"},
        )
        assert wh_bad_sig.status_code == 400


def test_7_2_1_tc02_acceptance_mocked_http_boundary():
    """TC02: Real Razorpay HTTP boundary mock creates order and validates HMAC-SHA256 signature."""
    cookies = _login_test_user("9999977032")
    order = _create_test_order(cookies, payment_method="UPI")

    mock_rzp_order_id = "order_rzp_acceptance_001"
    mock_rzp_payment_id = "pay_rzp_acceptance_002"
    test_key_id = "rzp_live_key_xyz"
    test_secret = "super_secret_signing_key_456"

    mock_resp = httpx.Response(
        200,
        json={
            "id": mock_rzp_order_id,
            "entity": "order",
            "amount": order["totalAmountPaise"],
            "currency": "INR",
            "status": "created",
        },
        request=httpx.Request("POST", "https://api.razorpay.com/v1/orders"),
    )

    # 1. Intent creation posts to Razorpay orders API
    with patch.object(settings, "razorpay_key_id", test_key_id), \
         patch.object(settings, "razorpay_key_secret", test_secret), \
         _mock_razorpay_post(mock_resp) as mock_post:
        intent_res = client.post(
            "/api/v1/payments/intent",
            json={"orderId": order["id"], "provider": "razorpay"},
            cookies=cookies,
        )
        assert intent_res.status_code == 201
        intent = intent_res.json()
        assert intent["providerOrderId"] == mock_rzp_order_id
        assert intent["keyId"] == test_key_id

    # 2. Cryptographic signature calculation
    msg = f"{mock_rzp_order_id}|{mock_rzp_payment_id}".encode("utf-8")
    valid_sig = hmac.new(test_secret.encode("utf-8"), msg, hashlib.sha256).hexdigest()

    # 3. Client verify callback with valid HMAC signature
    with patch.object(settings, "razorpay_key_secret", test_secret):
        verify_res = client.post(
            "/api/v1/payments/verify",
            json={
                "paymentId": intent["paymentId"],
                "providerPaymentId": mock_rzp_payment_id,
                "providerOrderId": mock_rzp_order_id,
                "providerSignature": valid_sig,
                "paymentMethodDetail": "Razorpay Netbanking (HDFC)",
            },
            cookies=cookies,
        )
        assert verify_res.status_code == 200
        verified_payment = verify_res.json()
        assert verified_payment["status"] == "SUCCESS"
        assert verified_payment["providerPaymentId"] == mock_rzp_payment_id
        assert verified_payment["providerOrderId"] == mock_rzp_order_id

    # 4. Verify Order transitions to PAID / CONFIRMED
    chk_order = client.get(f"/api/v1/orders/{order['id']}", cookies=cookies).json()
    assert chk_order["paymentStatus"] == "PAID"
    assert chk_order["status"] == "CONFIRMED"
    assert any("verified via RAZORPAY" in h["note"] for h in chk_order["statusHistory"])


def test_7_2_1_tc03_regression_idempotency():
    """TC03: Verifies idempotency of verify callback and webhook without duplicating side effects."""
    cookies = _login_test_user("9999977033")
    order = _create_test_order(cookies, payment_method="CARD")

    rzp_order_id = "order_rzp_idemp_001"
    rzp_payment_id = "pay_rzp_idemp_002"
    secret = "idempotency_secret_key_789"

    mock_resp = httpx.Response(
        200,
        json={"id": rzp_order_id, "amount": order["totalAmountPaise"], "currency": "INR", "status": "created"},
        request=httpx.Request("POST", "https://api.razorpay.com/v1/orders"),
    )
    with patch.object(settings, "razorpay_key_id", "rzp_k"), \
         patch.object(settings, "razorpay_key_secret", secret), \
         _mock_razorpay_post(mock_resp):
        intent = client.post(
            "/api/v1/payments/intent",
            json={"orderId": order["id"], "provider": "razorpay"},
            cookies=cookies,
        ).json()

    valid_sig = hmac.new(
        secret.encode("utf-8"),
        f"{rzp_order_id}|{rzp_payment_id}".encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    # First verify: succeeds
    with patch.object(settings, "razorpay_key_secret", secret):
        res1 = client.post(
            "/api/v1/payments/verify",
            json={
                "paymentId": intent["paymentId"],
                "providerPaymentId": rzp_payment_id,
                "providerOrderId": rzp_order_id,
                "providerSignature": valid_sig,
            },
            cookies=cookies,
        )
        assert res1.status_code == 200

    order_after_first = client.get(f"/api/v1/orders/{order['id']}", cookies=cookies).json()
    history_len = len(order_after_first["statusHistory"])

    # Duplicate verify call: returns 200 idempotently without extra history
    with patch.object(settings, "razorpay_key_secret", secret):
        res2 = client.post(
            "/api/v1/payments/verify",
            json={
                "paymentId": intent["paymentId"],
                "providerPaymentId": rzp_payment_id,
                "providerOrderId": rzp_order_id,
                "providerSignature": valid_sig,
            },
            cookies=cookies,
        )
        assert res2.status_code == 200

    order_after_second = client.get(f"/api/v1/orders/{order['id']}", cookies=cookies).json()
    assert len(order_after_second["statusHistory"]) == history_len

    # Duplicate webhook call: returns 200 without duplicate history
    webhook_secret = "wh_secret_idemp_xyz"
    raw_payload = json.dumps({
        "event": "payment.captured",
        "payload": {
            "payment": {
                "entity": {
                    "id": rzp_payment_id,
                    "order_id": rzp_order_id,
                    "status": "captured",
                }
            }
        }
    }).encode("utf-8")
    wh_sig = hmac.new(webhook_secret.encode("utf-8"), raw_payload, hashlib.sha256).hexdigest()

    with patch.object(settings, "razorpay_webhook_secret", webhook_secret):
        wh_res = client.post(
            "/api/v1/payments/webhook/razorpay",
            content=raw_payload,
            headers={"x-razorpay-signature": wh_sig, "content-type": "application/json"},
        )
        assert wh_res.status_code == 200
        assert wh_res.json()["status"] == "ok"

    order_after_webhook = client.get(f"/api/v1/orders/{order['id']}", cookies=cookies).json()
    assert len(order_after_webhook["statusHistory"]) == history_len


def test_7_2_1_tc04_resilience_gateway_failure():
    """TC04: Gateway timeouts, 500 errors, and refund failures are caught and mapped cleanly."""
    cookies = _login_test_user("9999977034")
    order = _create_test_order(cookies, payment_method="UPI")

    # 1. Gateway network timeout during intent creation
    with patch.object(settings, "razorpay_key_id", "rzp_k"), \
         patch.object(settings, "razorpay_key_secret", "rzp_s"), \
         _mock_razorpay_post(httpx.ConnectTimeout("Network timed out")):
        res_timeout = client.post(
            "/api/v1/payments/intent",
            json={"orderId": order["id"], "provider": "razorpay"},
            cookies=cookies,
        )
        assert res_timeout.status_code == 502
        assert "Payment gateway error" in res_timeout.json()["detail"]

    # 2. Gateway 500 error during intent creation
    err_500 = httpx.Response(500, text="Internal Server Error", request=httpx.Request("POST", "http://test"))
    with patch.object(settings, "razorpay_key_id", "rzp_k"), \
         patch.object(settings, "razorpay_key_secret", "rzp_s"), \
         _mock_razorpay_post(err_500):
        res_500 = client.post(
            "/api/v1/payments/intent",
            json={"orderId": order["id"], "provider": "razorpay"},
            cookies=cookies,
        )
        assert res_500.status_code == 502
        assert "Payment gateway error" in res_500.json()["detail"]

    # Order remains untouched
    order_chk = client.get(f"/api/v1/orders/{order['id']}", cookies=cookies).json()
    assert order_chk["status"] == "PENDING_PAYMENT"

    # 3. Provider refund resilience (direct provider check)
    provider = RazorpayPaymentProvider(key_id="rzp_k", key_secret="rzp_s")
    dummy_payment = Payment(id=999, provider_payment_id="pay_fail_test", amount=500)

    # 3a: Missing payment ID fails closed
    dummy_no_id = Payment(id=998, provider_payment_id=None, amount=500)
    refund_no_id = provider.refund_payment(dummy_no_id, 500)
    assert refund_no_id["success"] is False

    # 3b: Gateway refund error (e.g., 400 Bad Request) fails closed
    ref_err_resp = httpx.Response(400, json={"error": {"description": "Payment already refunded"}}, request=httpx.Request("POST", "http://test"))
    with _mock_razorpay_post(ref_err_resp):
        refund_err = provider.refund_payment(dummy_payment, 500)
        assert refund_err["success"] is False
        assert "Payment already refunded" in refund_err["error"]

    # 3c: Network error during refund fails closed
    with _mock_razorpay_post(httpx.ReadTimeout("Read timeout")):
        refund_timeout = provider.refund_payment(dummy_payment, 500)
        assert refund_timeout["success"] is False
        assert "Failed to reach Razorpay" in refund_timeout["error"]


def test_7_2_1_tc05_cross_user_authorization():
    """TC05: User 2 cannot verify or inspect User 1's payment."""
    user1_cookies = _login_test_user("9999977035")
    user2_cookies = _login_test_user("9999977036")

    order = _create_test_order(user1_cookies, payment_method="UPI")
    intent = client.post(
        "/api/v1/payments/intent",
        json={"orderId": order["id"]},
        cookies=user1_cookies,
    ).json()

    payment_id = intent["paymentId"]

    # User 2 attempts to verify User 1's payment
    forbidden_verify = client.post(
        "/api/v1/payments/verify",
        json={
            "paymentId": payment_id,
            "providerPaymentId": "pay_mock_unauth",
            "providerOrderId": intent["providerOrderId"],
            "providerSignature": "mock_sig_valid",
        },
        cookies=user2_cookies,
    )
    assert forbidden_verify.status_code == 404

    # User 2 attempts to retrieve User 1's payment
    forbidden_get = client.get(f"/api/v1/payments/{payment_id}", cookies=user2_cookies)
    assert forbidden_get.status_code == 404


def test_7_2_1_tc06_mock_provider_compatibility():
    """TC06: Mock payment provider remains fully functional for offline development and testing."""
    cookies = _login_test_user("9999977037")
    order = _create_test_order(cookies, payment_method="UPI")

    # 1. Intent with provider="mock"
    intent_res = client.post(
        "/api/v1/payments/intent",
        json={"orderId": order["id"], "provider": "mock"},
        cookies=cookies,
    )
    assert intent_res.status_code == 201
    intent = intent_res.json()
    assert intent["provider"] == "mock"
    assert intent["providerOrderId"].startswith("mock_order_")

    # 2. Verify with mock signature
    verify_res = client.post(
        "/api/v1/payments/verify",
        json={
            "paymentId": intent["paymentId"],
            "providerPaymentId": "pay_mock_comp_123",
            "providerOrderId": intent["providerOrderId"],
            "providerSignature": "mock_sig_valid",
            "paymentMethodDetail": "Mock UPI (buyer@okmock)",
        },
        cookies=cookies,
    )
    assert verify_res.status_code == 200
    assert verify_res.json()["status"] == "SUCCESS"

    # 3. Order is confirmed
    order_chk = client.get(f"/api/v1/orders/{order['id']}", cookies=cookies).json()
    assert order_chk["status"] == "CONFIRMED"
    assert order_chk["paymentStatus"] == "PAID"
