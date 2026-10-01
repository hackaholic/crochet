"""Schemas package."""

from app.schemas.auth import (
    AuthResponse,
    EmailStartRequest,
    EmailStartResponse,
    FacebookAuthRequest,
    GoogleAuthRequest,
    UserOut,
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
    "EmailStartRequest",
    "EmailStartResponse",
    "FacebookAuthRequest",
    "GoogleAuthRequest",
    "OccasionOut",
    "ProductDetail",
    "ProductImageOut",
    "ProductListItem",
    "ProductListResponse",
    "ReviewOut",
    "UserOut",
    "VariantOut",
]
