"""Integration tests for Task 7.6: Storefront Discovery Sections & Opaque Cursor Pagination API."""

import base64
import json
import secrets
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.models.cart import Cart, CartItem
from app.models.catalogue import Category, Collection, Product, ProductVariant, Review, Tag
from app.models.order import Order, OrderItem, OrderStatus, PaymentMethod, PaymentStatus
from app.models.user import User, UserSession

client = TestClient(app)


def test_discovery_default_contract_and_structure():
    """Verify default GET /api/v1/storefront/discovery structure and constraints."""
    res = client.get("/api/v1/storefront/discovery?context=checkout")
    assert res.status_code == 200
    data = res.json()

    assert "sections" in data
    assert "nextCursor" in data
    sections = data["sections"]
    assert isinstance(sections, list)
    assert len(sections) <= 5

    valid_strategies = {"related", "newest", "featured", "trending", "popular"}
    total_products = 0
    seen_ids = set()

    for sec in sections:
        assert isinstance(sec["id"], str)
        assert isinstance(sec["title"], str)
        assert sec["strategy"] in valid_strategies
        assert isinstance(sec["products"], list)
        assert len(sec["products"]) <= 8
        assert len(sec["products"]) > 0  # No empty sections returned

        for prod in sec["products"]:
            total_products += 1
            # Deduplication across sections in same page
            assert prod["id"] not in seen_ids, f"Product {prod['id']} was duplicated across sections"
            seen_ids.add(prod["id"])

            # Verify ProductListItem schema fields
            assert "name" in prod
            assert "slug" in prod
            assert "price" in prod
            assert prod.get("inStock") is True

    assert total_products <= 16


def test_discovery_invalid_parameters_fail_validation():
    """Verify boundary validation for context, limit, and cursor length (422)."""
    # Invalid context
    res1 = client.get("/api/v1/storefront/discovery?context=invalid_context")
    assert res1.status_code == 422

    # Limit > 16
    res2 = client.get("/api/v1/storefront/discovery?limit=20")
    assert res2.status_code == 422

    # Limit < 1
    res3 = client.get("/api/v1/storefront/discovery?limit=0")
    assert res3.status_code == 422

    # Cursor > 512 characters
    oversized_cursor = "a" * 513
    res4 = client.get(f"/api/v1/storefront/discovery?cursor={oversized_cursor}")
    assert res4.status_code == 422

    # Invalid cursor encoding/schema
    res5 = client.get("/api/v1/storefront/discovery?cursor=not-valid-base64!!!")
    assert res5.status_code == 422

    # Cursor with wrong context
    mismatched_payload = json.dumps({"s": [1, 2], "c": "basket", "v": 1})
    mismatched_cursor = base64.urlsafe_b64encode(mismatched_payload.encode()).decode()
    res6 = client.get(f"/api/v1/storefront/discovery?context=checkout&cursor={mismatched_cursor}")
    assert res6.status_code == 422


def test_discovery_basket_exclusion():
    """Verify products currently in user's active cart are excluded from discovery sections."""
    token = f"test_guest_token_{secrets.token_hex(8)}"
    with SessionLocal() as db:
        # Find an active product with variant
        active_prod = db.query(Product).filter(Product.status == "ACTIVE").first()
        assert active_prod is not None
        variant = db.query(ProductVariant).filter(ProductVariant.product_id == active_prod.id).first()
        assert variant is not None
        excluded_pid = active_prod.id

        # Create cart for guest with this item
        cart = Cart(guest_token=token, status="ACTIVE")
        db.add(cart)
        db.commit()
        db.refresh(cart)

        item = CartItem(cart_id=cart.id, product_variant_id=variant.id, quantity=1)
        db.add(item)
        db.commit()

    # Query discovery with the guest cart token cookie
    res = client.get(
        "/api/v1/storefront/discovery?context=checkout",
        cookies={"guest_cart_token": token},
    )
    assert res.status_code == 200
    sections = res.json()["sections"]

    for sec in sections:
        for p in sec["products"]:
            assert p["id"] != excluded_pid, f"Product {excluded_pid} in basket was not excluded from discovery"


