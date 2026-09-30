"""Pydantic schemas for Customer Reviews."""

from pydantic import BaseModel, ConfigDict, Field


class ReviewCreateRequest(BaseModel):
    """Payload for customer review submission."""

    model_config = ConfigDict(populate_by_name=True)

    rating: int = Field(..., ge=1, le=5, description="Star rating from 1 to 5")
    text: str = Field(..., min_length=3, max_length=2000, description="Review text or customer feedback")
    author_name: str | None = Field(default=None, alias="authorName", description="Customer display name")
    location: str | None = Field(default=None, description="City / Region, e.g. 'Bengaluru'")


class AdminReviewOut(BaseModel):
    """Review representation for admin moderation."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    product_id: int | None = Field(default=None, alias="productId")
    product_name: str | None = Field(default=None, alias="productName")
    product_slug: str | None = Field(default=None, alias="productSlug")
    author_name: str = Field(alias="authorName")
    location: str | None = None
    rating: int
    text: str
    avatar_url: str | None = Field(default=None, alias="avatarUrl")
    date: str | None = None
