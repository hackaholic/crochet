"""Pydantic schemas for SEO Metadata Resolver conforming to docs/api-seo.md."""

from datetime import datetime
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.media import MediaMetadataOut


class SeoBreadcrumb(BaseModel):
    """Breadcrumb trail item for search engines and structured data."""

    model_config = ConfigDict(from_attributes=True)

    name: str
    path: str


class SeoFaqItem(BaseModel):
    """FAQ item for structured data Schema.org FAQPage and rich search snippets."""

    question: str
    answer: str


class SeoShippingInfo(BaseModel):
    """Shipping information for structured offers and merchant search details."""

    model_config = ConfigDict(populate_by_name=True)

    free_shipping_threshold: int = Field(default=999, serialization_alias="freeShippingThreshold", alias="freeShippingThreshold")
    standard_fee: int = Field(default=100, serialization_alias="standardFee", alias="standardFee")
    currency: str = Field(default="INR")
    transit_time: str = Field(default="3-5 business days", serialization_alias="transitTime", alias="transitTime")
    country: str = Field(default="IN")


class SeoReturnPolicy(BaseModel):
    """Merchant return policy details for rich snippets."""

    model_config = ConfigDict(populate_by_name=True)

    return_window_days: int = Field(default=7, serialization_alias="returnWindowDays", alias="returnWindowDays")
    policy_url: str = Field(default="/info/refund", serialization_alias="policyUrl", alias="policyUrl")
    return_fees: str = Field(default="Free for damaged or defective items", serialization_alias="returnFees", alias="returnFees")


class SeoBrandInfo(BaseModel):
    """Storewide brand configuration for Organization/WebSite structured data."""

    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(default="Sulocraft")
    legal_name: str | None = Field(default=None, serialization_alias="legalName", alias="legalName")
    logo_url: str | None = Field(default=None, serialization_alias="logoUrl", alias="logoUrl")
    owner_name: str | None = Field(default=None, serialization_alias="ownerName", alias="ownerName")
    instagram_url: str | None = Field(default=None, serialization_alias="instagramUrl", alias="instagramUrl")
    whatsapp_url: str | None = Field(default=None, serialization_alias="whatsappUrl", alias="whatsappUrl")
    same_as: list[str] = Field(default_factory=list, serialization_alias="sameAs", alias="sameAs")


class SeoProductVariant(BaseModel):
    """Product variant details for structured offer parity."""

    model_config = ConfigDict(populate_by_name=True)

    id: int
    sku: str
    name: str
    price: float
    price_paise: int = Field(..., serialization_alias="pricePaise", alias="pricePaise")
    stock_quantity: int = Field(..., serialization_alias="stockQuantity", alias="stockQuantity")
    in_stock: bool = Field(..., serialization_alias="inStock", alias="inStock")
    attributes: dict[str, Any] = Field(default_factory=dict)


class SeoAggregateRating(BaseModel):
    """Aggregate rating derived from verified product reviews."""

    model_config = ConfigDict(populate_by_name=True)

    rating_value: float = Field(..., serialization_alias="ratingValue", alias="ratingValue")
    review_count: int = Field(..., serialization_alias="reviewCount", alias="reviewCount")
    best_rating: float = Field(default=5.0, serialization_alias="bestRating", alias="bestRating")
    worst_rating: float = Field(default=1.0, serialization_alias="worstRating", alias="worstRating")
    provenance: str = Field(default="VERIFIED_REVIEWS")


class SeoProductEntity(BaseModel):
    """Truthful database-derived product entity for Product/Offer schema parity."""

    model_config = ConfigDict(populate_by_name=True)

    id: int
    name: str
    slug: str
    description: str | None = None
    sku: str
    price: float
    price_paise: int = Field(..., serialization_alias="pricePaise", alias="pricePaise")
    currency: str = Field(default="INR")
    in_stock: bool = Field(..., serialization_alias="inStock", alias="inStock")
    inventory_status: str = Field(..., serialization_alias="inventoryStatus", alias="inventoryStatus")
    brand: str = Field(default="Sulocraft")
    primary_category_name: str | None = Field(default=None, serialization_alias="primaryCategoryName", alias="primaryCategoryName")
    category_names: list[str] = Field(default_factory=list, serialization_alias="categoryNames", alias="categoryNames")
    image_urls: list[str] = Field(default_factory=list, serialization_alias="imageUrls", alias="imageUrls")
    media: list[MediaMetadataOut] = Field(default_factory=list)
    variants: list[SeoProductVariant] = Field(default_factory=list)
    aggregate_rating: SeoAggregateRating | None = Field(default=None, serialization_alias="aggregateRating", alias="aggregateRating")
    handmade_details: str | None = Field(default=None, serialization_alias="handmadeDetails", alias="handmadeDetails")
    materials_used: str | None = Field(default=None, serialization_alias="materialsUsed", alias="materialsUsed")
    size_dimensions: str | None = Field(default=None, serialization_alias="sizeDimensions", alias="sizeDimensions")
    care_instructions: str | None = Field(default=None, serialization_alias="careInstructions", alias="careInstructions")
    shipping_delivery: str | None = Field(default=None, serialization_alias="shippingDelivery", alias="shippingDelivery")
    processing_time: str | None = Field(default=None, serialization_alias="processingTime", alias="processingTime")


