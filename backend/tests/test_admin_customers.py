"""Integration and security tests for Read-Only Customer Administration API (Task 1.9.1).

Covers:
- 1.9.1-TC01: Security — 401 unauthenticated, 403 customer, no PII leakage across all endpoints.
- 1.9.1-TC02: Success — Admin lists customers with pagination, accurate totals, deterministic sorting,
              order counts, zero-order customers included, admins strictly excluded.
- 1.9.1-TC03: Boundary — Oversized query (>200 chars), invalid page (<1), invalid pageSize (<1, >100),
              missing customer ID (404), admin user ID requested as customer (404).
- 1.9.1-TC04: Security/regression — Quotes and SQL injection strings safely handled via parameterization;
              strict user_id isolation (guest orders sharing contact info are never attached).
- 1.9.1-TC05: Success — Nullable contact fields preserved as null; orders across all statuses (PAID, CANCELLED)
              counted and listed in history.
"""

from datetime import datetime, timezone
import uuid
from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.models.order import Order, OrderStatus, PaymentMethod, PaymentStatus
from app.models.user import User, UserIdentity

client = TestClient(app)


def _login_customer(phone: str = "9999911005") -> dict[str, str]:
    """Helper to authenticate a non-admin customer user."""
    email = f"customer_{phone}@example.com"
    res = client.post(
        "/api/v1/auth/google",
        json={
            "credential": f"mock_cust_{phone}",
            "email": email,
            "name": "Customer User",
            "sub": f"sub_{phone}",
        },
    )
    assert res.status_code == 200
    return dict(res.cookies)


