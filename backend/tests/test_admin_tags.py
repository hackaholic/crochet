"""Integration and security tests for Admin Tag-Management API (Task 1.7.5).

Covers:
1. RBAC protection: 401 unauthenticated, 403 customer, 200 admin.
2. Tag validation: 422 for empty, whitespace-only, and oversized names (>50 chars).
3. Parameterized safety: Quotes and SQL-like names handled safely.
4. Idempotency & case-insensitivity: Duplicate names (e.g. 'Handmade' vs ' handmade ') return existing tag without creating duplicate records.
5. Deterministic ordering: GET /admin/tags returns tags sorted by name/id.
6. Product association validation on create: Invalid tag IDs return 400 and fail atomically.
7. Product association validation on update: Invalid tag IDs return 400 and preserve existing associations intact.
"""

import uuid
from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.models.catalogue import Product, Tag
from app.models.user import User, UserIdentity

client = TestClient(app)


def _login_customer(phone: str = "9999911005") -> dict[str, str]:
    """Helper to authenticate a non-admin customer user."""
    email = f"customer_{phone}@example.com"
    res = client.post(
        "/api/v1/auth/google",
        json={
            "credential": f"mock_cust_{phone}",
            "email": email,
            "name": "Customer User",
            "sub": f"sub_{phone}",
        },
    )
    assert res.status_code == 200
    return dict(res.cookies)


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

    res = client.post(
        "/api/v1/auth/google",
        json={
            "credential": "mock_admin_token_admin",
            "email": admin_email,
            "name": "Store Admin",
            "sub": "admin_sub_admin",
        },
    )
    assert res.status_code == 200
    assert res.json()["user"]["role"] == "ADMIN"
    return dict(res.cookies)


def test_admin_tags_rbac():
    """Verify unauthenticated requests return 401 and non-admin customers return 403."""
    # 1. Unauthenticated GET & POST
    res_get = client.get("/api/v1/admin/tags")
    assert res_get.status_code == 401

    res_post = client.post("/api/v1/admin/tags", json={"name": "test-tag"})
    assert res_post.status_code == 401

    # 2. Customer authenticated GET & POST
    cust_cookies = _login_customer("9999922001")
    res_cust_get = client.get("/api/v1/admin/tags", cookies=cust_cookies)
    assert res_cust_get.status_code == 403
    assert "Admin privileges required" in res_cust_get.json()["detail"]

    res_cust_post = client.post("/api/v1/admin/tags", json={"name": "test-tag"}, cookies=cust_cookies)
    assert res_cust_post.status_code == 403
    assert "Admin privileges required" in res_cust_post.json()["detail"]

    # 3. Admin authenticated request succeeds
    admin_cookies = _login_admin()
    res_admin_get = client.get("/api/v1/admin/tags", cookies=admin_cookies)
    assert res_admin_get.status_code == 200
    assert isinstance(res_admin_get.json(), list)


def test_admin_tags_validation():
    """Verify empty, whitespace-only, and oversized tag names are rejected with 422."""
    admin_cookies = _login_admin()

    # Empty string
    res_empty = client.post("/api/v1/admin/tags", json={"name": ""}, cookies=admin_cookies)
    assert res_empty.status_code == 422

    # Whitespace only
    res_spaces = client.post("/api/v1/admin/tags", json={"name": "     "}, cookies=admin_cookies)
    assert res_spaces.status_code == 422

    # Oversized name (> 50 chars)
    res_long = client.post("/api/v1/admin/tags", json={"name": "A" * 51}, cookies=admin_cookies)
    assert res_long.status_code == 422


