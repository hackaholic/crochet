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
    assert len(data) == 16
    first = data[0]
    assert "id" in first
    assert "name" in first
    assert "slug" in first
    assert "price" in first
    assert "inventoryStatus" in first
    assert "categories" in first


def test_filter_products_by_category():
    """Verify category filtering."""
    response = client.get("/api/v1/products?category=flowers")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert all("Flowers" in p["categories"] for p in data)


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
    """Verify occasions list."""
    response = client.get("/api/v1/occasions")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 10
    assert any(o["id"] == "birthday" for o in data)
