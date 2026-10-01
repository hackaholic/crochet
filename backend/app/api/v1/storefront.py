"""Public storefront API conforming to docs/api-storefront.md."""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.storefront import BrandSettings, HomepageCampaign
from app.schemas.storefront import BrandSettingsOut, HomepageCampaignOut, StorefrontResponse

router = APIRouter(prefix="/storefront", tags=["storefront"])


@router.get("", response_model=StorefrontResponse)
def get_storefront_content(db: Session = Depends(get_db)) -> StorefrontResponse:
    """Retrieve public brand profile and active scheduled homepage campaigns."""
    # 1. Fetch brand settings or provide default
    brand = db.query(BrandSettings).order_by(BrandSettings.id.asc()).first()
    if not brand:
        brand_out = BrandSettingsOut(
            name="Sulocraft",
            owner_name="Anupama",
            instagram_url="https://instagram.com/sulocraft",
            whatsapp_url="https://wa.me/919876543210",
        )
    else:
        brand_out = BrandSettingsOut.model_validate(brand)

    # 2. Fetch active campaigns within schedule, ordered by priority (max 5)
    now = datetime.now(timezone.utc)
    campaigns = (
        db.query(HomepageCampaign)
        .filter(
            HomepageCampaign.is_active.is_(True),
            or_(HomepageCampaign.starts_at.is_(None), HomepageCampaign.starts_at <= now),
            or_(HomepageCampaign.ends_at.is_(None), HomepageCampaign.ends_at >= now),
        )
        .order_by(HomepageCampaign.priority.asc(), HomepageCampaign.id.asc())
        .limit(5)
        .all()
    )

    hero_campaigns = [HomepageCampaignOut.model_validate(c) for c in campaigns]

    return StorefrontResponse(
        brand=brand_out,
        hero_campaigns=hero_campaigns,
    )