def test_admin_tags_create_and_case_insensitive_duplicate():
    """Verify tag creation and case-insensitive duplicate returns existing tag safely."""
    admin_cookies = _login_admin()
    unique_suffix = uuid.uuid4().hex[:6]
    base_name = f"Handmade {unique_suffix}"

    # 1. Create original tag
    res_create = client.post("/api/v1/admin/tags", json={"name": base_name}, cookies=admin_cookies)
    assert res_create.status_code == 201
    data_created = res_create.json()
    tag_id = data_created["id"]
    assert data_created["name"] == base_name

    # 2. Post case-insensitive duplicate with whitespace padding
    res_dup = client.post("/api/v1/admin/tags", json={"name": f"  {base_name.lower()}  "}, cookies=admin_cookies)
    assert res_dup.status_code == 200
    data_dup = res_dup.json()
    assert data_dup["id"] == tag_id
    assert data_dup["name"] == base_name

    # 3. Verify exactly one tag exists in DB with this name
    with SessionLocal() as db:
        matches = db.query(Tag).filter(Tag.name == base_name).all()
        assert len(matches) == 1

    # 4. Quotes and SQL-like characters handled safely
    quote_name = f"Mom's 'Special' {unique_suffix}"
    res_quote = client.post("/api/v1/admin/tags", json={"name": quote_name}, cookies=admin_cookies)
    assert res_quote.status_code == 201
    assert res_quote.json()["name"] == quote_name


def test_admin_tags_ordering():
    """Verify GET /api/v1/admin/tags returns tags ordered by name/id."""
    admin_cookies = _login_admin()
    unique_suffix = uuid.uuid4().hex[:6]

    # Create distinct sorted tags
    client.post("/api/v1/admin/tags", json={"name": f"Z-Tag {unique_suffix}"}, cookies=admin_cookies)
    client.post("/api/v1/admin/tags", json={"name": f"A-Tag {unique_suffix}"}, cookies=admin_cookies)
    client.post("/api/v1/admin/tags", json={"name": f"M-Tag {unique_suffix}"}, cookies=admin_cookies)

    res = client.get("/api/v1/admin/tags", cookies=admin_cookies)
    assert res.status_code == 200
    tags = res.json()
    assert len(tags) >= 3

    # Filter down to the tags created with this suffix
    matching_tags = [t for t in tags if unique_suffix in t["name"]]
    names = [t["name"] for t in matching_tags]
    assert names == sorted(names)


def test_product_create_with_tags():
    """Verify creating a product with valid tagIds persists associations, and invalid tagIds fail."""
    admin_cookies = _login_admin()
    unique_suffix = uuid.uuid4().hex[:6]

    # Create 2 valid tags
    t1 = client.post("/api/v1/admin/tags", json={"name": f"Tag1 {unique_suffix}"}, cookies=admin_cookies).json()
    t2 = client.post("/api/v1/admin/tags", json={"name": f"Tag2 {unique_suffix}"}, cookies=admin_cookies).json()

    # 1. Successful product creation with valid tagIds
    product_payload = {
        "name": f"Tagged Crochet Product {unique_suffix}",
        "primaryImage": "https://example.com/image.jpg",
        "tagIds": [t1["id"], t2["id"]],
    }
    res_prod = client.post("/api/v1/admin/products", json=product_payload, cookies=admin_cookies)
    assert res_prod.status_code == 201
    prod_data = res_prod.json()
    prod_id = prod_data["id"]
    assert set(prod_data["tagIds"]) == {t1["id"], t2["id"]}
    assert set(prod_data["tagNames"]) == {t1["name"], t2["name"]}

    # Verify directly in DB
    with SessionLocal() as db:
        prod_in_db = db.query(Product).filter(Product.id == prod_id).first()
        assert prod_in_db is not None
        assert {t.id for t in prod_in_db.tags} == {t1["id"], t2["id"]}

    # 2. Product creation with invalid tagIds fails with 400
    invalid_payload = {
        "name": f"Invalid Tag Product {unique_suffix}",
        "primaryImage": "https://example.com/image.jpg",
        "tagIds": [t1["id"], 9999999],
    }
    res_invalid = client.post("/api/v1/admin/products", json=invalid_payload, cookies=admin_cookies)
    assert res_invalid.status_code == 400
    assert "Invalid tagIds" in res_invalid.json()["detail"]
    assert "9999999" in res_invalid.json()["detail"]

    # Verify invalid product was not created
    with SessionLocal() as db:
        uncreated = db.query(Product).filter(Product.name == invalid_payload["name"]).first()
        assert uncreated is None


