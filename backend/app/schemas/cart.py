"""Pydantic schemas for Cart and Cart Items conforming to Sections 6, 7, and 18 of Specification."""

from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class CartItemAdd(BaseModel):
    """Payload to add an item to the shopping cart."""

    model_config = ConfigDict(populate_by_name=True)

    product_variant_id: int | None = Field(
        default=None,
        alias="productVariantId",
        description="ID of specific variant to add. If omitted, product_id or sku must be provided.",
    )
    product_id: int | None = Field(
        default=None,
        alias="productId",
        description="ID of product (will auto-resolve to primary variant if product_variant_id is omitted).",
    )
    sku: str | None = Field(
        default=None,
        description="SKU of variant (alternative to product_variant_id).",
    )
    quantity: int = Field(default=1, ge=1, le=99, description="Quantity to add.")
    personalization: dict[str, Any] = Field(
        default_factory=dict,
        description="Custom personalization options (e.g. gift_message, color_choice).",
    )


class CartItemUpdate(BaseModel):
    """Payload to update quantity or personalization of a cart line item."""

    quantity: int = Field(..., ge=1, le=99, description="New quantity for this item.")
    personalization: dict[str, Any] | None = Field(
        default=None,
        description="Updated personalization attributes.",
    )


class CartItemOut(BaseModel):
    """Representation of an individual cart line item."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    product_id: int = Field(..., serialization_alias="productId")
    product_name: str = Field(..., serialization_alias="productName")
    product_slug: str = Field(..., serialization_alias="productSlug")
    product_image: str = Field(..., serialization_alias="productImage")
    variant_id: int = Field(..., serialization_alias="variantId")
    variant_sku: str = Field(..., serialization_alias="variantSku")
    variant_name: str = Field(..., serialization_alias="variantName")
    unit_price: int = Field(..., serialization_alias="unitPrice")
    unit_price_paise: int | None = Field(default=None, serialization_alias="unitPricePaise")
    currency: str = "INR"
    compare_at_price: int | None = Field(default=None, serialization_alias="compareAtPrice")
    quantity: int
    line_total: int = Field(..., serialization_alias="lineTotal")
    line_total_paise: int | None = Field(default=None, serialization_alias="lineTotalPaise")
    personalization: dict[str, Any] = Field(default_factory=dict)
    stock_available: int = Field(..., serialization_alias="stockAvailable")


class CartOut(BaseModel):
    """Complete shopping cart representation."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int | None = None
    guest_token: str | None = Field(default=None, serialization_alias="guestToken")
    items: list[CartItemOut] = []
    item_count: int = Field(default=0, serialization_alias="itemCount")
    subtotal: int = 0
    subtotal_paise: int | None = Field(default=None, serialization_alias="subtotalPaise")
    currency: str = "INR"
    status: str = "ACTIVE"


class CartMergeRequest(BaseModel):
    """Request to merge an anonymous guest cart into the active cart."""

    guest_token: str = Field(..., description="Guest cart token to merge from.")
