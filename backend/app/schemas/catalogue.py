from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core.images import build_image_url


class CategorySummary(BaseModel):
    """Concise category representation for product classification."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int | None = None
    name: str
    slug: str

    @model_validator(mode="before")
    @classmethod
    def parse_category(cls, data: Any) -> Any:
        if isinstance(data, str):
            return {"name": data, "slug": data.lower().replace(" ", "-")}
        return data


class CollectionSummary(BaseModel):
    """Concise collection representation for product classification."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int | None = None
    name: str
    slug: str

    @model_validator(mode="before")
    @classmethod
    def parse_collection(cls, data: Any) -> Any:
        if isinstance(data, str):
            return {"name": data, "slug": data.lower().replace(" ", "-")}
        return data


class CategoryOut(BaseModel):
    """Category output schema with nested children hierarchy and product count."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    name: str
    slug: str
    parent_id: int | None = Field(default=None, serialization_alias="parentId", alias="parentId")
    description: str | None = None
    image: str | None = None
    image_url: str | None = Field(default=None, serialization_alias="imageUrl", alias="imageUrl")
    icon: str | None = None
    display_order: int = Field(default=0, serialization_alias="displayOrder", alias="displayOrder")
    is_active: bool = Field(default=True, serialization_alias="isActive", alias="isActive")
    show_when_empty: bool = Field(default=False, serialization_alias="showWhenEmpty", alias="showWhenEmpty")
    product_count: int = Field(default=0, serialization_alias="productCount", alias="productCount")
    children: list["CategoryOut"] = []

    @model_validator(mode="before")
    @classmethod
    def resolve_category_fields(cls, data: Any) -> Any:
        if hasattr(data, "__dict__"):
            raw_img = getattr(data, "image_key", None) or getattr(data, "image", None)
            url = build_image_url(raw_img) if raw_img else None
            return {
                "id": getattr(data, "id"),
                "name": getattr(data, "name"),
                "slug": getattr(data, "slug"),
                "parentId": getattr(data, "parent_id", None),
                "description": getattr(data, "description", None),
                "image": url,
                "imageUrl": url,
                "icon": getattr(data, "icon", None),
                "displayOrder": getattr(data, "display_order", 0),
                "isActive": getattr(data, "is_active", True),
                "showWhenEmpty": getattr(data, "show_when_empty", False),
                "productCount": getattr(data, "product_count", 0),
                "children": getattr(data, "children", []),
            }
        elif isinstance(data, dict):
            raw_img = data.get("image_key") or data.get("image") or data.get("imageUrl")
            url = build_image_url(raw_img) if raw_img else None
            data["image"] = url
            data["imageUrl"] = url
            if "product_count" not in data and "productCount" in data:
                data["product_count"] = data["productCount"]
            return data
        return data


class CollectionOut(BaseModel):
    """Collection public output schema conforming to launch taxonomy contract."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    name: str
    slug: str
    description: str | None = None
    image_url: str | None = Field(default=None, serialization_alias="imageUrl", alias="imageUrl")
    collection_type: str = Field(default="MERCHANDISING", serialization_alias="collectionType", alias="collectionType")
    display_order: int = Field(default=0, serialization_alias="displayOrder", alias="displayOrder")
    is_active: bool = Field(default=True, serialization_alias="isActive", alias="isActive")
    starts_at: datetime | None = Field(default=None, serialization_alias="startsAt", alias="startsAt")
    ends_at: datetime | None = Field(default=None, serialization_alias="endsAt", alias="endsAt")
    product_count: int = Field(default=0, serialization_alias="productCount", alias="productCount")

    @model_validator(mode="before")
    @classmethod
    def resolve_collection_fields(cls, data: Any) -> Any:
        if hasattr(data, "__dict__"):
            raw_img = getattr(data, "image_key", None)
            url = build_image_url(raw_img) if raw_img else None
            return {
                "id": getattr(data, "id"),
                "name": getattr(data, "name"),
                "slug": getattr(data, "slug"),
                "description": getattr(data, "description", None),
                "imageUrl": url,
                "collectionType": getattr(data, "collection_type", "MERCHANDISING"),
                "displayOrder": getattr(data, "display_order", 0),
                "isActive": getattr(data, "is_active", True),
                "startsAt": getattr(data, "starts_at", None),
                "endsAt": getattr(data, "ends_at", None),
                "productCount": getattr(data, "product_count", 0),
            }
        elif isinstance(data, dict):
            raw_img = data.get("image_key") or data.get("imageUrl")
            url = build_image_url(raw_img) if raw_img else None
            data["imageUrl"] = url
            if "product_count" not in data and "productCount" in data:
                data["product_count"] = data["productCount"]
            return data
        return data


