"""Pydantic schemas for Storefront and Brand content conforming to docs/api-storefront.md."""

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class BrandSettingsOut(BaseModel):
    """Public brand profile representation."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    name: str = "Sulocraft"
    owner_name: str = Field(default="Anupama", serialization_alias="ownerName", alias="ownerName")
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


class StorefrontResponse(BaseModel):
    """Public storefront aggregate response for the homepage."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    brand: BrandSettingsOut
    hero_campaigns: list[HomepageCampaignOut] = Field(default_factory=list, serialization_alias="heroCampaigns")


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