def test_product_update_with_tags_integrity():
    """Verify product update with invalid tagIds is rejected and preserves existing associations."""
    admin_cookies = _login_admin()
    unique_suffix = uuid.uuid4().hex[:6]

    # Create 2 valid tags
    t1 = client.post("/api/v1/admin/tags", json={"name": f"TagA {unique_suffix}"}, cookies=admin_cookies).json()
    t2 = client.post("/api/v1/admin/tags", json={"name": f"TagB {unique_suffix}"}, cookies=admin_cookies).json()

    # Create base product with TagA
    prod_res = client.post(
        "/api/v1/admin/products",
        json={
            "name": f"Update Tag Prod {unique_suffix}",
            "primaryImage": "https://example.com/image.jpg",
            "tagIds": [t1["id"]],
        },
        cookies=admin_cookies,
    )
    assert prod_res.status_code == 201
    prod_id = prod_res.json()["id"]

    # 1. Update with non-existent tag ID fails with 400
    bad_update_res = client.put(
        f"/api/v1/admin/products/{prod_id}",
        json={"tagIds": [9999998]},
        cookies=admin_cookies,
    )
    assert bad_update_res.status_code == 400
    assert "Invalid tagIds" in bad_update_res.json()["detail"]

    # Verify existing associations remained intact
    get_res = client.get(f"/api/v1/admin/products/{prod_id}", cookies=admin_cookies)
    assert get_res.status_code == 200
    assert get_res.json()["tagIds"] == [t1["id"]]

    with SessionLocal() as db:
        prod_db = db.query(Product).filter(Product.id == prod_id).first()
        assert [t.id for t in prod_db.tags] == [t1["id"]]

    # 2. Update with valid tags succeeds
    good_update_res = client.put(
        f"/api/v1/admin/products/{prod_id}",
        json={"tagIds": [t1["id"], t2["id"]]},
        cookies=admin_cookies,
    )
    assert good_update_res.status_code == 200
    assert set(good_update_res.json()["tagIds"]) == {t1["id"], t2["id"]}


def test_concurrent_tag_creation_case_insensitive():
    """Verify concurrent requests with different casing serialize safely and produce exactly one tag."""
    import concurrent.futures
    from sqlalchemy import func

    admin_cookies = _login_admin()
    unique_suffix = uuid.uuid4().hex[:6]
    base_name = f"ConcTag_{unique_suffix}"

    variations = [
        base_name,
        base_name.lower(),
        base_name.upper(),
        f"  {base_name.lower()}  ",
        f" {base_name.upper()} ",
        base_name.capitalize(),
        base_name,
        base_name.lower(),
    ]

    def _create_tag(name_variant: str):
        return client.post("/api/v1/admin/tags", json={"name": name_variant}, cookies=admin_cookies)

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(variations)) as executor:
        responses = list(executor.map(_create_tag, variations))

    for r in responses:
        assert r.status_code in (200, 201), f"Unexpected status {r.status_code}: {r.text}"
        data = r.json()
        assert "id" in data
        assert "name" in data

    # All threads must receive the exact same tag ID
    tag_ids = {r.json()["id"] for r in responses}
    assert len(tag_ids) == 1, f"Expected exactly 1 tag ID, got: {tag_ids}"

    # Verify database has exactly 1 record matching this name case-insensitively
    with SessionLocal() as db:
        matches = db.query(Tag).filter(func.lower(Tag.name) == base_name.lower()).all()
        assert len(matches) == 1
        assert matches[0].id == list(tag_ids)[0]

