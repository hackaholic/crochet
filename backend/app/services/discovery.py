"""Storefront discovery and ranking service conforming to Tasks 7.6 & 7.6.1.

Implements ranked, truthful catalogue discovery sections with fair allocation,
ranking provenance, deduplication, basket exclusion, and opaque cursor pagination.
"""

import base64
import json
from typing import Any
from fastapi import HTTPException, status
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from app.models.cart import Cart, CartItem
from app.models.catalogue import Category, Collection, Product, ProductVariant, Review, Tag
from app.models.order import Order, OrderItem, OrderStatus, PaymentMethod, PaymentStatus
from app.models.user import User
from app.schemas.discovery import DiscoverySectionOut

MAX_CURSOR_LENGTH = 512
MAX_SECTIONS = 5
MAX_PRODUCTS_PER_SECTION = 8
MAX_TOTAL_PAGE_PRODUCTS = 16
ALLOWED_DISCOVERY_CONTEXTS = {"checkout", "basket", "wishlist"}


def get_cart_product_ids(
    db: Session,
    user: User | None = None,
    guest_token: str | None = None,
) -> set[int]:
    """Extract product IDs currently in the user's or guest's active cart without side effects."""
    cart = None
    if user:
        cart = db.query(Cart).filter(Cart.user_id == user.id, Cart.status == "ACTIVE").first()
    if not cart and guest_token:
        cart = db.query(Cart).filter(Cart.guest_token == guest_token, Cart.status == "ACTIVE").first()
        if cart and cart.user_id is not None and (not user or cart.user_id != user.id):
            cart = None  # Prevent IDOR

    if not cart:
        return set()

    items = (
        db.query(CartItem)
        .options(joinedload(CartItem.variant))
        .filter(CartItem.cart_id == cart.id)
        .all()
    )
    return {item.variant.product_id for item in items if item.variant and item.variant.product_id}


def encode_cursor(seen_ids: list[int], context: str) -> str:
    """Encode pagination state into an opaque, URL-safe base64 string <= 512 chars."""
    if context not in ALLOWED_DISCOVERY_CONTEXTS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unsupported discovery context: '{context}'",
        )
    payload = {
        "s": sorted(list(set(seen_ids))),
        "c": context,
        "v": 1,
    }
    raw_json = json.dumps(payload, separators=(",", ":"))
    cursor = base64.urlsafe_b64encode(raw_json.encode("utf-8")).decode("ascii")
    if len(cursor) > MAX_CURSOR_LENGTH:
        # If cursor string exceeds 512 chars under extreme sets, return terminal None
        return ""
    return cursor


def decode_cursor(cursor: str | None, expected_context: str, db: Session | None = None) -> list[int]:
    """Decode and validate an opaque discovery cursor, raising HTTP 422 if invalid."""
    if expected_context not in ALLOWED_DISCOVERY_CONTEXTS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unsupported discovery context: '{expected_context}'",
        )
    if not cursor:
        return []

    if len(cursor) > MAX_CURSOR_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Cursor exceeds maximum allowed length of 512 characters",
        )

    # Reserve catalogue: prefix for client compatibility; never issue it
    if cursor.startswith("catalogue:"):
        offset_str = cursor[len("catalogue:"):]
        if not offset_str.isdigit():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid catalogue cursor",
            )
        offset = int(offset_str)
        if offset < 0 or offset > 10000:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Catalogue cursor offset out of bounds",
            )
        if db is not None:
            rows = (
                db.query(Product.id)
                .filter(Product.status == "ACTIVE")
                .order_by(Product.id.asc())
                .limit(offset)
                .all()
            )
            return [r[0] for r in rows]
        return []

    try:
        raw_bytes = base64.urlsafe_b64decode(cursor.encode("ascii"))
        data = json.loads(raw_bytes.decode("utf-8"))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid discovery cursor encoding",
        )

    if not isinstance(data, dict) or data.get("v") != 1:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid discovery cursor version or schema",
        )

    if data.get("c") != expected_context:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Cursor context mismatch: expected '{expected_context}'",
        )

    seen = data.get("s")
    if not isinstance(seen, list) or not all(isinstance(x, int) and x > 0 for x in seen):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid product IDs in cursor",
        )

    return seen


