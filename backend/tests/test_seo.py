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
    """Verify /sitemap.xml and /api/v1/seo/sitemap.xml generate valid sitemaps with all active entities."""
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
