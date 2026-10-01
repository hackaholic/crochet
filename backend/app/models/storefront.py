"""Database models for Storefront content: BrandSettings and HomepageCampaign."""

from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text

from app.db.base import Base


class BrandSettings(Base):
    """Storewide brand configuration and social links."""

    __tablename__ = "brand_settings"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, default="Sulocraft")
    owner_name = Column(String(100), nullable=False, default="Anupama")
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
