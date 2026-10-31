"""Payment API endpoints.

Conforms to Section 25 (Payment Architecture) and Milestone 7 of the Specification.
"""

from datetime import datetime, timezone
from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session, joinedload

from app.api.v1.auth import get_optional_current_user
from app.db.session import get_db
from app.models.order import Order, OrderStatus, OrderStatusHistory, PaymentStatus
from app.models.payment import Payment, PaymentRecordStatus
from app.models.user import User
from app.services.guest_tracking import validate_guest_order_token
from app.services.notification import (
    dispatch_order_placed_background,
    dispatch_payment_confirmed_background,
)
from app.schemas.payment import (
    PaymentIntentCreate,
    PaymentIntentOut,
    PaymentOut,
    PaymentRetryRequest,
    PaymentVerifyRequest,
    PaymentWebhookResult,
)
from app.services.payment import (
    get_payment_provider,
    PaymentGatewayConfigurationError,
    PaymentGatewayError,
)

router = APIRouter(prefix="/payments", tags=["payments"])

_FORBIDDEN_QUERY_TOKEN_KEYS = {
    "token",
    "guestordertoken",
    "guest_order_token",
    "guesttrackingtoken",
    "guest_tracking_token",
}


def _is_order_retry_eligible(order: Order | None, payment: Payment | None = None) -> bool:
    """Return True only when authoritative server state allows a new payment attempt for the order."""
    if not order:
        return False
    if order.payment_status in (
        PaymentStatus.PAID.value,
        PaymentStatus.REFUNDED.value,
        "PARTIALLY_REFUNDED",
    ):
        return False
    if order.status != OrderStatus.PENDING_PAYMENT.value:
        return False
    if (order.payment_method or "").strip().upper() == "COD":
        return False
    if payment is not None and payment.status == PaymentRecordStatus.SUCCESS.value:
        return False
    if any(p.status == PaymentRecordStatus.SUCCESS.value for p in (order.payments or [])):
        return False
    return True


def _to_payment_out(payment: Payment, verification_state: str | None = None) -> PaymentOut:
    """Convert Payment ORM to PaymentOut schema."""
    order = payment.order
    resolved_verification_state = (
        verification_state
        or getattr(payment, "_verification_state", None)
        or payment.status
    )
    return PaymentOut(
        id=payment.id,
        order_id=payment.order_id,
        order_number=order.order_number if order else None,
        order_status=order.status if order else None,
        order_payment_status=order.payment_status if order else None,
        provider=payment.provider,
        provider_payment_id=payment.provider_payment_id,
        provider_order_id=payment.provider_order_id,
        amount=payment.amount,
        amount_paise=payment.amount_paise,
        currency=payment.currency or "INR",
        status=payment.status,
        verification_state=resolved_verification_state,
        can_retry=_is_order_retry_eligible(order, payment),
        error_message=payment.error_message,
        payment_method_detail=payment.payment_method_detail,
        created_at=payment.created_at.isoformat() if payment.created_at else "",
        updated_at=payment.updated_at.isoformat() if payment.updated_at else "",
    )


def _extract_guest_capability(
    body_guest_token: str | None = None,
    body_tracking_token: str | None = None,
    header_guest_token: str | None = None,
    authorization: str | None = None,
    user: User | None = None,
) -> str | None:
    """Extract guest order capability token from request body or headers (never query params)."""
    for candidate in (body_guest_token, body_tracking_token, header_guest_token):
        if candidate and candidate.strip():
            return candidate.strip()
    if user is None and authorization and authorization.startswith("Bearer "):
        bearer_val = authorization.removeprefix("Bearer ").strip()
        if bearer_val:
            return bearer_val
    return None


def _authorize_order_payment_access(
    db: Session,
    order: Order,
    user: User | None,
    guest_token: str | None,
    request: Request | None = None,
    not_found_detail: str = "Order not found.",
) -> None:
    """Enforce owner or guest-capability authorization with non-enumerating 404 on failure."""
    if request is not None:
        query_keys = {k.strip().lower() for k in request.query_params.keys()}
        if query_keys & _FORBIDDEN_QUERY_TOKEN_KEYS:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=not_found_detail,
            )

    if order.user_id is not None:
        if not user or user.id != order.user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=not_found_detail,
            )
    else:
        if not guest_token or not validate_guest_order_token(db, order.id, guest_token):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=not_found_detail,
            )


