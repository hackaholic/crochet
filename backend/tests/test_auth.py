"""Automated tests for Authentication conforming to Milestone 5."""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_send_otp_success():
    """Verify requesting an OTP succeeds and returns devOtp in test mode."""
    response = client.post("/api/v1/auth/phone/send-otp", json={"phone": "9999900001"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["phone"] == "9999900001"
    assert data["cooldownSeconds"] == 60
    assert data["devOtp"] is not None


def test_send_otp_cooldown_throttling():
    """Verify rapid repeated OTP requests are throttled with 429."""
    phone = "9999900002"
    res1 = client.post("/api/v1/auth/phone/send-otp", json={"phone": phone})
    assert res1.status_code == 200

    # Immediate second request should be throttled
    res2 = client.post("/api/v1/auth/phone/send-otp", json={"phone": phone})
    assert res2.status_code == 429
    assert "Please wait" in res2.json()["detail"]


def test_send_otp_invalid_phone():
    """Verify malformed phone numbers are rejected with 422."""
    response = client.post("/api/v1/auth/phone/send-otp", json={"phone": "12345"})
    assert response.status_code == 422


def test_verify_otp_incorrect_code():
    """Verify incorrect OTP code returns 400."""
    phone = "9999900003"
    client.post("/api/v1/auth/phone/send-otp", json={"phone": phone})

    verify_res = client.post(
        "/api/v1/auth/phone/verify-otp",
        json={"phone": phone, "otp": "000000"},
    )
    assert verify_res.status_code == 400
    assert "Incorrect OTP" in verify_res.json()["detail"]


def test_verify_otp_success_sets_session_cookie():
    """Verify successful OTP verification creates user, session, and sets cookie."""
    auth_client = TestClient(app)
    phone = "9999900004"
    send_res = auth_client.post("/api/v1/auth/phone/send-otp", json={"phone": phone})
    otp_code = send_res.json()["devOtp"]

    verify_res = auth_client.post(
        "/api/v1/auth/phone/verify-otp",
        json={"phone": phone, "otp": otp_code, "name": "Aditi Roy"},
    )
    assert verify_res.status_code == 200
    assert "session_token" in verify_res.cookies
    data = verify_res.json()
    assert data["user"]["name"] == "Aditi Roy"
    assert data["user"]["phone"] == phone
    assert "phone" in data["user"]["identities"]

    # Verify /auth/me returns this authenticated customer
    me_res = auth_client.get("/api/v1/auth/me")
    assert me_res.status_code == 200
    assert me_res.json()["phone"] == phone


def test_google_sign_in():
    """Verify One-Click Google Authentication creates user and session."""
    auth_client = TestClient(app)
    payload = {
        "credential": "mock_google_jwt_token",
        "email": "riya.sen@example.com",
        "name": "Riya Sen",
        "sub": "google_sub_109283",
    }
    response = auth_client.post("/api/v1/auth/google", json=payload)
    assert response.status_code == 200
    assert "session_token" in response.cookies
    data = response.json()
    assert data["user"]["email"] == "riya.sen@example.com"
    assert "google" in data["user"]["identities"]

    # Verify /auth/me
    me_res = auth_client.get("/api/v1/auth/me")
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "riya.sen@example.com"


def test_logout_revokes_session():
    """Verify logout clears the session cookie and revokes access."""
    auth_client = TestClient(app)
    phone = "9999900005"
    send_res = auth_client.post("/api/v1/auth/phone/send-otp", json={"phone": phone})
    auth_client.post(
        "/api/v1/auth/phone/verify-otp",
        json={"phone": phone, "otp": send_res.json()["devOtp"]},
    )

    # Logout
    logout_res = auth_client.post("/api/v1/auth/logout")
    assert logout_res.status_code == 200

    # /auth/me should now return 401
    me_res = auth_client.get("/api/v1/auth/me")
    assert me_res.status_code == 401


def test_login_auto_merges_guest_cart():
    """Verify anonymous guest cart automatically merges upon login."""
    session_client = TestClient(app)

    # 1. Add item to guest cart
    add_res = session_client.post("/api/v1/cart/items", json={"product_id": 1, "quantity": 2})
    assert add_res.status_code == 201
    assert "guest_cart_token" in session_client.cookies

    # 2. Login via OTP in the same browser session
    phone = "9999900006"
    send_res = session_client.post("/api/v1/auth/phone/send-otp", json={"phone": phone})
    otp_code = send_res.json()["devOtp"]

    verify_res = session_client.post(
        "/api/v1/auth/phone/verify-otp",
        json={"phone": phone, "otp": otp_code},
    )
    assert verify_res.status_code == 200
    assert verify_res.json()["cartMerged"] is True

    # 3. Retrieve cart - should have the merged items!
    cart_res = session_client.get("/api/v1/cart")
    assert cart_res.status_code == 200
    assert cart_res.json()["itemCount"] == 2
    assert cart_res.json()["items"][0]["productId"] == 1
