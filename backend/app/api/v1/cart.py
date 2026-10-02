"""Shopping cart endpoints conforming to Sections 6, 7, 18, and 28 of the Specification."""

import secrets
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Cookie, Depends, Header, HTTPException, Response, status
from sqlalchemy.orm import Session, joinedload

from app.api.v1.auth import get_optional_current_user
from app.core.config import settings
from app.db.session import get_db
from app.models.cart import Cart, CartItem
from app.models.catalogue import Product, ProductVariant
from app.models.promotion import Coupon
from app.models.user import User
from app.schemas.cart import (
    CartItemAdd,
    CartItemOut,
    CartItemUpdate,
    CartMergeRequest,
    CartOut,
)
from app.schemas.promotion import CouponApplyRequest, CouponApplyResponse

router = APIRouter(prefix="/cart", tags=["cart"])

COOKIE_NAME = "guest_cart_token"
COOKIE_MAX_AGE = 30 * 24 * 3600  # 30 days


def _get_cart_token(
    guest_cart_token: str | None = Cookie(default=None),
    x_cart_token: str | None = Header(default=None),
) -> str | None:
    """Extract cart token from cookie or X-Cart-Token header fallback."""
    return guest_cart_token or x_cart_token


def _get_or_create_cart(
    response: Response,
    db: Session,
    token: str | None,
    user: User | None = None,
    create_if_missing: bool = False,
) -> tuple[Cart | None, str | None]:
    """Retrieve existing active cart by user or token, or create a new cart."""
    # 1. Look up user cart if user is authenticated
    if user:
        user_cart = (
            db.query(Cart)
            .options(
                joinedload(Cart.items).joinedload(CartItem.variant).joinedload(ProductVariant.product)
            )
            .filter(Cart.user_id == user.id, Cart.status == "ACTIVE")
            .first()
        )
        if user_cart:
            return user_cart, user_cart.guest_token

    # 2. Look up guest cart by token
    if token:
        cart = (
            db.query(Cart)
            .options(
                joinedload(Cart.items).joinedload(CartItem.variant).joinedload(ProductVariant.product)
            )
            .filter(Cart.guest_token == token, Cart.status == "ACTIVE")
            .first()
        )
        if cart:
            # Prevent IDOR: if cart is claimed by a specific user, reject unauthorized access
            if cart.user_id is not None and (not user or cart.user_id != user.id):
                cart = None
            elif user and not cart.user_id:
                cart.user_id = user.id
                db.commit()
        if cart:
            return cart, token

    if not create_if_missing:
        return None, None

    # Generate new secure guest token
    new_token = secrets.token_urlsafe(32)
    cart = Cart(
        guest_token=new_token,
        user_id=user.id if user else None,
        status="ACTIVE",
        expires_at=datetime.now(timezone.utc) + timedelta(days=30),
    )
    db.add(cart)
    db.commit()
    db.refresh(cart)

    # Set HttpOnly, SameSite=Lax cookie on response
    response.set_cookie(
        key=COOKIE_NAME,
        value=new_token,
        max_age=COOKIE_MAX_AGE,
        httponly=True,
        samesite="lax",
        secure=settings.cookie_secure,
        domain=settings.cookie_domain,
    )
    return cart, new_token


def _build_cart_response(cart: Cart | None, token: str | None = None) -> CartOut:
    """Format Cart ORM model into CartOut schema."""
    if not cart:
        return CartOut(id=None, guest_token=token, items=[], item_count=0, subtotal=0, status="ACTIVE")

    out_items: list[CartItemOut] = []
    total_qty = 0
    subtotal = 0

    for item in cart.items:
        variant = item.variant
        product = variant.product
        unit_price = variant.price
        line_total = unit_price * item.quantity

        total_qty += item.quantity
        subtotal += line_total

        out_items.append(
            CartItemOut(
                id=item.id,
                product_id=product.id,
                product_name=product.name,
                product_slug=product.slug,
                product_image=product.primary_image,
                variant_id=variant.id,
                variant_sku=variant.sku,
                variant_name=variant.name,
                unit_price=unit_price,
                unit_price_paise=unit_price * 100,
                currency="INR",
                compare_at_price=variant.compare_at_price,
                quantity=item.quantity,
                line_total=line_total,
                line_total_paise=line_total * 100,
                personalization=item.personalization_json or {},
                stock_available=variant.stock_quantity,
            )
        )

    return CartOut(
        id=cart.id,
        guest_token=cart.guest_token,
        items=out_items,
        item_count=total_qty,
        subtotal=subtotal,
        subtotal_paise=subtotal * 100,
        currency="INR",
        status=cart.status,
    )


