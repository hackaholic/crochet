"""Automated tests for Work 001 Task 1.7.11: Seeded catalogue ID sequence alignment."""

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.db.seed import align_postgres_sequences, seed_catalogue
from app.db.session import SessionLocal
from app.main import app
from app.models.catalogue import Category, Product, Tag
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
        "credential": "mock_admin_token_seq_test",
        "email": admin_email,
        "name": "Store Admin",
        "sub": "admin_sub_seq_test",
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


# =============================================================================
# 1.7.11-TC01: Explicit high-ID seed then admin create with variant/categories/tags
# =============================================================================

def test_admin_product_create_succeeds_after_seed():
    """1.7.11-TC01: Admin can create product immediately after seed without ID collision."""
    with SessionLocal() as db:
        seed_catalogue(db)
        cat = db.query(Category).first()
        assert cat is not None
        cat_id = cat.id

    cookies = _login_admin()
    create_payload = {
        "name": "Sequence Verification Rose",
        "primaryImage": "products/seq_rose.jpg",
        "description": "Handcrafted rose verifying sequence alignment.",
        "badge": "Handmade",
        "customizable": False,
        "categoryIds": [cat_id],
        "primaryCategoryId": cat_id,
        "variants": [
            {
                "sku": "SKU-SEQ-ROSE-01",
                "name": "Single Stem",
                "price": 499,
                "stockQuantity": 15,
            }
        ],
    }

    res = client.post("/api/v1/admin/products", json=create_payload, cookies=cookies)
    assert res.status_code == 201, f"Product creation failed: {res.text}"
    data = res.json()
    assert data["name"] == "Sequence Verification Rose"
    # Seeded products have max ID 24/25, newly created product should have a higher ID
    assert data["id"] > 24
    assert len(data["variants"]) == 1
    assert data["variants"][0]["sku"] == "SKU-SEQ-ROSE-01"


# =============================================================================
# 1.7.11-TC02: Repeat seed with sequence already ahead (never rewind)
# =============================================================================

def test_sequence_never_rewinds_on_reseed():
    """1.7.11-TC02: If sequence is already ahead of MAX(id), repeat seeding does not rewind it."""
    with SessionLocal() as db:
        seed_catalogue(db)
        bind = db.get_bind()
        if not bind or bind.dialect.name != "postgresql":
            pytest.skip("PostgreSQL specific test")

        # Manually advance products_id_seq to 100
        db.execute(text("SELECT setval('products_id_seq', 100, true)"))
        db.commit()

        # Re-run align_postgres_sequences
        align_postgres_sequences(db)
        db.commit()

        # Verify sequence is still at 100, NOT rewound back to 25
        seq_val = db.execute(text("SELECT last_value FROM products_id_seq")).scalar()
        assert seq_val >= 100, f"Sequence rewound to {seq_val}"

        # Clean up products_id_seq back to MAX(id)
        max_id = db.execute(text("SELECT MAX(id) FROM products")).scalar()
        db.execute(text(f"SELECT setval('products_id_seq', {max_id}, true)"))
        db.commit()


# =============================================================================
# 1.7.11-TC03: Non-PostgreSQL test configuration (SQLite safe no-op)
# =============================================================================

def test_align_postgres_sequences_safe_on_sqlite():
    """1.7.11-TC03: align_postgres_sequences is a safe no-op on SQLite and non-PostgreSQL engines."""
    engine = create_engine("sqlite:///:memory:")
    Session = sessionmaker(bind=engine)
    with Session() as session:
        count = align_postgres_sequences(session)
        assert count == 0


# =============================================================================
# 1.7.11-TC04: Unauthenticated / Customer create attempt
# =============================================================================

def test_unauthenticated_and_customer_create_denied():
    """1.7.11-TC04: Unauthenticated and non-admin customer create attempts are rejected."""
    payload = {
        "name": "Unauthorized Rose",
        "primaryImage": "products/unauth.jpg",
    }
    # Unauthenticated
    res_anon = client.post("/api/v1/admin/products", json=payload)
    assert res_anon.status_code in (401, 403)

    # Customer
    cust_cookies = _login_customer()
    res_cust = client.post("/api/v1/admin/products", json=payload, cookies=cust_cookies)
    assert res_cust.status_code == 403


# =============================================================================
# 1.7.11-TC05: Empty tables sequence alignment prevention test (PostgreSQL)
# =============================================================================

def test_sequence_alignment_on_empty_tables():
    """1.7.11-TC05: Empty tables (count == 0) never trigger NumericValueOutOfRange setval(0) on Postgres."""
    with SessionLocal() as db:
        bind = db.get_bind()
        if not bind or bind.dialect.name != "postgresql":
            pytest.skip("PostgreSQL specific test")

        # Truncate addresses to guarantee 0 rows
        db.execute(text("TRUNCATE TABLE addresses RESTART IDENTITY CASCADE"))
        db.commit()

        # align_postgres_sequences must succeed without throwing NumericValueOutOfRange
        aligned = align_postgres_sequences(db)
        db.commit()

        # Verify inserting a new address gets sequence 1
        addr_id = db.execute(
            text(
                "INSERT INTO addresses (user_id, name, phone, line1, city, state, postal_code, country) "
                "VALUES (1, 'Test User', '9999999999', '123 St', 'City', 'State', '110001', 'India') RETURNING id"
            )
        ).scalar()
        db.commit()
        assert addr_id >= 1, f"Expected positive sequence id, got {addr_id}"


# =============================================================================
# 1.7.11-TC06: Cold-boot application lifespan startup test
# =============================================================================

def test_cold_boot_lifespan_startup():
    """1.7.11-TC06: Cold-boot application lifespan completes cleanly without exception."""
    import asyncio
    from app.main import lifespan

    async def _run_startup():
        async with lifespan(app):
            with SessionLocal() as db:
                prod_count = db.query(Product).count()
                assert prod_count > 0, "Catalogue products should be seeded on startup"

    asyncio.run(_run_startup())
