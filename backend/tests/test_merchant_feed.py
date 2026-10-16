"""Tests for Google Merchant Center / Free Listings product feed conforming to docs/merchant-center.md."""

import re
import xml.etree.ElementTree as ET
import pytest
from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.models.catalogue import Category, Product, ProductVariant
from app.services.seo import SeoService

client = TestClient(app)

GOOGLE_NS = {"g": "http://base.google.com/ns/1.0"}


@pytest.fixture(autouse=True)
def default_seo_env(monkeypatch):
    """Ensure baseline test execution simulates configured production environment."""
    monkeypatch.setenv("CANONICAL_BASE_URL", "https://sulocraft.com")
    monkeypatch.setenv("SEO_PUBLIC_ORIGIN", "https://sulocraft.com")
    monkeypatch.setenv("SEO_INDEXING_ENABLED", "true")


def test_merchant_feed_xml_structure():
    """Verify generated XML adheres to RSS 2.0 with Google Merchant Center namespace."""
    with SessionLocal() as db:
        xml_content = SeoService.generate_merchant_feed_xml(db)

    assert xml_content.startswith('<?xml version="1.0" encoding="UTF-8"?>')
    root = ET.fromstring(xml_content)
    assert root.tag == "rss"
    assert root.attrib.get("version") == "2.0"

    channel = root.find("channel")
    assert channel is not None
    assert channel.find("title").text == "Sulocraft Product Feed"
    assert channel.find("link").text == "https://sulocraft.com/"
    assert "Sulocraft" in channel.find("description").text

    items = channel.findall("item")
    assert len(items) > 0


def test_merchant_feed_item_attributes():
    """Verify all required Google Merchant Center attributes are present, typed, and bounded."""
    with SessionLocal() as db:
        xml_content = SeoService.generate_merchant_feed_xml(db)

    root = ET.fromstring(xml_content)
    channel = root.find("channel")
    items = channel.findall("item")
    assert len(items) >= 5

    price_pattern = re.compile(r"^\d+\.\d{2} INR$")

    for item in items:
        # g:id
        item_id = item.find("g:id", GOOGLE_NS)
        assert item_id is not None and item_id.text, "g:id must not be empty"

        # g:title
        title = item.find("g:title", GOOGLE_NS)
        assert title is not None and title.text, "g:title must not be empty"
        assert len(title.text) <= 150, "g:title must not exceed 150 characters"

        # g:description
        desc = item.find("g:description", GOOGLE_NS)
        assert desc is not None and desc.text, "g:description must not be empty"
        assert len(desc.text) <= 5000, "g:description must not exceed 5000 characters"

        # g:link
        link = item.find("g:link", GOOGLE_NS)
        assert link is not None and link.text.startswith("https://sulocraft.com/products/")

        # g:image_link
        img = item.find("g:image_link", GOOGLE_NS)
        assert img is not None and (img.text.startswith("http://") or img.text.startswith("https://"))

        # g:availability
        avail = item.find("g:availability", GOOGLE_NS)
        assert avail is not None and avail.text in ("in_stock", "out_of_stock")

        # g:price
        price = item.find("g:price", GOOGLE_NS)
        assert price is not None and price_pattern.match(price.text)

        # g:brand
        brand = item.find("g:brand", GOOGLE_NS)
        assert brand is not None and brand.text == "Sulocraft"

        # g:condition
        condition = item.find("g:condition", GOOGLE_NS)
        assert condition is not None and condition.text == "new"

        # g:identifier_exists
        ident = item.find("g:identifier_exists", GOOGLE_NS)
        assert ident is not None and ident.text == "no"


def test_merchant_feed_truthful_identifiers():
    """Verify custom handmade products truthfully omit fake GTIN/MPN and set identifier_exists='no'."""
    with SessionLocal() as db:
        xml_content = SeoService.generate_merchant_feed_xml(db)

    root = ET.fromstring(xml_content)
    for item in root.findall(".//item"):
        ident = item.find("g:identifier_exists", GOOGLE_NS)
        assert ident is not None and ident.text == "no"
        assert item.find("g:gtin", GOOGLE_NS) is None, "Custom handmade items must not emit fake GTIN"
        assert item.find("g:mpn", GOOGLE_NS) is None, "Custom handmade items must not emit fake MPN"


