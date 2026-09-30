"""Integration tests for Customer Account, Profile, and Wishlist conforming to Milestone 8."""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def _login_test_user(phone: str = "9999966001") -> dict[str, str]:
    """Helper to authenticate and return session cookies."""
    send_res = client.post("/api/v1/auth/phone/send-otp", json={"phone": phone})
    assert send_res.status_code == 200
    otp = send_res.json().get("devOtp") or "123456"
    res = client.post("/api/v1/auth/phone/verify-otp", json={"phone": phone, "otp": otp})
    assert res.status_code == 200
    return dict(res.cookies)


def test_customer_profile_get_and_update():
    """Verify viewing and updating customer profile information."""
    cookies = _login_test_user("9999966001")

    # 1. Fetch initial profile
    res = client.get("/api/v1/account/profile", cookies=cookies)
    assert res.status_code == 200
    profile = res.json()
    assert profile["phone"] == "9999966001"
    assert "identities" in profile

    # 2. Update profile
    update_res = client.patch(
        "/api/v1/account/profile",
        json={"name": "Meera Patel", "email": "meera.patel@example.com"},
        cookies=cookies,
    )
    assert update_res.status_code == 200
    updated = update_res.json()
    assert updated["name"] == "Meera Patel"
    assert updated["email"] == "meera.patel@example.com"

    # 3. Verify get returns new values
    res2 = client.get("/api/v1/account/profile", cookies=cookies)
    assert res2.json()["name"] == "Meera Patel"


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
