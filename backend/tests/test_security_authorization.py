"""Security Integration Tests: Authorization and Broken Access Control (IDOR, RBAC).

Conforms to Work 009 Task 9.5 and Audit Policy Level 1 & 2 requirements.
Ensures zero Broken Access Control:
- Customer A cannot access, read, or modify Customer B's orders, addresses, cart items, or payments.
- Path parameter manipulation returns 404 or 403, NEVER 200.
- Unauthenticated requests to protected endpoints return 401.
- Regular customers attempting to access administrative endpoints return 403.
"""

from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.models.catalogue import Product, ProductVariant
from app.models.order import Address, Order
from app.models.user import User, UserIdentity


def _create_authenticated_client(phone: str) -> tuple[TestClient, dict[str, str]]:
    """Helper to create an independent TestClient session for a customer."""
    client = TestClient(app)
    email = f"cust_{phone}@example.com"
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


def _create_admin_client(email: str = "sec_admin@sulocraft.com") -> tuple[TestClient, dict[str, str]]:
    """Helper to create an independent TestClient session for an admin."""
    client = TestClient(app)
    with SessionLocal() as db:
        admin = db.query(User).filter(User.email == email).first()
        if not admin:
            admin = User(
                name="Security Admin",
                phone="9999900999",
                email=email,
                role="ADMIN",
                status="ACTIVE",
            )
            db.add(admin)
            db.flush()
            db.add(UserIdentity(user_id=admin.id, provider="email", provider_subject=email))
            db.commit()
        elif admin.role != "ADMIN":
            admin.role = "ADMIN"
            db.commit()

    res = client.post(
        "/api/v1/auth/google",
        json={
            "credential": f"mock_admin_token_{email}",
            "email": email,
            "name": "Security Admin",
            "sub": f"admin_sub_{email}",
        },
    )
    assert res.status_code == 200
    assert res.json()["user"]["role"] == "ADMIN"
    return client, dict(res.cookies)


def test_idor_order_detail_and_tracking_prevented():
    """Verify Customer B cannot access Customer A's order details or tracking timeline."""
    client_a, _ = _create_authenticated_client("9999911001")
    client_b, _ = _create_authenticated_client("9999911002")
    unauth_client = TestClient(app)

    # User A adds item to cart and creates an order
    client_a.post("/api/v1/cart/items", json={"product_id": 1, "quantity": 1})
    order_res = client_a.post(
        "/api/v1/orders",
        json={
            "shippingAddress": {
                "name": "Customer A",
                "phone": "9999911001",
                "line1": "123 Security Lane",
                "city": "Bengaluru",
                "state": "Karnataka",
                "postalCode": "560001",
            },
            "paymentMethod": "COD",
        },
    )
    assert order_res.status_code == 201
    order_data = order_res.json()
    order_id = order_data["id"]
    order_number = order_data["orderNumber"]

    # 1. User A can view their own order
    a_res = client_a.get(f"/api/v1/orders/{order_number}")
    assert a_res.status_code == 200
    assert a_res.json()["orderNumber"] == order_number

    # 2. User B attempts to access User A's order by orderNumber -> MUST return 404 (safe error)
    b_num_res = client_b.get(f"/api/v1/orders/{order_number}")
    assert b_num_res.status_code == 404, "IDOR Vulnerability: User B accessed User A's order by order_number!"

    # 3. User B attempts to access User A's order by integer ID -> MUST return 404
    b_id_res = client_b.get(f"/api/v1/orders/{order_id}")
    assert b_id_res.status_code == 404, "IDOR Vulnerability: User B accessed User A's order by integer id!"

    # 4. Unauthenticated visitor attempts to access User A's order -> MUST return 404
    unauth_res = unauth_client.get(f"/api/v1/orders/{order_number}")
    assert unauth_res.status_code == 404, "Unauthenticated visitor accessed order without authorization!"

    # 5. User B attempts to track User A's order -> MUST return 404
    b_track_res = client_b.get(f"/api/v1/orders/{order_number}/tracking")
    assert b_track_res.status_code == 404, "IDOR Vulnerability: User B accessed User A's order tracking!"


