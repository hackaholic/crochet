"""Automated tests for Storefront content & campaigns API conforming to docs/api-storefront.md."""

from datetime import datetime, timedelta, timezone
import pytest
from fastapi.testclient import TestClient

from app.db.seed import seed_catalogue
from app.db.session import SessionLocal
from app.main import app
from app.models.storefront import BrandSettings, HomepageCampaign
from app.models.user import User, UserIdentity

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_storefront():
    """Ensure database has seed data prior to running storefront tests."""
    with SessionLocal() as db:
        seed_catalogue(db)


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

    res = client.post("/api/v1/auth/google", json={
        "credential": "mock_admin_token_storefront",
        "email": admin_email,
        "name": "Store Admin",
        "sub": "admin_sub_storefront",
    })
    assert res.status_code == 200
    assert res.json()["user"]["role"] == "ADMIN"
    return dict(res.cookies)


def _login_customer(phone: str = "9999911001") -> dict[str, str]:
    """Helper to authenticate a customer."""
    email = f"customer_{phone}@example.com"
    res = client.post("/api/v1/auth/google", json={
        "credential": f"mock_cust_{phone}",
        "email": email,
        "name": "Customer User",
        "sub": f"sub_{phone}",
    })
    assert res.status_code == 200
    return dict(res.cookies)


def test_get_public_storefront_returns_brand_and_seeded_campaigns():
    """Verify GET /api/v1/storefront returns public brand profile and 5 active hero campaigns."""
    response = client.get("/api/v1/storefront")
    assert response.status_code == 200
    data = response.json()

    # Brand checks
    assert "brand" in data
    assert data["brand"]["name"] == "Sulocraft"
    assert data["brand"]["ownerName"] == "Anupama Sharma"
    assert "instagramUrl" in data["brand"]
    assert "whatsappUrl" in data["brand"]

    # Campaign checks
    assert "heroCampaigns" in data
    campaigns = data["heroCampaigns"]
    assert len(campaigns) == 5

    first = campaigns[0]
    assert first["title"] == "Rooted in Warmth, Woven by Hand"
    assert first["priority"] == 1
    assert first["destination"] == "/about"
    assert "imageUrl" in first
    assert "imageAlt" in first


def test_storefront_active_and_schedule_filtering():
    """Verify inactive and out-of-schedule campaigns are omitted from the public storefront."""
    with SessionLocal() as db:
        now = datetime.now(timezone.utc)
        # 1. Inactive campaign
        c_inactive = HomepageCampaign(
            title="Inactive Campaign",
            description="Should not appear",
            image_url="https://images.sulocraft.com/test.jpg",
            image_alt="Test",
            priority=0,
            is_active=False,
        )
        # 2. Future campaign
        c_future = HomepageCampaign(
            title="Future Campaign",
            description="Starts tomorrow",
            image_url="https://images.sulocraft.com/test.jpg",
            image_alt="Test",
            priority=0,
            is_active=True,
            starts_at=now + timedelta(days=1),
        )
        # 3. Expired campaign
        c_expired = HomepageCampaign(
            title="Expired Campaign",
            description="Ended yesterday",
            image_url="https://images.sulocraft.com/test.jpg",
            image_alt="Test",
            priority=0,
            is_active=True,
            ends_at=now - timedelta(days=1),
        )
        db.add_all([c_inactive, c_future, c_expired])
        db.commit()
        inactive_id = c_inactive.id
        future_id = c_future.id
        expired_id = c_expired.id

    try:
        response = client.get("/api/v1/storefront")
        assert response.status_code == 200
        active_ids = [c["id"] for c in response.json()["heroCampaigns"]]
        assert inactive_id not in active_ids
        assert future_id not in active_ids
        assert expired_id not in active_ids
    finally:
        with SessionLocal() as db:
            db.query(HomepageCampaign).filter(
                HomepageCampaign.id.in_([inactive_id, future_id, expired_id])
            ).delete(synchronize_session=False)
            db.commit()


