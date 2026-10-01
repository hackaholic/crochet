"""API endpoints for SEO Metadata Resolution, Sitemap XML, and Robots.txt conforming to docs/api-seo.md."""

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.schemas.seo import SeoMetadataOut
from app.services.seo import SeoService

router = APIRouter(prefix="/seo", tags=["seo"])


@router.get("/resolve", response_model=SeoMetadataOut)
def resolve_seo_metadata(
    path: str = Query(default="/", description="Relative pathname or full URL to resolve metadata for"),
    db: Session = Depends(get_db),
) -> SeoMetadataOut:
    """Resolve dynamic SEO metadata (title, description, canonical, robots, og:image, breadcrumbs) for any storefront path."""
    return SeoService.resolve_path(db, path)


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
