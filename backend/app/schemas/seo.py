"""Pydantic schemas for SEO Metadata Resolver conforming to docs/api-seo.md."""

from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


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
    faqs: list[SeoFaqItem] = Field(default_factory=list)
    shipping_info: SeoShippingInfo | None = Field(default=None, serialization_alias="shippingInfo", alias="shippingInfo")
    return_policy: SeoReturnPolicy | None = Field(default=None, serialization_alias="returnPolicy", alias="returnPolicy")
