"""Automated tests for Seasonal Gift by Occasion Admin Configuration & Distinct Artwork.

Covers:
1. Admin Occasions CRUD & multi-occasion product associations.
2. Image key uniqueness validation (rejects duplicate artwork).
3. Public storefront occasion_grid resolution (only enabled & in-season occasions).
4. Hidden Rakhi and off-season occasions (is_enabled=False).
5. Asia/Kolkata timezone schedule filtering (future & expired occasions hidden).
6. Total omission of occasion_grid if no occasions qualify (no empty heading).
7. Single product identity across multiple occasions via GET /api/v1/products?occasion=<id>.
"""

from datetime import datetime, timedelta, timezone
try:
    from zoneinfo import ZoneInfo
    IST = ZoneInfo("Asia/Kolkata")
except Exception:
    IST = timezone(timedelta(hours=5, minutes=30))

from fastapi.testclient import TestClient
import pytest

from app.db.session import SessionLocal
from app.main import app
from app.models.catalogue import Occasion, Product, ProductOccasion
from app.models.storefront import HomepageSection
from app.models.user import User, UserIdentity

client = TestClient(app)


def _login_admin() -> dict[str, str]:
    """Helper to authenticate an admin user."""
    admin_email = "admin_occasions@sulocraft.com"
    with SessionLocal() as db:
        admin = db.query(User).filter(User.email == admin_email).first()
        if not admin:
            admin = User(
                name="Occasions Admin",
                phone="9898989898",
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
        "credential": "mock_admin_token_occ",
        "email": admin_email,
        "name": "Occasions Admin",
        "sub": "admin_sub_occ",
    })
    assert res.status_code == 200
    assert res.json()["user"]["role"] == "ADMIN"
    return dict(res.cookies)


def test_initial_occasions_seeded_with_distinct_artwork_and_hidden_rakhi():
    """Verify initial 9 occasions are active with distinct images, and Rakhi is hidden."""
    with SessionLocal() as db:
        occasions = db.query(Occasion).all()
        occ_map = {o.id: o for o in occasions}

        # 9 required active occasions (4 evergreen + 5 active seasonal)
        required_active = ["birthday", "anniversary", "valentine", "wedding", "decor", "diwali", "mother", "father", "babyshower"]
        for occ_id in required_active:
            assert occ_id in occ_map, f"Missing required occasion {occ_id}"
            assert occ_map[occ_id].is_enabled is True, f"Occasion {occ_id} should be enabled"
            assert occ_map[occ_id].image_key is not None, f"Occasion {occ_id} must have image_key"

        # Check all active occasions have completely distinct image keys
        active_keys = [occ_map[oid].image_key for oid in required_active]
        assert len(active_keys) == len(set(active_keys)), f"Duplicate image keys found: {active_keys}"

        # Evergreen core occasions have v2 artwork and is_evergreen = True
        assert occ_map["birthday"].image_key == "occasions/birthday-gifting-v2.png"
        assert occ_map["anniversary"].image_key == "occasions/anniversary-gifting-v2.png"
        assert occ_map["wedding"].image_key == "occasions/wedding-gifting-v2.png"
        for eid in ["birthday", "anniversary", "wedding", "babyshower"]:
            assert occ_map[eid].is_evergreen is True

        for sid in ["valentine", "decor", "diwali", "mother", "father", "rakhi"]:
            assert occ_map[sid].is_evergreen is False

        # Rakhi must exist but be hidden (is_enabled=False)
        assert "rakhi" in occ_map
        assert occ_map["rakhi"].is_enabled is False, "Rakhi must not be enabled on storefront"