def _reconcile_confirmed_payment(
    db: Session,
    order: Order,
    payment: Payment,
    now: datetime,
    background_tasks: BackgroundTasks | None = None,
) -> None:
    """Transition payment and order to confirmed/paid state idempotently."""
    resolved_payment_id = payment.provider_payment_id or payment.provider_order_id
    payment.status = PaymentRecordStatus.SUCCESS.value
    payment.provider_payment_id = resolved_payment_id
    payment.error_message = None
    payment.updated_at = now

    already_paid = order.payment_status == PaymentStatus.PAID.value
    order.payment_status = PaymentStatus.PAID.value
    if order.status == OrderStatus.PENDING_PAYMENT.value:
        order.status = OrderStatus.CONFIRMED.value
    if not order.tracking_number:
        import secrets
        order.tracking_number = f"SLC-LOCAL-{secrets.token_hex(3).upper()}"
        order.courier_name = "Sulocraft Local Express"
    if not order.estimated_delivery:
        from datetime import timedelta
        order.estimated_delivery = now + timedelta(days=5)
    order.updated_at = now

    if not already_paid:
        history = OrderStatusHistory(
            order_id=order.id,
            status=OrderStatus.CONFIRMED.value,
            note=f"Payment of ₹{payment.amount} verified via {payment.provider.upper()} ({resolved_payment_id}).",
            timestamp=now,
        )
        db.add(history)

    db.commit()
    db.refresh(payment)
    if not already_paid and background_tasks is not None:
        background_tasks.add_task(dispatch_order_placed_background, order.id)
        background_tasks.add_task(dispatch_payment_confirmed_background, order.id, payment.id)


def _issue_order_payment_intent(
    db: Session,
    order: Order,
    provider_name: str | None,
    background_tasks: BackgroundTasks | None = None,
) -> PaymentIntentOut:
    """Validate order retry eligibility and create a new server-derived payment attempt."""
    if order.payment_status == PaymentStatus.PAID.value or any(
        p.status == PaymentRecordStatus.SUCCESS.value for p in (order.payments or [])
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This order has already been paid.",
        )

    if order.status == OrderStatus.CANCELLED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot pay for a cancelled order.",
        )

    if order.status != OrderStatus.PENDING_PAYMENT.value or (order.payment_method or "").strip().upper() == "COD":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This order is not eligible for online payment retry.",
        )

    try:
        provider = get_payment_provider(provider_name)
    except (PaymentGatewayConfigurationError, PaymentGatewayError, RuntimeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Payment gateway error: {str(exc)}",
        )

    now = datetime.now(timezone.utc)

    # Safe pending-attempt policy: if a prior Cashfree attempt is still PENDING, check whether
    # the gateway has already confirmed it as PAID before issuing a new session.
    if provider.provider_name == "cashfree":
        for prev_payment in order.payments or []:
            if (
                prev_payment.status == PaymentRecordStatus.PENDING.value
                and prev_payment.provider == "cashfree"
                and prev_payment.provider_order_id
            ):
                if provider.verify_payment(
                    prev_payment,
                    {"provider_order_id": prev_payment.provider_order_id},
                ):
                    _reconcile_confirmed_payment(db, order, prev_payment, now, background_tasks)
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="This order has already been paid.",
                    )

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

    try:
        intent_data = provider.create_intent(order, payment)
    except (PaymentGatewayConfigurationError, PaymentGatewayError) as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Payment gateway error: {str(exc)}",
        )

    # Supersede any prior unresolved PENDING attempts for this order now that a fresh attempt exists
    for prev_payment in order.payments or []:
        if prev_payment.id != payment.id and prev_payment.status == PaymentRecordStatus.PENDING.value:
            prev_payment.status = PaymentRecordStatus.FAILED.value
            prev_payment.error_message = "Superseded by a new payment retry attempt."
            prev_payment.updated_at = now

    db.commit()
    db.refresh(payment)

    return PaymentIntentOut(
        payment_id=payment.id,
        order_id=order.id,
        order_number=order.order_number,
        provider=provider.provider_name,
        provider_order_id=intent_data.get("providerOrderId"),
        payment_session_id=intent_data.get("paymentSessionId"),
        environment=intent_data.get("environment"),
        return_url=intent_data.get("returnUrl"),
        amount=payment.amount,
        amount_paise=payment.amount_paise,
        currency=payment.currency,
        key_id=intent_data.get("keyId"),
        notes=intent_data.get("notes", {}),
    )


