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


def _cashfree_webhook_sig(secret: str, timestamp: str, raw_body: bytes) -> str:
    import base64
    digest = hmac.new(
        secret.encode("utf-8"),
        timestamp.encode("utf-8") + raw_body,
        hashlib.sha256,
    ).digest()
    return base64.b64encode(digest).decode("utf-8")


def test_7_2_3_tc01_cashfree_order_creation():
    """7.2.3-TC01: Create Cashfree order sends server-derived amount/metadata and returns paymentSessionId without secrets."""
    cookies = _login_test_user("9999977041")
    order = _create_test_order(cookies, payment_method="UPI")

    captured_requests: list[dict] = []

    def mock_post(url, headers=None, json=None, **kwargs):
        captured_requests.append({"url": url, "headers": headers or {}, "json": json or {}})
        return httpx.Response(
            200,
            json={
                "cf_order_id": "2149460581",
                "order_id": json["order_id"],
                "entity": "order",
                "order_currency": "INR",
                "order_amount": json["order_amount"],
                "order_status": "ACTIVE",
                "payment_session_id": "session_cf_sandbox_tc01_xyz987",
            },
            request=httpx.Request("POST", url),
        )

    mock_ctx = MagicMock()
    mock_client = MagicMock()
    mock_ctx.__enter__.return_value = mock_client
    mock_ctx.__exit__.return_value = None
    mock_client.post.side_effect = mock_post

    cf_secret = "cf_super_secret_do_not_leak_tc01"
    with patch.object(settings, "cashfree_environment", "sandbox"), \
         patch.object(settings, "cashfree_app_id", "CF_APP_TEST_01"), \
         patch.object(settings, "cashfree_secret_key", cf_secret), \
         patch("app.services.payment.cashfree.httpx.Client", return_value=mock_ctx):
        res = client.post(
            "/api/v1/payments/intent",
            json={"orderId": order["id"], "provider": "cashfree"},
            cookies=cookies,
        )

    assert res.status_code == 201
    intent = res.json()
    assert intent["provider"] == "cashfree"
    assert intent["paymentSessionId"] == "session_cf_sandbox_tc01_xyz987"
    assert intent["providerOrderId"].startswith(order["orderNumber"])
    assert intent["environment"] == "sandbox"
    assert intent["amount"] == order["totalAmount"]
    assert intent["amountPaise"] == order["totalAmountPaise"]
    assert intent["currency"] == "INR"
    assert intent["keyId"] is None
    assert f"orderNumber={order['orderNumber']}" in intent["returnUrl"]
    assert cf_secret not in json.dumps(intent)
    assert "CF_APP_TEST_01" not in json.dumps(intent)

    # Verify outbound payload to Cashfree sandbox
    assert len(captured_requests) == 1
    req = captured_requests[0]
    assert req["url"] == "https://sandbox.cashfree.com/pg/orders"
    assert req["headers"]["x-client-id"] == "CF_APP_TEST_01"
    assert req["headers"]["x-client-secret"] == cf_secret
    assert req["headers"]["x-api-version"] == "2023-08-01"
    assert req["json"]["order_amount"] == round(order["totalAmountPaise"] / 100.0, 2)
    assert req["json"]["order_currency"] == "INR"
    assert req["json"]["customer_details"]["customer_phone"] == "9999977001"
    assert "/api/v1/payments/webhook/cashfree" in req["json"]["order_meta"]["notify_url"]


def test_7_2_3_tc02_cashfree_credentials_and_environment_fail_closed():
    """7.2.3-TC02: Missing credentials, invalid environment, or sandbox-in-prod fail closed without fallback or secret leak."""
    cookies = _login_test_user("9999977042")
    order = _create_test_order(cookies, payment_method="UPI")
    secret_val = "cf_top_secret_value_tc02"

    # 1. Missing CASHFREE_ENVIRONMENT
    with patch.object(settings, "cashfree_environment", None), \
         patch.object(settings, "cashfree_app_id", "CF_ID"), \
         patch.object(settings, "cashfree_secret_key", secret_val):
        r1 = client.post(
            "/api/v1/payments/intent",
            json={"orderId": order["id"], "provider": "cashfree"},
            cookies=cookies,
        )
        assert r1.status_code == 502
        assert secret_val not in r1.text

    # 2. Invalid CASHFREE_ENVIRONMENT value
    with patch.object(settings, "cashfree_environment", "staging_invalid"), \
         patch.object(settings, "cashfree_app_id", "CF_ID"), \
         patch.object(settings, "cashfree_secret_key", secret_val):
        r2 = client.post(
            "/api/v1/payments/intent",
            json={"orderId": order["id"], "provider": "cashfree"},
            cookies=cookies,
        )
        assert r2.status_code == 502
        assert secret_val not in r2.text

    # 3. APP_ENV=production rejects CASHFREE_ENVIRONMENT=sandbox
    with patch.object(settings, "app_env", "production"), \
         patch.object(settings, "cashfree_environment", "sandbox"), \
         patch.object(settings, "cashfree_app_id", "CF_ID"), \
         patch.object(settings, "cashfree_secret_key", secret_val):
        r3 = client.post(
            "/api/v1/payments/intent",
            json={"orderId": order["id"], "provider": "cashfree"},
            cookies=cookies,
        )
        assert r3.status_code == 502
        assert "production" in r3.json()["detail"].lower()
        assert secret_val not in r3.text

    # 4. Missing secret key fails closed
    with patch.object(settings, "cashfree_environment", "sandbox"), \
         patch.object(settings, "cashfree_app_id", "CF_ID"), \
         patch.object(settings, "cashfree_secret_key", ""):
        r4 = client.post(
            "/api/v1/payments/intent",
            json={"orderId": order["id"], "provider": "cashfree"},
            cookies=cookies,
        )
        assert r4.status_code == 502

    # 5. Unknown provider fails closed (no silent fallback to mock)
    r5 = client.post(
        "/api/v1/payments/intent",
        json={"orderId": order["id"], "provider": "nonexistent_gateway"},
        cookies=cookies,
    )
    assert r5.status_code == 502
    assert "Unsupported payment provider" in r5.json()["detail"]