def test_admin_get_and_update_brand_settings():
    """Verify admin can view and update brand settings."""
    admin_cookies = _login_admin("9999900000")

    # GET
    res = client.get("/api/v1/admin/storefront/brand", cookies=admin_cookies)
    assert res.status_code == 200
    assert res.json()["name"] == "Sulocraft"
    assert res.json()["ownerName"] == "Anupama Sharma"

    # PUT
    update_res = client.put(
        "/api/v1/admin/storefront/brand",
        cookies=admin_cookies,
        json={
            "name": "Sulocraft Artisans",
            "ownerName": "Anupama Roy",
            "instagramUrl": "https://instagram.com/sulocraft.artisans",
        },
    )
    assert update_res.status_code == 200
    data = update_res.json()
    assert data["name"] == "Sulocraft Artisans"
    assert data["ownerName"] == "Anupama Roy"
    assert data["instagramUrl"] == "https://instagram.com/sulocraft.artisans"

    # Reset back to default
    client.put(
        "/api/v1/admin/storefront/brand",
        cookies=admin_cookies,
        json={"name": "Sulocraft", "ownerName": "Anupama Sharma", "instagramUrl": "https://instagram.com/sulocraft"},
    )


def test_admin_campaign_crud():
    """Verify admin can create, update, list, and delete homepage campaigns."""
    admin_cookies = _login_admin("9999900000")

    # 1. Create
    create_payload = {
        "title": "Summer Bloom Festival",
        "emphasis": "Limited Edition",
        "description": "Exclusive sunflower collection for sunny days.",
        "eyebrow": "Seasonal Spotlight",
        "imageUrl": "https://images.sulocraft.com/sunflowers.jpg",
        "imageAlt": "Sunflowers in crochet vase",
        "destination": "/shop?category=Flowers",
        "priority": 10,
        "isActive": True,
    }
    create_res = client.post("/api/v1/admin/storefront/campaigns", cookies=admin_cookies, json=create_payload)
    assert create_res.status_code == 201
    created_data = create_res.json()
    campaign_id = created_data["id"]
    assert created_data["title"] == "Summer Bloom Festival"
    assert created_data["priority"] == 10
    assert created_data["isActive"] is True

    # 2. List
    list_res = client.get("/api/v1/admin/storefront/campaigns", cookies=admin_cookies)
    assert list_res.status_code == 200
    campaign_ids = [c["id"] for c in list_res.json()]
    assert campaign_id in campaign_ids

    # 3. Update
    update_res = client.put(
        f"/api/v1/admin/storefront/campaigns/{campaign_id}",
        cookies=admin_cookies,
        json={"title": "Updated Summer Bloom Festival", "priority": 12, "isActive": False},
    )
    assert update_res.status_code == 200
    assert update_res.json()["title"] == "Updated Summer Bloom Festival"
    assert update_res.json()["priority"] == 12
    assert update_res.json()["isActive"] is False

    # 4. Delete
    delete_res = client.delete(f"/api/v1/admin/storefront/campaigns/{campaign_id}", cookies=admin_cookies)
    assert delete_res.status_code == 200
    assert delete_res.json()["status"] == "ok"


def test_admin_storefront_unauthorized_forbidden():
    """Verify unauthenticated calls return 401 and customer calls return 403."""
    # Unauthenticated
    unauth_res = client.get("/api/v1/admin/storefront/brand")
    assert unauth_res.status_code == 401

    # Customer forbidden
    cust_cookies = _login_customer("9999911002")
    forbidden_res = client.get("/api/v1/admin/storefront/brand", cookies=cust_cookies)
    assert forbidden_res.status_code == 403


