"""Payment API endpoints.

Conforms to Section 25 (Payment Architecture) and Milestone 7 of the Specification.
"""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session, joinedload

from app.api.v1.auth import get_optional_current_user
from app.db.session import get_db
from app.models.order import Order, OrderStatus, OrderStatusHistory, PaymentStatus
from app.models.payment import Payment, PaymentRecordStatus
from app.models.user import User
from app.schemas.payment import (
    PaymentIntentCreate,
    PaymentIntentOut,
    PaymentOut,
    PaymentVerifyRequest,
    PaymentWebhookResult,
)
from app.services.payment.factory import get_payment_provider

router = APIRouter(prefix="/payments", tags=["payments"])


def _to_payment_out(payment: Payment) -> PaymentOut:
    """Convert Payment ORM to PaymentOut schema."""
    return PaymentOut(
        id=payment.id,
        order_id=payment.order_id,
        provider=payment.provider,
        provider_payment_id=payment.provider_payment_id,
        provider_order_id=payment.provider_order_id,
        amount=payment.amount,
        amount_paise=payment.amount_paise,
        currency=payment.currency or "INR",
        status=payment.status,
        payment_method_detail=payment.payment_method_detail,
        created_at=payment.created_at.isoformat() if payment.created_at else "",
        updated_at=payment.updated_at.isoformat() if payment.updated_at else "",
    )


@router.post("/intent", response_model=PaymentIntentOut, status_code=status.HTTP_201_CREATED)
def create_payment_intent(
    payload: PaymentIntentCreate,
    user: User | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
) -> PaymentIntentOut:
    """Create a gateway payment intent/order for an order."""
    query = db.query(Order).options(joinedload(Order.payments))

    if payload.order_id:
        order = query.filter(Order.id == payload.order_id).first()
    elif payload.order_number:
        order = query.filter(Order.order_number == payload.order_number).first()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either 'orderId' or 'orderNumber' is required.",
        )

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found.",
        )

    # Authorization verification
    if order.user_id is not None:
        if not user or user.id != order.user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found.",
            )

    if order.payment_status == PaymentStatus.PAID.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This order has already been paid.",
        )

    if order.status == OrderStatus.CANCELLED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot pay for a cancelled order.",
        )

    # Resolve payment provider
    provider = get_payment_provider(payload.provider)

    now = datetime.now(timezone.utc)
    payment = Payment(
        order_id=order.id,
        provider=provider.provider_name,
        amount=order.total_amount,
        amount_paise=order.total_amount * 100,
        currency=order.currency or "INR",
        status=PaymentRecordStatus.PENDING.value,
        created_at=now,
        updated_at=now,
    )
    db.add(payment)
    db.flush()

    intent_data = provider.create_intent(order, payment)
    db.commit()
    db.refresh(payment)

    return PaymentIntentOut(
        payment_id=payment.id,
        order_id=order.id,
        order_number=order.order_number,
        provider=provider.provider_name,
        provider_order_id=intent_data.get("providerOrderId"),
        amount=payment.amount,
        amount_paise=payment.amount_paise,
        currency=payment.currency,
        key_id=intent_data.get("keyId"),
        notes=intent_data.get("notes", {}),
    )


@router.post("/verify", response_model=PaymentOut)
def verify_payment(
    payload: PaymentVerifyRequest,
    user: User | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
) -> PaymentOut:
    """Verify payment completion callback from client gateway popup.

    On success, transitions Payment status to SUCCESS, Order payment_status to PAID,
    Order status to CONFIRMED, and records audit history.
    """
    payment = (
        db.query(Payment)
        .options(joinedload(Payment.order))
        .filter(Payment.id == payload.payment_id)
        .first()
    )
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment record not found.",
        )

    order = payment.order
    if order.user_id is not None:
        if not user or user.id != order.user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment record not found.",
            )

    # Idempotent: already marked success
    if payment.status == PaymentRecordStatus.SUCCESS.value:
        return _to_payment_out(payment)

    provider = get_payment_provider(payment.provider)
    is_valid = provider.verify_payment(payment, payload.model_dump())

    now = datetime.now(timezone.utc)
    if not is_valid:
        payment.status = PaymentRecordStatus.FAILED.value
        payment.error_message = "Gateway signature or transaction verification failed."
        payment.updated_at = now
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment verification failed. Invalid signature or unconfirmed transaction.",
        )

    # Success updates
    payment.status = PaymentRecordStatus.SUCCESS.value
    payment.provider_payment_id = payload.provider_payment_id
    if payload.provider_order_id:
        payment.provider_order_id = payload.provider_order_id
    if payload.payment_method_detail:
        payment.payment_method_detail = payload.payment_method_detail
    payment.updated_at = now

    order.payment_status = PaymentStatus.PAID.value
    order.status = OrderStatus.CONFIRMED.value
    order.updated_at = now

    history = OrderStatusHistory(
        order_id=order.id,
        status=OrderStatus.CONFIRMED.value,
        note=f"Payment of ₹{payment.amount} verified via {payment.provider.upper()} ({payload.provider_payment_id}).",
        timestamp=now,
    )
    db.add(history)

    db.commit()
    db.refresh(payment)
    return _to_payment_out(payment)


@router.post("/webhook/{provider}", response_model=PaymentWebhookResult)
async def payment_webhook(
    provider: str,
    request: Request,
    x_razorpay_signature: str | None = Header(default=None),
    x_signature: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> PaymentWebhookResult:
    """Gateway webhook handler for asynchronous payment updates."""
    body_bytes = await request.body()
    signature = x_razorpay_signature or x_signature or ""

    provider_instance = get_payment_provider(provider)
    if not provider_instance.verify_webhook(body_bytes, signature):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid webhook signature.",
        )

    try:
        data = await request.json()
    except Exception:
        data = {}

    event = data.get("event", "payment.captured")
    payment_entity = data.get("payload", {}).get("payment", {}).get("entity", {})
    provider_payment_id = payment_entity.get("id") or data.get("provider_payment_id")
    provider_order_id = payment_entity.get("order_id") or data.get("provider_order_id")

    if provider_order_id:
        payment = (
            db.query(Payment)
            .options(joinedload(Payment.order))
            .filter(Payment.provider_order_id == provider_order_id)
            .first()
        )
        if payment and payment.status != PaymentRecordStatus.SUCCESS.value:
            now = datetime.now(timezone.utc)
            if "captured" in event or "success" in event:
                payment.status = PaymentRecordStatus.SUCCESS.value
                payment.provider_payment_id = provider_payment_id or payment.provider_payment_id
                payment.updated_at = now

                order = payment.order
                order.payment_status = PaymentStatus.PAID.value
                order.status = OrderStatus.CONFIRMED.value
                order.updated_at = now

                history = OrderStatusHistory(
                    order_id=order.id,
                    status=OrderStatus.CONFIRMED.value,
                    note=f"Payment verified via gateway webhook ({provider_payment_id}).",
                    timestamp=now,
                )
                db.add(history)
                db.commit()

    return PaymentWebhookResult(status="ok", message="Webhook processed successfully.")


@router.get("/{payment_id}", response_model=PaymentOut)
def get_payment(
    payment_id: int,
    user: User | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
) -> PaymentOut:
    """Retrieve payment details."""
    payment = (
        db.query(Payment)
        .options(joinedload(Payment.order))
        .filter(Payment.id == payment_id)
        .first()
    )
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment record not found.",
        )

    order = payment.order
    if order.user_id is not None:
        if not user or user.id != order.user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment record not found.",
            )

    return _to_payment_out(payment)
