"""Pydantic schemas for Payments.

Conforms to Section 25 (Payment Architecture) of the Specification.
"""

from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class PaymentIntentCreate(BaseModel):
    """Request to initiate payment for an existing order."""

    model_config = ConfigDict(populate_by_name=True)

    order_id: int | None = Field(default=None, alias="orderId", description="Database ID of the order")
    order_number: str | None = Field(default=None, alias="orderNumber", description="Readable order number (e.g. CB-20260930-XXXX)")
    provider: str | None = Field(default=None, description="Payment provider: 'razorpay' or 'mock'")


class PaymentIntentOut(BaseModel):
    """Payment intent output returned to frontend checkout."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    payment_id: int = Field(..., serialization_alias="paymentId")
    order_id: int = Field(..., serialization_alias="orderId")
    order_number: str = Field(..., serialization_alias="orderNumber")
    provider: str
    provider_order_id: str | None = Field(default=None, serialization_alias="providerOrderId")
    amount: int
    amount_paise: int = Field(..., serialization_alias="amountPaise")
    currency: str = "INR"
    key_id: str | None = Field(default=None, serialization_alias="keyId")
    notes: dict[str, Any] = Field(default_factory=dict)


class PaymentVerifyRequest(BaseModel):
    """Client verification callback payload after gateway popup completion."""

    model_config = ConfigDict(populate_by_name=True)

    payment_id: int = Field(..., alias="paymentId")
    provider_payment_id: str = Field(..., alias="providerPaymentId", description="Gateway payment ID (e.g. pay_XXXX)")
    provider_order_id: str | None = Field(default=None, alias="providerOrderId", description="Gateway order ID")
    provider_signature: str | None = Field(default=None, alias="providerSignature", description="HMAC verification signature")
    payment_method_detail: str | None = Field(default=None, alias="paymentMethodDetail", description="e.g. UPI / Google Pay")


class PaymentOut(BaseModel):
    """Detailed payment record representation."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    order_id: int = Field(..., serialization_alias="orderId")
    provider: str
    provider_payment_id: str | None = Field(default=None, serialization_alias="providerPaymentId")
    provider_order_id: str | None = Field(default=None, serialization_alias="providerOrderId")
    amount: int
    amount_paise: int = Field(..., serialization_alias="amountPaise")
    currency: str = "INR"
    status: str
    payment_method_detail: str | None = Field(default=None, serialization_alias="paymentMethodDetail")
    created_at: str = Field(..., serialization_alias="createdAt")
    updated_at: str = Field(..., serialization_alias="updatedAt")


class PaymentWebhookResult(BaseModel):
    """Webhook acknowledgment response."""

    status: str = "ok"
    message: str
