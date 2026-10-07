"""End-to-End Opaque-Box Test Suite for Work 009: Storefront Search Discovery & Telemetry.

Authoritative Requirements Source:
- /home/anu/git/crochet/.agents/ORIGINAL_REQUEST.md (§R1, §R2, §R3, §R4)
- /home/anu/git/crochet/.agents/teamwork_preview_orchestrator_1/PROJECT.md
- /home/anu/git/crochet/.agents/teamwork_preview_orchestrator_1/TEST_INFRA.md

Coverage Structure:
- Tier 1: Feature Coverage (11 features x 5 tests each = 55 tests)
  - F1: GET /api/v1/products/search/suggestions basic contract
  - F2: Bounds validation (keyword_limit 1-10, product_limit 1-8)
  - F3: Zero-data empty fallback (trending_keywords: [], trending_products: [])
  - F4: POST /api/v1/products/search/events ingestion
  - F5: Query normalization (trim, lowercase, whitespace collapse, punctuation)
  - F6: Privacy suppression (email, phone, >80 chars)
  - F7: Keyword threshold gating (count < 3 excluded, count >= 3 included)
  - F8: Order-backed trending product ranking (volume sum, rolling 30d)
  - F9: Order exclusion (cancelled, refunded, failed payment excluded)
  - F10: Product qualification (active, in-stock, image, category)
  - F11: Telemetry failure non-interference with search
- Tier 2: Boundary & Corner Cases (24 tests)
  - Limits boundary checks (min, max, underflow, overflow, invalid types)
  - Query length boundary checks (len 1, 2, 80, 81, 10000)
  - Complex PII patterns (embedded email, formatted phone)
  - Date window boundary checks (29d 23h vs 30d 1h)
  - Stock boundaries (0 vs 1)
  - Ties & determinism
  - SQL injection & XSS safety
- Tier 3: Cross-Feature Interactions (7 tests)
  - Telemetry to suggestions end-to-end
  - Orders to trending products end-to-end
  - Dual-source simultaneous suggestions
  - Dynamic threshold activation (2 -> 3 queries)
  - Out of stock transition
  - Repeated PII never activates threshold
  - Order cancellation dynamically removes product
- Tier 4: Real-World Scenarios (5 tests)
  - S1: Full Search & Discovery Lifecycle
  - S2: Adversarial Telemetry & Privacy Audit
  - S3: Festive Promotional Sales Wave
  - S4: Flash Sale Stock Depletion
  - S5: Store Launch Day-0 Zero State
"""

import uuid
from datetime import datetime, timedelta, timezone
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.main import app
from app.db.session import SessionLocal
from app.models import (
    Order,
    OrderItem,
    OrderStatus,
    PaymentStatus,
    Product,
    ProductVariant,
    Category,
)


# -----------------------------------------------------------------------------
# Fixtures & Test Helpers
# -----------------------------------------------------------------------------

@pytest.fixture
def client() -> TestClient:
    """FastAPI test client fixture."""
    return TestClient(app)