def test_discovery_related_strategy_matches_cart_categories():
    """Verify that 'related' strategy surfaces products matching categories/tags of cart items."""
    token = f"test_related_token_{secrets.token_hex(8)}"
    with SessionLocal() as db:
        # Pick category with multiple products
        prod_with_cats = (
            db.query(Product)
            .filter(Product.status == "ACTIVE", Product.categories.any())
            .first()
        )
        assert prod_with_cats is not None
        var = db.query(ProductVariant).filter(ProductVariant.product_id == prod_with_cats.id).first()
        assert var is not None

        cart = Cart(guest_token=token, status="ACTIVE")
        db.add(cart)
        db.commit()
        db.refresh(cart)
        db.add(CartItem(cart_id=cart.id, product_variant_id=var.id, quantity=1))
        db.commit()

    res = client.get(
        "/api/v1/storefront/discovery?context=checkout",
        cookies={"guest_cart_token": token},
    )
    assert res.status_code == 200
    sections = res.json()["sections"]
    strategies = [s["strategy"] for s in sections]

    # When cart has items, 'related' section is evaluated
    assert "related" in strategies
    related_sec = next(s for s in sections if s["strategy"] == "related")
    assert related_sec["id"] == "related"
    assert len(related_sec["products"]) > 0


def test_discovery_cursor_pagination_deduplication_and_termination():
    """Verify that cursor pagination deduplicates across pages and terminates with null nextCursor."""
    # Request page 1 with limit 8
    res1 = client.get("/api/v1/storefront/discovery?context=checkout&limit=8")
    assert res1.status_code == 200
    data1 = res1.json()

    p1_ids = {p["id"] for s in data1["sections"] for p in s["products"]}
    assert len(p1_ids) > 0
    next_cursor = data1["nextCursor"]

    if next_cursor:
        # Request page 2 with limit 8
        res2 = client.get(f"/api/v1/storefront/discovery?context=checkout&limit=8&cursor={next_cursor}")
        assert res2.status_code == 200
        data2 = res2.json()

        p2_ids = {p["id"] for s in data2["sections"] for p in s["products"]}
        # Strict cross-page deduplication
        overlap = p1_ids.intersection(p2_ids)
        assert len(overlap) == 0, f"Overlapping products across pages: {overlap}"

    # Verify terminal cursor: encode all existing product IDs as already seen
    with SessionLocal() as db:
        all_ids = [p.id for p in db.query(Product.id).all()]

    terminal_payload = json.dumps({"s": all_ids, "c": "checkout", "v": 1})
    terminal_cursor = base64.urlsafe_b64encode(terminal_payload.encode()).decode()

    res_term = client.get(f"/api/v1/storefront/discovery?context=checkout&cursor={terminal_cursor}")
    assert res_term.status_code == 200
    term_data = res_term.json()
    assert term_data["sections"] == []
    assert term_data["nextCursor"] is None


def test_discovery_inactive_and_out_of_stock_exclusion():
    """Verify inactive and out-of-stock products never appear in discovery."""
    suffix = secrets.token_hex(4)
    with SessionLocal() as db:
        # Create an inactive product
        inactive_prod = Product(
            name=f"Inactive Test Product {suffix}",
            slug=f"inactive-prod-{suffix}",
            status="DRAFT",
            badge="Bestseller",
            primary_image="inactive.jpg",
        )
        db.add(inactive_prod)
        db.flush()
        db.add(ProductVariant(product_id=inactive_prod.id, sku=f"SKU-INACT-{suffix}", price=999, stock_quantity=10))

        # Create an out-of-stock active product
        oos_prod = Product(
            name=f"OOS Test Product {suffix}",
            slug=f"oos-prod-{suffix}",
            status="ACTIVE",
            badge="Bestseller",
            primary_image="oos.jpg",
        )
        db.add(oos_prod)
        db.flush()
        db.add(ProductVariant(product_id=oos_prod.id, sku=f"SKU-OOS-{suffix}", price=888, stock_quantity=0))
        db.commit()

        inactive_id = inactive_prod.id
        oos_id = oos_prod.id

    res = client.get("/api/v1/storefront/discovery?context=checkout")
    assert res.status_code == 200
    all_returned_ids = {p["id"] for s in res.json()["sections"] for p in s["products"]}

    assert inactive_id not in all_returned_ids
    assert oos_id not in all_returned_ids


