"""Pydantic schemas for Storefront and Brand content conforming to docs/api-storefront.md."""

from datetime import datetime
from typing import Annotated, Any, Literal, Union
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.images import build_image_url
from app.schemas.catalogue import ProductListItem


class BrandSettingsOut(BaseModel):
    """Public brand profile representation."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    name: str = "Sulocraft"
    owner_name: str = Field(default="Anupama Sharma", serialization_alias="ownerName", alias="ownerName")
    instagram_url: str | None = Field(default=None, serialization_alias="instagramUrl", alias="instagramUrl")
    whatsapp_url: str | None = Field(default=None, serialization_alias="whatsappUrl", alias="whatsappUrl")


class BrandSettingsUpdate(BaseModel):
    """Payload to update storewide brand settings."""

    model_config = ConfigDict(populate_by_name=True)

    name: str | None = None
    owner_name: str | None = Field(default=None, alias="ownerName")
    instagram_url: str | None = Field(default=None, alias="instagramUrl")
    whatsapp_url: str | None = Field(default=None, alias="whatsappUrl")


class HomepageCampaignOut(BaseModel):
    """Public homepage campaign item representation."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    title: str
    emphasis: str | None = None
    description: str
    eyebrow: str | None = None
    image_url: str = Field(..., serialization_alias="imageUrl", alias="imageUrl")
    image_alt: str = Field(..., serialization_alias="imageAlt", alias="imageAlt")
    destination: str | None = None
    priority: int = 0
    starts_at: datetime | None = Field(default=None, serialization_alias="startsAt", alias="startsAt")
    ends_at: datetime | None = Field(default=None, serialization_alias="endsAt", alias="endsAt")

    @field_validator("image_url", mode="after")
    @classmethod
    def resolve_image_url(cls, v: str) -> str:
        return build_image_url(v) if v else v


class StorefrontResponse(BaseModel):
    """Public storefront aggregate response for the homepage (legacy compatibility)."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    brand: BrandSettingsOut
    hero_campaigns: list[HomepageCampaignOut] = Field(default_factory=list, serialization_alias="heroCampaigns")


# -----------------------------------------------------------------------------
# Controlled Homepage Sections Schemas
# -----------------------------------------------------------------------------

class CategorySummary(BaseModel):
    """Summarized category for homepage category grids."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    name: str
    slug: str
    description: str | None = None
    image_url: str = Field(default="", serialization_alias="imageUrl", alias="imageUrl")

    @field_validator("image_url", mode="after")
    @classmethod
    def resolve_image_url(cls, v: str) -> str:
        return build_image_url(v) if v else v


class ReviewSummary(BaseModel):
    """Summarized customer testimonial for homepage review section."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    author_name: str = Field(..., serialization_alias="authorName", alias="authorName")
    location: str | None = None
    rating: int = 5
    text: str
    avatar_url: str | None = Field(default=None, serialization_alias="avatarUrl", alias="avatarUrl")

    @field_validator("avatar_url", mode="after")
    @classmethod
    def resolve_avatar_url(cls, v: str | None) -> str | None:
        return build_image_url(v) if v else None


class BaseHomepageSectionOut(BaseModel):
    """Base fields shared by all homepage section templates."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    order: int
    enabled: bool = True


class CategoryGridSectionOut(BaseHomepageSectionOut):
    """Controlled category grid section template."""

    type: Literal["category_grid"] = "category_grid"
    title: str
    eyebrow: str | None = None
    categories: list[CategorySummary] = Field(default_factory=list)


class ProductCollectionSectionOut(BaseHomepageSectionOut):
    """Controlled product collection carousel/grid section template."""

    type: Literal["product_collection"] = "product_collection"
    title: str
    eyebrow: str | None = None
    description: str | None = None
    collection_slug: str = Field(..., serialization_alias="collectionSlug", alias="collectionSlug")
    products: list[ProductListItem] = Field(default_factory=list)