@router.post("/intent", response_model=PaymentIntentOut, status_code=status.HTTP_201_CREATED)
def create_payment_intent(
    payload: PaymentIntentCreate,
    request: Request,
    background_tasks: BackgroundTasks,
    x_guest_order_token: str | None = Header(default=None, alias="X-Guest-Order-Token"),
    authorization: str | None = Header(default=None),
    user: User | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
) -> PaymentIntentOut:
    """Create or retry a gateway payment intent/order for an eligible unpaid order."""
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

    guest_token = _extract_guest_capability(
        body_guest_token=payload.guest_order_token,
        body_tracking_token=payload.guest_tracking_token,
        header_guest_token=x_guest_order_token,
        authorization=authorization,
        user=user,
    )
    _authorize_order_payment_access(
        db=db,
        order=order,
        user=user,
        guest_token=guest_token,
        request=request,
        not_found_detail="Order not found.",
    )

    return _issue_order_payment_intent(
        db=db,
        order=order,
        provider_name=payload.provider,
        background_tasks=background_tasks,
    )


@router.post("/{payment_id}/retry", response_model=PaymentIntentOut, status_code=status.HTTP_201_CREATED)
def retry_payment_intent(
    payment_id: int,
    request: Request,
    background_tasks: BackgroundTasks,
    payload: PaymentRetryRequest | None = None,
    x_guest_order_token: str | None = Header(default=None, alias="X-Guest-Order-Token"),
    authorization: str | None = Header(default=None),
    user: User | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
) -> PaymentIntentOut:
    """Create a new payment attempt for the same unpaid order after a failed or pending attempt."""
    payment = (
        db.query(Payment)
        .options(joinedload(Payment.order).joinedload(Order.payments))
        .filter(Payment.id == payment_id)
        .first()
    )
    if not payment or not payment.order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment record not found.",
        )

    order = payment.order
    guest_token = _extract_guest_capability(
        body_guest_token=payload.guest_order_token if payload else None,
        body_tracking_token=payload.guest_tracking_token if payload else None,
        header_guest_token=x_guest_order_token,
        authorization=authorization,
        user=user,
    )
    _authorize_order_payment_access(
        db=db,
        order=order,
        user=user,
        guest_token=guest_token,
        request=request,
        not_found_detail="Payment record not found.",
    )

    provider_name = (payload.provider if payload and payload.provider else None) or payment.provider
    return _issue_order_payment_intent(
        db=db,
        order=order,
        provider_name=provider_name,
        background_tasks=background_tasks,
    )


@router.post("/verify", response_model=PaymentOut)
def verify_payment(
    payload: PaymentVerifyRequest,
    background_tasks: BackgroundTasks,
    user: User | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
) -> PaymentOut | JSONResponse:
    """Verify payment completion callback or redirect from client gateway.

    On success, transitions Payment status to SUCCESS, Order payment_status to PAID,
    Order status to CONFIRMED, and records audit history.
    """
    payment = (
        db.query(Payment)
        .options(joinedload(Payment.order).joinedload(Order.payments))
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

    # Strict order binding & guest authorization:
    # Guest payments (user_id is None) require the server-issued provider_order_id nonce
    # before any idempotent return or gateway check, and mismatched/missing bindings
    # must never mutate stored payment/order state.
    supplied_order_id = (payload.provider_order_id or "").strip()
    expected_order_id = (payment.provider_order_id or "").strip()
    if order.user_id is None:
        if not expected_order_id or not supplied_order_id or supplied_order_id != expected_order_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment verification failed. Mismatched order binding.",
            )
    elif supplied_order_id and expected_order_id and supplied_order_id != expected_order_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment verification failed. Mismatched order binding.",
        )

    # Idempotent: already marked success
    if payment.status == PaymentRecordStatus.SUCCESS.value:
        return _to_payment_out(payment, verification_state="SUCCESS")

    try:
        provider = get_payment_provider(payment.provider)
    except (PaymentGatewayConfigurationError, PaymentGatewayError, RuntimeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment verification failed. Gateway configuration unavailable.",
        )

    is_valid = provider.verify_payment(payment, payload.model_dump())

    now = datetime.now(timezone.utc)
    if not is_valid:
        verification_state = getattr(payment, "_verification_state", "FAILED")
        if verification_state == "PENDING":
            payment.status = PaymentRecordStatus.PENDING.value
            payment.error_message = "Payment is still pending confirmation with gateway."
            payment.updated_at = now
            db.commit()
            db.refresh(payment)
            detail_msg = "Payment verification failed. Transaction is still pending with the payment gateway."
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    **_to_payment_out(payment, verification_state="PENDING").model_dump(by_alias=True),
                    "detail": detail_msg,
                },
            )

        payment.status = PaymentRecordStatus.FAILED.value
        custom_fail_msg = getattr(payment, "_verification_message", None)
        payment.error_message = custom_fail_msg or "Gateway signature or transaction verification failed."
        payment.updated_at = now
        db.commit()
        db.refresh(payment)
        detail_msg = "Payment verification failed. Invalid signature or unconfirmed transaction."
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                **_to_payment_out(payment, verification_state="FAILED").model_dump(by_alias=True),
                "detail": detail_msg,
            },
        )

    resolved_payment_id = payload.provider_payment_id or payment.provider_payment_id
    payment.provider_payment_id = resolved_payment_id
    if not payment.provider_order_id and payload.provider_order_id:
        payment.provider_order_id = payload.provider_order_id
    if payload.payment_method_detail:
        payment.payment_method_detail = payload.payment_method_detail

    _reconcile_confirmed_payment(db, order, payment, now, background_tasks)
    return _to_payment_out(payment, verification_state="SUCCESS")


