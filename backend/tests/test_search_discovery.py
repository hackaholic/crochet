"""Unit and integration tests for Search Discovery Suggestions, Telemetry, and Order-Backed Ranking."""

from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient

from app.api.v1.catalogue import reset_search_event_rate_limit_store
from app.db.session import SessionLocal
from app.main import app
from app.models import (
    Category,
    Order,
    OrderItem,
    OrderStatus,
    PaymentStatus,
    Product,
    ProductVariant,
    SearchEvent,
    User,
    UserIdentity,
)
from app.services.search import prune_expired_search_events

client = TestClient(app)


# -----------------------------------------------------------------------------
# 1. Empty State Fallback Tests (R1)
# -----------------------------------------------------------------------------

def test_search_suggestions_empty_state_returns_empty_arrays():
    """Verify that empty search discovery returns empty lists without hardcoded mock trends."""
    res = client.get("/api/v1/products/search/suggestions")
    assert res.status_code == 200
    data = res.json()
    assert "trending_keywords" in data
    assert "trending_products" in data
    assert data["trending_keywords"] == []
    assert data["trending_products"] == []


# -----------------------------------------------------------------------------
# 2. Telemetry Ingestion & Query Normalization Tests (R2)
# -----------------------------------------------------------------------------

def test_record_search_event_normalization():
    """Verify normalization: lowercasing, whitespace trimming and collapsing, outer punctuation removal."""
    res1 = client.post("/api/v1/products/search/events", json={"query": "  Crochet Flowers  "})
    assert res1.status_code == 200
    assert res1.json() == {"status": "recorded"}

    res2 = client.post("/api/v1/products/search/events", json={"query": "amigurumi toys!"})
    assert res2.status_code == 200

    res3 = client.post("/api/v1/products/search/events", json={"query": "pink    carnations"})
    assert res3.status_code == 200

    with SessionLocal() as db:
        events = db.query(SearchEvent).all()
        queries = [e.query for e in events]
        assert "crochet flowers" in queries
        assert "amigurumi toys" in queries
        assert "pink carnations" in queries


# -----------------------------------------------------------------------------
# 3. Privacy Sanitization & PII Suppression Tests (R2)
# -----------------------------------------------------------------------------

def test_record_search_event_suppresses_emails():
    """Verify that email addresses in search queries are suppressed and never persisted."""
    email_queries = [
        "user@example.com",
        "contact customer.support@sulocraft.org please",
        "john.doe+test@domain.co.in",
    ]
    for q in email_queries:
        res = client.post("/api/v1/products/search/events", json={"query": q})
        assert res.status_code == 200
        assert res.json() == {"status": "recorded"}

    with SessionLocal() as db:
        events = db.query(SearchEvent).all()
        assert len(events) == 0


def test_record_search_event_suppresses_phone_numbers():
    """Verify that phone numbers (10+ digits or formatted) are suppressed and never persisted."""
    phone_queries = [
        "9876543210",
        "+91 98765 43210",
        "call 123-456-7890",
        "+1-555-0199",
    ]
    for q in phone_queries:
        res = client.post("/api/v1/products/search/events", json={"query": q})
        assert res.status_code == 200
        assert res.json() == {"status": "recorded"}

    with SessionLocal() as db:
        events = db.query(SearchEvent).all()
        assert len(events) == 0


def test_record_search_event_suppresses_credit_cards():
    """Verify that payment card-like sequences are suppressed and never persisted."""
    res = client.post("/api/v1/products/search/events", json={"query": "4111 2222 3333 4444"})
    assert res.status_code == 200

    with SessionLocal() as db:
        events = db.query(SearchEvent).all()
        assert len(events) == 0


def test_record_search_event_suppresses_invalid_length_and_symbols():
    """Verify that queries too short (<2 chars), too long (>80 chars), or only symbols are suppressed."""
    invalid_queries = [
        "a",  # len 1
        "a" * 81,  # len 81
        "???!!!...",  # punctuation only
        "   ",  # whitespace only
    ]
    for q in invalid_queries:
        res = client.post("/api/v1/products/search/events", json={"query": q})
        assert res.status_code == 200

    with SessionLocal() as db:
        events = db.query(SearchEvent).all()
        assert len(events) == 0


