"""Pydantic schemas for Addresses, Checkout, and Orders.

Conforms to Sections 18, 20, 21, and 26 of the E-commerce Multi-Agent Specification.
"""

from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class AddressBase(BaseModel):
    """Base address fields."""

    name: str = Field(..., min_length=2, max_length=100, description="Recipient full name")
    phone: str = Field(..., min_length=10, max_length=20, description="10-digit contact mobile number")
    line1: str = Field(..., min_length=3, max_length=255, description="House/Flat number, building name, street")
    line2: str | None = Field(default=None, max_length=255, description="Apartment, suite, unit, etc.")
    landmark: str | None = Field(default=None, max_length=255, description="Nearby landmark")
    city: str = Field(..., min_length=2, max_length=100, description="City/District")
    state: str = Field(..., min_length=2, max_length=100, description="State/Province")
    postal_code: str = Field(..., min_length=6, max_length=10, alias="postalCode", description="6-digit Indian PIN code")
    country: str = Field(default="IN", description="ISO 3166-1 alpha-2 country code")
    is_default: bool = Field(default=False, alias="isDefault", description="Set as default delivery address")


class AddressCreate(AddressBase):
    """Schema to create a new address."""

    model_config = ConfigDict(populate_by_name=True)


class AddressUpdate(BaseModel):
    """Schema to update an existing address."""

    model_config = ConfigDict(populate_by_name=True)

    name: str | None = Field(default=None, min_length=2, max_length=100)
    phone: str | None = Field(default=None, min_length=10, max_length=20)
    line1: str | None = Field(default=None, min_length=3, max_length=255)
    line2: str | None = None
    landmark: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = Field(default=None, min_length=6, max_length=10, alias="postalCode")
    country: str | None = None
    is_default: bool | None = Field(default=None, alias="isDefault")


class AddressOut(BaseModel):
    """Address output representation."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    user_id: int = Field(..., serialization_alias="userId")
    name: str
    phone: str
    line1: str
    line2: str | None = None
    landmark: str | None = None
    city: str
    state: str
    postal_code: str = Field(..., serialization_alias="postalCode")
    country: str = "IN"
    is_default: bool = Field(default=False, serialization_alias="isDefault")
    created_at: str = Field(..., serialization_alias="createdAt")


class OrderItemOut(BaseModel):
    """Snapshotted line item of an order."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    order_id: int = Field(..., serialization_alias="orderId")
    product_id: int | None = Field(default=None, serialization_alias="productId")
    product_variant_id: int | None = Field(default=None, serialization_alias="productVariantId")
    product_name: str = Field(..., serialization_alias="productName")
    product_slug: str | None = Field(default=None, serialization_alias="productSlug")
    sku: str
    variant_name: str = Field(..., serialization_alias="variantName")
    product_image: str | None = Field(default=None, serialization_alias="productImage")
    unit_price: int = Field(..., serialization_alias="unitPrice")
    unit_price_paise: int = Field(..., serialization_alias="unitPricePaise")
    quantity: int
    line_total: int = Field(..., serialization_alias="lineTotal")
    line_total_paise: int = Field(..., serialization_alias="lineTotalPaise")
    personalization: dict[str, Any] = Field(default_factory=dict)


class OrderStatusHistoryOut(BaseModel):
    """Audit log entry for order status transition."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    status: str
    note: str | None = None
    timestamp: str


class OrderCreate(BaseModel):
    """Order checkout request."""

    model_config = ConfigDict(populate_by_name=True)

    address_id: int | None = Field(default=None, alias="addressId", description="ID of saved address to use")
    shipping_address: AddressCreate | None = Field(default=None, alias="shippingAddress", description="Inline address if not using saved address")
    payment_method: str = Field(default="COD", alias="paymentMethod", description="Payment method: COD, UPI, CARD, NETBANKING")
    customer_name: str | None = Field(default=None, alias="customerName", description="Customer full name")
    customer_phone: str | None = Field(default=None, alias="customerPhone", description="Customer mobile number")
    customer_email: str | None = Field(default=None, alias="customerEmail", description="Customer email address")
    coupon_code: str | None = Field(default=None, alias="couponCode", description="Optional promo coupon code")
    notes: str | None = Field(default=None, max_length=500, description="Optional delivery or gift notes")


class OrderOut(BaseModel):
    """Detailed order response representation."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    order_number: str = Field(..., serialization_alias="orderNumber")
    user_id: int | None = Field(default=None, serialization_alias="userId")
    customer_name: str = Field(..., serialization_alias="customerName")
    customer_phone: str = Field(..., serialization_alias="customerPhone")
    customer_email: str | None = Field(default=None, serialization_alias="customerEmail")
    shipping_address: dict[str, Any] = Field(..., serialization_alias="shippingAddress")
    billing_address: dict[str, Any] | None = Field(default=None, serialization_alias="billingAddress")
    status: str
    payment_status: str = Field(..., serialization_alias="paymentStatus")
    payment_method: str = Field(..., serialization_alias="paymentMethod")
    currency: str = "INR"
    subtotal: int
    subtotal_paise: int = Field(..., serialization_alias="subtotalPaise")
    shipping_fee: int = Field(..., serialization_alias="shippingFee")
    shipping_fee_paise: int = Field(..., serialization_alias="shippingFeePaise")
    discount_amount: int = Field(default=0, serialization_alias="discountAmount")
    discount_amount_paise: int = Field(default=0, serialization_alias="discountAmountPaise")
    tax_amount: int = Field(default=0, serialization_alias="taxAmount")
    tax_amount_paise: int = Field(default=0, serialization_alias="taxAmountPaise")
    total_amount: int = Field(..., serialization_alias="totalAmount")
    total_amount_paise: int = Field(..., serialization_alias="totalAmountPaise")
    notes: str | None = None
    items: list[OrderItemOut] = []
    status_history: list[OrderStatusHistoryOut] = Field(default_factory=list, serialization_alias="statusHistory")
    tracking_number: str | None = Field(default=None, serialization_alias="trackingNumber")
    courier_name: str | None = Field(default=None, serialization_alias="courierName")
    estimated_delivery: str | None = Field(default=None, serialization_alias="estimatedDelivery")
    created_at: str = Field(..., serialization_alias="createdAt")
    updated_at: str = Field(..., serialization_alias="updatedAt")


class OrderTrackingOut(BaseModel):
    """Order tracking details and timeline."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    order_number: str = Field(..., serialization_alias="orderNumber")
    status: str
    payment_status: str = Field(..., serialization_alias="paymentStatus")
    tracking_number: str | None = Field(default=None, serialization_alias="trackingNumber")
    courier_name: str | None = Field(default=None, serialization_alias="courierName")
    estimated_delivery: str | None = Field(default=None, serialization_alias="estimatedDelivery")
    timeline: list[OrderStatusHistoryOut] = []
