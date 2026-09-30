"""Schemas package."""

from app.schemas.auth import (
    AuthResponse,
    GoogleAuthRequest,
    SendOtpRequest,
    SendOtpResponse,
    UserOut,
    VerifyOtpRequest,
)
from app.schemas.cart import (
    CartItemAdd,
    CartItemOut,
    CartItemUpdate,
    CartMergeRequest,
    CartOut,
)
from app.schemas.catalogue import (
    CategoryOut,
    OccasionOut,
    ProductDetail,
    ProductImageOut,
    ProductListItem,
    ProductListResponse,
    ReviewOut,
    VariantOut,
)

__all__ = [
    "AuthResponse",
    "CartItemAdd",
    "CartItemOut",
    "CartItemUpdate",
    "CartMergeRequest",
    "CartOut",
    "CategoryOut",
    "GoogleAuthRequest",
    "OccasionOut",
    "ProductDetail",
    "ProductImageOut",
    "ProductListItem",
    "ProductListResponse",
    "ReviewOut",
    "SendOtpRequest",
    "SendOtpResponse",
    "UserOut",
    "VariantOut",
    "VerifyOtpRequest",
]
