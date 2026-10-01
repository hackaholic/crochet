"""Pydantic schemas for Authentication conforming to Sections 3, 4, and 5 of Specification."""

import re
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator


def normalize_phone(phone: str) -> str:
    """Normalize phone number to 10-digit string or international +91 format."""
    digits = re.sub(r"\D", "", phone)
    if len(digits) == 10:
        return digits
    if len(digits) == 12 and digits.startswith("91"):
        return digits[2:]
    if len(digits) == 11 and digits.startswith("0"):
        return digits[1:]
    raise ValueError("Invalid phone number format. Please provide a valid 10-digit mobile number.")


class EmailStartRequest(BaseModel):
    """Payload to request an email magic link."""

    email: str = Field(..., description="Customer email address.")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        clean = v.strip().lower()
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", clean):
            raise ValueError("Invalid email format.")
        return clean


class EmailStartResponse(BaseModel):
    """Generic non-enumerating response for magic link initiation."""

    message: str = "If the email address is valid, a sign-in link has been sent."
    dev_magic_link: str | None = Field(default=None, serialization_alias="devMagicLink", description="Provided in local/test mode only.")



class SendOtpRequest(BaseModel):
    """Payload to request an SMS OTP."""

    phone: str = Field(..., description="Customer 10-digit mobile phone number.")

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        return normalize_phone(v)


class SendOtpResponse(BaseModel):
    """Response after sending OTP."""

    status: str = "ok"
    phone: str
    cooldown_seconds: int = Field(default=60, serialization_alias="cooldownSeconds")
    message: str = "OTP sent successfully"
    dev_otp: str | None = Field(default=None, serialization_alias="devOtp", description="Provided in local/test mode only.")


class VerifyOtpRequest(BaseModel):
    """Payload to verify OTP and log in."""

    phone: str = Field(..., description="Customer mobile phone number.")
    otp: str = Field(..., min_length=4, max_length=6, description="4 to 6 digit verification code.")
    name: str | None = Field(default=None, description="Optional customer name for new accounts.")

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        return normalize_phone(v)


class GoogleAuthRequest(BaseModel):
    """Payload for One-Click Google Authentication."""

    model_config = ConfigDict(populate_by_name=True)

    credential: str = Field(..., description="Google ID token credential from Google Sign-In button.")
    name: str | None = Field(default=None, description="User full name.")
    email: str | None = Field(default=None, description="User email address.")
    sub: str | None = Field(default=None, description="Google Subject / user ID.")


class FacebookAuthRequest(BaseModel):
    """Payload for Facebook (Meta) Authentication."""

    model_config = ConfigDict(populate_by_name=True)

    access_token: str = Field(..., description="Facebook user access token.", alias="accessToken")
    user_id: str | None = Field(default=None, description="Facebook user ID.", alias="userId")
    email: str | None = Field(default=None, description="Facebook user email address.")
    name: str | None = Field(default=None, description="Facebook user name.")


class UserOut(BaseModel):
    """Unified user profile representation."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    role: str = "CUSTOMER"
    status: str = "ACTIVE"
    identities: list[str] = []
    created_at: datetime | None = Field(default=None, serialization_alias="createdAt")
    last_login_at: datetime | None = Field(default=None, serialization_alias="lastLoginAt")


class AuthResponse(BaseModel):
    """Authentication success response."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    user: UserOut
    message: str = "Authentication successful"
    cart_merged: bool = Field(default=False, serialization_alias="cartMerged")
