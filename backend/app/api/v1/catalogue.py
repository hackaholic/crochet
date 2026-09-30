from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from app.api.v1.auth import get_current_user
from app.db.session import get_db
from app.models.catalogue import (
    Category,
    Occasion,
    Product,
    ProductImage,
    ProductVariant,
    Review,
    Tag,
    product_categories,
)
from app.models.user import User
from app.schemas.catalogue import (
    CategoryOut,
    OccasionOut,
    ProductDetail,
    ProductImageOut,
    ProductListItem,
    ReviewOut,
    VariantOut,
)
from app.schemas.review import ReviewCreateRequest

router = APIRouter(tags=["catalogue"])


# -----------------------------------------------------------------------------
# Categories Endpoints (Section 18)
# -----------------------------------------------------------------------------

@router.get("/categories", response_model=list[CategoryOut])
def get_categories(
    flat: bool = Query(default=False, description="Return flat list instead of hierarchical tree"),
    db: Session = Depends(get_db),
) -> list[CategoryOut]:
    """Retrieve all categories. By default returns root categories with nested children."""
    if flat:
        categories = db.query(Category).order_by(Category.display_order, Category.id).all()
        return [CategoryOut.model_validate(c) for c in categories]

    # Return top-level categories with nested children
    root_categories = (
        db.query(Category)
        .filter(Category.parent_id.is_(None))
        .order_by(Category.display_order, Category.id)
        .all()
    )
    return [CategoryOut.model_validate(c) for c in root_categories]


@router.get("/categories/{slug}", response_model=CategoryOut)
def get_category_by_slug(
    slug: str,
    db: Session = Depends(get_db),
) -> CategoryOut:
    """Retrieve a single category by its slug."""
    category = db.query(Category).filter(Category.slug == slug).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category '{slug}' not found",
        )
    return CategoryOut.model_validate(category)


