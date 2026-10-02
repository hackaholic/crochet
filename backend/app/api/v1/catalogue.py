from collections import defaultdict
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from app.api.v1.auth import get_current_user
from app.db.session import get_db
from app.models.catalogue import (
    Category,
    Collection,
    Occasion,
    Product,
    ProductCollection,
    ProductImage,
    ProductVariant,
    Review,
    Tag,
    product_categories,
)
from app.models.user import User
from app.schemas.catalogue import (
    CategoryOut,
    CategorySummary,
    CollectionOut,
    CollectionSummary,
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
# Categories Endpoints (Section 18 & Taxonomy Contract)
# -----------------------------------------------------------------------------

def _collect_descendant_category_ids(category: Category, all_cats: list[Category]) -> set[int]:
    """Helper to collect IDs of category and all its descendants recursively."""
    descendants = {category.id}
    children = [c for c in all_cats if c.parent_id == category.id]
    for child in children:
        descendants.update(_collect_descendant_category_ids(child, all_cats))
    return descendants


@router.get("/categories", response_model=list[CategoryOut])
def get_categories(
    flat: bool = Query(default=False, description="Return flat list instead of hierarchical tree"),
    include_empty: bool = Query(default=False, alias="includeEmpty", description="Include empty categories"),
    db: Session = Depends(get_db),
) -> list[CategoryOut]:
    """Retrieve all categories conforming to product-taxonomy spec."""
    all_categories = (
        db.query(Category)
        .order_by(Category.display_order, Category.id)
        .all()
    )

    # Filter out categories with inactive ancestors
    cat_by_id = {c.id: c for c in all_categories}

    def is_ancestry_active(c: Category) -> bool:
        curr: Category | None = c
        while curr:
            if not curr.is_active:
                return False
            curr = cat_by_id.get(curr.parent_id) if curr.parent_id else None
        return True

    active_categories = [c for c in all_categories if is_ancestry_active(c)]

    # Precompute product counts per category (active products only)
    active_prod_cats = (
        db.query(product_categories.c.product_id, product_categories.c.category_id)
        .join(Product, Product.id == product_categories.c.product_id)
        .filter(Product.status == "ACTIVE")
        .all()
    )
    direct_pids = defaultdict(set)
    for pid, cid in active_prod_cats:
        direct_pids[cid].add(pid)

    # Compute descendant product count for each active category
    product_counts: dict[int, int] = {}
    for cat in active_categories:
        desc_ids = _collect_descendant_category_ids(cat, active_categories)
        pids = set().union(*(direct_pids[cid] for cid in desc_ids if cid in direct_pids)) if desc_ids else set()
        product_counts[cat.id] = len(pids)

    # Filter based on empty/show_when_empty
    def should_include(c: Category) -> bool:
        if include_empty:
            return True
        if product_counts.get(c.id, 0) > 0 or c.show_when_empty:
            return True
        desc_ids = _collect_descendant_category_ids(c, active_categories) - {c.id}
        for desc_id in desc_ids:
            desc_cat = cat_by_id.get(desc_id)
            if desc_cat and (product_counts.get(desc_id, 0) > 0 or desc_cat.show_when_empty):
                return True
        return False

    filtered_categories = [c for c in active_categories if should_include(c)]
    filtered_ids = {c.id for c in filtered_categories}

    if flat:
        result = []
        for c in filtered_categories:
            c_dict = {
                "id": c.id,
                "name": c.name,
                "slug": c.slug,
                "parentId": c.parent_id,
                "description": c.description,
                "imageUrl": c.image_url,
                "icon": c.icon,
                "displayOrder": c.display_order,
                "isActive": c.is_active,
                "showWhenEmpty": c.show_when_empty,
                "productCount": product_counts.get(c.id, 0),
                "children": [],
            }
            result.append(CategoryOut.model_validate(c_dict))
        return result

    # Hierarchical tree construction
    def build_node(c: Category) -> CategoryOut:
        children = [
            build_node(child)
            for child in active_categories
            if child.parent_id == c.id and child.id in filtered_ids
        ]
        return CategoryOut.model_validate({
            "id": c.id,
            "name": c.name,
            "slug": c.slug,
            "parentId": c.parent_id,
            "description": c.description,
            "imageUrl": c.image_url,
            "icon": c.icon,
            "displayOrder": c.display_order,
            "isActive": c.is_active,
            "showWhenEmpty": c.show_when_empty,
            "productCount": product_counts.get(c.id, 0),
            "children": children,
        })

    roots = [c for c in filtered_categories if c.parent_id is None or c.parent_id not in filtered_ids]
    return [build_node(r) for r in roots]


@router.get("/categories/{slug}", response_model=CategoryOut)
def get_category_by_slug(
    slug: str,
    db: Session = Depends(get_db),
) -> CategoryOut:
    """Retrieve a single category by its slug with accurate descendant product count."""
    category = db.query(Category).filter(Category.slug == slug, Category.is_active.is_(True)).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category '{slug}' not found",
        )

    all_categories = db.query(Category).filter(Category.is_active.is_(True)).all()
    desc_ids = _collect_descendant_category_ids(category, all_categories)

    active_pids = (
        db.query(Product.id)
        .join(product_categories, product_categories.c.product_id == Product.id)
        .filter(Product.status == "ACTIVE", product_categories.c.category_id.in_(desc_ids))
        .distinct()
        .count()
    )

    children_out = []
    for ch in category.children:
        if ch.is_active:
            ch_desc = _collect_descendant_category_ids(ch, all_categories)
            ch_pids = (
                db.query(Product.id)
                .join(product_categories, product_categories.c.product_id == Product.id)
                .filter(Product.status == "ACTIVE", product_categories.c.category_id.in_(ch_desc))
                .distinct()
                .count()
            )
            children_out.append(
                CategoryOut.model_validate({
                    "id": ch.id,
                    "name": ch.name,
                    "slug": ch.slug,
                    "parentId": ch.parent_id,
                    "description": ch.description,
                    "imageUrl": ch.image_url,
                    "icon": ch.icon,
                    "displayOrder": ch.display_order,
                    "isActive": ch.is_active,
                    "showWhenEmpty": ch.show_when_empty,
                    "productCount": ch_pids,
                    "children": [],
                })
            )

    return CategoryOut.model_validate({
        "id": category.id,
        "name": category.name,
        "slug": category.slug,
        "parentId": category.parent_id,
        "description": category.description,
        "imageUrl": category.image_url,
        "icon": category.icon,
        "displayOrder": category.display_order,
        "isActive": category.is_active,
        "showWhenEmpty": category.show_when_empty,
        "productCount": active_pids,
        "children": children_out,
    })


