"""Admin schemas conforming to Sections 18, 20, 34, and Milestone 9 of Specification."""

from datetime import datetime
from typing import Any
from app.core.images import build_image_url
from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator, model_validator


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


    @computed_field(alias="primaryImageUrl")
    @property
    def primary_image_url(self) -> str:
        return build_image_url(self.primary_image)

    @computed_field(alias="galleryImageUrls")
    @property
    def gallery_image_urls(self) -> list[str]:
        return [build_image_url(key) for key in self.gallery_images]


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


class AdminSendWelcomeRequest(BaseModel):
    """Payload to dispatch a welcome email with optional custom note."""

    model_config = ConfigDict(populate_by_name=True)

    email: str = Field(..., description="Customer recipient email address")
    name: str | None = Field(default=None, description="Customer name for personalized greeting")
    custom_message: str | None = Field(
        default=None,
        alias="customMessage",
        description="Custom greeting or note from the founder/team",
    )


# -----------------------------------------------------------------------------
# Figma Admin Dashboard Expansion Schemas
# -----------------------------------------------------------------------------


class AdminDashboardComparison(BaseModel):
    """Period-over-period comparison metrics."""

    model_config = ConfigDict(populate_by_name=True)

    previous_total_sales: int = Field(alias="previousTotalSales")
    previous_total_sales_paise: int = Field(alias="previousTotalSalesPaise")
    previous_order_count: int = Field(alias="previousOrderCount")
    sales_growth_percent: float | None = Field(default=None, alias="salesGrowthPercent")
    order_growth_percent: float | None = Field(default=None, alias="orderGrowthPercent")


class AdminDashboardSummaryOut(BaseModel):
    """Comprehensive dashboard summary metrics for admin."""

    model_config = ConfigDict(populate_by_name=True)

    effective_range: dict[str, str] = Field(alias="effectiveRange")
    total_sales: int = Field(alias="totalSales")
    total_sales_paise: int = Field(alias="totalSalesPaise")
    net_revenue: int = Field(alias="netRevenue")
    net_revenue_paise: int = Field(alias="netRevenuePaise")
    order_count: int = Field(alias="orderCount")
    average_order_value: float = Field(alias="averageOrderValue")
    average_order_value_paise: int = Field(alias="averageOrderValuePaise")
    comparison: AdminDashboardComparison | None = None
    status_counts: dict[str, int] = Field(alias="statusCounts")
    recent_orders: list[AdminOrderDetailOut] = Field(default_factory=list, alias="recentOrders")
    inventory_alerts: dict[str, Any] = Field(alias="inventoryAlerts")
    attention_count: int = Field(alias="attentionCount")


class AdminSalesBucket(BaseModel):
    """Sales bucket for dashboard chart series."""

    model_config = ConfigDict(populate_by_name=True)

    date: str
    timestamp: str
    sales: int
    sales_paise: int = Field(alias="salesPaise")
    order_count: int = Field(alias="orderCount")


class AdminSalesSeriesOut(BaseModel):
    """Sales trend response."""

    model_config = ConfigDict(populate_by_name=True)

    interval: str
    effective_range: dict[str, str] = Field(alias="effectiveRange")
    buckets: list[AdminSalesBucket]


class AdminFinanceSummaryOut(BaseModel):
    """Detailed financial breakdown and reconciliation."""

    model_config = ConfigDict(populate_by_name=True)

    effective_range: dict[str, str] = Field(alias="effectiveRange")
    gross_sales: int = Field(alias="grossSales")
    gross_sales_paise: int = Field(alias="grossSalesPaise")
    discounts: int
    discounts_paise: int = Field(alias="discountsPaise")
    shipping_collected: int = Field(alias="shippingCollected")
    shipping_collected_paise: int = Field(alias="shippingCollectedPaise")
    stored_tax: int = Field(alias="storedTax")
    stored_tax_paise: int = Field(alias="storedTaxPaise")
    refunds: int
    refunds_paise: int = Field(alias="refundsPaise")
    gateway_fees: int | None = Field(default=None, alias="gatewayFees")
    gateway_fees_available: bool = Field(default=False, alias="gatewayFeesAvailable")
    adjustments: int = 0
    adjustments_paise: int = Field(default=0, alias="adjustmentsPaise")
    net_revenue: int = Field(alias="netRevenue")
    net_revenue_paise: int = Field(alias="netRevenuePaise")
    taxable_sales: int = Field(alias="taxableSales")
    taxable_sales_paise: int = Field(alias="taxableSalesPaise")
    order_count: int = Field(alias="orderCount")
    refund_count: int = Field(alias="refundCount")


