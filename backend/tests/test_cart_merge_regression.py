"""Work007: exact merge semantics and claimed-cart ownership boundaries."""
from urllib.parse import parse_qs, urlparse
from datetime import datetime, timedelta, timezone
from app.db.session import SessionLocal
from app.models.user import MagicLinkToken
import pytest
from fastapi.testclient import TestClient
from app.main import app


def login(client, email):
    # Age only consumed fixture tokens; exercise real magic-link/session logic
    # without weakening production resend throttling or sleeping in tests.
    with SessionLocal() as db:
        db.query(MagicLinkToken).filter_by(email=email, is_used=True).update(
            {"created_at": datetime.now(timezone.utc) - timedelta(days=1)}
        )
        db.commit()
    response = client.post('/api/v1/auth/email/start', json={'email': email})
    assert response.status_code == 202
    token = parse_qs(urlparse(response.json()['devMagicLink']).query)['token'][0]
    response = client.get('/api/v1/auth/email/verify', params={'token': token}, follow_redirects=False)
    assert response.status_code == 303
    assert 'invalid_link' not in response.headers['location']


def add(client, note, quantity=1):
    product = client.get('/api/v1/products').json()[0]
    variant = client.get(f"/api/v1/products/{product['slug']}").json()['variants'][0]
    response = client.post('/api/v1/cart/items', json={
        'product_variant_id': variant['id'], 'quantity': quantity,
        'personalization': {'note': note},
    })
    assert response.status_code == 201
    return variant


def test_existing_customer_merge_keeps_exact_notes_quantities_and_prices():
    customer = TestClient(app)
    email = 'merge-existing@example.com'
    login(customer, email)
    variant = add(customer, 'For Mum', 1)
    guest = TestClient(app)
    add(guest, 'For Mum', 2)
    add(guest, 'For Dad', 1)
    login(guest, email)
    cart = guest.get('/api/v1/cart').json()
    assert cart['itemCount'] == 4
    assert len(cart['items']) == 2
    assert {item['personalization']['note']: item['quantity'] for item in cart['items']} == {'For Mum': 3, 'For Dad': 1}
    assert all(item['variantId'] == variant['id'] and item['unitPrice'] == variant['price'] for item in cart['items'])
    login(guest, email)
    assert guest.get('/api/v1/cart').json()['itemCount'] == 4
    assert customer.get('/api/v1/cart').json()['itemCount'] == 4


@pytest.mark.parametrize('attack', ['merge_endpoint', 'email_login'])
def test_claimed_customer_cart_cannot_be_merged_by_another_identity(attack):
    owner = TestClient(app)
    add(owner, 'Private customer note', 2)
    old_guest_token = owner.cookies['guest_cart_token']
    login(owner, 'merge-owner@example.com')
    before = owner.get('/api/v1/cart').json()
    stranger = TestClient(app)
    if attack == 'merge_endpoint':
        response = stranger.post('/api/v1/cart/merge', json={'guest_token': old_guest_token})
        assert response.status_code == 200
        assert response.json()['items'] == []
    else:
        stranger.cookies.set('guest_cart_token', old_guest_token)
        assert stranger.get('/api/v1/cart').json()['items'] == []
        login(stranger, 'merge-other@example.com')
        stranger.cookies.delete('guest_cart_token')
        assert stranger.get('/api/v1/cart').json()['items'] == []
    after = owner.get('/api/v1/cart')
    assert after.status_code == 200
    assert after.json()['items'] == before['items']


def test_guest_quantity_rejection_and_other_cart_item_mutation_have_no_side_effect():
    owner = TestClient(app)
    variant = add(owner, '<plain gift note>')
    before = owner.get('/api/v1/cart').json()
    for quantity in [0, -1, variant['stockQuantity'] + 1]:
        response = owner.post('/api/v1/cart/items', json={'product_variant_id': variant['id'], 'quantity': quantity})
        assert response.status_code in [400, 422]
    stranger = TestClient(app)
    response = stranger.patch(f"/api/v1/cart/items/{before['items'][0]['id']}", json={'quantity': 2})
    assert response.status_code == 404
    assert stranger.delete(f"/api/v1/cart/items/{before['items'][0]['id']}").status_code == 404
    invalid = owner.post('/api/v1/cart/items', json={'product_variant_id': 2147483647, 'quantity': 1})
    assert invalid.status_code == 404
    assert owner.get('/api/v1/cart').json()['items'] == before['items']


def test_logout_retires_claimed_cart_cookie_without_destroying_customer_cart():
    customer = TestClient(app)
    add(customer, 'Saved customer basket', 2)
    login(customer, 'merge-logout@example.com')
    saved = customer.get('/api/v1/cart').json()
    revoked_token = customer.cookies['session_token']
    assert customer.post('/api/v1/auth/logout').status_code == 200
    assert customer.get('/api/v1/auth/me').status_code == 401
    assert 'guest_cart_token' not in customer.cookies
    replay = TestClient(app)
    replay.cookies.set('session_token', revoked_token)
    assert replay.get('/api/v1/auth/me').status_code == 401
    assert replay.get('/api/v1/cart').json()['items'] == []
    add(customer, 'New anonymous basket', 1)
    assert customer.get('/api/v1/cart').json()['itemCount'] == 1
    returning = TestClient(app)
    login(returning, 'merge-logout@example.com')
    assert returning.get('/api/v1/cart').json()['items'] == saved['items']
