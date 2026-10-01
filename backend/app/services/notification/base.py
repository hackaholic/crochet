"""Abstract base interfaces for SMS and Email notification providers."""

from abc import ABC, abstractmethod


class BaseSmsProvider(ABC):
    """Abstract SMS delivery provider interface."""

    @abstractmethod
    def send_otp(self, phone: str, otp_code: str) -> tuple[bool, str | None]:
        """Send a 6-digit OTP verification code to a mobile phone number.

        Returns:
            tuple[bool, str | None]: (success_flag, error_message_or_none)
        """
        pass

    @abstractmethod
    def send_sms(self, phone: str, message: str) -> tuple[bool, str | None]:
        """Send an arbitrary plain-text transactional SMS message.

        Returns:
            tuple[bool, str | None]: (success_flag, error_message_or_none)
        """
        pass


class BaseEmailProvider(ABC):
    """Abstract Email delivery provider interface."""

    @abstractmethod
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str | None = None,
        from_email: str | None = None,
    ) -> tuple[bool, str | None]:
        """Send a transactional HTML/text email to a recipient.

        Returns:
            tuple[bool, str | None]: (success_flag, error_message_or_none)
        """
        pass
