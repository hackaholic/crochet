"""Pydantic schemas for Google Merchant Center / Free Listings product feeds."""

from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class MerchantFeedItemOut(BaseModel):
    """Single sellable product or variant item formatted for Google Merchant Center."""

    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(description="Stable unique product or variant identifier (e.g. SKU)")
    title: str = Field(description="Item title, max 150 chars")
    description: str = Field(description="Plain text item description, max 5000 chars")
    link: str = Field(description="Direct URL to product landing page on storefront")
    image_link: str = Field(
        description="Public URL of primary product image",
        serialization_alias="imageLink",
        alias="imageLink",
    )
    additional_image_links: list[str] = Field(
        default_factory=list,
        description="Up to 10 additional product image URLs",
        serialization_alias="additionalImageLinks",
        alias="additionalImageLinks",
    )
    availability: Literal["in_stock", "out_of_stock", "preorder", "backorder"] = Field(
        default="in_stock",
        description="Current inventory availability",
    )
    price: str = Field(description="Price with ISO 4217 currency code (e.g. '2599.00 INR')")
    sale_price: str | None = Field(
        default=None,
        description="Sale price with currency if active discount exists",
        serialization_alias="salePrice",
        alias="salePrice",
    )
    brand: str = Field(default="Sulocraft", description="Brand name")
    condition: Literal["new", "refurbished", "used"] = Field(
        default="new",
        description="Item condition; handcrafted goods are new",
    )
    item_group_id: str | None = Field(
        default=None,
        description="Parent product slug or ID to group variants",
        serialization_alias="itemGroupId",
        alias="itemGroupId",
    )
    identifier_exists: Literal["yes", "no"] = Field(
        default="no",
        description="Must be 'no' for custom/handcrafted goods without GTIN or MPN",
        serialization_alias="identifierExists",
        alias="identifierExists",
    )
    product_type: str | None = Field(
        default=None,
        description="Product categorization / category breadcrumb string",
        serialization_alias="productType",
        alias="productType",
    )
    google_product_category: str | None = Field(
        default=None,
        description="Standard Google product category string or numeric ID if mapped",
        serialization_alias="googleProductCategory",
        alias="googleProductCategory",
    )
    shipping_weight: str | None = Field(
        default=None,
        description="Weight string with unit (e.g. '350 g')",
        serialization_alias="shippingWeight",
        alias="shippingWeight",
    )
    custom_label_0: str | None = Field(
        default=None,
        description="Merchandising badge (e.g. 'Bestseller', 'Handmade')",
        serialization_alias="customLabel0",
        alias="customLabel0",
    )
    custom_label_1: str | None = Field(
        default=None,
        description="Primary collection or occasion name",
        serialization_alias="customLabel1",
        alias="customLabel1",
    )


class MerchantFeedResponse(BaseModel):
    """API envelope response for inspectable JSON merchant feed."""

    model_config = ConfigDict(populate_by_name=True)

    feed_version: str = Field(
        default="1.0",
        description="Feed schema version",
        serialization_alias="feedVersion",
        alias="feedVersion",
    )
    title: str = Field(default="Sulocraft Product Feed", description="Channel title")
    link: str = Field(description="Storefront base URL")
    description: str = Field(
        default="Sulocraft Handcrafted Crochet Creations Product Feed",
        description="Channel description",
    )
    generated_at: str = Field(
        description="ISO 8601 generation timestamp",
        serialization_alias="generatedAt",
        alias="generatedAt",
    )
    total_items: int = Field(
        description="Total count of variant items in feed",
        serialization_alias="totalItems",
        alias="totalItems",
    )
    eligible_products_count: int = Field(
        description="Total count of unique active products in feed",
        serialization_alias="eligibleProductsCount",
        alias="eligibleProductsCount",
    )
    items: list[MerchantFeedItemOut] = Field(default_factory=list, description="Feed items")
    policy_disclaimer: str = Field(
        default=(
            "Sulocraft creations are artisanal handcrafted goods without manufacturer GTIN/MPN; "
            "identifier_exists is set to 'no' in compliance with Google specifications. Storewide "
            "shipping and return policies are configured at the Merchant Center account level."
        ),
        description="Policy declaration for missing identifiers and account-level settings",
        serialization_alias="policyDisclaimer",
        alias="policyDisclaimer",
    )
