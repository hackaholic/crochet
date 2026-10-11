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


def test_admin_finance_categories_destinations_products_and_trends():
    """Verify 1.14.2 (categories), 1.14.3 (destinations), 1.14.4 (top products), and 1.14.5 (trends)."""
    admin_cookies = _login_admin("9999900000")
    now = datetime.now(timezone.utc)
    from_str = (now - timedelta(days=7)).strftime("%Y-%m-%d")
    to_str = now.strftime("%Y-%m-%d")

    # 1. Categories
    res_cat = client.get(
        f"/api/v1/admin/finance/categories?from={from_str}&to={to_str}",
        cookies=admin_cookies,
    )
    assert res_cat.status_code == 200
    cat_data = res_cat.json()
    assert "categories" in cat_data
    assert "totalGrossSales" in cat_data
    assert "totalUnitsSold" in cat_data
    # Verify shares sum to <= 100% and grossSalesPaise matches
    for cat in cat_data["categories"]:
        assert cat["grossSalesPaise"] == cat["grossSales"] * 100
        assert 0.0 <= cat["salesSharePct"] <= 100.0

    # 2. Destinations
    res_dest = client.get(
        f"/api/v1/admin/finance/destinations?from={from_str}&to={to_str}",
        cookies=admin_cookies,
    )
    assert res_dest.status_code == 200
    dest_data = res_dest.json()
    assert "countries" in dest_data
    assert "totalOrders" in dest_data
    for country in dest_data["countries"]:
        assert country["grossSalesPaise"] == country["grossSales"] * 100
        if country["countryCode"] == "IN":
            assert isinstance(country["regions"], list)
            for reg in country["regions"]:
                assert reg["grossSalesPaise"] == reg["grossSales"] * 100

    # 3. Top Products
    res_top = client.get(
        f"/api/v1/admin/finance/top-products?from={from_str}&to={to_str}&metric=revenue&limit=5",
        cookies=admin_cookies,
    )
    assert res_top.status_code == 200
    top_data = res_top.json()
    assert "items" in top_data
    assert top_data["rankingMetric"] == "revenue"
    for item in top_data["items"]:
        assert item["productRevenuePaise"] == item["productRevenue"] * 100
        assert item["unitsSold"] >= 0

    # 4. Finance Trends and Operational Indicators
    res_trends = client.get(
        f"/api/v1/admin/finance/trends?from={from_str}&to={to_str}",
        cookies=admin_cookies,
    )
    assert res_trends.status_code == 200
    trends_data = res_trends.json()
    assert "grossSales" in trends_data
    assert "netRevenue" in trends_data
    assert "orders" in trends_data
    assert "averageOrderValue" in trends_data
    assert "operationalIndicators" in trends_data
    op = trends_data["operationalIndicators"]
    assert "pendingPaymentCount" in op
    assert "pendingPaymentTotal" in op
    assert "cancelledCount" in op
    assert "refundedCount" in op
    assert "fulfillmentStates" in op


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


def test_finance_analytics_authorization_and_filter_denial():
    """1.14.6-TC05: aggregate endpoints deny non-admins and invalid filters."""
    endpoints = ['categories', 'destinations', 'top-products', 'trends']
    with SessionLocal() as db:
        before = db.query(Order).count()
    client.cookies.clear()
    for endpoint in endpoints:
        response = client.get(f'/api/v1/admin/finance/{endpoint}')
        assert response.status_code == 401
        assert 'grossSales' not in response.json()
    customer = _login_customer()
    for endpoint in endpoints:
        response = client.get(f'/api/v1/admin/finance/{endpoint}', cookies=customer)
        assert response.status_code == 403
        assert 'countries' not in response.json()
    admin = _login_admin()
    for path in ['categories?sortBy=invalid', 'categories?limit=201',
                 'top-products?metric=invalid', 'top-products?limit=101',
                 'trends?from=not-a-date']:
        assert client.get(f'/api/v1/admin/finance/{path}', cookies=admin).status_code in (400, 422)
    with SessionLocal() as db:
        assert db.query(Order).count() == before

@pytest.mark.parametrize("endpoint", ["categories", "destinations", "top-products", "trends"])
def test_finance_acceptance_excludes_unpaid_prepaid(endpoint):
    """TC-FIN-27-01: only paid prepaid and active COD recognize sales."""
    cookies = _login_admin()
    stamp = datetime(2050, 1, 10, 6, tzinfo=timezone.utc)
    with SessionLocal() as db:
        _create_test_order(db, "QA-FIN-PAID", subtotal=1000, shipping_fee=0,
                           total_amount=1000, created_at=stamp)
        _create_test_order(db, "QA-FIN-UNPAID", subtotal=9000, shipping_fee=0,
                           total_amount=9000, payment_status="PENDING", created_at=stamp)
        _create_test_order(db, "QA-FIN-CANCELLED", subtotal=8000, shipping_fee=0,
                           total_amount=8000, status="CANCELLED", created_at=stamp)
        cod = _create_test_order(db, "QA-FIN-COD", subtotal=500, shipping_fee=0,
                                total_amount=500, payment_status="PENDING", created_at=stamp)
        cod.payment_method = "COD"
        db.commit()
    response = client.get(f"/api/v1/admin/finance/{endpoint}",
                          params={"from": "2050-01-10", "to": "2050-01-10"}, cookies=cookies)
    assert response.status_code == 200
    body = response.json()
    if endpoint in ("categories", "destinations"):
        assert body["totalGrossSalesPaise"] == 150000
    elif endpoint == "top-products":
        assert sum(item["productRevenuePaise"] for item in body["items"]) == 150000
    else:
        assert body["grossSales"]["currentPaise"] == 150000
        assert body["orders"]["current"] == 2