# -----------------------------------------------------------------------------
# Cart Endpoints (Section 18)
# -----------------------------------------------------------------------------

@router.get("", response_model=CartOut)
def get_cart(
    response: Response,
    token: str | None = Depends(_get_cart_token),
    current_user: User | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
) -> CartOut:
    """Retrieve current shopping cart. Returns empty cart representation if no cart exists."""
    cart, active_token = _get_or_create_cart(response, db, token, user=current_user, create_if_missing=False)
    return _build_cart_response(cart, active_token)


@router.post("/items", response_model=CartOut, status_code=status.HTTP_201_CREATED)
def add_cart_item(
    payload: CartItemAdd,
    response: Response,
    token: str | None = Depends(_get_cart_token),
    current_user: User | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
) -> CartOut:
    """Add a product or variant to the cart with quantity and optional personalization."""
    # 1. Resolve variant
    variant: ProductVariant | None = None
    if payload.product_variant_id is not None:
        variant = db.query(ProductVariant).filter_by(id=payload.product_variant_id).first()
    elif payload.sku:
        variant = db.query(ProductVariant).filter_by(sku=payload.sku).first()
    elif payload.product_id is not None:
        product = db.query(Product).options(joinedload(Product.variants)).filter_by(id=payload.product_id).first()
        if product and product.variants:
            variant = product.variants[0]

    if not variant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product variant not found",
        )

    if variant.stock_quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"'{variant.name}' is currently out of stock",
        )

    # 2. Get or create cart and set guest cookie
    cart, _ = _get_or_create_cart(response, db, token, user=current_user, create_if_missing=True)
    assert cart is not None

    # 3. Check if identical item (same variant and personalization) already in cart
    existing_item = next(
        (
            item
            for item in cart.items
            if item.product_variant_id == variant.id
            and (item.personalization_json or {}) == (payload.personalization or {})
        ),
        None,
    )

    if existing_item:
        new_quantity = existing_item.quantity + payload.quantity
        if new_quantity > variant.stock_quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot add {payload.quantity} more. Only {variant.stock_quantity} available in stock.",
            )
        existing_item.quantity = new_quantity
    else:
        if payload.quantity > variant.stock_quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Requested quantity {payload.quantity} exceeds available stock of {variant.stock_quantity}.",
            )
        new_item = CartItem(
            cart_id=cart.id,
            product_variant_id=variant.id,
            quantity=payload.quantity,
            personalization_json=payload.personalization or {},
        )
        db.add(new_item)

    db.commit()
    db.refresh(cart)
    return _build_cart_response(cart)


@router.patch("/items/{item_id}", response_model=CartOut)
def update_cart_item(
    item_id: int,
    payload: CartItemUpdate,
    response: Response,
    token: str | None = Depends(_get_cart_token),
    current_user: User | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
) -> CartOut:
    """Update quantity or personalization for a specific line item in the cart."""
    cart, _ = _get_or_create_cart(response, db, token, user=current_user, create_if_missing=False)
    if not cart:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")

    item = db.query(CartItem).filter_by(id=item_id, cart_id=cart.id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Cart item {item_id} not found")

    variant = item.variant
    if payload.quantity > variant.stock_quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Requested quantity {payload.quantity} exceeds available stock of {variant.stock_quantity}.",
        )

    item.quantity = payload.quantity
    if payload.personalization is not None:
        item.personalization_json = payload.personalization

    db.commit()
    db.refresh(cart)
    return _build_cart_response(cart)


