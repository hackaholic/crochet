"""Pydantic schemas for media metadata and responsive variants."""

from pydantic import BaseModel, ConfigDict, Field


class MediaVariantOut(BaseModel):
    """Derivative or responsive media variant (e.g. mobile vs desktop, alternate formats)."""

    model_config = ConfigDict(populate_by_name=True)

    url: str
    key: str | None = None
    width: int | None = None
    height: int | None = None
    content_type: str | None = Field(default=None, serialization_alias="contentType", alias="contentType")
    descriptor: str | None = None


class MediaMetadataOut(BaseModel):
    """Rich media metadata carrying intrinsic dimensions, alt text, MIME type, and variants."""

    model_config = ConfigDict(populate_by_name=True)

    url: str
    key: str | None = None
    alt_text: str | None = Field(default=None, serialization_alias="altText", alias="altText")
    width: int | None = None
    height: int | None = None
    content_type: str | None = Field(default=None, serialization_alias="contentType", alias="contentType")
    variants: list[MediaVariantOut] = Field(default_factory=list)
