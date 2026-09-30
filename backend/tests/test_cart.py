"""Automated tests for Shopping Cart and Guest Cart persistence conforming to Milestone 4."""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_empty_cart_returns_zero_items():
    """Verify requesting cart without cookie returns empty cart object gracefully."""
    response = client.get("/api/v1/cart")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["itemCount"] == 0
    assert data["subtotal"] == 0


def test_add_item_creates_guest_cart_and_sets_cookie():
    """Verify adding an item creates a cart and sets the guest_cart_token cookie."""
    add_payload = {
        "product_id": 1,
        "quantity": 1,
        "personalization": {"gift_message": "Happy Birthday"},
    }
    response = client.post("/api/v1/cart/items", json=add_payload)
    assert response.status_code == 201
    assert "guest_cart_token" in response.cookies
    data = response.json()
    assert data["itemCount"] == 1
    assert len(data["items"]) == 1

    item = data["items"][0]
    assert item["productId"] == 1
    assert item["productName"] == "Forever Crochet Rose Bouquet"
    assert item["quantity"] == 1
    assert item["unitPrice"] == 2599
    assert item["lineTotal"] == 2599
    assert item["personalization"] == {"gift_message": "Happy Birthday"}


def test_add_identical_item_increments_quantity():
    """Verify adding identical item (same variant and personalization) increments quantity."""
    # Start fresh session
    cart_client = TestClient(app)
    add_payload = {"product_id": 2, "quantity": 1}

    res1 = cart_client.post("/api/v1/cart/items", json=add_payload)
    assert res1.status_code == 201
    assert res1.json()["itemCount"] == 1

    # Add same product again
    res2 = cart_client.post("/api/v1/cart/items", json=add_payload)
    assert res2.status_code == 201
    data = res2.json()
    assert data["itemCount"] == 2
    assert len(data["items"]) == 1
    assert data["items"][0]["quantity"] == 2
    assert data["subtotal"] == 1599 * 2


def test_add_item_stock_limit_validation():
    """Verify error when attempting to add more items than available in stock."""
    cart_client = TestClient(app)
    # Variant has stock 15; attempting to add 99 should fail
    excessive_payload = {"product_id": 1, "quantity": 99}
    response = cart_client.post("/api/v1/cart/items", json=excessive_payload)
    assert response.status_code == 400
    assert "exceeds available stock" in response.json()["detail"]


def test_update_item_quantity():
    """Verify updating line item quantity and subtotal recalculation."""
    cart_client = TestClient(app)
    add_res = cart_client.post("/api/v1/cart/items", json={"product_id": 3, "quantity": 1})
    item_id = add_res.json()["items"][0]["id"]

    update_res = cart_client.patch(
        f"/api/v1/cart/items/{item_id}",
        json={"quantity": 3, "personalization": {"color": "Custom Cream"}},
    )
    assert update_res.status_code == 200
    data = update_res.json()
    assert data["itemCount"] == 3
    assert data["items"][0]["quantity"] == 3
    assert data["items"][0]["lineTotal"] == 1799 * 3
    assert data["items"][0]["personalization"] == {"color": "Custom Cream"}


def test_delete_single_item():
    """Verify deleting a specific line item from cart."""
    cart_client = TestClient(app)
    add1 = cart_client.post("/api/v1/cart/items", json={"product_id": 1, "quantity": 1})
    add2 = cart_client.post("/api/v1/cart/items", json={"product_id": 2, "quantity": 1})
    item1_id = add2.json()["items"][0]["id"]

    del_res = cart_client.delete(f"/api/v1/cart/items/{item1_id}")
    assert del_res.status_code == 200
    data = del_res.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["productId"] == 2


def test_clear_entire_cart():
    """Verify clearing the entire cart."""
    cart_client = TestClient(app)
    cart_client.post("/api/v1/cart/items", json={"product_id": 1, "quantity": 1})
    cart_client.post("/api/v1/cart/items", json={"product_id": 2, "quantity": 1})

    clear_res = cart_client.delete("/api/v1/cart")
    assert clear_res.status_code == 200
    data = clear_res.json()
    assert data["itemCount"] == 0
    assert data["items"] == []
    assert data["subtotal"] == 0


def test_merge_guest_cart():
    """Verify merging an anonymous guest cart into another active session cart."""
    # 1. Guest A creates a cart
    client_a = TestClient(app)
    res_a = client_a.post("/api/v1/cart/items", json={"product_id": 1, "quantity": 2})
    guest_token_a = res_a.json()["guestToken"]
    assert guest_token_a is not None

    # 2. User B has an existing cart with product 1 (qty 1) and product 2 (qty 1)
    client_b = TestClient(app)
    client_b.post("/api/v1/cart/items", json={"product_id": 1, "quantity": 1})
    client_b.post("/api/v1/cart/items", json={"product_id": 2, "quantity": 1})

    # 3. Merge guest A's cart into User B's cart
    merge_res = client_b.post("/api/v1/cart/merge", json={"guest_token": guest_token_a})
    assert merge_res.status_code == 200
    data = merge_res.json()

    # Product 1 should now have quantity = 1 + 2 = 3
    # Product 2 should have quantity = 1
    # Total itemCount = 4
    assert data["itemCount"] == 4
    item1 = next(i for i in data["items"] if i["productId"] == 1)
    assert item1["quantity"] == 3
