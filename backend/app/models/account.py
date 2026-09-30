"""Customer Account and Wishlist models conforming to Sections 19 & 27 of the Specification."""

from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.base import Base


class Wishlist(Base):
    """Customer wishlist container."""

    __tablename__ = "wishlists"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="wishlist")
    items = relationship(
        "WishlistItem",
        back_populates="wishlist",
        cascade="all, delete-orphan",
        order_by="WishlistItem.id.desc()",
    )


class WishlistItem(Base):
    """Product bookmarked in a customer's wishlist."""

    __tablename__ = "wishlist_items"

    id = Column(Integer, primary_key=True, index=True)
    wishlist_id = Column(Integer, ForeignKey("wishlists.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        UniqueConstraint("wishlist_id", "product_id", name="uq_wishlist_product"),
    )

    wishlist = relationship("Wishlist", back_populates="items")
    product = relationship("Product")