def test_get_storefront_home_returns_brand_hero_and_resolved_sections():
    """Verify GET /api/v1/storefront/home returns brand, hero, and all 5 resolved sections."""
    response = client.get("/api/v1/storefront/home")
    assert response.status_code == 200
    data = response.json()

    assert "brand" in data
    assert data["brand"]["name"] == "Sulocraft"
    assert data["brand"]["ownerName"] == "Anupama Sharma"

    assert "hero" in data
    assert len(data["hero"]) >= 1
    assert "heroCampaigns" in data

    assert "sections" in data
    sections = data["sections"]
    assert len(sections) >= 5

    section_types = [s["type"] for s in sections]
    assert "category_grid" in section_types
    assert "product_collection" in section_types
    assert "promo_banner" in section_types
    assert "review_section" in section_types
    assert "image_text" in section_types

    # 1. Category Grid verification
    cg = next(s for s in sections if s["type"] == "category_grid")
    assert cg["order"] == 1
    assert cg["enabled"] is True
    assert cg["title"] == "Shop by Category"
    assert len(cg["categories"]) > 0
    cat0 = cg["categories"][0]
    assert "id" in cat0
    assert "name" in cat0
    assert "slug" in cat0
    assert "imageUrl" in cat0

    # 2. Product Collection verification
    pc = next(s for s in sections if s["type"] == "product_collection")
    assert pc["order"] == 2
    assert pc["enabled"] is True
    assert pc["title"] == "Most Loved Creations"
    assert pc["collectionSlug"] == "bestsellers"
    assert len(pc["products"]) > 0
    prod0 = pc["products"][0]
    assert "id" in prod0
    assert "name" in prod0
    assert "price" in prod0
    assert "rating" in prod0

    # 3. Promo Banner verification
    pb = next(s for s in sections if s["type"] == "promo_banner")
    assert pb["order"] == 3
    assert pb["enabled"] is True
    assert pb["title"] == "Gift Handcrafted Warmth This Season"
    assert "imageUrl" in pb
    assert "ctaText" in pb
    assert "ctaUrl" in pb

    # 4. Review Section verification
    rs = next(s for s in sections if s["type"] == "review_section")
    assert rs["order"] == 4
    assert rs["enabled"] is True
    assert len(rs["reviews"]) > 0
    rev0 = rs["reviews"][0]
    assert "authorName" in rev0
    assert "rating" in rev0
    assert "text" in rev0

    # 5. Image Text verification
    it = next(s for s in sections if s["type"] == "image_text")
    assert it["order"] == 5
    assert it["enabled"] is True
    assert it["title"] == "Handmade with Love, Thread by Thread"
    assert "description" in it
    assert "imageUrl" in it
    assert it["imagePosition"] in ("left", "right")


def test_storefront_home_section_scheduling_and_disabled_filtering():
    """Verify disabled and out-of-schedule sections are excluded from /storefront/home."""
    from app.models.storefront import HomepageSection

    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        # 1. Disabled section
        s_disabled = HomepageSection(
            section_type="promo_banner",
            title="Disabled Section",
            display_order=100,
            is_enabled=False,
        )
        # 2. Future section
        s_future = HomepageSection(
            section_type="promo_banner",
            title="Future Section",
            display_order=101,
            is_enabled=True,
            starts_at=now + timedelta(days=2),
        )
        # 3. Expired section
        s_expired = HomepageSection(
            section_type="promo_banner",
            title="Expired Section",
            display_order=102,
            is_enabled=True,
            ends_at=now - timedelta(days=2),
        )
        db.add_all([s_disabled, s_future, s_expired])
        db.commit()
        disabled_id = s_disabled.id
        future_id = s_future.id
        expired_id = s_expired.id

    try:
        response = client.get("/api/v1/storefront/home")
        assert response.status_code == 200
        sec_ids = [s["id"] for s in response.json()["sections"]]
        assert disabled_id not in sec_ids
        assert future_id not in sec_ids
        assert expired_id not in sec_ids
    finally:
        with SessionLocal() as db:
            db.query(HomepageSection).filter(
                HomepageSection.id.in_([disabled_id, future_id, expired_id])
            ).delete(synchronize_session=False)
            db.commit()


