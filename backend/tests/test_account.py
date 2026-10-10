"""Integration tests for Customer Account, Profile, and Wishlist conforming to Milestone 8."""

from fastapi.testclient import TestClient
from app.main import app

from app.db.session import SessionLocal
from app.models.user import User

client = TestClient(app)


def _login_test_user(phone: str = "9999966001") -> dict[str, str]:
    """Helper to authenticate and return session cookies."""
    email = f"user_{phone}@example.com"
    res = client.post("/api/v1/auth/google", json={
        "credential": f"mock_token_{phone}",
        "email": email,
        "name": "Test Customer",
        "sub": f"sub_{phone}",
    })
    assert res.status_code == 200
    with SessionLocal() as db:
        user = db.query(User).filter(User.email == email).first()
        if user and user.phone != phone:
            user.phone = phone
            db.commit()
    return dict(res.cookies)


def test_customer_profile_get_and_update():
    """Verify viewing and updating customer profile information with phone and DEC018-3 policy."""
    cookies = _login_test_user("9999966001")

    # 1. Fetch initial profile
    res = client.get("/api/v1/account/profile", cookies=cookies)
    assert res.status_code == 200
    profile = res.json()
    assert profile["phone"] == "9999966001"
    assert "identities" in profile

    # 2. Update profile name and phone (18.2-TC01)
    update_res = client.patch(
        "/api/v1/account/profile",
        json={"name": "Meera Patel", "phone": "+919876543210"},
        cookies=cookies,
    )
    assert update_res.status_code == 200
    updated = update_res.json()
    assert updated["name"] == "Meera Patel"
    assert updated["phone"] == "+919876543210"

    # 3. Verify get returns new values
    res2 = client.get("/api/v1/account/profile", cookies=cookies)
    assert res2.json()["name"] == "Meera Patel"
    assert res2.json()["phone"] == "+919876543210"


def test_customer_profile_unicode_and_whitespace():
    """18.2-TC02: Verify Unicode name and trimmed whitespace."""
    cookies = _login_test_user("9999966011")

    update_res = client.patch(
        "/api/v1/account/profile",
        json={"name": "  Meera Patel (మీరా)  ", "phone": " 9876543211 "},
        cookies=cookies,
    )
    assert update_res.status_code == 200
    data = update_res.json()
    assert data["name"] == "Meera Patel (మీరా)"
    assert data["phone"] == "9876543211"


def test_customer_profile_clear_phone():
    """18.2-TC03: Verify clearing optional phone deliberately."""
    cookies = _login_test_user("9999966012")

    update_res = client.patch(
        "/api/v1/account/profile",
        json={"phone": None},
        cookies=cookies,
    )
    assert update_res.status_code == 200
    assert update_res.json()["phone"] is None

    # Verify cleared via GET
    res = client.get("/api/v1/account/profile", cookies=cookies)
    assert res.json()["phone"] is None


def test_customer_profile_reject_blank_name():
    """18.2-TC04: Verify rejection of empty/blank name."""
    cookies = _login_test_user("9999966013")

    update_res = client.patch(
        "/api/v1/account/profile",
        json={"name": "   "},
        cookies=cookies,
    )
    assert update_res.status_code == 422


def test_customer_profile_reject_malformed_phone():
    """18.2-TC05: Verify rejection of malformed phone number."""
    cookies = _login_test_user("9999966014")

    for invalid_phone in ["123", "abcdefghij", "12345678901234567890"]:
        res = client.patch(
            "/api/v1/account/profile",
            json={"phone": invalid_phone},
            cookies=cookies,
        )
        assert res.status_code == 422


def test_customer_profile_phone_uniqueness_conflict():
    """18.2-TC06: Verify duplicate phone conflict safe response."""
    # Ensure user A has phone 9999966015
    _login_test_user("9999966015")
    # User B tries to set phone to 9999966015
    cookies_b = _login_test_user("9999966016")

    res = client.patch(
        "/api/v1/account/profile",
        json={"phone": "9999966015"},
        cookies=cookies_b,
    )
    assert res.status_code == 400
    assert "already associated" in res.json()["detail"].lower()


