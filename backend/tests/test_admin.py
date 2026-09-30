"""Integration tests for Admin Catalog Management, Inventory, Order Status Transitions, and Store Analytics."""

from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.models.catalogue import Category, Product, ProductVariant
from app.models.order import Order
from app.models.user import User, UserIdentity

client = TestClient(app)


def _login_customer(phone: str = "9999911001") -> dict[str, str]:
    """Helper to authenticate a regular customer."""
    send_res = client.post("/api/v1/auth/phone/send-otp", json={"phone": phone})
    assert send_res.status_code == 200
    otp = send_res.json().get("devOtp") or "123456"
    res = client.post("/api/v1/auth/phone/verify-otp", json={"phone": phone, "otp": otp})
    assert res.status_code == 200
    return dict(res.cookies)


def _login_admin(phone: str = "9999900000") -> dict[str, str]:
    """Helper to authenticate an admin user."""
    with SessionLocal() as db:
        admin = db.query(User).filter(User.phone == phone).first()
        if not admin:
            admin = User(
                name="Store Admin",
                phone=phone,
                email="admin@sulocraft.com",
                role="ADMIN",
                status="ACTIVE",
            )
            db.add(admin)
            db.flush()
            db.add(UserIdentity(user_id=admin.id, provider="phone", provider_subject=phone))
            db.commit()

    send_res = client.post("/api/v1/auth/phone/send-otp", json={"phone": phone})
    assert send_res.status_code == 200
    otp = send_res.json().get("devOtp") or "123456"
    res = client.post("/api/v1/auth/phone/verify-otp", json={"phone": phone, "otp": otp})
    assert res.status_code == 200
    assert res.json()["user"]["role"] == "ADMIN"
    return dict(res.cookies)


def test_admin_rbac_protection():
    """Verify unauthenticated requests return 401 and non-admin customer returns 403."""
    # 1. Unauthenticated request
    res = client.get("/api/v1/admin/products")
    assert res.status_code == 401

    # 2. Customer authenticated request
    customer_cookies = _login_customer("9999911002")
    res_forbidden = client.get("/api/v1/admin/products", cookies=customer_cookies)
    assert res_forbidden.status_code == 403
    assert "Admin privileges required" in res_forbidden.json()["detail"]

    # 3. Admin authenticated request succeeds
    admin_cookies = _login_admin("9999900000")
    res_ok = client.get("/api/v1/admin/products", cookies=admin_cookies)
    assert res_ok.status_code == 200
    assert "items" in res_ok.json()


