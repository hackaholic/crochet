"""Admin schemas conforming to Sections 18, 20, 34, and Milestone 9 of Specification."""

from datetime import datetime
from typing import Any
from app.core.images import build_image_url
from pydantic import BaseModel, ConfigDict, Field, model_validator


class AdminVariantCreate(BaseModel):
    """Payload to create a new product variant."""

    model_config = ConfigDict(populate_by_name=True)

    sku: str = Field(..., description="Unique Stock Keeping Unit identifier")
    name: str = Field(default="Default", description="Variant name, e.g. 'Red / Medium'")
    price: int = Field(..., ge=0, description="Retail price in INR rupees")
    compare_at_price: int | None = Field(default=None, ge=0, alias="compareAtPrice")
    cost: int | None = Field(default=None, ge=0, description="Cost of goods in INR rupees")
    stock_quantity: int = Field(default=10, ge=0, alias="stockQuantity")
    weight: float | None = Field(default=None, ge=0, description="Weight in grams")
    attributes_json: dict[str, Any] = Field(default_factory=dict, alias="attributes")


class AdminVariantUpdate(BaseModel):
    """Payload to partially update a variant."""

    model_config = ConfigDict(populate_by_name=True)

    sku: str | None = None
    name: str | None = None
    price: int | None = Field(default=None, ge=0)
    compare_at_price: int | None = Field(default=None, ge=0, alias="compareAtPrice")
    cost: int | None = Field(default=None, ge=0)
    stock_quantity: int | None = Field(default=None, ge=0, alias="stockQuantity")
    weight: float | None = Field(default=None, ge=0)
    status: str | None = None
    attributes_json: dict[str, Any] | None = Field(default=None, alias="attributes")


class AdminVariantOut(BaseModel):
    """Detailed variant representation."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    product_id: int = Field(alias="productId")
    sku: str
    name: str
    price: int
    price_paise: int = Field(alias="pricePaise")
    compare_at_price: int | None = Field(default=None, alias="compareAtPrice")
    compare_at_price_paise: int | None = Field(default=None, alias="compareAtPricePaise")
    cost: int | None = None
    stock_quantity: int = Field(alias="stockQuantity")
    weight: float | None = None
    status: str
    attributes_json: dict[str, Any] = Field(default_factory=dict, alias="attributes")
    created_at: datetime | None = Field(default=None, alias="createdAt")
    updated_at: datetime | None = Field(default=None, alias="updatedAt")


class AdminInventoryAdjustRequest(BaseModel):
    """Payload to adjust or set inventory stock."""

    model_config = ConfigDict(populate_by_name=True)

    stock_quantity: int | None = Field(default=None, ge=0, alias="stockQuantity", description="Set absolute stock quantity")
    adjustment: int | None = Field(default=None, description="Relative adjustment (+5, -3)")
    reason: str | None = Field(default=None, description="Optional audit reason")


class AdminProductCreate(BaseModel):
    """Payload to create a new product."""

    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(..., min_length=2, max_length=200)
    slug: str | None = Field(default=None, description="Auto-slugified from name if omitted")
    short_description: str | None = Field(default=None, alias="shortDescription")
    description: str | None = None
    brand: str = "Sulocraft"
    primary_image: str = Field(..., alias="primaryImage")
    badge: str | None = None
    customizable: bool = False
    primary_category_id: int | None = Field(default=None, alias="primaryCategoryId")
    category_ids: list[int] = Field(default_factory=list, alias="categoryIds")
    collection_ids: list[int] = Field(default_factory=list, alias="collectionIds")
    tag_ids: list[int] = Field(default_factory=list, alias="tagIds")
    gallery_images: list[str] = Field(default_factory=list, alias="galleryImages")
    variants: list[AdminVariantCreate] = Field(default_factory=list)
    metadata_json: dict[str, Any] = Field(default_factory=dict, alias="metadata")


class AdminProductUpdate(BaseModel):
    """Payload to update an existing product."""

    model_config = ConfigDict(populate_by_name=True)

    name: str | None = None
    slug: str | None = None
    short_description: str | None = Field(default=None, alias="shortDescription")
    description: str | None = None
    status: str | None = None  # ACTIVE, DRAFT, ARCHIVED
    brand: str | None = None
    primary_image: str | None = Field(default=None, alias="primaryImage")
    badge: str | None = None
    customizable: bool | None = None
    primary_category_id: int | None = Field(default=None, alias="primaryCategoryId")
    category_ids: list[int] | None = Field(default=None, alias="categoryIds")
    collection_ids: list[int] | None = Field(default=None, alias="collectionIds")
    tag_ids: list[int] | None = Field(default=None, alias="tagIds")
    gallery_images: list[str] | None = Field(default=None, alias="galleryImages")
    metadata_json: dict[str, Any] | None = Field(default=None, alias="metadata")


class AdminProductOut(BaseModel):
    """Comprehensive product representation for administration."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    name: str
    slug: str
    short_description: str | None = Field(default=None, alias="shortDescription")
    description: str | None = None
    status: str
    brand: str
    primary_image: str = Field(alias="primaryImage")
    badge: str | None = None
    customizable: bool
    rating: float
    reviews_count: int = Field(alias="reviewsCount")
    primary_category_id: int | None = Field(default=None, alias="primaryCategoryId")
    category_ids: list[int] = Field(default_factory=list, alias="categoryIds")
    category_names: list[str] = Field(default_factory=list, alias="categoryNames")
    collection_ids: list[int] = Field(default_factory=list, alias="collectionIds")
    collection_names: list[str] = Field(default_factory=list, alias="collectionNames")
    tag_ids: list[int] = Field(default_factory=list, alias="tagIds")
    tag_names: list[str] = Field(default_factory=list, alias="tagNames")
    gallery_images: list[str] = Field(default_factory=list, alias="galleryImages")
    variants: list[AdminVariantOut] = Field(default_factory=list)
    total_stock: int = Field(default=0, alias="totalStock")
    min_price: int = Field(default=0, alias="minPrice")
    min_price_paise: int = Field(default=0, alias="minPricePaise")
    created_at: datetime | None = Field(default=None, alias="createdAt")
    updated_at: datetime | None = Field(default=None, alias="updatedAt")


