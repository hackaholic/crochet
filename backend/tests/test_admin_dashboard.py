"""Integration tests for Figma Admin Dashboard API expansion:
- /api/v1/admin/dashboard/summary
- /api/v1/admin/dashboard/sales
- /api/v1/admin/dashboard/attention
- /api/v1/admin/finance/summary
- /api/v1/admin/finance/sales
- /api/v1/admin/search
- /api/v1/admin/returns & refunds
"""

from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
import pytest

from app.db.session import SessionLocal
from app.main import app
from app.models.catalogue import Product, ProductVariant
from app.models.order import (
    Address,
    Order,
    OrderItem,
    OrderStatus,
    OrderStatusHistory,
    PaymentStatus,
    RefundStatus,
    ReturnRequest,
    ReturnStatus,
)
from app.models.payment import Payment, PaymentRecordStatus
from app.models.user import User, UserIdentity

client = TestClient(app)


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

    res = client.post("/api/v1/auth/google", json={
        "credential": "mock_admin_token_dash",
        "email": admin_email,
        "name": "Store Admin",
        "sub": "admin_sub_dash",
    })
    assert res.status_code == 200
    assert res.json()["user"]["role"] == "ADMIN"
    return dict(res.cookies)


def _login_customer(phone: str = "9999911005") -> dict[str, str]:
    """Helper to authenticate a customer."""
    email = f"cust_{phone}@example.com"
    res = client.post("/api/v1/auth/google", json={
        "credential": f"mock_cust_{phone}",
        "email": email,
        "name": "Test Customer",
        "sub": f"sub_{phone}",
    })
    assert res.status_code == 200
    return dict(res.cookies)


def _create_test_order(
    db,
    order_number: str,
    total_amount: int = 1500,
    subtotal: int = 1400,
    shipping_fee: int = 100,
    discount: int = 0,
    tax: int = 0,
    status: str = "CONFIRMED",
    payment_status: str = "PAID",
    created_at: datetime | None = None,
    sku: str = "TEST-SKU-001",
    customer_name: str = "Aarav Sharma",
    country: str = "IN",
) -> Order:
    created = created_at or datetime.now(timezone.utc)
    order = Order(
        order_number=order_number,
        customer_name=customer_name,
        customer_phone="9876543210",
        customer_email="aarav@example.com",
        status=status,
        payment_status=payment_status,
        payment_method="UPI",
        currency="INR",
        subtotal=subtotal,
        shipping_fee=shipping_fee,
        discount_amount=discount,
        tax_amount=tax,
        total_amount=total_amount,
        shipping_address_json={
            "name": customer_name,
            "city": "Bengaluru",
            "state": "Karnataka",
            "postal_code": "560001",
            "country": country,
        },
        created_at=created,
        updated_at=created,
    )
    db.add(order)
    db.flush()

    item = OrderItem(
        order_id=order.id,
        product_name="Test Crochet Flower",
        sku=sku,
        variant_name="Default",
        unit_price=subtotal,
        quantity=1,
        line_total=subtotal,
        created_at=created,
    )
    db.add(item)

    payment = Payment(
        order_id=order.id,
        provider="mock",
        provider_order_id=f"prov_ord_{order.id}",
        provider_payment_id=f"prov_pay_{order.id}",
        amount=total_amount,
        amount_paise=total_amount * 100,
        status="SUCCESS" if payment_status == "PAID" else "PENDING",
        created_at=created,
        updated_at=created,
    )
    db.add(payment)
    db.commit()
    db.refresh(order)
    return order