def _base_candidate_query(db: Session, excluded_ids: set[int]):
    """Query active, in-stock products excluding specified IDs."""
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
        .filter(Product.variants.any(ProductVariant.stock_quantity > 0))
    )
    if excluded_ids:
        query = query.filter(~Product.id.in_(list(excluded_ids)))
    return query


def _resolve_related_products(
    db: Session,
    cart_product_ids: set[int],
    excluded_ids: set[int],
    limit: int,
) -> list[Product]:
    """Resolve related products based on categories and tags of current basket items."""
    if not cart_product_ids or limit <= 0:
        return []

    # Get categories and tags of products in cart
    cart_products = db.query(Product).filter(Product.id.in_(list(cart_product_ids))).all()
    target_category_ids = {cat.id for p in cart_products for cat in p.categories}
    target_tag_ids = {t.id for p in cart_products for t in p.tags}

    if not target_category_ids and not target_tag_ids:
        return []

    conditions = []
    if target_category_ids:
        conditions.append(Product.categories.any(Category.id.in_(list(target_category_ids))))
    if target_tag_ids:
        conditions.append(Product.tags.any(Tag.id.in_(list(target_tag_ids))))

    query = (
        _base_candidate_query(db, excluded_ids)
        .filter(or_(*conditions))
        .order_by(Product.rating.desc(), Product.reviews_count.desc(), Product.id.desc())
        .limit(limit)
    )
    return query.all()


def _resolve_popular_products(
    db: Session,
    excluded_ids: set[int],
    limit: int,
) -> list[Product]:
    """Resolve popular/bestseller products using real collection/badge/eligible sales signals.
    
    Excludes cancelled, refunded, failed, and unpaid orders.
    """
    if limit <= 0:
        return []

    col = (
        db.query(Collection)
        .filter(Collection.slug.in_(["bestsellers", "best-sellers"]), Collection.is_active == True)
        .first()
    )
    col_product_ids = [p.id for p in col.products] if col else []

    conditions = [Product.badge.in_(["Bestseller", "Popular"])]
    if col_product_ids:
        conditions.append(Product.id.in_(col_product_ids))

    # Eligible order sales only: paid or active COD, excluding cancelled/refunded/failed
    excluded_order_statuses = [
        OrderStatus.CANCELLED.value,
        OrderStatus.REFUNDED.value,
        "CANCELLED",
        "REFUNDED",
    ]
    excluded_payments = [
        PaymentStatus.FAILED.value,
        PaymentStatus.REFUNDED.value,
        "FAILED",
        "REFUNDED",
    ]
    eligible_paid_statuses = [
        PaymentStatus.PAID.value,
        "PAID",
        "PARTIALLY_REFUNDED",
    ]

    top_ordered = (
        db.query(OrderItem.product_id, func.sum(OrderItem.quantity).label("sold_qty"))
        .join(Order, Order.id == OrderItem.order_id)
        .filter(
            OrderItem.product_id.isnot(None),
            Order.status.not_in(excluded_order_statuses),
            Order.payment_status.not_in(excluded_payments),
            or_(
                Order.payment_method == PaymentMethod.COD.value,
                Order.payment_status.in_(eligible_paid_statuses),
            ),
        )
        .group_by(OrderItem.product_id)
        .order_by(func.sum(OrderItem.quantity).desc())
        .limit(limit * 2)
        .all()
    )
    ordered_pids = [pid for pid, _ in top_ordered if pid]
    if ordered_pids:
        conditions.append(Product.id.in_(ordered_pids))

    query = (
        _base_candidate_query(db, excluded_ids)
        .filter(or_(*conditions))
        .order_by(Product.rating.desc(), Product.id.desc())
        .limit(limit)
    )
    return query.all()


