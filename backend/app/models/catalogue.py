"""Catalogue database models conforming to the E-commerce Multi-Agent Specification."""

from datetime import datetime, timedelta, timezone
try:
    from zoneinfo import ZoneInfo
    IST = ZoneInfo("Asia/Kolkata")
except Exception:
    IST = timezone(timedelta(hours=5, minutes=30))

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, JSON, String, Table, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.core.images import build_image_url
from app.db.base import Base


# Association table for Many-to-Many relationship between Products and Tags
product_tags = Table(
    "product_tags",
    Base.metadata,
    Column("product_id", Integer, ForeignKey("products.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class ProductCategory(Base):
    """Explicit association model between Products and Categories with primary designation."""

    __tablename__ = "product_categories"

    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), primary_key=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True)
    is_primary = Column(Boolean, default=False, nullable=False, index=True)
    display_order = Column(Integer, default=0, nullable=False)

    product = relationship("Product", back_populates="product_categories", overlaps="products,categories")
    category = relationship("Category", back_populates="category_products", overlaps="products,categories")


# Retain table alias for backward compatibility with existing raw queries
product_categories = ProductCategory.__table__


class Category(Base):
    """Hierarchical category model supporting arbitrary parent-child depth and cycle prevention."""

    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    parent_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True)
    description = Column(Text, nullable=True)
    image = Column(String(500), nullable=True)
    image_key = Column(String(500), nullable=True)
    icon = Column(String(20), nullable=True)
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    show_when_empty = Column(Boolean, default=False, nullable=False)
    seo_title = Column(String(255), nullable=True)
    seo_description = Column(Text, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    parent = relationship("Category", remote_side=[id], backref="children")
    category_products = relationship("ProductCategory", back_populates="category", cascade="all, delete-orphan", overlaps="products,categories")
    products = relationship(
        "Product",
        secondary="product_categories",
        back_populates="categories",
        overlaps="category_products,category,product_categories,product",
    )

    @property
    def image_url(self) -> str | None:
        """Resolve full image URL from image_key or legacy image."""
        raw = self.image_key or getattr(self, "image", None)
        return build_image_url(raw) if raw else None

    def would_create_cycle(self, potential_parent_id: int | None) -> bool:
        """Check if assigning potential_parent_id as parent would create a cycle in the hierarchy."""
        if potential_parent_id is None:
            return False
        if potential_parent_id == self.id:
            return True
        visited = set()
        queue = [self]
        while queue:
            node = queue.pop(0)
            if node.id in visited:
                continue
            visited.add(node.id)
            if node.id == potential_parent_id:
                return True
            for child in getattr(node, "children", []):
                queue.append(child)
        return False


class Collection(Base):
    """Curated merchandising collections (occasions, gifts, campaigns, best sellers)."""

    __tablename__ = "collections"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    image_key = Column(String(500), nullable=True)
    collection_type = Column(String(50), default="MERCHANDISING", nullable=False, index=True)
    display_order = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    starts_at = Column(DateTime, nullable=True)
    ends_at = Column(DateTime, nullable=True)
    seo_title = Column(String(255), nullable=True)
    seo_description = Column(Text, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    product_associations = relationship("ProductCollection", back_populates="collection", cascade="all, delete-orphan", overlaps="products,collections")
    products = relationship(
        "Product",
        secondary="product_collections",
        back_populates="collections",
        overlaps="product_associations,collection,product_collections,product",
    )

    @property
    def image_url(self) -> str | None:
        """Resolve full image URL from image_key."""
        return build_image_url(self.image_key) if self.image_key else None


class ProductCollection(Base):
    """Association model between Products and Collections."""

    __tablename__ = "product_collections"

    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), primary_key=True)
    collection_id = Column(Integer, ForeignKey("collections.id", ondelete="CASCADE"), primary_key=True)
    display_order = Column(Integer, default=0, nullable=False)

    product = relationship("Product", back_populates="product_collections", overlaps="products,collections")
    collection = relationship("Collection", back_populates="product_associations", overlaps="products,collections")


product_collections = ProductCollection.__table__


class ProductOccasion(Base):
    """Association model between Products and Curated Occasions."""

    __tablename__ = "product_occasions"

    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), primary_key=True)
    occasion_id = Column(String(50), ForeignKey("occasions.id", ondelete="CASCADE"), primary_key=True)
    display_order = Column(Integer, default=0, nullable=False)

    product = relationship("Product", back_populates="product_occasions", overlaps="occasions,products")
    occasion = relationship("Occasion", back_populates="product_associations", overlaps="occasions,products")


product_occasions = ProductOccasion.__table__


class Tag(Base):
    """Cross-cutting discovery tags (e.g. romantic, birthday, diwali, handmade)."""

    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)

    products = relationship("Product", secondary=product_tags, back_populates="tags")


