"""Factory functions to instantiate SMS and Email notification providers based on configuration."""

from app.core.config import settings
from app.services.notification.base import BaseEmailProvider, BaseSmsProvider
from app.services.notification.email import MockEmailProvider, ResendEmailProvider, SmtpEmailProvider
from app.services.notification.sms import Fast2SmsProvider, MockSmsProvider, TwilioSmsProvider

# Shared singleton instances for mock providers to easily inspect in tests
_mock_sms_instance: MockSmsProvider | None = None
_mock_email_instance: MockEmailProvider | None = None


def get_sms_provider() -> BaseSmsProvider:
    """Return configured SMS provider instance."""
    global _mock_sms_instance
    provider_name = (settings.sms_provider or "mock").lower()

    if provider_name == "fast2sms":
        return Fast2SmsProvider()
    elif provider_name == "twilio":
        return TwilioSmsProvider()

    # Default to mock
    if _mock_sms_instance is None:
        _mock_sms_instance = MockSmsProvider()
    return _mock_sms_instance


def get_email_provider() -> BaseEmailProvider:
    """Return configured Email provider instance."""
    global _mock_email_instance
    provider_name = (settings.email_provider or "mock").lower()

    if provider_name == "smtp":
        return SmtpEmailProvider()
    elif provider_name == "resend":
        return ResendEmailProvider()

    # Default to mock
    if _mock_email_instance is None:
        _mock_email_instance = MockEmailProvider()
    return _mock_email_instance