# -----------------------------------------------------------------------------
# 4. Trending Keywords Gating & Rolling Window Tests (R1, R2)
# -----------------------------------------------------------------------------

def test_trending_keywords_minimum_threshold_gating():
    """Verify that trending keywords require minimum 3 occurrences before surfacing."""
    with SessionLocal() as db:
        # Term 1: 1 occurrence (should not appear)
        db.add(SearchEvent(query="rare search item"))
        # Term 2: 2 occurrences (should not appear)
        db.add(SearchEvent(query="semi rare term"))
        db.add(SearchEvent(query="semi rare term"))
        # Term 3: 3 occurrences (should appear)
        for _ in range(3):
            db.add(SearchEvent(query="trending tulips"))
        # Term 4: 5 occurrences (should appear first)
        for _ in range(5):
            db.add(SearchEvent(query="crochet roses"))
        db.commit()

    res = client.get("/api/v1/products/search/suggestions")
    assert res.status_code == 200
    keywords = res.json()["trending_keywords"]

    # Only terms with count >= 3 appear
    terms = [k["term"] for k in keywords]
    assert "crochet roses" in terms
    assert "trending tulips" in terms
    assert "semi rare term" not in terms
    assert "rare search item" not in terms

    # crochet roses (5) should precede trending tulips (3)
    assert terms[0] == "crochet roses"
    assert terms[1] == "trending tulips"


def test_trending_keywords_rolling_30_day_window():
    """Verify that search events older than 30 days are excluded from trending aggregation."""
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        # 5 searches from 35 days ago (should be excluded)
        for _ in range(5):
            db.add(SearchEvent(query="expired trend", created_at=now - timedelta(days=35)))
        # 3 searches from 5 days ago (should be included)
        for _ in range(3):
            db.add(SearchEvent(query="active trend", created_at=now - timedelta(days=5)))
        db.commit()

    res = client.get("/api/v1/products/search/suggestions")
    assert res.status_code == 200
    keywords = res.json()["trending_keywords"]
    terms = [k["term"] for k in keywords]

    assert "active trend" in terms
    assert "expired trend" not in terms


def test_trending_keywords_limit_parameter():
    """Verify keyword_limit query parameter bounds and pagination."""
    with SessionLocal() as db:
        for i in range(5):
            term = f"popular term {i}"
            for _ in range(3 + i):
                db.add(SearchEvent(query=term))
        db.commit()

    res = client.get("/api/v1/products/search/suggestions?keyword_limit=2")
    assert res.status_code == 200
    keywords = res.json()["trending_keywords"]
    assert len(keywords) == 2


# -----------------------------------------------------------------------------
# 5. Order-Backed Trending Product Ranking & Exclusions (R3)
# -----------------------------------------------------------------------------

def test_trending_products_ranked_by_order_line_volume():
    """Verify that products are ranked by paid/confirmed line item volume in rolling 30 days."""
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        products = db.query(Product).filter(Product.status == "ACTIVE").limit(2).all()
        assert len(products) >= 2, "Test requires seeded catalogue products"
        prod_a, prod_b = products[0], products[1]

        order1 = Order(
            order_number="ORD-TEST-TREND-001",
            customer_name="Customer 1",
            customer_phone="9999900001",
            shipping_address_json={"line1": "Test", "city": "Bengaluru"},
            status=OrderStatus.CONFIRMED.value,
            payment_status=PaymentStatus.PAID.value,
            subtotal=1000,
            total_amount=1000,
            created_at=now - timedelta(days=2),
        )
        db.add(order1)
        db.flush()

        # Prod A: 10 units, Prod B: 3 units
        db.add(OrderItem(
            order_id=order1.id,
            product_id=prod_a.id,
            product_name=prod_a.name,
            sku="SKU-A",
            variant_name="Default",
            unit_price=100,
            quantity=10,
            line_total=1000,
            created_at=now - timedelta(days=2),
        ))
        db.add(OrderItem(
            order_id=order1.id,
            product_id=prod_b.id,
            product_name=prod_b.name,
            sku="SKU-B",
            variant_name="Default",
            unit_price=100,
            quantity=3,
            line_total=300,
            created_at=now - timedelta(days=2),
        ))
        db.commit()

        prod_a_id = prod_a.id
        prod_b_id = prod_b.id

    res = client.get("/api/v1/products/search/suggestions?product_limit=4")
    assert res.status_code == 200
    trending_products = res.json()["trending_products"]
    assert len(trending_products) >= 2

    # Prod A had higher volume (10 > 3), must be ranked first
    assert trending_products[0]["id"] == prod_a_id
    assert trending_products[1]["id"] == prod_b_id

    # Verify standard ProductListItem schema fields
    item = trending_products[0]
    assert "slug" in item
    assert "price" in item
    assert "pricePaise" in item
    assert "inStock" in item
    assert item["inStock"] is True
    assert "imageUrls" in item
    assert "primaryCategory" in item


