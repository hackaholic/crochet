"""Tests for media metadata, dimension resolution, and SSRF/security protections (Task 5.20)."""

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from app.main import app
from app.db.session import SessionLocal
from app.models.catalogue import Product, ProductImage
from app.schemas.media import MediaMetadataOut, MediaVariantOut
from app.schemas.catalogue import ProductImageOut, ProductListItem, ProductDetail
from app.schemas.storefront import (
    HomepageCampaignOut,
    CategorySummary,
    OccasionSummary,
    PromoBannerSectionOut,
    ImageTextSectionOut,
)
from app.schemas.seo import SeoMetadataOut
from app.services.media import (
    inspect_image_bytes,
    get_image_dimensions,
    build_media_metadata,
    _resolve_local_image_path,
    get_image_variants,
    get_media_manifest_hash,
)
from app.services.seo import SeoService


@pytest.fixture
def client():
    return TestClient(app)


# -----------------------------------------------------------------------------
# 5.20-TC01: Acceptance & Dimensions Parsing on Real Assets
# -----------------------------------------------------------------------------

def test_inspect_image_bytes_png():
    """Verify PNG header parsing returns expected dimensions and MIME type."""
    # 100x200 PNG header sample: 16 bytes prefix, 4 bytes width (100 = 0x64), 4 bytes height (200 = 0xC8)
    png_header = (
        b"\x89PNG\r\n\x1a\n"
        b"\x00\x00\x00\rIHDR"
        b"\x00\x00\x00\x64"
        b"\x00\x00\x00\xc8"
        b"\x08\x06\x00\x00\x00"
    )
    w, h, mime = inspect_image_bytes(png_header)
    assert w == 100
    assert h == 200
    assert mime == "image/png"


def test_inspect_image_bytes_corrupt():
    """Verify corrupt or truncated binary data safely yields None without raising exceptions."""
    assert inspect_image_bytes(b"") == (None, None, None)
    assert inspect_image_bytes(b"invalid data") == (None, None, None)
    assert inspect_image_bytes(b"\x89PNG\r\n\x1a\n") == (None, None, "image/png")


def test_real_project_asset_dimensions():
    """Verify real project assets resolve to accurate intrinsic pixel dimensions."""
    # Products
    w, h, mime = get_image_dimensions("products/forever-crochet-rose-bouquet/primary.png")
    assert w == 1122
    assert h == 1402
    assert mime == "image/png"

    # Hero
    w, h, mime = get_image_dimensions("hero/heritage.png")
    assert w == 1672
    assert h == 941
    assert mime == "image/png"

    # About
    w, h, mime = get_image_dimensions("about/anupama-sharma.png")
    assert w == 1114
    assert h == 1411
    assert mime == "image/png"

    # Occasions (via alias map)
    w, h, mime = get_image_dimensions("occasions/birthday-gifting-v2.png")
    assert w == 1448
    assert h == 1086
    assert mime == "image/png"


def test_build_media_metadata_helper():
    """Verify build_media_metadata produces complete MediaMetadataOut objects with responsive variants."""
    meta = build_media_metadata(
        "products/forever-crochet-rose-bouquet/primary.png",
        alt_text="Forever Rose Bouquet",
    )
    assert meta is not None
    assert meta.key == "products/forever-crochet-rose-bouquet/primary.png"
    assert "forever-crochet-rose-bouquet/primary.png" in meta.url
    assert meta.alt_text == "Forever Rose Bouquet"
    assert meta.width == 1122
    assert meta.height == 1402
    assert meta.content_type == "image/png"
    assert len(meta.variants) == 3
    assert [v.width for v in meta.variants] == [480, 800, 1122]
    assert all(v.content_type == "image/webp" for v in meta.variants)
    assert all(v.descriptor == f"{v.width}w" for v in meta.variants)

    # Explicit empty variants override
    meta_empty = build_media_metadata(
        "products/forever-crochet-rose-bouquet/primary.png",
        variants=[],
    )
    assert meta_empty.variants == []

    # Non-manifest asset yields empty variants
    meta_unknown = build_media_metadata("unoptimized/unknown-image.jpg")
    assert meta_unknown.variants == []