class PromoBannerSectionOut(BaseHomepageSectionOut):
    """Controlled promotional banner section template."""

    type: Literal["promo_banner"] = "promo_banner"
    title: str
    description: str | None = None
    image_url: str | None = Field(default=None, serialization_alias="imageUrl", alias="imageUrl")
    image_alt: str | None = Field(default=None, serialization_alias="imageAlt", alias="imageAlt")
    cta_text: str | None = Field(default=None, serialization_alias="ctaText", alias="ctaText")
    cta_url: str | None = Field(default=None, serialization_alias="ctaUrl", alias="ctaUrl")

    @field_validator("image_url", mode="after")
    @classmethod
    def resolve_image_url(cls, v: str | None) -> str | None:
        return build_image_url(v) if v else None


class ReviewSectionOut(BaseHomepageSectionOut):
    """Controlled customer reviews section template."""

    type: Literal["review_section"] = "review_section"
    title: str
    reviews: list[ReviewSummary] = Field(default_factory=list)


class ImageTextSectionOut(BaseHomepageSectionOut):
    """Controlled artisanal story/craft editorial section template."""

    type: Literal["image_text"] = "image_text"
    title: str
    description: str
    image_url: str = Field(default="", serialization_alias="imageUrl", alias="imageUrl")
    image_alt: str = Field(default="", serialization_alias="imageAlt", alias="imageAlt")
    image_position: Literal["left", "right"] = Field(
        default="left",
        serialization_alias="imagePosition",
        alias="imagePosition",
    )
    cta_text: str | None = Field(default=None, serialization_alias="ctaText", alias="ctaText")
    cta_url: str | None = Field(default=None, serialization_alias="ctaUrl", alias="ctaUrl")

    @field_validator("image_url", mode="after")
    @classmethod
    def resolve_image_url(cls, v: str) -> str:
        return build_image_url(v) if v else v


class OccasionSummary(BaseModel):
    """Occasion item representation for storefront navigation."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    name: str
    icon: str | None = None
    image_url: str | None = Field(default=None, serialization_alias="imageUrl", alias="imageUrl")
    display_order: int = Field(default=0, serialization_alias="displayOrder", alias="displayOrder")
    description: str | None = None

    @field_validator("image_url", mode="after")
    @classmethod
    def resolve_image_url(cls, v: str | None) -> str | None:
        return build_image_url(v) if v else v


class OccasionGridSectionOut(BaseHomepageSectionOut):
    """Controlled occasion card grid section template."""

    type: Literal["occasion_grid"] = "occasion_grid"
    title: str
    eyebrow: str | None = None
    description: str | None = None
    occasions: list[OccasionSummary] = Field(default_factory=list)


HomepageSectionOut = Annotated[
    Union[
        CategoryGridSectionOut,
        ProductCollectionSectionOut,
        OccasionGridSectionOut,
        PromoBannerSectionOut,
        ReviewSectionOut,
        ImageTextSectionOut,
    ],
    Field(discriminator="type"),
]


class StorefrontHomeResponse(BaseModel):
    """Comprehensive dynamic storefront homepage composition response."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    brand: BrandSettingsOut
    hero: list[HomepageCampaignOut] = Field(default_factory=list)
    hero_campaigns: list[HomepageCampaignOut] = Field(default_factory=list, serialization_alias="heroCampaigns")
    sections: list[HomepageSectionOut] = Field(default_factory=list)



