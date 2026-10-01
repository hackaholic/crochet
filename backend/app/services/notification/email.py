"""Email delivery providers: Mock, SMTP (Universal relay), and Resend API."""

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import httpx

from app.core.config import settings
from app.services.notification.base import BaseEmailProvider

logger = logging.getLogger("sulocraft.notifications.email")


class MockEmailProvider(BaseEmailProvider):
    """Zero-credential mock email provider for automated testing and local development."""

    def __init__(self) -> None:
        self.sent_emails: list[dict] = []

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str | None = None,
        from_email: str | None = None,
    ) -> tuple[bool, str | None]:
        sender = from_email or settings.email_from_orders
        entry = {
            "from": sender,
            "to": to_email,
            "subject": subject,
            "html": html_content,
            "text": text_content or "",
            "provider": "mock",
        }
        self.sent_emails.append(entry)
        logger.info("[MockEmail] -> From: %s | To: %s | Subject: %s", sender, to_email, subject)
        return True, None

    def clear(self) -> None:
        """Clear recorded emails."""
        self.sent_emails.clear()


class SmtpEmailProvider(BaseEmailProvider):
    """Standard SMTP email provider compatible with Gmail, AWS SES, Zoho, Brevo, and SendGrid."""

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        user: str | None = None,
        password: str | None = None,
        use_tls: bool | None = None,
        from_email: str | None = None,
    ) -> None:
        self.host = host or settings.smtp_host
        self.port = port or settings.smtp_port
        self.user = user or settings.smtp_user
        self.password = password or settings.smtp_password
        self.use_tls = use_tls if use_tls is not None else settings.smtp_tls
        self.from_email = from_email or settings.email_from_orders

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str | None = None,
        from_email: str | None = None,
    ) -> tuple[bool, str | None]:
        if not self.host or not self.user or not self.password:
            return False, "SMTP configuration incomplete (HOST, USER, PASSWORD required)"

        sender = from_email or self.from_email or settings.email_from_orders
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = to_email

        if text_content:
            msg.attach(MIMEText(text_content, "plain", "utf-8"))
        msg.attach(MIMEText(html_content, "html", "utf-8"))

        try:
            if self.port == 465:
                # SSL
                with smtplib.SMTP_SSL(self.host, self.port, timeout=15.0) as server:
                    server.login(self.user, self.password)
                    server.send_message(msg)
            else:
                # STARTTLS
                with smtplib.SMTP(self.host, self.port, timeout=15.0) as server:
                    if self.use_tls:
                        server.starttls()
                    server.login(self.user, self.password)
                    server.send_message(msg)

            logger.info("SMTP email successfully sent to %s (Subject: %s)", to_email, subject)
            return True, None
        except Exception as e:
            logger.exception("SMTP email sending error to %s: %s", to_email, e)
            return False, str(e)


class ResendEmailProvider(BaseEmailProvider):
    """Developer-first transactional email API via Resend (https://resend.com)."""

    RESEND_ENDPOINT = "https://api.resend.com/emails"

    def __init__(self, api_key: str | None = None, from_email: str | None = None) -> None:
        self.api_key = api_key or settings.resend_api_key
        self.from_email = from_email or settings.email_from_orders

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str | None = None,
        from_email: str | None = None,
    ) -> tuple[bool, str | None]:
        if not self.api_key:
            return False, "Resend API key not configured"

        sender = from_email or self.from_email or settings.email_from_orders
        payload = {
            "from": sender,
            "to": [to_email],
            "subject": subject,
            "html": html_content,
        }
        if text_content:
            payload["text"] = text_content

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.post(self.RESEND_ENDPOINT, json=payload, headers=headers)
                if resp.status_code in (200, 201):
                    logger.info("Resend email successfully sent to %s", to_email)
                    return True, None
                body = resp.json()
                err = body.get("message", f"HTTP {resp.status_code}")
                logger.error("Resend email failed to %s: %s", to_email, err)
                return False, err
        except Exception as e:
            logger.exception("Resend email request error to %s", to_email)
            return False, str(e)