def test_admin_dashboard_rbac():
    """Verify RBAC protections on all new dashboard routes."""
    routes = [
        "/api/v1/admin/dashboard/summary",
        "/api/v1/admin/dashboard/sales",
        "/api/v1/admin/dashboard/attention",
        "/api/v1/admin/finance/summary",
        "/api/v1/admin/finance/sales",
        "/api/v1/admin/search?q=test",
        "/api/v1/admin/returns",
    ]

    for route in routes:
        # 1. Unauthenticated -> 401
        client.cookies.clear()
        res = client.get(route)
        assert res.status_code == 401, f"Expected 401 for unauthenticated {route}"

        # 2. Customer -> 403
        client.cookies.clear()
        cust_cookies = _login_customer("9999911005")
        res_cust = client.get(route, cookies=cust_cookies)
        assert res_cust.status_code == 403, f"Expected 403 for customer on {route}"

        # 3. Admin -> 200
        client.cookies.clear()
        admin_cookies = _login_admin("9999900000")
        res_admin = client.get(route, cookies=admin_cookies)
        assert res_admin.status_code == 200, f"Expected 200 for admin on {route}: {res_admin.text}"
    client.cookies.clear()


def test_admin_dashboard_summary_and_comparisons():
    """Verify metrics calculation, period comparison, and recent orders."""
    admin_cookies = _login_admin("9999900000")
    now = datetime.now(timezone.utc)

    with SessionLocal() as db:
        # Create an order in previous period (40 days ago)
        _create_test_order(
            db,
            order_number=f"TEST-PREV-{int(now.timestamp())}",
            total_amount=2000,
            subtotal=1900,
            shipping_fee=100,
            created_at=now - timedelta(days=40),
        )
        # Create order in current period (today)
        _create_test_order(
            db,
            order_number=f"TEST-CURR-{int(now.timestamp())}",
            total_amount=3000,
            subtotal=2900,
            shipping_fee=100,
            created_at=now,
        )

    today_str = (now + timedelta(days=1)).strftime("%Y-%m-%d")
    ten_days_ago_str = (now - timedelta(days=10)).strftime("%Y-%m-%d")
    fifty_days_ago_str = (now - timedelta(days=50)).strftime("%Y-%m-%d")
    thirty_days_ago_str = (now - timedelta(days=30)).strftime("%Y-%m-%d")

    res = client.get(
        f"/api/v1/admin/dashboard/summary?from={ten_days_ago_str}&to={today_str}&compareFrom={fifty_days_ago_str}&compareTo={thirty_days_ago_str}",
        cookies=admin_cookies,
    )
    assert res.status_code == 200
    data = res.json()

    assert "effectiveRange" in data
    assert data["effectiveRange"]["from"] == ten_days_ago_str
    assert data["effectiveRange"]["to"] == today_str
    assert data["totalSales"] >= 3000
    assert data["orderCount"] >= 1
    assert data["averageOrderValue"] > 0
    assert "statusCounts" in data
    assert "recentOrders" in data
    assert len(data["recentOrders"]) <= 10
    assert "inventoryAlerts" in data
    assert "attentionCount" in data

    # Comparison metrics
    assert data["comparison"] is not None
    assert data["comparison"]["previousTotalSales"] >= 2000
    assert data["comparison"]["previousOrderCount"] >= 1


def test_admin_dashboard_sales_series_buckets():
    """Verify sales buckets return continuous data with zero-filled gaps."""
    admin_cookies = _login_admin("9999900000")
    now = datetime.now(timezone.utc)
    from_str = (now - timedelta(days=5)).strftime("%Y-%m-%d")
    to_str = now.strftime("%Y-%m-%d")

    res = client.get(
        f"/api/v1/admin/dashboard/sales?from={from_str}&to={to_str}&interval=daily",
        cookies=admin_cookies,
    )
    assert res.status_code == 200
    data = res.json()

    assert data["interval"] == "daily"
    assert len(data["buckets"]) >= 6  # 5 days ago to today inclusive = 6 days
    for b in data["buckets"]:
        assert "date" in b
        assert "sales" in b
        assert "salesPaise" in b
        assert "orderCount" in b
        assert b["salesPaise"] == b["sales"] * 100


