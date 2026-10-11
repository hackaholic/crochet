"""Automated tests for Work 019 Task 19.1: Product information persistence and defaults API."""

import pytest
from fastapi.testclient import TestClient

from app.db.seed import seed_catalogue
from app.db.session import SessionLocal
from app.main import app
from app.models.catalogue import Product, ProductInformationDefaults
from app.models.user import User, UserIdentity

client = TestClient(app)


def _login_admin(phone: str = "9999900000") -> dict[str, str]:
    """Helper to authenticate an admin user via session cookie."""
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
        "credential": "mock_admin_token_prod_info",
        "email": admin_email,
        "name": "Store Admin",
        "sub": "admin_sub_prod_info",
    })
    assert res.status_code == 200
    assert res.json()["user"]["role"] == "ADMIN"
    return dict(res.cookies)


def _login_customer(phone: str = "9888800000") -> dict[str, str]:
    """Helper to authenticate a non-admin customer via session cookie."""
    customer_email = f"customer_{phone}@example.com"
    res = client.post("/api/v1/auth/google", json={
        "credential": f"mock_cust_{phone}",
        "email": customer_email,
        "name": "Customer User",
        "sub": f"sub_{phone}",
    })
    assert res.status_code == 200
    return dict(res.cookies)


@pytest.fixture(autouse=True)
def setup_catalogue():
    """Ensure database has seed data prior to running product information tests."""
    with SessionLocal() as db:
        seed_catalogue(db)


# =============================================================================
# 19.1-TC01: Acceptance & Snapshot Semantics
# =============================================================================

def test_get_product_defaults_admin():
    """19.1-TC01: Admin can retrieve the storewide configurable product defaults."""
    cookies = _login_admin()
    response = client.get("/api/v1/admin/storefront/product-defaults", cookies=cookies)
    assert response.status_code == 200
    data = response.json()
    assert "handmadeDetails" in data
    assert "materialsUsed" in data
    assert "sizeDimensions" in data
    assert "processingTime" in data
    assert "careInstructions" in data
    assert "shippingDelivery" in data
    assert "Handcrafted" in (data["handmadeDetails"] or "")


def test_update_product_defaults_admin():
    """19.1-TC01: Admin can update storewide product defaults; omitted fields are preserved."""
    cookies = _login_admin()
    update_payload = {
        "processingTime": "Handcrafted to order: 2–4 working days.",
        "careInstructions": "Dust with dry microfiber cloth only. Keep away from water.",
    }
    response = client.put("/api/v1/admin/storefront/product-defaults", json=update_payload, cookies=cookies)
    assert response.status_code == 200
    data = response.json()
    assert data["processingTime"] == "Handcrafted to order: 2–4 working days."
    assert data["careInstructions"] == "Dust with dry microfiber cloth only. Keep away from water."
    assert "Handcrafted" in (data["handmadeDetails"] or "")


def test_product_creation_snapshots_defaults_when_omitted():
    """19.1-TC01: Creating product without 6 fields snapshots current storewide defaults."""
    cookies = _login_admin()
    # 1. Update defaults to a known custom value
    client.put("/api/v1/admin/storefront/product-defaults", json={
        "handmadeDetails": "Unique snapshot test details",
        "processingTime": "Snapshot processing 4 days",
    }, cookies=cookies)

    # 2. Create product omitting handmadeDetails and processingTime
    prod_payload = {
        "name": "Snapshot Test Daisy",
        "primaryImage": "products/daisy.jpg",
        "description": "Lovely daisy",
    }
    create_res = client.post("/api/v1/admin/products", json=prod_payload, cookies=cookies)
    assert create_res.status_code == 201
    prod_data = create_res.json()
    assert prod_data["handmadeDetails"] == "Unique snapshot test details"
    assert prod_data["processingTime"] == "Snapshot processing 4 days"
    prod_id = prod_data["id"]
    prod_slug = prod_data["slug"]

    # 3. Public catalogue endpoint also renders the snapshotted values
    pub_res = client.get(f"/api/v1/products/{prod_slug}")
    assert pub_res.status_code == 200
    pub_data = pub_res.json()
    assert pub_data["handmadeDetails"] == "Unique snapshot test details"
    assert pub_data["processingTime"] == "Snapshot processing 4 days"

    # 4. Modify storewide defaults afterwards — must NOT mutate the existing product
    client.put("/api/v1/admin/storefront/product-defaults", json={
        "handmadeDetails": "Brand new future default",
    }, cookies=cookies)

    verify_res = client.get(f"/api/v1/admin/products/{prod_id}", cookies=cookies)
    assert verify_res.status_code == 200
    assert verify_res.json()["handmadeDetails"] == "Unique snapshot test details"