class Product(Base):
    """Core product model with flexible metadata, categories, collections, and variants."""

    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    slug = Column(String(200), unique=True, index=True, nullable=False)
    short_description = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    status = Column(String(20), default="ACTIVE", index=True)  # DRAFT, ACTIVE, ARCHIVED
    brand = Column(String(100), default="Sulocraft")
    primary_image = Column(String(500), nullable=False)
    badge = Column(String(50), nullable=True)  # Bestseller, New, Limited, Handmade
    customizable = Column(Boolean, default=False)
    rating = Column(Float, default=5.0)
    reviews_count = Column(Integer, default=0)
    metadata_json = Column(JSON().with_variant(JSONB, "postgresql"), default=dict)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    published_at = Column(DateTime, nullable=True)

    product_categories = relationship(
        "ProductCategory",
        back_populates="product",
        cascade="all, delete-orphan",
        order_by="ProductCategory.display_order",
        overlaps="categories,products",
    )
    categories = relationship(
        "Category",
        secondary="product_categories",
        back_populates="products",
        overlaps="product_categories,category,category_products,product",
    )
    product_collections = relationship(
        "ProductCollection",
        back_populates="product",
        cascade="all, delete-orphan",
        order_by="ProductCollection.display_order",
        overlaps="collections,products",
    )
    collections = relationship(
        "Collection",
        secondary="product_collections",
        back_populates="products",
        overlaps="product_collections,collection,product_associations,product",
    )
    product_occasions = relationship(
        "ProductOccasion",
        back_populates="product",
        cascade="all, delete-orphan",
        order_by="ProductOccasion.display_order",
        overlaps="occasions,products",
    )
    occasions = relationship(
        "Occasion",
        secondary="product_occasions",
        back_populates="products",
        order_by="ProductOccasion.display_order",
        overlaps="product_occasions,occasion,product_associations,product",
    )
    tags = relationship("Tag", secondary=product_tags, back_populates="products")
    variants = relationship("ProductVariant", back_populates="product", cascade="all, delete-orphan")
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan", order_by="ProductImage.sort_order")
    reviews = relationship("Review", back_populates="product", cascade="all, delete-orphan")

    @property
    def primary_category(self) -> Category | None:
        """Resolve the primary Category for this product."""
        for pc in self.product_categories:
            if pc.is_primary:
                return pc.category
        if self.categories:
            return self.categories[0]
        return None


class ProductVariant(Base):
    """Sellable product variant carrying unique SKU, price, stock, and attributes."""

    __tablename__ = "product_variants"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    sku = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(150), default="Default")
    price = Column(Integer, nullable=False)  # In INR
    compare_at_price = Column(Integer, nullable=True)
    cost = Column(Integer, nullable=True)
    stock_quantity = Column(Integer, default=10)
    weight = Column(Float, nullable=True)  # Grams
    status = Column(String(20), default="ACTIVE")
    attributes_json = Column(JSON().with_variant(JSONB, "postgresql"), default=dict)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    product = relationship("Product", back_populates="variants")
    images = relationship("ProductImage", back_populates="variant")


class ProductImage(Base):
    """Supplementary and variant-specific product images."""

    __tablename__ = "product_images"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    variant_id = Column(Integer, ForeignKey("product_variants.id", ondelete="SET NULL"), nullable=True, index=True)
    url = Column(String(500), nullable=False)
    alt_text = Column(String(255), nullable=True)
    sort_order = Column(Integer, default=0)
    is_primary = Column(Boolean, default=False)

    product = relationship("Product", back_populates="images")
    variant = relationship("ProductVariant", back_populates="images")


class Review(Base):
    """Product reviews and customer testimonials."""

    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="SET NULL"), nullable=True, index=True)
    product_name = Column(String(200), nullable=True)
    author_name = Column(String(100), nullable=False)
    location = Column(String(100), nullable=True)
    rating = Column(Integer, default=5)
    text = Column(Text, nullable=False)
    avatar_url = Column(String(500), nullable=True)
    date = Column(String(50), nullable=True)

    product = relationship("Product", back_populates="reviews")


EVERGREEN_OCCASION_IDS = frozenset({"birthday", "anniversary", "wedding", "babyshower"})


class Occasion(Base):
    """Curated occasions for gift navigation (e.g. Birthday, Wedding, Diwali)."""

    __tablename__ = "occasions"

    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    icon = Column(String(20), nullable=True)
    image_key = Column(String(255), nullable=True)
    _legacy_image_url = Column("image_url", String(500), nullable=True)
    description = Column(Text, nullable=True)
    display_order = Column(Integer, default=0, nullable=False)
    is_enabled = Column(Boolean, default=True, nullable=False)
    starts_at = Column(DateTime, nullable=True)
    ends_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    product_associations = relationship(
        "ProductOccasion",
        back_populates="occasion",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="ProductOccasion.display_order",
        overlaps="products,occasions",
    )
    products = relationship(
        "Product",
        secondary="product_occasions",
        back_populates="occasions",
        order_by="ProductOccasion.display_order",
        overlaps="product_associations,product,product_occasions,occasion",
    )

    @property
    def is_evergreen(self) -> bool:
        """Core evergreen occasions remain visible year-round and ignore seasonal schedules."""
        return self.id in EVERGREEN_OCCASION_IDS

    @property
    def image_url(self) -> str | None:
        """Resolve public CDN image URL from image_key or legacy image_url."""
        if self.image_key:
            return build_image_url(self.image_key)
        return self._legacy_image_url

    @image_url.setter
    def image_url(self, value: str | None) -> None:
        self._legacy_image_url = value
        if value and not value.startswith("http"):
            self.image_key = value

    def is_in_season(self, current_time: datetime | None = None) -> bool:
        """Evaluate whether this occasion's schedule window includes current time in Asia/Kolkata."""
        if self.is_evergreen:
            return True

        if not self.is_enabled:
            return False

        if self.starts_at is None and self.ends_at is None:
            return True

        now_ist = current_time or datetime.now(IST)
        if now_ist.tzinfo is None:
            now_ist = now_ist.replace(tzinfo=IST)

        if self.starts_at is not None:
            s = self.starts_at
            if s.tzinfo is None:
                s = s.replace(tzinfo=IST)
            if now_ist < s:
                return False

        if self.ends_at is not None:
            e = self.ends_at
            if e.tzinfo is None:
                e = e.replace(tzinfo=IST)
            if now_ist > e:
                return False

        return True
