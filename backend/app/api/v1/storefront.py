"""Public storefront API conforming to docs/api-storefront.md."""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api.v1.catalogue import _to_product_list_item
from app.db.session import get_db
from app.models.catalogue import Category, Collection, Product, Review, Tag
from app.models.storefront import BrandSettings, HomepageCampaign, HomepageSection
from app.schemas.storefront import (
    BrandSettingsOut,
    CategoryGridSectionOut,
    CategorySummary,
    HomepageCampaignOut,
    ImageTextSectionOut,
    ProductCollectionSectionOut,
    PromoBannerSectionOut,
    ReviewSectionOut,
    ReviewSummary,
    StorefrontHomeResponse,
    StorefrontResponse,
)

router = APIRouter(prefix="/storefront", tags=["storefront"])


def _resolve_homepage_section(db: Session, section: HomepageSection):
    """Resolve catalogue and content references for an approved section template."""
    sec_type = (section.section_type or "").lower().strip()

    if sec_type == "category_grid":
        cat_ids = (section.metadata_json or {}).get("category_ids") if isinstance(section.metadata_json, dict) else None
        cat_slugs = (section.metadata_json or {}).get("category_slugs") if isinstance(section.metadata_json, dict) else None

        if cat_ids:
            cats = db.query(Category).filter(Category.id.in_(cat_ids), Category.is_active.is_(True)).all()
            # Preserve ordering of specified IDs
            cat_map = {c.id: c for c in cats}
            ordered_cats = [cat_map[cid] for cid in cat_ids if cid in cat_map]
        elif cat_slugs:
            cats = db.query(Category).filter(Category.slug.in_(cat_slugs), Category.is_active.is_(True)).all()
            cat_map = {c.slug: c for c in cats}
            ordered_cats = [cat_map[slug] for slug in cat_slugs if slug in cat_map]
        else:
            limit = section.item_limit or 4
            ordered_cats = (
                db.query(Category)
                .filter(Category.parent_id.is_(None), Category.is_active.is_(True))
                .order_by(Category.display_order.asc(), Category.id.asc())
                .limit(limit)
                .all()
            )

        cat_summaries = [
            CategorySummary(
                id=c.id,
                name=c.name,
                slug=c.slug,
                description=c.description,
                image_url=c.image_key or c.image or "",
            )
            for c in ordered_cats
        ]
        return CategoryGridSectionOut(
            id=section.id,
            order=section.display_order,
            enabled=section.is_enabled,
            title=section.title,
            eyebrow=section.eyebrow,
            categories=cat_summaries,
        )

    elif sec_type == "product_collection":
        slug = (section.collection_slug or "bestsellers").lower().strip()
        limit = section.item_limit or 4
        query = db.query(Product).filter(Product.status == "ACTIVE")

        if slug in ("bestsellers", "best-sellers"):
            col = db.query(Collection).filter(Collection.slug.in_(["bestsellers", "best-sellers"]), Collection.is_active == True).first()
            if col and col.products:
                products = [p for p in col.products if p.status == "ACTIVE"][:limit]
            else:
                bestsellers = query.filter(Product.badge == "Bestseller").order_by(Product.rating.desc(), Product.reviews_count.desc()).limit(limit).all()
                if len(bestsellers) < limit:
                    # Top rated/reviewed products as backfill
                    existing_ids = {p.id for p in bestsellers}
                    extras = (
                        query.filter(~Product.id.in_(existing_ids))
                        .order_by(Product.reviews_count.desc(), Product.rating.desc())
                        .limit(limit - len(bestsellers))
                        .all()
                    )
                    products = bestsellers + extras
                else:
                    products = bestsellers
        elif slug in ("new-arrivals", "new"):
            col = db.query(Collection).filter(Collection.slug.in_(["new-arrivals", "new"]), Collection.is_active == True).first()
            if col and col.products:
                products = [p for p in col.products if p.status == "ACTIVE"][:limit]
            else:
                products = query.order_by(Product.id.desc()).limit(limit).all()
        else:
            # Check if matching collection slug
            col = db.query(Collection).filter(Collection.slug == slug, Collection.is_active == True).first()
            if col and col.products:
                products = [p for p in col.products if p.status == "ACTIVE"][:limit]
            else:
                # Check if matching category slug
                category = db.query(Category).filter(Category.slug == slug).first()
                if category:
                    category_ids = [category.id] + [ch.id for ch in category.children]
                    products = query.filter(Product.categories.any(Category.id.in_(category_ids))).limit(limit).all()
                else:
                    # Check tag
                    tag = db.query(Tag).filter(Tag.name.ilike(slug)).first()
                    if tag:
                        products = query.filter(Product.tags.any(Tag.id == tag.id)).limit(limit).all()
                    else:
                        products = query.limit(limit).all()

        items = [_to_product_list_item(p) for p in products]
        return ProductCollectionSectionOut(
            id=section.id,
            order=section.display_order,
            enabled=section.is_enabled,
            title=section.title,
            eyebrow=section.eyebrow,
            collection_slug=section.collection_slug or "bestsellers",
            products=items,
        )

    elif sec_type == "promo_banner":
        return PromoBannerSectionOut(
            id=section.id,
            order=section.display_order,
            enabled=section.is_enabled,
            title=section.title,
            description=section.description,
            image_url=section.image_url,
            image_alt=section.image_alt,
            cta_text=section.cta_text,
            cta_url=section.cta_url,
        )

    elif sec_type == "review_section":
        review_ids = (section.metadata_json or {}).get("review_ids") if isinstance(section.metadata_json, dict) else None
        limit = section.item_limit or 3

        if review_ids:
            reviews = db.query(Review).filter(Review.id.in_(review_ids)).all()
            rev_map = {r.id: r for r in reviews}
            ordered_reviews = [rev_map[rid] for rid in review_ids if rid in rev_map]
        else:
            ordered_reviews = (
                db.query(Review)
                .filter(Review.rating >= 4)
                .order_by(Review.rating.desc(), Review.id.asc())
                .limit(limit)
                .all()
            )
            if not ordered_reviews:
                ordered_reviews = db.query(Review).order_by(Review.id.asc()).limit(limit).all()

        review_summaries = [
            ReviewSummary(
                id=r.id,
                author_name=r.author_name or "Verified Customer",
                location=r.location,
                rating=r.rating or 5,
                text=r.text or "",
                avatar_url=r.avatar_url,
            )
            for r in ordered_reviews
        ]
        return ReviewSectionOut(
            id=section.id,
            order=section.display_order,
            enabled=section.is_enabled,
            title=section.title,
            reviews=review_summaries,
        )

    elif sec_type == "image_text":
        pos = "right" if (section.image_position or "").lower() == "right" else "left"
        return ImageTextSectionOut(
            id=section.id,
            order=section.display_order,
            enabled=section.is_enabled,
            title=section.title,
            description=section.description or "",
            image_url=section.image_url or "",
            image_alt=section.image_alt or "",
            image_position=pos,
            cta_text=section.cta_text,
            cta_url=section.cta_url,
        )

    # Unknown section template type ignored safely per docs/api-storefront.md
    return None