def _to_product_list_item(p: Product) -> ProductListItem:
    """Helper to convert ORM Product to ProductListItem schema."""
    prim_cat = p.primary_category
    primary_category_name = prim_cat.name if prim_cat else (p.categories[0].name if p.categories else "Other")
    primary_cat_summary = (
        CategorySummary(id=prim_cat.id, name=prim_cat.name, slug=prim_cat.slug)
        if prim_cat
        else None
    )
    categories_summary = [
        CategorySummary(id=c.id, name=c.name, slug=c.slug) for c in p.categories
    ]
    collections_summary = [
        CollectionSummary(id=col.id, name=col.name, slug=col.slug) for col in p.collections
    ]
    occ_ids = [occ.id for occ in p.occasions]
    occ_names = [occ.name for occ in p.occasions]
    tag_names = list(dict.fromkeys([t.name for t in p.tags] + occ_ids + occ_names))

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
        category=primary_category_name,
        primary_category=primary_cat_summary,
        categories=categories_summary,
        collections=collections_summary,
        badge=p.badge,
        tags=tag_names,
        occasions=occ_ids,
        description=p.short_description or p.description,
        customizable=p.customizable,
        in_stock=in_stock,
        inventory_status=inventory_status,
    )


@router.get("/categories/{slug}/products", response_model=list[ProductListItem])
def get_category_products(
    slug: str,
    response: Response,
    sort: str = Query(default="featured"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[ProductListItem]:
    """Retrieve all products under a category (including subcategories) deduplicated."""
    category = db.query(Category).filter(Category.slug == slug).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category '{slug}' not found",
        )

    all_categories = db.query(Category).all()
    category_ids = list(_collect_descendant_category_ids(category, all_categories))

    query = (
        db.query(Product)
        .options(
            joinedload(Product.product_categories),
            joinedload(Product.categories),
            joinedload(Product.product_collections),
            joinedload(Product.collections),
            joinedload(Product.tags),
            joinedload(Product.variants),
            joinedload(Product.images),
        )
        .filter(Product.status == "ACTIVE")
        .filter(Product.categories.any(Category.id.in_(category_ids)))
        .distinct()
    )

    total_count = query.count()
    response.headers["X-Total-Count"] = str(total_count)

    products = query.offset(offset).limit(limit).all()
    return [_to_product_list_item(p) for p in products]


# -----------------------------------------------------------------------------
# Collections Endpoints (Section 18 & Taxonomy Contract)
# -----------------------------------------------------------------------------

@router.get("/collections", response_model=list[CollectionOut])
def get_collections(
    db: Session = Depends(get_db),
) -> list[CollectionOut]:
    """Retrieve active and currently scheduled collections ordered by display_order."""
    now = datetime.now(timezone.utc)
    collections = (
        db.query(Collection)
        .filter(
            Collection.is_active.is_(True),
            or_(Collection.starts_at.is_(None), Collection.starts_at <= now),
            or_(Collection.ends_at.is_(None), Collection.ends_at >= now),
        )
        .order_by(Collection.display_order, Collection.id)
        .all()
    )

    col_ids = [c.id for c in collections]
    counts_query = (
        db.query(ProductCollection.collection_id, func.count(Product.id.distinct()))
        .join(Product, Product.id == ProductCollection.product_id)
        .filter(Product.status == "ACTIVE", ProductCollection.collection_id.in_(col_ids))
        .group_by(ProductCollection.collection_id)
        .all()
    )
    counts_map = dict(counts_query)

    result = []
    for col in collections:
        c_dict = {
            "id": col.id,
            "name": col.name,
            "slug": col.slug,
            "description": col.description,
            "imageUrl": col.image_url,
            "collectionType": col.collection_type,
            "displayOrder": col.display_order,
            "isActive": col.is_active,
            "startsAt": col.starts_at,
            "endsAt": col.ends_at,
            "productCount": counts_map.get(col.id, 0),
        }
        result.append(CollectionOut.model_validate(c_dict))
    return result


@router.get("/collections/{slug}", response_model=CollectionOut)
def get_collection_by_slug(
    slug: str,
    db: Session = Depends(get_db),
) -> CollectionOut:
    """Retrieve a single active scheduled collection by slug."""
    now = datetime.now(timezone.utc)
    col = (
        db.query(Collection)
        .filter(
            Collection.slug == slug,
            Collection.is_active.is_(True),
            or_(Collection.starts_at.is_(None), Collection.starts_at <= now),
            or_(Collection.ends_at.is_(None), Collection.ends_at >= now),
        )
        .first()
    )
    if not col:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Collection '{slug}' not found",
        )

    product_count = (
        db.query(Product.id)
        .join(ProductCollection, ProductCollection.product_id == Product.id)
        .filter(Product.status == "ACTIVE", ProductCollection.collection_id == col.id)
        .distinct()
        .count()
    )

    return CollectionOut.model_validate({
        "id": col.id,
        "name": col.name,
        "slug": col.slug,
        "description": col.description,
        "imageUrl": col.image_url,
        "collectionType": col.collection_type,
        "displayOrder": col.display_order,
        "isActive": col.is_active,
        "startsAt": col.starts_at,
        "endsAt": col.ends_at,
        "productCount": product_count,
    })


