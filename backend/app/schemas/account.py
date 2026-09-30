"""Pydantic schemas for Customer Profile, Account Overview, and Wishlist.

Conforms to Sections 19 & 27 of the Specification.
"""

from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class ProfileUpdate(BaseModel):
    """Payload to update customer profile fields."""

    name: str | None = Field(default=None, min_length=2, max_length=100)
    email: str | None = Field(default=None, max_length=255)


class ProfileOut(BaseModel):
    """Customer profile details."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    status: str
    identities: list[str] = []
    created_at: str = Field(..., serialization_alias="createdAt")
    last_login_at: str | None = Field(default=None, serialization_alias="lastLoginAt")


class AccountOverviewOut(BaseModel):
    """Aggregated metrics for customer account dashboard."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    profile: ProfileOut
    total_orders: int = Field(default=0, serialization_alias="totalOrders")
    active_orders: int = Field(default=0, serialization_alias="activeOrders")
    saved_addresses: int = Field(default=0, serialization_alias="savedAddresses")
    wishlist_items_count: int = Field(default=0, serialization_alias="wishlistItemsCount")


class WishlistItemAdd(BaseModel):
    """Request to add an item to the wishlist."""

    model_config = ConfigDict(populate_by_name=True)

    product_id: int | None = Field(default=None, alias="productId")
    product_slug: str | None = Field(default=None, alias="productSlug")


class WishlistItemOut(BaseModel):
    """Snapshotted product item inside a customer's wishlist."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    product_id: int = Field(..., serialization_alias="productId")
    product_name: str = Field(..., serialization_alias="productName")
    product_slug: str = Field(..., serialization_alias="productSlug")
    product_image: str = Field(..., serialization_alias="productImage")
    price: int
    price_paise: int = Field(..., serialization_alias="pricePaise")
    compare_at_price: int | None = Field(default=None, serialization_alias="compareAtPrice")
    original_price: int | None = Field(default=None, serialization_alias="originalPrice")
    badge: str | None = None
    category: str
    in_stock: bool = Field(default=True, serialization_alias="inStock")
    rating: float = 5.0
    reviews: int = 0
    created_at: str = Field(..., serialization_alias="createdAt")


class WishlistOut(BaseModel):
    """Customer wishlist response."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    items: list[WishlistItemOut] = []
    total_items: int = Field(default=0, serialization_alias="totalItems")