def test_product_creation_explicit_overrides_win():
    """19.1-TC01: Explicit overrides on product creation override storewide defaults."""
    cookies = _login_admin()
    prod_payload = {
        "name": "Custom Overrides Sunflower",
        "primaryImage": "products/sunflower.jpg",
        "handmadeDetails": "Custom handmade sunflower details for this specific piece.",
        "materialsUsed": "100% bamboo yarn with floral wire.",
        "sizeDimensions": "Height 25cm, Bloom diameter 10cm.",
    }
    create_res = client.post("/api/v1/admin/products", json=prod_payload, cookies=cookies)
    assert create_res.status_code == 201
    prod_data = create_res.json()
    assert prod_data["handmadeDetails"] == "Custom handmade sunflower details for this specific piece."
    assert prod_data["materialsUsed"] == "100% bamboo yarn with floral wire."
    assert prod_data["sizeDimensions"] == "Height 25cm, Bloom diameter 10cm."
    # Omitted fields still snapshot default
    assert prod_data["processingTime"] is not None


def test_partial_update_preserves_omitted_product_fields():
    """19.1-TC01: PATCH/PUT on product preserves omitted info fields and updates specified ones."""
    cookies = _login_admin()
    # Create product
    create_res = client.post("/api/v1/admin/products", json={
        "name": "Partial Update Rose",
        "primaryImage": "products/rose.jpg",
        "handmadeDetails": "Initial handmade rose",
        "materialsUsed": "Initial cotton",
    }, cookies=cookies)
    assert create_res.status_code == 201
    prod_id = create_res.json()["id"]

    # Partial update: update materialsUsed only
    update_res = client.patch(f"/api/v1/admin/products/{prod_id}", json={
        "materialsUsed": "Updated mercerized organic cotton",
    }, cookies=cookies)
    assert update_res.status_code == 200
    updated_data = update_res.json()
    assert updated_data["materialsUsed"] == "Updated mercerized organic cotton"
    assert updated_data["handmadeDetails"] == "Initial handmade rose"


# =============================================================================
# 19.1-TC02: Security & Validation Negatives
# =============================================================================

def test_unauthorized_product_defaults_access():
    """19.1-TC02: Defaults endpoints reject anonymous or non-admin users."""
    # Anonymous GET
    anon_get = client.get("/api/v1/admin/storefront/product-defaults")
    assert anon_get.status_code in (401, 403)

    # Anonymous PUT
    anon_put = client.put("/api/v1/admin/storefront/product-defaults", json={"handmadeDetails": "Hacked"})
    assert anon_put.status_code in (401, 403)

    # Customer PUT
    cust_cookies = _login_customer()
    cust_put = client.put("/api/v1/admin/storefront/product-defaults", json={"handmadeDetails": "Hacked"}, cookies=cust_cookies)
    assert cust_put.status_code == 403


def test_reject_oversized_info_text():
    """19.1-TC02: Rejects text exceeding 5,000 characters."""
    cookies = _login_admin()
    oversized = "A" * 5001
    res = client.put("/api/v1/admin/storefront/product-defaults", json={"handmadeDetails": oversized}, cookies=cookies)
    assert res.status_code == 422


def test_reject_html_injection_in_info_fields():
    """19.1-TC02: Plain text only: rejects raw HTML tags to prevent stored XSS."""
    cookies = _login_admin()
    xss_payload = {
        "handmadeDetails": "Normal text <script>alert('xss')</script> end text",
    }
    res = client.put("/api/v1/admin/storefront/product-defaults", json=xss_payload, cookies=cookies)
    assert res.status_code == 422

    # HTML tags in product creation also rejected
    prod_res = client.post("/api/v1/admin/products", json={
        "name": "XSS Test Product",
        "primaryImage": "products/test.jpg",
        "careInstructions": "<img src=x onerror=alert(1)>",
    }, cookies=cookies)
    assert prod_res.status_code == 422