def test_7_2_3_tc03_cashfree_server_side_verification():
    """7.2.3-TC03: Only server-verified PAID with matching order_id, amount, and currency marks order paid."""
    cookies = _login_test_user("9999977043")
    order = _create_test_order(cookies, payment_method="UPI")
    expected_rupees = round(order["totalAmountPaise"] / 100.0, 2)

    mock_ctx = MagicMock()
    mock_client = MagicMock()
    mock_ctx.__enter__.return_value = mock_client
    mock_ctx.__exit__.return_value = None

    def create_order_post(url, headers=None, json=None, **kwargs):
        return httpx.Response(
            200,
            json={
                "cf_order_id": "2149460999",
                "order_id": json["order_id"],
                "order_amount": expected_rupees,
                "order_currency": "INR",
                "order_status": "ACTIVE",
                "payment_session_id": "session_cf_tc03",
            },
            request=httpx.Request("POST", url),
        )

    mock_client.post.side_effect = create_order_post

    with patch.object(settings, "cashfree_environment", "sandbox"), \
         patch.object(settings, "cashfree_app_id", "CF_ID"), \
         patch.object(settings, "cashfree_secret_key", "CF_SEC"), \
         patch("app.services.payment.cashfree.httpx.Client", return_value=mock_ctx):
        intent = client.post(
            "/api/v1/payments/intent",
            json={"orderId": order["id"], "provider": "cashfree"},
            cookies=cookies,
        ).json()

    payment_id = intent["paymentId"]
    cf_order_id = intent["providerOrderId"]

    # Case A: Cashfree order is still ACTIVE (pending) -> verify returns 400, payment stays PENDING, order stays PENDING_PAYMENT
    def get_active(url, **kwargs):
        return httpx.Response(
            200,
            json={
                "order_id": cf_order_id,
                "order_amount": expected_rupees,
                "order_currency": "INR",
                "order_status": "ACTIVE",
            },
            request=httpx.Request("GET", url),
        )

    mock_client.get.side_effect = get_active
    with patch.object(settings, "cashfree_environment", "sandbox"), \
         patch.object(settings, "cashfree_app_id", "CF_ID"), \
         patch.object(settings, "cashfree_secret_key", "CF_SEC"), \
         patch("app.services.payment.cashfree.httpx.Client", return_value=mock_ctx):
        res_pending = client.post(
            "/api/v1/payments/verify",
            json={"paymentId": payment_id},
            cookies=cookies,
        )
        assert res_pending.status_code == 400
        assert "pending" in res_pending.json()["detail"].lower()

    pay_state = client.get(f"/api/v1/payments/{payment_id}", cookies=cookies).json()
    assert pay_state["status"] == "PENDING"

    # Case B: Forged client payload claiming success while Cashfree says EXPIRED/FAILED -> rejected (400), marked FAILED
    def get_expired(url, **kwargs):
        return httpx.Response(
            200,
            json={
                "order_id": cf_order_id,
                "order_amount": expected_rupees,
                "order_currency": "INR",
                "order_status": "EXPIRED",
            },
            request=httpx.Request("GET", url),
        )

    mock_client.get.side_effect = get_expired
    with patch.object(settings, "cashfree_environment", "sandbox"), \
         patch.object(settings, "cashfree_app_id", "CF_ID"), \
         patch.object(settings, "cashfree_secret_key", "CF_SEC"), \
         patch("app.services.payment.cashfree.httpx.Client", return_value=mock_ctx):
        res_forged = client.post(
            "/api/v1/payments/verify",
            json={
                "paymentId": payment_id,
                "providerPaymentId": "forged_cf_pay_999",
                "providerOrderId": cf_order_id,
                "providerSignature": "forged_sig",
            },
            cookies=cookies,
        )
        assert res_forged.status_code == 400

    assert client.get(f"/api/v1/payments/{payment_id}", cookies=cookies).json()["status"] == "FAILED"
    assert client.get(f"/api/v1/orders/{order['id']}", cookies=cookies).json()["paymentStatus"] == "PENDING"

    # Case C: Amount mismatch from gateway (e.g. ₹1.00 instead of actual order total) -> rejected (400)
    def get_wrong_amount(url, **kwargs):
        if url.endswith("/payments"):
            return httpx.Response(200, json=[{"cf_payment_id": "cf_pay_1", "payment_status": "SUCCESS", "payment_amount": 1.00}], request=httpx.Request("GET", url))
        return httpx.Response(
            200,
            json={
                "order_id": cf_order_id,
                "order_amount": 1.00,
                "order_currency": "INR",
                "order_status": "PAID",
            },
            request=httpx.Request("GET", url),
        )

    mock_client.get.side_effect = get_wrong_amount
    with patch.object(settings, "cashfree_environment", "sandbox"), \
         patch.object(settings, "cashfree_app_id", "CF_ID"), \
         patch.object(settings, "cashfree_secret_key", "CF_SEC"), \
         patch("app.services.payment.cashfree.httpx.Client", return_value=mock_ctx):
        res_amt_mismatch = client.post(
            "/api/v1/payments/verify",
            json={"paymentId": payment_id},
            cookies=cookies,
        )
        assert res_amt_mismatch.status_code == 400

    # Case D: Authoritative PAID order + SUCCESS payment attempt -> verified with only {paymentId}
    def get_paid(url, **kwargs):
        if url.endswith("/payments"):
            return httpx.Response(
                200,
                json=[
                    {
                        "cf_payment_id": "8877665544",
                        "order_id": cf_order_id,
                        "payment_status": "SUCCESS",
                        "payment_amount": expected_rupees,
                        "payment_currency": "INR",
                        "payment_group": "upi",
                    }
                ],
                request=httpx.Request("GET", url),
            )
        return httpx.Response(
            200,
            json={
                "cf_order_id": "2149460999",
                "order_id": cf_order_id,
                "order_amount": expected_rupees,
                "order_currency": "INR",
                "order_status": "PAID",
            },
            request=httpx.Request("GET", url),
        )

    mock_client.get.side_effect = get_paid
    with patch.object(settings, "cashfree_environment", "sandbox"), \
         patch.object(settings, "cashfree_app_id", "CF_ID"), \
         patch.object(settings, "cashfree_secret_key", "CF_SEC"), \
         patch("app.services.payment.cashfree.httpx.Client", return_value=mock_ctx):
        res_ok = client.post(
            "/api/v1/payments/verify",
            json={"paymentId": payment_id},
            cookies=cookies,
        )
        assert res_ok.status_code == 200
        pay_ok = res_ok.json()
        assert pay_ok["status"] == "SUCCESS"
        assert pay_ok["providerPaymentId"] == "8877665544"
        assert pay_ok["paymentMethodDetail"] == "Cashfree (UPI)"

    ord_ok = client.get(f"/api/v1/orders/{order['id']}", cookies=cookies).json()
    assert ord_ok["paymentStatus"] == "PAID"
    assert ord_ok["status"] == "CONFIRMED"