class SeoCategoryEntity(BaseModel):
    """Truthful category entity hierarchy and metadata."""

    model_config = ConfigDict(populate_by_name=True)

    id: int
    name: str
    slug: str
    description: str | None = None
    image_url: str | None = Field(default=None, serialization_alias="imageUrl", alias="imageUrl")
    image_alt: str | None = Field(default=None, serialization_alias="imageAlt", alias="imageAlt")
    image_width: int | None = Field(default=None, serialization_alias="imageWidth", alias="imageWidth")
    image_height: int | None = Field(default=None, serialization_alias="imageHeight", alias="imageHeight")
    image_type: str | None = Field(default=None, serialization_alias="imageType", alias="imageType")
    image_metadata: MediaMetadataOut | None = Field(default=None, serialization_alias="imageMetadata", alias="imageMetadata")
    parent_id: int | None = Field(default=None, serialization_alias="parentId", alias="parentId")
    parent_name: str | None = Field(default=None, serialization_alias="parentName", alias="parentName")
    parent_slug: str | None = Field(default=None, serialization_alias="parentSlug", alias="parentSlug")
    product_count: int = Field(default=0, serialization_alias="productCount", alias="productCount")


class SeoCollectionEntity(BaseModel):
    """Truthful collection entity metadata."""

    model_config = ConfigDict(populate_by_name=True)

    id: int
    name: str
    slug: str
    description: str | None = None
    image_url: str | None = Field(default=None, serialization_alias="imageUrl", alias="imageUrl")
    image_alt: str | None = Field(default=None, serialization_alias="imageAlt", alias="imageAlt")
    image_width: int | None = Field(default=None, serialization_alias="imageWidth", alias="imageWidth")
    image_height: int | None = Field(default=None, serialization_alias="imageHeight", alias="imageHeight")
    image_type: str | None = Field(default=None, serialization_alias="imageType", alias="imageType")
    image_metadata: MediaMetadataOut | None = Field(default=None, serialization_alias="imageMetadata", alias="imageMetadata")
    collection_type: str = Field(default="EVERGREEN", serialization_alias="collectionType", alias="collectionType")


class SeoMetadataOut(BaseModel):
    """Structured SEO metadata response for page head rendering."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    title: str
    description: str
    canonical_path: str = Field(..., serialization_alias="canonicalPath", alias="canonicalPath")
    canonical_url: str | None = Field(default=None, serialization_alias="canonicalUrl", alias="canonicalUrl")
    robots: Literal["index,follow", "noindex,nofollow"]
    h1: str | None = Field(default=None)
    image_url: str | None = Field(default=None, serialization_alias="imageUrl", alias="imageUrl")
    image_alt: str | None = Field(default=None, serialization_alias="imageAlt", alias="imageAlt")
    image_width: int | None = Field(default=None, serialization_alias="imageWidth", alias="imageWidth")
    image_height: int | None = Field(default=None, serialization_alias="imageHeight", alias="imageHeight")
    image_type: str | None = Field(default=None, serialization_alias="imageType", alias="imageType")
    image_metadata: MediaMetadataOut | None = Field(default=None, serialization_alias="imageMetadata", alias="imageMetadata")
    page_type: Literal["website", "product", "collection", "article"] = Field(
        ..., serialization_alias="pageType", alias="pageType"
    )
    breadcrumbs: list[SeoBreadcrumb] = Field(default_factory=list)
    faqs: list[SeoFaqItem] = Field(default_factory=list)
    shipping_info: SeoShippingInfo | None = Field(default=None, serialization_alias="shippingInfo", alias="shippingInfo")
    return_policy: SeoReturnPolicy | None = Field(default=None, serialization_alias="returnPolicy", alias="returnPolicy")
    brand: SeoBrandInfo | None = Field(default=None)
    product_entity: SeoProductEntity | None = Field(default=None, serialization_alias="productEntity", alias="productEntity")
    category_entity: SeoCategoryEntity | None = Field(default=None, serialization_alias="categoryEntity", alias="categoryEntity")
    collection_entity: SeoCollectionEntity | None = Field(default=None, serialization_alias="collectionEntity", alias="collectionEntity")
    http_status: int = Field(default=200, serialization_alias="httpStatus", alias="httpStatus")
    redirect_to: str | None = Field(default=None, serialization_alias="redirectTo", alias="redirectTo")



class SeoRouteItem(BaseModel):
    """An individual indexable public storefront route item."""

    model_config = ConfigDict(populate_by_name=True)

    path: str
    canonical_url: str = Field(..., serialization_alias="canonicalUrl", alias="canonicalUrl")
    page_type: Literal["website", "product", "collection", "article"] = Field(
        ..., serialization_alias="pageType", alias="pageType"
    )
    lastmod: str | None = Field(default=None)
    changefreq: Literal["always", "hourly", "daily", "weekly", "monthly", "yearly", "never"] = "weekly"
    priority: float = 0.8


class SeoRouteInventoryOut(BaseModel):
    """Complete inventory of all eligible public routes across the store."""

    model_config = ConfigDict(populate_by_name=True)

    total_routes: int = Field(..., serialization_alias="totalRoutes", alias="totalRoutes")
    routes: list[SeoRouteItem]
    generated_at: datetime = Field(..., serialization_alias="generatedAt", alias="generatedAt")


class SeoPageSnapshotItem(BaseModel):
    """A pre-rendered route entry containing full truthful metadata and structured data."""

    model_config = ConfigDict(populate_by_name=True)

    path: str
    metadata: SeoMetadataOut


class SeoSnapshotResponse(BaseModel):
    """Paginated snapshot response of public routes and their full metadata."""

    model_config = ConfigDict(populate_by_name=True)

    page: int
    limit: int
    total_count: int = Field(..., serialization_alias="totalCount", alias="totalCount")
    total_pages: int = Field(..., serialization_alias="totalPages", alias="totalPages")
    items: list[SeoPageSnapshotItem]
    version_hash: str = Field(..., serialization_alias="versionHash", alias="versionHash")