def test_trending_products_excludes_cancelled_and_refunded_orders():
    """Verify that cancelled and refunded orders do not contribute to trending volume."""
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        products = db.query(Product).filter(Product.status == "ACTIVE").limit(2).all()
        prod_cancelled, prod_valid = products[0], products[1]

        # Order 1: CANCELLED order with large volume (20 units)
        order_canc = Order(
            order_number="ORD-CANC-001",
            customer_name="Customer Cancelled",
            customer_phone="9999900002",
            shipping_address_json={"line1": "Test", "city": "Bengaluru"},
            status=OrderStatus.CANCELLED.value,
            payment_status=PaymentStatus.PAID.value,
            subtotal=2000,
            total_amount=2000,
            created_at=now - timedelta(days=1),
        )
        db.add(order_canc)
        db.flush()
        db.add(OrderItem(
            order_id=order_canc.id,
            product_id=prod_cancelled.id,
            product_name=prod_cancelled.name,
            sku="SKU-CANC",
            variant_name="Default",
            unit_price=100,
            quantity=20,
            line_total=2000,
            created_at=now - timedelta(days=1),
        ))

        # Order 2: Valid CONFIRMED order (2 units)
        order_valid = Order(
            order_number="ORD-VALID-001",
            customer_name="Customer Valid",
            customer_phone="9999900003",
            shipping_address_json={"line1": "Test", "city": "Bengaluru"},
            status=OrderStatus.CONFIRMED.value,
            payment_status=PaymentStatus.PAID.value,
            subtotal=200,
            total_amount=200,
            created_at=now - timedelta(days=1),
        )
        db.add(order_valid)
        db.flush()
        db.add(OrderItem(
            order_id=order_valid.id,
            product_id=prod_valid.id,
            product_name=prod_valid.name,
            sku="SKU-VALID",
            variant_name="Default",
            unit_price=100,
            quantity=2,
            line_total=200,
            created_at=now - timedelta(days=1),
        ))
        db.commit()

        prod_valid_id = prod_valid.id
        prod_cancelled_id = prod_cancelled.id

    res = client.get("/api/v1/products/search/suggestions")
    assert res.status_code == 200
    trending_products = res.json()["trending_products"]

    product_ids = [p["id"] for p in trending_products]
    assert prod_valid_id in product_ids
    assert prod_cancelled_id not in product_ids


def test_trending_products_excludes_failed_payments():
    """Verify that orders with failed payments do not contribute to trending volume."""
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        prod = db.query(Product).filter(Product.status == "ACTIVE").first()

        order_failed = Order(
            order_number="ORD-FAILED-001",
            customer_name="Customer Failed",
            customer_phone="9999900004",
            shipping_address_json={"line1": "Test", "city": "Bengaluru"},
            status=OrderStatus.CONFIRMED.value,
            payment_status=PaymentStatus.FAILED.value,
            subtotal=500,
            total_amount=500,
            created_at=now - timedelta(days=1),
        )
        db.add(order_failed)
        db.flush()
        db.add(OrderItem(
            order_id=order_failed.id,
            product_id=prod.id,
            product_name=prod.name,
            sku="SKU-F",
            variant_name="Default",
            unit_price=100,
            quantity=15,
            line_total=1500,
            created_at=now - timedelta(days=1),
        ))
        db.commit()

    res = client.get("/api/v1/products/search/suggestions")
    assert res.status_code == 200
    assert len(res.json()["trending_products"]) == 0


