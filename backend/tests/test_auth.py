"""Automated tests for V1 Authentication (Email Magic Link, Google, Facebook) conforming to docs/api-auth.md."""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_email_start_returns_202_and_generic_message():
    """Verify POST /api/v1/auth/email/start returns 202 with non-enumerating message."""
    response = client.post("/api/v1/auth/email/start", json={"email": "aditi@example.com"})
    assert response.status_code == 202
    data = response.json()
    assert data["message"] == "If the email address is valid, a sign-in link has been sent."
    assert "devMagicLink" in data
    assert "token=" in data["devMagicLink"]


def test_email_start_invalid_email_rejected():
    """Verify malformed email addresses are rejected with 422."""
    response = client.post("/api/v1/auth/email/start", json={"email": "not-an-email"})
    assert response.status_code == 422


def test_email_start_rate_limiting():
    """Verify rapid repeated requests return 202 without revealing membership or erroring."""
    email = "throttled@example.com"
    res1 = client.post("/api/v1/auth/email/start", json={"email": email})
    assert res1.status_code == 202

    res2 = client.post("/api/v1/auth/email/start", json={"email": email})
    assert res2.status_code == 202
    assert res2.json()["message"] == "If the email address is valid, a sign-in link has been sent."


def test_email_verify_success_sets_session_cookie():
    """Verify GET /api/v1/auth/email/verify validates token, issues session cookie, and redirects."""
    auth_client = TestClient(app)
    email = "verify.user@example.com"

    start_res = auth_client.post("/api/v1/auth/email/start", json={"email": email})
    assert start_res.status_code == 202
    dev_link = start_res.json()["devMagicLink"]
    token = dev_link.split("token=")[1]

    # Verify token
    verify_res = auth_client.get(
        f"/api/v1/auth/email/verify?token={token}&returnTo=/account",
        follow_redirects=False,
    )
    assert verify_res.status_code == 303
    assert "/account" in verify_res.headers["location"]
    assert "session_token" in verify_res.cookies

    # Profile check via /auth/me
    me_res = auth_client.get("/api/v1/auth/me")
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["email"] == email
    assert "email" in me_data["identities"]


def test_email_verify_single_use():
    """Verify token can only be consumed once."""
    auth_client = TestClient(app)
    email = "single.use@example.com"

    start_res = auth_client.post("/api/v1/auth/email/start", json={"email": email})
    token = start_res.json()["devMagicLink"].split("token=")[1]

    # 1. First consumption succeeds
    res1 = auth_client.get(f"/api/v1/auth/email/verify?token={token}", follow_redirects=False)
    assert res1.status_code == 303
    assert "error" not in res1.headers["location"]

    # 2. Second consumption fails and redirects to error
    res2 = auth_client.get(f"/api/v1/auth/email/verify?token={token}", follow_redirects=False)
    assert res2.status_code == 303
    assert "error=invalid_link" in res2.headers["location"]


def test_email_verify_invalid_token_redirects_to_error():
    """Verify invalid token redirects to error parameter."""
    auth_client = TestClient(app)
    res = auth_client.get("/api/v1/auth/email/verify?token=completely_fake_invalid_token_12345", follow_redirects=False)
    assert res.status_code == 303
    assert "error=invalid_link" in res.headers["location"]