def test_product_image_out_schema_dimensions():
    """Verify ProductImageOut auto-resolves dimensions and maintains serialization alias compatibility."""
    item = ProductImageOut(
        id=1,
        url="products/forever-crochet-rose-bouquet/primary.png",
        alt_text="Handcrafted Rose",
        is_primary=True,
    )
    assert item.width == 1122
    assert item.height == 1402
    assert item.content_type == "image/png"

    dump = item.model_dump(by_alias=True)
    assert dump["width"] == 1122
    assert dump["height"] == 1402
    assert dump["contentType"] == "image/png"
    assert "url" in dump


def test_product_list_item_and_detail_primary_media():
    """Verify ProductListItem and ProductDetail schemas include primaryImageMetadata."""
    item = ProductListItem(
        id=1,
        name="Rose Bouquet",
        slug="rose-bouquet",
        price=1999,
        image="products/forever-crochet-rose-bouquet/primary.png",
    )
    assert item.primary_image_metadata is not None
    assert item.primary_image_metadata.width == 1122
    assert item.primary_image_metadata.height == 1402
    assert item.primary_image_metadata.content_type == "image/png"

    detail = ProductDetail(
        id=1,
        name="Rose Bouquet",
        slug="rose-bouquet",
        price=1999,
        images=["products/forever-crochet-rose-bouquet/primary.png"],
    )
    assert detail.primary_image_metadata is not None
    assert detail.primary_image_metadata.width == 1122
    assert detail.primary_image_metadata.height == 1402


def test_storefront_campaign_and_category_summary():
    """Verify HomepageCampaignOut and CategorySummary schemas expose media dimensions."""
    campaign = HomepageCampaignOut(
        id=1,
        title="Artisan Story",
        description="Handcrafted in India",
        imageUrl="hero/heritage.png",
        imageAlt="Hero banner",
        mobileImageUrl="hero/heritage.png",
    )
    assert campaign.image_width == 1672
    assert campaign.image_height == 941
    assert campaign.image_type == "image/png"
    assert campaign.mobile_image_width == 1672
    assert campaign.mobile_image_height == 941
    assert campaign.mobile_image_type == "image/png"

    dump = campaign.model_dump(by_alias=True)
    assert dump["imageWidth"] == 1672
    assert dump["imageHeight"] == 941
    assert dump["imageType"] == "image/png"

    cat = CategorySummary(
        id=1,
        name="Amigurumi",
        slug="amigurumi",
        imageUrl="categories/amigurumi/card-v2.png",
    )
    assert cat.image_width == 1672
    assert cat.image_height == 941
    assert cat.image_alt == "Amigurumi category"


def test_seo_resolve_homepage_media_metadata(client):
    """Verify /api/v1/seo/resolve returns imageWidth, imageHeight, imageType, imageMetadata for homepage."""
    res = client.get("/api/v1/seo/resolve?path=/")
    assert res.status_code == 200
    data = res.json()
    assert data["imageWidth"] == 1672
    assert data["imageHeight"] == 941
    assert data["imageType"] == "image/png"
    assert data["imageMetadata"] is not None
    assert data["imageMetadata"]["width"] == 1672
    assert data["imageMetadata"]["height"] == 941
    assert data["imageMetadata"]["contentType"] == "image/png"


def test_seo_resolve_about_media_metadata(client):
    """Verify /api/v1/seo/resolve returns image metadata for /about page."""
    res = client.get("/api/v1/seo/resolve?path=/about")
    assert res.status_code == 200
    data = res.json()
    assert data["imageWidth"] == 1114
    assert data["imageHeight"] == 1411
    assert data["imageType"] == "image/png"
    assert data["imageMetadata"]["altText"] == "Sulocraft founder Anupama Sharma with a bouquet"


def test_seo_resolve_product_media_metadata(client):
    """Verify /api/v1/seo/resolve returns primary image dimensions and productEntity.media list."""
    res = client.get("/api/v1/seo/resolve?path=/products/forever-crochet-rose-bouquet")
    assert res.status_code == 200
    data = res.json()
    assert data["imageWidth"] == 1122
    assert data["imageHeight"] == 1402
    assert data["imageType"] == "image/png"
    assert data["imageMetadata"] is not None

    entity = data["productEntity"]
    assert "media" in entity
    assert len(entity["media"]) > 0
    primary_media = entity["media"][0]
    assert primary_media["width"] == 1122
    assert primary_media["height"] == 1402
    assert primary_media["contentType"] == "image/png"


# -----------------------------------------------------------------------------
# 5.20-TC02: Failure & Security Boundaries
# -----------------------------------------------------------------------------

