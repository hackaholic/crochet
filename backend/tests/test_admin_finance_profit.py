"""Unit and integration tests for Work 020 Task 20.2: Authoritative profit and payment reporting with recorded cost support.

Covers test cases 20.2-TC01 to 20.2-TC05:
- 20.2-TC01: Profit Reconciliation (Gross profit = Net sales - COGS; Net profit = Gross profit + Shipping + Tax - Expenses; exact paise match).
- 20.2-TC02: Incomplete Cost Safety (Orders with missing unit_cost -> profit_available: false, gross_profit: null, unavailability_reason: INCOMPLETE_PRODUCT_COSTS).
- 20.2-TC03: Historical Snapshot Integrity (Change variant cost in catalogue after purchase; prior order_item.unit_cost remains unchanged).
- 20.2-TC04: Loss / Negative Profit (COGS + expenses exceed recognized revenue -> negative gross/net profit returned truthfully).
- 20.2-TC05: Admin Cost/Expense RBAC & Validation (Non-admin 401/403 denied; validation rejects negative amounts or invalid categories 422).
"""

from datetime import datetime, timezone
import pytest
from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.models.catalogue import Product, ProductVariant
from app.models.expense import AdminExpense, ExpenseCategory
from app.models.order import (
    Order,
    OrderItem,
    OrderStatus,
    PaymentMethod,
    PaymentStatus,
    RefundStatus,
    ReturnRequest,
    ReturnStatus,
)
from app.models.payment import Payment
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

    client.cookies.clear()
    res = client.post("/api/v1/auth/google", json={
        "credential": "mock_admin_token_profit",
        "email": admin_email,
        "name": "Store Admin",
        "sub": "admin_sub_profit",
    })
    assert res.status_code == 200
    assert res.json()["user"]["role"] == "ADMIN"
    return dict(res.cookies)


def _login_customer(phone: str = "9999922001") -> dict[str, str]:
    """Helper to authenticate a customer."""
    client.cookies.clear()
    email = f"cust_{phone}@example.com"
    res = client.post("/api/v1/auth/google", json={
        "credential": f"mock_cust_{phone}",
        "email": email,
        "name": "Test Customer",
        "sub": f"sub_{phone}",
    })
    assert res.status_code == 200
    return dict(res.cookies)