def test_accept_legitimate_unicode_and_newlines():
    """19.1-TC02: Preserves valid multiline newlines, bullet points, and Unicode symbols."""
    cookies = _login_admin()
    multiline_text = (
        "• 100% Handcrafted crochet artistry 🌸\n"
        "• Detailed floral petals & subtle stem wire\n"
        "• Designed in India with warmth & care ✨"
    )
    res = client.put("/api/v1/admin/storefront/product-defaults", json={
        "handmadeDetails": multiline_text,
    }, cookies=cookies)
    assert res.status_code == 200
    assert res.json()["handmadeDetails"] == multiline_text


def test_explicit_blank_override_and_clear_do_not_reapply_defaults():
    cookies = _login_admin()
    client.put('/api/v1/admin/storefront/product-defaults', json={'materialsUsed': 'Default yarn'}, cookies=cookies)
    created = client.post('/api/v1/admin/products', json={'name': 'Blank information fixture', 'primaryImage': 'products/test.jpg', 'materialsUsed': '', 'handmadeDetails': 'Original'}, cookies=cookies)
    assert created.status_code == 201
    product_id = created.json()['id']
    assert created.json()['materialsUsed'] == ''
    updated = client.patch(f'/api/v1/admin/products/{product_id}', json={'handmadeDetails': ''}, cookies=cookies)
    assert updated.status_code == 200
    assert updated.json()['handmadeDetails'] == ''
    assert updated.json()['materialsUsed'] == ''
    detail = client.get(f'/api/v1/products/{product_id}')
    assert detail.status_code == 200
    assert detail.json()['handmadeDetails'] == ''


def test_acceptance_all_six_fields_roundtrip_and_defaults_do_not_rewrite_products():
    cookies = _login_admin()
    keys = ['handmadeDetails', 'materialsUsed', 'sizeDimensions', 'processingTime', 'careInstructions', 'shippingDelivery']
    defaults = {key: f'Default {key}' for key in keys}
    assert client.put('/api/v1/admin/storefront/product-defaults', json=defaults, cookies=cookies).status_code == 200
    product = client.post('/api/v1/admin/products', json={'name': 'Six field acceptance fixture', 'primaryImage': 'products/test.jpg', **defaults}, cookies=cookies)
    assert product.status_code == 201
    pid = product.json()['id']
    overrides = {key: f'Override {key}\nSecond line 🌸' for key in keys}
    updated = client.patch(f'/api/v1/admin/products/{pid}', json=overrides, cookies=cookies)
    assert updated.status_code == 200
    assert {key: updated.json()[key] for key in keys} == overrides
    future_defaults = {key: f'Future {key}' for key in keys}
    client.put('/api/v1/admin/storefront/product-defaults', json=future_defaults, cookies=cookies)
    public = client.get(f'/api/v1/products/{pid}')
    assert {key: public.json()[key] for key in keys} == overrides
    unchanged = client.get(f'/api/v1/admin/products/{pid}', cookies=cookies).json()
    assert unchanged['primaryImage'] == product.json()['primaryImage']
    assert unchanged['variants'] == product.json()['variants']
    assert unchanged['categoryIds'] == product.json()['categoryIds']
    assert unchanged['tagIds'] == product.json()['tagIds']
    next_product = client.post('/api/v1/admin/products', json={'name': 'Future defaults acceptance fixture', 'primaryImage': 'products/test.jpg'}, cookies=cookies)
    assert next_product.status_code == 201
    assert {key: next_product.json()[key] for key in keys} == future_defaults


def test_text_edit_preserves_unchanged_gallery_identity_and_alt_text():
    cookies = _login_admin()
    created = client.post('/api/v1/admin/products', json={'name': 'Gallery preservation fixture', 'primaryImage': 'products/one.jpg', 'galleryImages': ['products/two.jpg']}, cookies=cookies)
    assert created.status_code == 201
    pid = created.json()['id']
    with SessionLocal() as db:
        product = db.get(Product, pid)
        original = [(image.id, image.url) for image in product.images]
        for image in product.images:
            image.alt_text = 'Persisted accessible image description'
        db.commit()
    updated = client.patch(f'/api/v1/admin/products/{pid}', json={'materialsUsed':'Updated text', 'galleryImages':['products/one.jpg','products/two.jpg']}, cookies=cookies)
    assert updated.status_code == 200
    with SessionLocal() as db:
        product = db.get(Product, pid)
        assert [(image.id,image.url) for image in product.images] == original
        assert all(image.alt_text == 'Persisted accessible image description' for image in product.images)
