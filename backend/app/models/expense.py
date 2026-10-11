"""Expense models conforming to Work 020 financial accounting specification."""

from datetime import datetime, timezone
import enum
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.db.base import Base


class ExpenseCategory(str, enum.Enum):
    GATEWAY_FEE = "GATEWAY_FEE"
    FULFILMENT = "FULFILMENT"
    PACKAGING = "PACKAGING"
    MARKETING = "MARKETING"
    OPERATING = "OPERATING"
    OTHER = "OTHER"


class AdminExpense(Base):
    """Recorded operating, payment gateway, shipping, or administrative expense."""

    __tablename__ = "admin_expenses"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(50), default=ExpenseCategory.OPERATING.value, index=True, nullable=False)
    amount = Column(Integer, nullable=False)  # Rupees
    amount_paise = Column(Integer, nullable=False)  # Paise
    currency = Column(String(10), default="INR", nullable=False)

    order_id = Column(Integer, ForeignKey("orders.id", ondelete="SET NULL"), nullable=True, index=True)
    description = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)

    expense_date = Column(DateTime, index=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    order = relationship("Order")
