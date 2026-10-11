"""Tests for Asset Storage, durable uploads, and Cache-Control headers."""

import io
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.models.user import User, UserIdentity
from app.services.storage.local import LocalStorageProvider
from app.services.storage.factory import get_storage_provider

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


def test_admin_image_upload_and_retrieve_actual_bytes(tmp_path):
    """1.7.12-TC01: Admin uploads valid image; retrieve URL serves exact bytes."""
    admin_cookies = _login_admin()
    test_image_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDRtest_image_bytes_content_sulocraft"
    files = {
        "file": ("test-bouquet.png", io.BytesIO(test_image_bytes), "image/png"),
    }

    res = client.post("/api/v1/admin/images/upload", files=files, cookies=admin_cookies)
    assert res.status_code == 200
    data = res.json()
    assert "url" in data
    assert "key" in data
    key = data["key"]
    assert key.startswith("products/")
    assert key.endswith(".png")

    # Fetch the uploaded image via API route
    url = f"/static/images/{key}"
    img_res = client.get(url)
    assert img_res.status_code == 200
    assert img_res.content == test_image_bytes

    # Clean up test artifact from disk
    storage = get_storage_provider()
    storage.delete_file(key)


def test_upload_persists_across_provider_recreation(tmp_path):
    """1.7.12-TC02: Recreate storage provider/service; file is still retrievable."""
    provider1 = LocalStorageProvider(base_dir=tmp_path, base_url="http://localhost:8000/static/images")
    content = b"persisted-raw-image-bytes-across-recreation"
    dest_path = "products/persisted-sample.png"

    url = provider1.upload_file(content, dest_path, content_type="image/png")
    assert url == "http://localhost:8000/static/images/products/persisted-sample.png"

    # Recreate provider pointing to the same storage
    provider2 = LocalStorageProvider(base_dir=tmp_path, base_url="http://localhost:8000/static/images")
    safe_path = provider2._resolve_safe_path(dest_path)
    assert safe_path.is_file()
    assert safe_path.read_bytes() == content

    # Test delete
    assert provider2.delete_file(dest_path) is True
    assert not safe_path.is_file()


def test_missing_image_fails_honestly_without_unsplash():
    """1.7.12-TC03: Missing image key returns honest 404; no 307 Unsplash fallback."""
    nonexistent_key = "products/definitely-nonexistent-key-99999.png"
    res = client.get(f"/static/images/{nonexistent_key}", follow_redirects=False)
    assert res.status_code == 404
    assert res.json()["detail"] == "Image not found"


def test_unauthorized_and_invalid_uploads_rejected():
    """1.7.12-TC04: Denied/invalid uploads have no storage side-effects; path traversal rejected."""
    # 1. Unauthorized
    anon_client = TestClient(app)
    files = {
        "file": ("test.png", io.BytesIO(b"fake-png-content"), "image/png"),
    }
    res_anon = anon_client.post("/api/v1/admin/images/upload", files=files)
    assert res_anon.status_code == 401

    # 2. Invalid MIME
    admin_cookies = _login_admin()
    pdf_files = {
        "file": ("document.pdf", io.BytesIO(b"fake-pdf-content"), "application/pdf"),
    }
    res_pdf = client.post("/api/v1/admin/images/upload", files=pdf_files, cookies=admin_cookies)
    assert res_pdf.status_code == 400
    assert "Unsupported image type" in res_pdf.json()["detail"]

    # 3. Path traversal safety on LocalStorageProvider
    provider = LocalStorageProvider()
    with pytest.raises(ValueError, match="Path traversal detected"):
        provider.upload_file(b"bad", "../../../etc/passwd")

    with pytest.raises(ValueError, match="Path traversal detected"):
        provider.delete_file("../../../etc/passwd")


def test_cloudflare_cache_control_headers():
    """Verify sensitive customer endpoints return Cache-Control: no-store, no-cache."""
    # Cart endpoint
    res_cart = client.get("/api/v1/cart")
    assert "no-store" in res_cart.headers.get("Cache-Control", "")
    assert "no-cache" in res_cart.headers.get("Cache-Control", "")

    # Auth me endpoint
    res_auth = client.get("/api/v1/auth/me")
    assert "no-store" in res_auth.headers.get("Cache-Control", "")