def test_public_storefront_shows_only_active_in_season_occasions():
    """Verify GET /storefront/home returns active occasions in seasonal-first order, never Rakhi."""
    res = client.get("/api/v1/storefront/home")
    assert res.status_code == 200
    data = res.json()

    occ_section = next((s for s in data["sections"] if s["type"] == "occasion_grid"), None)
    assert occ_section is not None, "Occasion grid section should be returned"

    visible_ids = [o["id"] for o in occ_section["occasions"]]
    # Active seasonal occasions lead the grid in admin display order, followed by evergreen occasions
    expected_order = [
        "valentine", "decor", "diwali", "mother", "father",  # Seasonal (display_order 3, 5, 6, 7, 8)
        "birthday", "anniversary", "wedding", "babyshower",   # Evergreen (display_order 1, 2, 4, 10)
    ]
    assert visible_ids == expected_order, f"Expected {expected_order}, got {visible_ids}"

    # Rakhi and off-season must NOT be in the visible grid
    assert "rakhi" not in visible_ids
    assert "housewarming" not in visible_ids
    assert "justbecause" not in visible_ids
    assert "christmas" not in visible_ids

    # Every visible occasion must have a non-empty image URL
    for item in occ_section["occasions"]:
        assert item["imageUrl"], f"Occasion {item['id']} is missing imageUrl"


def test_admin_occasion_crud_and_product_associations():
    """Admin can create, view, update, and delete an occasion with product IDs."""
    cookies = _login_admin()

    # 1. Create a test occasion
    create_payload = {
        "id": "christmas-cheer",
        "name": "Christmas Cheer",
        "icon": "🎄",
        "imageKey": "occasions/christmas-test.jpg",
        "description": "Handcrafted Christmas ornaments and festive keepsakes",
        "displayOrder": 20,
        "isEnabled": False,  # Off-season by default
        "productIds": [1, 3],
    }
    create_res = client.post("/api/v1/admin/occasions", json=create_payload, cookies=cookies)
    assert create_res.status_code == 201
    created = create_res.json()
    assert created["id"] == "christmas-cheer"
    assert created["name"] == "Christmas Cheer"
    assert created["productCount"] == 2
    assert created["productIds"] == [1, 3]

    # 2. Get the created occasion
    get_res = client.get("/api/v1/admin/occasions/christmas-cheer", cookies=cookies)
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "Christmas Cheer"

    # 3. Update occasion (change name, activate, update products)
    update_res = client.put("/api/v1/admin/occasions/christmas-cheer", json={
        "name": "Winter & Christmas",
        "isEnabled": True,
        "productIds": [3, 6],
    }, cookies=cookies)
    assert update_res.status_code == 200
    updated = update_res.json()
    assert updated["name"] == "Winter & Christmas"
    assert updated["isEnabled"] is True
    assert updated["productIds"] == [3, 6]

    # 4. Delete the test occasion
    del_res = client.delete("/api/v1/admin/occasions/christmas-cheer", cookies=cookies)
    assert del_res.status_code == 200
    assert client.get("/api/v1/admin/occasions/christmas-cheer", cookies=cookies).status_code == 404


def test_admin_rejects_duplicate_image_key():
    """Admin cannot assign an image key already used by another occasion."""
    cookies = _login_admin()

    # Clean up duplicate-birthday if left over from previous run
    client.delete("/api/v1/admin/occasions/duplicate-birthday", cookies=cookies)

    # Try to create an occasion with birthday's current v2 image key
    res = client.post("/api/v1/admin/occasions", json={
        "id": "duplicate-birthday",
        "name": "Duplicate Birthday",
        "imageKey": "occasions/birthday-gifting-v2.png",
    }, cookies=cookies)
    assert res.status_code == 400
    assert "already assigned" in res.json()["detail"]

    # Try to update anniversary to wedding's current v2 image key
    update_res = client.put("/api/v1/admin/occasions/anniversary", json={
        "imageKey": "occasions/wedding-gifting-v2.png",
    }, cookies=cookies)
    assert update_res.status_code == 400
    assert "already assigned" in update_res.json()["detail"]


