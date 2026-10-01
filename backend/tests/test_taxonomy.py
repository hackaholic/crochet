"""Automated integration tests for Hierarchical Taxonomy and Collections conforming to docs/product-taxonomy.md."""

from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from app.db.seed import COLLECTIONS_DATA, LOCAL_IMAGE_DIR, PRODUCTS_DATA, TAXONOMY_TREE, seed_catalogue, validate_seed_data
from app.db.session import SessionLocal
from app.main import app
from app.models.catalogue import Category, Collection, Product
from app.models.user import User, UserIdentity

client = TestClient(app)


@pytest.fixture(autouse=True)
def ensure_seed():
    """Ensure database has seed data prior to running taxonomy tests."""
    with SessionLocal() as db:
        seed_catalogue(db)


def _login_admin() -> dict[str, str]:
    """Helper to authenticate an admin user."""
    admin_email = "admin@sulocraft.com"
    with SessionLocal() as db:
        admin = db.query(User).filter(User.email == admin_email).first()
        if not admin:
            admin = User(
                name="Store Admin",
                phone="9999900000",
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
        "credential": "mock_admin_token_taxonomy",
        "email": admin_email,
        "name": "Store Admin",
        "sub": "admin_sub_taxonomy",
    })
    assert res.status_code == 200
    return dict(res.cookies)


def test_canonical_root_categories_order():
    """Verify GET /api/v1/categories returns 5 canonical roots in exact storefront order."""
    response = client.get("/api/v1/categories")
    assert response.status_code == 200
    roots = response.json()
    assert len(roots) == 5

    expected = [
        ("Flowers", "flowers"),
        ("Amigurumi", "amigurumi"),
        ("Baby", "baby"),
        ("Home & Decor", "home-decor"),
        ("Pooja & Devotional", "pooja-devotional"),
    ]

    for i, (name, slug) in enumerate(expected):
        assert roots[i]["name"] == name
        assert roots[i]["slug"] == slug
        assert roots[i]["parentId"] is None
        assert len(roots[i]["children"]) > 0


def test_category_descendant_product_count():
    """Verify category tree counts include direct and descendant product associations."""
    response = client.get("/api/v1/categories")
    assert response.status_code == 200
    roots = {c["slug"]: c for c in response.json()}

    # Flowers root should aggregate products from Bouquets, Roses, Sunflowers, Tulips, Single Flowers
    flowers = roots["flowers"]
    assert flowers["productCount"] >= 5
    assert len(flowers["children"]) >= 5


def test_category_products_endpoint():
    """Verify GET /api/v1/categories/{slug}/products returns products under category or descendants."""
    res_parent = client.get("/api/v1/categories/flowers/products")
    assert res_parent.status_code == 200
    flowers_products = res_parent.json()
    assert len(flowers_products) >= 5

    res_leaf = client.get("/api/v1/categories/bouquets/products")
    assert res_leaf.status_code == 200
    bouquet_products = res_leaf.json()
    assert len(bouquet_products) >= 1
    assert all(any(c["slug"] == "bouquets" for c in p["categories"]) for p in bouquet_products)


def test_collections_public_endpoints():
    """Verify GET /api/v1/collections returns all 15 active collections."""
    response = client.get("/api/v1/collections")
    assert response.status_code == 200
    collections = response.json()
    assert len(collections) >= 15

    slugs = {c["slug"] for c in collections}
    assert "gifts" in slugs
    assert "birthday-gifts" in slugs
    assert "anniversary-gifts" in slugs
    assert "bestsellers" in slugs
    assert "new-arrivals" in slugs

    # Test single collection detail
    res_single = client.get("/api/v1/collections/bestsellers")
    assert res_single.status_code == 200
    bestsellers = res_single.json()
    assert bestsellers["slug"] == "bestsellers"
    assert bestsellers["collectionType"] == "MERCHANDISING"

    # Test collection products endpoint
    res_col_prods = client.get("/api/v1/collections/bestsellers/products")
    assert res_col_prods.status_code == 200
    prods = res_col_prods.json()
    assert len(prods) >= 1
    assert all(any(c["slug"] == "bestsellers" for c in p["collections"]) for p in prods)


def test_product_classification_primary_and_secondary_categories():
    """Verify Heart Bear has primaryCategory=Toys, secondaryCategory=Teddy Bear, and collections."""
    response = client.get("/api/v1/products/heart-bear")
    assert response.status_code == 200
    product = response.json()

    assert product["primaryCategory"] is not None
    assert product["primaryCategory"]["slug"] == "toys"
    assert product["primaryCategory"]["name"] == "Toys"

    cat_slugs = [c["slug"] for c in product["categories"]]
    assert "toys" in cat_slugs
    assert "teddy-bear" in cat_slugs

    col_slugs = [c["slug"] for c in product["collections"]]
    assert "bestsellers" in col_slugs
    assert "baby-shower-gifts" in col_slugs
    assert "gifts-for-kids" in col_slugs
    assert "gifts" in col_slugs


