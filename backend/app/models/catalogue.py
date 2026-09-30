"""Catalogue database models conforming to the E-commerce Multi-Agent Specification."""

from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, JSON, String, Table, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.db.base import Base

# Association table for Many-to-Many relationship between Products and Categories
product_categories = Table(
    "product_categories",
    Base.metadata,
    Column("product_id", Integer, ForeignKey("products.id", ondelete="CASCADE"), primary_key=True),
    Column("category_id", Integer, ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True),
)

# Association table for Many-to-Many relationship between Products and Tags
product_tags = Table(
    "product_tags",
    Base.metadata,
    Column("product_id", Integer, ForeignKey("products.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Category(Base):
    """Hierarchical category model supporting arbitrary parent-child depth."""

    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    parent_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True)
    description = Column(Text, nullable=True)
    image = Column(String(500), nullable=True)
    icon = Column(String(20), nullable=True)
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

    parent = relationship("Category", remote_side=[id], backref="children")
    products = relationship("Product", secondary=product_categories, back_populates="categories")


class Tag(Base):
    """Cross-cutting discovery tags (e.g. romantic, birthday, diwali, handmade)."""

    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)

    products = relationship("Product", secondary=product_tags, back_populates="tags")


class Product(Base):
    """Core product model with flexible metadata and variants."""

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

    categories = relationship("Category", secondary=product_categories, back_populates="products")
    tags = relationship("Tag", secondary=product_tags, back_populates="products")
    variants = relationship("ProductVariant", back_populates="product", cascade="all, delete-orphan")
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan", order_by="ProductImage.sort_order")
    reviews = relationship("Review", back_populates="product", cascade="all, delete-orphan")


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


class Occasion(Base):
    """Curated occasions for gift navigation (e.g. Birthday, Wedding, Diwali)."""

    __tablename__ = "occasions"

    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    icon = Column(String(20), nullable=True)
    image_url = Column(String(500), nullable=True)
