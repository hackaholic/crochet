"""Pytest test configuration and fixtures."""

import os
import sys
from urllib.parse import urlparse
import pytest

os.environ["TESTING"] = "true"
os.environ["APP_ENV"] = "development"
os.environ["EMAIL_PROVIDER"] = "mock"
os.environ["SMS_PROVIDER"] = "mock"
os.environ["PAYMENT_PROVIDER"] = "mock"

# Check if DATABASE_URL_FILE is configured
db_url_file = os.environ.get("DATABASE_URL_FILE")
if db_url_file:
    filename = os.path.basename(db_url_file).lower()
    if "test" not in filename:
        raise RuntimeError(
            f"Unsafe test configuration: DATABASE_URL_FILE='{db_url_file}' points to a non-test secret file. "
            "Tests refuse to run against shared development or preprod databases."
        )

# Prioritize TEST_DATABASE_URL if provided
if os.environ.get("TEST_DATABASE_URL"):
    os.environ["DATABASE_URL"] = os.environ["TEST_DATABASE_URL"]

# Validate resolved DATABASE_URL
target_url = os.environ.get("DATABASE_URL")
if target_url:
    target_lower = target_url.lower()
    if "preprod" in target_lower or "sulocraft.com" in target_lower:
        raise RuntimeError(
            "Unsafe test configuration: DATABASE_URL targets production/preprod. "
            "Tests refuse to run against shared or production databases."
        )
    if target_lower.startswith("postgres"):
        parsed = urlparse(target_url)
        db_name = parsed.path.lstrip("/").split("?")[0]
        if not db_name or "test" not in db_name.lower():
            raise RuntimeError(
                f"Unsafe test configuration: PostgreSQL database name '{db_name}' does not contain 'test'. "
                "Tests must run only against an isolated test database (e.g. sulocraft_test)."
            )
    elif target_lower.startswith("sqlite"):
        if not (":memory:" in target_lower or "test" in target_lower):
            raise RuntimeError(
                "Unsafe test configuration: SQLite database path does not contain 'test' or ':memory:'. "
                "Tests must run only against an isolated test database."
            )
else:
    # Default to an isolated test SQLite database if not specified
    os.environ["DATABASE_URL"] = "sqlite:///./test_sulocraft.db"

from app.db.seed import seed_catalogue
from app.db.session import SessionLocal, init_db, engine
from app.models import (
    Address,
    Cart,
    CartItem,
    Category,
    Coupon,
    NotificationLog,
    Order,
    OrderItem,
    OrderStatusHistory,
    OtpVerification,
    Payment,
    Product,
    ProductImage,
    ProductCollection,
    ProductOccasion,
    ProductVariant,
    ReturnRequest,
    Review,
    SearchEvent,
    User,
    UserIdentity,
    UserSession,
    Wishlist,
    WishlistItem,
)
from app.models.catalogue import ProductInformationDefaults, product_tags, product_collections, product_occasions
from app.models.expense import AdminExpense
from app.models.user import MagicLinkToken

SEEDED_PRODUCT_IDS: set[int] = set()
SEEDED_VARIANT_IDS: set[int] = set()
SEEDED_REVIEW_IDS: set[int] = set()
SEEDED_CATEGORY_IDS: set[int] = set()
SEEDED_USER_IDS: set[int] = set()
SEEDED_IMAGE_IDS: set[int] = set()


from app.db.seed import align_postgres_sequences, seed_catalogue


