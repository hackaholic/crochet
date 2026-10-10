"""Service functions for read-only customer administration (Task 1.9.1)."""

from __future__ import annotations

import logging
from typing import Sequence

from fastapi import HTTPException, status
import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.user import User
from app.schemas.admin import AdminCustomerOut

logger = logging.getLogger(__name__)


def list_admin_customers(
    db: Session,
    q: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[AdminCustomerOut], int]:
    """Retrieve paginated customers with optional text search and order counts.

    Guarantees:
    - Only users with role 'CUSTOMER' are returned; admins are excluded.
    - Parameterized search across name, email, and phone.
    - Stable newest-first deterministic sorting (created_at desc nullslast, id desc).
    - Accurate total count of filtered matching customers.
    """
    clean_q = q.strip() if q else None
    if clean_q and len(clean_q) > 200:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Query cannot exceed 200 characters",
        )

    base_filters = [User.role == "CUSTOMER"]
    if clean_q:
        pattern = f"%{clean_q}%"
        base_filters.append(
            sa.or_(
                User.name.ilike(pattern),
                User.email.ilike(pattern),
                User.phone.ilike(pattern),
            )
        )

    # 1. Total matching count
    total = db.query(sa.func.count(User.id)).filter(*base_filters).scalar() or 0

    # 2. Correlated subquery for total linked orders per customer
    order_count_subquery = (
        db.query(sa.func.count(Order.id))
        .filter(Order.user_id == User.id)
        .scalar_subquery()
        .label("order_count")
    )

    # 3. Paginated customer rows
    rows = (
        db.query(User, order_count_subquery)
        .filter(*base_filters)
        .order_by(User.created_at.desc().nullslast(), User.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    items = [
        AdminCustomerOut(
            id=u.id,
            name=u.name,
            email=u.email,
            phone=u.phone,
            status=u.status or "ACTIVE",
            createdAt=u.created_at,
            lastLoginAt=u.last_login_at,
            orderCount=oc or 0,
        )
        for u, oc in rows
    ]

    return items, total


def get_admin_customer(db: Session, customer_id: int) -> AdminCustomerOut:
    """Retrieve detailed customer profile by ID.

    Returns 404 if the customer does not exist or has role other than CUSTOMER.
    """
    customer = (
        db.query(User)
        .filter(User.id == customer_id, User.role == "CUSTOMER")
        .first()
    )
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )

    order_count = (
        db.query(sa.func.count(Order.id))
        .filter(Order.user_id == customer.id)
        .scalar()
        or 0
    )

    return AdminCustomerOut(
        id=customer.id,
        name=customer.name,
        email=customer.email,
        phone=customer.phone,
        status=customer.status or "ACTIVE",
        createdAt=customer.created_at,
        lastLoginAt=customer.last_login_at,
        orderCount=order_count,
    )


def get_admin_customer_orders(
    db: Session,
    customer_id: int,
    page: int = 1,
    page_size: int = 20,
) -> tuple[Sequence[Order], int]:
    """Retrieve paginated order history strictly linked to customer by user_id.

    Returns 404 if the customer does not exist or has role other than CUSTOMER.
    Guest orders are never matched by phone/email.
    """
    customer = (
        db.query(User)
        .filter(User.id == customer_id, User.role == "CUSTOMER")
        .first()
    )
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )

    query = (
        db.query(Order)
        .filter(Order.user_id == customer.id)
        .order_by(Order.created_at.desc().nullslast(), Order.id.desc())
    )
    total = query.count()
    orders = (
        query
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return orders, total