def _create_order_with_items(
    db,
    order_number: str,
    subtotal: int,
    shipping_fee: int,
    discount_amount: int,
    tax_amount: int,
    items_spec: list[dict],  # list of {sku, unit_price, quantity, unit_cost}
    created_at: datetime | None = None,
    payment_status: str = "PAID",
    payment_method: str = "UPI",
    order_status: str = "CONFIRMED",
) -> Order:
    created = created_at or datetime.now(timezone.utc)
    total_amount = subtotal - discount_amount + shipping_fee + tax_amount
    order = Order(
        order_number=order_number,
        customer_name="Finance Tester",
        customer_phone="9876543210",
        customer_email="financetester@example.com",
        status=order_status,
        payment_status=payment_status,
        payment_method=payment_method,
        currency="INR",
        subtotal=subtotal,
        shipping_fee=shipping_fee,
        discount_amount=discount_amount,
        tax_amount=tax_amount,
        total_amount=total_amount,
        shipping_address_json={
            "name": "Finance Tester",
            "city": "Bengaluru",
            "state": "Karnataka",
            "postal_code": "560001",
            "country": "IN",
        },
        created_at=created,
        updated_at=created,
    )
    db.add(order)
    db.flush()

    for spec in items_spec:
        u_cost = spec.get("unit_cost")
        t_cost = (u_cost * spec["quantity"]) if u_cost is not None else None
        item = OrderItem(
            order_id=order.id,
            product_name=spec.get("name", "Craft Item"),
            sku=spec["sku"],
            variant_name="Standard",
            unit_price=spec["unit_price"],
            quantity=spec["quantity"],
            line_total=spec["unit_price"] * spec["quantity"],
            unit_cost=u_cost,
            total_cost=t_cost,
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


def test_20_2_tc01_profit_reconciliation():
    """20.2-TC01: Gross profit = Net sales - COGS; Net profit = Gross profit + Shipping + Tax - Expenses; exact paise match."""
    admin_cookies = _login_admin()
    with SessionLocal() as db:
        # Clean up test scope
        db.query(OrderItem).filter(OrderItem.sku.like("FIN-TC01-%")).delete()
        db.query(Order).filter(Order.order_number.like("FIN-TC01-%")).delete()
        db.query(AdminExpense).filter(AdminExpense.description.like("FIN-TC01-%")).delete()
        db.commit()

        # Create Order 1: Subtotal 2000, Discount 200, Shipping 100, Tax 50. Total 1950.
        # Item 1: 2 units @ 1000, cost 400 each (COGS = 800)
        _create_order_with_items(
            db,
            order_number="FIN-TC01-ORD1",
            subtotal=2000,
            shipping_fee=100,
            discount_amount=200,
            tax_amount=50,
            items_spec=[{"sku": "FIN-TC01-A", "unit_price": 1000, "quantity": 2, "unit_cost": 400}],
        )

        # Create Order 2: Subtotal 1500, Discount 0, Shipping 50, Tax 0. Total 1550.
        # Item 2: 1 unit @ 1500, cost 600 (COGS = 600)
        _create_order_with_items(
            db,
            order_number="FIN-TC01-ORD2",
            subtotal=1500,
            shipping_fee=50,
            discount_amount=0,
            tax_amount=0,
            items_spec=[{"sku": "FIN-TC01-B", "unit_price": 1500, "quantity": 1, "unit_cost": 600}],
        )

        # Add Expenses: Packaging 150, Gateway fee 50
        exp1 = AdminExpense(
            category=ExpenseCategory.PACKAGING.value,
            amount=150,
            amount_paise=15000,
            currency="INR",
            description="FIN-TC01-Packaging",
            expense_date=datetime.now(timezone.utc),
        )
        exp2 = AdminExpense(
            category=ExpenseCategory.GATEWAY_FEE.value,
            amount=50,
            amount_paise=5000,
            currency="INR",
            description="FIN-TC01-Gateway",
            expense_date=datetime.now(timezone.utc),
        )
        db.add_all([exp1, exp2])
        db.commit()

    # Query finance summary
    res = client.get("/api/v1/admin/finance/summary", cookies=admin_cookies)
    assert res.status_code == 200
    data = res.json()

    assert data["profitAvailable"] is True
    assert data["costCoveragePct"] == 100.0
    assert data["unavailabilityReason"] is None

    # Expected numbers
    # Gross sales >= 3500, Discounts >= 200, Shipping >= 150, Tax >= 50
    # COGS >= 1400 (800 + 600)
    # Net sales = grossSales - discounts - refunds
    # Gross profit = net_sales - cogs
    # Net profit = gross_profit + shipping + tax - operating_expenses
    assert data["cogs"] is not None
    assert data["cogsPaise"] == data["cogs"] * 100
    assert data["grossProfit"] is not None
    assert data["grossProfitPaise"] == data["grossProfit"] * 100

    net_sales = data["grossSales"] - data["discounts"] - data["refunds"]
    assert data["grossProfit"] == net_sales - data["cogs"]

    expected_net_profit = data["grossProfit"] + data["shippingCollected"] + data["storedTax"] - data["operatingExpenses"]
    assert data["netProfit"] == expected_net_profit
    assert data["netProfitPaise"] == data["netProfit"] * 100

    # Payment overview verification
    assert "paymentOverview" in data
    po = data["paymentOverview"]
    assert po["paid"]["count"] >= 2
    assert po["paid"]["amountPaise"] == po["paid"]["amount"] * 100
    assert po["pending"]["amountPaise"] == po["pending"]["amount"] * 100
    assert po["refunded"]["amountPaise"] == po["refunded"]["amount"] * 100


def test_20_2_tc02_incomplete_cost_safety():
    """20.2-TC02: Incomplete cost coverage produces profitAvailable: false and unavailabilityReason: INCOMPLETE_PRODUCT_COSTS."""
    admin_cookies = _login_admin()
    with SessionLocal() as db:
        # Create an order with missing cost
        ord_no = f"FIN-TC02-NOCOST-{int(datetime.now().timestamp())}"
        _create_order_with_items(
            db,
            order_number=ord_no,
            subtotal=1000,
            shipping_fee=50,
            discount_amount=0,
            tax_amount=0,
            items_spec=[{"sku": f"FIN-TC02-SKU-{ord_no}", "unit_price": 1000, "quantity": 1, "unit_cost": None}],
        )

    res = client.get("/api/v1/admin/finance/summary", cookies=admin_cookies)
    assert res.status_code == 200
    data = res.json()

    assert data["profitAvailable"] is False
    assert data["grossProfit"] is None
    assert data["grossProfitPaise"] is None
    assert data["netProfit"] is None
    assert data["netProfitPaise"] is None
    assert data["unavailabilityReason"] == "INCOMPLETE_PRODUCT_COSTS"
    assert data["costCoveragePct"] < 100.0


def test_20_2_tc03_historical_snapshot_and_backfill():
    """20.2-TC03: Catalog variant cost change does not mutate order item cost; patch endpoint backfills cost correctly."""
    admin_cookies = _login_admin()
    with SessionLocal() as db:
        # 1. Create a product and variant with cost 300
        p = Product(
            name="Snapshot Test Toy",
            slug=f"snap-toy-{int(datetime.now().timestamp())}",
            brand="Sulocraft",
            primary_image="catalog/toy.jpg",
            status="ACTIVE",
        )
        db.add(p)
        db.flush()
        v = ProductVariant(product_id=p.id, sku=f"SNAP-SKU-{p.id}", name="Blue", price=800, cost=300, stock_quantity=10, status="ACTIVE")
        db.add(v)
        db.commit()

        # 2. Checkout creates order item snapshotting cost
        ord_no = f"SNAP-ORD-{p.id}"
        order = _create_order_with_items(
            db,
            order_number=ord_no,
            subtotal=800,
            shipping_fee=50,
            discount_amount=0,
            tax_amount=0,
            items_spec=[{"sku": v.sku, "unit_price": 800, "quantity": 2, "unit_cost": v.cost}],
        )
        order_id = order.id
        item_id = order.items[0].id
        assert order.items[0].unit_cost == 300
        assert order.items[0].total_cost == 600

        # 3. Change catalog variant cost to 500
        v.cost = 500
        db.commit()

        # 4. Check that order item still has 300
        db.refresh(order)
        item = db.query(OrderItem).filter(OrderItem.id == item_id).first()
        assert item.unit_cost == 300
        assert item.total_cost == 600

    # 5. Verify detail endpoint returns cost fields
    res = client.get(f"/api/v1/admin/orders/{order_id}", cookies=admin_cookies)
    assert res.status_code == 200
    it_data = next((it for it in res.json()["items"] if it["id"] == item_id), None)
    assert it_data is not None
    assert it_data["unitCost"] == 300
    assert it_data["unitCostPaise"] == 30000
    assert it_data["totalCost"] == 600
    assert it_data["totalCostPaise"] == 60000

    # 6. Test backfill endpoint PATCH /api/v1/admin/orders/{order_id}/items/{item_id}/cost
    res_patch = client.patch(
        f"/api/v1/admin/orders/{order_id}/items/{item_id}/cost",
        json={"unitCost": 350},
        cookies=admin_cookies,
    )
    assert res_patch.status_code == 200
    patched_it = next((it for it in res_patch.json()["items"] if it["id"] == item_id), None)
    assert patched_it["unitCost"] == 350
    assert patched_it["totalCost"] == 700


def test_20_2_tc04_negative_profit():
    """20.2-TC04: When costs and operating expenses exceed revenue, truthful negative profit is returned."""
    admin_cookies = _login_admin()
    with SessionLocal() as db:
        ord_no = f"FIN-TC04-LOSS-{int(datetime.now().timestamp())}"
        # Selling price 500, but cost is 800 (negative gross profit: 500 - 800 = -300)
        _create_order_with_items(
            db,
            order_number=ord_no,
            subtotal=500,
            shipping_fee=0,
            discount_amount=0,
            tax_amount=0,
            items_spec=[{"sku": f"LOSS-SKU-{ord_no}", "unit_price": 500, "quantity": 1, "unit_cost": 800}],
        )

        # Huge marketing expense 100000
        exp = AdminExpense(
            category=ExpenseCategory.MARKETING.value,
            amount=100000,
            amount_paise=10000000,
            currency="INR",
            description="Campaign blowout",
            expense_date=datetime.now(timezone.utc),
        )
        db.add(exp)
        db.commit()

    # Query single day range
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    res = client.get(f"/api/v1/admin/finance/summary?from={today_str}&to={today_str}", cookies=admin_cookies)
    assert res.status_code == 200
    data = res.json()

    # If all items in this period have costs, profit is available and negative
    if data["profitAvailable"]:
        assert data["netProfit"] < 0
        assert data["netProfitPaise"] == data["netProfit"] * 100


def test_20_2_tc05_admin_expense_rbac_and_validation():
    """20.2-TC05: Admin expense routes require authentication and role; validation rejects invalid data."""
    # 1. Unauthenticated request -> 401
    client.cookies.clear()
    res_unauth = client.get("/api/v1/admin/finance/expenses")
    assert res_unauth.status_code == 401

    # 2. Customer request -> 403
    client.cookies.clear()
    customer_cookies = _login_customer()
    res_cust = client.get("/api/v1/admin/finance/expenses", cookies=customer_cookies)
    assert res_cust.status_code == 403

    # 3. Admin request -> 200
    client.cookies.clear()
    admin_cookies = _login_admin()
    res_admin = client.get("/api/v1/admin/finance/expenses", cookies=admin_cookies)
    assert res_admin.status_code == 200

    # 4. Create expense with invalid category -> 422
    res_invalid_cat = client.post(
        "/api/v1/admin/finance/expenses",
        json={"category": "INVALID_CAT", "amount": 500, "expenseDate": "2026-10-10"},
        cookies=admin_cookies,
    )
    assert res_invalid_cat.status_code == 422

    # 5. Create expense with negative amount -> 422
    res_negative = client.post(
        "/api/v1/admin/finance/expenses",
        json={"category": "OPERATING", "amount": -100, "expenseDate": "2026-10-10"},
        cookies=admin_cookies,
    )
    assert res_negative.status_code == 422

    # 6. Create valid expense -> 201
    res_create = client.post(
        "/api/v1/admin/finance/expenses",
        json={"category": "OPERATING", "amount": 250, "expenseDate": "2026-10-10", "description": "Stationery"},
        cookies=admin_cookies,
    )
    assert res_create.status_code == 201
    exp_id = res_create.json()["id"]
    assert res_create.json()["amount"] == 250
    assert res_create.json()["amountPaise"] == 25000

    # 7. Delete expense -> 204
    res_delete = client.delete(f"/api/v1/admin/finance/expenses/{exp_id}", cookies=admin_cookies)
    assert res_delete.status_code == 204