def test_merchant_feed_parity_with_database():
    """Verify feed values accurately reflect database variants, prices, and inventory."""
    with SessionLocal() as db:
        rose_prod = db.query(Product).filter(Product.slug == "forever-crochet-rose-bouquet").first()
        assert rose_prod is not None
        rose_variant = [v for v in rose_prod.variants if v.status == "ACTIVE"][0]

        items = SeoService.get_merchant_feed_items(db)
        matching = [item for item in items if item.id == rose_variant.sku]
        assert len(matching) == 1
        rose_feed_item = matching[0]

        assert rose_feed_item.link == "https://sulocraft.com/products/forever-crochet-rose-bouquet"
        assert rose_feed_item.price == f"{float(rose_variant.price):.2f} INR"
        expected_avail = "in_stock" if rose_variant.stock_quantity > 0 else "out_of_stock"
        assert rose_feed_item.availability == expected_avail
        assert rose_feed_item.brand == "Sulocraft"
        assert rose_feed_item.item_group_id == "forever-crochet-rose-bouquet"


def test_merchant_feed_excludes_draft_and_archived():
    """Verify draft and archived products are strictly excluded from the feed."""
    with SessionLocal() as db:
        # Create draft product
        draft_prod = Product(
            name="Draft Amigurumi Bee",
            slug="draft-amigurumi-bee",
            status="DRAFT",
            primary_image="products/draft-bee.png",
            description="Draft product description.",
        )
        db.add(draft_prod)
        db.flush()

        draft_var = ProductVariant(
            product_id=draft_prod.id,
            sku="SULO-DRAFT-001",
            name="Default",
            price=899,
            stock_quantity=10,
            status="ACTIVE",
        )
        db.add(draft_var)

        # Create archived product
        arch_prod = Product(
            name="Archived Daisy Pot",
            slug="archived-daisy-pot",
            status="ARCHIVED",
            primary_image="products/archived-daisy.png",
            description="Archived product description.",
        )
        db.add(arch_prod)
        db.flush()

        arch_var = ProductVariant(
            product_id=arch_prod.id,
            sku="SULO-ARCH-001",
            name="Default",
            price=1299,
            stock_quantity=5,
            status="ACTIVE",
        )
        db.add(arch_var)
        db.commit()

        items = SeoService.get_merchant_feed_items(db)
        skus = {item.id for item in items}
        assert "SULO-DRAFT-001" not in skus, "DRAFT product variants must not be exported in feed"
        assert "SULO-ARCH-001" not in skus, "ARCHIVED product variants must not be exported in feed"


def test_merchant_feed_excludes_inactive_variants():
    """Verify inactive variants within an active product are excluded."""
    with SessionLocal() as db:
        prod = Product(
            name="Test Multi-Variant Plant",
            slug="test-multi-variant-plant",
            status="ACTIVE",
            primary_image="products/test-plant.png",
            description="Handcrafted plant test.",
        )
        db.add(prod)
        db.flush()

        v_active = ProductVariant(
            product_id=prod.id,
            sku="SULO-PLANT-ACT-001",
            name="Green Leaves",
            price=1499,
            stock_quantity=8,
            status="ACTIVE",
        )
        v_inactive = ProductVariant(
            product_id=prod.id,
            sku="SULO-PLANT-INACT-001",
            name="Discontinued Variegated",
            price=1699,
            stock_quantity=0,
            status="INACTIVE",
        )
        db.add_all([v_active, v_inactive])
        db.commit()

        items = SeoService.get_merchant_feed_items(db)
        skus = {item.id for item in items}
        assert "SULO-PLANT-ACT-001" in skus
        assert "SULO-PLANT-INACT-001" not in skus, "INACTIVE variants must be excluded from feed"


