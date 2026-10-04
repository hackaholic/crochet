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
    """Verify exactly 5 initial occasions are active with distinct Sulocraft artwork, and remaining 8 are disabled (DEC-010-010)."""
    with SessionLocal() as db:
        occasions = db.query(Occasion).all()
        occ_map = {o.id: o for o in occasions}

        # 5 required active default occasions
        required_active = ["birthday", "justbecause", "anniversary", "babyshower", "wedding"]
        for occ_id in required_active:
            assert occ_id in occ_map, f"Missing required occasion {occ_id}"
            assert occ_map[occ_id].is_enabled is True, f"Occasion {occ_id} should be enabled by default"
            assert occ_map[occ_id].image_key is not None, f"Occasion {occ_id} must have image_key"

        # Check all 13 occasions exist and have completely distinct image keys
        assert len(occasions) == 13
        all_keys = [o.image_key for o in occasions]
        assert len(all_keys) == len(set(all_keys)), f"Duplicate image keys found: {all_keys}"

        # Distinct Sulocraft artwork paths
        assert occ_map["birthday"].image_key == "occasions/birthday-gifting-v2.png"
        assert occ_map["justbecause"].image_key == "occasions/just-because-gifting.png"
        assert occ_map["anniversary"].image_key == "occasions/anniversary-gifting-v2.png"
        assert occ_map["babyshower"].image_key == "occasions/baby-shower-hamper.png"
        assert occ_map["wedding"].image_key == "occasions/wedding-gifting-v2.png"

        # Remaining 8 occasions must be disabled by default (DEC-010-010)
        disabled_defaults = ["valentine", "decor", "diwali", "mother", "father", "rakhi", "housewarming", "christmas"]
        for dis_id in disabled_defaults:
            assert dis_id in occ_map, f"Missing occasion {dis_id}"
            assert occ_map[dis_id].is_enabled is False, f"Occasion {dis_id} must be disabled by default"


def test_public_storefront_shows_only_active_in_season_occasions():
    """Verify GET /storefront/home returns exactly the 5 enabled default occasions in admin display order."""
    res = client.get("/api/v1/storefront/home")
    assert res.status_code == 200
    data = res.json()

    occ_section = next((s for s in data["sections"] if s["type"] == "occasion_grid"), None)
    assert occ_section is not None, "Occasion grid section should be returned"

    visible_ids = [o["id"] for o in occ_section["occasions"]]
    expected_order = ["birthday", "justbecause", "anniversary", "babyshower", "wedding"]
    assert visible_ids == expected_order, f"Expected {expected_order}, got {visible_ids}"

    # Disabled occasions must NOT be in the visible grid
    for dis_id in ["valentine", "decor", "diwali", "mother", "father", "rakhi", "housewarming", "christmas"]:
        assert dis_id not in visible_ids

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
    from app.db.seed import (
        PRODUCT_OCCASIONS_MAP,
        PRODUCTS_DATA,
        reseed_catalogue,
        seed_catalogue,
        seed_product_occasions,
        seed_storefront_content,
    )
    with SessionLocal() as db:
        # Run multiple times to verify no unique constraint or primary key collisions occur
        seed_storefront_content(db)
        seed_storefront_content(db)
        seed_catalogue(db)
        seed_catalogue(db)

        # Verify all product occasion associations and display order match PRODUCT_OCCASIONS_MAP
        valid_pids = {p["id"] for p in PRODUCTS_DATA}
        for occ_id, expected_pids in PRODUCT_OCCASIONS_MAP.items():
            assocs = (
                db.query(ProductOccasion)
                .filter_by(occasion_id=occ_id)
                .order_by(ProductOccasion.display_order.asc())
                .all()
            )
            actual_pids = [a.product_id for a in assocs]
            expected_filtered = [pid for pid in expected_pids if pid in valid_pids]
            assert actual_pids == expected_filtered
            for idx, a in enumerate(assocs):
                assert a.display_order == idx

        # Test updating an existing association's display_order: reseed repairs it idempotently
        first_assoc = db.query(ProductOccasion).first()
        assert first_assoc is not None
        original_order = first_assoc.display_order
        first_assoc.display_order = 999
        db.commit()

        seed_product_occasions(db)
        db.commit()

        db.refresh(first_assoc)
        assert first_assoc.display_order == original_order

        # Reseed catalogue clears and restores cleanly
        reseed_catalogue(db)


def test_fresh_database_seed_idempotency_isolated():
    """Verify a clean, fresh database seeds successfully and repeated runs preserve associations."""
    import tempfile
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.db.base import Base
    import app.models  # noqa: F401
    from app.db.seed import PRODUCT_OCCASIONS_MAP, PRODUCTS_DATA, seed_catalogue, seed_storefront_content

    with tempfile.NamedTemporaryFile(suffix=".db") as tmp:
        db_url = f"sqlite:///{tmp.name}"
        test_engine = create_engine(db_url)
        Base.metadata.create_all(bind=test_engine)
        TestSession = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)

        # 1. Fresh database seed completes cleanly
        with TestSession() as s:
            seed_catalogue(s)

        # 2. Repeated seed execution on fresh database succeeds idempotently
        with TestSession() as s:
            seed_catalogue(s)
            seed_storefront_content(s)

        # 3. Verify associations and ordering are preserved
        with TestSession() as s:
            valid_pids = {p["id"] for p in PRODUCTS_DATA}
            for occ_id, expected_pids in PRODUCT_OCCASIONS_MAP.items():
                assocs = (
                    s.query(ProductOccasion)
                    .filter_by(occasion_id=occ_id)
                    .order_by(ProductOccasion.display_order.asc())
                    .all()
                )
                actual_pids = [a.product_id for a in assocs]
                expected_filtered = [pid for pid in expected_pids if pid in valid_pids]
                assert actual_pids == expected_filtered
                for idx, a in enumerate(assocs):
                    assert a.display_order == idx



