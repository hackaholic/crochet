"""Razorpay payment provider conforming to Indian online payment standards."""

import hashlib
import hmac
from typing import Any
import httpx

from app.core.config import settings
from app.models.order import Order
from app.models.payment import Payment
from app.services.payment.base import (
    BasePaymentProvider,
    PaymentGatewayError,
    PaymentGatewayConfigurationError,
)

RAZORPAY_API_BASE = "https://api.razorpay.com/v1"


class RazorpayPaymentProvider(BasePaymentProvider):
    """Production provider for Razorpay gateway (UPI, Netbanking, Cards, Wallets)."""

    def __init__(self, key_id: str | None = None, key_secret: str | None = None):
        self.key_id = (key_id if key_id is not None else settings.razorpay_key_id) or ""
        self.key_secret = (key_secret if key_secret is not None else settings.razorpay_key_secret) or ""
        self.webhook_secret = settings.razorpay_webhook_secret or self.key_secret

    @property
    def provider_name(self) -> str:
        return "razorpay"

    def create_intent(self, order: Order, payment: Payment) -> dict[str, Any]:
        """Create Razorpay order intent via real gateway API call."""
        if not self.key_id or not self.key_secret:
            raise PaymentGatewayConfigurationError(
                "Razorpay key_id and key_secret must be configured to create payment intents."
            )

        payload = {
            "amount": int(payment.amount_paise),
            "currency": payment.currency or "INR",
            "receipt": order.order_number,
            "notes": {
                "orderNumber": order.order_number,
                "customerPhone": order.customer_phone or "",
            },
        }

        try:
            with httpx.Client(timeout=15.0) as client:
                response = client.post(
                    f"{RAZORPAY_API_BASE}/orders",
                    auth=(self.key_id, self.key_secret),
                    json=payload,
                )
        except httpx.RequestError as exc:
            raise PaymentGatewayError(f"Razorpay gateway connection error: {exc}") from exc

        if response.status_code != 200:
            try:
                err_data = response.json()
                err_desc = err_data.get("error", {}).get("description") or response.text
            except Exception:
                err_desc = response.text
            raise PaymentGatewayError(
                f"Razorpay order creation failed (HTTP {response.status_code}): {err_desc}"
            )

        data = response.json()
        rzp_order_id = data.get("id")
        if not rzp_order_id or not isinstance(rzp_order_id, str):
            raise PaymentGatewayError("Razorpay response did not include a valid order id.")

        payment.provider_order_id = rzp_order_id
        return {
            "provider": self.provider_name,
            "providerOrderId": rzp_order_id,
            "amount": payment.amount,
            "amountPaise": payment.amount_paise,
            "currency": payment.currency,
            "keyId": self.key_id,
            "notes": {
                "orderNumber": order.order_number,
                "customerPhone": order.customer_phone or "",
            },
        }

    def verify_payment(self, payment: Payment, payload: dict[str, Any]) -> bool:
        """Verify Razorpay payment signature with strict order binding and fail-closed semantics."""
        # Fail-closed: missing key_secret can never verify
        if not self.key_secret:
            return False

        razorpay_order_id = payload.get("provider_order_id") or payload.get("providerOrderId")
        razorpay_payment_id = payload.get("provider_payment_id") or payload.get("providerPaymentId")
        razorpay_signature = payload.get("provider_signature") or payload.get("providerSignature")

        if not razorpay_payment_id or not razorpay_order_id or not razorpay_signature:
            return False

        # Order binding guard: callback order ID must match stored payment.provider_order_id
        if payment.provider_order_id and razorpay_order_id != payment.provider_order_id:
            return False

        message = f"{razorpay_order_id}|{razorpay_payment_id}".encode("utf-8")
        generated_signature = hmac.new(
            self.key_secret.encode("utf-8"),
            message,
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(generated_signature, str(razorpay_signature).strip())

    def verify_webhook(self, payload: bytes, signature: str, timestamp: str | None = None) -> bool:
        """Verify Razorpay webhook signature with fail-closed semantics."""
        if not self.webhook_secret or not signature or not payload:
            return False

        generated_signature = hmac.new(
            self.webhook_secret.encode("utf-8"),
            payload,
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(generated_signature, signature.strip())

    def refund_payment(self, payment: Payment, amount: int, reason: str | None = None) -> dict[str, Any]:
        """Process refund via Razorpay gateway API call."""
        if not self.key_id or not self.key_secret:
            return {
                "success": False,
                "error": "Razorpay key_id and key_secret must be configured to process refunds.",
            }

        if not payment.provider_payment_id:
            return {
                "success": False,
                "error": "Cannot process refund: payment record has no provider_payment_id.",
            }

        refund_payload = {
            "amount": int(amount),
            "notes": {
                "reason": reason or "Customer requested refund",
            },
        }

        try:
            with httpx.Client(timeout=15.0) as client:
                response = client.post(
                    f"{RAZORPAY_API_BASE}/payments/{payment.provider_payment_id}/refund",
                    auth=(self.key_id, self.key_secret),
                    json=refund_payload,
                )
        except httpx.RequestError as exc:
            return {
                "success": False,
                "error": f"Failed to reach Razorpay refund API: {exc}",
            }

        if response.status_code not in (200, 201):
            try:
                err_data = response.json()
                err_desc = err_data.get("error", {}).get("description") or response.text
            except Exception:
                err_desc = response.text
            return {
                "success": False,
                "error": f"Razorpay refund failed (HTTP {response.status_code}): {err_desc}",
            }

        data = response.json()
        refund_id = data.get("id")
        rzp_status = str(data.get("status", "processed")).upper()
        final_status = "COMPLETED" if rzp_status in ("PROCESSED", "COMPLETED") else rzp_status

        return {
            "success": True,
            "refund_id": refund_id,
            "amount": amount,
            "status": final_status,
        }