def test_seasonal_schedule_boundaries_in_asia_kolkata():
    """Test that future and past occasions are excluded based on Asia/Kolkata boundaries."""
    cookies = _login_admin()
    now_ist = datetime.now(IST)

    # 1. Create a future seasonal occasion (e.g. starts 5 days from now)
    future_start = now_ist + timedelta(days=5)
    future_end = now_ist + timedelta(days=20)
    client.post("/api/v1/admin/occasions", json={
        "id": "new-year-special",
        "name": "New Year Special",
        "imageKey": "occasions/newyear-test.jpg",
        "displayOrder": 15,
        "isEnabled": True,
        "startsAt": future_start.isoformat(),
        "endsAt": future_end.isoformat(),
    }, cookies=cookies)

    # 2. Create an expired seasonal occasion (ended 2 days ago)
    past_start = now_ist - timedelta(days=10)
    past_end = now_ist - timedelta(days=2)
    client.post("/api/v1/admin/occasions", json={
        "id": "summer-fest",
        "name": "Summer Fest",
        "imageKey": "occasions/summer-test.jpg",
        "displayOrder": 16,
        "isEnabled": True,
        "startsAt": past_start.isoformat(),
        "endsAt": past_end.isoformat(),
    }, cookies=cookies)

    # 3. Create a currently active in-season occasion
    active_start = now_ist - timedelta(days=2)
    active_end = now_ist + timedelta(days=10)
    client.post("/api/v1/admin/occasions", json={
        "id": "festive-in-season",
        "name": "Festive In Season",
        "imageKey": "occasions/inseason-test.jpg",
        "displayOrder": 17,
        "isEnabled": True,
        "startsAt": active_start.isoformat(),
        "endsAt": active_end.isoformat(),
    }, cookies=cookies)

    try:
        # Check public storefront
        res = client.get("/api/v1/storefront/home")
        assert res.status_code == 200
        occ_section = next(s for s in res.json()["sections"] if s["type"] == "occasion_grid")
        ids = [o["id"] for o in occ_section["occasions"]]

        # Future and expired must NOT appear
        assert "new-year-special" not in ids
        assert "summer-fest" not in ids

        # Currently active in-season MUST appear
        assert "festive-in-season" in ids

        # Check public GET /api/v1/occasions
        occ_res = client.get("/api/v1/occasions")
        assert occ_res.status_code == 200
        pub_ids = [o["id"] for o in occ_res.json()]
        assert "new-year-special" not in pub_ids
        assert "summer-fest" not in pub_ids
        assert "festive-in-season" in pub_ids
    finally:
        # Cleanup
        client.delete("/api/v1/admin/occasions/new-year-special", cookies=cookies)
        client.delete("/api/v1/admin/occasions/summer-fest", cookies=cookies)
        client.delete("/api/v1/admin/occasions/festive-in-season", cookies=cookies)


def test_omits_occasion_grid_section_when_none_qualify():
    """When no occasions qualify (e.g. no distinct images or all occasions removed), occasion_grid is omitted."""
    cookies = _login_admin()
    with SessionLocal() as db:
        # Temporarily clear occasion image keys and urls
        db.query(Occasion).update({"image_key": None, "_legacy_image_url": None})
        db.commit()

    try:
        res = client.get("/api/v1/storefront/home")
        assert res.status_code == 200
        section_types = [s["type"] for s in res.json()["sections"]]
        assert "occasion_grid" not in section_types, "Empty occasion grid must be omitted entirely"
    finally:
        # Restore active occasions using seed_catalogue
        from app.db.seed import seed_catalogue
        with SessionLocal() as db:
            seed_catalogue(db)