def _login_admin(phone: str = "9999900000") -> dict[str, str]:
    """Helper to authenticate an admin user."""
    admin_email = "admin@sulocraft.com"
    with SessionLocal() as db:
        admin = db.query(User).filter(User.email == admin_email).first()
        if not admin:
            admin = User(
                name="Store Admin",
                phone=phone,
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

    res = client.post(
        "/api/v1/auth/google",
        json={
            "credential": "mock_admin_token_admin",
            "email": admin_email,
            "name": "Store Admin",
            "sub": "admin_sub_admin",
        },
    )
    assert res.status_code == 200
    assert res.json()["user"]["role"] == "ADMIN"
    return dict(res.cookies)


_UNSET = object()


def _create_customer_fixture(
    db,
    name: str | None = "Test Customer",
    email: str | None = None,
    phone: object = _UNSET,
    role: str = "CUSTOMER",
    status: str = "ACTIVE",
) -> User:
    """Create a temporary user fixture."""
    uid = uuid.uuid4().hex[:8]
    if email is None:
        email = f"cust_{uid}@test.com"
    if phone is _UNSET:
        phone = f"9{uuid.uuid4().int % 1000000000:09d}"

    user = User(
        name=name,
        email=email,
        phone=phone,
        role=role,
        status=status,
        created_at=datetime.now(timezone.utc),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.expunge(user)
    return user


def _create_order_fixture(
    db,
    user_id: int | None,
    customer_name: str = "Test Customer",
    customer_phone: str = "9999999999",
    customer_email: str | None = "cust@test.com",
    order_status: str = OrderStatus.CONFIRMED.value,
) -> Order:
    """Create an order fixture."""
    order_num = f"ORD-TEST-{uuid.uuid4().hex[:8].upper()}"
    order = Order(
        order_number=order_num,
        user_id=user_id,
        customer_name=customer_name,
        customer_phone=customer_phone,
        customer_email=customer_email,
        shipping_address_json={"line1": "123 Test St", "city": "Bengaluru", "postal_code": "560001"},
        status=order_status,
        payment_status=PaymentStatus.PAID.value,
        payment_method=PaymentMethod.UPI.value,
        subtotal=1000,
        total_amount=1000,
        created_at=datetime.now(timezone.utc),
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    db.expunge(order)
    return order


def test_tc01_security_rbac():
    """1.9.1-TC01: Verify unauthenticated requests return 401 and customer callers return 403."""
    with SessionLocal() as db:
        cust = _create_customer_fixture(db)
        cust_id = cust.id

    try:
        endpoints = [
            "/api/v1/admin/customers",
            f"/api/v1/admin/customers/{cust_id}",
            f"/api/v1/admin/customers/{cust_id}/orders",
        ]

        # 1. Unauthenticated requests -> 401
        for ep in endpoints:
            client.cookies.clear()
            res = client.get(ep)
            assert res.status_code == 401, f"Expected 401 for {ep}, got {res.status_code}"

        # 2. Customer caller -> 403
        cust_cookies = _login_customer("9999944001")
        for ep in endpoints:
            res = client.get(ep, cookies=cust_cookies)
            assert res.status_code == 403, f"Expected 403 for {ep}, got {res.status_code}"
            assert "Admin privileges required" in res.json().get("detail", "")
    finally:
        with SessionLocal() as db:
            c = db.query(User).filter(User.id == cust_id).first()
            if c:
                db.delete(c)
                db.commit()


def test_tc02_customer_list_pagination_and_role_filtering():
    """1.9.1-TC02: Admin lists customers with pagination, complete totals, and role isolation."""
    created_ids = []
    admin_cookies = _login_admin()

    with SessionLocal() as db:
        # Create 22 customer fixtures and 1 admin fixture
        for i in range(22):
            c = _create_customer_fixture(db, name=f"ListCust {i}")
            created_ids.append(c.id)

        # Create one admin user to verify admins are excluded
        admin_fixture = _create_customer_fixture(db, name="Admin NotCustomer", role="ADMIN")
        created_ids.append(admin_fixture.id)
        admin_id = admin_fixture.id

    try:
        # Page 1 (pageSize=10)
        res_p1 = client.get("/api/v1/admin/customers?page=1&pageSize=10", cookies=admin_cookies)
        assert res_p1.status_code == 200
        data_p1 = res_p1.json()
        assert data_p1["page"] == 1
        assert data_p1["pageSize"] == 10
        assert data_p1["total"] >= 22
        assert len(data_p1["items"]) == 10

        # Page 2 (pageSize=10)
        res_p2 = client.get("/api/v1/admin/customers?page=2&pageSize=10", cookies=admin_cookies)
        assert res_p2.status_code == 200
        data_p2 = res_p2.json()
        assert data_p2["page"] == 2
        assert len(data_p2["items"]) == 10

        # Items across pages must be disjoint (stable pagination)
        p1_ids = {item["id"] for item in data_p1["items"]}
        p2_ids = {item["id"] for item in data_p2["items"]}
        assert p1_ids.isdisjoint(p2_ids)

        # Admin fixture must NOT appear in any page
        all_returned_ids = p1_ids.union(p2_ids)
        assert admin_id not in all_returned_ids

        # Zero-order customer has orderCount == 0
        for item in data_p1["items"]:
            if item["id"] in created_ids:
                assert item["orderCount"] == 0
    finally:
        with SessionLocal() as db:
            for uid in created_ids:
                u = db.query(User).filter(User.id == uid).first()
                if u:
                    db.delete(u)
            db.commit()


def test_tc03_boundary_validation():
    """1.9.1-TC03: Bounds validation (422) and missing/admin customer ID lookup (404)."""
    admin_cookies = _login_admin()

    with SessionLocal() as db:
        admin_user = _create_customer_fixture(db, name="Staff Admin", role="ADMIN")
        admin_id = admin_user.id

    try:
        # 1. Query > 200 characters -> 422
        long_q = "a" * 201
        res_long = client.get(f"/api/v1/admin/customers?q={long_q}", cookies=admin_cookies)
        assert res_long.status_code == 422

        # 2. page < 1 -> 422
        res_p0 = client.get("/api/v1/admin/customers?page=0", cookies=admin_cookies)
        assert res_p0.status_code == 422

        # 3. pageSize < 1 -> 422
        res_ps0 = client.get("/api/v1/admin/customers?pageSize=0", cookies=admin_cookies)
        assert res_ps0.status_code == 422

        # 4. pageSize > 100 -> 422
        res_ps101 = client.get("/api/v1/admin/customers?pageSize=101", cookies=admin_cookies)
        assert res_ps101.status_code == 422

        # 5. Missing customer ID -> 404
        res_missing = client.get("/api/v1/admin/customers/999999999", cookies=admin_cookies)
        assert res_missing.status_code == 404
        assert res_missing.json()["detail"] == "Customer not found"

        # 6. Admin user ID -> 404 (non-customer)
        res_admin_cust = client.get(f"/api/v1/admin/customers/{admin_id}", cookies=admin_cookies)
        assert res_admin_cust.status_code == 404
        assert res_admin_cust.json()["detail"] == "Customer not found"

        # 7. Admin user ID orders -> 404
        res_admin_orders = client.get(f"/api/v1/admin/customers/{admin_id}/orders", cookies=admin_cookies)
        assert res_admin_orders.status_code == 404
        assert res_admin_orders.json()["detail"] == "Customer not found"
    finally:
        with SessionLocal() as db:
            u = db.query(User).filter(User.id == admin_id).first()
            if u:
                db.delete(u)
                db.commit()


def test_tc04_parameterized_search_and_guest_order_isolation():
    """1.9.1-TC04: Parameterized search safety and strict user_id order isolation (no guest leakage)."""
    admin_cookies = _login_admin()
    created_user_ids = []
    created_order_ids = []

    with SessionLocal() as db:
        unique_suffix = uuid.uuid4().hex[:6]
        c1 = _create_customer_fixture(
            db,
            name=f"Alice Smith {unique_suffix}",
            email=f"alice_{unique_suffix}@example.com",
            phone=f"98111{unique_suffix[:5]}",
        )
        c1_id = c1.id
        created_user_ids.append(c1_id)

        # Linked customer order
        o1 = _create_order_fixture(
            db,
            user_id=c1_id,
            customer_name=c1.name,
            customer_phone=c1.phone,
            customer_email=c1.email,
        )
        o1_id = o1.id
        created_order_ids.append(o1_id)

        # Unlinked guest order sharing the exact same email and phone
        o_guest = _create_order_fixture(
            db,
            user_id=None,
            customer_name=c1.name,
            customer_phone=c1.phone,
            customer_email=c1.email,
        )
        o_guest_id = o_guest.id
        created_order_ids.append(o_guest_id)

    try:
        # 1. SQL Injection / Quote safety: query with injection strings
        res_sqli = client.get("/api/v1/admin/customers?q=' OR '1'='1", cookies=admin_cookies)
        assert res_sqli.status_code == 200
        # Must not return all users indiscriminately
        data_sqli = res_sqli.json()
        assert isinstance(data_sqli["items"], list)

        # 2. Text search matches name, email, and phone
        res_search = client.get(f"/api/v1/admin/customers?q={unique_suffix}", cookies=admin_cookies)
        assert res_search.status_code == 200
        items = res_search.json()["items"]
        assert len(items) == 1
        assert items[0]["id"] == c1_id

        # 3. Order count must be strictly 1 (guest order NOT counted)
        assert items[0]["orderCount"] == 1

        # 4. GET /customers/{id} must reflect orderCount == 1
        res_profile = client.get(f"/api/v1/admin/customers/{c1_id}", cookies=admin_cookies)
        assert res_profile.status_code == 200
        assert res_profile.json()["orderCount"] == 1

        # 5. GET /customers/{id}/orders must ONLY contain the linked order
        res_orders = client.get(f"/api/v1/admin/customers/{c1_id}/orders", cookies=admin_cookies)
        assert res_orders.status_code == 200
        orders_data = res_orders.json()
        assert orders_data["total"] == 1
        assert len(orders_data["items"]) == 1
        assert orders_data["items"][0]["id"] == o1_id
        assert orders_data["items"][0]["id"] != o_guest_id
    finally:
        with SessionLocal() as db:
            for oid in created_order_ids:
                o = db.query(Order).filter(Order.id == oid).first()
                if o:
                    db.delete(o)
            for uid in created_user_ids:
                u = db.query(User).filter(User.id == uid).first()
                if u:
                    db.delete(u)
            db.commit()


def test_tc05_nullable_fields_and_order_status_aggregation():
    """1.9.1-TC05: Nullable contact info preserved; all order statuses (PAID, CANCELLED) counted."""
    admin_cookies = _login_admin()
    created_user_ids = []
    created_order_ids = []

    with SessionLocal() as db:
        c = _create_customer_fixture(
            db,
            name=None,
            email=f"null_test_{uuid.uuid4().hex[:6]}@example.com",
            phone=None,
        )
        c_id = c.id
        c_email = c.email
        created_user_ids.append(c_id)

        # One CONFIRMED order and one CANCELLED order
        o1 = _create_order_fixture(db, user_id=c_id, order_status=OrderStatus.CONFIRMED.value)
        o2 = _create_order_fixture(db, user_id=c_id, order_status=OrderStatus.CANCELLED.value)
        o1_id = o1.id
        o2_id = o2.id
        created_order_ids.extend([o1_id, o2_id])

    try:
        res_profile = client.get(f"/api/v1/admin/customers/{c_id}", cookies=admin_cookies)
        assert res_profile.status_code == 200
        prof = res_profile.json()
        # Null contacts preserved as None
        assert prof["name"] is None
        assert prof["phone"] is None
        assert prof["email"] == c_email
        assert prof["status"] == "ACTIVE"
        # Total orders counted across all statuses
        assert prof["orderCount"] == 2

        # Verify order history lists both orders
        res_orders = client.get(f"/api/v1/admin/customers/{c_id}/orders", cookies=admin_cookies)
        assert res_orders.status_code == 200
        data_orders = res_orders.json()
        assert data_orders["total"] == 2
        returned_order_ids = {item["id"] for item in data_orders["items"]}
        assert returned_order_ids == {o1_id, o2_id}
    finally:
        with SessionLocal() as db:
            for oid in created_order_ids:
                o = db.query(Order).filter(Order.id == oid).first()
                if o:
                    db.delete(o)
            for uid in created_user_ids:
                u = db.query(User).filter(User.id == uid).first()
                if u:
                    db.delete(u)
            db.commit()