@router.delete("/items/{item_id}", response_model=CartOut)
def delete_cart_item(
    item_id: int,
    response: Response,
    token: str | None = Depends(_get_cart_token),
    current_user: User | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
) -> CartOut:
    """Remove a specific line item from the cart."""
    cart, _ = _get_or_create_cart(response, db, token, user=current_user, create_if_missing=False)
    if not cart:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")

    item = db.query(CartItem).filter_by(id=item_id, cart_id=cart.id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Cart item {item_id} not found")

    db.delete(item)
    db.commit()
    db.refresh(cart)
    return _build_cart_response(cart)


@router.delete("", response_model=CartOut)
def clear_cart(
    response: Response,
    token: str | None = Depends(_get_cart_token),
    current_user: User | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
) -> CartOut:
    """Clear all items from the current cart."""
    cart, _ = _get_or_create_cart(response, db, token, user=current_user, create_if_missing=False)
    if cart:
        db.query(CartItem).filter_by(cart_id=cart.id).delete()
        db.commit()
        db.refresh(cart)

    return _build_cart_response(cart)


@router.post("/merge", response_model=CartOut)
def merge_guest_cart(
    payload: CartMergeRequest,
    response: Response,
    token: str | None = Depends(_get_cart_token),
    current_user: User | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
) -> CartOut:
    """Merge an anonymous guest cart into the active session cart conforming to Section 6 of Spec."""
    source_cart = (
        db.query(Cart)
        .options(joinedload(Cart.items).joinedload(CartItem.variant))
        .filter(Cart.guest_token == payload.guest_token, Cart.status == "ACTIVE")
        .first()
    )

    if not source_cart or not source_cart.items:
        # Nothing to merge; return current target cart
        cart, _ = _get_or_create_cart(response, db, token, user=current_user, create_if_missing=False)
        return _build_cart_response(cart)

    # Ensure target cart exists
    target_cart, _ = _get_or_create_cart(response, db, token, user=current_user, create_if_missing=True)
    assert target_cart is not None

    if source_cart.id == target_cart.id:
        return _build_cart_response(target_cart)

    # Deterministic merge rule:
    # quantity = min(guest_quantity + existing_quantity, stock_quantity)
    for src_item in source_cart.items:
        existing = next(
            (
                tgt
                for tgt in target_cart.items
                if tgt.product_variant_id == src_item.product_variant_id
                and (tgt.personalization_json or {}) == (src_item.personalization_json or {})
            ),
            None,
        )

        stock = src_item.variant.stock_quantity
        if existing:
            existing.quantity = min(existing.quantity + src_item.quantity, stock)
        else:
            merged_qty = min(src_item.quantity, stock)
            if merged_qty > 0:
                target_cart.items.append(
                    CartItem(
                        product_variant_id=src_item.product_variant_id,
                        quantity=merged_qty,
                        personalization_json=src_item.personalization_json or {},
                    )
                )

    # Mark source cart as converted
    source_cart.status = "CONVERTED"

    db.commit()
    db.refresh(target_cart)
    return _build_cart_response(target_cart)


@router.post("/apply-coupon", response_model=CouponApplyResponse)
def apply_coupon(
    payload: CouponApplyRequest,
    response: Response,
    token: str | None = Depends(_get_cart_token),
    current_user: User | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
) -> CouponApplyResponse:
    """Validate and apply promo coupon to active cart."""
    cart, _ = _get_or_create_cart(response, db, token, current_user, create_if_missing=False)
    if not cart or not cart.items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Active cart is empty")

    now = datetime.now(timezone.utc)
    code_clean = payload.code.strip().upper()
    coupon = db.query(Coupon).filter(Coupon.code == code_clean, Coupon.is_active.is_(True)).first()
    if not coupon:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Coupon '{payload.code}' is invalid or expired.")

    # Validate dates
    if coupon.valid_from:
        v_from = coupon.valid_from.replace(tzinfo=timezone.utc) if coupon.valid_from.tzinfo is None else coupon.valid_from
        if now < v_from:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Coupon is not yet active.")

    if coupon.valid_until:
        v_until = coupon.valid_until.replace(tzinfo=timezone.utc) if coupon.valid_until.tzinfo is None else coupon.valid_until
        if now > v_until:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Coupon has expired.")

    # Validate usage limit
    if coupon.usage_limit is not None and coupon.usage_count >= coupon.usage_limit:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Coupon usage limit reached.")

    # Compute cart subtotal
    subtotal = sum(item.variant.price * item.quantity for item in cart.items if item.variant)
    if subtotal < coupon.min_order_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Minimum order amount for this coupon is ₹{coupon.min_order_amount}. Cart total is ₹{subtotal}.",
        )

    # Compute discount
    if coupon.discount_type == "PERCENTAGE":
        discount = (subtotal * coupon.discount_value) // 100
        if coupon.max_discount_amount is not None:
            discount = min(discount, coupon.max_discount_amount)
    else:  # FLAT
        discount = min(coupon.discount_value, subtotal)

    subtotal_after = max(0, subtotal - discount)

    return CouponApplyResponse(
        code=coupon.code,
        discountType=coupon.discount_type,
        discountValue=coupon.discount_value,
        discountAmount=discount,
        discountAmountPaise=discount * 100,
        subtotalBeforeDiscount=subtotal,
        subtotalAfterDiscount=subtotal_after,
        subtotalAfterDiscountPaise=subtotal_after * 100,
        message=f"Coupon '{coupon.code}' applied: ₹{discount} discount",
    )


@router.delete("/coupon")
def remove_coupon() -> dict[str, str]:
    """Remove coupon from cart session."""
    return {"status": "ok", "message": "Coupon removed from cart"}

