"""Tests for Asset Storage, Cloudflare R2 uploads, and Cache-Control headers."""

import io
from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.models.user import User, UserIdentity

client = TestClient(app)


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

    res = client.post("/api/v1/auth/google", json={
        "credential": "mock_admin_token_storage",
        "email": admin_email,
        "name": "Store Admin",
        "sub": "admin_sub_storage",
    })
    assert res.status_code == 200
    assert res.json()["user"]["role"] == "ADMIN"
    return dict(res.cookies)


def test_admin_image_upload_success():
    """Verify admin can upload a product image and receive an images.sulocraft.com CDN URL."""
    admin_cookies = _login_admin()
    test_image_bytes = b"fake-webp-binary-content-for-testing"
    files = {
        "file": ("rose-flower.webp", io.BytesIO(test_image_bytes), "image/webp"),
    }

    res = client.post("/api/v1/admin/images/upload", files=files, cookies=admin_cookies)
    assert res.status_code == 200
    data = res.json()
    assert "url" in data
    assert data["url"].startswith("https://images.sulocraft.com/products/")
    assert data["key"].startswith("products/")
    assert data["key"].endswith(".webp")
    assert data["contentType"] == "image/webp"
    assert data["size"] == len(test_image_bytes)


def test_admin_image_upload_invalid_type_rejected():
    """Verify non-image files are rejected with HTTP 400."""
    admin_cookies = _login_admin()
    files = {
        "file": ("document.pdf", io.BytesIO(b"fake-pdf-content"), "application/pdf"),
    }

    res = client.post("/api/v1/admin/images/upload", files=files, cookies=admin_cookies)
    assert res.status_code == 400
    assert "Unsupported image type" in res.json()["detail"]


def test_unauthorized_image_upload_rejected():
    """Verify unauthenticated requests cannot upload images."""
    anon_client = TestClient(app)
    files = {
        "file": ("test.png", io.BytesIO(b"fake-png-content"), "image/png"),
    }
    res = anon_client.post("/api/v1/admin/images/upload", files=files)
    assert res.status_code == 401


def test_cloudflare_cache_control_headers():
    """Verify sensitive customer endpoints return Cache-Control: no-store, no-cache."""
    # Cart endpoint
    res_cart = client.get("/api/v1/cart")
    assert "no-store" in res_cart.headers.get("Cache-Control", "")
    assert "no-cache" in res_cart.headers.get("Cache-Control", "")

    # Auth me endpoint
    res_auth = client.get("/api/v1/auth/me")
    assert "no-store" in res_auth.headers.get("Cache-Control", "")
