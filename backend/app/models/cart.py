"""Cart and CartItem models conforming to Sections 6, 7, and 28 of the Specification."""

from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.db.base import Base


class Cart(Base):
    """Shopping cart entity supporting anonymous guests and authenticated users."""

    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, index=True)
    guest_token = Column(String(64), unique=True, index=True, nullable=True)
    user_id = Column(Integer, index=True, nullable=True)
    status = Column(String(20), default="ACTIVE", index=True)  # ACTIVE, CONVERTED, ABANDONED
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, nullable=True)

    items = relationship(
        "CartItem",
        back_populates="cart",
        cascade="all, delete-orphan",
        order_by="CartItem.id",
    )


class CartItem(Base):
    """Cart line item linking to a specific ProductVariant with quantity and personalization."""

    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey("carts.id", ondelete="CASCADE"), nullable=False, index=True)
    product_variant_id = Column(Integer, ForeignKey("product_variants.id", ondelete="CASCADE"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False, default=1)
    personalization_json = Column(JSON().with_variant(JSONB, "postgresql"), default=dict)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    cart = relationship("Cart", back_populates="items")
    variant = relationship("ProductVariant")