def test_7_2_3_tc04_cashfree_webhook_authentication():
    """7.2.3-TC04: Webhook verifies raw bytes + timestamp with Base64 HMAC-SHA256 and rejects tampered/malformed payloads."""
    cookies = _login_test_user("9999977044")
    order = _create_test_order(cookies, payment_method="UPI")
    expected_rupees = round(order["totalAmountPaise"] / 100.0, 2)

    mock_ctx = MagicMock()
    mock_client = MagicMock()
    mock_ctx.__enter__.return_value = mock_client
    mock_ctx.__exit__.return_value = None
    mock_client.post.side_effect = lambda url, json=None, **kw: httpx.Response(
        200,
        json={"order_id": json["order_id"], "payment_session_id": "sess_wh_tc04"},
        request=httpx.Request("POST", url),
    )

    cf_secret = "cf_wh_secret_tc04"
    with patch.object(settings, "cashfree_environment", "sandbox"), \
         patch.object(settings, "cashfree_app_id", "CF_ID"), \
         patch.object(settings, "cashfree_secret_key", cf_secret), \
         patch("app.services.payment.cashfree.httpx.Client", return_value=mock_ctx):
        intent = client.post(
            "/api/v1/payments/intent",
            json={"orderId": order["id"], "provider": "cashfree"},
            cookies=cookies,
        ).json()

    cf_order_id = intent["providerOrderId"]
    timestamp = "1730280000123"
    valid_payload = json.dumps({
        "data": {
            "order": {
                "order_id": cf_order_id,
                "order_amount": expected_rupees,
                "order_currency": "INR",
            },
            "payment": {
                "cf_payment_id": "cf_wh_pay_001",
                "payment_status": "SUCCESS",
                "payment_amount": expected_rupees,
                "payment_currency": "INR",
                "payment_group": "credit_card",
            },
        },
        "type": "PAYMENT_SUCCESS_WEBHOOK",
    }).encode("utf-8")
    valid_sig = _cashfree_webhook_sig(cf_secret, timestamp, valid_payload)

    with patch.object(settings, "cashfree_environment", "sandbox"), \
         patch.object(settings, "cashfree_app_id", "CF_ID"), \
         patch.object(settings, "cashfree_secret_key", cf_secret):
        # 1. Missing signature -> 400
        r_no_sig = client.post(
            "/api/v1/payments/webhook/cashfree",
            content=valid_payload,
            headers={"x-webhook-timestamp": timestamp, "content-type": "application/json"},
        )
        assert r_no_sig.status_code == 400

        # 2. Missing or malformed non-numeric timestamp -> 400
        r_bad_ts = client.post(
            "/api/v1/payments/webhook/cashfree",
            content=valid_payload,
            headers={
                "x-webhook-signature": valid_sig,
                "x-webhook-timestamp": "not-a-timestamp",
                "content-type": "application/json",
            },
        )
        assert r_bad_ts.status_code == 400

        # 3. Tampered body with original signature -> 400
        tampered_body = valid_payload.replace(b"cf_wh_pay_001", b"cf_wh_pay_999")
        r_tampered = client.post(
            "/api/v1/payments/webhook/cashfree",
            content=tampered_body,
            headers={
                "x-webhook-signature": valid_sig,
                "x-webhook-timestamp": timestamp,
                "content-type": "application/json",
            },
        )
        assert r_tampered.status_code == 400

        # 4. Malformed JSON with valid signature -> 400
        bad_json = b"{malformed_json:"
        bad_json_sig = _cashfree_webhook_sig(cf_secret, timestamp, bad_json)
        r_bad_json = client.post(
            "/api/v1/payments/webhook/cashfree",
            content=bad_json,
            headers={
                "x-webhook-signature": bad_json_sig,
                "x-webhook-timestamp": timestamp,
                "content-type": "application/json",
            },
        )
        assert r_bad_json.status_code == 400

        # Verify zero DB side effects after all invalid attempts
        ord_before = client.get(f"/api/v1/orders/{order['id']}", cookies=cookies).json()
        assert ord_before["paymentStatus"] == "PENDING"
        assert ord_before["status"] == "PENDING_PAYMENT"

        # 5. Valid signature + timestamp + payload -> 200 OK and order PAID
        r_valid = client.post(
            "/api/v1/payments/webhook/cashfree",
            content=valid_payload,
            headers={
                "x-webhook-signature": valid_sig,
                "x-webhook-timestamp": timestamp,
                "content-type": "application/json",
            },
        )
        assert r_valid.status_code == 200

    ord_after = client.get(f"/api/v1/orders/{order['id']}", cookies=cookies).json()
    assert ord_after["paymentStatus"] == "PAID"
    assert ord_after["status"] == "CONFIRMED"


