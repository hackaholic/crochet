"""Pydantic schemas for Payments.

Conforms to Section 25 (Payment Architecture) of the Specification.
"""

from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class PaymentIntentCreate(BaseModel):
    """Request to initiate or retry payment for an existing order."""

    model_config = ConfigDict(populate_by_name=True)

    order_id: int | None = Field(default=None, ge=1, le=2_147_483_647, alias="orderId", description="Database ID of the order")
    order_number: str | None = Field(default=None, max_length=64, alias="orderNumber", description="Readable order number (e.g. CB-20260930-XXXX)")
    provider: str | None = Field(default=None, max_length=32, description="Payment provider: 'cashfree', 'razorpay', or 'mock'")
    guest_order_token: str | None = Field(
        default=None,
        max_length=256,
        alias="guestOrderToken",
        description="Order-scoped guest capability token (required for guest orders if not sent via header)",
    )
    guest_tracking_token: str | None = Field(
        default=None,
        max_length=256,
        alias="guestTrackingToken",
        description="Alias for guestOrderToken matching OrderOut.guestTrackingToken",
    )


class PaymentRetryRequest(BaseModel):
    """Request to create a new payment attempt for the same unpaid order after a failed or pending attempt."""

    model_config = ConfigDict(populate_by_name=True)

    provider: str | None = Field(default=None, max_length=32, description="Optional payment provider override")
    guest_order_token: str | None = Field(
        default=None,
        max_length=256,
        alias="guestOrderToken",
        description="Order-scoped guest capability token (required for guest orders if not sent via header)",
    )
    guest_tracking_token: str | None = Field(
        default=None,
        max_length=256,
        alias="guestTrackingToken",
        description="Alias for guestOrderToken matching OrderOut.guestTrackingToken",
    )


class PaymentIntentOut(BaseModel):
    """Payment intent output returned to frontend checkout."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    payment_id: int = Field(..., serialization_alias="paymentId")
    order_id: int = Field(..., serialization_alias="orderId")
    order_number: str = Field(..., serialization_alias="orderNumber")
    provider: str
    provider_order_id: str | None = Field(default=None, serialization_alias="providerOrderId")
    payment_session_id: str | None = Field(default=None, serialization_alias="paymentSessionId")
    environment: str | None = Field(default=None, description="Gateway environment mode ('sandbox' or 'production')")
    return_url: str | None = Field(default=None, serialization_alias="returnUrl")
    amount: int
    amount_paise: int = Field(..., serialization_alias="amountPaise")
    currency: str = "INR"
    key_id: str | None = Field(default=None, serialization_alias="keyId")
    notes: dict[str, Any] = Field(default_factory=dict)


class PaymentVerifyRequest(BaseModel):
    """Client verification callback payload after gateway popup or redirect completion."""

    model_config = ConfigDict(populate_by_name=True)

    payment_id: int = Field(..., ge=1, le=2_147_483_647, alias="paymentId")
    provider_payment_id: str | None = Field(default=None, alias="providerPaymentId", description="Gateway payment ID (optional for Cashfree server-verified orders)")
    provider_order_id: str | None = Field(default=None, alias="providerOrderId", description="Gateway order ID")
    provider_signature: str | None = Field(default=None, alias="providerSignature", description="HMAC verification signature")
    payment_method_detail: str | None = Field(default=None, alias="paymentMethodDetail", description="e.g. UPI / Google Pay")


class PaymentOut(BaseModel):
    """Detailed payment record representation."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    order_id: int = Field(..., serialization_alias="orderId")
    order_number: str | None = Field(default=None, serialization_alias="orderNumber")
    order_status: str | None = Field(default=None, serialization_alias="orderStatus")
    order_payment_status: str | None = Field(default=None, serialization_alias="orderPaymentStatus")
    provider: str
    provider_payment_id: str | None = Field(default=None, serialization_alias="providerPaymentId")
    provider_order_id: str | None = Field(default=None, serialization_alias="providerOrderId")
    amount: int
    amount_paise: int = Field(..., serialization_alias="amountPaise")
    currency: str = "INR"
    status: str
    verification_state: str | None = Field(default=None, serialization_alias="verificationState")
    can_retry: bool = Field(default=False, serialization_alias="canRetry")
    error_message: str | None = Field(default=None, serialization_alias="errorMessage")
    payment_method_detail: str | None = Field(default=None, serialization_alias="paymentMethodDetail")
    created_at: str = Field(..., serialization_alias="createdAt")
    updated_at: str = Field(..., serialization_alias="updatedAt")


class PaymentWebhookResult(BaseModel):
    """Webhook acknowledgment response."""

    status: str = "ok"
    message: str