def test_admin_section_crud():
    """Verify admin can create, read, update, list, and delete homepage sections."""
    admin_cookies = _login_admin("9999900000")

    # 1. Create with invalid type -> 422
    invalid_res = client.post(
        "/api/v1/admin/storefront/sections",
        cookies=admin_cookies,
        json={"sectionType": "invalid_random_type", "title": "Bad Section"},
    )
    assert invalid_res.status_code == 422

    # 2. Create valid section
    create_payload = {
        "sectionType": "promo_banner",
        "title": "Festive Flash Sale",
        "description": "20% off all crochet bouquets this weekend only.",
        "imageUrl": "https://images.sulocraft.com/sale.jpg",
        "imageAlt": "Festive bouquets sale",
        "ctaText": "Shop Sale",
        "ctaUrl": "/shop?sale=true",
        "displayOrder": 10,
        "isEnabled": True,
    }
    create_res = client.post(
        "/api/v1/admin/storefront/sections",
        cookies=admin_cookies,
        json=create_payload,
    )
    assert create_res.status_code == 201
    section_data = create_res.json()
    section_id = section_data["id"]
    assert section_data["sectionType"] == "promo_banner"
    assert section_data["title"] == "Festive Flash Sale"
    assert section_data["displayOrder"] == 10
    assert section_data["isEnabled"] is True

    # 3. Get section detail
    get_res = client.get(f"/api/v1/admin/storefront/sections/{section_id}", cookies=admin_cookies)
    assert get_res.status_code == 200
    assert get_res.json()["title"] == "Festive Flash Sale"

    # 4. List sections
    list_res = client.get("/api/v1/admin/storefront/sections", cookies=admin_cookies)
    assert list_res.status_code == 200
    ids = [s["id"] for s in list_res.json()]
    assert section_id in ids

    # 5. Update section
    update_res = client.put(
        f"/api/v1/admin/storefront/sections/{section_id}",
        cookies=admin_cookies,
        json={"title": "Updated Flash Sale", "displayOrder": 15, "isEnabled": False},
    )
    assert update_res.status_code == 200
    assert update_res.json()["title"] == "Updated Flash Sale"
    assert update_res.json()["displayOrder"] == 15
    assert update_res.json()["isEnabled"] is False

    # 6. Delete section
    del_res = client.delete(f"/api/v1/admin/storefront/sections/{section_id}", cookies=admin_cookies)
    assert del_res.status_code == 200
    assert del_res.json()["status"] == "ok"

    # Verify 404 after deletion
    get_after_res = client.get(f"/api/v1/admin/storefront/sections/{section_id}", cookies=admin_cookies)
    assert get_after_res.status_code == 404


def test_admin_section_unauthorized_forbidden():
    """Verify unauthenticated calls return 401 and customer calls return 403 on admin section routes."""
    # Unauthenticated
    unauth_res = client.get("/api/v1/admin/storefront/sections")
    assert unauth_res.status_code == 401

    # Customer forbidden
    cust_cookies = _login_customer("9999911003")
    forbidden_res = client.get("/api/v1/admin/storefront/sections", cookies=cust_cookies)
    assert forbidden_res.status_code == 403


def test_root_status_endpoint():
    """Verify GET / returns online status with docs and health links."""
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "online"
    assert data["service"] == "Sulocraft API"
    assert "docs" in data
    assert "health" in data


def test_static_image_redirect_resolver():
    """Verify GET /static/images/{path} redirects to mock/high-res photography."""
    # Known product image
    res = client.get("/static/images/products/forever-crochet-rose-bouquet/primary.jpg", follow_redirects=False)
    assert res.status_code == 307
    assert "location" in res.headers
    assert "images.unsplash.com" in res.headers["location"]

    # Unknown path falls back gracefully
    fallback_res = client.get("/static/images/unknown/path.jpg", follow_redirects=False)
    assert fallback_res.status_code == 307
    assert "location" in fallback_res.headers


