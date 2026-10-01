"""Pytest test configuration and fixtures."""

import os
os.environ["TESTING"] = "true"
os.environ["APP_ENV"] = "development"
os.environ["EMAIL_PROVIDER"] = "mock"
os.environ["SMS_PROVIDER"] = "mock"
os.environ["PAYMENT_PROVIDER"] = "mock"

import pytest
from app.db.seed import seed_catalogue
from app.db.session import SessionLocal, init_db
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
    ProductVariant,
    Review,
    User,
    UserIdentity,
    UserSession,
    Wishlist,
    WishlistItem,
)
from app.models.user import MagicLinkToken


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Ensure database schema is created and seeded before running tests."""
    init_db()
    with SessionLocal() as db:
        seed_catalogue(db)
    yield


@pytest.fixture(autouse=True)
def clean_transactional_data():
    """Clean payments, orders, addresses, carts, wishlists, sessions, users, and tokens after each test."""
    yield
    with SessionLocal() as db:
        db.query(MagicLinkToken).delete()
        db.query(NotificationLog).delete()
        db.query(Payment).delete()
        db.query(OrderItem).delete()
        db.query(OrderStatusHistory).delete()
        db.query(Order).delete()
        db.query(Address).delete()
        db.query(WishlistItem).delete()
        db.query(Wishlist).delete()
        db.query(CartItem).delete()
        db.query(Cart).delete()
        db.query(Coupon).delete()
        db.query(Review).filter(Review.id > 6).delete()
        db.query(OtpVerification).delete()
        db.query(UserSession).delete()
        db.query(UserIdentity).delete()
        db.query(User).delete()
        db.query(ProductVariant).update({"stock_quantity": 50})
        # Clean any dynamically created test products and test categories
        for tp in db.query(Product).filter(Product.id > 24).all():
            db.delete(tp)
        db.query(Category).filter(Category.slug.like("test-%")).delete()
        db.commit()
