"""Pydantic schemas conforming to the E-commerce Multi-Agent Specification."""

from typing import Any
from pydantic import BaseModel, ConfigDict, Field, model_validator


class CategoryBase(BaseModel):
    """Base category fields."""

    id: int
    name: str
    slug: str
    parent_id: int | None = None
    description: str | None = None
    image: str | None = None
    icon: str | None = None
    display_order: int = 0
    is_active: bool = True


class CategoryOut(CategoryBase):
    """Category output schema with nested children hierarchy."""

    model_config = ConfigDict(from_attributes=True)
    children: list["CategoryOut"] = []


class OccasionOut(BaseModel):
    """Curated occasions for gift navigation."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    icon: str | None = None
    image_url: str | None = None


class ReviewOut(BaseModel):
    """Customer product reviews."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    product_id: int | None = Field(default=None, alias="productId")
    product_name: str | None = Field(default=None, alias="productName")
    author_name: str = Field(default="Verified Customer", alias="authorName")
    name: str | None = None
    location: str | None = None
    rating: int = 5
    text: str
    image: str | None = None
    avatar_url: str | None = Field(default=None, alias="avatarUrl")
    date: str | None = None

    @model_validator(mode="before")
    @classmethod
    def sync_aliases(cls, data: Any) -> Any:
        if hasattr(data, "__dict__"):
            author = getattr(data, "author_name", None) or "Verified Customer"
            avatar = getattr(data, "avatar_url", None)
            return {
                "id": getattr(data, "id"),
                "productId": getattr(data, "product_id", None),
                "productName": getattr(data, "product_name", None),
                "authorName": author,
                "name": author,
                "location": getattr(data, "location", None),
                "rating": getattr(data, "rating", 5),
                "text": getattr(data, "text", ""),
                "image": avatar,
                "avatarUrl": avatar,
                "date": getattr(data, "date", None),
            }
        elif isinstance(data, dict):
            author = data.get("author_name") or data.get("authorName") or data.get("name") or "Verified Customer"
            avatar = data.get("avatar_url") or data.get("avatarUrl") or data.get("image")
            data["authorName"] = author
            data["name"] = author
            data["image"] = avatar
            data["avatarUrl"] = avatar
            return data
        return data


class VariantOut(BaseModel):
    """Sellable product variant carrying unique SKU, price, stock, and attributes."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    product_id: int
    sku: str
    name: str = "Default"
    price: int
    price_paise: int | None = Field(default=None, serialization_alias="pricePaise")
    currency: str = "INR"
    compare_at_price: int | None = Field(default=None, serialization_alias="compareAtPrice")
    stock_quantity: int = Field(default=10, serialization_alias="stockQuantity")
    weight: float | None = None
    status: str = "ACTIVE"
    attributes: dict[str, Any] = Field(default_factory=dict, alias="attributes_json")


class ProductImageOut(BaseModel):
    """Product gallery image."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    url: str
    alt_text: str | None = None
    sort_order: int = 0
    is_primary: bool = False
    variant_id: int | None = None


class ProductListItem(BaseModel):
    """Product card summary conforming to Section 2 of Specification & frontend UI."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    name: str
    slug: str
    price: int
    price_paise: int | None = Field(default=None, serialization_alias="pricePaise")
    currency: str = "INR"
    compare_at_price: int | None = Field(default=None, serialization_alias="compareAtPrice")
    original_price: int | None = Field(default=None, serialization_alias="originalPrice")  # Backward compat
    rating: float = 5.0
    reviews: int = Field(default=0, serialization_alias="reviews")
    review_count: int = Field(default=0, serialization_alias="reviewCount")
    image: str
    image_urls: list[str] = Field(default_factory=list, serialization_alias="imageUrls")
    category: str
    categories: list[str] = []
    badge: str | None = None
    tags: list[str] = []
    description: str | None = None
    customizable: bool = False
    in_stock: bool = Field(default=True, serialization_alias="inStock")
    inventory_status: str = Field(default="IN_STOCK", serialization_alias="inventoryStatus")


class ProductDetail(BaseModel):
    """Full product detail conforming to Section 2 of Specification."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    name: str
    slug: str
    short_description: str | None = None
    description: str | None = None
    category: str
    categories: list[str] = []
    tags: list[str] = []
    images: list[str] = []
    image_urls: list[str] = Field(default_factory=list, serialization_alias="imageUrls")
    gallery: list[ProductImageOut] = []
    variants: list[VariantOut] = []
    price: int
    price_paise: int | None = Field(default=None, serialization_alias="pricePaise")
    currency: str = "INR"
    compare_at_price: int | None = Field(default=None, serialization_alias="compareAtPrice")
    original_price: int | None = Field(default=None, serialization_alias="originalPrice")
    rating: float = 5.0
    reviews: int = Field(default=0, serialization_alias="reviews")
    review_count: int = Field(default=0, serialization_alias="reviewCount")
    in_stock: bool = Field(default=True, serialization_alias="inStock")
    inventory_status: str = Field(default="IN_STOCK", serialization_alias="inventoryStatus")
    badge: str | None = None
    brand: str = "Sulocraft"
    customizable: bool = False
    attributes: dict[str, Any] = Field(default_factory=dict, alias="metadata_json")
    customer_reviews: list[ReviewOut] = Field(default_factory=list, serialization_alias="customerReviews")


class ProductListResponse(BaseModel):
    """Paginated product list response."""

    items: list[ProductListItem]
    total: int
    limit: int
    offset: int