def test_admin_category_cycle_prevention():
    """Verify admin PATCH /api/v1/admin/categories/{id} detects and rejects hierarchy cycles."""
    cookies = _login_admin()
    with SessionLocal() as db:
        flowers = db.query(Category).filter(Category.slug == "flowers").first()
        bouquets = db.query(Category).filter(Category.slug == "bouquets").first()
        flowers_id = flowers.id
        bouquets_id = bouquets.id

    # Try setting Flowers (parent) parent_id to Bouquets (child) -> Cycle!
    res = client.patch(
        f"/api/v1/admin/categories/{flowers_id}",
        json={"parentId": bouquets_id},
        cookies=cookies,
    )
    assert res.status_code == 400
    assert "circular" in res.json()["detail"].lower() or "cycle" in res.json()["detail"].lower()


def test_admin_safe_category_deletion():
    """Verify admin DELETE /api/v1/admin/categories/{id} blocks deletion when children or products are attached."""
    cookies = _login_admin()
    with SessionLocal() as db:
        flowers = db.query(Category).filter(Category.slug == "flowers").first()
        bouquets = db.query(Category).filter(Category.slug == "bouquets").first()
        flowers_id = flowers.id
        bouquets_id = bouquets.id

    # Flowers has children -> deletion must fail
    res_parent = client.delete(f"/api/v1/admin/categories/{flowers_id}", cookies=cookies)
    assert res_parent.status_code == 400
    assert "child categories" in res_parent.json()["detail"].lower()

    # Bouquets has products -> deletion must fail
    res_child = client.delete(f"/api/v1/admin/categories/{bouquets_id}", cookies=cookies)
    assert res_child.status_code == 400
    assert "products" in res_child.json()["detail"].lower()


def test_admin_collection_crud():
    """Verify admin CRUD operations on collections."""
    cookies = _login_admin()

    # Create collection
    res_create = client.post(
        "/api/v1/admin/collections",
        json={
            "name": "Spring Special",
            "slug": "spring-special",
            "description": "Seasonal blooms for spring celebrations",
            "collectionType": "SEASONAL",
            "displayOrder": 50,
            "isActive": True,
        },
        cookies=cookies,
    )
    assert res_create.status_code == 201
    created = res_create.json()
    col_id = created["id"]
    assert created["slug"] == "spring-special"

    # Update collection
    res_update = client.patch(
        f"/api/v1/admin/collections/{col_id}",
        json={"name": "Spring Bloom Collection", "displayOrder": 55},
        cookies=cookies,
    )
    assert res_update.status_code == 200
    assert res_update.json()["name"] == "Spring Bloom Collection"

    # Assign product
    with SessionLocal() as db:
        prod = db.query(Product).first()
        prod_id = prod.id

    res_assign = client.post(
        f"/api/v1/admin/collections/{col_id}/products",
        json={"productIds": [prod_id]},
        cookies=cookies,
    )
    assert res_assign.status_code == 200
    assert res_assign.json()["productCount"] == 1

    # Delete collection
    res_delete = client.delete(f"/api/v1/admin/collections/{col_id}", cookies=cookies)
    assert res_delete.status_code in (200, 204)


def test_publication_gate_validator():
    """Verify publication validator enforces SKUs, images, and primary category rules."""
    # Baseline seed data validates cleanly
    validate_seed_data(TAXONOMY_TREE, COLLECTIONS_DATA, PRODUCTS_DATA, LOCAL_IMAGE_DIR)

    # Test duplicate SKU rejection
    bad_products_sku = [dict(p) for p in PRODUCTS_DATA]
    bad_products_sku[1] = dict(bad_products_sku[1])
    dupe_sku = PRODUCTS_DATA[0]["variants"][0]["sku"]
    bad_products_sku[1]["variants"] = [{"sku": dupe_sku, "name": "Dupe", "price": 100}]
    with pytest.raises(ValueError, match="Duplicate SKU"):
        validate_seed_data(TAXONOMY_TREE, COLLECTIONS_DATA, bad_products_sku, LOCAL_IMAGE_DIR)

    # Test missing primary image file rejection
    bad_products_img = [dict(p) for p in PRODUCTS_DATA]
    bad_products_img[0] = dict(bad_products_img[0])
    bad_products_img[0]["image"] = "products/non-existent-image.png"
    with pytest.raises(ValueError, match="does not exist on disk"):
        validate_seed_data(TAXONOMY_TREE, COLLECTIONS_DATA, bad_products_img, LOCAL_IMAGE_DIR)

    # Test reused primary image rejection
    bad_products_reused = [dict(p) for p in PRODUCTS_DATA]
    bad_products_reused[1] = dict(bad_products_reused[1])
    bad_products_reused[1]["image"] = bad_products_reused[0]["image"]
    with pytest.raises(ValueError, match="reused across multiple product slugs"):
        validate_seed_data(TAXONOMY_TREE, COLLECTIONS_DATA, bad_products_reused, LOCAL_IMAGE_DIR)

    # Test missing primary category rejection
    bad_products_no_prim = [dict(p) for p in PRODUCTS_DATA]
    bad_products_no_prim[0] = dict(bad_products_no_prim[0])
    bad_products_no_prim[0]["primary_category_slug"] = "invalid-category"
    with pytest.raises(ValueError, match="invalid primary category"):
        validate_seed_data(TAXONOMY_TREE, COLLECTIONS_DATA, bad_products_no_prim, LOCAL_IMAGE_DIR)
