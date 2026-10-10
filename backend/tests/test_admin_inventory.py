"""Integration and concurrency tests for Admin Inventory Adjustments (Task 1.8.4).

Covers:
1. RBAC protection: 401 unauthenticated, 403 customer, 200 admin.
2. Input validation:
   - 404 for non-existent variant ID.
   - 400 when neither stockQuantity nor adjustment is provided.
   - 400 when adjustment would result in negative stock.
3. Compatibility: Absolute stock setting and relative deltas.
4. Concurrency - Relative additions: Concurrent positive adjustments all persist without lost updates.
5. Concurrency - Mixed adjustments: Concurrent additions and subtractions preserve exact net total.
6. Concurrency - Competing withdrawals: Concurrent subtractions cannot drive stock below 0;
   rejected requests fail with 400 and leave stock unchanged.
"""

import concurrent.futures
import uuid
from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.models.catalogue import Product, ProductVariant
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


def _create_test_product_with_variant(initial_stock: int = 10) -> tuple[int, int]:
    """Create a temporary test product and variant for testing without mutating real data."""
    admin_cookies = _login_admin()
    uid = uuid.uuid4().hex[:8]
    prod_res = client.post(
        "/api/v1/admin/products",
        json={
            "name": f"Test Inv Prod {uid}",
            "primaryImage": "https://example.com/test.jpg",
            "variants": [
                {
                    "sku": f"TEST-SKU-{uid}",
                    "name": "Standard",
                    "price": 500,
                    "stockQuantity": initial_stock,
                }
            ],
        },
        cookies=admin_cookies,
    )
    assert prod_res.status_code == 201
    prod_data = prod_res.json()
    product_id = prod_data["id"]
    variant_id = prod_data["variants"][0]["id"]
    return product_id, variant_id


def _delete_test_product(product_id: int):
    """Clean up test product and associated variants."""
    with SessionLocal() as db:
        p = db.query(Product).filter(Product.id == product_id).first()
        if p:
            db.delete(p)
            db.commit()


def test_admin_inventory_rbac():
    """Verify unauthenticated requests return 401 and customer returns 403."""
    product_id, var_id = _create_test_product_with_variant(10)
    try:
        # 1. Unauthenticated request -> 401
        client.cookies.clear()
        res = client.patch(
            f"/api/v1/admin/variants/{var_id}/inventory",
            json={"adjustment": 5},
        )
        assert res.status_code == 401

        # 2. Customer request -> 403
        cust_cookies = _login_customer("9999933001")
        res_cust = client.patch(
            f"/api/v1/admin/variants/{var_id}/inventory",
            json={"adjustment": 5},
            cookies=cust_cookies,
        )
        assert res_cust.status_code == 403

        # 3. Admin request -> 200
        admin_cookies = _login_admin()
        res_admin = client.patch(
            f"/api/v1/admin/variants/{var_id}/inventory",
            json={"adjustment": 5},
            cookies=admin_cookies,
        )
        assert res_admin.status_code == 200
        assert res_admin.json()["stockQuantity"] == 15
    finally:
        _delete_test_product(product_id)


def test_admin_inventory_validation():
    """Verify 404 for missing variant, 400 for empty payload, and 400 for negative stock."""
    admin_cookies = _login_admin()
    product_id, var_id = _create_test_product_with_variant(5)
    try:
        # 1. Nonexistent variant -> 404
        res_404 = client.patch(
            "/api/v1/admin/variants/99999999/inventory",
            json={"adjustment": 5},
            cookies=admin_cookies,
        )
        assert res_404.status_code == 404
        assert res_404.json()["detail"] == "Variant not found"

        # 2. Empty payload (neither stockQuantity nor adjustment) -> 400
        res_empty = client.patch(
            f"/api/v1/admin/variants/{var_id}/inventory",
            json={},
            cookies=admin_cookies,
        )
        assert res_empty.status_code == 400
        assert "Must provide stock_quantity or adjustment" in res_empty.json()["detail"]

        # 3. Withdrawal exceeding available stock (5 - 10 < 0) -> 400
        res_neg = client.patch(
            f"/api/v1/admin/variants/{var_id}/inventory",
            json={"adjustment": -10},
            cookies=admin_cookies,
        )
        assert res_neg.status_code == 400
        assert "cannot be negative" in res_neg.json()["detail"]

        # Stock must remain unchanged at 5
        with SessionLocal() as db:
            var = db.query(ProductVariant).filter(ProductVariant.id == var_id).first()
            assert var.stock_quantity == 5
    finally:
        _delete_test_product(product_id)


