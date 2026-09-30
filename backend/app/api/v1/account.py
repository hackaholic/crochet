"""Customer Account, Profile, and Wishlist API endpoints.

Conforms to Sections 19 (Customer Account) & 27 (Wishlist) of the Specification.
"""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.api.v1.auth import get_current_user
from app.db.session import get_db
from app.models.account import Wishlist, WishlistItem
from app.models.catalogue import Product
from app.models.order import Address, Order, OrderStatus
from app.models.user import User
from app.schemas.account import (
    AccountOverviewOut,
    ProfileOut,
    ProfileUpdate,
    WishlistItemAdd,
    WishlistItemOut,
    WishlistOut,
)

router = APIRouter(tags=["account"])


def _to_profile_out(user: User) -> ProfileOut:
    """Helper to convert User ORM to ProfileOut."""
    identities = [i.provider for i in user.identities] if user.identities else []
    return ProfileOut(
        id=user.id,
        name=user.name,
        email=user.email,
        phone=user.phone,
        status=user.status,
        identities=identities,
        created_at=user.created_at.isoformat() if user.created_at else "",
        last_login_at=user.last_login_at.isoformat() if user.last_login_at else None,
    )


def _to_wishlist_item_out(item: WishlistItem) -> WishlistItemOut:
    """Helper to convert WishlistItem ORM to WishlistItemOut."""
    product = item.product
    primary_category = product.categories[0].name if product.categories else "Other"
    primary_variant = product.variants[0] if product.variants else None
    price = primary_variant.price if primary_variant else 0
    compare_at_price = primary_variant.compare_at_price if primary_variant else None
    stock = sum(v.stock_quantity for v in product.variants) if product.variants else (primary_variant.stock_quantity if primary_variant else 10)

    return WishlistItemOut(
        id=item.id,
        product_id=product.id,
        product_name=product.name,
        product_slug=product.slug,
        product_image=product.primary_image,
        price=price,
        price_paise=price * 100,
        compare_at_price=compare_at_price,
        original_price=compare_at_price,
        badge=product.badge,
        category=primary_category,
        in_stock=stock > 0,
        rating=product.rating,
        reviews=product.reviews_count,
        created_at=item.created_at.isoformat() if item.created_at else "",
    )


def _get_or_create_wishlist(db: Session, user: User) -> Wishlist:
    """Get active customer wishlist or initialize one."""
    wishlist = (
        db.query(Wishlist)
        .options(
            joinedload(Wishlist.items)
            .joinedload(WishlistItem.product)
            .joinedload(Product.categories),
            joinedload(Wishlist.items)
            .joinedload(WishlistItem.product)
            .joinedload(Product.variants),
        )
        .filter(Wishlist.user_id == user.id)
        .first()
    )
    if not wishlist:
        wishlist = Wishlist(user_id=user.id)
        db.add(wishlist)
        db.commit()
        db.refresh(wishlist)
    return wishlist


# =============================================================================
# Customer Profile & Account Overview (Section 19)
# =============================================================================

@router.get("/account/profile", response_model=ProfileOut)
def get_customer_profile(
    user: User = Depends(get_current_user),
) -> ProfileOut:
    """Retrieve logged-in customer's profile."""
    return _to_profile_out(user)


@router.patch("/account/profile", response_model=ProfileOut)
def update_customer_profile(
    payload: ProfileUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProfileOut:
    """Update customer profile information."""
    if payload.name is not None:
        user.name = payload.name
    if payload.email is not None:
        # Check uniqueness if changing email
        if payload.email != user.email:
            existing = db.query(User).filter(User.email == payload.email).first()
            if existing and existing.id != user.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="This email address is already associated with another account.",
                )
            user.email = payload.email

    user.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)
    return _to_profile_out(user)


@router.get("/account/overview", response_model=AccountOverviewOut)
def get_account_overview(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AccountOverviewOut:
    """Retrieve aggregate statistics for customer dashboard."""
    total_orders = db.query(Order).filter(Order.user_id == user.id).count()
    active_statuses = [
        OrderStatus.CONFIRMED.value,
        OrderStatus.PROCESSING.value,
        OrderStatus.READY_TO_SHIP.value,
        OrderStatus.SHIPPED.value,
        OrderStatus.OUT_FOR_DELIVERY.value,
    ]
    active_orders = (
        db.query(Order)
        .filter(Order.user_id == user.id, Order.status.in_(active_statuses))
        .count()
    )
    saved_addresses = db.query(Address).filter(Address.user_id == user.id).count()

    wishlist = db.query(Wishlist).filter(Wishlist.user_id == user.id).first()
    wishlist_count = len(wishlist.items) if wishlist else 0

    return AccountOverviewOut(
        profile=_to_profile_out(user),
        total_orders=total_orders,
        active_orders=active_orders,
        saved_addresses=saved_addresses,
        wishlist_items_count=wishlist_count,
    )


# =============================================================================
# Wishlist Endpoints (Section 27)
# =============================================================================

@router.get("/wishlist", response_model=WishlistOut)
def get_wishlist(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WishlistOut:
    """Retrieve all products saved in customer's wishlist."""
    wishlist = _get_or_create_wishlist(db, user)
    items_out = [_to_wishlist_item_out(i) for i in wishlist.items if i.product]
    return WishlistOut(items=items_out, total_items=len(items_out))


@router.post("/wishlist/items", response_model=WishlistOut, status_code=status.HTTP_201_CREATED)
def add_to_wishlist(
    payload: WishlistItemAdd,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WishlistOut:
    """Add a product to the customer's wishlist."""
    product = None
    if payload.product_id:
        product = db.query(Product).filter(Product.id == payload.product_id).first()
    elif payload.product_slug:
        product = db.query(Product).filter(Product.slug == payload.product_slug).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found.",
        )

    wishlist = _get_or_create_wishlist(db, user)

    # Check if already in wishlist
    existing_item = (
        db.query(WishlistItem)
        .filter(WishlistItem.wishlist_id == wishlist.id, WishlistItem.product_id == product.id)
        .first()
    )
    if not existing_item:
        new_item = WishlistItem(
            wishlist_id=wishlist.id,
            product_id=product.id,
            created_at=datetime.now(timezone.utc),
        )
        db.add(new_item)
        wishlist.updated_at = datetime.now(timezone.utc)
        db.commit()

    return get_wishlist(user, db)


@router.delete("/wishlist/items/{product_id_or_slug}", response_model=WishlistOut)
def remove_from_wishlist(
    product_id_or_slug: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WishlistOut:
    """Remove a product from the customer's wishlist."""
    wishlist = _get_or_create_wishlist(db, user)

    product = None
    if product_id_or_slug.isdigit():
        product = db.query(Product).filter(Product.id == int(product_id_or_slug)).first()
    else:
        product = db.query(Product).filter(Product.slug == product_id_or_slug).first()

    if product:
        item = (
            db.query(WishlistItem)
            .filter(WishlistItem.wishlist_id == wishlist.id, WishlistItem.product_id == product.id)
            .first()
        )
        if item:
            db.delete(item)
            wishlist.updated_at = datetime.now(timezone.utc)
            db.commit()

    return get_wishlist(user, db)


@router.delete("/wishlist", response_model=WishlistOut)
def clear_wishlist(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WishlistOut:
    """Clear all products from the customer's wishlist."""
    wishlist = _get_or_create_wishlist(db, user)
    db.query(WishlistItem).filter(WishlistItem.wishlist_id == wishlist.id).delete()
    wishlist.updated_at = datetime.now(timezone.utc)
    db.commit()
    return WishlistOut(items=[], total_items=0)