def test_trending_products_excludes_refunded_payments():
    """Verify that orders with refunded payment status do not contribute to trending volume."""
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        prod = db.query(Product).filter(Product.status == "ACTIVE").first()

        order_refunded = Order(
            order_number="ORD-REFUND-001",
            customer_name="Customer Refunded",
            customer_phone="9999900007",
            shipping_address_json={"line1": "Test", "city": "Bengaluru"},
            status=OrderStatus.CONFIRMED.value,
            payment_status=PaymentStatus.REFUNDED.value,
            subtotal=500,
            total_amount=500,
            created_at=now - timedelta(days=1),
        )
        db.add(order_refunded)
        db.flush()
        db.add(OrderItem(
            order_id=order_refunded.id,
            product_id=prod.id,
            product_name=prod.name,
            sku="SKU-REF",
            variant_name="Default",
            unit_price=100,
            quantity=15,
            line_total=1500,
            created_at=now - timedelta(days=1),
        ))
        db.commit()

    res = client.get("/api/v1/products/search/suggestions")
    assert res.status_code == 200
    assert len(res.json()["trending_products"]) == 0


def test_trending_products_excludes_orders_older_than_30_days():
    """Verify that orders older than rolling 30-day window are excluded."""
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        prod = db.query(Product).filter(Product.status == "ACTIVE").first()

        order_old = Order(
            order_number="ORD-OLD-001",
            customer_name="Customer Old",
            customer_phone="9999900005",
            shipping_address_json={"line1": "Test", "city": "Bengaluru"},
            status=OrderStatus.CONFIRMED.value,
            payment_status=PaymentStatus.PAID.value,
            subtotal=500,
            total_amount=500,
            created_at=now - timedelta(days=32),
        )
        db.add(order_old)
        db.flush()
        db.add(OrderItem(
            order_id=order_old.id,
            product_id=prod.id,
            product_name=prod.name,
            sku="SKU-OLD",
            variant_name="Default",
            unit_price=100,
            quantity=10,
            line_total=1000,
            created_at=now - timedelta(days=32),
        ))
        db.commit()

    res = client.get("/api/v1/products/search/suggestions")
    assert res.status_code == 200
    assert len(res.json()["trending_products"]) == 0


def test_trending_products_excludes_out_of_stock_products():
    """Verify that out-of-stock products are excluded from trending products."""
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        prod = db.query(Product).filter(Product.status == "ACTIVE").first()
        prod_id = prod.id

        # Set all variants to out of stock
        for v in prod.variants:
            v.stock_quantity = 0
        db.flush()

        order = Order(
            order_number="ORD-OOS-001",
            customer_name="Customer OOS",
            customer_phone="9999900006",
            shipping_address_json={"line1": "Test", "city": "Bengaluru"},
            status=OrderStatus.CONFIRMED.value,
            payment_status=PaymentStatus.PAID.value,
            subtotal=500,
            total_amount=500,
            created_at=now - timedelta(days=1),
        )
        db.add(order)
        db.flush()
        db.add(OrderItem(
            order_id=order.id,
            product_id=prod_id,
            product_name=prod.name,
            sku="SKU-OOS",
            variant_name="Default",
            unit_price=100,
            quantity=5,
            line_total=500,
            created_at=now - timedelta(days=1),
        ))
        db.commit()

    res = client.get("/api/v1/products/search/suggestions")
    assert res.status_code == 200
    product_ids = [p["id"] for p in res.json()["trending_products"]]
    assert prod_id not in product_ids


# -----------------------------------------------------------------------------
# 6. Route Precedence & System Integrity
# -----------------------------------------------------------------------------

