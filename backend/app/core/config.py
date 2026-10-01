"""Central application settings and environment configuration."""

import os
from dataclasses import dataclass, field
from typing import List


@dataclass
class Settings:
    """Application configuration conforming to Sulocraft deployment specifications."""

    app_env: str = os.getenv("APP_ENV", "development")
    project_name: str = os.getenv("PROJECT_NAME", "Sulocraft")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./crochet.db")

    # Frontend & CORS
    frontend_url: str = os.getenv(
        "FRONTEND_URL",
        "http://localhost:8080" if os.getenv("APP_ENV", "development") == "development" else "https://sulocraft.com",
    )
    additional_cors_origins: str = os.getenv(
        "ADDITIONAL_CORS_ORIGINS",
        "https://www.sulocraft.com,http://localhost:3000,http://localhost:5173,http://localhost:8080,http://127.0.0.1:3000,http://127.0.0.1:5173,http://127.0.0.1:8080",
    )
    public_api_url: str = os.getenv(
        "PUBLIC_API_URL",
        "http://localhost:8000" if os.getenv("APP_ENV", "development") == "development" else "https://api.sulocraft.com",
    )

    # Cookies
    # In production, set COOKIE_DOMAIN to ".sulocraft.com" for cross-subdomain auth
    cookie_domain: str | None = os.getenv("COOKIE_DOMAIN") or (
        ".sulocraft.com" if os.getenv("APP_ENV") == "production" else None
    )
    cookie_secure: bool = os.getenv("COOKIE_SECURE", "false").lower() in ("true", "1", "yes") or (
        os.getenv("APP_ENV") == "production"
    )

    # Cloudflare R2 Object Storage
    r2_endpoint: str | None = os.getenv("R2_ENDPOINT")
    r2_access_key_id: str | None = os.getenv("R2_ACCESS_KEY_ID")
    r2_secret_access_key: str | None = os.getenv("R2_SECRET_ACCESS_KEY")
    r2_public_bucket: str = os.getenv("R2_PUBLIC_BUCKET", "sulocraft-products")
    r2_private_backup_bucket: str = os.getenv("R2_PRIVATE_BACKUP_BUCKET", "sulocraft-backups")
    r2_public_base_url: str = os.getenv("R2_PUBLIC_BASE_URL", "https://images.sulocraft.com")
    image_base_url: str = os.getenv(
        "IMAGE_BASE_URL",
        (
            "http://localhost:8000/static/images"
            if os.getenv("APP_ENV", "development") == "development"
            else os.getenv("R2_PUBLIC_BASE_URL", "https://images.sulocraft.com")
        ),
    )

    # Auth Providers
    google_client_id: str | None = os.getenv("GOOGLE_CLIENT_ID")
    google_client_secret: str | None = os.getenv("GOOGLE_CLIENT_SECRET")
    facebook_app_id: str | None = os.getenv("FACEBOOK_APP_ID")
    # Administrator Bootstrap (Configurable for Anupama / Production)
    admin_email: str = os.getenv("ADMIN_EMAIL", "anupama@sulocraft.com")
    admin_name: str = os.getenv("ADMIN_NAME", "Anupama Sharma")

    # SMS Notifications (Fast2SMS / Twilio / Mock for Order Updates)
    sms_provider: str = os.getenv("SMS_PROVIDER", "mock")
    fast2sms_api_key: str | None = os.getenv("FAST2SMS_API_KEY")
    fast2sms_route: str = os.getenv("FAST2SMS_ROUTE", "dlt")
    twilio_account_sid: str | None = os.getenv("TWILIO_ACCOUNT_SID")
    twilio_auth_token: str | None = os.getenv("TWILIO_AUTH_TOKEN")
    twilio_from_phone: str | None = os.getenv("TWILIO_FROM_PHONE")

    # Email Notifications (SMTP / Resend / Mock)
    email_provider: str = os.getenv("EMAIL_PROVIDER", "mock")
    email_from: str = os.getenv("EMAIL_FROM", "Sulocraft <orders@sulocraft.com>")
    smtp_host: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_user: str | None = os.getenv("SMTP_USER")
    smtp_password: str | None = os.getenv("SMTP_PASSWORD")
    smtp_tls: bool = os.getenv("SMTP_TLS", "true").lower() in ("true", "1", "yes")
    resend_api_key: str | None = os.getenv("RESEND_API_KEY")

    # Payment Provider
    payment_provider: str = os.getenv("PAYMENT_PROVIDER", "mock")

    @property
    def cors_origins(self) -> list[str]:
        """Combine primary frontend URL and additional origins into a clean unique list."""
        origins = [self.frontend_url]
        if self.additional_cors_origins:
            for o in self.additional_cors_origins.split(","):
                o_clean = o.strip()
                if o_clean and o_clean not in origins:
                    origins.append(o_clean)
        return origins


settings = Settings()