def _resolve_newest_products(
    db: Session,
    excluded_ids: set[int],
    limit: int,
) -> list[Product]:
    """Resolve new arrival products strictly based on new-arrivals collection or New badge.
    
    Zero broad backfill of unrelated catalogue items (Task 7.6.1).
    """
    if limit <= 0:
        return []

    col = (
        db.query(Collection)
        .filter(Collection.slug.in_(["new-arrivals", "new"]), Collection.is_active == True)
        .first()
    )
    col_pids = [p.id for p in col.products] if col else []

    conditions = [Product.badge == "New"]
    if col_pids:
        conditions.append(Product.id.in_(col_pids))

    new_products = (
        _base_candidate_query(db, excluded_ids)
        .filter(or_(*conditions))
        .order_by(Product.created_at.desc(), Product.id.desc())
        .limit(limit)
        .all()
    )
    return new_products


def _resolve_featured_products(
    db: Session,
    excluded_ids: set[int],
    limit: int,
) -> list[Product]:
    """Resolve featured products using curated badges, curated collections, or high ratings (>= 4.5)."""
    if limit <= 0:
        return []

    col = (
        db.query(Collection)
        .filter(Collection.slug.in_(["featured", "curated", "exclusive"]), Collection.is_active == True)
        .first()
    )
    col_pids = [p.id for p in col.products] if col else []

    conditions = [
        Product.badge.in_(["Featured", "Limited", "Handmade", "Artisanal", "Heirloom", "Devotional", "Duo", "Set"]),
        Product.rating >= 4.5,
    ]
    if col_pids:
        conditions.append(Product.id.in_(col_pids))

    query = (
        _base_candidate_query(db, excluded_ids)
        .filter(or_(*conditions))
        .order_by(Product.rating.desc(), Product.id.desc())
        .limit(limit)
    )
    return query.all()


def _resolve_trending_products(
    db: Session,
    excluded_ids: set[int],
    limit: int,
) -> list[Product]:
    """Resolve trending products based strictly on genuine Review records in the reviews table."""
    if limit <= 0:
        return []

    # Query genuine review counts and average rating from reviews table
    review_stats = (
        db.query(
            Review.product_id,
            func.count(Review.id).label("rev_count"),
            func.avg(Review.rating).label("avg_rating"),
        )
        .filter(Review.product_id.isnot(None))
        .group_by(Review.product_id)
        .having(func.count(Review.id) >= 1)
        .order_by(func.count(Review.id).desc(), func.avg(Review.rating).desc())
        .all()
    )
    if not review_stats:
        return []

    ordered_review_pids = [r[0] for r in review_stats if r[0] is not None]

    candidates = (
        _base_candidate_query(db, excluded_ids)
        .filter(Product.id.in_(ordered_review_pids))
        .all()
    )
    if not candidates:
        return []

    # Maintain rank order from genuine reviews
    rank_map = {pid: idx for idx, pid in enumerate(ordered_review_pids)}
    candidates.sort(key=lambda p: rank_map.get(p.id, 9999))
    return candidates[:limit]


def _resolve_strategy_candidates(
    strat_key: str,
    db: Session,
    cart_ids: set[int],
    excluded_ids: set[int],
    limit: int,
) -> list[Product]:
    """Dispatch strategy candidate resolution."""
    if strat_key == "related":
        return _resolve_related_products(db, cart_ids, excluded_ids, limit)
    elif strat_key == "popular":
        return _resolve_popular_products(db, excluded_ids, limit)
    elif strat_key == "newest":
        return _resolve_newest_products(db, excluded_ids, limit)
    elif strat_key == "featured":
        return _resolve_featured_products(db, excluded_ids, limit)
    elif strat_key == "trending":
        return _resolve_trending_products(db, excluded_ids, limit)
    return []