class OccasionOut(BaseModel):
    """Curated occasions for gift navigation."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    name: str
    icon: str | None = None
    image_url: str | None = Field(default=None, serialization_alias="imageUrl", alias="imageUrl")
    imageUrl: str | None = None
    description: str | None = None
    display_order: int = Field(default=0, serialization_alias="displayOrder", alias="displayOrder")
    displayOrder: int = 0

    @model_validator(mode="before")
    @classmethod
    def resolve_fields(cls, data: Any) -> Any:
        if hasattr(data, "__dict__"):
            raw_img = getattr(data, "image_key", None) or getattr(data, "_legacy_image_url", None)
            url = build_image_url(raw_img) if raw_img else None
            order = getattr(data, "display_order", 0)
            return {
                "id": getattr(data, "id"),
                "name": getattr(data, "name"),
                "icon": getattr(data, "icon", None),
                "image_url": url,
                "imageUrl": url,
                "description": getattr(data, "description", None),
                "display_order": order,
                "displayOrder": order,
            }
        elif isinstance(data, dict):
            raw_img = data.get("image_key") or data.get("image_url") or data.get("imageUrl")
            url = build_image_url(raw_img) if raw_img else None
            data["image_url"] = url
            data["imageUrl"] = url
            order = data.get("display_order", data.get("displayOrder", 0))
            data["display_order"] = order
            data["displayOrder"] = order
            return data
        return data



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

    @field_validator("url", mode="after")
    @classmethod
    def resolve_url(cls, v: str) -> str:
        return build_image_url(v)


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
    category: str = ""
    primary_category: CategorySummary | None = Field(default=None, serialization_alias="primaryCategory")
    categories: list[CategorySummary] = []
    collections: list[CollectionSummary] = []
    badge: str | None = None
    tags: list[str] = []
    occasions: list[str] = Field(default_factory=list, serialization_alias="occasions")
    description: str | None = None
    customizable: bool = False
    in_stock: bool = Field(default=True, serialization_alias="inStock")
    inventory_status: str = Field(default="IN_STOCK", serialization_alias="inventoryStatus")

    @field_validator("image", mode="after")
    @classmethod
    def resolve_image(cls, v: str) -> str:
        return build_image_url(v)

    @field_validator("image_urls", mode="after")
    @classmethod
    def resolve_image_urls(cls, v: list[str]) -> list[str]:
        return [build_image_url(x) for x in v]


class ProductDetail(BaseModel):
    """Full product detail conforming to Section 2 of Specification."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    name: str
    slug: str
    short_description: str | None = None
    description: str | None = None
    category: str = ""
    primary_category: CategorySummary | None = Field(default=None, serialization_alias="primaryCategory")
    categories: list[CategorySummary] = []
    collections: list[CollectionSummary] = []
    tags: list[str] = []
    occasions: list[str] = Field(default_factory=list, serialization_alias="occasions")
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

    @field_validator("images", mode="after")
    @classmethod
    def resolve_images(cls, v: list[str]) -> list[str]:
        return [build_image_url(x) for x in v]

    @field_validator("image_urls", mode="after")
    @classmethod
    def resolve_image_urls(cls, v: list[str]) -> list[str]:
        return [build_image_url(x) for x in v]


class ProductListResponse(BaseModel):
    """Paginated product list response."""

    items: list[ProductListItem]
    total: int
    limit: int
    offset: int


class SearchSuggestionKeyword(BaseModel):
    """Keyword item in trending search suggestions."""

    term: str


class SearchSuggestionsResponse(BaseModel):
    """Response schema for search discovery suggestions."""

    trending_keywords: list[SearchSuggestionKeyword] = Field(default_factory=list)
    trending_products: list[ProductListItem] = Field(default_factory=list)


class SearchEventCreate(BaseModel):
    """Telemetry payload for recording a debounced search query."""

    query: str = Field(..., max_length=120, description="Debounced search query string (max 120 characters)")


class SearchEventResponse(BaseModel):
    """Acknowledgment response for recorded search telemetry."""

    status: str = "recorded"


# Schema aliases for compatibility
SearchSuggestionsOut = SearchSuggestionsResponse
SearchEventOut = SearchEventResponse