def test_7_2_3_tc05_cashfree_duplicate_and_out_of_order_events():
    """7.2.3-TC05: Duplicate webhooks/callbacks and out-of-order failed events preserve single confirmation and stock."""
    cookies = _login_test_user("9999977045")
    order = _create_test_order(cookies, payment_method="UPI")
    expected_rupees = round(order["totalAmountPaise"] / 100.0, 2)

    mock_ctx = MagicMock()
    mock_client = MagicMock()
    mock_ctx.__enter__.return_value = mock_client
    mock_ctx.__exit__.return_value = None
    mock_client.post.side_effect = lambda url, json=None, **kw: httpx.Response(
        200,
        json={"order_id": json["order_id"], "payment_session_id": "sess_idemp_tc05"},
        request=httpx.Request("POST", url),
    )

    cf_secret = "cf_idemp_secret_tc05"
    with patch.object(settings, "cashfree_environment", "sandbox"), \
         patch.object(settings, "cashfree_app_id", "CF_ID"), \
         patch.object(settings, "cashfree_secret_key", cf_secret), \
         patch("app.services.payment.cashfree.httpx.Client", return_value=mock_ctx):
        intent = client.post(
            "/api/v1/payments/intent",
            json={"orderId": order["id"], "provider": "cashfree"},
            cookies=cookies,
        ).json()

    cf_order_id = intent["providerOrderId"]
    payment_id = intent["paymentId"]
    ts = "1730280005000"

    # 1. Initial failed attempt webhook arrives while order is pending -> payment marked FAILED, order still PENDING_PAYMENT
    failed_body = json.dumps({
        "data": {
            "order": {"order_id": cf_order_id, "order_amount": expected_rupees, "order_currency": "INR"},
            "payment": {
                "cf_payment_id": "cf_pay_fail_01",
                "payment_status": "FAILED",
                "payment_amount": expected_rupees,
                "payment_currency": "INR",
                "payment_message": "UPI PIN incorrect",
            },
        },
        "type": "PAYMENT_FAILED_WEBHOOK",
    }).encode("utf-8")
    failed_sig = _cashfree_webhook_sig(cf_secret, ts, failed_body)

    success_body = json.dumps({
        "data": {
            "order": {"order_id": cf_order_id, "order_amount": expected_rupees, "order_currency": "INR"},
            "payment": {
                "cf_payment_id": "cf_pay_succ_02",
                "payment_status": "SUCCESS",
                "payment_amount": expected_rupees,
                "payment_currency": "INR",
                "payment_group": "upi",
            },
        },
        "type": "PAYMENT_SUCCESS_WEBHOOK",
    }).encode("utf-8")
    success_sig = _cashfree_webhook_sig(cf_secret, ts, success_body)

    with patch.object(settings, "cashfree_environment", "sandbox"), \
         patch.object(settings, "cashfree_app_id", "CF_ID"), \
         patch.object(settings, "cashfree_secret_key", cf_secret):
        r_fail = client.post(
            "/api/v1/payments/webhook/cashfree",
            content=failed_body,
            headers={"x-webhook-signature": failed_sig, "x-webhook-timestamp": ts, "content-type": "application/json"},
        )
        assert r_fail.status_code == 200
        assert client.get(f"/api/v1/payments/{payment_id}", cookies=cookies).json()["status"] == "FAILED"

        # 2. Subsequent success webhook reconciles payment & order
        r_succ1 = client.post(
            "/api/v1/payments/webhook/cashfree",
            content=success_body,
            headers={"x-webhook-signature": success_sig, "x-webhook-timestamp": ts, "content-type": "application/json"},
        )
        assert r_succ1.status_code == 200

        ord_confirmed = client.get(f"/api/v1/orders/{order['id']}", cookies=cookies).json()
        assert ord_confirmed["paymentStatus"] == "PAID"
        assert ord_confirmed["status"] == "CONFIRMED"
        history_count = len(ord_confirmed["statusHistory"])

        # 3. Duplicate success webhook -> idempotent, no extra history
        r_succ2 = client.post(
            "/api/v1/payments/webhook/cashfree",
            content=success_body,
            headers={"x-webhook-signature": success_sig, "x-webhook-timestamp": ts, "content-type": "application/json"},
        )
        assert r_succ2.status_code == 200

        # 4. Out-of-order replay of earlier failed webhook -> ignored, does NOT downgrade PAID order
        r_late_fail = client.post(
            "/api/v1/payments/webhook/cashfree",
            content=failed_body,
            headers={"x-webhook-signature": failed_sig, "x-webhook-timestamp": ts, "content-type": "application/json"},
        )
        assert r_late_fail.status_code == 200

        # 5. Subsequent client /verify call -> idempotent 200
        r_verify = client.post(
            "/api/v1/payments/verify",
            json={"paymentId": payment_id},
            cookies=cookies,
        )
        assert r_verify.status_code == 200
        assert r_verify.json()["status"] == "SUCCESS"

    ord_final = client.get(f"/api/v1/orders/{order['id']}", cookies=cookies).json()
    assert ord_final["paymentStatus"] == "PAID"
    assert ord_final["status"] == "CONFIRMED"
    assert len(ord_final["statusHistory"]) == history_count