def test_ssrf_protection_no_outbound_http_probing():
    """Verify remote external URLs are never fetched over HTTP(S) to prevent SSRF."""
    with patch("urllib.request.urlopen") as mock_url:
        w, h, mime = get_image_dimensions("https://malicious.example.com/exploit.png")
        assert not mock_url.called
        assert w is None
        assert h is None
        assert mime == "image/png"

        w, h, mime = get_image_dimensions("http://169.254.169.254/latest/meta-data/")
        assert not mock_url.called
        assert w is None
        assert h is None


def test_directory_traversal_protection():
    """Verify path traversal sequences are rejected and do not read arbitrary filesystem paths."""
    assert _resolve_local_image_path("../../etc/passwd") is None
    assert _resolve_local_image_path("../../../etc/shadow") is None
    assert _resolve_local_image_path("products/../../../etc/hosts") is None
    assert _resolve_local_image_path("/etc/passwd") is None
    assert _resolve_local_image_path("products/test\0file.png") is None

    w, h, mime = get_image_dimensions("../../etc/passwd")
    assert w is None
    assert h is None


def test_unknown_missing_file_fallback():
    """Verify missing or non-existent assets safely yield None for dimensions with frontend-safe fallback."""
    w, h, mime = get_image_dimensions("products/non-existent-item/primary.png")
    assert w is None
    assert h is None
    assert mime == "image/png"

    meta = build_media_metadata("products/non-existent-item/primary.png", alt_text="Placeholder")
    assert meta is not None
    assert meta.width is None
    assert meta.height is None
    assert meta.content_type == "image/png"
    assert meta.alt_text == "Placeholder"


def test_db_product_image_dimensions_persisted():
    """Verify database ProductImage model supports and persists width, height, and content_type."""
    with SessionLocal() as db:
        img = db.query(ProductImage).filter(ProductImage.width.isnot(None)).first()
        if img:
            assert isinstance(img.width, int)
            assert isinstance(img.height, int)
            assert img.content_type == "image/png"


# -----------------------------------------------------------------------------
# 5.11.2-TC01: Real Seeded Hero/Category/Product/Gallery Metadata & Responsive WebP
# -----------------------------------------------------------------------------

def test_tc01_real_hero_and_category_variants():
    """Verify hero, category, and occasion assets resolve real sorted WebP variants with <width>w descriptors."""
    # Hero heritage banner
    hero_variants = get_image_variants("hero/heritage.png")
    assert len(hero_variants) == 5
    assert [v.width for v in hero_variants] == [480, 800, 1200, 1600, 1672]
    assert all(v.content_type == "image/webp" for v in hero_variants)
    assert all(v.descriptor == f"{v.width}w" for v in hero_variants)
    assert all("optimized/hero/heritage" in v.key for v in hero_variants)
    assert all(v.url.startswith("http://localhost:8000/static/images/") for v in hero_variants)

    # Category card
    cat_variants = get_image_variants("categories/amigurumi/card-v2.png")
    assert len(cat_variants) == 5
    assert [v.width for v in cat_variants] == [480, 800, 1200, 1600, 1672]
    assert all(v.content_type == "image/webp" for v in cat_variants)
    assert all(v.descriptor == f"{v.width}w" for v in cat_variants)

    # Product gallery image auto-resolves variants
    gallery_img = ProductImageOut(
        id=1,
        url="products/forever-crochet-rose-bouquet/primary.png",
        is_primary=True,
    )
    assert len(gallery_img.variants) == 3
    assert [v.width for v in gallery_img.variants] == [480, 800, 1122]
    assert all(v.content_type == "image/webp" for v in gallery_img.variants)


# -----------------------------------------------------------------------------
# 5.11.2-TC02: Failure & Security Boundaries for Manifest Loading
# -----------------------------------------------------------------------------

def test_tc02_security_traversal_and_malformed_manifest():
    """Verify traversal keys, external URLs, and malformed manifest contents are safely rejected."""
    # Directory traversal in key returns empty
    assert get_image_variants("../../etc/passwd") == []
    assert get_image_variants("products/../../secret.png") == []
    assert get_image_variants("products/null\0byte.png") == []
    assert get_image_variants("products\\backslash.png") == []

    # External URLs without known prefix return empty (no outbound fetches, SSRF safe)
    with patch("urllib.request.urlopen") as mock_url:
        assert get_image_variants("https://evil.example.com/exploit.png") == []
        assert not mock_url.called

    # Corrupt or invalid JSON manifest fails safely without raising exceptions
    from app.services import media
    with patch.object(media, "_find_manifest_path", return_value=None):
        # Invalidate cache
        media._MANIFEST_CACHE = None
        variants = media.get_image_variants("hero/heritage.png")
        assert variants == []
        assert media.get_media_manifest_hash() == ""

    # Restore cache
    media._MANIFEST_CACHE = None