def get_discovery_feed(
    db: Session,
    context: str = "checkout",
    limit: int = 16,
    cursor: str | None = None,
    cart_product_ids: set[int] | None = None,
) -> tuple[list[DiscoverySectionOut], str | None]:
    """Assemble ranked discovery sections with deterministic fair allocation and opaque cursor.

    Returns (sections, next_cursor).
    """
    effective_limit = max(1, min(limit, MAX_TOTAL_PAGE_PRODUCTS))
    seen_ids = set(decode_cursor(cursor, context, db))
    cart_ids = cart_product_ids or set()

    # Excluded products: already seen on prior pages and items currently in active cart
    excluded_ids = set(cart_ids) | set(seen_ids)

    # Strategy definitions in natural presentation order
    strategy_definitions = [
        ("related", "Recommended for Your Order", "related"),
        ("popular", "Best Sellers", "popular"),
        ("new-arrivals", "New Arrivals", "newest"),
        ("featured", "Featured Picks", "featured"),
        ("trending", "Trending Now", "trending"),
    ]

    active_specs: list[tuple[str, str, str]] = []
    for sec_id, title, strat_key in strategy_definitions:
        if strat_key == "related" and not cart_ids:
            continue
        active_specs.append((sec_id, title, strat_key))

    # Pre-fetch candidate pools for each active strategy (up to effective_limit)
    candidate_pools: dict[str, list[Product]] = {}
    for sec_id, _, strat_key in active_specs:
        candidate_pools[sec_id] = _resolve_strategy_candidates(
            strat_key, db, cart_ids, excluded_ids, limit=effective_limit
        )

    # Round-robin fair allocation across active strategies
    # Prevents early strategies from monopolizing the page or starving later groups
    section_products: dict[str, list[Product]] = {sec_id: [] for sec_id, _, _ in active_specs}
    claimed_ids: set[int] = set()

    max_rounds = MAX_PRODUCTS_PER_SECTION
    for _ in range(max_rounds):
        picked_in_round = False
        for sec_id, _, _ in active_specs:
            if len(claimed_ids) >= effective_limit:
                break
            if len(section_products[sec_id]) >= MAX_PRODUCTS_PER_SECTION:
                continue

            pool = candidate_pools[sec_id]
            for p in pool:
                if p.id not in claimed_ids:
                    claimed_ids.add(p.id)
                    section_products[sec_id].append(p)
                    picked_in_round = True
                    break

        if len(claimed_ids) >= effective_limit or not picked_in_round:
            break

    # Build response sections in presentation order, omitting empty unsupported groups
    from app.api.v1.catalogue import _to_product_list_items

    page_seen_ids: list[int] = []
    sections: list[DiscoverySectionOut] = []

    for sec_id, title, strat_key in active_specs:
        prods = section_products.get(sec_id, [])
        if prods:
            for p in prods:
                page_seen_ids.append(p.id)
            list_items = _to_product_list_items(prods, db)
            sections.append(
                DiscoverySectionOut(
                    id=sec_id,
                    title=title,
                    strategy=strat_key,  # type: ignore[arg-type]
                    products=list_items,
                )
            )

    # Check whether more eligible products exist for any active strategy
    all_seen = list(seen_ids) + page_seen_ids
    next_excluded = set(all_seen) | set(cart_ids)

    has_more = False
    if page_seen_ids:
        for _, _, strat_key in active_specs:
            more_candidates = _resolve_strategy_candidates(
                strat_key, db, cart_ids, next_excluded, limit=1
            )
            if more_candidates:
                has_more = True
                break

    if has_more:
        next_cursor = encode_cursor(all_seen, context)
        if not next_cursor:
            next_cursor = None
    else:
        next_cursor = None

    return sections, next_cursor