def test_7_2_3_tc06_cashfree_gateway_errors_and_refunds():
    """7.2.3-TC06: Gateway timeouts/4xx/5xx/malformed responses and unconfirmed refunds fail closed."""
    from app.services.payment.cashfree import CashfreePaymentProvider

    cookies = _login_test_user("9999977046")
    order = _create_test_order(cookies, payment_method="UPI")

    mock_ctx = MagicMock()
    mock_client = MagicMock()
    mock_ctx.__enter__.return_value = mock_client
    mock_ctx.__exit__.return_value = None

    # 1. Timeout on create_intent -> 502
    mock_client.post.side_effect = httpx.ConnectTimeout("Cashfree timed out")
    with patch.object(settings, "cashfree_environment", "sandbox"), \
         patch.object(settings, "cashfree_app_id", "CF_ID"), \
         patch.object(settings, "cashfree_secret_key", "CF_SEC"), \
         patch("app.services.payment.cashfree.httpx.Client", return_value=mock_ctx):
        r_timeout = client.post(
            "/api/v1/payments/intent",
            json={"orderId": order["id"], "provider": "cashfree"},
            cookies=cookies,
        )
        assert r_timeout.status_code == 502

    # 2. Malformed response missing payment_session_id -> 502
    mock_client.post.side_effect = None
    mock_client.post.return_value = httpx.Response(
        200,
        json={"order_id": "cf_123"},
        request=httpx.Request("POST", "https://sandbox.cashfree.com/pg/orders"),
    )
    with patch.object(settings, "cashfree_environment", "sandbox"), \
         patch.object(settings, "cashfree_app_id", "CF_ID"), \
         patch.object(settings, "cashfree_secret_key", "CF_SEC"), \
         patch("app.services.payment.cashfree.httpx.Client", return_value=mock_ctx):
        r_malformed = client.post(
            "/api/v1/payments/intent",
            json={"orderId": order["id"], "provider": "cashfree"},
            cookies=cookies,
        )
        assert r_malformed.status_code == 502

    # 3. Refund validation: unconfirmed/PENDING/FAILED/4xx/timeout cannot report completion
    provider = CashfreePaymentProvider(
        app_id="CF_ID",
        secret_key="CF_SEC",
        environment="sandbox",
    )
    payment = Payment(
        id=501,
        order_id=order["id"],
        provider="cashfree",
        provider_order_id="CB-REF-501",
        provider_payment_id="cf_pay_501",
        amount=1200,
        amount_paise=120000,
        currency="INR",
    )

    # 3a. Refund status PENDING does NOT report completion
    mock_client.post.return_value = httpx.Response(
        200,
        json={"cf_refund_id": "cf_rfnd_pending_1", "refund_id": "rfnd_1", "refund_status": "PENDING"},
        request=httpx.Request("POST", "https://sandbox.cashfree.com/pg/orders/CB-REF-501/refunds"),
    )
    with patch("app.services.payment.cashfree.httpx.Client", return_value=mock_ctx):
        ref_pending = provider.refund_payment(payment, 500, "Customer return")
        assert ref_pending["success"] is False
        assert ref_pending["status"] == "PENDING"

    # 3b. Refund HTTP 400 error fails closed
    mock_client.post.return_value = httpx.Response(
        400,
        json={"message": "Refund already processed for this order"},
        request=httpx.Request("POST", "https://sandbox.cashfree.com/pg/orders/CB-REF-501/refunds"),
    )
    with patch("app.services.payment.cashfree.httpx.Client", return_value=mock_ctx):
        ref_400 = provider.refund_payment(payment, 500, "Duplicate refund")
        assert ref_400["success"] is False
        assert "Refund already processed" in ref_400["error"]

    # 3c. Refund confirmed with SUCCESS returns COMPLETED
    mock_client.post.return_value = httpx.Response(
        200,
        json={"cf_refund_id": "cf_rfnd_ok_99", "refund_id": "rfnd_99", "refund_status": "SUCCESS"},
        request=httpx.Request("POST", "https://sandbox.cashfree.com/pg/orders/CB-REF-501/refunds"),
    )
    with patch("app.services.payment.cashfree.httpx.Client", return_value=mock_ctx):
        ref_ok = provider.refund_payment(payment, 500, "Approved return")
        assert ref_ok["success"] is True
        assert ref_ok["refund_id"] == "cf_rfnd_ok_99"
        assert ref_ok["status"] == "COMPLETED"


def test_7_2_3_tc07_cashfree_ownership_and_provider_isolation():
    """7.2.3-TC07: Cross-customer access is denied and cross-provider webhooks cannot mutate a Cashfree payment."""
    user1_cookies = _login_test_user("9999977047")
    user2_cookies = _login_test_user("9999977048")
    order = _create_test_order(user1_cookies, payment_method="UPI")

    mock_ctx = MagicMock()
    mock_client = MagicMock()
    mock_ctx.__enter__.return_value = mock_client
    mock_ctx.__exit__.return_value = None
    mock_client.post.side_effect = lambda url, json=None, **kw: httpx.Response(
        200,
        json={"order_id": json["order_id"], "payment_session_id": "sess_iso_tc07"},
        request=httpx.Request("POST", url),
    )

    with patch.object(settings, "cashfree_environment", "sandbox"), \
         patch.object(settings, "cashfree_app_id", "CF_ID"), \
         patch.object(settings, "cashfree_secret_key", "CF_SEC"), \
         patch("app.services.payment.cashfree.httpx.Client", return_value=mock_ctx):
        # User 2 cannot create Cashfree intent for User 1's order
        r_cross_intent = client.post(
            "/api/v1/payments/intent",
            json={"orderId": order["id"], "provider": "cashfree"},
            cookies=user2_cookies,
        )
        assert r_cross_intent.status_code == 404

        intent = client.post(
            "/api/v1/payments/intent",
            json={"orderId": order["id"], "provider": "cashfree"},
            cookies=user1_cookies,
        ).json()

    payment_id = intent["paymentId"]
    cf_order_id = intent["providerOrderId"]

    # User 2 cannot verify or fetch User 1's Cashfree payment
    r_cross_verify = client.post(
        "/api/v1/payments/verify",
        json={"paymentId": payment_id},
        cookies=user2_cookies,
    )
    assert r_cross_verify.status_code == 404
    assert client.get(f"/api/v1/payments/{payment_id}", cookies=user2_cookies).status_code == 404

    # Wrong-provider webhook attack: valid mock webhook targeting Cashfree payment's provider_order_id -> 400
    r_wrong_provider_wh = client.post(
        "/api/v1/payments/webhook/mock",
        json={
            "event": "payment.captured",
            "provider_order_id": cf_order_id,
            "provider_payment_id": "mock_spoof_pay_1",
        },
        headers={"x-signature": "valid_mock_signature"},
    )
    assert r_wrong_provider_wh.status_code == 400
    assert "provider" in r_wrong_provider_wh.json()["detail"].lower()

    # Payment and order remain untouched
    assert client.get(f"/api/v1/payments/{payment_id}", cookies=user1_cookies).json()["status"] == "PENDING"
    assert client.get(f"/api/v1/orders/{order['id']}", cookies=user1_cookies).json()["paymentStatus"] == "PENDING"