def test_multi_occasion_product_associations_and_filter():
    """Verify single product identity across multiple occasions and GET /products?occasion=<id>."""
    # Product 1 (Forever Crochet Rose Bouquet) should belong to Anniversary and Valentine's Day
    res_bday = client.get("/api/v1/products?occasion=birthday")
    assert res_bday.status_code == 200
    bday_prods = res_bday.json()
    bday_ids = [p["id"] for p in bday_prods]
    assert 3 in bday_ids, "Heart bear (id 3) should be in birthday"

    res_val = client.get("/api/v1/products?occasion=valentine")
    assert res_val.status_code == 200
    val_prods = res_val.json()
    val_ids = [p["id"] for p in val_prods]
    assert 3 in val_ids, "Heart bear (id 3) should also be in valentine"
    assert 1 in val_ids, "Forever Crochet Rose Bouquet (id 1) should be in valentine"

    res_anniv = client.get("/api/v1/products?occasion=anniversary")
    assert res_anniv.status_code == 200
    anniv_prods = res_anniv.json()
    anniv_ids = [p["id"] for p in anniv_prods]
    assert 1 in anniv_ids, "Forever Crochet Rose Bouquet (id 1) should also be in anniversary"

    # Verify single product row identity (same SKU, same product ID)
    rose_val = next(p for p in val_prods if p["id"] == 1)
    rose_anniv = next(p for p in anniv_prods if p["id"] == 1)
    assert rose_val["id"] == rose_anniv["id"]
    assert rose_val["slug"] == rose_anniv["slug"]

    # Verify occasions and tags include associated occasions for frontend client filtering
    assert "valentine" in rose_val["occasions"]
    assert "anniversary" in rose_val["occasions"]
    assert "valentine" in rose_val["tags"]
    assert "anniversary" in rose_val["tags"]


def test_seed_repair_idempotence():
    """Verify seed_storefront_content and seed_catalogue are fully idempotent when run repeatedly."""
    from app.db.seed import seed_catalogue, seed_storefront_content
    with SessionLocal() as db:
        # Run multiple times to verify no unique constraint or primary key collisions occur
        seed_storefront_content(db)
        seed_storefront_content(db)
        seed_catalogue(db)
        seed_catalogue(db)


def test_evergreen_occasions_cannot_be_disabled_scheduled_or_deleted():
    """Evergreen occasions (birthday, anniversary, wedding, babyshower) reject disable, schedule, and delete."""
    cookies = _login_admin()

    # 1. Attempt to disable an evergreen occasion
    res_disable = client.put("/api/v1/admin/occasions/birthday", json={"isEnabled": False}, cookies=cookies)
    assert res_disable.status_code == 400
    assert "Evergreen occasions cannot be disabled" in res_disable.json()["detail"]

    # 2. Attempt to schedule dates on an evergreen occasion
    now_ist = datetime.now(IST)
    res_schedule = client.patch(
        "/api/v1/admin/occasions/wedding",
        json={"startsAt": (now_ist + timedelta(days=1)).isoformat()},
        cookies=cookies,
    )
    assert res_schedule.status_code == 400
    assert "Evergreen occasions cannot have seasonal schedule dates" in res_schedule.json()["detail"]

    # 3. Attempt to delete an evergreen occasion
    res_del_anniv = client.delete("/api/v1/admin/occasions/anniversary", cookies=cookies)
    assert res_del_anniv.status_code == 400
    assert "Evergreen occasions cannot be deleted" in res_del_anniv.json()["detail"]

    res_del_baby = client.delete("/api/v1/admin/occasions/babyshower", cookies=cookies)
    assert res_del_baby.status_code == 400
    assert "Evergreen occasions cannot be deleted" in res_del_baby.json()["detail"]


