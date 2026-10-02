"""Mock payment provider for local development, sandbox, and automated tests."""

import secrets
from typing import Any
from app.models.order import Order
from app.models.payment import Payment
from app.services.payment.base import BasePaymentProvider


class MockPaymentProvider(BasePaymentProvider):
    """Zero-credential mock payment gateway for reliable automated testing and local frontend integration."""

    @property
    def provider_name(self) -> str:
        return "mock"

    def create_intent(self, order: Order, payment: Payment) -> dict[str, Any]:
        """Generate a mock gateway order ID and client intent parameters."""
        mock_order_id = f"mock_order_{secrets.token_hex(8)}"
        payment.provider_order_id = mock_order_id
        return {
            "provider": self.provider_name,
            "providerOrderId": mock_order_id,
            "amount": payment.amount,
            "amountPaise": payment.amount_paise,
            "currency": payment.currency,
            "keyId": "mock_key_crochet_bloom",
            "notes": {
                "orderNumber": order.order_number,
                "customerName": order.customer_name,
            },
        }

    def verify_payment(self, payment: Payment, payload: dict[str, Any]) -> bool:
        """Verify client verification payload. Fails if provider_payment_id starts with 'fail_'."""
        payment_id = payload.get("provider_payment_id") or payload.get("providerPaymentId")
        if not payment_id:
            return False
        if str(payment_id).startswith("fail_"):
            return False
        return True

    def verify_webhook(self, payload: bytes, signature: str) -> bool:
        """Verify mock webhook signature."""
        return signature == "valid_mock_signature" or signature.startswith("mock_")

    def refund_payment(self, payment: Payment, amount: int, reason: str | None = None) -> dict[str, Any]:
        """Simulate refund in mock gateway."""
        refund_id = f"mock_rfnd_{secrets.token_hex(8)}"
        return {
            "success": True,
            "refund_id": refund_id,
            "amount": amount,
            "status": "COMPLETED",
        }