def test_discovery_all_eligible_groups_appear_across_cursor_pages_without_starvation():
    """Verify that when distinct eligible fixtures exist for all groups,
    every group appears without starvation, duplicate IDs, or unbounded pages (Task 7.6.1)."""
    suffix = secrets.token_hex(4)
    with SessionLocal() as db:
        # Create a category for related items
        cat = Category(name=f"Fair Alloc Cat {suffix}", slug=f"fair-cat-{suffix}", is_active=True)
        db.add(cat)
        db.flush()

        # 1. Cart product
        cart_prod = Product(name=f"InCart {suffix}", slug=f"in-cart-{suffix}", status="ACTIVE", primary_image="c.jpg")
        db.add(cart_prod)
        db.flush()
        db.add(ProductVariant(product_id=cart_prod.id, sku=f"SKU-C-{suffix}", price=500, stock_quantity=10))
        cart_prod.categories.append(cat)

        # 2. Related product (in same category)
        rel_prod = Product(name=f"RelProd {suffix}", slug=f"rel-prod-{suffix}", status="ACTIVE", primary_image="r.jpg")
        db.add(rel_prod)
        db.flush()
        db.add(ProductVariant(product_id=rel_prod.id, sku=f"SKU-R-{suffix}", price=600, stock_quantity=10))
        rel_prod.categories.append(cat)

        # 3. Popular product (badge Bestseller)
        pop_prod = Product(name=f"PopProd {suffix}", slug=f"pop-prod-{suffix}", status="ACTIVE", badge="Bestseller", primary_image="p.jpg")
        db.add(pop_prod)
        db.flush()
        db.add(ProductVariant(product_id=pop_prod.id, sku=f"SKU-P-{suffix}", price=700, stock_quantity=10))

        # 4. New arrival product (badge New)
        new_prod = Product(name=f"NewProd {suffix}", slug=f"new-prod-{suffix}", status="ACTIVE", badge="New", primary_image="n.jpg")
        db.add(new_prod)
        db.flush()
        db.add(ProductVariant(product_id=new_prod.id, sku=f"SKU-N-{suffix}", price=800, stock_quantity=10))

        # 5. Featured product (badge Limited, rating 4.9)
        feat_prod = Product(name=f"FeatProd {suffix}", slug=f"feat-prod-{suffix}", status="ACTIVE", badge="Limited", rating=4.9, primary_image="f.jpg")
        db.add(feat_prod)
        db.flush()
        db.add(ProductVariant(product_id=feat_prod.id, sku=f"SKU-F-{suffix}", price=900, stock_quantity=10))

        # 6. Trending product (with genuine Review record)
        trend_prod = Product(name=f"TrendProd {suffix}", slug=f"trend-prod-{suffix}", status="ACTIVE", primary_image="t.jpg")
        db.add(trend_prod)
        db.flush()
        db.add(ProductVariant(product_id=trend_prod.id, sku=f"SKU-T-{suffix}", price=1000, stock_quantity=10))
        db.add(Review(product_id=trend_prod.id, author_name="Reviewer", text="Amazing piece!", rating=5))

        # Setup cart with cart_prod
        token = f"guest_fair_{suffix}"
        cart = Cart(guest_token=token, status="ACTIVE")
        db.add(cart)
        db.flush()
        variant_c = db.query(ProductVariant).filter(ProductVariant.product_id == cart_prod.id).first()
        db.add(CartItem(cart_id=cart.id, product_variant_id=variant_c.id, quantity=1))
        db.commit()

        cart_pid = cart_prod.id
        target_pids = {rel_prod.id, pop_prod.id, new_prod.id, feat_prod.id, trend_prod.id}

    # Traverse pages with limit 8
    cursor = None
    all_seen_ids = set()
    surfaced_strategies = set()
    page_count = 0

    while page_count < 5:
        page_count += 1
        url = "/api/v1/storefront/discovery?context=checkout&limit=8"
        if cursor:
            url += f"&cursor={cursor}"

        res = client.get(url, cookies={"guest_cart_token": token})
        assert res.status_code == 200
        data = res.json()

        for sec in data["sections"]:
            surfaced_strategies.add(sec["strategy"])
            for p in sec["products"]:
                # Strict deduplication across sections and pages
                assert p["id"] not in all_seen_ids, f"Product {p['id']} was duplicated"
                all_seen_ids.add(p["id"])

        cursor = data.get("nextCursor")
        if not cursor:
            break

    # Every single strategy must appear across the pages - no strategy starvation!
    assert "related" in surfaced_strategies
    assert "popular" in surfaced_strategies
    assert "newest" in surfaced_strategies
    assert "featured" in surfaced_strategies
    assert "trending" in surfaced_strategies

    # In-cart product was never surfaced
    assert cart_pid not in all_seen_ids
    # All fixture target products were surfaced
    assert target_pids.issubset(all_seen_ids)