def test_admin_inventory_absolute_and_relative_compatibility():
    """Verify absolute stock quantity setting and relative deltas work interchangeably."""
    admin_cookies = _login_admin()
    product_id, var_id = _create_test_product_with_variant(10)
    try:
        # 1. Absolute set to 25
        res1 = client.patch(
            f"/api/v1/admin/variants/{var_id}/inventory",
            json={"stockQuantity": 25},
            cookies=admin_cookies,
        )
        assert res1.status_code == 200
        assert res1.json()["stockQuantity"] == 25

        # 2. Relative delta +10
        res2 = client.patch(
            f"/api/v1/admin/variants/{var_id}/inventory",
            json={"adjustment": 10},
            cookies=admin_cookies,
        )
        assert res2.status_code == 200
        assert res2.json()["stockQuantity"] == 35

        # 3. Relative delta down to 0
        res3 = client.patch(
            f"/api/v1/admin/variants/{var_id}/inventory",
            json={"adjustment": -35},
            cookies=admin_cookies,
        )
        assert res3.status_code == 200
        assert res3.json()["stockQuantity"] == 0
    finally:
        _delete_test_product(product_id)


def test_concurrent_inventory_relative_additions():
    """Verify concurrent relative additions all persist without lost updates."""
    admin_cookies = _login_admin()
    initial_stock = 10
    product_id, var_id = _create_test_product_with_variant(initial_stock)
    try:
        # 10 concurrent requests: 5 of +2 and 5 of +3 -> total +25
        adjustments = [2, 3, 2, 3, 2, 3, 2, 3, 2, 3]
        expected_final = initial_stock + sum(adjustments)  # 10 + 25 = 35

        def _adjust(delta: int):
            return client.patch(
                f"/api/v1/admin/variants/{var_id}/inventory",
                json={"adjustment": delta},
                cookies=admin_cookies,
            )

        with concurrent.futures.ThreadPoolExecutor(max_workers=len(adjustments)) as executor:
            responses = list(executor.map(_adjust, adjustments))

        for r in responses:
            assert r.status_code == 200, f"Failed adjustment: {r.status_code} {r.text}"

        # Verify persisted stock in database matches exact sum
        with SessionLocal() as db:
            var = db.query(ProductVariant).filter(ProductVariant.id == var_id).first()
            assert var.stock_quantity == expected_final
    finally:
        _delete_test_product(product_id)


def test_concurrent_inventory_mixed_adjustments():
    """Verify concurrent mixed increases and decreases preserve exact arithmetic sum."""
    admin_cookies = _login_admin()
    initial_stock = 20
    product_id, var_id = _create_test_product_with_variant(initial_stock)
    try:
        # 4 additions of +5 (+20) and 4 deductions of -3 (-12) -> net +8
        adjustments = [5, -3, 5, -3, 5, -3, 5, -3]
        expected_final = initial_stock + sum(adjustments)  # 20 + 8 = 28

        def _adjust(delta: int):
            return client.patch(
                f"/api/v1/admin/variants/{var_id}/inventory",
                json={"adjustment": delta},
                cookies=admin_cookies,
            )

        with concurrent.futures.ThreadPoolExecutor(max_workers=len(adjustments)) as executor:
            responses = list(executor.map(_adjust, adjustments))

        for r in responses:
            assert r.status_code == 200, f"Failed mixed adjustment: {r.status_code} {r.text}"

        with SessionLocal() as db:
            var = db.query(ProductVariant).filter(ProductVariant.id == var_id).first()
            assert var.stock_quantity == expected_final
    finally:
        _delete_test_product(product_id)


def test_concurrent_competing_withdrawals_cannot_produce_negative_stock():
    """Verify competing concurrent withdrawals never produce negative stock and reject overages."""
    admin_cookies = _login_admin()
    initial_stock = 10
    product_id, var_id = _create_test_product_with_variant(initial_stock)
    try:
        # 5 concurrent threads each trying to withdraw -4
        # Total requested: -20, but stock is only 10.
        # Exactly 2 requests must succeed (10 - 4 - 4 = 2).
        # The remaining 3 requests must be rejected with 400 Bad Request.
        withdrawals = [-4] * 5

        def _withdraw(delta: int):
            return client.patch(
                f"/api/v1/admin/variants/{var_id}/inventory",
                json={"adjustment": delta},
                cookies=admin_cookies,
            )

        with concurrent.futures.ThreadPoolExecutor(max_workers=len(withdrawals)) as executor:
            responses = list(executor.map(_withdraw, withdrawals))

        successes = [r for r in responses if r.status_code == 200]
        rejections = [r for r in responses if r.status_code == 400]

        assert len(successes) == 2, f"Expected exactly 2 successes, got {len(successes)}"
        assert len(rejections) == 3, f"Expected exactly 3 rejections, got {len(rejections)}"

        for r in rejections:
            assert "cannot be negative" in r.json()["detail"]

        # Final stock must be strictly 2
        with SessionLocal() as db:
            var = db.query(ProductVariant).filter(ProductVariant.id == var_id).first()
            assert var.stock_quantity == 2
    finally:
        _delete_test_product(product_id)