def test_admin_product_crud():
    """Verify admin can create, read, update, and soft-delete a product."""
    admin_cookies = _login_admin("9999900000")

    with SessionLocal() as db:
        for p in db.query(Product).filter(Product.name.ilike("Handmade Pastel Tulip Pot%")).all():
            db.delete(p)
        db.commit()

    # 1. Create product
    payload = {
        "name": "Handmade Pastel Tulip Pot",
        "description": "Artisan crochet tulip pot for home office desk.",
        "primaryImage": "https://example.com/tulip-pot.jpg",
        "badge": "Limited Edition",
        "customizable": True,
        "galleryImages": ["https://example.com/tulip-pot.jpg", "https://example.com/tulip-pot-2.jpg"],
        "variants": [
            {
                "sku": "TULIP-POT-PINK-01",
                "name": "Pastel Pink",
                "price": 1299,
                "compareAtPrice": 1599,
                "stockQuantity": 15,
            },
            {
                "sku": "TULIP-POT-YELLOW-01",
                "name": "Sunshine Yellow",
                "price": 1299,
                "stockQuantity": 8,
            },
        ],
    }

    create_res = client.post("/api/v1/admin/products", json=payload, cookies=admin_cookies)
    assert create_res.status_code == 201
    created = create_res.json()
    product_id = created["id"]
    assert created["name"] == "Handmade Pastel Tulip Pot"
    assert created["slug"] == "handmade-pastel-tulip-pot"
    assert created["totalStock"] == 23
    assert created["minPrice"] == 1299
    assert created["minPricePaise"] == 129900
    assert len(created["variants"]) == 2

    # 2. Get product
    get_res = client.get(f"/api/v1/admin/products/{product_id}", cookies=admin_cookies)
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "Handmade Pastel Tulip Pot"

    # 3. Update product
    patch_res = client.patch(
        f"/api/v1/admin/products/{product_id}",
        json={"name": "Handmade Pastel Tulip Pot - Deluxe", "badge": "Bestseller"},
        cookies=admin_cookies,
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["name"] == "Handmade Pastel Tulip Pot - Deluxe"
    assert patch_res.json()["badge"] == "Bestseller"

    # 4. Soft delete product
    del_res = client.delete(f"/api/v1/admin/products/{product_id}", cookies=admin_cookies)
    assert del_res.status_code == 200
    assert del_res.json()["status"] == "ok"

    # Verify status changed to ARCHIVED
    get_archived = client.get(f"/api/v1/admin/products/{product_id}", cookies=admin_cookies)
    assert get_archived.json()["status"] == "ARCHIVED"


def test_admin_variant_and_inventory_management():
    """Verify adding variants and adjusting inventory levels."""
    admin_cookies = _login_admin("9999900000")

    with SessionLocal() as db:
        for p in db.query(Product).filter(Product.name.ilike("Sunflower Keychain Charm%")).all():
            db.delete(p)
        db.commit()

    # 1. Create a base product
    prod_res = client.post(
        "/api/v1/admin/products",
        json={
            "name": "Sunflower Keychain Charm",
            "primaryImage": "https://example.com/sunflower.jpg",
            "variants": [{"sku": "SF-KEY-01", "name": "Standard", "price": 499, "stockQuantity": 10}],
        },
        cookies=admin_cookies,
    )
    assert prod_res.status_code == 201
    product_id = prod_res.json()["id"]

    # 2. Add second variant
    var_res = client.post(
        f"/api/v1/admin/products/{product_id}/variants",
        json={"sku": "SF-KEY-GLOW", "name": "Glow-in-the-dark", "price": 699, "stockQuantity": 5},
        cookies=admin_cookies,
    )
    assert var_res.status_code == 201
    var_id = var_res.json()["id"]
    assert var_res.json()["price"] == 699
    assert var_res.json()["pricePaise"] == 69900

    # 3. Adjust inventory relative delta (+15)
    adj_res = client.patch(
        f"/api/v1/admin/variants/{var_id}/inventory",
        json={"adjustment": 15},
        cookies=admin_cookies,
    )
    assert adj_res.status_code == 200
    assert adj_res.json()["stockQuantity"] == 20

    # 4. Adjust inventory absolute (set to 7)
    set_res = client.patch(
        f"/api/v1/admin/variants/{var_id}/inventory",
        json={"stockQuantity": 7},
        cookies=admin_cookies,
    )
    assert set_res.status_code == 200
    assert set_res.json()["stockQuantity"] == 7


def test_admin_category_management():
    """Verify category creation, update, and deletion."""
    admin_cookies = _login_admin("9999900000")

    # Clean up test category if it exists from previous run
    with SessionLocal() as db:
        existing = db.query(Category).filter(Category.slug == "test-wedding-collection").first()
        if existing:
            db.delete(existing)
            db.commit()

    cat_res = client.post(
        "/api/v1/admin/categories",
        json={
            "name": "Test Wedding Collection",
            "slug": "test-wedding-collection",
            "description": "Elegant handmade crochet items for bridal showers and weddings",
            "displayOrder": 10,
        },
        cookies=admin_cookies,
    )
    assert cat_res.status_code == 201
    cat_id = cat_res.json()["id"]
    assert cat_res.json()["slug"] == "test-wedding-collection"

    patch_res = client.patch(
        f"/api/v1/admin/categories/{cat_id}",
        json={"name": "Luxury Test Wedding Collection"},
        cookies=admin_cookies,
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["name"] == "Luxury Test Wedding Collection"

    # Test category deletion
    del_res = client.delete(f"/api/v1/admin/categories/{cat_id}", cookies=admin_cookies)
    assert del_res.status_code == 200
    assert del_res.json()["status"] == "ok"


def test_admin_order_status_transitions():
    """Verify admin listing orders and transitioning order status to SHIPPED with tracking."""
    customer_cookies = _login_customer("9999911003")
    admin_cookies = _login_admin("9999900000")

    # 1. Add item to cart
    add_cart = client.post(
        "/api/v1/cart/items",
        json={"product_variant_id": 1, "quantity": 1},
        cookies=customer_cookies,
    )
    assert add_cart.status_code == 201

    # 2. Customer places order
    order_res = client.post(
        "/api/v1/orders",
        json={
            "customerName": "Rohan Verma",
            "customerPhone": "9999911003",
            "paymentMethod": "COD",
            "shippingAddress": {
                "name": "Rohan Verma",
                "phone": "9999911003",
                "line1": "Flat 402, Sunshine Heights",
                "city": "Bengaluru",
                "state": "Karnataka",
                "postalCode": "560001",
                "country": "IN",
            },
        },
        cookies=customer_cookies,
    )
    assert order_res.status_code == 201
    order_number = order_res.json()["orderNumber"]

    # 3. Admin lists orders
    admin_orders_res = client.get("/api/v1/admin/orders", cookies=admin_cookies)
    assert admin_orders_res.status_code == 200
    orders_list = admin_orders_res.json()["items"]
    assert any(o["orderNumber"] == order_number for o in orders_list)

    # 4. Admin transitions to PROCESSING
    proc_res = client.patch(
        f"/api/v1/admin/orders/{order_number}/status",
        json={"status": "PROCESSING", "note": "Order assigned to Bangalore artisan workshop."},
        cookies=admin_cookies,
    )
    assert proc_res.status_code == 200
    assert proc_res.json()["status"] == "PROCESSING"

    # 5. Admin transitions to SHIPPED with tracking number
    ship_res = client.patch(
        f"/api/v1/admin/orders/{order_number}/status",
        json={
            "status": "SHIPPED",
            "trackingNumber": "BLUEDART-8829104",
            "courierName": "BlueDart Express",
            "note": "Package dispatched from fulfillment hub",
        },
        cookies=admin_cookies,
    )
    assert ship_res.status_code == 200
    shipped = ship_res.json()
    assert shipped["status"] == "SHIPPED"
    assert shipped["trackingNumber"] == "BLUEDART-8829104"
    assert shipped["courierName"] == "BlueDart Express"
    assert len(shipped["statusHistory"]) >= 3


def test_admin_order_cancellation_restores_inventory():
    """Verify admin order cancellation restores variant inventory stock."""
    customer_cookies = _login_customer("9999911004")
    admin_cookies = _login_admin("9999900000")

    with SessionLocal() as db:
        v = db.query(ProductVariant).filter(ProductVariant.id == 1).first()
        initial_stock = v.stock_quantity

    # Add 2 items to cart
    add_cart = client.post(
        "/api/v1/cart/items",
        json={"product_variant_id": 1, "quantity": 2},
        cookies=customer_cookies,
    )
    assert add_cart.status_code == 201

    # Place order for 2 items
    order_res = client.post(
        "/api/v1/orders",
        json={
            "customerName": "Test Stock Restore",
            "customerPhone": "9999911004",
            "paymentMethod": "COD",
            "shippingAddress": {
                "name": "Test Customer",
                "phone": "9999911004",
                "line1": "Test Street",
                "city": "Mumbai",
                "state": "Maharashtra",
                "postalCode": "400001",
                "country": "IN",
            },
        },
        cookies=customer_cookies,
    )
    assert order_res.status_code == 201
    order_number = order_res.json()["orderNumber"]

    with SessionLocal() as db:
        v = db.query(ProductVariant).filter(ProductVariant.id == 1).first()
        assert v.stock_quantity == initial_stock - 2

    # Admin cancels order
    cancel_res = client.patch(
        f"/api/v1/admin/orders/{order_number}/status",
        json={"status": "CANCELLED", "note": "Customer called support to cancel order"},
        cookies=admin_cookies,
    )
    assert cancel_res.status_code == 200
    assert cancel_res.json()["status"] == "CANCELLED"

    with SessionLocal() as db:
        v = db.query(ProductVariant).filter(ProductVariant.id == 1).first()
        assert v.stock_quantity == initial_stock


def test_admin_store_analytics():
    """Verify admin analytics endpoint returns computed KPIs, recent orders, and top products."""
    admin_cookies = _login_admin("9999900000")

    analytics_res = client.get("/api/v1/admin/analytics", cookies=admin_cookies)
    assert analytics_res.status_code == 200
    data = analytics_res.json()

    assert "totalRevenue" in data
    assert "totalRevenuePaise" in data
    assert "totalOrders" in data
    assert "pendingOrders" in data
    assert "deliveredOrders" in data
    assert "cancelledOrders" in data
    assert "totalCustomers" in data
    assert "totalProducts" in data
    assert "lowStockCount" in data
    assert "lowStockItems" in data
    assert "recentOrders" in data
    assert "topSellingProducts" in data
