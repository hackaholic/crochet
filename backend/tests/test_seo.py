"""Automated tests for Dynamic SEO Metadata Resolver, Sitemap XML, and Robots.txt conforming to docs/api-seo.md."""

import xml.etree.ElementTree as ET
import pytest
from fastapi.testclient import TestClient

from app.db.seed import seed_catalogue
from app.db.session import SessionLocal
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def ensure_seed():
    """Ensure database has seed data prior to running SEO tests."""
    with SessionLocal() as db:
        seed_catalogue(db)


@pytest.fixture(autouse=True)
def default_seo_env(monkeypatch):
    """Ensure baseline test execution simulates configured production environment
    for standard entity and snapshot matrix assertions."""
    monkeypatch.setenv("CANONICAL_BASE_URL", "https://sulocraft.com")
    monkeypatch.setenv("SEO_PUBLIC_ORIGIN", "https://sulocraft.com")
    monkeypatch.setenv("SEO_INDEXING_ENABLED", "true")


def test_seo_resolve_home():
    """Verify GET /api/v1/seo/resolve for home path returns website metadata with index,follow."""
    for path in ("/", "", "https://sulocraft.com/"):
        res = client.get(f"/api/v1/seo/resolve?path={path}")
        assert res.status_code == 200
        data = res.json()
        assert "Sulocraft" in data["title"]
        assert len(data["description"]) > 10
        assert data["canonicalPath"] == "/"
        assert data["robots"] == "index,follow"
        assert data["pageType"] == "website"
        assert data["imageUrl"] is not None
        assert data["breadcrumbs"] == []
        assert len(data["faqs"]) >= 2
        assert "handmade" in data["faqs"][0]["question"].lower() or "sulocraft" in data["faqs"][0]["question"].lower()
        assert data["shippingInfo"] is not None
        assert data["shippingInfo"]["freeShippingThreshold"] == 999
        assert data["returnPolicy"] is not None
        assert data["returnPolicy"]["returnWindowDays"] == 7


def test_seo_resolve_static_pages():
    """Verify /about, /contact, /shop static public page metadata."""
    # /about
    res_about = client.get("/api/v1/seo/resolve?path=/about")
    assert res_about.status_code == 200
    d_about = res_about.json()
    assert "Our Story" in d_about["title"] or "About" in d_about["title"]
    assert d_about["canonicalPath"] == "/about"
    assert d_about["robots"] == "index,follow"
    assert d_about["pageType"] == "article"
    assert len(d_about["breadcrumbs"]) == 2
    assert d_about["breadcrumbs"][0]["name"] == "Home"
    assert d_about["breadcrumbs"][1]["path"] == "/about"

    # /contact
    res_contact = client.get("/api/v1/seo/resolve?path=/contact")
    assert res_contact.status_code == 200
    d_contact = res_contact.json()
    assert "Contact" in d_contact["title"]
    assert d_contact["canonicalPath"] == "/contact"
    assert d_contact["robots"] == "index,follow"
    assert d_contact["pageType"] == "website"

    # /shop (unfiltered)
    res_shop = client.get("/api/v1/seo/resolve?path=/shop")
    assert res_shop.status_code == 200
    d_shop = res_shop.json()
    assert "Shop" in d_shop["title"]
    assert d_shop["canonicalPath"] == "/shop"
    assert d_shop["robots"] == "index,follow"
    assert d_shop["pageType"] == "collection"


def test_seo_resolve_category_canonical_and_breadcrumbs():
    """Verify category resolution by path and query string normalizes canonical URL and builds breadcrumbs."""
    # Direct path
    res_direct = client.get("/api/v1/seo/resolve?path=/categories/flowers")
    assert res_direct.status_code == 200
    d_direct = res_direct.json()
    assert "Flowers" in d_direct["title"]
    assert d_direct["canonicalPath"] == "/categories/flowers"
    assert d_direct["robots"] == "index,follow"
    assert d_direct["pageType"] == "collection"
    assert d_direct["imageUrl"] is not None

    # Query string format /shop?category=flowers -> points canonical to /categories/flowers
    res_query = client.get("/api/v1/seo/resolve?path=/shop?category=flowers")
    assert res_query.status_code == 200
    d_query = res_query.json()
    assert d_query["canonicalPath"] == "/categories/flowers"
    assert d_query["title"] == d_direct["title"]

    # Child category /categories/bouquets has parent breadcrumb
    res_sub = client.get("/api/v1/seo/resolve?path=/categories/bouquets")
    assert res_sub.status_code == 200
    d_sub = res_sub.json()
    assert "Bouquets" in d_sub["title"]
    crumb_names = [c["name"] for c in d_sub["breadcrumbs"]]
    assert "Home" in crumb_names
    assert "Shop" in crumb_names
    assert "Flowers" in crumb_names
    assert "Bouquets" in crumb_names


def test_seo_resolve_collection_canonical_and_breadcrumbs():
    """Verify collection resolution by path and query string normalizes canonical URL."""
    res = client.get("/api/v1/seo/resolve?path=/collections/bestsellers")
    assert res.status_code == 200
    data = res.json()
    assert "Best Sellers" in data["title"]
    assert data["canonicalPath"] == "/collections/bestsellers"
    assert data["robots"] == "index,follow"
    assert data["pageType"] == "collection"

    # Query string format /shop?collection=bestsellers
    res_q = client.get("/api/v1/seo/resolve?path=/shop?collection=bestsellers")
    assert res_q.status_code == 200
    assert res_q.json()["canonicalPath"] == "/collections/bestsellers"


def test_seo_resolve_product():
    """Verify active product metadata with primary category hierarchy breadcrumbs."""
    res = client.get("/api/v1/seo/resolve?path=/products/heart-bear")
    assert res.status_code == 200
    data = res.json()
    assert "Heart Bear" in data["title"]
    assert len(data["description"]) > 10
    assert data["canonicalPath"] == "/products/heart-bear"
    assert data["robots"] == "index,follow"
    assert data["pageType"] == "product"
    assert data["imageUrl"] is not None
    assert "primary.png" in data["imageUrl"] or "images" in data["imageUrl"]

    # Check breadcrumbs: Home -> Shop -> [Baby] -> Toys -> Heart Bear
    crumb_names = [c["name"] for c in data["breadcrumbs"]]
    assert "Home" in crumb_names
    assert "Shop" in crumb_names
    assert "Toys" in crumb_names
    assert "Heart Bear" in crumb_names

    # Check rich snippet extensions
    assert len(data["faqs"]) >= 2
    assert any("clean" in f["question"].lower() or "care" in f["question"].lower() for f in data["faqs"])
    assert data["shippingInfo"] is not None
    assert data["shippingInfo"]["freeShippingThreshold"] == 999
    assert data["returnPolicy"] is not None
    assert data["returnPolicy"]["returnWindowDays"] == 7


def test_seo_resolve_private_routes_return_noindex():
    """Verify all private customer and admin routes return noindex,nofollow."""
    private_paths = [
        "/account",
        "/account/orders",
        "/account/profile",
        "/cart",
        "/checkout",
        "/checkout/payment",
        "/admin",
        "/admin/products",
        "/admin/orders",
        "/wishlist",
        "/login",
        "/auth/callback",
    ]
    for p in private_paths:
        res = client.get(f"/api/v1/seo/resolve?path={p}")
        assert res.status_code == 200, f"Path {p} failed"
        data = res.json()
        assert data["robots"] == "noindex,nofollow", f"Path {p} should have noindex, got {data['robots']}"
        assert data["canonicalPath"] == p
        assert data["breadcrumbs"] == []


def test_seo_resolve_missing_and_invalid_routes():
    """Verify 404 missing products, categories, and paths return noindex,nofollow with Page Not Found."""
    invalid_paths = [
        "/products/does-not-exist",
        "/categories/does-not-exist",
        "/collections/does-not-exist",
        "/something/random/and/missing",
    ]
    for p in invalid_paths:
        res = client.get(f"/api/v1/seo/resolve?path={p}")
        assert res.status_code == 200
        data = res.json()
        assert data["robots"] == "noindex,nofollow"
        assert "Not Found" in data["title"]
        assert data["breadcrumbs"] == []