@router.get("/home", response_model=StorefrontHomeResponse)
def get_storefront_home(db: Session = Depends(get_db)) -> StorefrontHomeResponse:
    """Retrieve full dynamic storefront homepage with brand, hero campaigns, and resolved sections."""
    # 1. Fetch brand settings
    brand = db.query(BrandSettings).order_by(BrandSettings.id.asc()).first()
    if not brand:
        brand_out = BrandSettingsOut(
            name="Sulocraft",
            owner_name="Anupama Sharma",
            instagram_url="https://instagram.com/sulocraft",
            whatsapp_url="https://wa.me/919876543210",
        )
    else:
        brand_out = BrandSettingsOut.model_validate(brand)

    # 2. Fetch active scheduled campaigns (hero)
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

    # 3. Fetch active scheduled homepage sections ordered by display_order
    sections_db = (
        db.query(HomepageSection)
        .filter(
            HomepageSection.is_enabled.is_(True),
            or_(HomepageSection.starts_at.is_(None), HomepageSection.starts_at <= now),
            or_(HomepageSection.ends_at.is_(None), HomepageSection.ends_at >= now),
        )
        .order_by(HomepageSection.display_order.asc(), HomepageSection.id.asc())
        .all()
    )

    resolved_sections = []
    for sec in sections_db:
        res = _resolve_homepage_section(db, sec)
        if res is not None:
            resolved_sections.append(res)

    return StorefrontHomeResponse(
        brand=brand_out,
        hero=hero_campaigns,
        hero_campaigns=hero_campaigns,
        sections=resolved_sections,
    )


@router.get("", response_model=StorefrontResponse)
def get_storefront_content(db: Session = Depends(get_db)) -> StorefrontResponse:
    """Retrieve public brand profile and active scheduled homepage campaigns (legacy compatibility)."""
    # 1. Fetch brand settings or provide default
    brand = db.query(BrandSettings).order_by(BrandSettings.id.asc()).first()
    if not brand:
        brand_out = BrandSettingsOut(
            name="Sulocraft",
            owner_name="Anupama Sharma",
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
