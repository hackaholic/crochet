"""Order and Address API endpoints.

Conforms to Sections 18, 20, 21, 22, and 26 of the E-commerce Multi-Agent Specification.
"""

from datetime import datetime, timedelta, timezone
import secrets
from typing import Any
from fastapi import APIRouter, BackgroundTasks, Cookie, Depends, Header, HTTPException, Query, Response, status
from sqlalchemy.orm import Session, joinedload

from app.core.images import build_image_url
from app.api.v1.auth import get_current_user, get_optional_current_user
from app.db.session import get_db
from app.models.cart import Cart, CartItem
from app.models.catalogue import ProductVariant
from app.models.order import (
    Address,
    Order,
    OrderItem,
    OrderStatus,
    OrderStatusHistory,
    PaymentMethod,
    PaymentStatus,
)
from app.models.promotion import Coupon
from app.services.notification import (
    dispatch_order_placed_background,
    dispatch_order_status_background,
)
from app.models.user import User
from app.schemas.order import (
    AddressCreate,
    AddressOut,
    AddressUpdate,
    OrderCreate,
    OrderItemOut,
    OrderOut,
    OrderStatusHistoryOut,
    OrderTrackingOut,
)

router = APIRouter(tags=["orders"])


def _get_cart_token(
    guest_cart_token: str | None = Cookie(default=None),
    x_cart_token: str | None = Header(default=None),
) -> str | None:
    """Extract cart token from cookie or X-Cart-Token header fallback."""
    return guest_cart_token or x_cart_token


def _address_to_dict(addr: Address) -> dict[str, Any]:
    """Snapshot address into dictionary."""
    return {
        "id": addr.id,
        "name": addr.name,
        "phone": addr.phone,
        "line1": addr.line1,
        "line2": addr.line2,
        "landmark": addr.landmark,
        "city": addr.city,
        "state": addr.state,
        "postalCode": addr.postal_code,
        "country": addr.country,
    }


def _to_address_out(addr: Address) -> AddressOut:
    """Convert Address ORM to AddressOut schema."""
    return AddressOut(
        id=addr.id,
        user_id=addr.user_id,
        name=addr.name,
        phone=addr.phone,
        line1=addr.line1,
        line2=addr.line2,
        landmark=addr.landmark,
        city=addr.city,
        state=addr.state,
        postal_code=addr.postal_code,
        country=addr.country,
        is_default=addr.is_default,
        created_at=addr.created_at.isoformat() if addr.created_at else "",
    )


def _to_order_out(order: Order) -> OrderOut:
    """Convert Order ORM to OrderOut schema with dual currency."""
    items_out = [
        OrderItemOut(
            id=item.id,
            order_id=item.order_id,
            product_id=item.product_id,
            product_variant_id=item.product_variant_id,
            product_name=item.product_name,
            product_slug=item.product_slug,
            sku=item.sku,
            variant_name=item.variant_name,
            product_image=build_image_url(item.product_image),
            unit_price=item.unit_price,
            unit_price_paise=item.unit_price * 100,
            quantity=item.quantity,
            line_total=item.line_total,
            line_total_paise=item.line_total * 100,
            personalization=item.personalization_json or {},
        )
        for item in order.items
    ]

    history_out = [
        OrderStatusHistoryOut(
            id=h.id,
            status=h.status,
            note=h.note,
            timestamp=h.timestamp.isoformat() if h.timestamp else "",
        )
        for h in order.status_history
    ]

    return OrderOut(
        id=order.id,
        order_number=order.order_number,
        user_id=order.user_id,
        customer_name=order.customer_name,
        customer_phone=order.customer_phone,
        customer_email=order.customer_email,
        shipping_address=order.shipping_address_json or {},
        billing_address=order.billing_address_json or order.shipping_address_json or {},
        status=order.status,
        payment_status=order.payment_status,
        payment_method=order.payment_method,
        currency=order.currency or "INR",
        subtotal=order.subtotal,
        subtotal_paise=order.subtotal * 100,
        shipping_fee=order.shipping_fee,
        shipping_fee_paise=order.shipping_fee * 100,
        discount_amount=order.discount_amount,
        discount_amount_paise=order.discount_amount * 100,
        tax_amount=order.tax_amount,
        tax_amount_paise=order.tax_amount * 100,
        total_amount=order.total_amount,
        total_amount_paise=order.total_amount * 100,
        notes=order.notes,
        items=items_out,
        status_history=history_out,
        tracking_number=order.tracking_number,
        courier_name=order.courier_name,
        estimated_delivery=order.estimated_delivery.isoformat() if order.estimated_delivery else None,
        created_at=order.created_at.isoformat() if order.created_at else "",
        updated_at=order.updated_at.isoformat() if order.updated_at else "",
    )