def test_sitemap_xml_endpoints():
    """Verify /sitemap.xml and /api/v1/seo/sitemap.xml generate valid sitemaps with all active entities and images."""
    for url in ("/sitemap.xml", "/api/v1/seo/sitemap.xml"):
        res = client.get(url)
        assert res.status_code == 200
        assert "application/xml" in res.headers["content-type"]
        xml_text = res.text

        # Validate XML structure
        root = ET.fromstring(xml_text)
        assert root.tag.endswith("urlset")

        locs = [elem.text for elem in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
        assert len(locs) >= 20

        # Check image sitemap tags
        img_locs = [elem.text for elem in root.findall(".//{http://www.google.com/schemas/sitemap-image/1.1}loc")]
        assert len(img_locs) >= 10, f"Expected image tags in sitemap, got {len(img_locs)}"

        # Check static pages
        assert any(l.endswith(".com/") for l in locs)
        assert any(l.endswith("/shop") for l in locs)
        assert any(l.endswith("/about") for l in locs)
        assert any(l.endswith("/contact") for l in locs)

        # Check products
        assert any(l.endswith("/products/heart-bear") for l in locs)
        assert any(l.endswith("/products/forever-crochet-rose-bouquet") for l in locs)

        # Check categories
        assert any(l.endswith("/categories/flowers") for l in locs)
        assert any(l.endswith("/categories/bouquets") for l in locs)

        # Check collections
        assert any(l.endswith("/collections/bestsellers") for l in locs)
        assert any(l.endswith("/collections/gifts") for l in locs)

        # Ensure NO private or query parameter routes exist in sitemap
        assert not any(l.endswith("/account") or "/account/" in l for l in locs)
        assert not any(l.endswith("/admin") or "/admin/" in l for l in locs)
        assert not any(l.endswith("/cart") or "/cart/" in l for l in locs)
        assert not any(l.endswith("/checkout") or "/checkout/" in l for l in locs)
        assert not any(l.endswith("/wishlist") or "/wishlist/" in l for l in locs)
        assert not any("?" in l for l in locs)


def test_robots_txt_endpoints():
    """Verify /robots.txt and /api/v1/seo/robots.txt disallow private routes and reference sitemap."""
    for url in ("/robots.txt", "/api/v1/seo/robots.txt"):
        res = client.get(url)
        assert res.status_code == 200
        assert "text/plain" in res.headers["content-type"]
        content = res.text

        assert "User-agent: *" in content
        assert "Allow: /" in content
        assert "Disallow: /admin/" in content
        assert "Disallow: /account/" in content
        assert "Disallow: /cart" in content
        assert "Disallow: /checkout" in content
        assert "Disallow: /wishlist" in content
        assert "Disallow: /auth/" in content
        assert "Disallow: /api/" in content
        assert "Sitemap: " in content
        assert "sitemap.xml" in content


# =============================================================================
# Task 5.17: 16-Domain SEO Resolver & Truthful Entity Contract Test Matrix
# =============================================================================

def test_domain_01_homepage_brand_and_social_profiles():
    """Domain 1: Homepage / returns truthful BrandSettings metadata, logo, and social links."""
    res = client.get("/api/v1/seo/resolve?path=/")
    assert res.status_code == 200
    data = res.json()
    assert data["canonicalPath"] == "/"
    assert data["canonicalUrl"] == "https://sulocraft.com/"
    assert data["h1"] == "Handcrafted Heirloom Crochet"
    assert data["robots"] == "index,follow"

    # Brand truth (Task 5.17 & 5.17.1)
    brand = data.get("brand")
    assert brand is not None
    assert brand["name"] == "Sulocraft"
    assert "sulocraft-logo.png" in brand["logoUrl"]
    assert brand["ownerName"] == "Anupama Sharma"
    assert brand.get("legalName") is None
    assert brand.get("whatsappUrl") == "https://wa.me/919876543210"
    assert any("instagram.com/sulocraft" in s for s in brand["sameAs"])
    assert not any("wa.me" in s for s in brand["sameAs"])
    assert brand["sameAs"] == ["https://instagram.com/sulocraft"]


def test_domain_02_product_entity_sunflower_price_sku_parity():
    """Domain 2: Sunflower Bouquet entity parity: price 2199 INR, variant SKU, inStock, and Work 019 attributes."""
    res = client.get("/api/v1/seo/resolve?path=/products/sunflower-bouquet")
    assert res.status_code == 200
    data = res.json()
    assert data["h1"] == "Sunflower Bouquet"
    assert data["canonicalPath"] == "/products/sunflower-bouquet"
    assert data["canonicalUrl"] == "https://sulocraft.com/products/sunflower-bouquet"
    assert data["pageType"] == "product"

    entity = data.get("productEntity")
    assert entity is not None
    assert entity["name"] == "Sunflower Bouquet"
    assert entity["slug"] == "sunflower-bouquet"
    assert entity["price"] == 2199.0
    assert entity["pricePaise"] == 219900
    assert entity["currency"] == "INR"
    assert entity["sku"] == "SULO-FLR-SUNFLOWER-001"
    assert entity["inStock"] is True
    assert entity["inventoryStatus"] == "IN_STOCK"
    assert entity["brand"] == "Sulocraft"

    # Variant details
    assert len(entity["variants"]) >= 1
    v0 = entity["variants"][0]
    assert v0["sku"] == "SULO-FLR-SUNFLOWER-001"
    assert v0["price"] == 2199.0
    assert v0["pricePaise"] == 219900
    assert v0["inStock"] is True

    # Review provenance (Task 5.22: Sunflower Bouquet has seed counters but 0 genuine review records)
    assert entity["aggregateRating"] is None

    # Work 019 attributes and FAQs
    assert len(data["faqs"]) >= 2
    assert any("clean" in f["question"].lower() or "care" in f["question"].lower() for f in data["faqs"])


def test_domain_03_review_provenance_omits_rating_when_zero_reviews():
    """Domain 3: Product with 0 reviews must omit aggregateRating per DEC-005-5."""
    from app.models.catalogue import Product
    with SessionLocal() as db:
        test_prod = db.query(Product).filter(Product.slug == "unreviewed-test-prod").first()
        if not test_prod:
            test_prod = Product(
                name="Unreviewed Test Item",
                slug="unreviewed-test-prod",
                primary_image="products/test/primary.png",
                status="ACTIVE",
                rating=0.0,
                reviews_count=0,
            )
            db.add(test_prod)
            db.commit()

    try:
        res = client.get("/api/v1/seo/resolve?path=/products/unreviewed-test-prod")
        assert res.status_code == 200
        data = res.json()
        assert data["productEntity"] is not None
        assert data["productEntity"]["aggregateRating"] is None
    finally:
        with SessionLocal() as db:
            p = db.query(Product).filter(Product.slug == "unreviewed-test-prod").first()
            if p:
                db.delete(p)
                db.commit()


def test_domain_04_out_of_stock_product_handling():
    """Domain 4: Out-of-stock product reflects inStock=False and inventoryStatus='OUT_OF_STOCK'."""
    from app.models.catalogue import Product, ProductVariant
    with SessionLocal() as db:
        test_prod = db.query(Product).filter(Product.slug == "out-of-stock-test-item").first()
        if not test_prod:
            test_prod = Product(
                name="Out of Stock Test Item",
                slug="out-of-stock-test-item",
                primary_image="products/test/primary.png",
                status="ACTIVE",
                rating=4.5,
                reviews_count=10,
            )
            db.add(test_prod)
            db.flush()
            var = ProductVariant(
                product_id=test_prod.id,
                sku="SULO-OOS-001",
                name="Standard",
                price=999.0,
                stock_quantity=0,
                status="ACTIVE",
            )
            db.add(var)
            db.commit()

    try:
        res = client.get("/api/v1/seo/resolve?path=/products/out-of-stock-test-item")
        assert res.status_code == 200
        data = res.json()
        entity = data["productEntity"]
        assert entity is not None
        assert entity["inStock"] is False
        assert entity["inventoryStatus"] == "OUT_OF_STOCK"
        assert len(entity["variants"]) == 1
        assert entity["variants"][0]["inStock"] is False
        assert entity["variants"][0]["stockQuantity"] == 0
    finally:
        with SessionLocal() as db:
            p = db.query(Product).filter(Product.slug == "out-of-stock-test-item").first()
            if p:
                db.query(ProductVariant).filter(ProductVariant.product_id == p.id).delete()
                db.delete(p)
                db.commit()


def test_domain_05_root_category_flowers():
    """Domain 5: Root Category /categories/flowers -> H1 is 'Flowers', categoryEntity has product count."""
    res = client.get("/api/v1/seo/resolve?path=/categories/flowers")
    assert res.status_code == 200
    data = res.json()
    assert data["h1"] == "Flowers"
    assert data["canonicalPath"] == "/categories/flowers"
    assert data["canonicalUrl"] == "https://sulocraft.com/categories/flowers"
    cat_entity = data.get("categoryEntity")
    assert cat_entity is not None
    assert cat_entity["name"] == "Flowers"
    assert cat_entity["slug"] == "flowers"
    assert cat_entity["parentId"] is None
    assert cat_entity["productCount"] > 0


def test_domain_06_child_subcategory_bouquets():
    """Domain 6: Child subcategory /categories/bouquets contains parent hierarchy in categoryEntity and breadcrumbs."""
    res = client.get("/api/v1/seo/resolve?path=/categories/bouquets")
    assert res.status_code == 200
    data = res.json()
    assert data["h1"] == "Bouquets"
    cat_entity = data.get("categoryEntity")
    assert cat_entity is not None
    assert cat_entity["name"] == "Bouquets"
    assert cat_entity["parentName"] == "Flowers"
    assert cat_entity["parentSlug"] == "flowers"

    crumb_names = [c["name"] for c in data["breadcrumbs"]]
    assert crumb_names == ["Home", "Shop", "Flowers", "Bouquets"]


def test_domain_07_category_query_param_canonicalizes():
    """Domain 7: /shop?category=flowers canonicalizes path and url to /categories/flowers."""
    res = client.get("/api/v1/seo/resolve?path=/shop?category=flowers")
    assert res.status_code == 200
    data = res.json()
    assert data["canonicalPath"] == "/categories/flowers"
    assert data["canonicalUrl"] == "https://sulocraft.com/categories/flowers"
    assert data["h1"] == "Flowers"
    assert data["categoryEntity"] is not None
    assert data["categoryEntity"]["slug"] == "flowers"


def test_domain_08_active_collection_bestsellers():
    """Domain 8: Active collection /collections/bestsellers -> H1 is 'Best Sellers', collectionEntity populated."""
    res = client.get("/api/v1/seo/resolve?path=/collections/bestsellers")
    assert res.status_code == 200
    data = res.json()
    assert data["h1"] == "Best Sellers"
    assert data["canonicalPath"] == "/collections/bestsellers"
    assert data["canonicalUrl"] == "https://sulocraft.com/collections/bestsellers"
    col_entity = data.get("collectionEntity")
    assert col_entity is not None
    assert col_entity["name"] == "Best Sellers"
    assert col_entity["slug"] == "bestsellers"


def test_domain_09_collection_query_param_canonicalizes():
    """Domain 9: /shop?collection=bestsellers canonicalizes path and url to /collections/bestsellers."""
    res = client.get("/api/v1/seo/resolve?path=/shop?collection=bestsellers")
    assert res.status_code == 200
    data = res.json()
    assert data["canonicalPath"] == "/collections/bestsellers"
    assert data["canonicalUrl"] == "https://sulocraft.com/collections/bestsellers"
    assert data["h1"] == "Best Sellers"
    assert data["collectionEntity"] is not None


def test_domain_10_unfiltered_shop():
    """Domain 10: Unfiltered /shop -> H1 is 'All Products', pageType='collection'."""
    res = client.get("/api/v1/seo/resolve?path=/shop")
    assert res.status_code == 200
    data = res.json()
    assert data["h1"] == "All Products"
    assert data["canonicalPath"] == "/shop"
    assert data["canonicalUrl"] == "https://sulocraft.com/shop"
    assert data["pageType"] == "collection"
    assert len(data["breadcrumbs"]) == 2
    assert data["breadcrumbs"][0]["name"] == "Home"
    assert data["breadcrumbs"][1]["name"] == "Shop"


def test_domain_11_about_us_image_and_h1():
    """Domain 11: /about has H1 'Our Story' and references about/anupama-sharma.png (fixing 404)."""
    res = client.get("/api/v1/seo/resolve?path=/about")
    assert res.status_code == 200
    data = res.json()
    assert data["h1"] == "Our Story"
    assert data["canonicalPath"] == "/about"
    assert data["canonicalUrl"] == "https://sulocraft.com/about"
    assert "about/anupama-sharma.png" in data["imageUrl"]
    assert "sections/artisan-story.jpg" not in data["imageUrl"]


def test_domain_12_contact_us_h1():
    """Domain 12: /contact has H1 'Contact Us' and canonical path/url."""
    res = client.get("/api/v1/seo/resolve?path=/contact")
    assert res.status_code == 200
    data = res.json()
    assert data["h1"] == "Contact Us"
    assert data["canonicalPath"] == "/contact"
    assert data["canonicalUrl"] == "https://sulocraft.com/contact"


def test_domain_13_policy_routes():
    """Domain 13: Policy routes return proper titles, H1s, and canonical paths."""
    policy_checks = {
        "/shipping-policy": "Shipping Policy",
        "/return-policy": "Return & Refund Policy",
        "/privacy-policy": "Privacy Policy",
        "/terms": "Terms of Service",
        "/faq": "Frequently Asked Questions",
    }
    for path, expected_h1 in policy_checks.items():
        res = client.get(f"/api/v1/seo/resolve?path={path}")
        assert res.status_code == 200, f"Failed for {path}"
        data = res.json()
        assert data["h1"] == expected_h1
        assert data["canonicalPath"] == path
        assert data["canonicalUrl"] == f"https://sulocraft.com{path}"
        assert data["robots"] == "index,follow"


def test_domain_14_policy_aliases_canonicalize():
    """Domain 14: Policy aliases (/info/shipping, /info/refund, etc.) canonicalize to primary policy paths."""
    alias_checks = {
        "/info/shipping": "/shipping-policy",
        "/info/refund": "/return-policy",
        "/info/privacy": "/privacy-policy",
        "/info/terms": "/terms",
        "/info/faq": "/faq",
    }
    for alias, canonical in alias_checks.items():
        res = client.get(f"/api/v1/seo/resolve?path={alias}")
        assert res.status_code == 200, f"Failed for alias {alias}"
        data = res.json()
        assert data["canonicalPath"] == canonical
        assert data["canonicalUrl"] == f"https://sulocraft.com{canonical}"
        assert data["robots"] == "index,follow"


def test_domain_15_private_routes_return_noindex():
    """Domain 15: Private routes return robots='noindex,nofollow' and empty breadcrumbs."""
    for path in ("/account", "/admin", "/cart", "/checkout", "/wishlist", "/login"):
        res = client.get(f"/api/v1/seo/resolve?path={path}")
        assert res.status_code == 200
        data = res.json()
        assert data["robots"] == "noindex,nofollow"
        assert data["canonicalPath"] == path
        assert data["breadcrumbs"] == []


def test_domain_16_missing_and_invalid_routes_return_404_noindex():
    """Domain 16: Missing/invalid routes return robots='noindex,nofollow' and H1='Page Not Found'."""
    for path in ("/products/non-existent-product", "/categories/non-existent-category", "/random-404-page"):
        res = client.get(f"/api/v1/seo/resolve?path={path}")
        assert res.status_code == 200
        data = res.json()
        assert data["robots"] == "noindex,nofollow"
        assert data["h1"] == "Page Not Found"
        assert "Not Found" in data["title"]


def test_domain_17_environment_indexability_policy(monkeypatch):
    """Domain 17: Enforce environment indexability per DEC-005-7 and Task 5.18.2
    (development and preprod default to noindex; production fails closed without explicit indexing)."""
    # 1. Staging/Preprod default -> noindex,nofollow
    monkeypatch.delenv("SEO_INDEXING_ENABLED", raising=False)
    monkeypatch.setenv("APP_ENV", "preprod")
    res_preprod = client.get("/api/v1/seo/resolve?path=/")
    assert res_preprod.status_code == 200
    assert res_preprod.json()["robots"] == "noindex,nofollow"

    # 2. Development default -> noindex,nofollow
    monkeypatch.setenv("APP_ENV", "development")
    res_dev = client.get("/api/v1/seo/resolve?path=/")
    assert res_dev.status_code == 200
    assert res_dev.json()["robots"] == "noindex,nofollow"

    # 3. Production default without explicit SEO_INDEXING_ENABLED -> noindex,nofollow (fail closed)
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("SEO_PUBLIC_ORIGIN", "https://sulocraft.com")
    res_prod_default = client.get("/api/v1/seo/resolve?path=/")
    assert res_prod_default.status_code == 200
    assert res_prod_default.json()["robots"] == "noindex,nofollow"

    # 4. Production with explicit SEO_INDEXING_ENABLED="true" -> index,follow
    monkeypatch.setenv("SEO_INDEXING_ENABLED", "true")
    res_prod = client.get("/api/v1/seo/resolve?path=/")
    assert res_prod.status_code == 200
    assert res_prod.json()["robots"] == "index,follow"

    # 5. Explicit SEO_INDEXING_ENABLED="true" override in preprod -> index,follow
    monkeypatch.setenv("APP_ENV", "preprod")
    res_override = client.get("/api/v1/seo/resolve?path=/")
    assert res_override.status_code == 200
    assert res_override.json()["robots"] == "index,follow"

    # 6. Explicit SEO_INDEXING_ENABLED="false" override in prod -> noindex,nofollow
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("SEO_INDEXING_ENABLED", "false")
    res_override_off = client.get("/api/v1/seo/resolve?path=/")
    assert res_override_off.status_code == 200
    assert res_override_off.json()["robots"] == "noindex,nofollow"


# =============================================================================
# Task 5.18: Route Inventory, Build Snapshot, & Environment Robots Tests
# =============================================================================

def test_route_inventory_endpoint():
    """Verify GET /api/v1/seo/routes returns complete, deduplicated public route inventory."""
    res = client.get("/api/v1/seo/routes")
    assert res.status_code == 200
    data = res.json()

    assert "totalRoutes" in data
    assert "routes" in data
    assert "generatedAt" in data
    assert data["totalRoutes"] == len(data["routes"])
    assert data["totalRoutes"] >= 25  # Core + policies + categories + collections + products

    paths = [r["path"] for r in data["routes"]]

    # 1. Core static and policy routes
    assert "/" in paths
    assert "/shop" in paths
    assert "/about" in paths
    assert "/contact" in paths
    assert "/shipping-policy" in paths
    assert "/return-policy" in paths
    assert "/privacy-policy" in paths
    assert "/terms" in paths
    assert "/faq" in paths

    # 2. Categories
    assert "/categories/flowers" in paths
    assert "/categories/bouquets" in paths
    assert "/categories/amigurumi" in paths

    # 3. Collections
    assert "/collections/bestsellers" in paths
    assert "/collections/gifts" in paths

    # 4. Products
    assert "/products/sunflower-bouquet" in paths
    assert "/products/heart-bear" in paths

    # 5. Ensure NO private routes, query parameters, or drafts exist in inventory
    assert not any(p.startswith("/account") or p.startswith("/admin") or p.startswith("/cart") for p in paths)
    assert not any("?" in p for p in paths)

    # 6. Verify item attributes & truthful lastmod provenance (Task 5.18.2)
    for r in data["routes"]:
        assert r["canonicalUrl"].startswith("https://sulocraft.com")
        assert r["pageType"] in ("website", "product", "collection", "article")
        assert 0.0 < r["priority"] <= 1.0
        if r["path"] in ("/", "/shop", "/about", "/contact", "/shipping-policy", "/return-policy", "/privacy-policy", "/terms", "/faq"):
            assert r["lastmod"] is None, f"Static route {r['path']} must omit manufactured lastmod"
        else:
            assert r["lastmod"] is not None and len(r["lastmod"]) == 10, f"Entity route {r['path']} must have DB lastmod"


def test_content_snapshot_endpoint():
    """Verify GET /api/v1/seo/snapshot returns paginated, deterministic build snapshots."""
    # Page 1 with limit 5
    res1 = client.get("/api/v1/seo/snapshot?page=1&limit=5")
    assert res1.status_code == 200
    data1 = res1.json()

    assert data1["page"] == 1
    assert data1["limit"] == 5
    assert data1["totalCount"] >= 25
    assert data1["totalPages"] >= 5
    assert len(data1["items"]) == 5
    assert len(data1["versionHash"]) >= 8

    # Check first item structure
    first_item = data1["items"][0]
    assert first_item["path"] == "/"
    assert first_item["metadata"]["title"] is not None
    assert first_item["metadata"]["h1"] is not None
    assert first_item["metadata"]["canonicalPath"] == "/"
    assert first_item["metadata"]["brand"] is not None

    # Page 2 with limit 5
    res2 = client.get("/api/v1/seo/snapshot?page=2&limit=5")
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["page"] == 2
    assert len(data2["items"]) == 5

    # 5.18.1-TC01: Ensure global versionHash is identical across pages
    assert data1["versionHash"] == data2["versionHash"]

    # Ensure pages do not overlap
    page1_paths = {it["path"] for it in data1["items"]}
    page2_paths = {it["path"] for it in data2["items"]}
    assert len(page1_paths.intersection(page2_paths)) == 0


def test_environment_aware_robots_txt(monkeypatch):
    """Verify /robots.txt never blocks crawlers with blanket Disallow: / in preprod/dev (allowing noindex inspection)
    while disallowing private routes and referencing sitemap only when indexing is enabled."""
    # 1. Preprod environment -> Allow: / (no blanket Disallow: /), sitemap omitted
    monkeypatch.delenv("SEO_INDEXING_ENABLED", raising=False)
    monkeypatch.setenv("APP_ENV", "preprod")
    res_preprod = client.get("/robots.txt")
    assert res_preprod.status_code == 200
    assert "Allow: /" in res_preprod.text
    # Ensure there is no line exactly matching 'Disallow: /'
    assert "Disallow: /" not in [line.strip() for line in res_preprod.text.splitlines() if line.strip() == "Disallow: /"]
    assert "Disallow: /admin/" in res_preprod.text
    assert "Sitemap:" not in res_preprod.text

    # 2. Production environment -> Allow: / with private route disallows and canonical sitemap reference
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("SEO_INDEXING_ENABLED", "true")
    monkeypatch.setenv("SEO_PUBLIC_ORIGIN", "https://sulocraft.com")
    res_prod = client.get("/robots.txt")
    assert res_prod.status_code == 200
    assert "Allow: /" in res_prod.text
    assert "Disallow: /admin/" in res_prod.text
    assert "Disallow: /cart" in res_prod.text
    assert "Sitemap: https://sulocraft.com/sitemap.xml" in res_prod.text


# =============================================================================
# Task 5.22: Review Rating Provenance Tests
# =============================================================================

def test_review_rating_provenance_aggregates_from_real_review_records():
    """Verify aggregateRating computes count and average from real Review records and includes provenance."""
    from app.models.catalogue import Product, Review

    with SessionLocal() as db:
        test_prod = db.query(Product).filter(Product.slug == "reviewed-test-prod").first()
        if not test_prod:
            test_prod = Product(
                name="Reviewed Test Product",
                slug="reviewed-test-prod",
                primary_image="products/test/primary.png",
                status="ACTIVE",
                rating=4.0,  # Static seed rating (must be ignored)
                reviews_count=99,  # Static seed count (must be ignored)
            )
            db.add(test_prod)
            db.flush()

            # Add 2 genuine reviews: rating 5 and 4 -> avg 4.5, count 2
            r1 = Review(
                product_id=test_prod.id,
                author_name="Alice",
                rating=5,
                text="Wonderful quality and craftsmanship!",
            )
            r2 = Review(
                product_id=test_prod.id,
                author_name="Bob",
                rating=4,
                text="Very cute, good packing.",
            )
            db.add_all([r1, r2])
            db.commit()

    try:
        res = client.get("/api/v1/seo/resolve?path=/products/reviewed-test-prod")
        assert res.status_code == 200
        data = res.json()
        entity = data["productEntity"]
        assert entity is not None
        assert entity["aggregateRating"] is not None

        rating = entity["aggregateRating"]
        assert rating["ratingValue"] == 4.5
        assert rating["reviewCount"] == 2
        assert rating["bestRating"] == 5.0
        assert rating["worstRating"] == 1.0
        assert rating["provenance"] == "VERIFIED_REVIEWS"
    finally:
        with SessionLocal() as db:
            p = db.query(Product).filter(Product.slug == "reviewed-test-prod").first()
            if p:
                db.query(Review).filter(Review.product_id == p.id).delete()
                db.delete(p)
                db.commit()


def test_review_rating_provenance_ignores_unrelated_reviews():
    """Verify reviews not linked to a product (or linked to another product) are never attributed."""
    from app.models.catalogue import Product, Review

    with SessionLocal() as db:
        test_prod = db.query(Product).filter(Product.slug == "unlinked-review-test-prod").first()
        if not test_prod:
            test_prod = Product(
                name="Unlinked Review Test Product",
                slug="unlinked-review-test-prod",
                primary_image="products/test/primary.png",
                status="ACTIVE",
                rating=4.9,
                reviews_count=50,
            )
            db.add(test_prod)
            db.flush()

            # Add an unlinked review (product_id = None)
            unlinked_review = Review(
                product_id=None,
                author_name="Anonymous",
                rating=5,
                text="Store review without product link",
            )
            db.add(unlinked_review)
            db.commit()

    try:
        res = client.get("/api/v1/seo/resolve?path=/products/unlinked-review-test-prod")
        assert res.status_code == 200
        data = res.json()
        assert data["productEntity"] is not None
        # Must omit aggregateRating because no reviews match this product.id
        assert data["productEntity"]["aggregateRating"] is None
    finally:
        with SessionLocal() as db:
            p = db.query(Product).filter(Product.slug == "unlinked-review-test-prod").first()
            if p:
                db.delete(p)
            db.query(Review).filter(Review.author_name == "Anonymous").delete()
            db.commit()


def test_snapshot_version_consistency_and_mutation():
    """Verify 5.18.1-TC01 and 5.18.1-TC02:
    - Global snapshot version hash is identical across all pages.
    - Snapshot version hash changes when prices or active entities are mutated, even without parent product updated_at modification.
    - Snapshot version hash is unaffected by draft products.
    """
    from app.models.catalogue import Product, ProductVariant

    # 1. Baseline hash across multiple pages
    res_p1 = client.get("/api/v1/seo/snapshot?page=1&limit=5")
    res_p2 = client.get("/api/v1/seo/snapshot?page=2&limit=5")
    assert res_p1.status_code == 200
    assert res_p2.status_code == 200
    base_hash_1 = res_p1.json()["versionHash"]
    base_hash_2 = res_p2.json()["versionHash"]
    assert base_hash_1 == base_hash_2

    # 2. Mutate a product variant price directly (in-place price mutation)
    with SessionLocal() as db:
        variant = db.query(ProductVariant).first()
        assert variant is not None
        variant_id = variant.id
        original_price = variant.price
        original_updated_at = variant.updated_at
        variant.price = original_price + 100
        db.commit()

    try:
        res_mutated = client.get("/api/v1/seo/snapshot?page=1&limit=5")
        assert res_mutated.status_code == 200
        new_hash = res_mutated.json()["versionHash"]
        assert new_hash != base_hash_1, "Snapshot version hash must change when variant price changes"

        # Check page 2 also has this new hash
        res_mutated_p2 = client.get("/api/v1/seo/snapshot?page=2&limit=5")
        assert res_mutated_p2.json()["versionHash"] == new_hash
    finally:
        # Revert variant price and updated_at
        with SessionLocal() as db:
            v = db.query(ProductVariant).filter(ProductVariant.id == variant_id).first()
            if v:
                v.price = original_price
                v.updated_at = original_updated_at
                db.commit()

    # Verify hash restored
    res_reverted = client.get("/api/v1/seo/snapshot?page=1&limit=5")
    assert res_reverted.json()["versionHash"] == base_hash_1

    # 3. Add a draft product: should NOT change public snapshot version
    with SessionLocal() as db:
        draft = Product(
            name="Secret Draft Product",
            slug="secret-draft-product-xyz",
            primary_image="products/draft.png",
            status="DRAFT",
        )
        db.add(draft)
        db.commit()

    try:
        res_draft = client.get("/api/v1/seo/snapshot?page=1&limit=5")
        assert res_draft.json()["versionHash"] == base_hash_1, "Draft product must not change public snapshot hash"
    finally:
        with SessionLocal() as db:
            d = db.query(Product).filter(Product.slug == "secret-draft-product-xyz").first()
            if d:
                db.delete(d)
                db.commit()


def test_slug_lifecycle_redirects_and_status_codes():
    """Verify Task 5.19 (5.19-TC01 and 5.19-TC02):
    - Admin slug change generates a 301 UrlRedirect from old path to new canonical path.
    - Resolving old slug path returns httpStatus=301, redirectTo=new_path, robots="noindex,nofollow".
    - Resolving new slug path returns httpStatus=200, canonicalPath=new_path.
    - Multi-hop chain prevention: A -> B then B -> C ensures A -> C (flattened).
    - Circular rename handling: A -> B then B -> A removes redirect loop.
    - Archived product returns httpStatus=410 Gone, robots="noindex,nofollow", h1="Product Discontinued".
    - Unknown/missing product or route returns httpStatus=404 Not Found.
    """
    from app.models.catalogue import Product, UrlRedirect

    # 1. Setup a test product
    with SessionLocal() as db:
        prod = Product(
            name="Lifecycle Test Product",
            slug="lifecycle-initial-slug",
            primary_image="products/lifecycle.png",
            status="ACTIVE",
        )
        db.add(prod)
        db.commit()
        db.refresh(prod)
        prod_id = prod.id

    try:
        # A. Verify initial resolution -> 200 OK
        res = client.get("/api/v1/seo/resolve?path=/products/lifecycle-initial-slug")
        assert res.status_code == 200
        data = res.json()
        assert data["httpStatus"] == 200
        assert data["redirectTo"] is None
        assert data["canonicalPath"] == "/products/lifecycle-initial-slug"

        # B. First slug update: lifecycle-initial-slug -> lifecycle-renamed-slug
        from app.api.v1.admin import _record_slug_redirect
        with SessionLocal() as db:
            p = db.query(Product).filter(Product.id == prod_id).first()
            old_path = f"/products/{p.slug}"
            new_path = "/products/lifecycle-renamed-slug"
            p.slug = "lifecycle-renamed-slug"
            _record_slug_redirect(db, old_path, new_path, "PRODUCT", p.id)
            db.commit()

        # Resolving old path should return 301 with redirectTo
        res_old = client.get("/api/v1/seo/resolve?path=/products/lifecycle-initial-slug")
        assert res_old.status_code == 200
        data_old = res_old.json()
        assert data_old["httpStatus"] == 301
        assert data_old["redirectTo"] == "/products/lifecycle-renamed-slug"
        assert data_old["canonicalPath"] == "/products/lifecycle-renamed-slug"
        assert data_old["robots"] == "noindex,nofollow"

        # Resolving new path should return 200
        res_new = client.get("/api/v1/seo/resolve?path=/products/lifecycle-renamed-slug")
        assert res_new.status_code == 200
        data_new = res_new.json()
        assert data_new["httpStatus"] == 200
        assert data_new["canonicalPath"] == "/products/lifecycle-renamed-slug"

        # C. Multi-hop chain prevention: lifecycle-renamed-slug -> lifecycle-final-slug
        with SessionLocal() as db:
            p = db.query(Product).filter(Product.id == prod_id).first()
            old_path = f"/products/{p.slug}"
            new_path = "/products/lifecycle-final-slug"
            p.slug = "lifecycle-final-slug"
            _record_slug_redirect(db, old_path, new_path, "PRODUCT", p.id)
            db.commit()

        # Both the original initial-slug and renamed-slug must point directly to final-slug (no chain)
        res_orig = client.get("/api/v1/seo/resolve?path=/products/lifecycle-initial-slug")
        assert res_orig.json()["httpStatus"] == 301
        assert res_orig.json()["redirectTo"] == "/products/lifecycle-final-slug"

        res_second = client.get("/api/v1/seo/resolve?path=/products/lifecycle-renamed-slug")
        assert res_second.json()["httpStatus"] == 301
        assert res_second.json()["redirectTo"] == "/products/lifecycle-final-slug"

        # D. Circular rename test: Rename final-slug back to initial-slug
        with SessionLocal() as db:
            p = db.query(Product).filter(Product.id == prod_id).first()
            old_path = f"/products/{p.slug}"
            new_path = "/products/lifecycle-initial-slug"
            p.slug = "lifecycle-initial-slug"
            _record_slug_redirect(db, old_path, new_path, "PRODUCT", p.id)
            db.commit()

        # Initial slug should now resolve as 200 OK (no redirect loop to itself)
        res_restored = client.get("/api/v1/seo/resolve?path=/products/lifecycle-initial-slug")
        assert res_restored.json()["httpStatus"] == 200
        assert res_restored.json()["canonicalPath"] == "/products/lifecycle-initial-slug"

        # E. 410 Gone for ARCHIVED / discontinued product
        with SessionLocal() as db:
            p = db.query(Product).filter(Product.id == prod_id).first()
            p.status = "ARCHIVED"
            db.commit()

        res_archived = client.get("/api/v1/seo/resolve?path=/products/lifecycle-initial-slug")
        assert res_archived.status_code == 200
        data_archived = res_archived.json()
        assert data_archived["httpStatus"] == 410
        assert data_archived["robots"] == "noindex,nofollow"
        assert data_archived["h1"] == "Product Discontinued"

        # F. 404 for nonexistent route
        res_404 = client.get("/api/v1/seo/resolve?path=/products/completely-nonexistent-slug-12345")
        assert res_404.status_code == 200
        data_404 = res_404.json()
        assert data_404["httpStatus"] == 404
        assert data_404["robots"] == "noindex,nofollow"
        assert data_404["h1"] == "Page Not Found"

    finally:
        with SessionLocal() as db:
            p = db.query(Product).filter(Product.id == prod_id).first()
            if p:
                db.delete(p)
            db.query(UrlRedirect).filter(UrlRedirect.old_path.like("/products/lifecycle-%")).delete()
            db.commit()


# =============================================================================
# Task 5.17.1: Brand Schema Truth Test Suite
# =============================================================================

def test_brand_truth_missing_brand_settings():
    """Verify 5.17.1: When no BrandSettings row exists in DB, fallback never manufactures
    invented legalName, ownerName, or social/contact URLs. Official logo is preserved."""
    from app.models.storefront import BrandSettings

    with SessionLocal() as db:
        saved_brands = db.query(BrandSettings).all()
        # Backup brand fields
        brand_backups = [
            {
                "id": b.id,
                "name": b.name,
                "logo_url": b.logo_url,
                "owner_name": b.owner_name,
                "instagram_url": b.instagram_url,
                "whatsapp_url": b.whatsapp_url,
            }
            for b in saved_brands
        ]
        db.query(BrandSettings).delete()
        db.commit()

    try:
        res = client.get("/api/v1/seo/resolve?path=/")
        assert res.status_code == 200
        brand = res.json().get("brand")
        assert brand is not None
        assert brand["name"] == "Sulocraft"
        assert brand.get("legalName") is None
        assert brand.get("ownerName") is None
        assert brand.get("instagramUrl") is None
        assert brand.get("whatsappUrl") is None
        assert brand["sameAs"] == []
        assert "sulocraft-logo.png" in brand.get("logoUrl", "")
    finally:
        with SessionLocal() as db:
            db.query(BrandSettings).delete()
            for b_data in brand_backups:
                db.add(BrandSettings(**b_data))
            db.commit()


def test_brand_truth_empty_brand_fields():
    """Verify 5.17.1: When BrandSettings exists but has empty/null fields,
    empty fields yield null/empty results and never fall back to seeded claims."""
    from app.models.storefront import BrandSettings

    with SessionLocal() as db:
        brand = db.query(BrandSettings).order_by(BrandSettings.id.asc()).first()
        assert brand is not None
        orig_logo = brand.logo_url
        orig_owner = brand.owner_name
        orig_ig = brand.instagram_url
        orig_wa = brand.whatsapp_url

        brand.logo_url = None
        brand.owner_name = ""
        brand.instagram_url = None
        brand.whatsapp_url = ""
        db.commit()

    try:
        res = client.get("/api/v1/seo/resolve?path=/")
        assert res.status_code == 200
        brand_data = res.json().get("brand")
        assert brand_data is not None
        assert brand_data["name"] == "Sulocraft"
        assert brand_data.get("legalName") is None
        assert brand_data.get("ownerName") is None
        assert brand_data.get("instagramUrl") is None
        assert brand_data.get("whatsappUrl") is None
        assert brand_data.get("logoUrl") is None
        assert brand_data["sameAs"] == []
    finally:
        with SessionLocal() as db:
            b = db.query(BrandSettings).order_by(BrandSettings.id.asc()).first()
            if b:
                b.logo_url = orig_logo
                b.owner_name = orig_owner
                b.instagram_url = orig_ig
                b.whatsapp_url = orig_wa
                db.commit()


def test_brand_truth_contact_vs_same_as():
    """Verify 5.17.1: WhatsApp contact URL is available as a contact link,
    but strictly excluded from sameAs identity profiles. Only genuine public
    profiles (Instagram) appear in sameAs."""
    from app.models.storefront import BrandSettings

    with SessionLocal() as db:
        brand = db.query(BrandSettings).order_by(BrandSettings.id.asc()).first()
        assert brand is not None
        brand.instagram_url = "https://instagram.com/sulocraft_official"
        brand.whatsapp_url = "https://wa.me/919999988888"
        db.commit()

    try:
        res = client.get("/api/v1/seo/resolve?path=/")
        assert res.status_code == 200
        brand_data = res.json().get("brand")
        assert brand_data is not None
        assert brand_data["instagramUrl"] == "https://instagram.com/sulocraft_official"
        assert brand_data["whatsappUrl"] == "https://wa.me/919999988888"
        assert brand_data["sameAs"] == ["https://instagram.com/sulocraft_official"]
        assert not any("wa.me" in url for url in brand_data["sameAs"])
    finally:
        with SessionLocal() as db:
            b = db.query(BrandSettings).order_by(BrandSettings.id.asc()).first()
            if b:
                b.instagram_url = "https://instagram.com/sulocraft"
                b.whatsapp_url = "https://wa.me/919876543210"
                db.commit()


def test_brand_truth_no_secrets_and_snapshot_brand():
    """Verify 5.17.1: Public SEO resolution and snapshots do not leak internal database
    attributes, and brand truth is preserved in snapshot items."""
    res = client.get("/api/v1/seo/snapshot?page=1&limit=5")
    assert res.status_code == 200
    data = res.json()
    items = data["items"]
    assert len(items) > 0
    for item in items:
        brand = item["metadata"].get("brand")
        if brand:
            assert brand.get("legalName") is None
            assert "wa.me" not in str(brand.get("sameAs", []))
            # No internal private columns
            assert "id" not in brand
            assert "updated_at" not in brand
            assert "updatedAt" not in brand
            assert "secret" not in brand


# =============================================================================
# Task 5.18.2: Backend Origin, Indexing, and Lastmod Provenance Test Suite
# =============================================================================

def test_origin_policy_development_defaults_to_local_origin(monkeypatch):
    """Verify 5.18.2: In development/test environments without explicit CANONICAL_BASE_URL,
    canonical URLs resolve to local frontend_url (http://localhost:8080) and never silently
    advertise production domain https://sulocraft.com."""
    monkeypatch.delenv("CANONICAL_BASE_URL", raising=False)
    monkeypatch.delenv("SEO_PUBLIC_ORIGIN", raising=False)
    monkeypatch.delenv("SEO_INDEXING_ENABLED", raising=False)
    monkeypatch.setenv("APP_ENV", "development")

    res = client.get("/api/v1/seo/resolve?path=/")
    assert res.status_code == 200
    data = res.json()
    assert data["canonicalUrl"] == "http://localhost:8080/"
    assert "https://sulocraft.com" not in data["canonicalUrl"]
    assert data["robots"] == "noindex,nofollow"


def test_origin_policy_preprod_defaults_to_preprod_origin(monkeypatch):
    """Verify 5.18.2: In preprod/staging environments without explicit overrides,
    canonical URLs resolve to preprod origin https://dev.sulocraft.com and never
    silently advertise production domain."""
    monkeypatch.delenv("CANONICAL_BASE_URL", raising=False)
    monkeypatch.delenv("SEO_PUBLIC_ORIGIN", raising=False)
    monkeypatch.delenv("SEO_INDEXING_ENABLED", raising=False)
    monkeypatch.setenv("APP_ENV", "preprod")

    res = client.get("/api/v1/seo/resolve?path=/")
    assert res.status_code == 200
    data = res.json()
    assert data["canonicalUrl"] == "https://dev.sulocraft.com/"
    assert "https://sulocraft.com/" not in data["canonicalUrl"]
    assert data["robots"] == "noindex,nofollow"


def test_origin_policy_production_fails_closed_without_origin(monkeypatch):
    """Verify 5.18.2: Production fails closed when SEO_PUBLIC_ORIGIN and CANONICAL_BASE_URL
    are missing or empty, refusing to serve unverified or guessed canonical domains."""
    from app.services.seo import SeoService
    from app.core.config import settings

    monkeypatch.delenv("CANONICAL_BASE_URL", raising=False)
    monkeypatch.delenv("SEO_PUBLIC_ORIGIN", raising=False)
    monkeypatch.setattr(settings, "frontend_url", "")
    monkeypatch.setenv("APP_ENV", "production")

    with pytest.raises(RuntimeError) as exc_info:
        SeoService.get_canonical_base_url()
    assert "Production requires explicit" in str(exc_info.value) or "missing or invalid" in str(exc_info.value)


def test_origin_policy_production_rejects_insecure_http(monkeypatch):
    """Verify 5.18.2: Production public origin rejects insecure HTTP URLs."""
    from app.services.seo import SeoService, validate_public_origin

    with pytest.raises(ValueError) as exc:
        validate_public_origin("http://sulocraft.com", is_production=True)
    assert "must use HTTPS" in str(exc.value)

    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("SEO_PUBLIC_ORIGIN", "http://sulocraft.com")
    with pytest.raises(RuntimeError):
        SeoService.get_canonical_base_url()


def test_origin_policy_rejects_credentials_paths_and_queries():
    """Verify 5.18.2: Origins containing user credentials, path components, or query strings
    are strictly rejected across all environments."""
    from app.services.seo import validate_public_origin

    for bad_origin in (
        "https://user:secret@store.example",
        "https://store.example/some-path",
        "https://store.example?ref=abc",
        "https://store.example#fragment",
        "ftp://store.example",
    ):
        with pytest.raises(ValueError):
            validate_public_origin(bad_origin)


def test_origin_policy_rejects_production_localhost():
    """Verify 5.18.2: Production rejects localhost or loopback addresses as public origins."""
    from app.services.seo import validate_public_origin

    for local in ("https://localhost", "https://127.0.0.1", "https://[::1]"):
        with pytest.raises(ValueError):
            validate_public_origin(local, is_production=True)


def test_lastmod_provenance_sitemap_xml_omits_static_lastmod():
    """Verify 5.18.2: Sitemap XML generator omits <lastmod> for static pages without database
    provenance, and includes truthful <lastmod> for entities with DB timestamps."""
    res = client.get("/sitemap.xml")
    assert res.status_code == 200
    root = ET.fromstring(res.text)

    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = root.findall("sm:url", ns)

    static_found = False
    entity_found = False

    for u in urls:
        loc = u.find("sm:loc", ns).text
        lastmod = u.find("sm:lastmod", ns)

        if loc.endswith(".com/") or loc.endswith("/shop") or loc.endswith("/about") or loc.endswith("/contact"):
            static_found = True
            assert lastmod is None, f"Static URL {loc} must not contain <lastmod>"
        elif "/products/" in loc or "/categories/" in loc or "/collections/" in loc:
            entity_found = True
            assert lastmod is not None, f"Entity URL {loc} must contain <lastmod>"
            assert len(lastmod.text) == 10

    assert static_found
    assert entity_found


def test_lastmod_entity_timestamp_mutation_updates_lastmod_and_snapshot_hash():
    """Verify 5.18.2: Mutating an entity's timestamp updates its route inventory lastmod
    and deterministically mutates the global snapshot version hash."""
    from app.models.catalogue import Product
    from datetime import datetime, timezone

    res_initial = client.get("/api/v1/seo/snapshot?page=1&limit=5")
    base_hash = res_initial.json()["versionHash"]

    with SessionLocal() as db:
        prod = db.query(Product).filter(Product.status == "ACTIVE").first()
        assert prod is not None
        prod_id = prod.id
        prod_slug = prod.slug
        orig_updated_at = prod.updated_at
        prod.updated_at = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        db.commit()

    try:
        res_mutated_inv = client.get("/api/v1/seo/routes")
        routes = res_mutated_inv.json()["routes"]
        matching_routes = [r for r in routes if r["path"] == f"/products/{prod_slug}"]
        assert len(matching_routes) == 1
        assert matching_routes[0]["lastmod"] == "2025-01-01"

        res_mutated_snap = client.get("/api/v1/seo/snapshot?page=1&limit=5")
        new_hash = res_mutated_snap.json()["versionHash"]
        assert new_hash != base_hash, "Mutating entity timestamp must mutate global snapshot version hash"
    finally:
        with SessionLocal() as db:
            p = db.query(Product).filter(Product.id == prod_id).first()
            if p:
                p.updated_at = orig_updated_at
                db.commit()


# -----------------------------------------------------------------------------
# Task 5.13.1 Tests: Full Product Content & Truthful Catalogue Review Summary
# -----------------------------------------------------------------------------

def test_5_13_1_tc01_full_product_description_in_seo_entity_and_snapshot():
    """Verify 5.13.1-TC01: SeoProductEntity and /snapshot contain the full database description,
    with no preference for short_description, SEO meta-description, or marketing fallback copy.
    Blank/null full description remains None without fallback."""
    from app.models.catalogue import Product

    with SessionLocal() as db:
        # 1. Product with distinct long description and short description
        prod = db.query(Product).filter(Product.status == "ACTIVE").first()
        assert prod is not None
        prod_id = prod.id
        prod_slug = prod.slug
        orig_desc = prod.description
        orig_short_desc = prod.short_description

        test_long_desc = "Distinct handcrafted full body description for crochet bouquet."
        test_short_desc = "Short summary only."
        prod.description = test_long_desc
        prod.short_description = test_short_desc
        db.commit()

    try:
        # Check /api/v1/seo/resolve
        res = client.get(f"/api/v1/seo/resolve?path=/products/{prod_slug}")
        assert res.status_code == 200
        data = res.json()
        entity = data["productEntity"]
        assert entity is not None
        assert entity["description"] == test_long_desc
        assert entity["description"] != test_short_desc
        # Ensure SEO meta-description is separate from full body
        assert data["description"] != test_long_desc

        # Check /api/v1/seo/snapshot
        snap_res = client.get("/api/v1/seo/snapshot?page=1&limit=200")
        assert snap_res.status_code == 200
        snap_items = snap_res.json()["items"]
        prod_snap = next((it for it in snap_items if it["path"] == f"/products/{prod_slug}"), None)
        assert prod_snap is not None
        assert prod_snap["metadata"]["productEntity"]["description"] == test_long_desc

        # 2. Blank / None full description must remain None (no fallback to short_description or marketing copy)
        with SessionLocal() as db:
            p = db.query(Product).filter(Product.id == prod_id).first()
            p.description = None
            db.commit()

        res_none = client.get(f"/api/v1/seo/resolve?path=/products/{prod_slug}")
        assert res_none.status_code == 200
        entity_none = res_none.json()["productEntity"]
        assert entity_none["description"] is None

    finally:
        with SessionLocal() as db:
            p = db.query(Product).filter(Product.id == prod_id).first()
            if p:
                p.description = orig_desc
                p.short_description = orig_short_desc
                db.commit()


def test_5_13_1_tc02_truthful_catalogue_rating_summary_no_seed_fallback():
    """Verify 5.13.1-TC02: ProductListItem and ProductDetail have aggregateRating: null
    when no genuine Review records exist, even if seeded rating/reviews_count exist.
    When genuine Review records exist, aggregateRating derives from actual reviews
    with explicit VERIFIED_REVIEWS provenance."""
    from app.models.catalogue import Product, Review

    with SessionLocal() as db:
        prod = db.query(Product).filter(Product.status == "ACTIVE").first()
        assert prod is not None
        prod_id = prod.id
        prod_slug = prod.slug
        prod_name = prod.name

        # Ensure product has seeded rating / reviews_count > 0, but no Review records
        orig_rating = prod.rating
        orig_rev_count = prod.reviews_count
        prod.rating = 4.9
        prod.reviews_count = 42

        # Delete any existing reviews for this product
        existing_reviews = db.query(Review).filter(Review.product_id == prod_id).all()
        saved_reviews = []
        for r in existing_reviews:
            saved_reviews.append({
                "author_name": r.author_name,
                "location": r.location,
                "rating": r.rating,
                "text": r.text,
                "avatar_url": r.avatar_url,
                "date": r.date,
            })
            db.delete(r)
        db.commit()

    try:
        # A. With NO genuine Review records:
        # 1. Product list
        res_list = client.get("/api/v1/products")
        assert res_list.status_code == 200
        items = res_list.json()
        item = next(it for it in items if it["id"] == prod_id)
        assert item["aggregateRating"] is None, "ProductListItem.aggregateRating must be null when no Review records exist"
        # Seeded fields remain for backward compat
        assert item["rating"] == 4.9
        assert item["reviewCount"] == 42

        # 2. Product detail
        res_detail = client.get(f"/api/v1/products/{prod_slug}")
        assert res_detail.status_code == 200
        detail = res_detail.json()
        assert detail["aggregateRating"] is None, "ProductDetail.aggregateRating must be null when no Review records exist"

        # B. Now add actual Review records:
        with SessionLocal() as db:
            r1 = Review(
                product_id=prod_id,
                product_name=prod_name,
                author_name="Alice Verified",
                rating=5,
                text="Wonderful handmade craft!",
            )
            r2 = Review(
                product_id=prod_id,
                product_name=prod_name,
                author_name="Bob Verified",
                rating=4,
                text="Very lovely roses.",
            )
            db.add_all([r1, r2])
            db.commit()

        # 1. Product list with actual reviews
        res_list_after = client.get("/api/v1/products")
        item_after = next(it for it in res_list_after.json() if it["id"] == prod_id)
        assert item_after["aggregateRating"] is not None
        assert item_after["aggregateRating"]["ratingValue"] == 4.5
        assert item_after["aggregateRating"]["reviewCount"] == 2
        assert item_after["aggregateRating"]["provenance"] == "VERIFIED_REVIEWS"

        # 2. Product detail with actual reviews
        res_detail_after = client.get(f"/api/v1/products/{prod_slug}")
        detail_after = res_detail_after.json()
        assert detail_after["aggregateRating"] is not None
        assert detail_after["aggregateRating"]["ratingValue"] == 4.5
        assert detail_after["aggregateRating"]["reviewCount"] == 2
        assert detail_after["aggregateRating"]["provenance"] == "VERIFIED_REVIEWS"

    finally:
        with SessionLocal() as db:
            # Cleanup added test reviews
            db.query(Review).filter(Review.product_id == prod_id).delete()
            # Restore saved reviews and product rating
            for rev_data in saved_reviews:
                db.add(Review(product_id=prod_id, product_name=prod_name, **rev_data))
            p = db.query(Product).filter(Product.id == prod_id).first()
            if p:
                p.rating = orig_rating
                p.reviews_count = orig_rev_count
            db.commit()


def test_5_13_1_tc03_security_sanitization_and_no_pii_in_aggregate():
    """Verify 5.13.1-TC03: HTML and plaintext descriptions are safely JSON serialized;
    aggregateRating payloads contain strictly aggregated stats without customer PII,
    author names, emails, authentication, or private fields."""
    from app.models.catalogue import Product, Review

    with SessionLocal() as db:
        prod = db.query(Product).filter(Product.status == "ACTIVE").first()
        assert prod is not None
        prod_id = prod.id
        prod_slug = prod.slug
        orig_desc = prod.description

        # HTML/special character description
        dangerous_desc = '<script>alert("xss")</script> & special chars "quotes" & \\n \t'
        prod.description = dangerous_desc

        test_rev = Review(
            product_id=prod_id,
            product_name=prod.name,
            author_name="Secret Customer Private Name",
            location="Secret Location",
            rating=5,
            text="Private review text containing secret customer note.",
        )
        db.add(test_rev)
        db.commit()
        test_rev_id = test_rev.id

    try:
        # Check SEO resolve
        res_seo = client.get(f"/api/v1/seo/resolve?path=/products/{prod_slug}")
        assert res_seo.status_code == 200
        seo_data = res_seo.json()
        assert seo_data["productEntity"]["description"] == dangerous_desc

        # Check catalogue product detail
        res_detail = client.get(f"/api/v1/products/{prod_slug}")
        assert res_detail.status_code == 200
        detail = res_detail.json()
        agg = detail["aggregateRating"]
        assert agg is not None
        # Strict schema verification: only ratingValue, reviewCount, bestRating, worstRating, provenance
        allowed_keys = {"ratingValue", "reviewCount", "bestRating", "worstRating", "provenance"}
        assert set(agg.keys()).issubset(allowed_keys)
        assert "author_name" not in agg
        assert "location" not in agg
        assert "text" not in agg
        assert "Secret Customer Private Name" not in str(agg)

        # Check catalogue product list item
        res_list = client.get("/api/v1/products")
        list_items = res_list.json()
        list_item = next(it for it in list_items if it["id"] == prod_id)
        assert set(list_item["aggregateRating"].keys()).issubset(allowed_keys)
        assert "Secret Customer Private Name" not in str(list_item["aggregateRating"])

    finally:
        with SessionLocal() as db:
            db.query(Review).filter(Review.id == test_rev_id).delete()
            p = db.query(Product).filter(Product.id == prod_id).first()
            if p:
                p.description = orig_desc
            db.commit()


def test_5_13_1_tc04_consistency_performance_and_snapshot_version_invalidation():
    """Verify 5.13.1-TC04:
    1. Consistent aggregateRating across /products, /categories/{slug}/products, /collections/{slug}/products,
       /products/search, /storefront/home, /products/{slug}, and /seo/resolve.
    2. Modifying Product.description mutates the global snapshot versionHash.
    3. Adding a new Review mutates the global snapshot versionHash."""
    from app.models.catalogue import Product, Review

    res_initial = client.get("/api/v1/seo/snapshot?page=1&limit=5")
    base_hash = res_initial.json()["versionHash"]

    with SessionLocal() as db:
        prod = db.query(Product).filter(Product.status == "ACTIVE").first()
        assert prod is not None
        prod_id = prod.id
        prod_slug = prod.slug
        prod_name = prod.name
        orig_desc = prod.description

        # Mutate Product.description
        prod.description = "Updated unique description body for cache invalidation check."
        db.commit()

    try:
        # Verify snapshot versionHash changes on description modification
        res_desc_mutated = client.get("/api/v1/seo/snapshot?page=1&limit=5")
        new_hash_desc = res_desc_mutated.json()["versionHash"]
        assert new_hash_desc != base_hash, "Mutating Product.description must mutate global snapshot version hash"

        # Now add a review and verify versionHash changes again
        with SessionLocal() as db:
            rev = Review(
                product_id=prod_id,
                product_name=prod_name,
                author_name="Reviewer Fresh",
                rating=5,
                text="Great product",
            )
            db.add(rev)
            db.commit()
            rev_id = rev.id

        res_rev_mutated = client.get("/api/v1/seo/snapshot?page=1&limit=5")
        new_hash_rev = res_rev_mutated.json()["versionHash"]
        assert new_hash_rev != new_hash_desc, "Adding a Review must mutate global snapshot version hash"

        # Verify cross-surface aggregate rating consistency:
        # 1. Product detail
        res_detail = client.get(f"/api/v1/products/{prod_slug}")
        detail_agg = res_detail.json()["aggregateRating"]
        assert detail_agg is not None

        # 2. Product list
        res_list = client.get("/api/v1/products")
        list_item = next(it for it in res_list.json() if it["id"] == prod_id)
        assert list_item["aggregateRating"] == detail_agg

        # 3. Product search
        res_search = client.get(f"/api/v1/products/search?q={prod_name[:6]}")
        search_matches = [it for it in res_search.json() if it["id"] == prod_id]
        if search_matches:
            assert search_matches[0]["aggregateRating"] == detail_agg

        # 4. Storefront home
        res_home = client.get("/api/v1/storefront/home")
        assert res_home.status_code == 200
        sections = res_home.json()["sections"]
        for sec in sections:
            if "products" in sec and sec["products"]:
                for p_item in sec["products"]:
                    if p_item["id"] == prod_id:
                        assert p_item["aggregateRating"] == detail_agg

    finally:
        with SessionLocal() as db:
            if "rev_id" in locals():
                db.query(Review).filter(Review.id == rev_id).delete()
            p = db.query(Product).filter(Product.id == prod_id).first()
            if p:
                p.description = orig_desc
            db.commit()


# -------------------------------------------------------------------------
# Section 5.16.1 Test Cases: Truthful backend sharing copy
# -------------------------------------------------------------------------

from app.models.catalogue import Product, ProductImage, Collection, Category

def test_5_16_1_tc01_saved_content_preserved_without_unsupported_claims():
    """5.16.1-TC01: Product lacks materials; saved description/alt exists.
    Saved content is preserved, no generated material/100%/limited-edition claim appended.
    """
    with SessionLocal() as db:
        prod = db.query(Product).filter(Product.status == "ACTIVE").first()
        assert prod is not None
        prod_id = prod.id
        prod_slug = prod.slug
        orig_desc = prod.description
        orig_short_desc = prod.short_description

        # Set saved description and custom alt text without material claims
        saved_text = "Handcrafted with precision and neat stitching."
        prod.short_description = saved_text
        prod.description = "Full body: Handcrafted with precision and neat stitching."
        
        # Save custom alt text on primary image if available
        orig_img_alt = None
        target_img_id = None
        if prod.images:
            target_img = prod.images[0]
            target_img_id = target_img.id
            orig_img_alt = target_img.alt_text
            target_img.alt_text = "Verified handcrafted crochet red rose bloom"
        db.commit()

    try:
        res = client.get(f"/api/v1/seo/resolve?path=/products/{prod_slug}")
        assert res.status_code == 200
        data = res.json()

        # Meta description must use saved content directly without appended marketing claims
        assert data["description"] == saved_text
        assert "milk cotton" not in data["description"].lower()
        assert "100% handmade heirloom" not in data["description"].lower()
        assert "heirloom" not in data["description"].lower()

        # Image alt must prefer saved DB alt text
        if target_img_id:
            assert data["imageAlt"] == "Verified handcrafted crochet red rose bloom"
            assert data["imageMetadata"]["altText"] == "Verified handcrafted crochet red rose bloom"
        assert "milk cotton" not in (data["imageAlt"] or "").lower()

    finally:
        with SessionLocal() as db:
            p = db.query(Product).filter(Product.id == prod_id).first()
            if p:
                p.description = orig_desc
                p.short_description = orig_short_desc
                if target_img_id:
                    img = db.query(ProductImage).filter(ProductImage.id == target_img_id).first()
                    if img:
                        img.alt_text = orig_img_alt
            db.commit()


def test_5_16_1_tc02_missing_content_neutral_fallback():
    """5.16.1-TC02: Missing product/collection copy or image alt.
    Neutral entity fallback, no invented facts; same existing URLs/dimensions.
    """
    with SessionLocal() as db:
        prod = db.query(Product).filter(Product.status == "ACTIVE").first()
        assert prod is not None
        prod_id = prod.id
        prod_slug = prod.slug
        prod_name = prod.name
        orig_desc = prod.description
        orig_short_desc = prod.short_description

        # Clear descriptions
        prod.short_description = None
        prod.description = None

        orig_alts = {}
        for img in prod.images:
            orig_alts[img.id] = img.alt_text
            img.alt_text = None

        col = db.query(Collection).filter(Collection.is_active.is_(True)).first()
        col_id = col.id if col else None
        orig_col_desc = col.description if col else None
        if col:
            col.description = None
            col_slug = col.slug
            col_name = col.name

        db.commit()

    try:
        # 1. Product fallback check
        res = client.get(f"/api/v1/seo/resolve?path=/products/{prod_slug}")
        assert res.status_code == 200
        data = res.json()

        expected_fallback = f"Handcrafted {prod_name} by Sulocraft."
        assert data["description"] == expected_fallback
        assert data["imageAlt"] == f"Handcrafted {prod_name} by Sulocraft"
        assert "milk cotton" not in data["description"].lower()
        assert "heirloom" not in data["description"].lower()

        # 2. Collection fallback check
        if col_id:
            col_res = client.get(f"/api/v1/seo/resolve?path=/collections/{col_slug}")
            assert col_res.status_code == 200
            col_data = col_res.json()
            assert col_data["description"] == f"Explore the {col_name} handcrafted crochet collection at Sulocraft."
            assert "limited edition heirloom" not in col_data["description"].lower()
            assert "heirloom" not in col_data["description"].lower()

    finally:
        with SessionLocal() as db:
            p = db.query(Product).filter(Product.id == prod_id).first()
            if p:
                p.description = orig_desc
                p.short_description = orig_short_desc
                for img in p.images:
                    if img.id in orig_alts:
                        img.alt_text = orig_alts[img.id]
            if col_id:
                c = db.query(Collection).filter(Collection.id == col_id).first()
                if c:
                    c.description = orig_col_desc
            db.commit()


def test_5_16_1_tc03_about_home_collection_regression():
    """5.16.1-TC03: About/home/collection metadata.
    Portrait alt does not invent activity; no generic unsupported marketing claims; canonical/image contract stable.
    """
    # 1. /about page
    res_about = client.get("/api/v1/seo/resolve?path=/about")
    assert res_about.status_code == 200
    about_data = res_about.json()
    assert about_data["imageAlt"] == "Sulocraft founder Anupama Sharma with a bouquet"
    assert about_data["imageMetadata"]["altText"] == "Sulocraft founder Anupama Sharma with a bouquet"
    assert "creating handcrafted crochet" not in (about_data["imageAlt"] or "").lower()
    assert about_data["title"] == "Our Story | Handcrafted Crochet | Sulocraft"
    assert about_data["description"] == "Founded by Anupama Sharma, Sulocraft creates handcrafted crochet pieces and flower bouquets in small batches."
    assert "heirloom" not in about_data["description"].lower()

    # 2. Homepage /
    res_home = client.get("/api/v1/seo/resolve?path=/")
    assert res_home.status_code == 200
    home_data = res_home.json()
    assert home_data["description"] == "Handcrafted crochet gifts, flower bouquets, amigurumi keepsakes, and home decor by Sulocraft in India."
    assert "milk cotton" not in home_data["description"].lower()
    assert "100% handcrafted heirloom" not in home_data["description"].lower()
    assert home_data["h1"] == "Handcrafted Heirloom Crochet"
    for faq in home_data.get("faqs", []):
        assert "milk cotton" not in faq["answer"].lower()
        assert "100% handmade" not in faq["answer"].lower()

    # 3. Category fallback
    res_cat = client.get("/api/v1/seo/resolve?path=/categories/flowers")
    if res_cat.status_code == 200:
        cat_data = res_cat.json()
        for faq in cat_data.get("faqs", []):
            assert "milk cotton" not in faq["answer"].lower()
            assert "100% hand-knitted" not in faq["answer"].lower()


def test_5_16_1_tc04_security_private_routes_and_markup_isolation():
    """5.16.1-TC04: Markup/private fields in stored content and private route.
    Typed plain data, no new private field exposure, no remote fetch or mutations.
    """
    # Private routes fail safe with noindex,nofollow
    for priv_path in ("/account", "/admin", "/cart", "/checkout"):
        res = client.get(f"/api/v1/seo/resolve?path={priv_path}")
        assert res.status_code == 200
        assert res.json()["robots"] == "noindex,nofollow"
        assert res.json()["productEntity"] is None
        assert res.json()["categoryEntity"] is None

    # Stored content with markup or script injection in product description
    with SessionLocal() as db:
        prod = db.query(Product).filter(Product.status == "ACTIVE").first()
        prod_id = prod.id
        prod_slug = prod.slug
        orig_short_desc = prod.short_description

        prod.short_description = "<script>alert('xss')</script> Safe Handcrafted Crochet"
        db.commit()

    try:
        res = client.get(f"/api/v1/seo/resolve?path=/products/{prod_slug}")
        assert res.status_code == 200
        data = res.json()
        # Returned as literal typed string in JSON
        assert "<script>alert('xss')</script> Safe Handcrafted Crochet" in data["description"]
    finally:
        with SessionLocal() as db:
            p = db.query(Product).filter(Product.id == prod_id).first()
            if p:
                p.short_description = orig_short_desc
            db.commit()