def test_merchant_feed_out_of_stock_variant():
    """Verify variants with stock_quantity=0 are correctly marked out_of_stock."""
    with SessionLocal() as db:
        prod = Product(
            name="Test Zero Stock Cactus",
            slug="test-zero-stock-cactus",
            status="ACTIVE",
            primary_image="products/test-cactus.png",
            description="Handmade crochet cactus.",
        )
        db.add(prod)
        db.flush()

        v_zero = ProductVariant(
            product_id=prod.id,
            sku="SULO-ZERO-001",
            name="Default",
            price=999,
            stock_quantity=0,
            status="ACTIVE",
        )
        db.add(v_zero)
        db.commit()

        items = SeoService.get_merchant_feed_items(db)
        zero_items = [i for i in items if i.id == "SULO-ZERO-001"]
        assert len(zero_items) == 1
        assert zero_items[0].availability == "out_of_stock"


def test_merchant_feed_sale_price_handling():
    """Verify compare_at_price > price properly populates regular price and sale_price."""
    with SessionLocal() as db:
        prod = Product(
            name="Test Discounted Flower",
            slug="test-discounted-flower",
            status="ACTIVE",
            primary_image="products/test-flower.png",
            description="Handmade discounted flower.",
        )
        db.add(prod)
        db.flush()

        v_sale = ProductVariant(
            product_id=prod.id,
            sku="SULO-SALE-001",
            name="Default",
            price=1999,
            compare_at_price=2499,
            stock_quantity=10,
            status="ACTIVE",
        )
        db.add(v_sale)
        db.commit()

        items = SeoService.get_merchant_feed_items(db)
        sale_items = [i for i in items if i.id == "SULO-SALE-001"]
        assert len(sale_items) == 1
        assert sale_items[0].price == "2499.00 INR"
        assert sale_items[0].sale_price == "1999.00 INR"


def test_merchant_feed_xml_injection_safety():
    """Verify special XML characters are properly escaped and do not corrupt the feed."""
    with SessionLocal() as db:
        prod = Product(
            name="Handcrafted & Stitched <Special> 'Rose' \"Limited\"",
            slug="test-escaped-special-rose",
            status="ACTIVE",
            primary_image="products/test-escaped.png",
            description="Special crafted item with 100% cotton & wool <guaranteed> \"art\".",
        )
        db.add(prod)
        db.flush()

        v_special = ProductVariant(
            product_id=prod.id,
            sku="SULO-ESC-001",
            name="Default",
            price=1500,
            stock_quantity=5,
            status="ACTIVE",
        )
        db.add(v_special)
        db.commit()

        xml_content = SeoService.generate_merchant_feed_xml(db)
        # Verify valid XML parsing
        root = ET.fromstring(xml_content)
        matching = [item for item in root.findall(".//item") if item.find("g:id", GOOGLE_NS).text == "SULO-ESC-001"]
        assert len(matching) == 1
        item = matching[0]

        # Parsed text matches original unescaped strings
        assert item.find("g:title", GOOGLE_NS).text == "Handcrafted & Stitched <Special> 'Rose' \"Limited\""
        assert "cotton & wool <guaranteed>" in item.find("g:description", GOOGLE_NS).text


def test_merchant_feed_json_endpoint():
    """Verify GET /api/v1/seo/merchant-feed returns structured JSON response."""
    res = client.get("/api/v1/seo/merchant-feed")
    assert res.status_code == 200
    data = res.json()

    assert data.get("feedVersion") == "1.0" or data.get("feed_version") == "1.0"
    total = data.get("totalItems", data.get("total_items", 0))
    assert total > 0
    eligible = data.get("eligibleProductsCount", data.get("eligible_products_count", 0))
    assert eligible > 0
    assert len(data["items"]) > 0

    first = data["items"][0]
    assert "id" in first
    assert "title" in first
    assert "link" in first
    assert "imageLink" in first or "image_link" in first
    assert "availability" in first
    assert "price" in first
    assert first.get("identifierExists") == "no" or first.get("identifier_exists") == "no"

    disclaimer = data.get("policyDisclaimer", data.get("policy_disclaimer", ""))
    assert "handcrafted" in disclaimer.lower()
    assert "identifier_exists is set to 'no'" in disclaimer


def test_merchant_feed_xml_endpoint():
    """Verify GET /api/v1/seo/merchant-feed.xml returns valid XML with proper content-type."""
    res = client.get("/api/v1/seo/merchant-feed.xml")
    assert res.status_code == 200
    assert "xml" in res.headers["content-type"]

    root = ET.fromstring(res.text)
    assert root.tag == "rss"
    items = root.findall(".//item")
    assert len(items) > 0
