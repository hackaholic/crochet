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


def _login_customer(phone: str = "9999911001") -> dict[str, str]:
    """Helper to authenticate a customer."""
    send_res = client.post("/api/v1/auth/phone/send-otp", json={"phone": phone})
    assert send_res.status_code == 200
    otp = send_res.json().get("devOtp") or "123456"
    res = client.post("/api/v1/auth/phone/verify-otp", json={"phone": phone, "otp": otp})
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
    assert data["brand"]["ownerName"] == "Anupama"
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
    assert res.json()["ownerName"] == "Anupama"

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
        json={"name": "Sulocraft", "ownerName": "Anupama", "instagramUrl": "https://instagram.com/sulocraft"},
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