def test_clearing_seasonal_dates_with_null():
    """Admin can clear seasonal startsAt and endsAt by explicitly providing null."""
    cookies = _login_admin()
    now_ist = datetime.now(IST)

    # First set dates on seasonal 'decor'
    res_set = client.patch(
        "/api/v1/admin/occasions/decor",
        json={
            "startsAt": (now_ist - timedelta(days=1)).isoformat(),
            "endsAt": (now_ist + timedelta(days=10)).isoformat(),
        },
        cookies=cookies,
    )
    assert res_set.status_code == 200
    assert res_set.json()["startsAt"] is not None
    assert res_set.json()["endsAt"] is not None

    # Now clear dates by sending null
    res_clear = client.patch(
        "/api/v1/admin/occasions/decor",
        json={"startsAt": None, "endsAt": None},
        cookies=cookies,
    )
    assert res_clear.status_code == 200
    assert res_clear.json()["startsAt"] is None
    assert res_clear.json()["endsAt"] is None


def test_seasonal_first_grid_ordering_and_enable_disable_transitions():
    """Active seasonal occasions appear before evergreen cards; enable/disable moves items in/out."""
    cookies = _login_admin()

    try:
        # Initial state: valentine is enabled and in season, leads the grid
        res1 = client.get("/api/v1/storefront/home")
        occ1 = next(s for s in res1.json()["sections"] if s["type"] == "occasion_grid")
        ids1 = [o["id"] for o in occ1["occasions"]]
        assert ids1[0] == "valentine"
        assert "birthday" in ids1

        # Disable valentine
        res_dis = client.patch("/api/v1/admin/occasions/valentine", json={"isEnabled": False}, cookies=cookies)
        assert res_dis.status_code == 200
        assert res_dis.json()["isEnabled"] is False

        # Now valentine is omitted, and decor (next seasonal) leads
        res2 = client.get("/api/v1/storefront/home")
        occ2 = next(s for s in res2.json()["sections"] if s["type"] == "occasion_grid")
        ids2 = [o["id"] for o in occ2["occasions"]]
        assert "valentine" not in ids2
        assert ids2[0] == "decor"
        # 4 evergreen occasions are still present
        for eid in ["birthday", "anniversary", "wedding", "babyshower"]:
            assert eid in ids2
    finally:
        # Re-enable valentine
        client.patch("/api/v1/admin/occasions/valentine", json={"isEnabled": True}, cookies=cookies)


def test_babyshower_product_associations_and_filtering():
    """Verify babyshower is linked to baby products and searchable via GET /products?occasion=babyshower."""
    res = client.get("/api/v1/products?occasion=babyshower")
    assert res.status_code == 200
    products = res.json()
    product_ids = [p["id"] for p in products]
    assert len(product_ids) >= 2
    # Should include Baby Gift Hamper (id 17) and Baby Blanket (id 19)
    assert 17 in product_ids, "Baby Gift Hamper (id 17) should be linked to babyshower"
    assert 19 in product_ids, "Handmade Crochet Baby Blanket (id 19) should be linked to babyshower"


def test_seed_preserves_admin_edits_and_repairs_evergreen():
    """Repeat seed execution preserves admin modifications while keeping evergreen occasions enabled."""
    cookies = _login_admin()
    from app.db.seed import seed_catalogue

    # Custom admin update on seasonal 'diwali'
    custom_desc = "Admin custom Diwali artisanal illumination gift description"
    client.patch("/api/v1/admin/occasions/diwali", json={"description": custom_desc}, cookies=cookies)

    with SessionLocal() as db:
        # Re-run catalogue seed
        seed_catalogue(db)

    # Verify custom description was preserved
    res = client.get("/api/v1/admin/occasions/diwali", cookies=cookies)
    assert res.status_code == 200
    assert res.json()["description"] == custom_desc

    # Verify evergreen occasions are all enabled with v2 artwork
    with SessionLocal() as db:
        for eid in ["birthday", "anniversary", "wedding", "babyshower"]:
            occ = db.query(Occasion).filter_by(id=eid).first()
            assert occ.is_enabled is True
            assert occ.starts_at is None
            assert occ.ends_at is None
            assert occ.is_evergreen is True
            if eid in {"birthday", "anniversary", "wedding"}:
                assert "-v2.png" in occ.image_key


