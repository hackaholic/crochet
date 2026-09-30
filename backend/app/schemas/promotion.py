"""Pydantic schemas for Promotions and Coupons."""

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class CouponApplyRequest(BaseModel):
    """Payload to apply a promotional coupon code."""

    model_config = ConfigDict(populate_by_name=True)

    code: str = Field(..., min_length=2, max_length=50, description="Coupon promo code, e.g. 'WELCOME10'")


class CouponApplyResponse(BaseModel):
    """Result of applying a promotional coupon to cart."""

    model_config = ConfigDict(populate_by_name=True)

    code: str
    discount_type: str = Field(alias="discountType")
    discount_value: int = Field(alias="discountValue")
    discount_amount: int = Field(alias="discountAmount")
    discount_amount_paise: int = Field(alias="discountAmountPaise")
    subtotal_before_discount: int = Field(alias="subtotalBeforeDiscount")
    subtotal_after_discount: int = Field(alias="subtotalAfterDiscount")
    subtotal_after_discount_paise: int = Field(alias="subtotalAfterDiscountPaise")
    message: str = "Coupon applied successfully"


class AdminCouponCreate(BaseModel):
    """Payload to create a new promo coupon."""

    model_config = ConfigDict(populate_by_name=True)

    code: str = Field(..., min_length=2, max_length=50)
    description: str | None = None
    discount_type: str = Field(..., alias="discountType", description="PERCENTAGE or FLAT")
    discount_value: int = Field(..., alias="discountValue", ge=1)
    min_order_amount: int = Field(default=0, alias="minOrderAmount", ge=0)
    max_discount_amount: int | None = Field(default=None, alias="maxDiscountAmount", ge=0)
    usage_limit: int | None = Field(default=None, alias="usageLimit", ge=1)
    valid_until: datetime | None = Field(default=None, alias="validUntil")
    is_active: bool = Field(default=True, alias="isActive")


class AdminCouponUpdate(BaseModel):
    """Payload to update an existing coupon."""

    model_config = ConfigDict(populate_by_name=True)

    description: str | None = None
    discount_type: str | None = Field(default=None, alias="discountType")
    discount_value: int | None = Field(default=None, alias="discountValue", ge=1)
    min_order_amount: int | None = Field(default=None, alias="minOrderAmount", ge=0)
    max_discount_amount: int | None = Field(default=None, alias="maxDiscountAmount")
    usage_limit: int | None = Field(default=None, alias="usageLimit")
    valid_until: datetime | None = Field(default=None, alias="validUntil")
    is_active: bool | None = Field(default=None, alias="isActive")


class AdminCouponOut(BaseModel):
    """Full coupon representation for administration."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    code: str
    description: str | None = None
    discount_type: str = Field(alias="discountType")
    discount_value: int = Field(alias="discountValue")
    min_order_amount: int = Field(alias="minOrderAmount")
    max_discount_amount: int | None = Field(default=None, alias="maxDiscountAmount")
    usage_limit: int | None = Field(default=None, alias="usageLimit")
    usage_count: int = Field(alias="usageCount")
    valid_from: datetime = Field(alias="validFrom")
    valid_until: datetime | None = Field(default=None, alias="validUntil")
    is_active: bool = Field(alias="isActive")
    created_at: datetime = Field(alias="createdAt")