class AdminHomepageCampaignOut(HomepageCampaignOut):
    """Admin detailed representation of a homepage campaign including status."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    is_active: bool = Field(default=True, serialization_alias="isActive", alias="isActive")
    created_at: datetime | None = Field(default=None, serialization_alias="createdAt")
    updated_at: datetime | None = Field(default=None, serialization_alias="updatedAt")


class AdminHomepageCampaignCreate(BaseModel):
    """Admin payload to create a new homepage campaign."""

    model_config = ConfigDict(populate_by_name=True)

    title: str
    emphasis: str | None = None
    description: str
    eyebrow: str | None = None
    image_url: str = Field(..., alias="imageUrl")
    image_alt: str = Field(..., alias="imageAlt")
    destination: str | None = None
    priority: int = 0
    is_active: bool = Field(default=True, alias="isActive")
    starts_at: datetime | None = Field(default=None, alias="startsAt")
    ends_at: datetime | None = Field(default=None, alias="endsAt")


class AdminHomepageCampaignUpdate(BaseModel):
    """Admin payload to update an existing homepage campaign."""

    model_config = ConfigDict(populate_by_name=True)

    title: str | None = None
    emphasis: str | None = None
    description: str | None = None
    eyebrow: str | None = None
    image_url: str | None = Field(default=None, alias="imageUrl")
    image_alt: str | None = Field(default=None, alias="imageAlt")
    destination: str | None = None
    priority: int | None = None
    is_active: bool | None = Field(default=None, alias="isActive")
    starts_at: datetime | None = Field(default=None, alias="startsAt")
    ends_at: datetime | None = Field(default=None, alias="endsAt")


class AdminHomepageSectionOut(BaseModel):
    """Admin detailed representation of a homepage section."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    section_type: str = Field(..., serialization_alias="sectionType", alias="sectionType")
    title: str
    eyebrow: str | None = None
    description: str | None = None
    image_url: str | None = Field(default=None, serialization_alias="imageUrl", alias="imageUrl")
    image_alt: str | None = Field(default=None, serialization_alias="imageAlt", alias="imageAlt")
    image_position: str | None = Field(default="left", serialization_alias="imagePosition", alias="imagePosition")
    cta_text: str | None = Field(default=None, serialization_alias="ctaText", alias="ctaText")
    cta_url: str | None = Field(default=None, serialization_alias="ctaUrl", alias="ctaUrl")
    collection_slug: str | None = Field(default=None, serialization_alias="collectionSlug", alias="collectionSlug")
    item_limit: int | None = Field(default=4, serialization_alias="itemLimit", alias="itemLimit")
    display_order: int = Field(default=0, serialization_alias="displayOrder", alias="displayOrder")
    is_enabled: bool = Field(default=True, serialization_alias="isEnabled", alias="isEnabled")
    starts_at: datetime | None = Field(default=None, serialization_alias="startsAt", alias="startsAt")
    ends_at: datetime | None = Field(default=None, serialization_alias="endsAt", alias="endsAt")
    metadata_json: dict[str, Any] = Field(default_factory=dict, serialization_alias="metadataJson", alias="metadataJson")
    created_at: datetime | None = Field(default=None, serialization_alias="createdAt")
    updated_at: datetime | None = Field(default=None, serialization_alias="updatedAt")


class AdminHomepageSectionCreate(BaseModel):
    """Admin payload to create a homepage section."""

    model_config = ConfigDict(populate_by_name=True)

    section_type: str = Field(..., alias="sectionType")
    title: str
    eyebrow: str | None = None
    description: str | None = None
    image_url: str | None = Field(default=None, alias="imageUrl")
    image_alt: str | None = Field(default=None, alias="imageAlt")
    image_position: str | None = Field(default="left", alias="imagePosition")
    cta_text: str | None = Field(default=None, alias="ctaText")
    cta_url: str | None = Field(default=None, alias="ctaUrl")
    collection_slug: str | None = Field(default=None, alias="collectionSlug")
    item_limit: int | None = Field(default=4, alias="itemLimit")
    display_order: int = Field(default=0, alias="displayOrder")
    is_enabled: bool = Field(default=True, alias="isEnabled")
    starts_at: datetime | None = Field(default=None, alias="startsAt")
    ends_at: datetime | None = Field(default=None, alias="endsAt")
    metadata_json: dict[str, Any] = Field(default_factory=dict, alias="metadataJson")


class AdminHomepageSectionUpdate(BaseModel):
    """Admin payload to update an existing homepage section."""

    model_config = ConfigDict(populate_by_name=True)

    section_type: str | None = Field(default=None, alias="sectionType")
    title: str | None = None
    eyebrow: str | None = None
    description: str | None = None
    image_url: str | None = Field(default=None, alias="imageUrl")
    image_alt: str | None = Field(default=None, alias="imageAlt")
    image_position: str | None = Field(default=None, alias="imagePosition")
    cta_text: str | None = Field(default=None, alias="ctaText")
    cta_url: str | None = Field(default=None, alias="ctaUrl")
    collection_slug: str | None = Field(default=None, alias="collectionSlug")
    item_limit: int | None = Field(default=None, alias="itemLimit")
    display_order: int | None = Field(default=None, alias="displayOrder")
    is_enabled: bool | None = Field(default=None, alias="isEnabled")
    starts_at: datetime | None = Field(default=None, alias="startsAt")
    ends_at: datetime | None = Field(default=None, alias="endsAt")
    metadata_json: dict[str, Any] | None = Field(default=None, alias="metadataJson")

