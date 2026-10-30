"""Payment provider factory and registry."""

from app.core.config import config_value, settings
from app.services.payment.base import BasePaymentProvider, PaymentGatewayConfigurationError
from app.services.payment.cashfree import CashfreePaymentProvider
from app.services.payment.mock import MockPaymentProvider
from app.services.payment.razorpay import RazorpayPaymentProvider

_PROVIDERS: dict[str, type[BasePaymentProvider]] = {
    "mock": MockPaymentProvider,
    "razorpay": RazorpayPaymentProvider,
    "cashfree": CashfreePaymentProvider,
}


def get_payment_provider(provider_name: str | None = None) -> BasePaymentProvider:
    """Resolve payment provider instance.

    Defaults to PAYMENT_PROVIDER env var, then 'razorpay' if RAZORPAY_KEY_ID is configured,
    otherwise 'mock'. Mock provider is forbidden when APP_ENV=production (fail-closed).
    Unknown provider names fail closed without falling back to MockPaymentProvider.
    """
    if not provider_name:
        provider_name = (config_value("PAYMENT_PROVIDER", "") or settings.payment_provider or "").strip().lower()

    if not provider_name:
        has_razorpay = bool(settings.razorpay_key_id)
        provider_name = "razorpay" if has_razorpay else "mock"

    normalized = provider_name.strip().lower()

    # Fail closed: mock payment is not allowed in production
    if normalized == "mock" and settings.app_env.strip().lower() == "production":
        raise RuntimeError(
            "PAYMENT_PROVIDER=mock is not allowed in production (APP_ENV=production). "
            "Configure PAYMENT_PROVIDER=cashfree or PAYMENT_PROVIDER=razorpay with valid credentials."
        )

    provider_cls = _PROVIDERS.get(normalized)
    if not provider_cls:
        raise PaymentGatewayConfigurationError(
            f"Unsupported payment provider '{provider_name}'. Supported providers: cashfree, razorpay, mock."
        )
    return provider_cls()
