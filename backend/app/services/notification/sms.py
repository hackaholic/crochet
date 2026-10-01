"""SMS delivery providers: Mock, Fast2SMS (India), and Twilio."""

import logging
import httpx

from app.core.config import settings
from app.services.notification.base import BaseSmsProvider

logger = logging.getLogger("sulocraft.notifications.sms")


class MockSmsProvider(BaseSmsProvider):
    """Zero-credential mock SMS provider for automated testing and local development."""

    def __init__(self) -> None:
        self.sent_messages: list[dict] = []

    def send_otp(self, phone: str, otp_code: str) -> tuple[bool, str | None]:
        msg = f"Your Sulocraft verification code is: {otp_code}. Valid for 5 minutes. Do not share this code."
        return self.send_sms(phone, msg)

    def send_sms(self, phone: str, message: str) -> tuple[bool, str | None]:
        entry = {"phone": phone, "message": message, "provider": "mock"}
        self.sent_messages.append(entry)
        logger.info("[MockSMS] -> To: %s | Message: %s", phone, message)
        return True, None

    def clear(self) -> None:
        """Clear recorded messages (helpful for unit tests)."""
        self.sent_messages.clear()


class Fast2SmsProvider(BaseSmsProvider):
    """Production Fast2SMS provider for quick transactional OTPs and alerts in India (+91)."""

    FAST2SMS_ENDPOINT = "https://www.fast2sms.com/dev/bulkV2"

    def __init__(self, api_key: str | None = None, route: str | None = None) -> None:
        self.api_key = api_key or settings.fast2sms_api_key
        self.route = route or settings.fast2sms_route

    def _sanitize_phone(self, phone: str) -> str:
        """Ensure 10-digit Indian mobile number."""
        clean = "".join(filter(str.isdigit, phone))
        if clean.startswith("91") and len(clean) == 12:
            clean = clean[2:]
        return clean

    def send_otp(self, phone: str, otp_code: str) -> tuple[bool, str | None]:
        if not self.api_key:
            return False, "Fast2SMS API key not configured"

        clean_phone = self._sanitize_phone(phone)
        payload = {
            "variables_values": otp_code,
            "route": "otp",
            "numbers": clean_phone,
        }
        headers = {
            "authorization": self.api_key,
            "Content-Type": "application/json",
        }

        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.post(self.FAST2SMS_ENDPOINT, json=payload, headers=headers)
                data = resp.json()
                if resp.status_code == 200 and data.get("return") is True:
                    logger.info("Fast2SMS OTP sent successfully to %s", clean_phone)
                    return True, None
                err = data.get("message", ["Unknown error"])[0] if isinstance(data.get("message"), list) else str(data.get("message"))
                logger.error("Fast2SMS OTP failed for %s: %s", clean_phone, err)
                return False, err
        except Exception as e:
            logger.exception("Fast2SMS HTTP request error for %s", clean_phone)
            return False, str(e)

    def send_sms(self, phone: str, message: str) -> tuple[bool, str | None]:
        if not self.api_key:
            return False, "Fast2SMS API key not configured"

        clean_phone = self._sanitize_phone(phone)
        payload = {
            "message": message,
            "language": "english",
            "route": "q",
            "numbers": clean_phone,
        }
        headers = {
            "authorization": self.api_key,
            "Content-Type": "application/json",
        }

        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.post(self.FAST2SMS_ENDPOINT, json=payload, headers=headers)
                data = resp.json()
                if resp.status_code == 200 and data.get("return") is True:
                    logger.info("Fast2SMS message sent successfully to %s", clean_phone)
                    return True, None
                err = str(data.get("message", "Unknown error"))
                logger.error("Fast2SMS message failed for %s: %s", clean_phone, err)
                return False, err
        except Exception as e:
            logger.exception("Fast2SMS HTTP request error for %s", clean_phone)
            return False, str(e)


class TwilioSmsProvider(BaseSmsProvider):
    """Twilio SMS provider for global international delivery."""

    def __init__(
        self,
        account_sid: str | None = None,
        auth_token: str | None = None,
        from_phone: str | None = None,
    ) -> None:
        self.account_sid = account_sid or settings.twilio_account_sid
        self.auth_token = auth_token or settings.twilio_auth_token
        self.from_phone = from_phone or settings.twilio_from_phone

    def _normalize_phone(self, phone: str) -> str:
        """Format phone with international E.164 prefix (+91 for India if omitted)."""
        clean = phone.strip()
        if not clean.startswith("+"):
            digits = "".join(filter(str.isdigit, clean))
            if len(digits) == 10:
                clean = f"+91{digits}"
            else:
                clean = f"+{digits}"
        return clean

    def send_otp(self, phone: str, otp_code: str) -> tuple[bool, str | None]:
        msg = f"Your Sulocraft verification code is: {otp_code}. Valid for 5 minutes. Do not share this code."
        return self.send_sms(phone, msg)

    def send_sms(self, phone: str, message: str) -> tuple[bool, str | None]:
        if not self.account_sid or not self.auth_token or not self.from_phone:
            return False, "Twilio credentials incomplete (ACCOUNT_SID, AUTH_TOKEN, FROM_PHONE required)"

        target_phone = self._normalize_phone(phone)
        url = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}/Messages.json"
        data = {
            "To": target_phone,
            "From": self.from_phone,
            "Body": message,
        }

        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.post(url, data=data, auth=(self.account_sid, self.auth_token))
                if resp.status_code in (200, 201):
                    logger.info("Twilio SMS sent to %s", target_phone)
                    return True, None
                body = resp.json()
                err = body.get("message", f"HTTP {resp.status_code}")
                logger.error("Twilio SMS failed to %s: %s", target_phone, err)
                return False, err
        except Exception as e:
            logger.exception("Twilio SMS request error to %s", target_phone)
            return False, str(e)