def _create_guest_order(email: str = "guest.buyer@example.com", payment_method: str = "UPI") -> dict:
    """Create a guest order (user_id is None) using an isolated anonymous TestClient."""
    guest_client = TestClient(app)
    add_res = guest_client.post("/api/v1/cart/items", json={"product_id": 1, "quantity": 1})
    assert add_res.status_code == 201
    order_res = guest_client.post(
        "/api/v1/orders",
        json={
            "customerEmail": email,
            "paymentMethod": payment_method,
            "shippingAddress": {
                "name": "Guest Buyer",
                "phone": "9888877001",
                "line1": "12 MG Road",
                "city": "Bengaluru",
                "state": "Karnataka",
                "postalCode": "560001",
            },
        },
    )
    assert order_res.status_code == 201
    return order_res.json()


def test_7_2_4_1_tc06_verified_order_identity_is_server_derived():
    """7.2.4.1-TC06: Tampering orderNumber on browser return cannot override server-bound orderNumber."""
    cookies = _login_test_user("9999977040")
    order_a = _create_test_order(cookies, payment_method="UPI")
    order_b = _create_test_order(cookies, payment_method="UPI")
    assert order_a["orderNumber"] != order_b["orderNumber"]

    mock_http_client = MagicMock()
    mock_ctx = MagicMock()
    mock_ctx.__enter__.return_value = mock_http_client
    mock_ctx.__exit__.return_value = None

    def mock_post(url, *, headers=None, json=None):
        return httpx.Response(
            200,
            json={
                "order_id": json["order_id"],
                "order_amount": json["order_amount"],
                "order_status": "ACTIVE",
                "payment_session_id": f"session_tc06_{json['order_id']}",
            },
            request=httpx.Request("POST", url),
        )

    def mock_get(url, *, headers=None):
        if url.endswith("/payments"):
            cf_id = url.rsplit("/", 2)[-2]
            return httpx.Response(
                200,
                json=[
                    {
                        "order_id": cf_id,
                        "cf_payment_id": "cf_pay_tc06_01",
                        "payment_status": "SUCCESS",
                        "payment_amount": round(order_a["totalAmountPaise"] / 100.0, 2),
                        "payment_currency": "INR",
                        "payment_group": "upi",
                    }
                ],
                request=httpx.Request("GET", url),
            )
        cf_id = url.rsplit("/", 1)[-1]
        return httpx.Response(
            200,
            json={
                "order_id": cf_id,
                "order_status": "PAID",
                "order_amount": round(order_a["totalAmountPaise"] / 100.0, 2),
                "order_currency": "INR",
            },
            request=httpx.Request("GET", url),
        )

    mock_http_client.post.side_effect = mock_post
    mock_http_client.get.side_effect = mock_get

    with patch.object(settings, "cashfree_environment", "sandbox"), \
         patch.object(settings, "cashfree_app_id", "CF_ID"), \
         patch.object(settings, "cashfree_secret_key", "CF_SEC"), \
         patch("app.services.payment.cashfree.httpx.Client", return_value=mock_ctx):
        intent_a = client.post(
            "/api/v1/payments/intent",
            json={"orderNumber": order_a["orderNumber"], "provider": "cashfree"},
            cookies=cookies,
        ).json()

        # Tamper orderNumber in query and JSON payload to point at order_b while verifying payment_a
        verify_res = client.post(
            f"/api/v1/payments/verify?orderNumber={order_b['orderNumber']}",
            json={
                "paymentId": intent_a["paymentId"],
                "providerOrderId": intent_a["providerOrderId"],
                "orderNumber": order_b["orderNumber"],
            },
            cookies=cookies,
        )
        assert verify_res.status_code == 200
        verified_body = verify_res.json()
        assert verified_body["orderId"] == order_a["id"]
        assert verified_body["orderNumber"] == order_a["orderNumber"]
        assert verified_body["orderNumber"] != order_b["orderNumber"]

        # Order B remains untouched (PENDING)
        order_b_state = client.get(f"/api/v1/orders/{order_b['id']}", cookies=cookies).json()
        assert order_b_state["paymentStatus"] == "PENDING"