@pytest.fixture
def db() -> Session:
    """Database session fixture with proper closing."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(autouse=True)
def clean_search_test_events():
    """Ensure search events table is clean before and after each test."""
    def _cleanup():
        with SessionLocal() as session:
            try:
                session.execute(text("DELETE FROM search_events"))
                session.commit()
            except Exception:
                session.rollback()

    _cleanup()
    yield
    _cleanup()


def post_search_event(client: TestClient, query: str):
    """Helper to post a search telemetry event."""
    return client.post("/api/v1/products/search/events", json={"query": query})


def get_suggestions(
    client: TestClient,
    keyword_limit: int | str | None = None,
    product_limit: int | str | None = None,
):
    """Helper to query search suggestions with optional limits."""
    params = {}
    if keyword_limit is not None:
        params["keyword_limit"] = keyword_limit
    if product_limit is not None:
        params["product_limit"] = product_limit
    return client.get("/api/v1/products/search/suggestions", params=params)


def create_test_order(
    db: Session,
    product_id: int,
    quantity: int = 1,
    status: str = OrderStatus.CONFIRMED.value,
    payment_status: str = PaymentStatus.PAID.value,
    days_ago: float = 0.0,
    order_number: str | None = None,
) -> Order:
    """Helper to create an order and corresponding line item."""
    if not order_number:
        order_number = f"ORD-TEST-{uuid.uuid4().hex[:10].upper()}"
    order_time = datetime.now(timezone.utc) - timedelta(days=days_ago)

    product = db.query(Product).filter(Product.id == product_id).first()
    product_name = product.name if product else f"Product {product_id}"

    order = Order(
        order_number=order_number,
        customer_name="Test Customer",
        customer_phone="9876543210",
        customer_email="customer@example.com",
        shipping_address_json={
            "name": "Test Customer",
            "phone": "9876543210",
            "line1": "123 MG Road",
            "city": "Bengaluru",
            "state": "Karnataka",
            "postal_code": "560001",
            "country": "IN",
        },
        status=status,
        payment_status=payment_status,
        payment_method="UPI",
        currency="INR",
        subtotal=499 * quantity,
        shipping_fee=0,
        total_amount=499 * quantity,
        created_at=order_time,
        updated_at=order_time,
    )
    db.add(order)
    db.flush()

    item = OrderItem(
        order_id=order.id,
        product_id=product_id,
        product_name=product_name,
        sku=f"SKU-TEST-{product_id}",
        variant_name="Standard",
        unit_price=499,
        quantity=quantity,
        line_total=499 * quantity,
        created_at=order_time,
    )
    db.add(item)
    db.commit()
    db.refresh(order)
    return order


def get_active_catalogue_products(db: Session, count: int = 5) -> list[Product]:
    """Retrieve active seeded products with stock and valid images."""
    products = (
        db.query(Product)
        .filter(Product.status == "ACTIVE")
        .all()
    )
    valid = []
    for p in products:
        if p.variants and any(v.stock_quantity > 0 for v in p.variants) and p.primary_image:
            valid.append(p)
        if len(valid) >= count:
            break
    assert len(valid) >= count, f"Expected at least {count} active products in seed data"
    return valid


# =============================================================================
# TIER 1: FEATURE COVERAGE (55 tests)
# =============================================================================

# --- Feature 1: GET /api/v1/products/search/suggestions Basic Contract ---

def test_tier1_f1_suggestions_status_code_200(client: TestClient):
    """Suggestions endpoint returns HTTP 200 OK."""
    res = get_suggestions(client)
    assert res.status_code == 200


def test_tier1_f1_suggestions_top_level_keys(client: TestClient):
    """Suggestions response contains top-level keys trending_keywords and trending_products."""
    res = get_suggestions(client)
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, dict)
    assert "trending_keywords" in data
    assert "trending_products" in data
    assert isinstance(data["trending_keywords"], list)
    assert isinstance(data["trending_products"], list)


def test_tier1_f1_suggestions_keywords_schema(client: TestClient):
    """Trending keywords entries contain a term string field."""
    for _ in range(3):
        post_search_event(client, "crochet sunflower")
    res = get_suggestions(client)
    assert res.status_code == 200
    keywords = res.json()["trending_keywords"]
    assert len(keywords) >= 1
    first = keywords[0]
    assert isinstance(first, dict)
    assert "term" in first
    assert isinstance(first["term"], str)
    assert first["term"] == "crochet sunflower"


def test_tier1_f1_suggestions_products_schema(client: TestClient, db: Session):
    """Trending products conform to ProductListItem schema matching /products/search."""
    prods = get_active_catalogue_products(db, 1)
    create_test_order(db, prods[0].id, quantity=3)

    res = get_suggestions(client)
    assert res.status_code == 200
    products = res.json()["trending_products"]
    assert len(products) >= 1
    item = products[0]
    required_keys = ["id", "name", "slug", "price", "currency", "image", "category", "inStock", "inventoryStatus"]
    for k in required_keys:
        assert k in item, f"Missing key {k} in trending product item"


def test_tier1_f1_suggestions_default_limits_applied(client: TestClient, db: Session):
    """Default limits are keyword_limit=6 and product_limit=4."""
    # Seed 8 keywords
    for i in range(8):
        for _ in range(3):
            post_search_event(client, f"keyword term {i}")
    # Seed 6 products
    prods = get_active_catalogue_products(db, 6)
    for p in prods:
        create_test_order(db, p.id, quantity=2)

    res = get_suggestions(client)
    assert res.status_code == 200
    data = res.json()
    assert len(data["trending_keywords"]) <= 6
    assert len(data["trending_products"]) <= 4


# --- Feature 2: Bounds Validation for Limits ---

def test_tier1_f2_suggestions_valid_bounds(client: TestClient):
    """Explicit valid query parameters are accepted with 200 OK."""
    res = get_suggestions(client, keyword_limit=3, product_limit=2)
    assert res.status_code == 200


def test_tier1_f2_suggestions_keyword_limit_upper_bound(client: TestClient):
    """keyword_limit=10 is accepted (maximum allowed)."""
    res = get_suggestions(client, keyword_limit=10)
    assert res.status_code == 200


def test_tier1_f2_suggestions_product_limit_upper_bound(client: TestClient):
    """product_limit=8 is accepted (maximum allowed)."""
    res = get_suggestions(client, product_limit=8)
    assert res.status_code == 200


def test_tier1_f2_suggestions_keyword_limit_out_of_bounds(client: TestClient):
    """keyword_limit outside [1, 10] returns 422 Unprocessable Entity."""
    res_under = get_suggestions(client, keyword_limit=0)
    assert res_under.status_code == 422
    res_over = get_suggestions(client, keyword_limit=11)
    assert res_over.status_code == 422


def test_tier1_f2_suggestions_product_limit_out_of_bounds(client: TestClient):
    """product_limit outside [1, 8] returns 422 Unprocessable Entity."""
    res_under = get_suggestions(client, product_limit=0)
    assert res_under.status_code == 422
    res_over = get_suggestions(client, product_limit=9)
    assert res_over.status_code == 422


# --- Feature 3: Zero-Data Empty Fallback ---

def test_tier1_f3_zero_data_returns_empty_lists(client: TestClient):
    """When no telemetry and no orders exist, returns empty lists."""
    res = get_suggestions(client)
    assert res.status_code == 200
    data = res.json()
    assert data["trending_keywords"] == []
    assert data["trending_products"] == []


def test_tier1_f3_zero_data_no_fabricated_keywords(client: TestClient):
    """Never fabricates fallback or default keywords when database is empty."""
    res = get_suggestions(client)
    assert res.status_code == 200
    assert len(res.json()["trending_keywords"]) == 0


def test_tier1_f3_zero_data_no_fabricated_products(client: TestClient):
    """Never fabricates fallback products when no qualified orders exist."""
    res = get_suggestions(client)
    assert res.status_code == 200
    assert len(res.json()["trending_products"]) == 0


def test_tier1_f3_zero_data_schema_valid(client: TestClient):
    """Empty response strictly matches schema contract."""
    res = get_suggestions(client)
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data.get("trending_keywords"), list)
    assert isinstance(data.get("trending_products"), list)


def test_tier1_f3_zero_data_status_is_200(client: TestClient):
    """Zero data returns HTTP 200, not 404 or 204."""
    res = get_suggestions(client)
    assert res.status_code == 200


# --- Feature 4: Telemetry Ingestion (POST /api/v1/products/search/events) ---

def test_tier1_f4_telemetry_returns_200(client: TestClient):
    """Telemetry ingestion returns HTTP 200."""
    res = post_search_event(client, "crochet rose")
    assert res.status_code == 200


def test_tier1_f4_telemetry_status_recorded(client: TestClient):
    """Telemetry response indicates recorded status."""
    res = post_search_event(client, "crochet rose")
    assert res.status_code == 200
    assert res.json() == {"status": "recorded"}


def test_tier1_f4_telemetry_accepts_standard_json(client: TestClient):
    """Telemetry endpoint accepts standard JSON query string."""
    res = post_search_event(client, "handmade bouquet")
    assert res.status_code == 200
    assert res.json().get("status") == "recorded"


def test_tier1_f4_telemetry_handles_unicode_query(client: TestClient):
    """Telemetry accepts Unicode and Hindi characters."""
    res = post_search_event(client, "गुलाब का फूल")
    assert res.status_code == 200
    assert res.json().get("status") == "recorded"


def test_tier1_f4_telemetry_public_no_auth_required(client: TestClient):
    """Telemetry endpoint is public and does not require authentication."""
    # Ensure no cookies or auth headers
    client.cookies.clear()
    res = client.post("/api/v1/products/search/events", json={"query": "public query"})
    assert res.status_code == 200


# --- Feature 5: Query Normalization ---

def test_tier1_f5_normalization_whitespace_trim(client: TestClient):
    """Leading and trailing whitespace are trimmed."""
    for _ in range(3):
        post_search_event(client, "   lavender bouquet   ")
    res = get_suggestions(client)
    assert res.status_code == 200
    terms = [k["term"] for k in res.json()["trending_keywords"]]
    assert "lavender bouquet" in terms
    assert "   lavender bouquet   " not in terms


def test_tier1_f5_normalization_lowercase(client: TestClient):
    """Uppercase queries are converted to lowercase."""
    for _ in range(3):
        post_search_event(client, "CROCHET DAISY")
    res = get_suggestions(client)
    assert res.status_code == 200
    terms = [k["term"] for k in res.json()["trending_keywords"]]
    assert "crochet daisy" in terms
    assert "CROCHET DAISY" not in terms


def test_tier1_f5_normalization_consecutive_spaces(client: TestClient):
    """Multiple consecutive internal spaces collapse into a single space."""
    for _ in range(3):
        post_search_event(client, "crochet    baby    hamper")
    res = get_suggestions(client)
    assert res.status_code == 200
    terms = [k["term"] for k in res.json()["trending_keywords"]]
    assert "crochet baby hamper" in terms


def test_tier1_f5_normalization_case_and_space_coalesce(client: TestClient):
    """Different casings and spaces coalesce to meet the 3-occurrence threshold."""
    post_search_event(client, "Crochet Orchid")
    post_search_event(client, "crochet   orchid")
    post_search_event(client, "  CROCHET ORCHID  ")
    res = get_suggestions(client)
    assert res.status_code == 200
    terms = [k["term"] for k in res.json()["trending_keywords"]]
    assert "crochet orchid" in terms


def test_tier1_f5_normalization_strips_outer_punctuation(client: TestClient):
    """Leading and trailing punctuation marks are stripped."""
    post_search_event(client, "crochet tulip!")
    post_search_event(client, "?crochet tulip")
    post_search_event(client, "crochet tulip.")
    res = get_suggestions(client)
    assert res.status_code == 200
    terms = [k["term"] for k in res.json()["trending_keywords"]]
    assert "crochet tulip" in terms


# --- Feature 6: Privacy Suppression ---

def test_tier1_f6_suppression_standard_email(client: TestClient):
    """Standard email address is suppressed from trending keywords."""
    for _ in range(5):
        post_search_event(client, "buyer@example.com")
    res = get_suggestions(client)
    assert res.status_code == 200
    terms = [k["term"] for k in res.json()["trending_keywords"]]
    assert "buyer@example.com" not in terms


def test_tier1_f6_suppression_complex_email(client: TestClient):
    """Complex email with subdomains and plus addressing is suppressed."""
    for _ in range(5):
        post_search_event(client, "first.last+tag@sub.domain.co.in")
    res = get_suggestions(client)
    assert res.status_code == 200
    terms = [k["term"] for k in res.json()["trending_keywords"]]
    assert len(terms) == 0


def test_tier1_f6_suppression_10_digit_phone(client: TestClient):
    """10-digit Indian phone number is suppressed."""
    for _ in range(5):
        post_search_event(client, "9876543210")
    res = get_suggestions(client)
    assert res.status_code == 200
    terms = [k["term"] for k in res.json()["trending_keywords"]]
    assert "9876543210" not in terms


def test_tier1_f6_suppression_formatted_phone(client: TestClient):
    """Formatted phone number with country code is suppressed."""
    for _ in range(5):
        post_search_event(client, "+91-98765-43210")
    res = get_suggestions(client)
    assert res.status_code == 200
    terms = [k["term"] for k in res.json()["trending_keywords"]]
    assert len(terms) == 0


def test_tier1_f6_suppression_excessive_length(client: TestClient):
    """Queries longer than 80 characters are suppressed."""
    long_query = "crochet flowers " * 6  # > 90 characters
    for _ in range(5):
        post_search_event(client, long_query)
    res = get_suggestions(client)
    assert res.status_code == 200
    terms = [k["term"] for k in res.json()["trending_keywords"]]
    assert len(terms) == 0


# --- Feature 7: Keyword Threshold Gating ---

def test_tier1_f7_gating_single_query_not_surfaced(client: TestClient):
    """Single query occurrence is not surfaced (threshold >= 3)."""
    post_search_event(client, "single rare search")
    res = get_suggestions(client)
    assert res.status_code == 200
    terms = [k["term"] for k in res.json()["trending_keywords"]]
    assert "single rare search" not in terms


def test_tier1_f7_gating_two_queries_not_surfaced(client: TestClient):
    """Two query occurrences are not surfaced (threshold >= 3)."""
    post_search_event(client, "double search term")
    post_search_event(client, "double search term")
    res = get_suggestions(client)
    assert res.status_code == 200
    terms = [k["term"] for k in res.json()["trending_keywords"]]
    assert "double search term" not in terms


def test_tier1_f7_gating_three_queries_surfaced(client: TestClient):
    """Three query occurrences cross the threshold and surface in suggestions."""
    for _ in range(3):
        post_search_event(client, "trending triple term")
    res = get_suggestions(client)
    assert res.status_code == 200
    terms = [k["term"] for k in res.json()["trending_keywords"]]
    assert "trending triple term" in terms


def test_tier1_f7_gating_multiple_terms_above_threshold(client: TestClient):
    """Only terms meeting threshold appear; sub-threshold terms do not."""
    for _ in range(4):
        post_search_event(client, "qualifying term a")
    for _ in range(3):
        post_search_event(client, "qualifying term b")
    for _ in range(2):
        post_search_event(client, "sub threshold term")

    res = get_suggestions(client)
    assert res.status_code == 200
    terms = [k["term"] for k in res.json()["trending_keywords"]]
    assert "qualifying term a" in terms
    assert "qualifying term b" in terms
    assert "sub threshold term" not in terms


def test_tier1_f7_gating_frequency_descending_order(client: TestClient):
    """Trending keywords are sorted in descending order of frequency."""
    for _ in range(3):
        post_search_event(client, "third place")
    for _ in range(10):
        post_search_event(client, "first place")
    for _ in range(6):
        post_search_event(client, "second place")

    res = get_suggestions(client)
    assert res.status_code == 200
    terms = [k["term"] for k in res.json()["trending_keywords"]]
    assert terms[:3] == ["first place", "second place", "third place"]


# --- Feature 8: Order-Backed Trending Product Ranking ---

def test_tier1_f8_order_volume_determines_rank(client: TestClient, db: Session):
    """Products with higher sales volume rank ahead of lower volume."""
    prods = get_active_catalogue_products(db, 2)
    p_high, p_low = prods[0], prods[1]
    create_test_order(db, p_high.id, quantity=10)
    create_test_order(db, p_low.id, quantity=2)

    res = get_suggestions(client)
    assert res.status_code == 200
    products = res.json()["trending_products"]
    assert len(products) >= 2
    assert products[0]["id"] == p_high.id
    assert products[1]["id"] == p_low.id


def test_tier1_f8_multi_order_volume_aggregated(client: TestClient, db: Session):
    """Product volume is aggregated across multiple distinct orders."""
    prods = get_active_catalogue_products(db, 2)
    p_multi, p_single = prods[0], prods[1]
    # p_multi has 3 orders of 3 units = 9 total
    for _ in range(3):
        create_test_order(db, p_multi.id, quantity=3)
    # p_single has 1 order of 5 units = 5 total
    create_test_order(db, p_single.id, quantity=5)

    res = get_suggestions(client)
    assert res.status_code == 200
    products = res.json()["trending_products"]
    assert products[0]["id"] == p_multi.id
    assert products[1]["id"] == p_single.id


def test_tier1_f8_rolling_30_days_included(client: TestClient, db: Session):
    """Orders within rolling 30 days contribute to trending count."""
    prods = get_active_catalogue_products(db, 1)
    create_test_order(db, prods[0].id, quantity=5, days_ago=15)

    res = get_suggestions(client)
    assert res.status_code == 200
    products = res.json()["trending_products"]
    assert len(products) >= 1
    assert products[0]["id"] == prods[0].id


def test_tier1_f8_older_than_30_days_excluded(client: TestClient, db: Session):
    """Orders older than 30 days (e.g. 35 days ago) are excluded."""
    prods = get_active_catalogue_products(db, 1)
    create_test_order(db, prods[0].id, quantity=10, days_ago=35)

    res = get_suggestions(client)
    assert res.status_code == 200
    assert res.json()["trending_products"] == []


def test_tier1_f8_product_limit_respected(client: TestClient, db: Session):
    """product_limit restricts the maximum number of returned trending products."""
    prods = get_active_catalogue_products(db, 5)
    for p in prods:
        create_test_order(db, p.id, quantity=2)

    res = get_suggestions(client, product_limit=3)
    assert res.status_code == 200
    products = res.json()["trending_products"]
    assert len(products) == 3


# --- Feature 9: Order Exclusion Logic ---

def test_tier1_f9_cancelled_orders_excluded(client: TestClient, db: Session):
    """Cancelled orders do not contribute to trending counts."""
    prods = get_active_catalogue_products(db, 1)
    create_test_order(db, prods[0].id, quantity=10, status=OrderStatus.CANCELLED.value)

    res = get_suggestions(client)
    assert res.status_code == 200
    assert res.json()["trending_products"] == []


def test_tier1_f9_refunded_orders_excluded(client: TestClient, db: Session):
    """Refunded orders do not contribute to trending counts."""
    prods = get_active_catalogue_products(db, 1)
    create_test_order(db, prods[0].id, quantity=10, status=OrderStatus.REFUNDED.value)

    res = get_suggestions(client)
    assert res.status_code == 200
    assert res.json()["trending_products"] == []


def test_tier1_f9_failed_payment_orders_excluded(client: TestClient, db: Session):
    """Orders with failed payment do not contribute to trending counts."""
    prods = get_active_catalogue_products(db, 1)
    create_test_order(db, prods[0].id, quantity=10, payment_status=PaymentStatus.FAILED.value)

    res = get_suggestions(client)
    assert res.status_code == 200
    assert res.json()["trending_products"] == []


def test_tier1_f9_mixed_statuses_only_confirmed_counted(client: TestClient, db: Session):
    """Only confirmed/paid orders contribute to ranking in mixed status scenario."""
    prods = get_active_catalogue_products(db, 2)
    p1, p2 = prods[0], prods[1]
    # p1 has 2 confirmed + 20 cancelled = 2 effective
    create_test_order(db, p1.id, quantity=2, status=OrderStatus.CONFIRMED.value)
    create_test_order(db, p1.id, quantity=20, status=OrderStatus.CANCELLED.value)

    # p2 has 4 confirmed = 4 effective
    create_test_order(db, p2.id, quantity=4, status=OrderStatus.CONFIRMED.value)

    res = get_suggestions(client)
    assert res.status_code == 200
    products = res.json()["trending_products"]
    assert len(products) == 2
    assert products[0]["id"] == p2.id
    assert products[1]["id"] == p1.id


def test_tier1_f9_only_cancelled_yields_empty_trending(client: TestClient, db: Session):
    """If all existing orders are cancelled, trending products is empty."""
    prods = get_active_catalogue_products(db, 3)
    for p in prods:
        create_test_order(db, p.id, quantity=5, status=OrderStatus.CANCELLED.value)

    res = get_suggestions(client)
    assert res.status_code == 200
    assert res.json()["trending_products"] == []


# --- Feature 10: Product Qualification ---

def test_tier1_f10_active_products_only(client: TestClient, db: Session):
    """Inactive (DRAFT/ARCHIVED) products are excluded from trending suggestions."""
    prods = get_active_catalogue_products(db, 1)
    target = prods[0]
    create_test_order(db, target.id, quantity=5)

    try:
        target.status = "ARCHIVED"
        db.commit()

        res = get_suggestions(client)
        assert res.status_code == 200
        p_ids = [p["id"] for p in res.json()["trending_products"]]
        assert target.id not in p_ids
    finally:
        target.status = "ACTIVE"
        db.commit()


def test_tier1_f10_in_stock_products_only(client: TestClient, db: Session):
    """Out-of-stock products (all variant stocks == 0) are excluded from trending."""
    prods = get_active_catalogue_products(db, 1)
    target = prods[0]
    create_test_order(db, target.id, quantity=5)

    for v in target.variants:
        v.stock_quantity = 0
    db.commit()

    res = get_suggestions(client)
    assert res.status_code == 200
    p_ids = [p["id"] for p in res.json()["trending_products"]]
    assert target.id not in p_ids


def test_tier1_f10_product_must_have_image(client: TestClient, db: Session):
    """Products returned in trending must possess a valid image."""
    prods = get_active_catalogue_products(db, 1)
    create_test_order(db, prods[0].id, quantity=5)

    res = get_suggestions(client)
    assert res.status_code == 200
    products = res.json()["trending_products"]
    assert len(products) >= 1
    assert bool(products[0]["image"])


def test_tier1_f10_product_must_have_category(client: TestClient, db: Session):
    """Products returned in trending must have a category assigned."""
    prods = get_active_catalogue_products(db, 1)
    create_test_order(db, prods[0].id, quantity=5)

    res = get_suggestions(client)
    assert res.status_code == 200
    products = res.json()["trending_products"]
    assert len(products) >= 1
    assert bool(products[0]["category"])


def test_tier1_f10_inventory_status_in_stock(client: TestClient, db: Session):
    """All trending products returned must have inStock=True and inventoryStatus='IN_STOCK'."""
    prods = get_active_catalogue_products(db, 2)
    for p in prods:
        create_test_order(db, p.id, quantity=3)

    res = get_suggestions(client)
    assert res.status_code == 200
    products = res.json()["trending_products"]
    for p in products:
        assert p["inStock"] is True
        assert p["inventoryStatus"] == "IN_STOCK"


# --- Feature 11: Telemetry Failure Non-Interference with Search ---

def test_tier1_f11_search_works_when_no_telemetry(client: TestClient):
    """Catalogue search functions perfectly with zero recorded telemetry."""
    res = client.get("/api/v1/products/search?q=rose")
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_tier1_f11_search_works_after_malformed_telemetry(client: TestClient):
    """Catalogue search is unaffected after posting malformed telemetry payload."""
    client.post("/api/v1/products/search/events", json={"invalid_field": 123})
    res = client.get("/api/v1/products/search?q=rose")
    assert res.status_code == 200


def test_tier1_f11_search_works_after_suppressed_telemetry(client: TestClient):
    """Catalogue search is unaffected after posting suppressed telemetry."""
    client.post("/api/v1/products/search/events", json={"query": "user@example.com"})
    res = client.get("/api/v1/products/search?q=rose")
    assert res.status_code == 200


def test_tier1_f11_telemetry_missing_payload_handled(client: TestClient):
    """Empty JSON body to telemetry returns 422 but does not crash catalogue search."""
    res_telem = client.post("/api/v1/products/search/events", json={})
    assert res_telem.status_code in [200, 422]
    res_search = client.get("/api/v1/products/search?q=sunflower")
    assert res_search.status_code == 200


def test_tier1_f11_telemetry_empty_query_handled(client: TestClient):
    """Telemetry with empty string query does not crash or break catalogue search."""
    res_telem = client.post("/api/v1/products/search/events", json={"query": ""})
    assert res_telem.status_code in [200, 422]
    res_search = client.get("/api/v1/products/search?q=sunflower")
    assert res_search.status_code == 200


# =============================================================================
# TIER 2: BOUNDARY & CORNER CASES (24 tests)
# =============================================================================

def test_tier2_b1_keyword_limit_min_boundary(client: TestClient):
    """keyword_limit=1 returns at most 1 keyword."""
    for i in range(3):
        for _ in range(3):
            post_search_event(client, f"term {i}")
    res = get_suggestions(client, keyword_limit=1)
    assert res.status_code == 200
    assert len(res.json()["trending_keywords"]) <= 1


def test_tier2_b2_keyword_limit_max_boundary(client: TestClient):
    """keyword_limit=10 returns at most 10 keywords."""
    res = get_suggestions(client, keyword_limit=10)
    assert res.status_code == 200
    assert len(res.json()["trending_keywords"]) <= 10


def test_tier2_b3_keyword_limit_underflow(client: TestClient):
    """keyword_limit=0 returns 422."""
    res = get_suggestions(client, keyword_limit=0)
    assert res.status_code == 422


def test_tier2_b4_keyword_limit_overflow(client: TestClient):
    """keyword_limit=11 returns 422."""
    res = get_suggestions(client, keyword_limit=11)
    assert res.status_code == 422


def test_tier2_b5_keyword_limit_negative(client: TestClient):
    """keyword_limit=-1 returns 422."""
    res = get_suggestions(client, keyword_limit=-1)
    assert res.status_code == 422


def test_tier2_b6_keyword_limit_non_integer(client: TestClient):
    """keyword_limit='abc' returns 422."""
    res = get_suggestions(client, keyword_limit="abc")
    assert res.status_code == 422


def test_tier2_b7_product_limit_min_boundary(client: TestClient, db: Session):
    """product_limit=1 returns at most 1 product."""
    prods = get_active_catalogue_products(db, 3)
    for p in prods:
        create_test_order(db, p.id, quantity=3)
    res = get_suggestions(client, product_limit=1)
    assert res.status_code == 200
    assert len(res.json()["trending_products"]) == 1


def test_tier2_b8_product_limit_max_boundary(client: TestClient, db: Session):
    """product_limit=8 returns at most 8 products."""
    res = get_suggestions(client, product_limit=8)
    assert res.status_code == 200
    assert len(res.json()["trending_products"]) <= 8


def test_tier2_b9_product_limit_underflow(client: TestClient):
    """product_limit=0 returns 422."""
    res = get_suggestions(client, product_limit=0)
    assert res.status_code == 422


def test_tier2_b10_product_limit_overflow(client: TestClient):
    """product_limit=9 returns 422."""
    res = get_suggestions(client, product_limit=9)
    assert res.status_code == 422


def test_tier2_b11_product_limit_negative(client: TestClient):
    """product_limit=-5 returns 422."""
    res = get_suggestions(client, product_limit=-5)
    assert res.status_code == 422


def test_tier2_b12_product_limit_non_integer(client: TestClient):
    """product_limit='xyz' returns 422."""
    res = get_suggestions(client, product_limit="xyz")
    assert res.status_code == 422


def test_tier2_b13_query_length_1_ignored(client: TestClient):
    """1-character query (length < 2) is suppressed/ignored even if repeated 5 times."""
    for _ in range(5):
        post_search_event(client, "a")
    res = get_suggestions(client)
    assert res.status_code == 200
    terms = [k["term"] for k in res.json()["trending_keywords"]]
    assert "a" not in terms


def test_tier2_b14_query_length_2_exact_min(client: TestClient):
    """Exactly 2-character query is accepted and surfaces after 3 occurrences."""
    for _ in range(3):
        post_search_event(client, "om")
    res = get_suggestions(client)
    assert res.status_code == 200
    terms = [k["term"] for k in res.json()["trending_keywords"]]
    assert "om" in terms


def test_tier2_b15_query_length_80_exact_max(client: TestClient):
    """Query of exactly 80 characters is accepted and surfaces after 3 occurrences."""
    term_80 = "a" * 80
    for _ in range(3):
        post_search_event(client, term_80)
    res = get_suggestions(client)
    assert res.status_code == 200
    terms = [k["term"] for k in res.json()["trending_keywords"]]
    assert term_80 in terms


def test_tier2_b16_query_length_81_suppressed(client: TestClient):
    """Query of exactly 81 characters is suppressed and does not surface."""
    term_81 = "b" * 81
    for _ in range(3):
        post_search_event(client, term_81)
    res = get_suggestions(client)
    assert res.status_code == 200
    terms = [k["term"] for k in res.json()["trending_keywords"]]
    assert term_81 not in terms


def test_tier2_b17_query_extreme_length_10000(client: TestClient):
    """Massive query payload (10,000 characters) is handled gracefully without 500 error."""
    extreme_payload = "x" * 10000
    res = post_search_event(client, extreme_payload)
    assert res.status_code in [200, 422]


def test_tier2_b18_complex_pii_email_in_sentence(client: TestClient):
    """Query containing an email embedded inside normal words is suppressed."""
    for _ in range(5):
        post_search_event(client, "please mail info@sulocraft.com order")
    res = get_suggestions(client)
    assert res.status_code == 200
    terms = [k["term"] for k in res.json()["trending_keywords"]]
    assert len(terms) == 0


def test_tier2_b19_complex_pii_phone_with_spaces(client: TestClient):
    """Phone number formatted with spaces is suppressed."""
    for _ in range(5):
        post_search_event(client, "call +91 98765 43210 please")
    res = get_suggestions(client)
    assert res.status_code == 200
    terms = [k["term"] for k in res.json()["trending_keywords"]]
    assert len(terms) == 0


def test_tier2_b20_date_boundary_29_vs_31_days(client: TestClient, db: Session):
    """Order at 29 days 23 hours is counted; order at 30 days 1 hour is excluded."""
    prods = get_active_catalogue_products(db, 2)
    p_inside, p_outside = prods[0], prods[1]

    # Inside window (29.9 days ago)
    create_test_order(db, p_inside.id, quantity=5, days_ago=29.9)
    # Outside window (30.1 days ago)
    create_test_order(db, p_outside.id, quantity=10, days_ago=30.1)

    res = get_suggestions(client)
    assert res.status_code == 200
    products = res.json()["trending_products"]
    p_ids = [p["id"] for p in products]
    assert p_inside.id in p_ids
    assert p_outside.id not in p_ids


def test_tier2_b21_stock_boundary_zero_vs_one(client: TestClient, db: Session):
    """Product with variant stock=0 is excluded; variant stock=1 is included."""
    prods = get_active_catalogue_products(db, 2)
    p_zero, p_one = prods[0], prods[1]

    create_test_order(db, p_zero.id, quantity=5)
    create_test_order(db, p_one.id, quantity=5)

    for v in p_zero.variants:
        v.stock_quantity = 0
    for v in p_one.variants:
        v.stock_quantity = 1
    db.commit()

    res = get_suggestions(client)
    assert res.status_code == 200
    products = res.json()["trending_products"]
    p_ids = [p["id"] for p in products]
    assert p_zero.id not in p_ids
    assert p_one.id in p_ids


def test_tier2_b22_order_volume_ties_deterministic(client: TestClient, db: Session):
    """Ties in order volume return deterministically without error."""
    prods = get_active_catalogue_products(db, 2)
    p1, p2 = prods[0], prods[1]
    create_test_order(db, p1.id, quantity=4)
    create_test_order(db, p2.id, quantity=4)

    res = get_suggestions(client)
    assert res.status_code == 200
    products = res.json()["trending_products"]
    assert len(products) == 2
    p_ids = {p["id"] for p in products}
    assert p_ids == {p1.id, p2.id}


def test_tier2_b23_sql_injection_tokens_in_telemetry(client: TestClient):
    """SQL injection tokens in search telemetry are safely handled as literals."""
    sqli_term = "'; DROP TABLE products; --"
    res = post_search_event(client, sqli_term)
    assert res.status_code == 200
    # Confirm catalogue products remain intact
    search_res = client.get("/api/v1/products/search?q=rose")
    assert search_res.status_code == 200


def test_tier2_b24_html_xss_tokens_in_telemetry(client: TestClient):
    """HTML / XSS tokens in search telemetry do not corrupt endpoints."""
    xss_term = "<script>alert('xss')</script>"
    res = post_search_event(client, xss_term)
    assert res.status_code == 200
    suggestions_res = get_suggestions(client)
    assert suggestions_res.status_code == 200


# =============================================================================
# TIER 3: CROSS-FEATURE INTERACTIONS (7 tests)
# =============================================================================

def test_tier3_c1_telemetry_to_suggestions_end_to_end(client: TestClient):
    """End-to-end integration: telemetry insertion -> threshold gating -> suggestions list."""
    # 5x term -> should be #1
    for _ in range(5):
        post_search_event(client, "crochet sunflower")
    # 3x term -> should be #2
    for _ in range(3):
        post_search_event(client, "crochet rose")
    # 2x term -> sub-threshold, omitted
    for _ in range(2):
        post_search_event(client, "crochet tulip")

    res = get_suggestions(client)
    assert res.status_code == 200
    keywords = res.json()["trending_keywords"]
    assert len(keywords) == 2
    assert keywords[0]["term"] == "crochet sunflower"
    assert keywords[1]["term"] == "crochet rose"


def test_tier3_c2_orders_to_trending_products_end_to_end(client: TestClient, db: Session):
    """End-to-end integration: orders placement -> status filters -> trending products ranking."""
    prods = get_active_catalogue_products(db, 3)
    p1, p2, p3 = prods[0], prods[1], prods[2]

    # p1: 10 units confirmed
    create_test_order(db, p1.id, quantity=10, status=OrderStatus.CONFIRMED.value)
    # p2: 5 units confirmed
    create_test_order(db, p2.id, quantity=5, status=OrderStatus.CONFIRMED.value)
    # p3: 20 units cancelled (must be excluded)
    create_test_order(db, p3.id, quantity=20, status=OrderStatus.CANCELLED.value)

    res = get_suggestions(client)
    assert res.status_code == 200
    products = res.json()["trending_products"]
    assert len(products) == 2
    assert products[0]["id"] == p1.id
    assert products[1]["id"] == p2.id


def test_tier3_c3_simultaneous_trending_keywords_and_products(client: TestClient, db: Session):
    """Both trending keywords and trending products populated in a single suggestions response."""
    for _ in range(4):
        post_search_event(client, "crochet lavender")
    prods = get_active_catalogue_products(db, 1)
    create_test_order(db, prods[0].id, quantity=6)

    res = get_suggestions(client, keyword_limit=2, product_limit=2)
    assert res.status_code == 200
    data = res.json()
    assert len(data["trending_keywords"]) == 1
    assert data["trending_keywords"][0]["term"] == "crochet lavender"
    assert len(data["trending_products"]) == 1
    assert data["trending_products"][0]["id"] == prods[0].id


def test_tier3_c4_dynamic_threshold_activation(client: TestClient):
    """A term transitions from invisible to visible upon recording its 3rd event."""
    term = "dynamic term"
    post_search_event(client, term)
    post_search_event(client, term)

    res1 = get_suggestions(client)
    assert term not in [k["term"] for k in res1.json()["trending_keywords"]]

    post_search_event(client, term)

    res2 = get_suggestions(client)
    assert term in [k["term"] for k in res2.json()["trending_keywords"]]


def test_tier3_c5_out_of_stock_transition(client: TestClient, db: Session):
    """When the top-trending product sells out, it immediately drops from suggestions."""
    prods = get_active_catalogue_products(db, 2)
    top_prod, runner_up = prods[0], prods[1]
    create_test_order(db, top_prod.id, quantity=10)
    create_test_order(db, runner_up.id, quantity=5)

    # Initial state: top_prod is #1
    res1 = get_suggestions(client)
    assert res1.json()["trending_products"][0]["id"] == top_prod.id

    # Stock out top_prod
    for v in top_prod.variants:
        v.stock_quantity = 0
    db.commit()

    # Next state: top_prod is omitted, runner_up becomes #1
    res2 = get_suggestions(client)
    products = res2.json()["trending_products"]
    assert products[0]["id"] == runner_up.id
    assert top_prod.id not in [p["id"] for p in products]


def test_tier3_c6_repeated_pii_never_activates_threshold(client: TestClient):
    """Repeatedly posting sensitive queries (10x) never crosses threshold or surfaces."""
    for _ in range(10):
        post_search_event(client, "private_user@sulocraft.com")
    res = get_suggestions(client)
    assert res.status_code == 200
    assert len(res.json()["trending_keywords"]) == 0


def test_tier3_c7_order_cancellation_dynamically_removes_product(client: TestClient, db: Session):
    """Changing an order status from CONFIRMED to CANCELLED removes product from trending."""
    prods = get_active_catalogue_products(db, 1)
    target = prods[0]
    order = create_test_order(db, target.id, quantity=5, status=OrderStatus.CONFIRMED.value)

    res1 = get_suggestions(client)
    assert len(res1.json()["trending_products"]) == 1

    order.status = OrderStatus.CANCELLED.value
    db.commit()

    res2 = get_suggestions(client)
    assert len(res2.json()["trending_products"]) == 0


# =============================================================================
# TIER 4: REAL-WORLD SCENARIOS (5 tests)
# =============================================================================

def test_tier4_s1_full_search_discovery_lifecycle(client: TestClient, db: Session):
    """Scenario 1: Full Search Lifecycle.

    1. Store opens: overlay suggestions empty.
    2. Multiple customers search for 'sunflower'.
    3. Suggestion surfaces in trending searches.
    4. Clicking suggested chip searches catalogue and returns Sunflower Bouquet.
    """
    # 1. Store empty
    res_init = get_suggestions(client)
    assert res_init.json()["trending_keywords"] == []

    # 2. Customers search
    for _ in range(3):
        post_search_event(client, "sunflower")

    # 3. Suggestions now surfaces 'sunflower'
    res_sugg = get_suggestions(client)
    assert res_sugg.status_code == 200
    keywords = res_sugg.json()["trending_keywords"]
    assert len(keywords) == 1
    assert keywords[0]["term"] == "sunflower"

    # 4. Search using suggested chip
    res_search = client.get(f"/api/v1/products/search?q={keywords[0]['term']}")
    assert res_search.status_code == 200
    results = res_search.json()
    assert len(results) >= 1
    assert any("sunflower" in r["name"].lower() for r in results)


def test_tier4_s2_adversarial_telemetry_and_privacy_audit(client: TestClient):
    """Scenario 2: Adversarial Telemetry & Privacy Audit.

    An attacker attempts to inject emails, phone numbers, SQL commands, and long strings.
    Verify that 0 sensitive terms surface and only clean legitimate queries are ranked.
    """
    # Attacker payloads
    post_search_event(client, "attacker@darkweb.org")
    post_search_event(client, "attacker@darkweb.org")
    post_search_event(client, "attacker@darkweb.org")

    post_search_event(client, "+91-9988776655")
    post_search_event(client, "+91-9988776655")
    post_search_event(client, "+91-9988776655")

    long_junk = "malicious " * 15
    for _ in range(3):
        post_search_event(client, long_junk)

    # Legitimate customer queries
    for _ in range(3):
        post_search_event(client, "crochet potli bag")

    res = get_suggestions(client)
    assert res.status_code == 200
    keywords = res.json()["trending_keywords"]
    assert len(keywords) == 1
    assert keywords[0]["term"] == "crochet potli bag"


def test_tier4_s3_festive_promotional_sales_wave(client: TestClient, db: Session):
    """Scenario 3: Festive Promotional Sales Wave.

    High order volume across multiple products with varied fulfillment statuses:
    - Product A: 8 units across 3 confirmed orders (volume 8)
    - Product B: 5 units across 1 delivered order (volume 5)
    - Product C: 20 units in cancelled order (volume 0)
    - Product D: 10 units in refunded order (volume 0)
    - Product E: 2 units in confirmed order (volume 2)
    Result: Trending products must strictly rank A -> B -> E.
    """
    prods = get_active_catalogue_products(db, 5)
    p_a, p_b, p_c, p_d, p_e = prods[0], prods[1], prods[2], prods[3], prods[4]

    # Product A: 8 units confirmed
    create_test_order(db, p_a.id, quantity=3, status=OrderStatus.CONFIRMED.value)
    create_test_order(db, p_a.id, quantity=3, status=OrderStatus.CONFIRMED.value)
    create_test_order(db, p_a.id, quantity=2, status=OrderStatus.CONFIRMED.value)

    # Product B: 5 units delivered
    create_test_order(db, p_b.id, quantity=5, status=OrderStatus.DELIVERED.value)

    # Product C: 20 units cancelled
    create_test_order(db, p_c.id, quantity=20, status=OrderStatus.CANCELLED.value)

    # Product D: 10 units refunded
    create_test_order(db, p_d.id, quantity=10, status=OrderStatus.REFUNDED.value)

    # Product E: 2 units confirmed
    create_test_order(db, p_e.id, quantity=2, status=OrderStatus.CONFIRMED.value)

    res = get_suggestions(client)
    assert res.status_code == 200
    trending = res.json()["trending_products"]
    assert len(trending) == 3
    assert trending[0]["id"] == p_a.id
    assert trending[1]["id"] == p_b.id
    assert trending[2]["id"] == p_e.id


def test_tier4_s4_flash_sale_stock_depletion(client: TestClient, db: Session):
    """Scenario 4: Flash Sale Stock Depletion.

    Two high-demand products: Product A (#1) and Product B (#2).
    Product A inventory depletes to 0 during checkout rush.
    Suggestions endpoint immediately drops Product A and elevates Product B to #1.
    """
    prods = get_active_catalogue_products(db, 2)
    p_a, p_b = prods[0], prods[1]

    create_test_order(db, p_a.id, quantity=15)
    create_test_order(db, p_b.id, quantity=10)

    res1 = get_suggestions(client)
    assert res1.json()["trending_products"][0]["id"] == p_a.id

    # Stock depletion
    for v in p_a.variants:
        v.stock_quantity = 0
    db.commit()

    res2 = get_suggestions(client)
    trending2 = res2.json()["trending_products"]
    assert trending2[0]["id"] == p_b.id
    assert p_a.id not in [p["id"] for p in trending2]


def test_tier4_s5_store_launch_day_zero_state(client: TestClient):
    """Scenario 5: Day-1 Launch Zero State.

    Freshly launched store with full catalogue but zero orders and zero searches.
    Verifies clean empty lists, no hardcoded fallbacks, and catalogue search works normally.
    """
    res_sugg = get_suggestions(client)
    assert res_sugg.status_code == 200
    data = res_sugg.json()
    assert data["trending_keywords"] == []
    assert data["trending_products"] == []

    # Catalogue search still functions for customers
    res_search = client.get("/api/v1/products/search?q=rose")
    assert res_search.status_code == 200
    assert len(res_search.json()) >= 1