def test_admin_finance_summary_and_sales():
    """Verify finance breakdown, stored tax, and explicit availability markers."""
    admin_cookies = _login_admin("9999900000")
    now = datetime.now(timezone.utc)
    from_str = (now - timedelta(days=7)).strftime("%Y-%m-%d")
    to_str = now.strftime("%Y-%m-%d")

    res = client.get(
        f"/api/v1/admin/finance/summary?from={from_str}&to={to_str}",
        cookies=admin_cookies,
    )
    assert res.status_code == 200
    data = res.json()

    assert "grossSales" in data
    assert "discounts" in data
    assert "shippingCollected" in data
    assert "storedTax" in data
    assert "refunds" in data
    assert data["gatewayFees"] is None
    assert data["gatewayFeesAvailable"] is False  # Never fabricate zeroes for untracked gateway fees
    assert "netRevenue" in data
    assert data["netRevenue"] == data["grossSales"] - data["discounts"] + data["shippingCollected"] + data["storedTax"] - data["refunds"]

    # Test finance sales trend
    res_trend = client.get(
        f"/api/v1/admin/finance/sales?from={from_str}&to={to_str}&interval=daily",
        cookies=admin_cookies,
    )
    assert res_trend.status_code == 200
    trend_data = res_trend.json()
    assert len(trend_data["buckets"]) >= 7


def test_admin_orders_extended_filters_and_sorting():
    """Verify date, country, min/max, SKU, and sort filters on orders list."""
    admin_cookies = _login_admin("9999900000")
    now = datetime.now(timezone.utc)
    unique_suffix = int(now.timestamp())

    with SessionLocal() as db:
        _create_test_order(
            db,
            order_number=f"TEST-ORD-CHEAP-{unique_suffix}",
            total_amount=500,
            subtotal=450,
            shipping_fee=50,
            sku=f"SKU-CHEAP-{unique_suffix}",
            country="IN",
        )
        _create_test_order(
            db,
            order_number=f"TEST-ORD-EXP-{unique_suffix}",
            total_amount=8000,
            subtotal=7900,
            shipping_fee=100,
            sku=f"SKU-EXP-{unique_suffix}",
            country="US",
        )

    # 1. Filter by SKU
    res_sku = client.get(f"/api/v1/admin/orders?sku=SKU-CHEAP-{unique_suffix}", cookies=admin_cookies)
    assert res_sku.status_code == 200
    orders_sku = res_sku.json()["items"]
    assert len(orders_sku) == 1
    assert orders_sku[0]["orderNumber"] == f"TEST-ORD-CHEAP-{unique_suffix}"

    # 2. Filter by minTotal
    res_min = client.get("/api/v1/admin/orders?minTotal=5000", cookies=admin_cookies)
    assert res_min.status_code == 200
    for o in res_min.json()["items"]:
        assert o["totalAmount"] >= 5000

    # 3. Filter by country
    res_country = client.get("/api/v1/admin/orders?country=US", cookies=admin_cookies)
    assert res_country.status_code == 200
    orders_us = [o for o in res_country.json()["items"] if o["orderNumber"] == f"TEST-ORD-EXP-{unique_suffix}"]
    assert len(orders_us) == 1

    # 4. Sort by total_desc
    res_sort = client.get("/api/v1/admin/orders?sortBy=total_desc&pageSize=5", cookies=admin_cookies)
    assert res_sort.status_code == 200
    totals = [o["totalAmount"] for o in res_sort.json()["items"]]
    assert totals == sorted(totals, reverse=True)


def test_admin_dashboard_attention_queue():
    """Verify detection of actionable items: unshipped orders, pending returns, low stock."""
    admin_cookies = _login_admin("9999900000")
    now = datetime.now(timezone.utc)

    with SessionLocal() as db:
        # Create an unshipped order > 48h old
        _create_test_order(
            db,
            order_number=f"TEST-OLD-UNSHIP-{int(now.timestamp())}",
            status="CONFIRMED",
            created_at=now - timedelta(hours=50),
        )

    res = client.get("/api/v1/admin/dashboard/attention", cookies=admin_cookies)
    assert res.status_code == 200
    data = res.json()

    assert "items" in data
    assert data["total"] > 0
    rules = [it["rule"] for it in data["items"]]
    assert "unshipped_over_48h" in rules or "critical_low_stock" in rules