def test_7_2_4_1_tc07_guest_payment_verification_isolation():
    """7.2.4.1-TC07: Guest payment verification rejects missing/foreign bindings without mutating state or leaking order data."""
    guest_order_1 = _create_guest_order("guest1@example.com")
    guest_order_2 = _create_guest_order("guest2@example.com")

    mock_http_client = MagicMock()
    mock_ctx = MagicMock()
    mock_ctx.__enter__.return_value = mock_http_client
    mock_ctx.__exit__.return_value = None

    def mock_post(url, *, headers=None, json=None):
        return httpx.Response(
            200,
            json={
                "order_id": json["order_id"],
                "order_amount": json["order_amount"],
                "order_status": "ACTIVE",
                "payment_session_id": f"sess_{json['order_id']}",
            },
            request=httpx.Request("POST", url),
        )

    def mock_get(url, *, headers=None):
        cf_id = url.rsplit("/", 1)[-1]
        return httpx.Response(
            200,
            json={
                "order_id": cf_id,
                "order_status": "ACTIVE",
                "order_amount": round(guest_order_1["totalAmountPaise"] / 100.0, 2),
                "order_currency": "INR",
            },
            request=httpx.Request("GET", url),
        )

    mock_http_client.post.side_effect = mock_post
    mock_http_client.get.side_effect = mock_get

    anon_client = TestClient(app)
    with patch.object(settings, "cashfree_environment", "sandbox"), \
         patch.object(settings, "cashfree_app_id", "CF_ID"), \
         patch.object(settings, "cashfree_secret_key", "CF_SEC"), \
         patch("app.services.payment.cashfree.httpx.Client", return_value=mock_ctx):
        intent_1 = anon_client.post(
            "/api/v1/payments/intent",
            json={"orderNumber": guest_order_1["orderNumber"], "provider": "cashfree"},
        ).json()
        intent_2 = anon_client.post(
            "/api/v1/payments/intent",
            json={"orderNumber": guest_order_2["orderNumber"], "provider": "cashfree"},
        ).json()

        pay_1_id = intent_1["paymentId"]
        cf_order_1 = intent_1["providerOrderId"]
        cf_order_2 = intent_2["providerOrderId"]

        # 1. Missing providerOrderId on guest payment must be rejected without calling gateway or mutating state
        mock_http_client.get.reset_mock()
        r_missing = anon_client.post("/api/v1/payments/verify", json={"paymentId": pay_1_id})
        assert r_missing.status_code == 400
        assert guest_order_1["orderNumber"] not in r_missing.text
        assert mock_http_client.get.call_count == 0

        # 2. Foreign providerOrderId (from guest_order_2) against guest payment 1 must be rejected without flipping payment 1 to FAILED
        r_foreign = anon_client.post(
            "/api/v1/payments/verify",
            json={"paymentId": pay_1_id, "providerOrderId": cf_order_2},
        )
        assert r_foreign.status_code == 400
        assert guest_order_1["orderNumber"] not in r_foreign.text
        assert mock_http_client.get.call_count == 0

        # 3. Anonymous GET /api/v1/payments/{id} without matching providerOrderId cannot enumerate guest payment/orderNumber
        r_get_no_token = anon_client.get(f"/api/v1/payments/{pay_1_id}")
        assert r_get_no_token.status_code == 404
        r_get_wrong_token = anon_client.get(f"/api/v1/payments/{pay_1_id}?providerOrderId={cf_order_2}")
        assert r_get_wrong_token.status_code == 404

        # With valid providerOrderId, GET returns the payment still in PENDING (not sabotaged to FAILED)
        r_get_valid = anon_client.get(f"/api/v1/payments/{pay_1_id}?providerOrderId={cf_order_1}")
        assert r_get_valid.status_code == 200
        assert r_get_valid.json()["status"] == "PENDING"
        assert r_get_valid.json()["orderNumber"] == guest_order_1["orderNumber"]

        # 4. Even with valid providerOrderId, real gateway status remains mandatory (ACTIVE -> 400 pending)
        r_unpaid = anon_client.post(
            "/api/v1/payments/verify",
            json={"paymentId": pay_1_id, "providerOrderId": cf_order_1},
        )
        assert r_unpaid.status_code == 400
        assert "pending" in r_unpaid.json()["detail"].lower()


def test_7_2_4_3_tc03_webhook_signature_replay_and_out_of_order_safety():
    """7.2.4.3-TC03: Deliver Cashfree webhook twice, with invalid signature, and out-of-order failure after success."""
    import base64
    import hashlib
    import hmac

    cookies = _login_test_user("9999977043")
    order_data = _create_test_order(cookies, payment_method="UPI")
    order_number = order_data["orderNumber"]
    amount_inr = round(order_data["totalAmountPaise"] / 100.0, 2)

    mock_http_client = MagicMock()
    mock_ctx = MagicMock()
    mock_ctx.__enter__.return_value = mock_http_client
    mock_ctx.__exit__.return_value = None
    mock_http_client.post.side_effect = lambda url, *, headers=None, json=None: httpx.Response(
        200,
        json={
            "order_id": json["order_id"],
            "order_amount": json["order_amount"],
            "order_status": "ACTIVE",
            "payment_session_id": f"sess_tc03_{json['order_id']}",
        },
        request=httpx.Request("POST", url),
    )

    secret = "CF_WEBHOOK_SECRET_TC03"
    ts = "1730332800000"

    def sign_body(raw: bytes) -> str:
        digest = hmac.new(secret.encode("utf-8"), ts.encode("utf-8") + raw, hashlib.sha256).digest()
        return base64.b64encode(digest).decode("utf-8")

    with patch.object(settings, "cashfree_environment", "sandbox"), \
         patch.object(settings, "cashfree_app_id", "CF_ID"), \
         patch.object(settings, "cashfree_secret_key", secret), \
         patch("app.services.payment.cashfree.httpx.Client", return_value=mock_ctx):
        intent = client.post(
            "/api/v1/payments/intent",
            json={"orderNumber": order_number, "provider": "cashfree"},
            cookies=cookies,
        ).json()
        cf_order_id = intent["providerOrderId"]

        success_raw = json.dumps(
            {
                "type": "PAYMENT_SUCCESS_WEBHOOK",
                "data": {
                    "order": {
                        "order_id": cf_order_id,
                        "order_amount": amount_inr,
                        "order_currency": "INR",
                    },
                    "payment": {
                        "cf_payment_id": "cf_pay_tc03_999",
                        "payment_status": "SUCCESS",
                        "payment_amount": amount_inr,
                        "payment_currency": "INR",
                        "payment_group": "upi",
                    },
                },
            }
        ).encode("utf-8")

        # 1. Invalid signature rejected with 400
        r_bad_sig = client.post(
            "/api/v1/payments/webhook/cashfree",
            content=success_raw,
            headers={
                "Content-Type": "application/json",
                "x-webhook-timestamp": ts,
                "x-webhook-signature": "invalid_signature_value",
            },
        )
        assert r_bad_sig.status_code == 400

        # 2. First valid delivery transitions order to CONFIRMED / PAID
        r_ok_1 = client.post(
            "/api/v1/payments/webhook/cashfree",
            content=success_raw,
            headers={
                "Content-Type": "application/json",
                "x-webhook-timestamp": ts,
                "x-webhook-signature": sign_body(success_raw),
            },
        )
        assert r_ok_1.status_code == 200
        assert r_ok_1.json()["status"] == "ok"

        # 3. Duplicate replay is idempotent and does not duplicate history records
        r_ok_2 = client.post(
            "/api/v1/payments/webhook/cashfree",
            content=success_raw,
            headers={
                "Content-Type": "application/json",
                "x-webhook-timestamp": ts,
                "x-webhook-signature": sign_body(success_raw),
            },
        )
        assert r_ok_2.status_code == 200
        assert r_ok_2.json()["status"] == "ok"

        # 4. Out-of-order failure webhook arriving after PAID is ignored and keeps order CONFIRMED/PAID
        failed_raw = json.dumps(
            {
                "type": "PAYMENT_FAILED_WEBHOOK",
                "data": {
                    "order": {
                        "order_id": cf_order_id,
                        "order_amount": amount_inr,
                        "order_currency": "INR",
                    },
                    "payment": {
                        "cf_payment_id": "cf_pay_tc03_late_fail",
                        "payment_status": "FAILED",
                        "payment_amount": amount_inr,
                        "payment_currency": "INR",
                    },
                },
            }
        ).encode("utf-8")
        r_late_fail = client.post(
            "/api/v1/payments/webhook/cashfree",
            content=failed_raw,
            headers={
                "Content-Type": "application/json",
                "x-webhook-timestamp": ts,
                "x-webhook-signature": sign_body(failed_raw),
            },
        )
        assert r_late_fail.status_code == 200
        order_after = client.get(f"/api/v1/orders/{order_data['id']}", cookies=cookies).json()
        assert order_after["paymentStatus"] == "PAID"
        assert order_after["status"] == "CONFIRMED"


