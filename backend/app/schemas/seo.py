"""Pydantic schemas for SEO Metadata Resolver conforming to docs/api-seo.md."""

from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class SeoBreadcrumb(BaseModel):
    """Breadcrumb trail item for search engines and structured data."""

    model_config = ConfigDict(from_attributes=True)

    name: str
    path: str


class SeoMetadataOut(BaseModel):
    """Structured SEO metadata response for page head rendering."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    title: str
    description: str
    canonical_path: str = Field(..., serialization_alias="canonicalPath", alias="canonicalPath")
    robots: Literal["index,follow", "noindex,nofollow"]
    image_url: str | None = Field(default=None, serialization_alias="imageUrl", alias="imageUrl")
    image_alt: str | None = Field(default=None, serialization_alias="imageAlt", alias="imageAlt")
    page_type: Literal["website", "product", "collection", "article"] = Field(
        ..., serialization_alias="pageType", alias="pageType"
    )
    breadcrumbs: list[SeoBreadcrumb] = Field(default_factory=list)