def test_email_verify_merges_guest_cart():
    """Verify magic link sign-in merges guest cart into user cart."""
    session_client = TestClient(app)

    # 1. Add item to guest cart
    add_res = session_client.post("/api/v1/cart/items", json={"product_id": 1, "quantity": 2})
    assert add_res.status_code == 201
    assert "guest_cart_token" in session_client.cookies

    # 2. Request and verify magic link in same session
    start_res = session_client.post("/api/v1/auth/email/start", json={"email": "cart.merge@example.com"})
    token = start_res.json()["devMagicLink"].split("token=")[1]

    verify_res = session_client.get(f"/api/v1/auth/email/verify?token={token}", follow_redirects=False)
    assert verify_res.status_code == 303

    # 3. Retrieve cart - merged items should be present
    cart_res = session_client.get("/api/v1/cart")
    assert cart_res.status_code == 200
    assert cart_res.json()["itemCount"] >= 2


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
    auth_client.post(
        "/api/v1/auth/google",
        json={"credential": "mock_token", "email": "logout.test@example.com", "name": "Logout Test"},
    )

    # Logout
    logout_res = auth_client.post("/api/v1/auth/logout")
    assert logout_res.status_code == 200

    # /auth/me should now return 401
    me_res = auth_client.get("/api/v1/auth/me")
    assert me_res.status_code == 401


def test_google_sign_in_account_unification():
    """Verify Google sign-in unifies with existing user account if email matches."""
    client1 = TestClient(app)
    email = "unify.test@example.com"
    res1 = client1.post(
        "/api/v1/auth/google",
        json={
            "credential": "mock_google_token_1",
            "email": email,
            "name": "First Name",
            "sub": "google_sub_unify_1",
        },
    )
    assert res1.status_code == 200
    user_id = res1.json()["user"]["id"]

    # Re-login with same Google sub
    client2 = TestClient(app)
    res2 = client2.post(
        "/api/v1/auth/google",
        json={
            "credential": "mock_google_token_2",
            "email": email,
            "name": "Updated Name",
            "sub": "google_sub_unify_1",
        },
    )
    assert res2.status_code == 200
    assert res2.json()["user"]["id"] == user_id


def test_facebook_sign_in():
    """Verify Facebook (Meta) authentication creates user, identity, and session cookie."""
    auth_client = TestClient(app)
    payload = {
        "accessToken": "mock_fb_access_token_123",
        "userId": "fb_uid_987654",
        "email": "priya.sharma@example.com",
        "name": "Priya Sharma",
    }
    response = auth_client.post("/api/v1/auth/facebook", json=payload)
    assert response.status_code == 200
    assert "session_token" in response.cookies
    data = response.json()
    assert data["user"]["email"] == "priya.sharma@example.com"
    assert data["user"]["name"] == "Priya Sharma"
    assert "facebook" in data["user"]["identities"]

    me_res = auth_client.get("/api/v1/auth/me")
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "priya.sharma@example.com"


def test_account_unification_email_and_social():
    """Verify Email magic link and Social accounts unify under the same user."""
    shared_email = "unified.family@example.com"

    # 1. Sign in via Google first
    g_client = TestClient(app)
    g_res = g_client.post(
        "/api/v1/auth/google",
        json={
            "credential": "mock_google_token_shared",
            "email": shared_email,
            "name": "Shared User",
            "sub": "google_sub_shared",
        },
    )
    assert g_res.status_code == 200
    unified_user_id = g_res.json()["user"]["id"]

    # 2. Sign in via Facebook with same email
    fb_client = TestClient(app)
    fb_res = fb_client.post(
        "/api/v1/auth/facebook",
        json={
            "accessToken": "mock_fb_token_shared",
            "userId": "fb_uid_shared",
            "email": shared_email,
            "name": "Shared User",
        },
    )
    assert fb_res.status_code == 200
    assert fb_res.json()["user"]["id"] == unified_user_id

    # 3. Sign in via Email magic link with same email
    em_client = TestClient(app)
    start_res = em_client.post("/api/v1/auth/email/start", json={"email": shared_email})
    token = start_res.json()["devMagicLink"].split("token=")[1]
    verify_res = em_client.get(f"/api/v1/auth/email/verify?token={token}", follow_redirects=False)
    assert verify_res.status_code == 303

    me_res = em_client.get("/api/v1/auth/me")
    assert me_res.status_code == 200
    assert me_res.json()["id"] == unified_user_id
    identities = me_res.json()["identities"]
    assert "google" in identities
    assert "facebook" in identities
    assert "email" in identities