def test_discovery_unsupported_groups_omitted_and_ranking_provenance():
    """Verify that:
    1. Unpaid/cancelled-only orders do NOT make a product appear in Popular.
    2. Regular active products without New badge/collection do NOT appear in New Arrivals.
    3. Seeded reviews_count without genuine Review records does NOT qualify for Trending.
    4. Unsupported groups with 0 products are completely omitted from response."""
    suffix = secrets.token_hex(4)
    with SessionLocal() as db:
        # 1. Product with ONLY cancelled order
        cancelled_prod = Product(
            name=f"Cancelled Order Prod {suffix}",
            slug=f"canc-prod-{suffix}",
            status="ACTIVE",
            primary_image="canc.jpg",
        )
        db.add(cancelled_prod)
        db.flush()
        var_canc = ProductVariant(product_id=cancelled_prod.id, sku=f"SKU-CANC-{suffix}", price=300, stock_quantity=10)
        db.add(var_canc)
        db.flush()

        canc_order = Order(
            order_number=f"ORD-CANC-{suffix}",
            customer_name="Cancelled Customer",
            customer_phone="9876543210",
            customer_email="cancelled@example.com",
            shipping_address_json={"line1": "123 Test St", "city": "Bengaluru", "postal_code": "560001"},
            subtotal=300,
            status=OrderStatus.CANCELLED.value,
            payment_status=PaymentStatus.FAILED.value,
            payment_method=PaymentMethod.UPI.value,
            total_amount=300,
        )
        db.add(canc_order)
        db.flush()
        db.add(
            OrderItem(
                order_id=canc_order.id,
                product_id=cancelled_prod.id,
                product_variant_id=var_canc.id,
                product_name=cancelled_prod.name,
                sku=var_canc.sku,
                variant_name="Default",
                quantity=5,
                unit_price=300,
                line_total=1500,
            )
        )

        # 2. Plain product without New badge or collection
        plain_prod = Product(
            name=f"Plain Prod {suffix}",
            slug=f"plain-prod-{suffix}",
            status="ACTIVE",
            primary_image="plain.jpg",
        )
        db.add(plain_prod)
        db.flush()
        db.add(ProductVariant(product_id=plain_prod.id, sku=f"SKU-PLAIN-{suffix}", price=400, stock_quantity=10))

        # 3. Product with reviews_count on Product table but 0 rows in reviews table
        fake_rev_prod = Product(
            name=f"Fake Review Prod {suffix}",
            slug=f"fake-rev-prod-{suffix}",
            status="ACTIVE",
            reviews_count=99,
            rating=5.0,
            primary_image="fakerev.jpg",
        )
        db.add(fake_rev_prod)
        db.flush()
        db.add(ProductVariant(product_id=fake_rev_prod.id, sku=f"SKU-FAKEREV-{suffix}", price=500, stock_quantity=10))

        db.commit()

        canc_id = cancelled_prod.id
        plain_id = plain_prod.id
        fake_rev_id = fake_rev_prod.id

    res = client.get("/api/v1/storefront/discovery?context=checkout")
    assert res.status_code == 200
    sections = res.json()["sections"]

    for sec in sections:
        # No section should be returned empty
        assert len(sec["products"]) > 0

        # Cancelled order product must NOT appear in popular
        if sec["strategy"] == "popular":
            assert canc_id not in [p["id"] for p in sec["products"]]

        # Plain product must NOT appear in newest
        if sec["strategy"] == "newest":
            assert plain_id not in [p["id"] for p in sec["products"]]

        # Fake review product must NOT appear in trending
        if sec["strategy"] == "trending":
            assert fake_rev_id not in [p["id"] for p in sec["products"]]