# =============================================================================
# Address Management Endpoints (Section 26)
# =============================================================================

@router.get("/addresses", response_model=list[AddressOut])
def list_addresses(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[AddressOut]:
    """Retrieve saved delivery addresses for the authenticated customer."""
    addresses = (
        db.query(Address)
        .filter(Address.user_id == user.id)
        .order_by(Address.is_default.desc(), Address.id.desc())
        .all()
    )
    return [_to_address_out(a) for a in addresses]


@router.post("/addresses", response_model=AddressOut, status_code=status.HTTP_201_CREATED)
def create_address(
    address_in: AddressCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AddressOut:
    """Save a new delivery address for the authenticated customer."""
    existing_count = db.query(Address).filter(Address.user_id == user.id).count()

    is_default = address_in.is_default
    if existing_count == 0:
        is_default = True
    elif is_default:
        db.query(Address).filter(Address.user_id == user.id).update({"is_default": False})

    address = Address(
        user_id=user.id,
        name=address_in.name,
        phone=address_in.phone,
        line1=address_in.line1,
        line2=address_in.line2,
        landmark=address_in.landmark,
        city=address_in.city,
        state=address_in.state,
        postal_code=address_in.postal_code,
        country=address_in.country,
        is_default=is_default,
    )
    db.add(address)
    db.commit()
    db.refresh(address)
    return _to_address_out(address)


@router.patch("/addresses/{address_id}", response_model=AddressOut)
def update_address(
    address_id: int,
    address_in: AddressUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AddressOut:
    """Update an existing delivery address belonging to the authenticated customer."""
    address = (
        db.query(Address)
        .filter(Address.id == address_id, Address.user_id == user.id)
        .first()
    )
    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found",
        )

    update_data = address_in.model_dump(exclude_unset=True)
    if update_data.get("is_default") is True:
        db.query(Address).filter(Address.user_id == user.id).update({"is_default": False})

    for field, value in update_data.items():
        setattr(address, field, value)

    address.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(address)
    return _to_address_out(address)


@router.delete("/addresses/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_address(
    address_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """Delete a saved delivery address."""
    address = (
        db.query(Address)
        .filter(Address.id == address_id, Address.user_id == user.id)
        .first()
    )
    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found",
        )

    was_default = address.is_default
    db.delete(address)
    db.commit()

    # Reassign default address if the deleted one was default
    if was_default:
        next_addr = db.query(Address).filter(Address.user_id == user.id).first()
        if next_addr:
            next_addr.is_default = True
            db.commit()


@router.post("/addresses/{address_id}/default", response_model=AddressOut)
def set_default_address(
    address_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AddressOut:
    """Set an address as the default delivery address."""
    address = (
        db.query(Address)
        .filter(Address.id == address_id, Address.user_id == user.id)
        .first()
    )
    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found",
        )

    db.query(Address).filter(Address.user_id == user.id).update({"is_default": False})
    address.is_default = True
    db.commit()
    db.refresh(address)
    return _to_address_out(address)


# =============================================================================
# Order & Checkout Endpoints (Section 18 & 20)
# =============================================================================

@router.post("/orders", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def checkout(
    order_in: OrderCreate,
    background_tasks: BackgroundTasks,
    user: User | None = Depends(get_optional_current_user),
    cart_token: str | None = Depends(_get_cart_token),
    db: Session = Depends(get_db),
) -> OrderOut:
    """Convert the current shopping cart into a placed order.

    Snapshots products, variant details, prices, and shipping address.
    Decrements inventory, clears active cart items, and logs initial status history.
    """
    now = datetime.now(timezone.utc)

    # 1. Resolve active cart
    cart = None
    if user:
        cart = (
            db.query(Cart)
            .options(
                joinedload(Cart.items)
                .joinedload(CartItem.variant)
                .joinedload(ProductVariant.product)
            )
            .filter(Cart.user_id == user.id, Cart.status == "ACTIVE")
            .first()
        )

    if not cart and cart_token:
        cart = (
            db.query(Cart)
            .options(
                joinedload(Cart.items)
                .joinedload(CartItem.variant)
                .joinedload(ProductVariant.product)
            )
            .filter(Cart.guest_token == cart_token, Cart.status == "ACTIVE")
            .first()
        )

    if not cart or not cart.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Your cart is empty. Add items before checking out.",
        )

    # 2. Resolve and snapshot shipping address
    shipping_address_data = None
    customer_name = order_in.customer_name
    customer_phone = order_in.customer_phone
    customer_email = order_in.customer_email

    if order_in.address_id:
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Login required to use saved addresses",
            )
        saved_addr = (
            db.query(Address)
            .filter(Address.id == order_in.address_id, Address.user_id == user.id)
            .first()
        )
        if not saved_addr:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Saved address with ID {order_in.address_id} not found",
            )
        shipping_address_data = _address_to_dict(saved_addr)
        customer_name = customer_name or saved_addr.name
        customer_phone = customer_phone or saved_addr.phone
    elif order_in.shipping_address:
        addr = order_in.shipping_address
        shipping_address_data = {
            "name": addr.name,
            "phone": addr.phone,
            "line1": addr.line1,
            "line2": addr.line2,
            "landmark": addr.landmark,
            "city": addr.city,
            "state": addr.state,
            "postalCode": addr.postal_code,
            "country": addr.country,
        }
        customer_name = customer_name or addr.name
        customer_phone = customer_phone or addr.phone
    elif user:
        default_addr = (
            db.query(Address)
            .filter(Address.user_id == user.id, Address.is_default == True)
            .first()
        )
        if default_addr:
            shipping_address_data = _address_to_dict(default_addr)
            customer_name = customer_name or default_addr.name
            customer_phone = customer_phone or default_addr.phone

    if not shipping_address_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A shipping address is required to place an order.",
        )

    # Fallbacks for contact info
    if user:
        customer_name = customer_name or user.name or "Valued Customer"
        customer_phone = customer_phone or user.phone or shipping_address_data.get("phone", "")
        customer_email = customer_email or user.email
    else:
        customer_name = customer_name or shipping_address_data.get("name", "Guest Customer")
        customer_phone = customer_phone or shipping_address_data.get("phone", "")

    if not customer_phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer phone number is required for shipping updates.",
        )

    # 3. Validate variant stock and compute prices
    subtotal = 0
    for cart_item in cart.items:
        variant = cart_item.variant
        if not variant or variant.status != "ACTIVE":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"An item in your cart is no longer available.",
            )
        if variant.stock_quantity < cart_item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Insufficient stock for '{variant.product.name} ({variant.name})'. "
                    f"Available: {variant.stock_quantity}, In cart: {cart_item.quantity}"
                ),
            )
        subtotal += variant.price * cart_item.quantity

    # 3b. Validate and calculate promo coupon discount if supplied
    discount_amount = 0
    if order_in.coupon_code:
        code_clean = order_in.coupon_code.strip().upper()
        coupon = db.query(Coupon).filter(Coupon.code == code_clean, Coupon.is_active.is_(True)).first()
        if not coupon:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Coupon '{order_in.coupon_code}' is invalid or inactive.",
            )
        if coupon.valid_until:
            v_until = coupon.valid_until.replace(tzinfo=timezone.utc) if coupon.valid_until.tzinfo is None else coupon.valid_until
            if now > v_until:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Coupon has expired.")
        if coupon.usage_limit is not None and coupon.usage_count >= coupon.usage_limit:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Coupon usage limit reached.")
        if subtotal < coupon.min_order_amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Minimum order amount for coupon '{coupon.code}' is ₹{coupon.min_order_amount}.",
            )
        if coupon.discount_type == "PERCENTAGE":
            discount_amount = (subtotal * coupon.discount_value) // 100
            if coupon.max_discount_amount:
                discount_amount = min(discount_amount, coupon.max_discount_amount)
        else:
            discount_amount = min(coupon.discount_value, subtotal)
        coupon.usage_count += 1

    # Free shipping on orders ₹999 and above, otherwise ₹99
    shipping_fee = 0 if subtotal >= 999 else 99
    total_amount = max(0, subtotal - discount_amount) + shipping_fee

    # 4. Generate unique readable order number (CB-YYYYMMDD-XXXX)
    date_str = now.strftime("%Y%m%d")
    rand_suffix = secrets.token_hex(2).upper()
    order_number = f"CB-{date_str}-{rand_suffix}"

    # 5. Order and Payment Status
    payment_method_str = order_in.payment_method.upper()
    if payment_method_str == "COD":
        order_status = OrderStatus.CONFIRMED.value
        payment_status = PaymentStatus.PENDING.value
        history_note = "Order confirmed with Cash on Delivery."
    else:
        order_status = OrderStatus.PENDING_PAYMENT.value
        payment_status = PaymentStatus.PENDING.value
        history_note = f"Order placed with {payment_method_str}. Awaiting payment confirmation."

    # 6. Create Order entity
    order = Order(
        order_number=order_number,
        user_id=user.id if user else None,
        customer_name=customer_name,
        customer_phone=customer_phone,
        customer_email=customer_email,
        shipping_address_json=shipping_address_data,
        billing_address_json=shipping_address_data,
        status=order_status,
        payment_status=payment_status,
        payment_method=payment_method_str,
        currency="INR",
        subtotal=subtotal,
        shipping_fee=shipping_fee,
        discount_amount=discount_amount,
        tax_amount=0,
        total_amount=total_amount,
        notes=order_in.notes,
        courier_name="BlueDart Express",
        tracking_number=f"SULO-EXP-{secrets.token_hex(3).upper()}",
        estimated_delivery=now + timedelta(days=5),
        created_at=now,
        updated_at=now,
    )
    db.add(order)
    db.flush()

    # 7. Snapshot items & decrement inventory
    for cart_item in cart.items:
        variant = cart_item.variant
        product = variant.product
        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            product_variant_id=variant.id,
            product_name=product.name,
            product_slug=product.slug,
            sku=variant.sku,
            variant_name=variant.name,
            product_image=product.primary_image,
            unit_price=variant.price,
            quantity=cart_item.quantity,
            line_total=variant.price * cart_item.quantity,
            personalization_json=cart_item.personalization_json or {},
            created_at=now,
        )
        db.add(order_item)
        # Decrement stock
        variant.stock_quantity = max(0, variant.stock_quantity - cart_item.quantity)

    # 8. Record initial status history
    history = OrderStatusHistory(
        order_id=order.id,
        status=order_status,
        note=history_note,
        timestamp=now,
    )
    db.add(history)

    # 9. Clear cart
    for cart_item in cart.items:
        db.delete(cart_item)
    cart.status = "CONVERTED"

    db.commit()
    db.refresh(order)
    background_tasks.add_task(dispatch_order_placed_background, order.id)
    return _to_order_out(order)