class AdminFinanceSalesBucket(BaseModel):
    """Finance trend bucket."""

    model_config = ConfigDict(populate_by_name=True)

    date: str
    timestamp: str
    gross_sales: int = Field(alias="grossSales")
    discounts: int
    refunds: int
    net_revenue: int = Field(alias="netRevenue")
    order_count: int = Field(alias="orderCount")


class AdminFinanceSeriesOut(BaseModel):
    """Finance trend response."""

    model_config = ConfigDict(populate_by_name=True)

    interval: str
    effective_range: dict[str, str] = Field(alias="effectiveRange")
    buckets: list[AdminFinanceSalesBucket]


class AdminAttentionItem(BaseModel):
    """Actionable alert item requiring admin intervention."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    severity: str  # CRITICAL, HIGH, WARNING, INFO
    rule: str
    title: str
    message: str
    order_number: str | None = Field(default=None, alias="orderNumber")
    order_id: int | None = Field(default=None, alias="orderId")
    variant_id: int | None = Field(default=None, alias="variantId")
    product_id: int | None = Field(default=None, alias="productId")
    created_at: datetime | None = Field(default=None, alias="createdAt")
    action_url: str | None = Field(default=None, alias="actionUrl")


class AdminAttentionListOut(BaseModel):
    """Paginated list of action-needed attention items."""

    model_config = ConfigDict(populate_by_name=True)

    items: list[AdminAttentionItem]
    total: int
    page: int
    page_size: int = Field(alias="pageSize")


class AdminSearchResultItem(BaseModel):
    """Item returned from global admin search."""

    model_config = ConfigDict(populate_by_name=True)

    kind: str  # 'order' | 'product' | 'customer' | 'variant'
    id: str
    title: str
    subtitle: str | None = None
    badge: str | None = None
    url: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class AdminGlobalSearchOut(BaseModel):
    """Global admin search result."""

    model_config = ConfigDict(populate_by_name=True)

    query: str
    total: int
    items: list[AdminSearchResultItem]
    page: int
    page_size: int = Field(alias="pageSize")


# -----------------------------------------------------------------------------
# Returns & Refunds Schemas
# -----------------------------------------------------------------------------


class AdminReturnItemIn(BaseModel):
    """Item to return within a return request."""

    model_config = ConfigDict(populate_by_name=True)

    order_item_id: int = Field(alias="orderItemId")
    quantity: int = Field(default=1, ge=1)
    reason: str | None = None


class AdminReturnCreateIn(BaseModel):
    """Payload to create a return request."""

    model_config = ConfigDict(populate_by_name=True)

    order_number: str = Field(alias="orderNumber")
    reason: str = Field(..., description="e.g. DEFECTIVE, WRONG_ITEM, NOT_AS_DESCRIBED, SIZE_FIT, OTHER")
    reason_details: str | None = Field(default=None, alias="reasonDetails")
    items: list[AdminReturnItemIn] = Field(default_factory=list)
    admin_notes: str | None = Field(default=None, alias="adminNotes")


class AdminReturnStatusUpdateIn(BaseModel):
    """Payload to transition return request status."""

    model_config = ConfigDict(populate_by_name=True)

    status: str = Field(..., description="APPROVED, REJECTED, ITEMS_RECEIVED, CANCELLED")
    note: str | None = Field(default=None, description="Optional audit note")


class AdminReturnRefundIn(BaseModel):
    """Payload to execute refund on a return request."""

    model_config = ConfigDict(populate_by_name=True)

    amount: int | None = Field(default=None, ge=1, description="Partial refund amount in rupees, or null for full return amount")
    note: str | None = Field(default=None, description="Audit note recorded in history")


class AdminReturnItemOut(BaseModel):
    """Item inside return response."""

    model_config = ConfigDict(populate_by_name=True)

    order_item_id: int = Field(alias="orderItemId")
    product_name: str = Field(alias="productName")
    sku: str
    quantity: int
    unit_price: int = Field(alias="unitPrice")
    line_total: int = Field(alias="lineTotal")


class AdminReturnDetailOut(BaseModel):
    """Full detail of a return and refund request."""

    model_config = ConfigDict(populate_by_name=True)

    id: int
    return_number: str = Field(alias="returnNumber")
    order_id: int = Field(alias="orderId")
    order_number: str = Field(alias="orderNumber")
    customer_name: str = Field(alias="customerName")
    customer_email: str | None = Field(default=None, alias="customerEmail")
    customer_phone: str = Field(alias="customerPhone")
    status: str
    reason: str
    reason_details: str | None = Field(default=None, alias="reasonDetails")
    items: list[AdminReturnItemOut] = Field(default_factory=list)
    refund_amount: int = Field(alias="refundAmount")
    refund_amount_paise: int = Field(alias="refundAmountPaise")
    refund_status: str = Field(alias="refundStatus")
    admin_notes: str | None = Field(default=None, alias="adminNotes")
    history: list[dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class AdminReturnListOut(BaseModel):
    """Paginated list of return requests."""

    model_config = ConfigDict(populate_by_name=True)

    items: list[AdminReturnDetailOut]
    total: int
    page: int
    page_size: int = Field(alias="pageSize")


class AdminOccasionIn(BaseModel):
    """Payload to create a curated gift occasion."""

    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(..., description="Unique slug identifier (e.g. 'birthday', 'valentine')")
    name: str = Field(..., description="Display title for the occasion")
    icon: str | None = Field(default=None, description="Optional icon identifier or emoji")
    image_key: str | None = Field(default=None, alias="imageKey", description="Internal asset key, e.g. occasions/birthday.jpg")
    image_url: str | None = Field(default=None, alias="imageUrl", description="Public image URL override")
    description: str | None = Field(default=None, description="Optional editorial description")
    display_order: int = Field(default=0, alias="displayOrder", description="Sort order ascending")
    is_enabled: bool = Field(default=True, alias="isEnabled", description="Whether active on storefront")
    starts_at: datetime | None = Field(default=None, alias="startsAt", description="Active start datetime (Asia/Kolkata)")
    ends_at: datetime | None = Field(default=None, alias="endsAt", description="Active end datetime (Asia/Kolkata)")
    product_ids: list[int] = Field(default_factory=list, alias="productIds", description="Associated product IDs")


class AdminOccasionUpdateIn(BaseModel):
    """Payload to update a curated gift occasion."""

    model_config = ConfigDict(populate_by_name=True)

    name: str | None = None
    icon: str | None = None
    image_key: str | None = Field(default=None, alias="imageKey")
    image_url: str | None = Field(default=None, alias="imageUrl")
    description: str | None = None
    display_order: int | None = Field(default=None, alias="displayOrder")
    is_enabled: bool | None = Field(default=None, alias="isEnabled")
    starts_at: datetime | None = Field(default=None, alias="startsAt")
    ends_at: datetime | None = Field(default=None, alias="endsAt")
    product_ids: list[int] | None = Field(default=None, alias="productIds")


class AdminOccasionOut(BaseModel):
    """Detailed occasion representation for admin management."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    name: str
    icon: str | None = None
    image_key: str | None = Field(default=None, alias="imageKey", serialization_alias="imageKey")
    image_url: str | None = Field(default=None, alias="imageUrl", serialization_alias="imageUrl")
    description: str | None = None
    display_order: int = Field(default=0, alias="displayOrder", serialization_alias="displayOrder")
    is_enabled: bool = Field(default=True, alias="isEnabled", serialization_alias="isEnabled")
    is_evergreen: bool = Field(default=False, alias="isEvergreen", serialization_alias="isEvergreen")
    starts_at: datetime | None = Field(default=None, alias="startsAt", serialization_alias="startsAt")
    ends_at: datetime | None = Field(default=None, alias="endsAt", serialization_alias="endsAt")
    product_count: int = Field(default=0, alias="productCount", serialization_alias="productCount")
    product_ids: list[int] = Field(default_factory=list, alias="productIds", serialization_alias="productIds")
    created_at: datetime | None = Field(default=None, alias="createdAt", serialization_alias="createdAt")
    updated_at: datetime | None = Field(default=None, alias="updatedAt", serialization_alias="updatedAt")


class AdminTagCreate(BaseModel):
    """Payload to create or get an existing tag."""

    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(..., min_length=1, max_length=50, description="Tag name")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Tag name cannot be empty or whitespace only")
        if len(trimmed) > 50:
            raise ValueError("Tag name cannot exceed 50 characters")
        return trimmed


class AdminTagOut(BaseModel):
    """Admin representation of a tag."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    name: str


# -----------------------------------------------------------------------------
# Customer Management (Task 1.9.1)
# -----------------------------------------------------------------------------


class AdminCustomerOut(BaseModel):
    """Admin representation of a customer profile."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    status: str
    created_at: datetime | None = Field(default=None, alias="createdAt")
    last_login_at: datetime | None = Field(default=None, alias="lastLoginAt")
    order_count: int = Field(default=0, alias="orderCount")


class AdminCustomerListOut(BaseModel):
    """Paginated list of customers for administration."""

    model_config = ConfigDict(populate_by_name=True)

    items: list[AdminCustomerOut]
    total: int
    page: int
    page_size: int = Field(alias="pageSize")