@router.get("/categories/{slug}/products", response_model=list[ProductListItem])
def get_category_products(
    slug: str,
    response: Response,
    sort: str = Query(default="featured"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[ProductListItem]:
    """Retrieve all products under a category (including subcategories)."""
    category = db.query(Category).filter(Category.slug == slug).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category '{slug}' not found",
        )

    # Collect category ID and any children IDs
    category_ids = [category.id] + [child.id for child in category.children]

    query = (
        db.query(Product)
        .filter(Product.status == "ACTIVE")
        .filter(Product.categories.any(Category.id.in_(category_ids)))
    )

    total_count = query.count()
    response.headers["X-Total-Count"] = str(total_count)

    products = query.offset(offset).limit(limit).all()
    return [_to_product_list_item(p) for p in products]


# -----------------------------------------------------------------------------
# Products Endpoints (Section 18)
# -----------------------------------------------------------------------------

def _to_product_list_item(p: Product) -> ProductListItem:
    """Helper to convert ORM Product to ProductListItem schema."""
    primary_category = p.categories[0].name if p.categories else "Other"
    category_names = [c.name for c in p.categories]
    tag_names = [t.name for t in p.tags]

    # Find starting price from variants or fallback
    primary_variant = p.variants[0] if p.variants else None
    price = primary_variant.price if primary_variant else 0
    compare_at_price = primary_variant.compare_at_price if primary_variant else None
    stock = sum(v.stock_quantity for v in p.variants) if p.variants else (primary_variant.stock_quantity if primary_variant else 10)

    inventory_status = "IN_STOCK" if stock > 0 else "OUT_OF_STOCK"
    in_stock = stock > 0
    gallery_urls = [img.url for img in p.images] if p.images else ([p.primary_image] if p.primary_image else [])

    return ProductListItem(
        id=p.id,
        name=p.name,
        slug=p.slug,
        price=price,
        price_paise=price * 100,
        currency="INR",
        compare_at_price=compare_at_price,
        original_price=compare_at_price,
        rating=p.rating,
        reviews=p.reviews_count,
        review_count=p.reviews_count,
        image=p.primary_image,
        image_urls=gallery_urls,
        category=primary_category,
        categories=category_names,
        badge=p.badge,
        tags=tag_names,
        description=p.short_description or p.description,
        customizable=p.customizable,
        in_stock=in_stock,
        inventory_status=inventory_status,
    )


@router.get("/products", response_model=list[ProductListItem])
def list_products(
    response: Response,
    category: str | None = Query(default=None, description="Filter by category slug or name"),
    tag: str | None = Query(default=None, description="Filter by tag name (e.g. romantic, birthday)"),
    occasion: str | None = Query(default=None, description="Alias for occasion/tag filtering"),
    color: str | None = Query(default=None, description="Filter by color attribute in variants"),
    customizable: bool | None = Query(default=None, description="Filter customizable products"),
    min_price: int | None = Query(default=None, ge=0, description="Minimum price in INR"),
    max_price: int | None = Query(default=None, ge=0, description="Maximum price in INR"),
    search: str | None = Query(default=None, description="Search keyword in name or description"),
    badge: str | None = Query(default=None, description="Filter by badge (e.g. Bestseller, New, Limited)"),
    sort: str = Query(default="featured", description="Sorting: featured, price_asc, price_desc, rating, newest, best_selling"),
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(default=50, ge=1, le=100, description="Items per page"),
    offset: int | None = Query(default=None, ge=0, description="Manual offset; overrides page if provided"),
    db: Session = Depends(get_db),
) -> list[ProductListItem]:
    """Search and filter the product catalogue with pagination and sorting."""
    query = (
        db.query(Product)
        .options(
            joinedload(Product.categories),
            joinedload(Product.tags),
            joinedload(Product.variants),
            joinedload(Product.images),
        )
        .filter(Product.status == "ACTIVE")
    )

    # Category filter
    if category and category.lower() != "all":
        query = query.filter(
            Product.categories.any(
                or_(
                    Category.slug.ilike(category),
                    Category.name.ilike(category),
                )
            )
        )

    # Tag / Occasion filter
    target_tag = tag or occasion
    if target_tag:
        query = query.filter(Product.tags.any(Tag.name.ilike(target_tag)))

    # Color filter
    if color:
        query = query.filter(
            Product.variants.any(
                or_(
                    ProductVariant.name.ilike(f"%{color}%"),
                    ProductVariant.sku.ilike(f"%{color}%"),
                )
            )
        )

    # Customizable filter
    if customizable is not None:
        query = query.filter(Product.customizable == customizable)

    # Badge filter
    if badge:
        query = query.filter(Product.badge.ilike(badge))

    # Search filter
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Product.name.ilike(search_pattern),
                Product.description.ilike(search_pattern),
                Product.short_description.ilike(search_pattern),
            )
        )

    # Price range filters (checked via variants)
    if min_price is not None:
        query = query.filter(Product.variants.any(ProductVariant.price >= min_price))
    if max_price is not None:
        query = query.filter(Product.variants.any(ProductVariant.price <= max_price))

    # Sorting
    if sort == "price_asc":
        min_price_sub = (
            db.query(func.min(ProductVariant.price))
            .filter(ProductVariant.product_id == Product.id)
            .correlate(Product)
            .scalar_subquery()
        )
        query = query.order_by(min_price_sub.asc())
    elif sort == "price_desc":
        max_price_sub = (
            db.query(func.max(ProductVariant.price))
            .filter(ProductVariant.product_id == Product.id)
            .correlate(Product)
            .scalar_subquery()
        )
        query = query.order_by(max_price_sub.desc())
    elif sort == "rating":
        query = query.order_by(Product.rating.desc(), Product.reviews_count.desc())
    elif sort in ("newest", "new"):
        query = query.order_by(Product.id.desc())
    elif sort in ("best_selling", "popular"):
        query = query.order_by(Product.reviews_count.desc())
    else:
        query = query.order_by(Product.id.asc())

    total_count = query.order_by(None).count()
    response.headers["X-Total-Count"] = str(total_count)

    calc_offset = offset if offset is not None else (page - 1) * limit
    products = query.offset(calc_offset).limit(limit).all()

    return [_to_product_list_item(p) for p in products]


@router.get("/products/search", response_model=list[ProductListItem])
def search_products(
    q: str = Query(..., min_length=1, description="Search keyword"),
    limit: int = Query(default=20, ge=1, le=50),
    db: Session = Depends(get_db),
) -> list[ProductListItem]:
    """Search products across name, description, tags, and category names."""
    pattern = f"%{q}%"
    products = (
        db.query(Product)
        .options(
            joinedload(Product.categories),
            joinedload(Product.tags),
            joinedload(Product.variants),
            joinedload(Product.images),
        )
        .filter(
            Product.status == "ACTIVE",
            or_(
                Product.name.ilike(pattern),
                Product.description.ilike(pattern),
                Product.tags.any(Tag.name.ilike(pattern)),
                Product.categories.any(Category.name.ilike(pattern)),
            ),
        )
        .order_by(Product.reviews_count.desc())
        .limit(limit)
        .all()
    )
    return [_to_product_list_item(p) for p in products]