@pytest.mark.parametrize("endpoint", ["categories", "destinations", "trends"])
def test_finance_acceptance_discount_does_not_inflate_gross(endpoint):
    """TC-FIN-27-02: checkout subtotal is gross, before order discount."""
    cookies = _login_admin()
    with SessionLocal() as db:
        _create_test_order(db, "QA-FIN-DISCOUNT", subtotal=1000, discount=200,
                           shipping_fee=100, total_amount=900,
                           created_at=datetime(2050, 1, 10, 6, tzinfo=timezone.utc))
    response = client.get(f"/api/v1/admin/finance/{endpoint}",
                          params={"from": "2050-01-10", "to": "2050-01-10"}, cookies=cookies)
    assert response.status_code == 200
    body = response.json()
    if endpoint == "trends":
        assert body["grossSales"]["currentPaise"] == 100000
        assert body["netRevenue"]["currentPaise"] == 90000
    else:
        assert body["totalGrossSalesPaise"] == 100000


def test_finance_acceptance_summary_and_sales_reconciliation():
    """TC-FIN-27-03: summary and series bucket totals reconcile with categories, destinations, trends."""
    cookies = _login_admin()
    stamp = datetime(2050, 3, 15, 8, tzinfo=timezone.utc)
    with SessionLocal() as db:
        # 1. Paid prepaid order
        _create_test_order(db, "QA-FIN-REC-PAID", subtotal=2000, discount=300,
                           shipping_fee=100, tax=50, total_amount=1850,
                           payment_status="PAID", created_at=stamp)
        # 2. Active COD order
        cod = _create_test_order(db, "QA-FIN-REC-COD", subtotal=1500, discount=0,
                                 shipping_fee=100, tax=0, total_amount=1600,
                                 payment_status="PENDING", created_at=stamp)
        cod.payment_method = "COD"
        # 3. Unpaid prepaid order (must be excluded from recognized)
        _create_test_order(db, "QA-FIN-REC-UNPAID", subtotal=5000, discount=500,
                           shipping_fee=0, tax=0, total_amount=4500,
                           payment_status="PENDING", created_at=stamp)
        # 4. Completed return / refund
        ret_ord = _create_test_order(db, "QA-FIN-REC-REF", subtotal=1000, discount=0,
                                     shipping_fee=0, tax=0, total_amount=1000,
                                     payment_status="PAID", created_at=stamp)
        ret = ReturnRequest(
            return_number="RET-QA-FIN-REC",
            order_id=ret_ord.id,
            user_id=None,
            reason="DEFECTIVE",
            status=ReturnStatus.REFUNDED.value,
            refund_status=RefundStatus.COMPLETED.value,
            refund_amount=400,
            refund_amount_paise=40000,
            created_at=stamp,
            updated_at=stamp,
        )
        db.add(ret)
        db.commit()

    params = {"from": "2050-03-15", "to": "2050-03-15"}
    # Summary
    res_sum = client.get("/api/v1/admin/finance/summary", params=params, cookies=cookies)
    assert res_sum.status_code == 200
    sum_data = res_sum.json()

    # Recognized orders = PAID (2000), COD (1500), REF order (1000) => Gross = 4500
    expected_gross = 4500
    expected_discounts = 300
    expected_shipping = 200
    expected_tax = 50
    expected_refunds = 400
    expected_net = expected_gross - expected_discounts + expected_shipping + expected_tax - expected_refunds

    assert sum_data["grossSales"] == expected_gross
    assert sum_data["grossSalesPaise"] == expected_gross * 100
    assert sum_data["discounts"] == expected_discounts
    assert sum_data["shippingCollected"] == expected_shipping
    assert sum_data["storedTax"] == expected_tax
    assert sum_data["refunds"] == expected_refunds
    assert sum_data["netRevenue"] == expected_net
    assert sum_data["netRevenuePaise"] == expected_net * 100
    assert sum_data["orderCount"] == 3
    assert sum_data["refundCount"] == 1

    # Sales series
    res_sales = client.get("/api/v1/admin/finance/sales", params={**params, "interval": "daily"}, cookies=cookies)
    assert res_sales.status_code == 200
    sales_data = res_sales.json()
    assert len(sales_data["buckets"]) == 1
    b = sales_data["buckets"][0]
    assert b["grossSales"] == expected_gross
    assert b["discounts"] == expected_discounts
    assert b["refunds"] == expected_refunds
    assert b["netRevenue"] == expected_net
    assert b["orderCount"] == 3

    # Destinations
    res_dest = client.get("/api/v1/admin/finance/destinations", params=params, cookies=cookies)
    assert res_dest.status_code == 200
    assert res_dest.json()["totalGrossSalesPaise"] == expected_gross * 100
    assert res_dest.json()["totalOrders"] == 3

    # Trends
    res_trends = client.get("/api/v1/admin/finance/trends", params=params, cookies=cookies)
    assert res_trends.status_code == 200
    tr_data = res_trends.json()
    assert tr_data["grossSales"]["currentPaise"] == expected_gross * 100
    assert tr_data["netRevenue"]["currentPaise"] == expected_net * 100
    assert tr_data["orders"]["current"] == 3
    assert tr_data["refunds"]["currentPaise"] == expected_refunds * 100
    # Unpaid prepaid order accounted for in operational indicators
    assert tr_data["operationalIndicators"]["pendingPaymentCount"] == 1
    assert tr_data["operationalIndicators"]["pendingPaymentTotal"] == 4500
    assert tr_data["operationalIndicators"]["refundedCount"] == 1