def _resolve_personalized_products(
    db: Session,
    user: User | None,
    excluded_ids: set[int],
    limit: int,
) -> list[Product]:
    """Resolve personalized recommendations for authenticated users based on real past orders."""
    if not user or limit <= 0:
        return []

    excluded_order_statuses = [
        OrderStatus.CANCELLED.value,
        OrderStatus.REFUNDED.value,
        "CANCELLED",
        "REFUNDED",
    ]
    excluded_payments = [
        PaymentStatus.FAILED.value,
        PaymentStatus.REFUNDED.value,
        "FAILED",
        "REFUNDED",
    ]
    eligible_paid_statuses = [
        PaymentStatus.PAID.value,
        "PAID",
        "PARTIALLY_REFUNDED",
    ]

    past_ordered_items = (
        db.query(OrderItem.product_id)
        .join(Order, Order.id == OrderItem.order_id)
        .filter(
            Order.user_id == user.id,
            OrderItem.product_id.isnot(None),
            Order.status.not_in(excluded_order_statuses),
            Order.payment_status.not_in(excluded_payments),
            or_(
                Order.payment_method == PaymentMethod.COD.value,
                Order.payment_status.in_(eligible_paid_statuses),
            ),
        )
        .all()
    )
    past_product_ids = {pid for pid, in past_ordered_items if pid}
    if not past_product_ids:
        return []

    past_products = db.query(Product).filter(Product.id.in_(list(past_product_ids))).all()
    target_category_ids = {cat.id for p in past_products for cat in p.categories}
    target_tag_ids = {t.id for p in past_products for t in p.tags}

    if not target_category_ids and not target_tag_ids:
        return []

    conditions = []
    if target_category_ids:
        conditions.append(Product.categories.any(Category.id.in_(list(target_category_ids))))
    if target_tag_ids:
        conditions.append(Product.tags.any(Tag.id.in_(list(target_tag_ids))))

    all_excluded = set(excluded_ids) | past_product_ids
    query = (
        _base_candidate_query(db, all_excluded)
        .filter(or_(*conditions))
        .order_by(Product.rating.desc(), Product.reviews_count.desc(), Product.id.desc())
        .limit(limit)
    )
    return query.all()


def get_cart_recommendations(
    db: Session,
    user: User | None = None,
    guest_token: str | None = None,
    limit: int = 4,
) -> tuple[str, list[Any]]:
    """Assemble basket-aware recommendations conforming to Task 23.3.

    Returns (strategy, products) where strategy is one of:
    - 'personalized': authenticated user with matching past purchase signals
    - 'related': cart contains items with matching categories or tags
    - 'featured': curated items / high rating fallback
    - 'newest': newest arrivals fallback

    Basket items, inactive products, and out-of-stock items are strictly excluded.
    """
    effective_limit = max(1, min(limit, 8))
    cart_ids = get_cart_product_ids(db, user=user, guest_token=guest_token)
    excluded_ids = set(cart_ids)

    # 1. Try personalized strategy if authenticated user has past purchase signals
    candidates: list[Product] = []
    strategy = "newest"

    if user:
        candidates = _resolve_personalized_products(db, user, excluded_ids, effective_limit)
        if candidates:
            strategy = "personalized"

    # 2. Try related strategy if cart has items
    if not candidates and cart_ids:
        candidates = _resolve_related_products(db, cart_ids, excluded_ids, effective_limit)
        if candidates:
            strategy = "related"

    # 3. Truthful fallback to featured
    if not candidates:
        candidates = _resolve_featured_products(db, excluded_ids, effective_limit)
        if candidates:
            strategy = "featured"

    # 4. Truthful fallback to newest
    if not candidates:
        candidates = _resolve_newest_products(db, excluded_ids, effective_limit)
        if candidates:
            strategy = "newest"

    # 5. Fallback to active catalogue ordered by creation date if specific badge/collection query returned empty
    if not candidates:
        candidates = (
            _base_candidate_query(db, excluded_ids)
            .order_by(Product.created_at.desc(), Product.id.desc())
            .limit(effective_limit)
            .all()
        )
        strategy = "newest"

    from app.api.v1.catalogue import _to_product_list_items
    list_items = _to_product_list_items(candidates, db)
    return strategy, list_items
