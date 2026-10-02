"""Abstract base class for payment providers.

Conforms to Section 25 (Payment Architecture) of the Specification.
"""

from abc import ABC, abstractmethod
from typing import Any
from app.models.order import Order
from app.models.payment import Payment


class BasePaymentProvider(ABC):
    """Payment provider interface decoupling orders from specific gateway vendors."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the payment provider."""
        pass

    @abstractmethod
    def create_intent(self, order: Order, payment: Payment) -> dict[str, Any]:
        """Create a payment order/intent with the gateway and return client checkout payload."""
        pass

    @abstractmethod
    def verify_payment(self, payment: Payment, payload: dict[str, Any]) -> bool:
        """Verify signature or transaction status from frontend payment callback."""
        pass

    @abstractmethod
    def verify_webhook(self, payload: bytes, signature: str) -> bool:
        """Verify gateway webhook payload authenticity."""
        pass

    def refund_payment(self, payment: Payment, amount: int, reason: str | None = None) -> dict[str, Any]:
        """Process refund with the payment provider."""
        raise NotImplementedError