class AdminProductListOut(BaseModel):
    """Paginated list of products."""

    model_config = ConfigDict(populate_by_name=True)

    items: list[AdminProductOut]
    total: int
    page: int
    page_size: int = Field(alias="pageSize")


class AdminCategoryCreate(BaseModel):
    """Payload to create a new category."""

    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(..., min_length=2, max_length=100)
    slug: str | None = None
    parent_id: int | None = Field(default=None, alias="parentId")
    description: str | None = None
    image_key: str | None = Field(default=None, alias="imageKey")
    image: str | None = None
    icon: str | None = None
    display_order: int = Field(default=0, alias="displayOrder")
    is_active: bool = Field(default=True, alias="isActive")
    show_when_empty: bool = Field(default=False, alias="showWhenEmpty")
    seo_title: str | None = Field(default=None, alias="seoTitle")
    seo_description: str | None = Field(default=None, alias="seoDescription")


class AdminCategoryUpdate(BaseModel):
    """Payload to update an existing category."""

    model_config = ConfigDict(populate_by_name=True)

    name: str | None = None
    slug: str | None = None
    parent_id: int | None = Field(default=None, alias="parentId")
    description: str | None = None
    image_key: str | None = Field(default=None, alias="imageKey")
    image: str | None = None
    icon: str | None = None
    display_order: int | None = Field(default=None, alias="displayOrder")
    is_active: bool | None = Field(default=None, alias="isActive")
    show_when_empty: bool | None = Field(default=None, alias="showWhenEmpty")
    seo_title: str | None = Field(default=None, alias="seoTitle")
    seo_description: str | None = Field(default=None, alias="seoDescription")


