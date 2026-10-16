"""API endpoints for SEO Metadata Resolution, Sitemap XML, and Robots.txt conforming to docs/api-seo.md."""

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.schemas.merchant import MerchantFeedResponse
from app.schemas.seo import SeoMetadataOut, SeoRouteInventoryOut, SeoSnapshotResponse
from app.services.seo import SeoService

router = APIRouter(prefix="/seo", tags=["seo"])


@router.get("/resolve", response_model=SeoMetadataOut)
def resolve_seo_metadata(
    path: str = Query(default="/", description="Relative pathname or full URL to resolve metadata for"),
    db: Session = Depends(get_db),
) -> SeoMetadataOut:
    """Resolve dynamic SEO metadata (title, description, canonical, robots, og:image, breadcrumbs) for any storefront path."""
    return SeoService.resolve_path(db, path)


@router.get("/routes", response_model=SeoRouteInventoryOut)
def get_public_routes(
    db: Session = Depends(get_db),
) -> SeoRouteInventoryOut:
    """Get complete database-driven inventory of all eligible public indexable routes across the storefront."""
    return SeoService.get_public_route_inventory(db)


@router.get("/snapshot", response_model=SeoSnapshotResponse)
def get_content_snapshot(
    page: int = Query(default=1, ge=1, description="Page number for snapshot pagination"),
    limit: int = Query(default=50, ge=1, le=200, description="Items per page"),
    db: Session = Depends(get_db),
) -> SeoSnapshotResponse:
    """Get paginated build snapshot containing fully resolved metadata and structured data for static pre-rendering."""
    return SeoService.get_content_snapshot(db, page=page, limit=limit)


@router.get("/sitemap.xml")
def get_sitemap_xml(
    db: Session = Depends(get_db),
) -> Response:
    """Generate dynamic XML sitemap containing all active products, categories, collections, and static pages."""
    content = SeoService.generate_sitemap_xml(db)
    return Response(content=content, media_type="application/xml")


@router.get("/robots.txt")
def get_robots_txt() -> Response:
    """Generate robots.txt specifying crawl directives and canonical sitemap URL."""
    content = SeoService.generate_robots_txt()
    return Response(content=content, media_type="text/plain")


@router.get("/merchant-feed.xml")
def get_merchant_feed_xml(
    db: Session = Depends(get_db),
) -> Response:
    """Generate dynamic Google Merchant Center XML product feed (RSS 2.0 with g: namespace)."""
    content = SeoService.generate_merchant_feed_xml(db)
    return Response(content=content, media_type="application/xml; charset=utf-8")


@router.get("/merchant-feed", response_model=MerchantFeedResponse)
def get_merchant_feed_json(
    db: Session = Depends(get_db),
) -> MerchantFeedResponse:
    """Get structured JSON product feed for programmatic inspection and audit."""
    return SeoService.get_merchant_feed_response(db)

