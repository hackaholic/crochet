"""Tests for Catalogue API endpoints and database integrity."""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    """Verify health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "sulocraft-api"}


def test_get_categories_tree():
    """Verify category tree returns root categories with children."""
    response = client.get("/api/v1/categories")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 5
    # Flowers should have children (Roses, Tulips, etc.)
    flowers = next(c for c in data if c["slug"] == "flowers")
    assert flowers["name"] == "Flowers"
    assert len(flowers["children"]) >= 4


def test_get_categories_flat():
    """Verify flat categories list returns all categories."""
    response = client.get("/api/v1/categories?flat=true")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 15  # Includes all root + child categories


def test_get_category_by_slug():
    """Verify single category retrieval."""
    response = client.get("/api/v1/categories/roses")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Roses"
    assert data["slug"] == "roses"


def test_get_products_list():
    """Verify product catalogue listing."""
    response = client.get("/api/v1/products")
    assert response.status_code == 200
    assert "X-Total-Count" in response.headers
    data = response.json()
    assert len(data) == 24
    first = data[0]
    assert "id" in first
    assert "name" in first
    assert "slug" in first
    assert "price" in first
    assert "inventoryStatus" in first
    assert "categories" in first


def test_filter_products_by_category():
    """Verify category filtering for root category and subcategories."""
    response = client.get("/api/v1/products?category=flowers")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    flower_slugs = {"flowers", "bouquets", "single-flowers", "roses", "sunflowers", "tulips", "potted-plants"}
    assert all(
        any((c.get("slug") in flower_slugs or c.get("name") == "Flowers") if isinstance(c, dict) else c in flower_slugs for c in p["categories"])
        for p in data
    )

    # Verify leaf subcategory filtering
    res_sub = client.get("/api/v1/products?category=bouquets")
    assert res_sub.status_code == 200
    sub_data = res_sub.json()
    assert len(sub_data) > 0
    assert all(
        any(c.get("slug") == "bouquets" if isinstance(c, dict) else c == "Bouquets" for c in p["categories"])
        for p in sub_data
    )


def test_filter_products_by_tag():
    """Verify tag filtering."""
    response = client.get("/api/v1/products?tag=romantic")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert all("romantic" in p["tags"] for p in data)


def test_search_products():
    """Verify search endpoint."""
    response = client.get("/api/v1/products/search?q=panda")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert "Panda" in data[0]["name"]


def test_get_product_detail_by_slug():
    """Verify full product detail by slug conforming to Section 2 of spec."""
    response = client.get("/api/v1/products/forever-crochet-rose-bouquet")
    assert response.status_code == 200
    data = response.json()
    assert data["slug"] == "forever-crochet-rose-bouquet"
    assert data["name"] == "Forever Crochet Rose Bouquet"
    assert len(data["variants"]) >= 1
    assert "sku" in data["variants"][0]
    assert len(data["images"]) >= 1
    assert "customerReviews" in data


def test_get_product_detail_not_found():
    """Verify 404 for nonexistent product."""
    response = client.get("/api/v1/products/non-existent-product")
    assert response.status_code == 404


def test_get_occasions():
    """Verify occasions list returns enabled and in-season occasions (5 active defaults, no Rakhi)."""
    response = client.get("/api/v1/occasions")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5
    assert [o["id"] for o in data] == ["birthday", "justbecause", "anniversary", "babyshower", "wedding"]
    assert not any(o["id"] == "rakhi" for o in data)



def test_owner_supplied_products_and_media():
    """Verify owner-supplied products (bunny, baby hamper, heart planter) and media paths."""
    # 1. Crochet bunny updated with owner pink bunny image and gallery collage
    res = client.get("/api/v1/products/crochet-bunny")
    assert res.status_code == 200
    bunny = res.json()
    assert bunny["slug"] == "crochet-bunny"
    assert len(bunny["images"]) == 2
    assert bunny["images"][0].endswith("/products/crochet-bunny/owner-pink-bunny.png")
    assert bunny["images"][1].endswith("/products/crochet-bunny/gallery-01-owner-collage.png")

    # 2. Baby Gift Hamper listing
    res_hamper = client.get("/api/v1/products/baby-gift-hamper")
    assert res_hamper.status_code == 200
    hamper = res_hamper.json()
    assert hamper["name"] == "Baby Gift Hamper"
    assert hamper["images"][0].endswith("/products/baby-gift-hamper/primary.png")
    assert hamper["variants"][0]["sku"] == "SULO-BABY-HAMPER-001"
    assert any(c["slug"] == "baby-gift-sets" for c in hamper["categories"])

    # 3. Crochet Heart Planter listing
    res_planter = client.get("/api/v1/products/crochet-heart-planter")
    assert res_planter.status_code == 200
    planter = res_planter.json()
    assert planter["name"] == "Crochet Heart Planter"
    assert planter["images"][0].endswith("/products/crochet-heart-planter/primary.png")
    assert planter["variants"][0]["sku"] == "SULO-HOME-HEART-001"
    assert any(c["slug"] == "flower-plant-decor" for c in planter["categories"])

    # 4. Sunflower Bouquet lifestyle gallery
    res_sunflower = client.get("/api/v1/products/sunflower-bouquet")
    assert res_sunflower.status_code == 200
    sunflower = res_sunflower.json()
    assert len(sunflower["images"]) == 2
    assert sunflower["images"][1].endswith("/products/sunflower-bouquet/gallery-01-owner-lifestyle.png")

    # 5. Baby Blanket
    res_blanket = client.get("/api/v1/products/baby-blanket")
    assert res_blanket.status_code == 200
    blanket = res_blanket.json()
    assert blanket["name"] == "Handmade Crochet Baby Blanket"
    assert blanket["images"][0].endswith("/products/baby-blanket/primary.png")
    assert blanket["variants"][0]["sku"] == "SULO-BABY-BLNK-001"
    assert any(c["slug"] == "blankets" for c in blanket["categories"])

    # 6. Bunny Amigurumi Trio
    res_trio = client.get("/api/v1/products/bunny-amigurami-set")
    assert res_trio.status_code == 200
    trio = res_trio.json()
    assert trio["name"] == "Pastel Bunny Amigurumi Trio"
    assert trio["images"][0].endswith("/products/bunny-amigurami-set/primary.png")
    assert trio["variants"][0]["sku"] == "SULO-AMI-BUNNY-003"
    assert any(c["slug"] == "bunny" for c in trio["categories"])

    # 7. Amigurumi Flower Bouquet
    res_flr_ami = client.get("/api/v1/products/amigurumi-flower-bouquet")
    assert res_flr_ami.status_code == 200
    flr_ami = res_flr_ami.json()
    assert flr_ami["name"] == "Amigurumi Floral Bloom Bouquet"
    assert flr_ami["images"][0].endswith("/products/amigurumi-flower-bouquet/primary.png")
    assert flr_ami["variants"][0]["sku"] == "SULO-FLR-AMI-001"
    assert any(c["slug"] == "bouquets" for c in flr_ami["categories"])

    # 8. Octopus Amigurumi Set
    res_octo = client.get("/api/v1/products/octopus-amigurami-set")
    assert res_octo.status_code == 200
    octo = res_octo.json()
    assert octo["name"] == "Octopus Amigurumi Duo Set"
    assert octo["images"][0].endswith("/products/octopus-amigurami-set/primary.png")
    assert octo["variants"][0]["sku"] == "SULO-AMI-OCTO-001"
    assert any(c["slug"] == "octopus" for c in octo["categories"])

    # 9. Pooja Dress (with 3 galleries)
    res_pooja = client.get("/api/v1/products/pooja-dress")
    assert res_pooja.status_code == 200
    pooja = res_pooja.json()
    assert pooja["name"] == "Handcrafted Deity Poshak (Pooja Dress)"
    assert len(pooja["images"]) == 4
    assert pooja["images"][0].endswith("/products/pooja-dress/primary.png")
    assert pooja["images"][1].endswith("/products/pooja-dress/gallery-01.png")
    assert pooja["images"][2].endswith("/products/pooja-dress/gallery-02.png")
    assert pooja["images"][3].endswith("/products/pooja-dress/gallery-03.png")
    assert pooja["variants"][0]["sku"] == "SULO-POOJA-DRESS-001"
    assert any(c["slug"] == "poshak-god-clothes" for c in pooja["categories"])

    # 10. Potli Handbag (with 1 gallery)
    res_potli = client.get("/api/v1/products/potli-handbag")
    assert res_potli.status_code == 200
    potli = res_potli.json()
    assert potli["name"] == "Handcrafted Crochet Potli Bag"
    assert len(potli["images"]) == 2
    assert potli["images"][0].endswith("/products/potli-handbag/primary.png")
    assert potli["images"][1].endswith("/products/potli-handbag/gallery-01.png")
    assert potli["variants"][0]["sku"] == "SULO-ACC-POTLI-001"
    assert any(c["slug"] == "other-home-decor" for c in potli["categories"])