@router.post("/webhook/{provider}", response_model=PaymentWebhookResult)
async def payment_webhook(
    provider: str,
    request: Request,
    background_tasks: BackgroundTasks,
    x_webhook_signature: str | None = Header(default=None),
    x_webhook_timestamp: str | None = Header(default=None),
    x_razorpay_signature: str | None = Header(default=None),
    x_signature: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> PaymentWebhookResult:
    """Gateway webhook handler for asynchronous payment updates."""
    import json

    body_bytes = await request.body()
    try:
        provider_instance = get_payment_provider(provider)
    except (PaymentGatewayConfigurationError, PaymentGatewayError, RuntimeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported webhook payment provider.",
        )

    if provider_instance.provider_name == "cashfree":
        signature = x_webhook_signature or x_signature or ""
    elif provider_instance.provider_name == "razorpay":
        signature = x_razorpay_signature or x_signature or ""
    else:
        signature = x_webhook_signature or x_razorpay_signature or x_signature or ""

    if not provider_instance.verify_webhook(body_bytes, signature, timestamp=x_webhook_timestamp):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid webhook signature.",
        )

    try:
        data = json.loads(body_bytes.decode("utf-8"))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Malformed webhook JSON payload.",
        )

    if not isinstance(data, dict):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Webhook payload must be a JSON object.",
        )

    # Extract standardized fields across Cashfree, Razorpay, and Mock formats
    cf_data = data.get("data") if isinstance(data.get("data"), dict) else {}
    cf_order = cf_data.get("order") if isinstance(cf_data.get("order"), dict) else {}
    cf_payment = cf_data.get("payment") if isinstance(cf_data.get("payment"), dict) else {}

    payment_entity = data.get("payload", {}).get("payment", {}).get("entity", {})
    if not isinstance(payment_entity, dict):
        payment_entity = {}

    provider_order_id = (
        cf_order.get("order_id")
        or payment_entity.get("order_id")
        or data.get("provider_order_id")
        or data.get("order_id")
    )
    provider_payment_id = (
        cf_payment.get("cf_payment_id")
        or payment_entity.get("id")
        or data.get("provider_payment_id")
    )
    if provider_payment_id is not None:
        provider_payment_id = str(provider_payment_id)

    event_type = str(data.get("type") or data.get("event") or "").strip().lower()
    cf_payment_status = str(cf_payment.get("payment_status") or "").strip().upper()

    if not provider_order_id:
        return PaymentWebhookResult(status="ok", message="Webhook acknowledged (no order reference).")

    payment = (
        db.query(Payment)
        .options(joinedload(Payment.order))
        .filter(Payment.provider_order_id == str(provider_order_id))
        .first()
    )
    if not payment:
        return PaymentWebhookResult(status="ok", message="Webhook acknowledged.")

    # Strict provider isolation: a mock or razorpay webhook can never reconcile a cashfree payment
    if (payment.provider or "").strip().lower() != provider_instance.provider_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Webhook provider does not match stored payment provider.",
        )

    # Verify currency & amount when provided in webhook payload
    expected_currency = (payment.currency or "INR").upper()
    webhook_currency = (
        cf_payment.get("payment_currency")
        or cf_order.get("order_currency")
        or payment_entity.get("currency")
    )
    if webhook_currency and str(webhook_currency).strip().upper() != expected_currency:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Webhook payment currency mismatch.",
        )

    if cf_payment.get("payment_amount") is not None or cf_order.get("order_amount") is not None:
        raw_cf_amt = cf_payment.get("payment_amount", cf_order.get("order_amount"))
        try:
            webhook_amount_paise = round(float(raw_cf_amt) * 100)
        except (TypeError, ValueError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid webhook payment amount.",
            )
        if webhook_amount_paise != int(payment.amount_paise):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Webhook payment amount mismatch.",
            )
    elif payment_entity.get("amount") is not None:
        try:
            if int(payment_entity.get("amount")) != int(payment.amount_paise):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Webhook payment amount mismatch.",
                )
        except (TypeError, ValueError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid webhook payment amount.",
            )

    order = payment.order
    now = datetime.now(timezone.utc)

    is_success_event = (
        (provider_instance.provider_name == "cashfree" and (
            event_type == "payment_success_webhook" or cf_payment_status == "SUCCESS"
        ) and cf_payment_status in ("SUCCESS", ""))
        or (provider_instance.provider_name != "cashfree" and (
            "captured" in event_type or "success" in event_type or (not event_type and bool(provider_payment_id))
        ))
    )
    is_failed_event = (
        "failed" in event_type
        or "dropped" in event_type
        or cf_payment_status in ("FAILED", "USER_DROPPED", "CANCELLED")
    )

    if is_success_event:
        # Idempotency guard: if already reconciled, do not duplicate state transitions or notifications
        if payment.status == PaymentRecordStatus.SUCCESS.value or order.payment_status == PaymentStatus.PAID.value:
            return PaymentWebhookResult(status="ok", message="Webhook processed idempotently.")

        payment.status = PaymentRecordStatus.SUCCESS.value
        payment.provider_payment_id = provider_payment_id or payment.provider_payment_id or str(provider_order_id)
        payment.error_message = None
        if cf_payment.get("payment_group") and not payment.payment_method_detail:
            payment.payment_method_detail = f"Cashfree ({str(cf_payment['payment_group']).upper()})"
        payment.updated_at = now

        order.payment_status = PaymentStatus.PAID.value
        if order.status == OrderStatus.PENDING_PAYMENT.value:
            order.status = OrderStatus.CONFIRMED.value
        order.updated_at = now

        history = OrderStatusHistory(
            order_id=order.id,
            status=OrderStatus.CONFIRMED.value,
            note=f"Payment verified via {provider_instance.provider_name.upper()} webhook ({payment.provider_payment_id}).",
            timestamp=now,
        )
        db.add(history)
        db.commit()
        background_tasks.add_task(dispatch_order_placed_background, order.id)
        background_tasks.add_task(dispatch_payment_confirmed_background, order.id, payment.id)
    elif is_failed_event:
        # Out-of-order guard: never downgrade an already paid/confirmed order or succeeded payment
        if payment.status != PaymentRecordStatus.SUCCESS.value and order.payment_status != PaymentStatus.PAID.value:
            payment.status = PaymentRecordStatus.FAILED.value
            payment.error_message = str(
                cf_payment.get("payment_message") or "Payment failed or dropped per gateway webhook."
            )
            payment.updated_at = now
            db.commit()

    return PaymentWebhookResult(status="ok", message="Webhook processed successfully.")


