"""Pydantic schemas for Addresses, Checkout, and Orders.

Conforms to Sections 18, 20, 21, and 26 of the E-commerce Multi-Agent Specification.
"""

import re
from typing import Any
from pydantic import BaseModel, ConfigDict, Field, field_validator


class AddressBase(BaseModel):
    """Base address fields."""

    name: str = Field(..., max_length=100, description="Recipient full name")
    phone: str = Field(..., max_length=20, description="10-digit contact mobile number")
    line1: str = Field(..., max_length=255, description="House/Flat number, building name, street")
    line2: str | None = Field(default=None, max_length=255, description="Apartment, suite, unit, etc.")
    landmark: str | None = Field(default=None, max_length=255, description="Nearby landmark")
    city: str = Field(..., max_length=100, description="City/District")
    state: str = Field(..., max_length=100, description="State/Province")
    postal_code: str = Field(..., alias="postalCode", description="6-digit Indian PIN code")
    country: str = Field(default="IN", description="ISO 3166-1 alpha-2 country code")
    is_default: bool = Field(default=False, alias="isDefault", description="Set as default delivery address")

    @field_validator("name", mode="before")
    @classmethod
    def validate_name(cls, v: Any) -> str:
        if not isinstance(v, str) or not v.strip():
            raise ValueError("Name cannot be empty or blank")
        trimmed = v.strip()
        if len(trimmed) < 2 or len(trimmed) > 100:
            raise ValueError("Name must be between 2 and 100 characters")
        return trimmed

    @field_validator("phone", mode="before")
    @classmethod
    def validate_phone(cls, v: Any) -> str:
        if not isinstance(v, str) or not v.strip():
            raise ValueError("Phone number cannot be empty or blank")
        cleaned = re.sub(r"[\s\-]", "", v.strip())
        if not re.match(r"^(\+?[1-9]\d{7,14}|\d{10})$", cleaned):
            raise ValueError("Phone number must be a valid 10-digit or E.164 phone number")
        return cleaned

    @field_validator("line1", mode="before")
    @classmethod
    def validate_line1(cls, v: Any) -> str:
        if not isinstance(v, str) or not v.strip():
            raise ValueError("Address line 1 cannot be empty or blank")
        trimmed = v.strip()
        if len(trimmed) < 3 or len(trimmed) > 255:
            raise ValueError("Address line 1 must be between 3 and 255 characters")
        return trimmed

    @field_validator("line2", "landmark", mode="before")
    @classmethod
    def validate_optional_text(cls, v: Any) -> str | None:
        if v is None:
            return None
        if not isinstance(v, str):
            return str(v)
        trimmed = v.strip()
        return trimmed if trimmed else None

    @field_validator("city", "state", mode="before")
    @classmethod
    def validate_city_state(cls, v: Any) -> str:
        if not isinstance(v, str) or not v.strip():
            raise ValueError("City and State cannot be empty or blank")
        trimmed = v.strip()
        if len(trimmed) < 2 or len(trimmed) > 100:
            raise ValueError("City and State must be between 2 and 100 characters")
        return trimmed

    @field_validator("postal_code", mode="before")
    @classmethod
    def validate_postal_code(cls, v: Any) -> str:
        if not isinstance(v, str) or not v.strip():
            raise ValueError("PIN code cannot be empty or blank")
        cleaned = re.sub(r"\s+", "", v.strip())
        # Indian PIN code: 6 digits starting with 1-9
        if not re.match(r"^[1-9][0-9]{5}$", cleaned):
            raise ValueError("PIN code must be a valid 6-digit Indian Postal PIN code")
        return cleaned


class AddressCreate(AddressBase):
    """Schema to create a new address."""

    model_config = ConfigDict(populate_by_name=True)