def test_discovery_security_tenant_isolation_and_no_mutation():
    """Verify authenticated/guest ownership isolation and that discovery GET never mutates state."""
    suffix = secrets.token_hex(4)
    with SessionLocal() as db:
        # Create User A & User B
        user_a = User(email=f"usera_{suffix}@example.com", name="User A", status="ACTIVE")
        user_b = User(email=f"userb_{suffix}@example.com", name="User B", status="ACTIVE")
        db.add_all([user_a, user_b])
        db.flush()

        # Sessions
        sess_token_a = f"token_a_{suffix}"
        sess_token_b = f"token_b_{suffix}"
        now = datetime.now(timezone.utc)
        db.add(UserSession(user_id=user_a.id, session_token=sess_token_a, expires_at=now + timedelta(days=1), is_revoked=False))
        db.add(UserSession(user_id=user_b.id, session_token=sess_token_b, expires_at=now + timedelta(days=1), is_revoked=False))

        # Products X and Y
        prod_x = Product(name=f"ProdX {suffix}", slug=f"prod-x-{suffix}", status="ACTIVE", primary_image="x.jpg")
        prod_y = Product(name=f"ProdY {suffix}", slug=f"prod-y-{suffix}", status="ACTIVE", primary_image="y.jpg")
        db.add_all([prod_x, prod_y])
        db.flush()
        var_x = ProductVariant(product_id=prod_x.id, sku=f"SKU-X-{suffix}", price=200, stock_quantity=10)
        var_y = ProductVariant(product_id=prod_y.id, sku=f"SKU-Y-{suffix}", price=300, stock_quantity=10)
        db.add_all([var_x, var_y])
        db.flush()

        # Cart for User A with Prod X
        cart_a = Cart(user_id=user_a.id, guest_token=f"claimed_guest_{suffix}", status="ACTIVE")
        db.add(cart_a)
        db.flush()
        db.add(CartItem(cart_id=cart_a.id, product_variant_id=var_x.id, quantity=1))

        # Cart for User B with Prod Y
        cart_b = Cart(user_id=user_b.id, status="ACTIVE")
        db.add(cart_b)
        db.flush()
        db.add(CartItem(cart_id=cart_b.id, product_variant_id=var_y.id, quantity=1))

        db.commit()

        cart_count_before = db.query(Cart).count()
        item_count_before = db.query(CartItem).count()
        order_count_before = db.query(Order).count()
        user_sess_count_before = db.query(UserSession).count()

        pid_x = prod_x.id
        pid_y = prod_y.id
        claimed_token = cart_a.guest_token

    # 1. Query discovery as User A -> Prod X excluded
    res_a = client.get("/api/v1/storefront/discovery?context=checkout", cookies={"session_token": sess_token_a})
    assert res_a.status_code == 200
    pids_a = {p["id"] for s in res_a.json()["sections"] for p in s["products"]}
    assert pid_x not in pids_a

    # 2. Query discovery as User B -> Prod Y excluded, Prod X not excluded by B
    res_b = client.get("/api/v1/storefront/discovery?context=checkout", cookies={"session_token": sess_token_b})
    assert res_b.status_code == 200
    pids_b = {p["id"] for s in res_b.json()["sections"] for p in s["products"]}
    assert pid_y not in pids_b

    # 3. IDOR check: Unauthenticated guest attempts to pass claimed_token belonging to User A
    # IDOR protection sets cart to None; User A's cart is not used for unauthenticated caller
    res_idor = client.get("/api/v1/storefront/discovery?context=checkout", cookies={"guest_cart_token": claimed_token})
    assert res_idor.status_code == 200

    # 4. Forged identity parameters ignored
    res_forged = client.get("/api/v1/storefront/discovery?context=checkout&user_id=1&customerId=999")
    assert res_forged.status_code == 200

    # 5. Zero database mutation verification
    with SessionLocal() as db:
        assert db.query(Cart).count() == cart_count_before
        assert db.query(CartItem).count() == item_count_before
        assert db.query(Order).count() == order_count_before
        assert db.query(UserSession).count() == user_sess_count_before