class AdminCategoryOut(BaseModel):
    """Category representation for administration."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    name: str
    slug: str
    parent_id: int | None = Field(default=None, alias="parentId")
    description: str | None = None
    image_key: str | None = Field(default=None, alias="imageKey")
    image: str | None = None
    image_url: str | None = Field(default=None, alias="imageUrl")
    icon: str | None = None
    display_order: int = Field(default=0, alias="displayOrder")
    is_active: bool = Field(default=True, alias="isActive")
    show_when_empty: bool = Field(default=False, alias="showWhenEmpty")
    seo_title: str | None = Field(default=None, alias="seoTitle")
    seo_description: str | None = Field(default=None, alias="seoDescription")
    products_count: int = Field(default=0, alias="productsCount")
    created_at: datetime | None = Field(default=None, alias="createdAt")
    updated_at: datetime | None = Field(default=None, alias="updatedAt")

    @model_validator(mode="before")
    @classmethod
    def resolve_images(cls, data: Any) -> Any:
        if hasattr(data, "__dict__"):
            raw_img = getattr(data, "image_key", None) or getattr(data, "image", None)
            url = build_image_url(raw_img) if raw_img else None
            return {
                "id": getattr(data, "id"),
                "name": getattr(data, "name"),
                "slug": getattr(data, "slug"),
                "parentId": getattr(data, "parent_id", None),
                "description": getattr(data, "description", None),
                "imageKey": getattr(data, "image_key", None),
                "image": url,
                "imageUrl": url,
                "icon": getattr(data, "icon", None),
                "displayOrder": getattr(data, "display_order", 0),
                "isActive": getattr(data, "is_active", True),
                "showWhenEmpty": getattr(data, "show_when_empty", False),
                "seoTitle": getattr(data, "seo_title", None),
                "seoDescription": getattr(data, "seo_description", None),
                "productsCount": getattr(data, "products_count", 0),
                "createdAt": getattr(data, "created_at", None),
                "updatedAt": getattr(data, "updated_at", None),
            }
        elif isinstance(data, dict):
            raw_img = data.get("image_key") or data.get("image") or data.get("imageUrl")
            url = build_image_url(raw_img) if raw_img else None
            data["image"] = url
            data["imageUrl"] = url
            return data
        return data


class AdminCollectionCreate(BaseModel):
    """Payload to create a new collection."""

    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(..., min_length=2, max_length=150)
    slug: str | None = None
    description: str | None = None
    image_key: str | None = Field(default=None, alias="imageKey")
    collection_type: str = Field(default="MERCHANDISING", alias="collectionType")
    display_order: int = Field(default=0, alias="displayOrder")
    is_active: bool = Field(default=True, alias="isActive")
    starts_at: datetime | None = Field(default=None, alias="startsAt")
    ends_at: datetime | None = Field(default=None, alias="endsAt")
    seo_title: str | None = Field(default=None, alias="seoTitle")
    seo_description: str | None = Field(default=None, alias="seoDescription")


class AdminCollectionUpdate(BaseModel):
    """Payload to update an existing collection."""

    model_config = ConfigDict(populate_by_name=True)

    name: str | None = None
    slug: str | None = None
    description: str | None = None
    image_key: str | None = Field(default=None, alias="imageKey")
    collection_type: str | None = Field(default=None, alias="collectionType")
    display_order: int | None = Field(default=None, alias="displayOrder")
    is_active: bool | None = Field(default=None, alias="isActive")
    starts_at: datetime | None = Field(default=None, alias="startsAt")
    ends_at: datetime | None = Field(default=None, alias="endsAt")
    seo_title: str | None = Field(default=None, alias="seoTitle")
    seo_description: str | None = Field(default=None, alias="seoDescription")


class AdminCollectionOut(BaseModel):
    """Collection representation for administration."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    name: str
    slug: str
    description: str | None = None
    image_key: str | None = Field(default=None, alias="imageKey")
    image_url: str | None = Field(default=None, alias="imageUrl")
    collection_type: str = Field(default="MERCHANDISING", alias="collectionType")
    display_order: int = Field(default=0, alias="displayOrder")
    is_active: bool = Field(default=True, alias="isActive")
    starts_at: datetime | None = Field(default=None, alias="startsAt")
    ends_at: datetime | None = Field(default=None, alias="endsAt")
    seo_title: str | None = Field(default=None, alias="seoTitle")
    seo_description: str | None = Field(default=None, alias="seoDescription")
    products_count: int = Field(default=0, alias="productsCount")
    created_at: datetime | None = Field(default=None, alias="createdAt")
    updated_at: datetime | None = Field(default=None, alias="updatedAt")

    @model_validator(mode="before")
    @classmethod
    def resolve_images(cls, data: Any) -> Any:
        if hasattr(data, "__dict__"):
            raw_img = getattr(data, "image_key", None)
            url = build_image_url(raw_img) if raw_img else None
            return {
                "id": getattr(data, "id"),
                "name": getattr(data, "name"),
                "slug": getattr(data, "slug"),
                "description": getattr(data, "description", None),
                "imageKey": getattr(data, "image_key", None),
                "imageUrl": url,
                "collectionType": getattr(data, "collection_type", "MERCHANDISING"),
                "displayOrder": getattr(data, "display_order", 0),
                "isActive": getattr(data, "is_active", True),
                "startsAt": getattr(data, "starts_at", None),
                "endsAt": getattr(data, "ends_at", None),
                "seoTitle": getattr(data, "seo_title", None),
                "seoDescription": getattr(data, "seo_description", None),
                "productsCount": getattr(data, "products_count", 0),
                "createdAt": getattr(data, "created_at", None),
                "updatedAt": getattr(data, "updated_at", None),
            }
        elif isinstance(data, dict):
            raw_img = data.get("image_key") or data.get("imageUrl")
            url = build_image_url(raw_img) if raw_img else None
            data["imageUrl"] = url
            return data
        return data


class AdminCollectionAssignProducts(BaseModel):
    """Payload to assign products to a collection."""

    model_config = ConfigDict(populate_by_name=True)

    product_ids: list[int] = Field(..., alias="productIds")