class AddressUpdate(BaseModel):
    """Schema to update an existing address."""

    model_config = ConfigDict(populate_by_name=True)

    name: str | None = None
    phone: str | None = None
    line1: str | None = None
    line2: str | None = None
    landmark: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = Field(default=None, alias="postalCode")
    country: str | None = None
    is_default: bool | None = Field(default=None, alias="isDefault")

    @field_validator("name", mode="before")
    @classmethod
    def validate_update_name(cls, v: Any) -> str | None:
        if v is None:
            return None
        if not isinstance(v, str) or not v.strip():
            raise ValueError("Name cannot be empty or blank")
        trimmed = v.strip()
        if len(trimmed) < 2 or len(trimmed) > 100:
            raise ValueError("Name must be between 2 and 100 characters")
        return trimmed

    @field_validator("phone", mode="before")
    @classmethod
    def validate_update_phone(cls, v: Any) -> str | None:
        if v is None:
            return None
        if not isinstance(v, str) or not v.strip():
            raise ValueError("Phone number cannot be empty or blank")
        cleaned = re.sub(r"[\s\-]", "", v.strip())
        if not re.match(r"^(\+?[1-9]\d{7,14}|\d{10})$", cleaned):
            raise ValueError("Phone number must be a valid 10-digit or E.164 phone number")
        return cleaned

    @field_validator("line1", mode="before")
    @classmethod
    def validate_update_line1(cls, v: Any) -> str | None:
        if v is None:
            return None
        if not isinstance(v, str) or not v.strip():
            raise ValueError("Address line 1 cannot be empty or blank")
        trimmed = v.strip()
        if len(trimmed) < 3 or len(trimmed) > 255:
            raise ValueError("Address line 1 must be between 3 and 255 characters")
        return trimmed

    @field_validator("line2", "landmark", mode="before")
    @classmethod
    def validate_update_optional_text(cls, v: Any) -> str | None:
        if v is None:
            return None
        if not isinstance(v, str):
            return str(v)
        trimmed = v.strip()
        return trimmed if trimmed else None

    @field_validator("city", "state", mode="before")
    @classmethod
    def validate_update_city_state(cls, v: Any) -> str | None:
        if v is None:
            return None
        if not isinstance(v, str) or not v.strip():
            raise ValueError("City and State cannot be empty or blank")
        trimmed = v.strip()
        if len(trimmed) < 2 or len(trimmed) > 100:
            raise ValueError("City and State must be between 2 and 100 characters")
        return trimmed

    @field_validator("postal_code", mode="before")
    @classmethod
    def validate_update_postal_code(cls, v: Any) -> str | None:
        if v is None:
            return None
        if not isinstance(v, str) or not v.strip():
            raise ValueError("PIN code cannot be empty or blank")
        cleaned = re.sub(r"\s+", "", v.strip())
        if not re.match(r"^[1-9][0-9]{5}$", cleaned):
            raise ValueError("PIN code must be a valid 6-digit Indian Postal PIN code")
        return cleaned


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
    guest_tracking_token: str | None = Field(default=None, serialization_alias="guestTrackingToken")
    created_at: str = Field(..., serialization_alias="createdAt")
    updated_at: str = Field(..., serialization_alias="updatedAt")


class OrderMilestoneOut(BaseModel):
    """Lifecycle progress milestone for order tracking."""

    model_config = ConfigDict(populate_by_name=True)

    code: str
    label: str
    state: str  # "COMPLETED" | "CURRENT" | "PENDING"
    timestamp: str | None = None


class OrderTerminalStateOut(BaseModel):
    """Explanation for terminal non-delivered orders (cancelled / refunded)."""

    model_config = ConfigDict(populate_by_name=True)

    code: str
    label: str
    explanation: str
    timestamp: str | None = None


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
    milestones: list[OrderMilestoneOut] = []
    terminal_state: OrderTerminalStateOut | None = Field(default=None, serialization_alias="terminalState")


class GuestTrackingLinkRequest(BaseModel):
    """Request payload to issue a secure guest order tracking magic link."""

    model_config = ConfigDict(populate_by_name=True)

    order_number: str = Field(..., min_length=1, max_length=50, alias="orderNumber", description="Order number (e.g. SLC-...)")
    email: str = Field(..., min_length=3, max_length=255, description="Email address used during checkout")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        clean = v.strip().lower()
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", clean):
            raise ValueError("Invalid email format.")
        return clean


class GuestTrackingLinkResponse(BaseModel):
    """Generic non-enumerating response for tracking link request."""

    model_config = ConfigDict(populate_by_name=True)

    message: str = Field(..., description="Status message indicating processing status")
    dev_tracking_link: str | None = Field(default=None, alias="devTrackingLink", description="Included only in development/testing environments")