def test_idor_order_cancellation_prevented():
    """Verify Customer B cannot cancel Customer A's order."""
    client_a, _ = _create_authenticated_client("9999911003")
    client_b, _ = _create_authenticated_client("9999911004")
    unauth_client = TestClient(app)

    client_a.post("/api/v1/cart/items", json={"product_id": 1, "quantity": 1})
    order_res = client_a.post(
        "/api/v1/orders",
        json={
            "shippingAddress": {
                "name": "Customer A",
                "phone": "9999911003",
                "line1": "123 Security Lane",
                "city": "Bengaluru",
                "state": "Karnataka",
                "postalCode": "560001",
            },
            "paymentMethod": "COD",
        },
    )
    assert order_res.status_code == 201
    order_number = order_res.json()["orderNumber"]

    # User B attempts to cancel User A's order
    cancel_res = client_b.post(f"/api/v1/orders/{order_number}/cancel")
    assert cancel_res.status_code == 404, "IDOR Vulnerability: User B cancelled User A's order!"

    # Unauthenticated visitor attempts to cancel User A's order -> 401 or 404 safe rejection
    unauth_cancel = unauth_client.post(f"/api/v1/orders/{order_number}/cancel")
    assert unauth_cancel.status_code in (401, 404)


def test_idor_address_operations_prevented():
    """Verify Customer B cannot view, edit, set default, or delete Customer A's saved addresses."""
    client_a, _ = _create_authenticated_client("9999911005")
    client_b, _ = _create_authenticated_client("9999911006")

    # User A creates an address
    addr_res = client_a.post(
        "/api/v1/addresses",
        json={
            "name": "Customer A Address",
            "phone": "9999911005",
            "line1": "Flat 101, Secret Residency",
            "city": "Bengaluru",
            "state": "Karnataka",
            "postalCode": "560001",
            "isDefault": True,
        },
    )
    assert addr_res.status_code == 201
    addr_id = addr_res.json()["id"]

    # 1. User B lists addresses -> User A's address is NOT in User B's list
    b_list = client_b.get("/api/v1/addresses")
    assert b_list.status_code == 200
    b_ids = [a["id"] for a in b_list.json()]
    assert addr_id not in b_ids

    # 2. User B attempts to update User A's address -> 404
    b_update = client_b.patch(
        f"/api/v1/addresses/{addr_id}",
        json={"line1": "Hacked Address Line"},
    )
    assert b_update.status_code == 404, "IDOR Vulnerability: User B modified User A's address!"

    # 3. User B attempts to set User A's address as default -> 404
    b_default = client_b.post(f"/api/v1/addresses/{addr_id}/default")
    assert b_default.status_code == 404, "IDOR Vulnerability: User B set User A's address as default!"

    # 4. User B attempts to delete User A's address -> 404
    b_delete = client_b.delete(f"/api/v1/addresses/{addr_id}")
    assert b_delete.status_code == 404, "IDOR Vulnerability: User B deleted User A's address!"


def test_idor_checkout_with_foreign_address_prevented():
    """Verify Customer B cannot hijack Customer A's address during checkout."""
    client_a, _ = _create_authenticated_client("9999911007")
    client_b, _ = _create_authenticated_client("9999911008")

    # User A creates an address
    addr_res = client_a.post(
        "/api/v1/addresses",
        json={
            "name": "Customer A VIP",
            "phone": "9999911007",
            "line1": "VIP Villa 1",
            "city": "Bengaluru",
            "state": "Karnataka",
            "postalCode": "560001",
        },
    )
    assert addr_res.status_code == 201
    user_a_addr_id = addr_res.json()["id"]

    # User B adds item to cart
    client_b.post("/api/v1/cart/items", json={"product_id": 1, "quantity": 1})

    # User B attempts to place order referencing User A's addressId
    order_res = client_b.post(
        "/api/v1/orders",
        json={
            "addressId": user_a_addr_id,
            "paymentMethod": "COD",
        },
    )
    assert order_res.status_code == 404, "IDOR Vulnerability: User B checked out with User A's addressId!"