class AdminOrderStatusUpdate(BaseModel):
    """Payload to transition order lifecycle status."""

    model_config = ConfigDict(populate_by_name=True)

    status: str = Field(..., description="Target status: PROCESSING, READY_TO_SHIP, SHIPPED, OUT_FOR_DELIVERY, DELIVERED, CANCELLED, REFUNDED")
    tracking_number: str | None = Field(default=None, alias="trackingNumber")
    courier_name: str | None = Field(default=None, alias="courierName")
    note: str | None = Field(default=None, description="Audit note recorded in status history")


class AdminOrderItemOut(BaseModel):
    """Snapshotted order item for admin view."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    product_id: int | None = Field(default=None, alias="productId")
    product_variant_id: int | None = Field(default=None, alias="variantId")
    product_name: str = Field(alias="productName")
    product_slug: str | None = Field(default=None, alias="productSlug")
    sku: str
    variant_name: str = Field(alias="variantName")
    product_image: str | None = Field(default=None, alias="productImage")
    unit_price: int = Field(alias="unitPrice")
    unit_price_paise: int = Field(alias="unitPricePaise")
    quantity: int
    line_total: int = Field(alias="lineTotal")
    line_total_paise: int = Field(alias="lineTotalPaise")
    personalization_json: dict[str, Any] = Field(default_factory=dict, alias="personalization")


class AdminOrderDetailOut(BaseModel):
    """Full order view for admin operations."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    order_number: str = Field(alias="orderNumber")
    customer_name: str = Field(alias="customerName")
    customer_phone: str = Field(alias="customerPhone")
    customer_email: str | None = Field(default=None, alias="customerEmail")
    status: str
    payment_status: str = Field(alias="paymentStatus")
    payment_method: str = Field(alias="paymentMethod")
    currency: str = "INR"
    subtotal: int
    subtotal_paise: int = Field(alias="subtotalPaise")
    shipping_fee: int = Field(alias="shippingFee")
    shipping_fee_paise: int = Field(alias="shippingFeePaise")
    discount_amount: int = Field(alias="discountAmount")
    discount_amount_paise: int = Field(alias="discountAmountPaise")
    tax_amount: int = Field(default=0, alias="taxAmount")
    tax_amount_paise: int = Field(default=0, alias="taxAmountPaise")
    total_amount: int = Field(alias="totalAmount")
    total_amount_paise: int = Field(alias="totalAmountPaise")
    shipping_address: dict[str, Any] = Field(alias="shippingAddress")
    billing_address: dict[str, Any] | None = Field(default=None, alias="billingAddress")
    tracking_number: str | None = Field(default=None, alias="trackingNumber")
    courier_name: str | None = Field(default=None, alias="courierName")
    notes: str | None = None
    items: list[AdminOrderItemOut] = Field(default_factory=list)
    status_history: list[dict[str, Any]] = Field(default_factory=list, alias="statusHistory")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class AdminOrderListOut(BaseModel):
    """Paginated list of orders for administration."""

    model_config = ConfigDict(populate_by_name=True)

    items: list[AdminOrderDetailOut]
    total: int
    page: int
    page_size: int = Field(alias="pageSize")


class AdminLowStockItem(BaseModel):
    """Low stock inventory alert item."""

    model_config = ConfigDict(populate_by_name=True)

    variant_id: int = Field(alias="variantId")
    product_id: int = Field(alias="productId")
    product_name: str = Field(alias="productName")
    sku: str
    variant_name: str = Field(alias="variantName")
    stock_quantity: int = Field(alias="stockQuantity")


class AdminTopSellingProduct(BaseModel):
    """Product sales analytics item."""

    model_config = ConfigDict(populate_by_name=True)

    product_id: int = Field(alias="productId")
    product_name: str = Field(alias="productName")
    total_sold: int = Field(alias="totalSold")
    total_revenue: int = Field(alias="totalRevenue")
    total_revenue_paise: int = Field(alias="totalRevenuePaise")


class AdminAnalyticsOut(BaseModel):
    """Dashboard KPIs and store analytics."""

    model_config = ConfigDict(populate_by_name=True)

    total_revenue: int = Field(alias="totalRevenue")
    total_revenue_paise: int = Field(alias="totalRevenuePaise")
    total_orders: int = Field(alias="totalOrders")
    pending_orders: int = Field(alias="pendingOrders")
    delivered_orders: int = Field(alias="deliveredOrders")
    cancelled_orders: int = Field(alias="cancelledOrders")
    total_customers: int = Field(alias="totalCustomers")
    total_products: int = Field(alias="totalProducts")
    low_stock_count: int = Field(alias="lowStockCount")
    low_stock_items: list[AdminLowStockItem] = Field(default_factory=list, alias="lowStockItems")
    recent_orders: list[AdminOrderDetailOut] = Field(default_factory=list, alias="recentOrders")
    top_selling_products: list[AdminTopSellingProduct] = Field(default_factory=list, alias="topSellingProducts")
