"""Promotions and Coupon database models conforming to Section 34 of Specification."""

from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text

from app.db.base import Base


class Coupon(Base):
    """Discount promo coupon model supporting percentage and flat rupee discounts."""

    __tablename__ = "coupons"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(255), nullable=True)
    discount_type = Column(String(20), nullable=False)  # PERCENTAGE, FLAT
    discount_value = Column(Integer, nullable=False)  # Percentage value (e.g. 15 for 15%) or Rupees (e.g. 200)
    min_order_amount = Column(Integer, default=0, nullable=False)  # In INR Rupees
    max_discount_amount = Column(Integer, nullable=True)  # Cap for percentage discounts in INR Rupees
    usage_limit = Column(Integer, nullable=True)  # Nullable for unlimited
    usage_count = Column(Integer, default=0, nullable=False)
    valid_from = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    valid_until = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