def test_idor_cart_item_tampering_prevented():
    """Verify Customer B cannot alter or delete items from Customer A's cart."""
    client_a, cookies_a = _create_authenticated_client("9999911009")
    client_b, cookies_b = _create_authenticated_client("9999911010")

    # User A adds item to cart
    add_res = client_a.post("/api/v1/cart/items", json={"product_id": 1, "quantity": 2})
    assert add_res.status_code == 201
    cart_items = add_res.json()["items"]
    user_a_cart_item_id = cart_items[0]["id"]

    # User B attempts to update User A's cart item -> 404
    update_res = client_b.patch(
        f"/api/v1/cart/items/{user_a_cart_item_id}",
        json={"quantity": 10},
    )
    assert update_res.status_code == 404, "IDOR Vulnerability: User B updated User A's cart item!"

    # User B attempts to delete User A's cart item -> 404
    delete_res = client_b.delete(f"/api/v1/cart/items/{user_a_cart_item_id}")
    assert delete_res.status_code == 404, "IDOR Vulnerability: User B deleted User A's cart item!"

    # User B attempts to access User A's cart by presenting User A's guest token
    guest_token_a = client_a.cookies.get("guest_cart_token")
    if guest_token_a:
        b_hijack_res = client_b.get("/api/v1/cart", headers={"X-Cart-Token": guest_token_a})
        # If User B already has a cart, they get their own cart; if not, they must NOT see User A's items
        if b_hijack_res.status_code == 200:
            b_item_ids = [it["id"] for it in b_hijack_res.json()["items"]]
            assert user_a_cart_item_id not in b_item_ids, "Guest cart token hijacked User A's cart!"


def test_idor_payments_prevented():
    """Verify Customer B cannot create payment intent or verify payments for Customer A's order."""
    client_a, _ = _create_authenticated_client("9999911011")
    client_b, _ = _create_authenticated_client("9999911012")
    unauth_client = TestClient(app)

    # User A places order
    client_a.post("/api/v1/cart/items", json={"product_id": 1, "quantity": 1})
    order_res = client_a.post(
        "/api/v1/orders",
        json={
            "shippingAddress": {
                "name": "Customer A",
                "phone": "9999911011",
                "line1": "123 Security Lane",
                "city": "Bengaluru",
                "state": "Karnataka",
                "postalCode": "560001",
            },
            "paymentMethod": "UPI",
        },
    )
    assert order_res.status_code == 201
    order_data = order_res.json()
    order_id = order_data["id"]
    order_number = order_data["orderNumber"]

    # User B attempts to create payment intent for User A's order -> 404
    b_intent = client_b.post(
        "/api/v1/payments/intent",
        json={"orderId": order_id},
    )
    assert b_intent.status_code == 404, "IDOR Vulnerability: User B created payment intent for User A's order!"

    # Unauthenticated visitor attempts to create payment intent -> 404
    unauth_intent = unauth_client.post(
        "/api/v1/payments/intent",
        json={"orderNumber": order_number},
    )
    assert unauth_intent.status_code == 404


def test_admin_rbac_protection():
    """Verify unauthenticated requests return 401 and regular customer requests return 403 on admin routes."""
    client_cust, _ = _create_authenticated_client("9999911013")
    client_admin, _ = _create_admin_client()
    unauth_client = TestClient(app)

    admin_endpoints = [
        ("GET", "/api/v1/admin/dashboard/summary", None),
        ("GET", "/api/v1/admin/orders", None),
        ("POST", "/api/v1/admin/products", {"name": "Hacked", "slug": "hacked-product", "price": 100}),
        ("POST", "/api/v1/admin/occasions", {"name": "Hacked Occasion", "slug": "hacked-occasion"}),
        ("GET", "/api/v1/admin/coupons", None),
        ("GET", "/api/v1/admin/reviews", None),
        ("GET", "/api/v1/admin/returns", None),
    ]

    for method, path, payload in admin_endpoints:
        # 1. Unauthenticated -> 401
        if method == "GET":
            unauth_res = unauth_client.get(path)
        else:
            unauth_res = unauth_client.post(path, json=payload)
        assert unauth_res.status_code == 401, f"Unauthenticated request to {path} did not return 401! Got {unauth_res.status_code}"

        # 2. Regular Customer -> 403 Forbidden
        if method == "GET":
            cust_res = client_cust.get(path)
        else:
            cust_res = client_cust.post(path, json=payload)
        assert cust_res.status_code == 403, f"Customer request to {path} did not return 403 Forbidden! Got {cust_res.status_code}"

    # 3. Admin user -> 200 on dashboard summary endpoint
    admin_res = client_admin.get("/api/v1/admin/dashboard/summary")
    assert admin_res.status_code == 200