def test_admin_global_search():
    """Verify unified global search across orders, products, and variants."""
    admin_cookies = _login_admin("9999900000")
    now = datetime.now(timezone.utc)
    unique_num = f"SEARCH-{int(now.timestamp())}"

    with SessionLocal() as db:
        _create_test_order(
            db,
            order_number=unique_num,
            customer_name="Distinctive Search Person",
        )

    # 1. Search by order number
    res = client.get(f"/api/v1/admin/search?q={unique_num}", cookies=admin_cookies)
    assert res.status_code == 200
    items = res.json()["items"]
    assert any(it["kind"] == "order" and unique_num in it["title"] for it in items)

    # 2. Search by customer name
    res_cust = client.get("/api/v1/admin/search?q=Distinctive Search Person", cookies=admin_cookies)
    assert res_cust.status_code == 200
    assert any(it["kind"] == "order" for it in res_cust.json()["items"])

    # 3. Search product
    res_prod = client.get("/api/v1/admin/search?q=Bunny", cookies=admin_cookies)
    assert res_prod.status_code == 200
    assert len(res_prod.json()["items"]) > 0


def test_admin_returns_and_refunds_workflow():
    """Verify complete returns and refund lifecycle from request to refund confirmation."""
    import secrets
    admin_cookies = _login_admin("9999900000")
    now = datetime.now(timezone.utc)
    ord_num = f"TEST-RET-ORD-{secrets.token_hex(6)}"

    with SessionLocal() as db:
        order = _create_test_order(
            db,
            order_number=ord_num,
            total_amount=1500,
            subtotal=1400,
            shipping_fee=100,
            payment_status="PAID",
        )

    # 1. Create return request
    create_payload = {
        "orderNumber": ord_num,
        "reason": "DEFECTIVE",
        "reasonDetails": "Petal yarn loose on delivery",
        "adminNotes": "Initiated via customer support chat",
    }
    res_create = client.post("/api/v1/admin/returns", json=create_payload, cookies=admin_cookies)
    assert res_create.status_code == 201
    ret_data = res_create.json()
    ret_num = ret_data["returnNumber"]
    assert ret_data["status"] == "REQUESTED"
    assert ret_data["refundStatus"] == "PENDING"
    assert ret_data["refundAmount"] == 1400

    # 2. List returns and verify inclusion
    res_list = client.get(f"/api/v1/admin/returns?orderNumber={ord_num}", cookies=admin_cookies)
    assert res_list.status_code == 200
    assert len(res_list.json()["items"]) == 1

    # 3. Transition status to APPROVED
    res_approve = client.patch(
        f"/api/v1/admin/returns/{ret_num}/status",
        json={"status": "APPROVED", "note": "Approved by support manager"},
        cookies=admin_cookies,
    )
    assert res_approve.status_code == 200
    assert res_approve.json()["status"] == "APPROVED"

    # 4. Transition status to ITEMS_RECEIVED
    res_rec = client.patch(
        f"/api/v1/admin/returns/{ret_num}/status",
        json={"status": "ITEMS_RECEIVED", "note": "Received back at studio warehouse"},
        cookies=admin_cookies,
    )
    assert res_rec.status_code == 200
    assert res_rec.json()["status"] == "ITEMS_RECEIVED"

    # 5. Execute refund via payment provider abstraction
    res_refund = client.post(
        f"/api/v1/admin/returns/{ret_num}/refund",
        json={"amount": 1400, "note": "Full return refund issued to customer"},
        cookies=admin_cookies,
    )
    assert res_refund.status_code == 200
    refunded_data = res_refund.json()
    assert refunded_data["status"] == "REFUNDED"
    assert refunded_data["refundStatus"] == "COMPLETED"
    assert len(refunded_data["history"]) >= 4

    # 6. Verify refund cannot be duplicated
    res_dup = client.post(
        f"/api/v1/admin/returns/{ret_num}/refund",
        json={"amount": 1400},
        cookies=admin_cookies,
    )
    assert res_dup.status_code == 400
    assert "already been completed" in res_dup.json()["detail"]