@router.get("/orders", response_model=list[OrderOut])
def list_orders(
    response: Response,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[OrderOut]:
    """Retrieve order history for the authenticated customer."""
    query = (
        db.query(Order)
        .options(
            joinedload(Order.items),
            joinedload(Order.status_history),
        )
        .filter(Order.user_id == user.id)
        .order_by(Order.created_at.desc())
    )

    total_count = query.count()
    response.headers["X-Total-Count"] = str(total_count)

    orders = query.offset(offset).limit(limit).all()
    return [_to_order_out(o) for o in orders]


@router.get("/orders/{order_id_or_number}", response_model=OrderOut)
def get_order_detail(
    order_id_or_number: str,
    user: User | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
) -> OrderOut:
    """Retrieve full details of an order.

    Conforms to Section 22 security: verifies customer authorization.
    """
    query = (
        db.query(Order)
        .options(
            joinedload(Order.items),
            joinedload(Order.status_history),
        )
    )

    if order_id_or_number.isdigit():
        order = query.filter(Order.id == int(order_id_or_number)).first()
    else:
        order = query.filter(Order.order_number == order_id_or_number).first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order '{order_id_or_number}' not found",
        )

    # Authorization verification
    if order.user_id is not None:
        if not user or user.id != order.user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order '{order_id_or_number}' not found",
            )

    return _to_order_out(order)