def test_route_precedence_and_wildcard_safety():
    """Verify that GET /products/search/suggestions does not collide with /products/{slug_or_id}."""
    res = client.get("/api/v1/products/search/suggestions")
    assert res.status_code == 200
    data = res.json()
    assert "trending_keywords" in data
    assert "trending_products" in data

    # Verify standard search still works
    search_res = client.get("/api/v1/products/search?q=rose")
    assert search_res.status_code == 200
    assert isinstance(search_res.json(), list)

    # Verify standard product slug lookup still works
    with SessionLocal() as db:
        prod = db.query(Product).filter(Product.status == "ACTIVE").first()
        prod_slug = prod.slug

    slug_res = client.get(f"/api/v1/products/{prod_slug}")
    assert slug_res.status_code == 200
    assert slug_res.json()["slug"] == prod_slug


# -----------------------------------------------------------------------------
# 7. Request Bounds, Rate Limiting & Non-Interference Tests (Task 9.8.1)
# -----------------------------------------------------------------------------

def test_search_events_oversized_payload_rejected_at_schema():
    """Verify that oversized search queries (> 120 chars) are rejected with 422 before DB writes."""
    reset_search_event_rate_limit_store()
    oversized_query = "a" * 121
    res = client.post("/api/v1/products/search/events", json={"query": oversized_query})
    assert res.status_code == 422
    data = res.json()
    assert "detail" in data

    # Verify nothing was persisted
    with SessionLocal() as db:
        events = db.query(SearchEvent).filter(SearchEvent.query == oversized_query).all()
        assert len(events) == 0


def test_search_events_client_rate_limiting():
    """Verify that search event ingestion is rate limited to 60 requests per minute per IP."""
    reset_search_event_rate_limit_store()

    # Send 60 legitimate requests
    for i in range(60):
        res = client.post("/api/v1/products/search/events", json={"query": f"test query {i}"})
        assert res.status_code == 200, f"Request {i+1} failed with {res.status_code}"

    # 61st request should be rate limited with HTTP 429
    res_overflow = client.post("/api/v1/products/search/events", json={"query": "overflow query"})
    assert res_overflow.status_code == 429
    assert "Rate limit exceeded" in res_overflow.json()["detail"]

    # Reset store for cleanup
    reset_search_event_rate_limit_store()


def test_catalogue_search_unaffected_when_rate_limited():
    """Verify that catalogue search queries continue to function even when telemetry is rate-limited."""
    reset_search_event_rate_limit_store()

    # Trigger rate limit on search events
    for _ in range(60):
        client.post("/api/v1/products/search/events", json={"query": "burst event"})

    res_limit = client.post("/api/v1/products/search/events", json={"query": "blocked event"})
    assert res_limit.status_code == 429

    # Verify standard catalogue search remains fully functional
    search_res = client.get("/api/v1/products/search?q=rose")
    assert search_res.status_code == 200
    assert isinstance(search_res.json(), list)

    # Reset store for cleanup
    reset_search_event_rate_limit_store()


# -----------------------------------------------------------------------------
# 8. Event Retention, Pruning & Maintenance Tests (Task 9.8.2)
# -----------------------------------------------------------------------------

def test_prune_expired_search_events_retention_policy():
    """Verify that search events older than the 30-day retention window are purged while newer events are kept."""
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        # Expired events (>30 days old)
        db.add(SearchEvent(query="expired term 1", created_at=now - timedelta(days=31)))
        db.add(SearchEvent(query="expired term 2", created_at=now - timedelta(days=45)))
        db.add(SearchEvent(query="expired term 3", created_at=now - timedelta(days=90)))

        # Unexpired events (<=30 days old)
        db.add(SearchEvent(query="recent term 1", created_at=now - timedelta(days=29)))
        db.add(SearchEvent(query="recent term 2", created_at=now - timedelta(days=5)))
        db.add(SearchEvent(query="recent term 3", created_at=now))
        db.commit()

        pruned_count = prune_expired_search_events(db, retention_days=30)
        assert pruned_count == 3

        remaining_events = db.query(SearchEvent).all()
        remaining_queries = {e.query for e in remaining_events}
        assert remaining_queries == {"recent term 1", "recent term 2", "recent term 3"}


def test_prune_custom_retention_window():
    """Verify pruning with custom retention period (e.g., 7 days)."""
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        db.add(SearchEvent(query="old 10 days", created_at=now - timedelta(days=10)))
        db.add(SearchEvent(query="fresh 3 days", created_at=now - timedelta(days=3)))
        db.commit()

        pruned = prune_expired_search_events(db, retention_days=7)
        assert pruned == 1

        remaining = db.query(SearchEvent).all()
        assert len(remaining) == 1
        assert remaining[0].query == "fresh 3 days"


