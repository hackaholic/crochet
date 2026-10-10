"""Pydantic schemas for Customer Profile, Account Overview, and Wishlist.

Conforms to Sections 19 & 27 of the Specification.
"""

import re
from typing import Any
from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProfileUpdate(BaseModel):
    """Payload to update customer profile fields."""

    model_config = ConfigDict(extra="ignore")

    name: str | None = Field(default=None, max_length=100)
    email: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=20)

    @field_validator("name", mode="before")
    @classmethod
    def validate_name(cls, v: Any) -> str | None:
        if v is None:
            return None
        if not isinstance(v, str):
            raise ValueError("Name must be a string")
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Name cannot be empty or blank")
        if len(trimmed) < 2:
            raise ValueError("Name must be at least 2 characters")
        if len(trimmed) > 100:
            raise ValueError("Name cannot exceed 100 characters")
        return trimmed

    @field_validator("phone", mode="before")
    @classmethod
    def validate_phone(cls, v: Any) -> str | None:
        if v is None:
            return None
        if not isinstance(v, str):
            raise ValueError("Phone must be a string")
        trimmed = v.strip()
        if not trimmed:
            return None  # clearing phone
        # Normalize: allow optional leading '+' and digits, spaces, hyphens
        cleaned = re.sub(r"[\s\-]", "", trimmed)
        # Check standard format: e.g. 10-digit Indian mobile or +91 followed by 10 digits
        if not re.match(r"^(\+?[1-9]\d{7,14}|\d{10})$", cleaned):
            raise ValueError("Phone number must be a valid 10-digit or E.164 phone number")
        return cleaned


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
