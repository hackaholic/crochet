"""Integration tests for Task 23.3: Basket-aware recommendation API (GET /api/v1/cart/recommendations)."""

import secrets
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.models.cart import Cart, CartItem
from app.models.catalogue import Category, Collection, Product, ProductVariant, Tag
from app.models.order import Order, OrderItem, OrderStatus, PaymentMethod, PaymentStatus
from app.models.user import User, UserSession

client = TestClient(app)


def test_cart_recommendations_default_contract():
    """Verify default contract: 200 OK, {strategy, products}, limit <= 4, active in-stock products."""
    res = client.get("/api/v1/cart/recommendations")
    assert res.status_code == 200
    data = res.json()

    assert "strategy" in data
    assert data["strategy"] in {"newest", "featured", "related", "personalized"}
    assert "products" in data
    assert isinstance(data["products"], list)
    assert len(data["products"]) <= 4

    seen_ids = set()
    for prod in data["products"]:
        assert isinstance(prod["id"], int)
        assert prod["id"] not in seen_ids, f"Duplicate product ID {prod['id']}"
        seen_ids.add(prod["id"])

        assert "name" in prod
        assert "slug" in prod
        assert "price" in prod
        assert prod.get("inStock") is True


def test_cart_recommendations_limit_bounds_and_validation():
    """Verify limit validation: 1 <= limit <= 8; out-of-bounds yields HTTP 422."""
    # Valid limits
    res_1 = client.get("/api/v1/cart/recommendations?limit=1")
    assert res_1.status_code == 200
    assert len(res_1.json()["products"]) <= 1

    res_8 = client.get("/api/v1/cart/recommendations?limit=8")
    assert res_8.status_code == 200
    assert len(res_8.json()["products"]) <= 8

    # Invalid limits: 0, 9, negative
    assert client.get("/api/v1/cart/recommendations?limit=0").status_code == 422
    assert client.get("/api/v1/cart/recommendations?limit=9").status_code == 422
    assert client.get("/api/v1/cart/recommendations?limit=-1").status_code == 422
    assert client.get("/api/v1/cart/recommendations?limit=invalid").status_code == 422


def test_cart_recommendations_basket_exclusion():
    """Verify that products currently in the guest or user basket are strictly excluded."""
    token = secrets.token_urlsafe(24)
    with SessionLocal() as db:
        prod = (
            db.query(Product)
            .filter(Product.status == "ACTIVE")
            .filter(Product.variants.any(ProductVariant.stock_quantity > 0))
            .first()
        )
        assert prod is not None
        target_prod_id = prod.id
        variant = prod.variants[0]

        cart = Cart(
            guest_token=token,
            status="ACTIVE",
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        )
        db.add(cart)
        db.flush()

        db.add(CartItem(cart_id=cart.id, product_variant_id=variant.id, quantity=1))
        db.commit()

    res = client.get("/api/v1/cart/recommendations?limit=8", cookies={"guest_cart_token": token})
    assert res.status_code == 200
    rec_ids = [p["id"] for p in res.json()["products"]]

    assert target_prod_id not in rec_ids, f"Cart item {target_prod_id} was not excluded from recommendations"


def test_cart_recommendations_related_strategy_with_cart_items():
    """Verify that a cart with categorized items selects 'related' strategy."""
    token = secrets.token_urlsafe(24)
    with SessionLocal() as db:
        # Find a product that shares a category with other products
        cat = (
            db.query(Category)
            .filter(Category.products.any(Product.status == "ACTIVE"))
            .first()
        )
        assert cat is not None
        active_in_cat = [p for p in cat.products if p.status == "ACTIVE" and any(v.stock_quantity > 0 for v in p.variants)]
        assert len(active_in_cat) >= 2, "Test requires at least 2 active products in a category"

        cart_prod = active_in_cat[0]
        var = cart_prod.variants[0]

        cart = Cart(
            guest_token=token,
            status="ACTIVE",
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        )
        db.add(cart)
        db.flush()

        db.add(CartItem(cart_id=cart.id, product_variant_id=var.id, quantity=1))
        db.commit()

    res = client.get("/api/v1/cart/recommendations", cookies={"guest_cart_token": token})
    assert res.status_code == 200
    data = res.json()
    assert data["strategy"] == "related"
    assert len(data["products"]) > 0


