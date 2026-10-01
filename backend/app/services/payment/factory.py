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

    Defaults to PAYMENT_PROVIDER env var, then 'razorpay' if RAZORPAY_KEY_ID is configured,
    otherwise 'mock'. Mock provider is forbidden when APP_ENV=production (fail-closed).
    """
    if not provider_name:
        provider_name = os.getenv("PAYMENT_PROVIDER", "").lower()

    if not provider_name:
        has_razorpay = bool(os.getenv("RAZORPAY_KEY_ID"))
        provider_name = "razorpay" if has_razorpay else "mock"

    # Fail closed: mock payment is not allowed in production
    if provider_name == "mock" and os.getenv("APP_ENV", "development") == "production":
        raise RuntimeError(
            "PAYMENT_PROVIDER=mock is not allowed in production (APP_ENV=production). "
            "Set PAYMENT_PROVIDER=razorpay and configure RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET."
        )

    provider_cls = _PROVIDERS.get(provider_name.lower(), MockPaymentProvider)
    return provider_cls()