def reset_postgres_sequences(session):
    """Synchronize PostgreSQL sequences without rewinding using seed.align_postgres_sequences."""
    align_postgres_sequences(session)
    session.commit()


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Ensure database schema is created and seeded before running tests."""
    init_db()
    with SessionLocal() as db:
        seed_catalogue(db)

        global SEEDED_PRODUCT_IDS, SEEDED_VARIANT_IDS, SEEDED_REVIEW_IDS, SEEDED_CATEGORY_IDS, SEEDED_USER_IDS, SEEDED_IMAGE_IDS
        SEEDED_PRODUCT_IDS = {p[0] for p in db.query(Product.id).all()}
        SEEDED_VARIANT_IDS = {v[0] for v in db.query(ProductVariant.id).all()}
        SEEDED_REVIEW_IDS = {r[0] for r in db.query(Review.id).all()}
        SEEDED_CATEGORY_IDS = {c[0] for c in db.query(Category.id).all()}
        SEEDED_USER_IDS = {u[0] for u in db.query(User.id).all()}
        SEEDED_IMAGE_IDS = {i[0] for i in db.query(ProductImage.id).all()}
    yield
    # Cleanup SQLite test database file if created
    current_db = os.environ.get("DATABASE_URL", "")
    if current_db.startswith("sqlite:///./test_"):
        sqlite_file = current_db.replace("sqlite:///./", "")
        if os.path.exists(sqlite_file):
            try:
                os.remove(sqlite_file)
            except OSError:
                pass


@pytest.fixture(autouse=True)
def clean_transactional_data():
    """Clean transactional and test-created data after each test."""
    from app.api.v1.catalogue import reset_search_event_rate_limit_store
    reset_search_event_rate_limit_store()
    yield
    reset_search_event_rate_limit_store()
    with SessionLocal() as db:
        db.query(MagicLinkToken).delete()
        db.query(NotificationLog).delete()
        db.query(SearchEvent).delete()
        db.query(AdminExpense).delete()
        db.query(Payment).delete()
        db.query(OrderItem).delete()
        db.query(ReturnRequest).delete()
        db.query(OrderStatusHistory).delete()
        db.query(Order).delete()
        db.query(Address).delete()
        db.query(WishlistItem).delete()
        db.query(Wishlist).delete()
        db.query(CartItem).delete()
        db.query(Cart).delete()
        db.query(Coupon).delete()
        db.query(OtpVerification).delete()
        db.query(UserSession).delete()
        db.query(UserIdentity).delete()

        # Reset storewide ProductInformationDefaults to seed defaults
        defaults = db.query(ProductInformationDefaults).first()
        if defaults:
            defaults.handmade_details = "Handcrafted with traditional crochet techniques. Each piece is made by hand with attention to detail; subtle variations are natural and make each item unique."
            defaults.materials_used = "Quality yarn and secure stitching tailored for crochet heirlooms."
            defaults.size_dimensions = "Dimensions vary by design; please refer to the product specifications."
            defaults.processing_time = "Processing time is confirmed for each order."
            defaults.care_instructions = "Gently spot clean or dust with a dry soft cloth. Keep away from excessive moisture and direct prolonged sunlight."
            defaults.shipping_delivery = "Shipping availability and delivery details are confirmed for each order."

        # Clean non-seeded users (preserving admin user seeded by seed_catalogue)
        if SEEDED_USER_IDS:
            db.query(User).filter(User.id.not_in(SEEDED_USER_IDS)).delete(synchronize_session=False)
        else:
            db.query(User).delete()

        # Clean non-seeded reviews dynamically without arbitrary primary-key thresholds
        if SEEDED_REVIEW_IDS:
            db.query(Review).filter(Review.id.not_in(SEEDED_REVIEW_IDS)).delete(synchronize_session=False)

        # Clean non-seeded products dynamically without arbitrary primary-key thresholds
        if SEEDED_PRODUCT_IDS:
            db.execute(product_tags.delete().where(product_tags.c.product_id.not_in(SEEDED_PRODUCT_IDS)))
            db.query(ProductVariant).filter(ProductVariant.product_id.not_in(SEEDED_PRODUCT_IDS)).delete(synchronize_session=False)
            db.query(ProductImage).filter(ProductImage.product_id.not_in(SEEDED_PRODUCT_IDS)).delete(synchronize_session=False)
            db.query(ProductCollection).filter(ProductCollection.product_id.not_in(SEEDED_PRODUCT_IDS)).delete(synchronize_session=False)
            db.query(ProductOccasion).filter(ProductOccasion.product_id.not_in(SEEDED_PRODUCT_IDS)).delete(synchronize_session=False)
            db.query(Product).filter(Product.id.not_in(SEEDED_PRODUCT_IDS)).delete(synchronize_session=False)
        if SEEDED_IMAGE_IDS:
            db.query(ProductImage).filter(ProductImage.id.not_in(SEEDED_IMAGE_IDS)).delete(synchronize_session=False)

        # Clean non-seeded categories
        if SEEDED_CATEGORY_IDS:
            db.query(Category).filter(Category.id.not_in(SEEDED_CATEGORY_IDS)).delete(synchronize_session=False)
        else:
            db.query(Category).filter(Category.slug.like("test-%")).delete()

        db.query(Product).update({"status": "ACTIVE"})
        if SEEDED_VARIANT_IDS:
            db.query(ProductVariant).filter(ProductVariant.id.in_(SEEDED_VARIANT_IDS)).update({"stock_quantity": 50}, synchronize_session=False)
        else:
            db.query(ProductVariant).update({"stock_quantity": 50})
        db.commit()

        reset_postgres_sequences(db)
