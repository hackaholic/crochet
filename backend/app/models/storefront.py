"""Database models for Storefront content: BrandSettings and HomepageCampaign."""

from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, Integer, JSON, String, Text
from sqlalchemy.dialects.postgresql import JSONB

from app.db.base import Base


class BrandSettings(Base):
    """Storewide brand configuration and social links."""

    __tablename__ = "brand_settings"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, default="Sulocraft")
    owner_name = Column(String(100), nullable=False, default="Anupama Sharma")
    instagram_url = Column(String(255), nullable=True, default="https://instagram.com/sulocraft")
    whatsapp_url = Column(String(255), nullable=True, default="https://wa.me/919876543210")
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class HomepageCampaign(Base):
    """Hero campaigns displayed dynamically on the storefront homepage."""

    __tablename__ = "homepage_campaigns"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    emphasis = Column(String(100), nullable=True)
    description = Column(Text, nullable=False)
    eyebrow = Column(String(100), nullable=True)
    image_url = Column(String(500), nullable=False)
    image_alt = Column(String(255), nullable=False)
    mobile_image_url = Column(String(500), nullable=True)
    mobile_image_position = Column(JSON().with_variant(JSONB, "postgresql"), nullable=True)
    destination = Column(String(255), nullable=True)  # Storefront route, e.g. /shop?category=Gifts
    priority = Column(Integer, default=0, nullable=False, index=True)  # 1 = top priority
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    starts_at = Column(DateTime, nullable=True, index=True)
    ends_at = Column(DateTime, nullable=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class HomepageSection(Base):
    """Database-backed ordered and scheduled homepage section."""

    __tablename__ = "homepage_sections"

    id = Column(Integer, primary_key=True, index=True)
    section_type = Column(String(50), nullable=False, index=True)  # category_grid, product_collection, promo_banner, review_section, image_text
    title = Column(String(255), nullable=False)
    eyebrow = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)
    image_alt = Column(String(255), nullable=True)
    image_position = Column(String(20), nullable=True, default="left")  # left | right
    cta_text = Column(String(100), nullable=True)
    cta_url = Column(String(500), nullable=True)
    collection_slug = Column(String(100), nullable=True)  # bestsellers, flowers, etc.
    item_limit = Column(Integer, default=4, nullable=True)
    display_order = Column(Integer, default=0, nullable=False, index=True)
    is_enabled = Column(Boolean, default=True, nullable=False, index=True)
    starts_at = Column(DateTime, nullable=True, index=True)
    ends_at = Column(DateTime, nullable=True, index=True)
    metadata_json = Column(JSON().with_variant(JSONB, "postgresql"), default=dict)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

