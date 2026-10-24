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
    CartRecommendationStrategy,
    CartRecommendationsOut,
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
from app.schemas.media import (
    MediaMetadataOut,
    MediaVariantOut,
)
from app.schemas.merchant import (
    MerchantFeedItemOut,
    MerchantFeedResponse,
)

__all__ = [
    "AuthResponse",
    "CartItemAdd",
    "CartItemOut",
    "CartItemUpdate",
    "CartMergeRequest",
    "CartOut",
    "CartRecommendationStrategy",
    "CartRecommendationsOut",
    "CategoryOut",
    "EmailStartRequest",
    "EmailStartResponse",
    "FacebookAuthRequest",
    "GoogleAuthRequest",
    "MediaMetadataOut",
    "MediaVariantOut",
    "MerchantFeedItemOut",
    "MerchantFeedResponse",
    "OccasionOut",
    "ProductDetail",
    "ProductImageOut",
    "ProductListItem",
    "ProductListResponse",
    "ReviewOut",
    "UserOut",
    "VariantOut",
]
