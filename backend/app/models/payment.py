"""Payment models conforming to Section 25 (Payment Architecture) of the Specification."""

from datetime import datetime, timezone
import enum
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.db.base import Base


class PaymentRecordStatus(str, enum.Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


class PaymentProviderName(str, enum.Enum):
    MOCK = "mock"
    RAZORPAY = "razorpay"
    UPI = "upi"
    COD = "cod"


class Payment(Base):
    """Payment record linked to an Order behind the provider abstraction layer."""

    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    provider = Column(String(50), default=PaymentProviderName.MOCK.value, nullable=False)
    provider_payment_id = Column(String(100), unique=True, index=True, nullable=True)
    provider_order_id = Column(String(100), index=True, nullable=True)

    # Financial amounts (Rupees and Paise)
    amount = Column(Integer, nullable=False)  # Rupees
    amount_paise = Column(Integer, nullable=False)  # Paise
    currency = Column(String(10), default="INR", nullable=False)

    status = Column(String(50), default=PaymentRecordStatus.PENDING.value, index=True, nullable=False)
    payment_method_detail = Column(String(100), nullable=True)  # e.g. "UPI / Google Pay", "Cards"
    error_message = Column(Text, nullable=True)
    metadata_json = Column(JSON().with_variant(JSONB, "postgresql"), default=dict)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    order = relationship("Order", back_populates="payments")