@router.get("/collections/{slug}/products", response_model=list[ProductListItem])
def get_collection_products(
    slug: str,
    response: Response,
    sort: str = Query(default="featured"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[ProductListItem]:
    """Retrieve all active products in a collection ordered by assignment display_order."""
    now = datetime.now(timezone.utc)
    col = (
        db.query(Collection)
        .filter(
            Collection.slug == slug,
            Collection.is_active.is_(True),
            or_(Collection.starts_at.is_(None), Collection.starts_at <= now),
            or_(Collection.ends_at.is_(None), Collection.ends_at >= now),
        )
        .first()
    )
    if not col:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Collection '{slug}' not found",
        )

    query = (
        db.query(Product)
        .join(ProductCollection, ProductCollection.product_id == Product.id)
        .options(
            joinedload(Product.product_categories),
            joinedload(Product.categories),
            joinedload(Product.product_collections),
            joinedload(Product.collections),
            joinedload(Product.tags),
            joinedload(Product.variants),
            joinedload(Product.images),
        )
        .filter(Product.status == "ACTIVE", ProductCollection.collection_id == col.id)
        .order_by(ProductCollection.display_order, Product.id)
        .distinct()
    )

    total_count = query.count()
    response.headers["X-Total-Count"] = str(total_count)

    products = query.offset(offset).limit(limit).all()
    return [_to_product_list_item(p) for p in products]





@router.get("/products", response_model=list[ProductListItem])
def list_products(
    response: Response,
    category: str | None = Query(default=None, description="Filter by category slug or name"),
    collection: str | None = Query(default=None, description="Filter by collection slug or name"),
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
            joinedload(Product.product_categories),
            joinedload(Product.categories),
            joinedload(Product.product_collections),
            joinedload(Product.collections),
            joinedload(Product.tags),
            joinedload(Product.variants),
            joinedload(Product.images),
        )
        .filter(Product.status == "ACTIVE")
    )

    # Category filter
    if category and category.lower() != "all":
        target_cat = (
            db.query(Category)
            .filter(or_(Category.slug.ilike(category), Category.name.ilike(category)))
            .first()
        )
        if target_cat:
            all_cats = db.query(Category).all()
            category_ids = list(_collect_descendant_category_ids(target_cat, all_cats))
            query = query.filter(Product.categories.any(Category.id.in_(category_ids)))
        else:
            query = query.filter(
                Product.categories.any(
                    or_(
                        Category.slug.ilike(category),
                        Category.name.ilike(category),
                    )
                )
            )

    # Collection filter
    if collection:
        query = query.filter(
            Product.collections.any(
                or_(
                    Collection.slug.ilike(collection),
                    Collection.name.ilike(collection),
                )
            )
        )

    # Occasion filter (queries product_occasions associations with fallback to tags)
    if occasion:
        target_occ = occasion.lower().strip()
        query = query.filter(
            or_(
                Product.occasions.any(
                    or_(
                        Occasion.id.ilike(target_occ),
                        Occasion.name.ilike(target_occ),
                    )
                ),
                Product.tags.any(Tag.name.ilike(target_occ)),
            )
        )

    # Tag filter
    if tag:
        query = query.filter(Product.tags.any(Tag.name.ilike(tag.strip())))


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
            joinedload(Product.product_categories),
            joinedload(Product.categories),
            joinedload(Product.product_collections),
            joinedload(Product.collections),
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
            joinedload(Product.product_categories),
            joinedload(Product.categories),
            joinedload(Product.product_collections),
            joinedload(Product.collections),
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

    prim_cat = product.primary_category
    primary_category_name = prim_cat.name if prim_cat else (product.categories[0].name if product.categories else "Other")
    primary_cat_summary = (
        CategorySummary(id=prim_cat.id, name=prim_cat.name, slug=prim_cat.slug)
        if prim_cat
        else None
    )
    categories_summary = [
        CategorySummary(id=c.id, name=c.name, slug=c.slug) for c in product.categories
    ]
    collections_summary = [
        CollectionSummary(id=col.id, name=col.name, slug=col.slug) for col in product.collections
    ]
    occ_ids = [occ.id for occ in product.occasions]
    occ_names = [occ.name for occ in product.occasions]
    tag_names = list(dict.fromkeys([t.name for t in product.tags] + occ_ids + occ_names))

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
        category=primary_category_name,
        primary_category=primary_cat_summary,
        categories=categories_summary,
        collections=collections_summary,
        tags=tag_names,
        occasions=occ_ids,
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
    """Retrieve curated gift occasions: active seasonal occasions first, then evergreen occasions."""
    all_occasions = (
        db.query(Occasion)
        .order_by(Occasion.display_order.asc(), Occasion.id.asc())
        .all()
    )
    seasonal = [o for o in all_occasions if not o.is_evergreen and o.is_enabled and o.is_in_season()]
    evergreen = [o for o in all_occasions if o.is_evergreen]
    return seasonal + evergreen



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