def test_all_occasions_admin_toggleable_and_core_protected_from_deletion():
    """All occasions can be enabled/disabled and scheduled by admin; core initial occasions cannot be deleted."""
    cookies = _login_admin()

    try:
        # 1. Admin can disable an initial occasion (e.g. birthday)
        res_disable = client.put("/api/v1/admin/occasions/birthday", json={"isEnabled": False}, cookies=cookies)
        assert res_disable.status_code == 200
        assert res_disable.json()["isEnabled"] is False

        # 2. Admin can schedule dates on an initial occasion (e.g. wedding)
        now_ist = datetime.now(IST)
        res_schedule = client.patch(
            "/api/v1/admin/occasions/wedding",
            json={"startsAt": (now_ist + timedelta(days=1)).isoformat()},
            cookies=cookies,
        )
        assert res_schedule.status_code == 200
        assert res_schedule.json()["startsAt"] is not None

        # 3. Core initial occasions reject deletion to protect catalogue integrity
        for core_id in ["birthday", "justbecause", "anniversary", "babyshower", "wedding"]:
            res_del = client.delete(f"/api/v1/admin/occasions/{core_id}", cookies=cookies)
            assert res_del.status_code == 400
            assert "Core initial occasions cannot be deleted" in res_del.json()["detail"]
    finally:
        # Restore birthday enabled and wedding schedule
        client.put("/api/v1/admin/occasions/birthday", json={"isEnabled": True}, cookies=cookies)
        client.patch("/api/v1/admin/occasions/wedding", json={"startsAt": None, "endsAt": None}, cookies=cookies)


def test_clearing_seasonal_dates_with_null():
    """Admin can clear startsAt and endsAt on any occasion by explicitly providing null."""
    cookies = _login_admin()
    now_ist = datetime.now(IST)

    # First set dates on 'decor'
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


def test_admin_toggle_and_display_order_transitions():
    """Storefront occasion grid displays enabled occasions in admin display order; toggling updates visibility."""
    cookies = _login_admin()

    try:
        # Initial state: 5 enabled defaults in order
        res1 = client.get("/api/v1/storefront/home")
        occ1 = next(s for s in res1.json()["sections"] if s["type"] == "occasion_grid")
        ids1 = [o["id"] for o in occ1["occasions"]]
        assert ids1 == ["birthday", "justbecause", "anniversary", "babyshower", "wedding"]

        # Admin enables diwali
        res_en = client.patch("/api/v1/admin/occasions/diwali", json={"isEnabled": True}, cookies=cookies)
        assert res_en.status_code == 200
        assert res_en.json()["isEnabled"] is True

        # Now diwali appears in the storefront occasion grid in its display order
        res2 = client.get("/api/v1/storefront/home")
        occ2 = next(s for s in res2.json()["sections"] if s["type"] == "occasion_grid")
        ids2 = [o["id"] for o in occ2["occasions"]]
        assert "diwali" in ids2
        assert ids2 == ["birthday", "justbecause", "anniversary", "babyshower", "wedding", "diwali"]
    finally:
        # Disable diwali again
        client.patch("/api/v1/admin/occasions/diwali", json={"isEnabled": False}, cookies=cookies)


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


def test_seed_preserves_admin_edits_and_repairs_occasions():
    """Repeat seed execution preserves admin modifications while keeping occasion records intact."""
    cookies = _login_admin()
    from app.db.seed import seed_catalogue

    # Custom admin update on 'diwali'
    custom_desc = "Admin custom Diwali artisanal illumination gift description"
    client.patch("/api/v1/admin/occasions/diwali", json={"description": custom_desc}, cookies=cookies)

    with SessionLocal() as db:
        # Re-run catalogue seed
        seed_catalogue(db)

    # Verify custom description was preserved
    res = client.get("/api/v1/admin/occasions/diwali", cookies=cookies)
    assert res.status_code == 200
    assert res.json()["description"] == custom_desc


def test_all_thirteen_occasion_images_accessible_and_valid():
    """Verify all 13 occasion image keys return HTTP 200 from the image endpoint with no 404s."""
    with SessionLocal() as db:
        occasions = db.query(Occasion).all()
        assert len(occasions) == 13

        for occ in occasions:
            assert occ.image_key is not None, f"Occasion {occ.id} must have image_key"
            res = client.get(f"/static/images/{occ.image_key}")
            assert res.status_code in (200, 307), f"Image for occasion {occ.id} ({occ.image_key}) returned HTTP {res.status_code}"
            if res.status_code == 200:
                assert res.headers["content-type"].startswith("image/"), f"Image for {occ.id} has invalid content-type {res.headers.get('content-type')}"
            else:
                assert "location" in res.headers, f"Redirect for {occ.id} missing location header"