@router.get("/orders/{order_id_or_number}/tracking", response_model=OrderTrackingOut)
def get_order_tracking(
    order_id_or_number: str,
    user: User | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
) -> OrderTrackingOut:
    """Retrieve order tracking status and chronological timeline history."""
    query = (
        db.query(Order)
        .options(
            joinedload(Order.status_history),
        )
    )

    if order_id_or_number.isdigit():
        order = query.filter(Order.id == int(order_id_or_number)).first()
    else:
        order = query.filter(Order.order_number == order_id_or_number).first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order '{order_id_or_number}' not found",
        )

    if order.user_id is not None:
        if not user or user.id != order.user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order '{order_id_or_number}' not found",
            )

    timeline_out = [
        OrderStatusHistoryOut(
            id=h.id,
            status=h.status,
            note=h.note,
            timestamp=h.timestamp.isoformat() if h.timestamp else "",
        )
        for h in order.status_history
    ]

    return OrderTrackingOut(
        order_number=order.order_number,
        status=order.status,
        payment_status=order.payment_status,
        tracking_number=order.tracking_number,
        courier_name=order.courier_name,
        estimated_delivery=order.estimated_delivery.isoformat() if order.estimated_delivery else None,
        timeline=timeline_out,
    )


@router.post("/orders/{order_id_or_number}/cancel", response_model=OrderOut)
def cancel_order(
    order_id_or_number: str,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OrderOut:
    """Cancel an order before shipping, restoring inventory and recording cancellation in history."""
    query = (
        db.query(Order)
        .options(
            joinedload(Order.items),
            joinedload(Order.status_history),
        )
    )

    if order_id_or_number.isdigit():
        order = query.filter(Order.id == int(order_id_or_number)).first()
    else:
        order = query.filter(Order.order_number == order_id_or_number).first()

    if not order or order.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order '{order_id_or_number}' not found",
        )

    # Only allow cancellation if order has not been dispatched yet
    cancellable_statuses = [
        OrderStatus.PENDING_PAYMENT.value,
        OrderStatus.CONFIRMED.value,
        OrderStatus.PROCESSING.value,
        OrderStatus.PAID.value,
    ]
    if order.status not in cancellable_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Order in '{order.status}' status cannot be cancelled.",
        )

    now = datetime.now(timezone.utc)
    order.status = OrderStatus.CANCELLED.value
    order.updated_at = now

    # Restore inventory
    for item in order.items:
        if item.product_variant_id:
            variant = (
                db.query(ProductVariant)
                .filter(ProductVariant.id == item.product_variant_id)
                .first()
            )
            if variant:
                variant.stock_quantity += item.quantity

    # Add cancellation history
    history = OrderStatusHistory(
        order_id=order.id,
        status=OrderStatus.CANCELLED.value,
        note="Order cancelled by customer.",
        timestamp=now,
    )
    db.add(history)

    db.commit()
    db.refresh(order)
    background_tasks.add_task(dispatch_order_status_background, order.id, OrderStatus.CANCELLED.value)
    return _to_order_out(order)
