"""Integration tests for Orders, Addresses, and Checkout flow."""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def _login_test_user(phone: str = "9999943210") -> dict[str, str]:
    """Helper to authenticate and return session cookies."""
    send_res = client.post("/api/v1/auth/phone/send-otp", json={"phone": phone})
    assert send_res.status_code == 200
    otp = send_res.json().get("devOtp") or "123456"
    res = client.post("/api/v1/auth/phone/verify-otp", json={"phone": phone, "otp": otp})
    assert res.status_code == 200
    return dict(res.cookies)


def test_address_management_lifecycle():
    """Test creating, listing, updating, setting default, and deleting customer addresses."""
    cookies = _login_test_user("9999900001")

    # 1. List initially empty
    res = client.get("/api/v1/addresses", cookies=cookies)
    assert res.status_code == 200
    assert res.json() == []

    # 2. Create first address (should automatically be default)
    addr_payload = {
        "name": "Priya Sharma",
        "phone": "9999900001",
        "line1": "Flat 402, Lotus Orchid",
        "line2": "MG Road, Indiranagar",
        "landmark": "Near Metro Pillar 45",
        "city": "Bengaluru",
        "state": "Karnataka",
        "postalCode": "560038",
        "country": "IN",
        "isDefault": False,
    }
    res = client.post("/api/v1/addresses", json=addr_payload, cookies=cookies)
    assert res.status_code == 201
    addr1 = res.json()
    assert addr1["isDefault"] is True
    assert addr1["city"] == "Bengaluru"
    addr1_id = addr1["id"]

    # 3. Create second address with isDefault=True
    addr2_payload = {
        "name": "Priya Office",
        "phone": "9999900001",
        "line1": "Tech Park Block B",
        "city": "Bengaluru",
        "state": "Karnataka",
        "postalCode": "560103",
        "isDefault": True,
    }
    res = client.post("/api/v1/addresses", json=addr2_payload, cookies=cookies)
    assert res.status_code == 201
    addr2 = res.json()
    assert addr2["isDefault"] is True
    addr2_id = addr2["id"]

    # 4. Verify addr1 is no longer default
    res = client.get("/api/v1/addresses", cookies=cookies)
    assert res.status_code == 200
    addresses = res.json()
    assert len(addresses) == 2
    for a in addresses:
        if a["id"] == addr1_id:
            assert a["isDefault"] is False
        elif a["id"] == addr2_id:
            assert a["isDefault"] is True

    # 5. Set addr1 back to default
    res = client.post(f"/api/v1/addresses/{addr1_id}/default", cookies=cookies)
    assert res.status_code == 200
    assert res.json()["isDefault"] is True

    # 6. Delete address
    res = client.delete(f"/api/v1/addresses/{addr2_id}", cookies=cookies)
    assert res.status_code == 204

    res = client.get("/api/v1/addresses", cookies=cookies)
    assert len(res.json()) == 1


def test_checkout_and_order_snapshots():
    """Test full checkout flow: cart -> place order -> snapshot verification -> cart empty."""
    cookies = _login_test_user("9999900002")

    # 1. Fetch products to get variant ID and initial stock
    prod_res = client.get("/api/v1/products")
    assert prod_res.status_code == 200
    products = prod_res.json()
    assert len(products) > 0
    product = products[0]

    detail_res = client.get(f"/api/v1/products/{product['slug']}")
    assert detail_res.status_code == 200
    variant = detail_res.json()["variants"][0]
    initial_stock = variant["stockQuantity"]
    variant_id = variant["id"]
    unit_price = variant["price"]

    # 2. Add variant to cart
    add_res = client.post(
        "/api/v1/cart/items",
        json={
            "product_variant_id": variant_id,
            "quantity": 2,
            "personalization": {"gift_note": "For Sarah"},
        },
        cookies=cookies,
    )
    assert add_res.status_code == 201

    # 3. Create a saved address
    addr_res = client.post(
        "/api/v1/addresses",
        json={
            "name": "Sarah Connor",
            "phone": "9999900002",
            "line1": "100 Cyberdyne Way",
            "city": "Mumbai",
            "state": "Maharashtra",
            "postalCode": "400001",
        },
        cookies=cookies,
    )
    assert addr_res.status_code == 201
    address_id = addr_res.json()["id"]

    # 4. Checkout / Place Order
    checkout_res = client.post(
        "/api/v1/orders",
        json={
            "addressId": address_id,
            "paymentMethod": "COD",
            "notes": "Please leave at reception",
        },
        cookies=cookies,
    )
    assert checkout_res.status_code == 201
    order = checkout_res.json()

    # 5. Verify order properties
    assert order["orderNumber"].startswith("CB-")
    assert order["status"] == "CONFIRMED"
    assert order["paymentStatus"] == "PENDING"
    assert order["paymentMethod"] == "COD"
    assert order["customerName"] == "Sarah Connor"
    assert order["shippingAddress"]["city"] == "Mumbai"
    assert order["subtotal"] == unit_price * 2
    assert order["subtotalPaise"] == unit_price * 2 * 100
    assert order["totalAmount"] == order["subtotal"] + order["shippingFee"]
    assert order["totalAmountPaise"] == (order["subtotal"] + order["shippingFee"]) * 100

    # 6. Verify item snapshot
    assert len(order["items"]) == 1
    item = order["items"][0]
    assert item["sku"] == variant["sku"]
    assert item["unitPrice"] == unit_price
    assert item["quantity"] == 2
    assert item["personalization"]["gift_note"] == "For Sarah"

    # 7. Verify inventory was decremented
    updated_detail = client.get(f"/api/v1/products/{product['slug']}").json()
    updated_variant = [v for v in updated_detail["variants"] if v["id"] == variant_id][0]
    assert updated_variant["stockQuantity"] == initial_stock - 2

    # 8. Verify cart is now empty
    cart_res = client.get("/api/v1/cart", cookies=cookies)
    assert cart_res.status_code == 200
    assert cart_res.json()["items"] == []

    # 9. Verify order listing
    orders_res = client.get("/api/v1/orders", cookies=cookies)
    assert orders_res.status_code == 200
    assert len(orders_res.json()) == 1
    assert orders_res.json()[0]["orderNumber"] == order["orderNumber"]