@router.get("/{payment_id}", response_model=PaymentOut)
def get_payment(
    payment_id: int,
    request: Request,
    provider_order_id: str | None = Query(default=None, alias="providerOrderId"),
    x_guest_order_token: str | None = Header(default=None, alias="X-Guest-Order-Token"),
    authorization: str | None = Header(default=None),
    user: User | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
) -> PaymentOut:
    """Retrieve payment details."""
    query_keys = {k.strip().lower() for k in request.query_params.keys()}
    if query_keys & _FORBIDDEN_QUERY_TOKEN_KEYS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment record not found.",
        )

    payment = (
        db.query(Payment)
        .options(joinedload(Payment.order).joinedload(Order.payments))
        .filter(Payment.id == payment_id)
        .first()
    )
    if not payment or not payment.order:
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
    else:
        guest_token = _extract_guest_capability(
            header_guest_token=x_guest_order_token,
            authorization=authorization,
            user=user,
        )
        valid_token = bool(guest_token and validate_guest_order_token(db, order.id, guest_token))
        expected_order_id = (payment.provider_order_id or "").strip()
        supplied_order_id = (provider_order_id or "").strip()
        valid_binding = bool(expected_order_id and supplied_order_id and supplied_order_id == expected_order_id)
        if not (valid_token or valid_binding):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment record not found.",
            )

    return _to_payment_out(payment)