def test_finance_acceptance_failed_prepaid_excluded():
    """TC-FIN-27-04: FAILED prepaid orders are excluded from recognized sales."""
    cookies = _login_admin()
    stamp = datetime(2050, 4, 1, 10, tzinfo=timezone.utc)
    with SessionLocal() as db:
        _create_test_order(db, "QA-FIN-FAILED", subtotal=3500, shipping_fee=0,
                           total_amount=3500, payment_status="FAILED", created_at=stamp)
        _create_test_order(db, "QA-FIN-PAID-OK", subtotal=1200, shipping_fee=0,
                           total_amount=1200, payment_status="PAID", created_at=stamp)
        db.commit()

    res = client.get("/api/v1/admin/finance/summary",
                     params={"from": "2050-04-01", "to": "2050-04-01"}, cookies=cookies)
    assert res.status_code == 200
    data = res.json()
    assert data["grossSalesPaise"] == 120000
    assert data["orderCount"] == 1



def test_finance_acceptance_ist_boundaries_and_equal_previous_period():
    """TC-FIN-27-05: midnight IST is 18:30 UTC; comparisons use equal days."""
    cookies = _login_admin()
    with SessionLocal() as db:
        for number, stamp, amount in [
            ('BEFORE', datetime(2050, 5, 9, 18, 29, 59, tzinfo=timezone.utc), 700),
            ('START', datetime(2050, 5, 9, 18, 30, tzinfo=timezone.utc), 1000),
            ('END', datetime(2050, 5, 10, 18, 29, 59, tzinfo=timezone.utc), 500),
            ('AFTER', datetime(2050, 5, 10, 18, 30, tzinfo=timezone.utc), 9000),
        ]:
            _create_test_order(db, f'QA-FIN-IST-{number}', subtotal=amount,
                               shipping_fee=0, total_amount=amount, created_at=stamp)
    response = client.get('/api/v1/admin/finance/trends',
                          params={'from': '2050-05-10', 'to': '2050-05-10'}, cookies=cookies)
    assert response.status_code == 200
    data = response.json()
    assert data['effectiveRange'] == {'from': '2050-05-10', 'to': '2050-05-10'}
    assert data['previousRange'] == {'from': '2050-05-09', 'to': '2050-05-09'}
    assert data['grossSales']['currentPaise'] == 150000
    assert data['grossSales']['previousPaise'] == 70000
    assert data['orders']['current'] == 2


def test_finance_acceptance_query_count_does_not_scale_per_order():
    """TC-FIN-27-06: breakdown reads batch order items instead of N+1 queries."""
    from sqlalchemy import event
    from app.db.session import engine
    import time
    cookies = _login_admin()
    with SessionLocal() as db:
        for i in range(20):
            _create_test_order(db, f'QA-FIN-BATCH-{i}', subtotal=100,
                               shipping_fee=0, total_amount=100,
                               created_at=datetime(2050, 6, 10, 6, tzinfo=timezone.utc))
    statements = []
    def record_statement(conn, cursor, statement, parameters, context, executemany):
        statements.append(statement)
    event.listen(engine, 'before_cursor_execute', record_statement)
    try:
        for endpoint in ('categories', 'destinations', 'top-products'):
            statements.clear()
            started = time.perf_counter()
            response = client.get(f'/api/v1/admin/finance/{endpoint}',
                                  params={'from': '2050-06-10', 'to': '2050-06-10'}, cookies=cookies)
            elapsed = time.perf_counter() - started
            assert response.status_code == 200
            assert len(statements) < 10, f'{endpoint}: {len(statements)} queries for20 orders'
            assert all(not s.lstrip().upper().startswith(('INSERT ', 'UPDATE ', 'DELETE ')) for s in statements)
            print(f'FINANCE_QUERY {endpoint}: {len(statements)} statements; {elapsed:.3f}s;20 orders')
    finally:
        event.remove(engine, 'before_cursor_execute', record_statement)