def test_order_security_and_authorization():
    """Verify that a customer cannot access or manipulate another customer's order."""
    user1_cookies = _login_test_user("9999900010")
    user2_cookies = _login_test_user("9999900020")

    # User 1 places an order
    client.post(
        "/api/v1/cart/items",
        json={"product_id": 1, "quantity": 1},
        cookies=user1_cookies,
    )
    order1_res = client.post(
        "/api/v1/orders",
        json={
            "shippingAddress": {
                "name": "User One",
                "phone": "9999900010",
                "line1": "Street 1",
                "city": "Delhi",
                "state": "Delhi",
                "postalCode": "110001",
            },
            "paymentMethod": "COD",
        },
        cookies=user1_cookies,
    )
    assert order1_res.status_code == 201
    order1_num = order1_res.json()["orderNumber"]

    # User 2 attempts to fetch User 1's order -> 404 (Section 22 safe error)
    forbidden_res = client.get(f"/api/v1/orders/{order1_num}", cookies=user2_cookies)
    assert forbidden_res.status_code == 404

    # User 2 attempts to cancel User 1's order -> 404
    forbidden_cancel = client.post(f"/api/v1/orders/{order1_num}/cancel", cookies=user2_cookies)
    assert forbidden_cancel.status_code == 404


def test_order_tracking_and_cancellation():
    """Test order tracking timeline and customer cancellation with inventory restoration."""
    cookies = _login_test_user("9999900030")

    # Check initial stock of product 2
    p2 = client.get("/api/v1/products/crochet-tulip-bouquet").json()
    initial_stock = p2["variants"][0]["stockQuantity"]
    variant_id = p2["variants"][0]["id"]

    # Add to cart and order
    client.post(
        "/api/v1/cart/items",
        json={"product_variant_id": variant_id, "quantity": 3},
        cookies=cookies,
    )
    order_res = client.post(
        "/api/v1/orders",
        json={
            "shippingAddress": {
                "name": "Rohan Verma",
                "phone": "9999900030",
                "line1": "Park Avenue",
                "city": "Pune",
                "state": "Maharashtra",
                "postalCode": "411001",
            },
            "paymentMethod": "COD",
        },
        cookies=cookies,
    )
    assert order_res.status_code == 201
    order_number = order_res.json()["orderNumber"]

    # Track order
    track_res = client.get(f"/api/v1/orders/{order_number}/tracking", cookies=cookies)
    assert track_res.status_code == 200
    track_data = track_res.json()
    assert track_data["orderNumber"] == order_number
    assert len(track_data["timeline"]) >= 1
    assert track_data["timeline"][0]["status"] == "CONFIRMED"

    # Cancel order
    cancel_res = client.post(f"/api/v1/orders/{order_number}/cancel", cookies=cookies)
    assert cancel_res.status_code == 200
    cancelled_order = cancel_res.json()
    assert cancelled_order["status"] == "CANCELLED"

    # Verify inventory was restored
    p2_updated = client.get("/api/v1/products/crochet-tulip-bouquet").json()
    restored_stock = p2_updated["variants"][0]["stockQuantity"]
    assert restored_stock == initial_stock

    # Check tracking timeline has cancellation record
    track_res2 = client.get(f"/api/v1/orders/{order_number}/tracking", cookies=cookies)
    assert track_res2.status_code == 200
    timeline = track_res2.json()["timeline"]
    assert len(timeline) == 2
    assert timeline[1]["status"] == "CANCELLED"