@router.get("/products/{slug_or_id}", response_model=ProductDetail)
def get_product_detail(
    slug_or_id: str,
    db: Session = Depends(get_db),
) -> ProductDetail:
    """Retrieve full product details conforming to Section 2 of Specification."""
    query = (
        db.query(Product)
        .options(
            joinedload(Product.categories),
            joinedload(Product.tags),
            joinedload(Product.variants),
            joinedload(Product.images),
            joinedload(Product.reviews),
        )
    )

    if slug_or_id.isdigit():
        product = query.filter(Product.id == int(slug_or_id)).first()
    else:
        product = query.filter(Product.slug == slug_or_id).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product '{slug_or_id}' not found",
        )

    primary_category = product.categories[0].name if product.categories else "Other"
    category_names = [c.name for c in product.categories]
    tag_names = [t.name for t in product.tags]

    image_urls = [img.url for img in product.images]
    if not image_urls and product.primary_image:
        image_urls = [product.primary_image]

    gallery = [
        ProductImageOut(
            id=img.id,
            url=img.url,
            alt_text=img.alt_text,
            sort_order=img.sort_order,
            is_primary=img.is_primary,
            variant_id=img.variant_id,
        )
        for img in product.images
    ]

    variants = [
        VariantOut(
            id=v.id,
            product_id=v.product_id,
            sku=v.sku,
            name=v.name,
            price=v.price,
            price_paise=v.price * 100,
            currency="INR",
            compare_at_price=v.compare_at_price,
            stock_quantity=v.stock_quantity,
            weight=v.weight,
            status=v.status,
            attributes=v.attributes_json or {},
        )
        for v in product.variants
    ]

    primary_variant = product.variants[0] if product.variants else None
    price = primary_variant.price if primary_variant else 0
    compare_at_price = primary_variant.compare_at_price if primary_variant else None
    stock = primary_variant.stock_quantity if primary_variant else 10

    inventory_status = "IN_STOCK" if stock > 0 else "OUT_OF_STOCK"

    customer_reviews = [
        ReviewOut(
            id=r.id,
            product_id=r.product_id,
            product_name=r.product_name,
            name=r.author_name,
            location=r.location,
            rating=r.rating,
            text=r.text,
            image=r.avatar_url,
            date=r.date,
        )
        for r in product.reviews
    ]

    return ProductDetail(
        id=product.id,
        name=product.name,
        slug=product.slug,
        short_description=product.short_description,
        description=product.description,
        category=primary_category,
        categories=category_names,
        tags=tag_names,
        images=image_urls,
        image_urls=image_urls,
        gallery=gallery,
        variants=variants,
        price=price,
        price_paise=price * 100,
        currency="INR",
        compare_at_price=compare_at_price,
        original_price=compare_at_price,
        rating=product.rating,
        reviews=product.reviews_count,
        review_count=product.reviews_count,
        in_stock=stock > 0,
        inventory_status=inventory_status,
        badge=product.badge,
        brand=product.brand,
        customizable=product.customizable,
        attributes=product.metadata_json or {},
        customer_reviews=customer_reviews,
    )


# -----------------------------------------------------------------------------
# Additional Supporting Endpoints (Occasions & Reviews)
# -----------------------------------------------------------------------------

@router.get("/occasions", response_model=list[OccasionOut])
def get_occasions(db: Session = Depends(get_db)) -> list[OccasionOut]:
    """Retrieve curated gift occasions."""
    return db.query(Occasion).all()


@router.get("/reviews", response_model=list[ReviewOut])
def get_reviews(
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
) -> list[ReviewOut]:
    """Retrieve customer testimonials and reviews for homepage and storefront."""
    return db.query(Review).order_by(Review.id).limit(limit).all()


@router.post("/products/{slug_or_id}/reviews", response_model=ReviewOut, status_code=status.HTTP_201_CREATED)
def submit_product_review(
    slug_or_id: str,
    payload: ReviewCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ReviewOut:
    """Submit a verified customer review for a product and recalculate product ratings."""
    query = db.query(Product)
    if slug_or_id.isdigit():
        product = query.filter((Product.id == int(slug_or_id)) | (Product.slug == slug_or_id)).first()
    else:
        product = query.filter(Product.slug == slug_or_id).first()

    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    author_name = payload.author_name or current_user.name or "Verified Customer"
    date_str = datetime.now(timezone.utc).strftime("%b %Y")

    review = Review(
        product_id=product.id,
        product_name=product.name,
        author_name=author_name,
        location=payload.location or "India",
        rating=payload.rating,
        text=payload.text,
        avatar_url=None,
        date=date_str,
    )
    db.add(review)
    db.flush()

    # Recalculate product aggregate rating and reviews count
    all_reviews = db.query(Review).filter(Review.product_id == product.id).all()
    if all_reviews:
        product.rating = round(sum(r.rating for r in all_reviews) / len(all_reviews), 1)
    product.reviews_count = (product.reviews_count or 0) + 1

    db.commit()
    db.refresh(review)
    return review
