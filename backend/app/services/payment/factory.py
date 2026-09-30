"""Payment provider factory and registry."""

import os
from app.services.payment.base import BasePaymentProvider
from app.services.payment.mock import MockPaymentProvider
from app.services.payment.razorpay import RazorpayPaymentProvider

_PROVIDERS: dict[str, type[BasePaymentProvider]] = {
    "mock": MockPaymentProvider,
    "razorpay": RazorpayPaymentProvider,
}


def get_payment_provider(provider_name: str | None = None) -> BasePaymentProvider:
    """Resolve payment provider instance.

    Defaults to 'razorpay' if RAZORPAY_KEY_ID is configured, otherwise 'mock'.
    """
    if not provider_name:
        has_razorpay = bool(os.getenv("RAZORPAY_KEY_ID"))
        provider_name = "razorpay" if has_razorpay else "mock"

    provider_cls = _PROVIDERS.get(provider_name.lower(), MockPaymentProvider)
    return provider_cls()