# -----------------------------------------------------------------------------
# 5.11.2-TC03: Mobile Campaign Independence & Section Schemas
# -----------------------------------------------------------------------------

def test_tc03_mobile_campaign_independence_and_section_metadata():
    """Verify distinct mobile campaign source never substitutes desktop variants, and section schemas carry imageMetadata."""
    # Desktop has variants, distinct mobile has none (e.g. unoptimized admin image)
    campaign = HomepageCampaignOut(
        id=10,
        title="Spring Collection",
        description="Fresh blooms",
        imageUrl="hero/heritage.png",
        imageAlt="Heritage blooms",
        mobileImageUrl="products/custom-mobile-unoptimized.png",
    )
    assert campaign.image_metadata is not None
    assert len(campaign.image_metadata.variants) == 5
    assert campaign.mobile_image_metadata is not None
    # Independent mobile metadata does NOT borrow or substitute desktop variants
    assert campaign.mobile_image_metadata.variants == []
    assert "custom-mobile-unoptimized.png" in campaign.mobile_image_metadata.url

    # OccasionSummary
    occ = OccasionSummary(
        id="birthday",
        name="Birthday Gifting",
        imageUrl="occasions/birthday-gifting-v2.png",
    )
    assert occ.image_metadata is not None
    assert len(occ.image_metadata.variants) == 4
    assert [v.width for v in occ.image_metadata.variants] == [480, 800, 1200, 1448]

    # PromoBannerSectionOut
    promo = PromoBannerSectionOut(
        id=1,
        order=1,
        title="Festive Offer",
        imageUrl="hero/heritage.png",
        imageAlt="Special banner",
    )
    assert promo.image_metadata is not None
    assert len(promo.image_metadata.variants) == 5

    # ImageTextSectionOut
    story = ImageTextSectionOut(
        id=2,
        order=2,
        title="Artisan Story",
        description="Handcrafted with love",
        imageUrl="categories/amigurumi/card-v2.png",
    )
    assert story.image_metadata is not None
    assert len(story.image_metadata.variants) == 5


# -----------------------------------------------------------------------------
# 5.11.2-TC04: Snapshot Version Hash Sensitivity to Media Manifest
# -----------------------------------------------------------------------------

def test_tc04_snapshot_version_sensitivity_to_manifest():
    """Verify that changing the verified manifest content alters the deterministic global snapshot version."""
    with SessionLocal() as db:
        inv = SeoService.get_public_route_inventory(db)
        initial_version = SeoService._compute_global_snapshot_version(db, inv)
        assert len(initial_version) == 16

        # Simulate manifest change via mocked hash
        with patch("app.services.seo.get_media_manifest_hash", return_value="f00ba2c0ffee12345678"):
            altered_version = SeoService._compute_global_snapshot_version(db, inv)
            assert altered_version != initial_version
            assert len(altered_version) == 16

        # All snapshot pages agree on version
        page1 = SeoService.get_content_snapshot(db, page=1, limit=5)
        page2 = SeoService.get_content_snapshot(db, page=2, limit=5)
        assert page1.version_hash == initial_version
        assert page2.version_hash == initial_version



@pytest.mark.parametrize("method", ["GET", "HEAD"])
def test_webp_asset_response_type_and_root_boundary(tmp_path, monkeypatch, method):
    monkeypatch.chdir(tmp_path)
    image_root = tmp_path / "public" / "images"
    image_root.mkdir(parents=True)
    (image_root / "test.webp").write_bytes(b"RIFFtestWEBP")
    private_file = tmp_path / "private.txt"
    private_file.write_text("must remain private")
    (image_root / "outside.webp").symlink_to(private_file)
    with TestClient(app) as browser:
        response = browser.request(method, "/static/images/test.webp")
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/webp"
        if method == "HEAD":
            assert response.content == b""
        for key in ["%2e%2e%2f%2e%2e%2fprivate.txt", "outside.webp", "folder%5cprivate.txt"]:
            response = browser.request(method, f"/static/images/{key}", follow_redirects=False)
            assert response.status_code == 404
            assert b"must remain private" not in response.content