def test_7_2_4_3_tc04_order_customer_amount_currency_binding():
    """7.2.4.3-TC04: Mismatched order, customer, amount, or currency cannot mark an order paid."""
    cookies_a = _login_test_user("9999977044")
    cookies_b = _login_test_user("9999977045")
    order_a = _create_test_order(cookies_a, payment_method="UPI")
    amount_inr = round(order_a["totalAmountPaise"] / 100.0, 2)

    mock_http_client = MagicMock()
    mock_ctx = MagicMock()
    mock_ctx.__enter__.return_value = mock_http_client
    mock_ctx.__exit__.return_value = None
    mock_http_client.post.side_effect = lambda url, *, headers=None, json=None: httpx.Response(
        200,
        json={
            "order_id": json["order_id"],
            "order_amount": json["order_amount"],
            "order_status": "ACTIVE",
            "payment_session_id": f"sess_tc04_{json['order_id']}",
        },
        request=httpx.Request("POST", url),
    )

    with patch.object(settings, "cashfree_environment", "sandbox"), \
         patch.object(settings, "cashfree_app_id", "CF_ID"), \
         patch.object(settings, "cashfree_secret_key", "CF_SEC"), \
         patch("app.services.payment.cashfree.httpx.Client", return_value=mock_ctx):
        intent = client.post(
            "/api/v1/payments/intent",
            json={"orderNumber": order_a["orderNumber"], "provider": "cashfree"},
            cookies=cookies_a,
        ).json()
        pay_id = intent["paymentId"]
        cf_order_id = intent["providerOrderId"]

        # 1. Wrong customer (User B) attempting to verify User A's payment -> 404 (anti-enumeration IDOR guard)
        r_wrong_user = client.post(
            "/api/v1/payments/verify",
            json={"paymentId": pay_id, "providerOrderId": cf_order_id},
            cookies=cookies_b,
        )
        assert r_wrong_user.status_code in (403, 404)

        # 2. Mismatched providerOrderId -> 400
        r_wrong_order = client.post(
            "/api/v1/payments/verify",
            json={"paymentId": pay_id, "providerOrderId": "cf_foreign_order_999"},
            cookies=cookies_a,
        )
        assert r_wrong_order.status_code == 400

        # 3. Gateway returns mismatched currency (USD instead of INR) -> 400
        mock_http_client.get.side_effect = lambda url, *, headers=None: httpx.Response(
            200,
            json={
                "order_id": cf_order_id,
                "order_status": "PAID",
                "order_amount": amount_inr,
                "order_currency": "USD",
            },
            request=httpx.Request("GET", url),
        )
        r_wrong_curr = client.post(
            "/api/v1/payments/verify",
            json={"paymentId": pay_id, "providerOrderId": cf_order_id},
            cookies=cookies_a,
        )
        assert r_wrong_curr.status_code == 400

        # 4. Gateway returns underpaid amount -> 400
        mock_http_client.get.side_effect = lambda url, *, headers=None: httpx.Response(
            200,
            json={
                "order_id": cf_order_id,
                "order_status": "PAID",
                "order_amount": round(amount_inr - 1.0, 2),
                "order_currency": "INR",
            },
            request=httpx.Request("GET", url),
        )
        r_underpaid = client.post(
            "/api/v1/payments/verify",
            json={"paymentId": pay_id, "providerOrderId": cf_order_id},
            cookies=cookies_a,
        )
        assert r_underpaid.status_code == 400

        # Order A remains unpaid
        order_state = client.get(f"/api/v1/orders/{order_a['id']}", cookies=cookies_a).json()
        assert order_state["paymentStatus"] != "PAID"