def test_customer_profile_prohibit_unverified_email_change():
    """18.2-TC07 & 18.2-TC08: DEC018-3 prohibit unverified email mutation, permit same-email no-op."""
    cookies = _login_test_user("9999966017")
    email = "user_9999966017@example.com"

    # Attempting to change email is rejected
    res = client.patch(
        "/api/v1/account/profile",
        json={"email": "new_email@example.com"},
        cookies=cookies,
    )
    assert res.status_code == 400
    assert "cannot be changed" in res.json()["detail"]

    # Same email no-op is accepted
    res_noop = client.patch(
        "/api/v1/account/profile",
        json={"name": "Meera Same", "email": email},
        cookies=cookies,
    )
    assert res_noop.status_code == 200
    assert res_noop.json()["email"] == email


def test_customer_profile_mass_assignment_protection():
    """18.2-TC09: Forbidden fields like role/status/identities are ignored and not mass-assigned."""
    cookies = _login_test_user("9999966018")

    res = client.patch(
        "/api/v1/account/profile",
        json={"name": "Attacker", "role": "ADMIN", "status": "SUSPENDED"},
        cookies=cookies,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ACTIVE"
    with SessionLocal() as db:
        user = db.query(User).filter(User.phone == "9999966018").first()
        assert user.role == "CUSTOMER"
        assert user.status == "ACTIVE"


def test_account_overview_metrics():
    """Verify aggregated dashboard statistics (orders, addresses, wishlist counts)."""
    cookies = _login_test_user("9999966002")

    # 1. Initially zero
    overview_res = client.get("/api/v1/account/overview", cookies=cookies)
    assert overview_res.status_code == 200
    overview = overview_res.json()
    assert overview["totalOrders"] == 0
    assert overview["savedAddresses"] == 0
    assert overview["wishlistItemsCount"] == 0

    # 2. Save an address
    client.post(
        "/api/v1/addresses",
        json={
            "name": "Meera Home",
            "phone": "9999966002",
            "line1": "Road 12, Jubilee Hills",
            "city": "Hyderabad",
            "state": "Telangana",
            "postalCode": "500033",
        },
        cookies=cookies,
    )

    # 3. Add to wishlist
    client.post(
        "/api/v1/wishlist/items",
        json={"productId": 1},
        cookies=cookies,
    )

    # 4. Place an order
    client.post(
        "/api/v1/cart/items",
        json={"product_id": 1, "quantity": 1},
        cookies=cookies,
    )
    client.post(
        "/api/v1/orders",
        json={"paymentMethod": "COD"},
        cookies=cookies,
    )

    # 5. Check updated overview
    overview_res2 = client.get("/api/v1/account/overview", cookies=cookies)
    assert overview_res2.status_code == 200
    data = overview_res2.json()
    assert data["savedAddresses"] == 1
    assert data["wishlistItemsCount"] == 1
    assert data["totalOrders"] == 1
    assert data["activeOrders"] == 1


def test_wishlist_lifecycle():
    """Verify adding, listing, removing, and clearing items in customer wishlist."""
    cookies = _login_test_user("9999966003")

    # 1. Wishlist initially empty
    res = client.get("/api/v1/wishlist", cookies=cookies)
    assert res.status_code == 200
    assert res.json()["totalItems"] == 0

    # 2. Add product by ID
    add1 = client.post("/api/v1/wishlist/items", json={"productId": 1}, cookies=cookies)
    assert add1.status_code == 201
    wishlist = add1.json()
    assert wishlist["totalItems"] == 1
    assert wishlist["items"][0]["productId"] == 1
    assert wishlist["items"][0]["pricePaise"] is not None

    # 3. Add product by Slug
    add2 = client.post(
        "/api/v1/wishlist/items",
        json={"productSlug": "crochet-tulip-bouquet"},
        cookies=cookies,
    )
    assert add2.status_code == 201
    assert add2.json()["totalItems"] == 2

    # 4. Remove item by product ID
    rem_res = client.delete("/api/v1/wishlist/items/1", cookies=cookies)
    assert rem_res.status_code == 200
    assert rem_res.json()["totalItems"] == 1

    # 5. Clear wishlist
    clear_res = client.delete("/api/v1/wishlist", cookies=cookies)
    assert clear_res.status_code == 200
    assert clear_res.json()["totalItems"] == 0


def test_account_authorization():
    """Verify unauthenticated requests are rejected."""
    res_profile = client.get("/api/v1/account/profile")
    assert res_profile.status_code == 401

    res_wishlist = client.get("/api/v1/wishlist")
    assert res_wishlist.status_code == 401
