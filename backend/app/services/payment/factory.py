"""Payment provider factory and registry."""

from app.core.config import config_value, settings
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
        provider_name = (config_value("PAYMENT_PROVIDER", "") or "").lower()

    if not provider_name:
        has_razorpay = bool(settings.razorpay_key_id)
        provider_name = "razorpay" if has_razorpay else "mock"

    # Fail closed: mock payment is not allowed in production
    if provider_name == "mock" and settings.app_env == "production":
        raise RuntimeError(
            "PAYMENT_PROVIDER=mock is not allowed in production (APP_ENV=production). "
            "Set PAYMENT_PROVIDER=razorpay and configure RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET."
        )

    provider_cls = _PROVIDERS.get(provider_name.lower(), MockPaymentProvider)
    return provider_cls()