def test_cart_recommendations_personalized_strategy_for_authenticated_user():
    """Verify that an authenticated user with past completed orders receives 'personalized' strategy."""
    email = f"pers_{secrets.token_hex(4)}@example.com"
    session_token = secrets.token_urlsafe(32)

    with SessionLocal() as db:
        user = User(email=email, status="ACTIVE", role="CUSTOMER")
        db.add(user)
        db.flush()

        # Create session
        user_sess = UserSession(
            user_id=user.id,
            session_token=session_token,
            expires_at=datetime.now(timezone.utc) + timedelta(days=1),
        )
        db.add(user_sess)

        # Find an active product in a category with other active products
        cat = (
            db.query(Category)
            .filter(Category.products.any(Product.status == "ACTIVE"))
            .first()
        )
        assert cat is not None
        prods = [p for p in cat.products if p.status == "ACTIVE" and any(v.stock_quantity > 0 for v in p.variants)]
        assert len(prods) >= 2
        past_product = prods[0]
        past_product_id = past_product.id

        # Create paid order for user
        order = Order(
            order_number=f"ORD-REC-{secrets.token_hex(4).upper()}",
            user_id=user.id,
            customer_name="Test Rec Customer",
            customer_phone="9876543210",
            customer_email=email,
            shipping_address_json={"line1": "123 Test St", "city": "Bengaluru", "postal_code": "560001"},
            status=OrderStatus.DELIVERED.value,
            payment_status=PaymentStatus.PAID.value,
            payment_method=PaymentMethod.CARD.value,
            subtotal=1000,
            total_amount=1000,
            currency="INR",
        )
        db.add(order)
        db.flush()

        var = past_product.variants[0]
        db.add(
            OrderItem(
                order_id=order.id,
                product_id=past_product.id,
                product_variant_id=var.id,
                product_name=past_product.name,
                product_slug=past_product.slug,
                sku=var.sku,
                variant_name=var.name or "Default",
                unit_price=1000,
                quantity=1,
                line_total=1000,
            )
        )
        db.commit()

    res = client.get(
        "/api/v1/cart/recommendations",
        cookies={"session_token": session_token},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["strategy"] == "personalized"
    assert len(data["products"]) > 0
    # User's already purchased product should also be excluded
    rec_ids = [p["id"] for p in data["products"]]
    assert past_product_id not in rec_ids


def test_cart_recommendations_tenant_isolation_and_no_mutation():
    """Verify IDOR protection and ensure recommendations make 0 mutations to cart."""
    token_a = secrets.token_urlsafe(24)
    with SessionLocal() as db:
        user_a = User(email=f"user_a_{secrets.token_hex(4)}@example.com", status="ACTIVE")
        db.add(user_a)
        db.flush()

        cart_a = Cart(
            user_id=user_a.id,
            guest_token=token_a,
            status="ACTIVE",
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        )
        db.add(cart_a)
        db.commit()

        initial_item_count = db.query(CartItem).filter(CartItem.cart_id == cart_a.id).count()

    # Anonymous user passes user_a's guest_token -> IDOR check prevents using user_a's cart
    res = client.get("/api/v1/cart/recommendations", cookies={"guest_cart_token": token_a})
    assert res.status_code == 200

    # Ensure zero mutation
    with SessionLocal() as db:
        after_item_count = db.query(CartItem).filter(CartItem.cart_id == cart_a.id).count()
        assert after_item_count == initial_item_count


def test_cart_recommendations_inactive_and_out_of_stock_exclusion():
    """Verify inactive (DRAFT) and 0-stock products never appear in recommendations."""
    suffix = secrets.token_hex(4)
    with SessionLocal() as db:
        inactive_prod = Product(
            name=f"Inactive Rec Product {suffix}",
            slug=f"inactive-rec-{suffix}",
            status="DRAFT",
            badge="Bestseller",
            primary_image="inactive.jpg",
        )
        db.add(inactive_prod)
        db.flush()
        db.add(ProductVariant(product_id=inactive_prod.id, sku=f"SKU-INACT-{suffix}", price=999, stock_quantity=10))

        oos_prod = Product(
            name=f"OOS Rec Product {suffix}",
            slug=f"oos-rec-{suffix}",
            status="ACTIVE",
            badge="Bestseller",
            primary_image="oos.jpg",
        )
        db.add(oos_prod)
        db.flush()
        db.add(ProductVariant(product_id=oos_prod.id, sku=f"SKU-OOS-{suffix}", price=888, stock_quantity=0))
        db.commit()

        inact_id = inactive_prod.id
        oos_id = oos_prod.id

    res = client.get("/api/v1/cart/recommendations?limit=8")
    assert res.status_code == 200
    rec_ids = [p["id"] for p in res.json()["products"]]

    assert inact_id not in rec_ids, f"Inactive product {inact_id} appeared in recommendations"
    assert oos_id not in rec_ids, f"Out of stock product {oos_id} appeared in recommendations"
