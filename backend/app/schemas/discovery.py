"""Discovery API schemas conforming to Task 7.6 of Specification."""

from typing import Literal
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.catalogue import ProductListItem

DiscoveryStrategy = Literal["related", "newest", "featured", "trending", "popular"]


class DiscoverySectionOut(BaseModel):
    """A ranked storefront discovery section with associated products."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    title: str
    strategy: DiscoveryStrategy
    products: list[ProductListItem]


class DiscoveryResponse(BaseModel):
    """Storefront discovery response containing ranked sections and pagination cursor."""

    model_config = ConfigDict(populate_by_name=True)

    sections: list[DiscoverySectionOut]
    next_cursor: str | None = Field(
        default=None, serialization_alias="nextCursor", alias="nextCursor"
    )