def test_prune_zero_when_no_expired_events():
    """Verify pruning returns 0 and leaves records intact when all events are fresh."""
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        db.add(SearchEvent(query="today query", created_at=now))
        db.commit()

        pruned = prune_expired_search_events(db, retention_days=30)
        assert pruned == 0

        remaining = db.query(SearchEvent).all()
        assert len(remaining) == 1


def test_opportunistic_background_pruning_scheduling():
    """Verify maybe_schedule_opportunistic_pruning schedules background task when interval elapsed."""
    from fastapi import BackgroundTasks
    from app.services.search import maybe_schedule_opportunistic_pruning, reset_prune_timestamp

    reset_prune_timestamp()
    bg_tasks = BackgroundTasks()

    # First call: interval has elapsed (since _LAST_PRUNE_TIMESTAMP == 0.0) -> schedules task
    scheduled = maybe_schedule_opportunistic_pruning(bg_tasks, interval_seconds=3600.0)
    assert scheduled is True
    assert len(bg_tasks.tasks) == 1

    # Immediate second call: interval has not elapsed -> skips
    scheduled_second = maybe_schedule_opportunistic_pruning(bg_tasks, interval_seconds=3600.0)
    assert scheduled_second is False
    assert len(bg_tasks.tasks) == 1


def test_admin_prune_search_events_endpoint():
    """Verify POST /api/v1/admin/maintenance/search-events/prune requires admin and cleans expired events."""
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        db.add(SearchEvent(query="expired admin test", created_at=now - timedelta(days=35)))
        db.add(SearchEvent(query="active admin test", created_at=now - timedelta(days=2)))
        db.commit()

    # 1. Unauthenticated request rejected
    res_unauth = client.post("/api/v1/admin/maintenance/search-events/prune")
    assert res_unauth.status_code in (401, 403)

    # 2. Authenticated admin request
    admin_email = "admin_search_retention@sulocraft.com"
    with SessionLocal() as db:
        admin = db.query(User).filter(User.email == admin_email).first()
        if not admin:
            admin = User(name="Admin Retention", email=admin_email, phone="9797979797", role="ADMIN", status="ACTIVE")
            db.add(admin)
            db.flush()
            db.add(UserIdentity(user_id=admin.id, provider="email", provider_subject=admin_email))
            db.commit()
        elif admin.role != "ADMIN":
            admin.role = "ADMIN"
            db.commit()

    login_res = client.post("/api/v1/auth/google", json={
        "credential": "mock_admin_token_retention",
        "email": admin_email,
        "name": "Admin Retention",
        "sub": "admin_sub_retention",
    })
    assert login_res.status_code == 200
    cookies = dict(login_res.cookies)

    res_admin = client.post("/api/v1/admin/maintenance/search-events/prune?retention_days=30", cookies=cookies)
    assert res_admin.status_code == 200
    data = res_admin.json()
    assert data["status"] == "ok"
    assert data["pruned_count"] == 1
    assert data["retention_days"] == 30

    # Verify database state
    with SessionLocal() as db:
        remaining = db.query(SearchEvent).all()
        assert len(remaining) == 1
        assert remaining[0].query == "active admin test"


def test_cli_prune_search_events_script():
    """Verify execution of backend/scripts/prune_search_events.py CLI script."""
    import subprocess
    import sys

    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        db.add(SearchEvent(query="expired cli test", created_at=now - timedelta(days=40)))
        db.add(SearchEvent(query="fresh cli test", created_at=now))
        db.commit()

    result = subprocess.run(
        [sys.executable, "backend/scripts/prune_search_events.py", "--days", "30"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "Successfully pruned 1 expired search event" in result.stdout or "Successfully pruned 1 expired search event" in result.stderr

    with SessionLocal() as db:
        remaining = db.query(SearchEvent).all()
        assert len(remaining) == 1
        assert remaining[0].query == "fresh cli test"


