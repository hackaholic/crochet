"""Order, OrderItem, OrderStatusHistory, and Address models.

Conforms to Sections 18, 20, 21, and 26 of the E-commerce Multi-Agent Specification.
"""

from datetime import datetime, timezone
import enum
from sqlalchemy import (
    Boolean,
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


class OrderStatus(str, enum.Enum):
    PENDING_PAYMENT = "PENDING_PAYMENT"
    PAID = "PAID"
    CONFIRMED = "CONFIRMED"
    PROCESSING = "PROCESSING"
    READY_TO_SHIP = "READY_TO_SHIP"
    SHIPPED = "SHIPPED"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED"


class PaymentStatus(str, enum.Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


class PaymentMethod(str, enum.Enum):
    COD = "COD"
    UPI = "UPI"
    CARD = "CARD"
    NETBANKING = "NETBANKING"


class ReturnStatus(str, enum.Enum):
    REQUESTED = "REQUESTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    ITEMS_RECEIVED = "ITEMS_RECEIVED"
    REFUNDED = "REFUNDED"
    CANCELLED = "CANCELLED"


class RefundStatus(str, enum.Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class Address(Base):
    """Customer delivery address conforming to Section 26 of Specification."""

    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    line1 = Column(String(255), nullable=False)
    line2 = Column(String(255), nullable=True)
    landmark = Column(String(255), nullable=True)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    postal_code = Column(String(20), nullable=False)
    country = Column(String(50), default="IN", nullable=False)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="addresses")


class Order(Base):
    """Customer order entity with status history and address snapshots."""

    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    customer_name = Column(String(100), nullable=False)
    customer_phone = Column(String(20), nullable=False)
    customer_email = Column(String(255), nullable=True)

    # Snapshotted addresses
    shipping_address_json = Column(JSON().with_variant(JSONB, "postgresql"), nullable=False)
    billing_address_json = Column(JSON().with_variant(JSONB, "postgresql"), nullable=True)

    # Status & payment
    status = Column(String(50), default=OrderStatus.CONFIRMED.value, index=True, nullable=False)
    payment_status = Column(String(50), default=PaymentStatus.PENDING.value, index=True, nullable=False)
    payment_method = Column(String(50), default=PaymentMethod.COD.value, nullable=False)

    # Dual financial accounting (Rupees and Paise)
    currency = Column(String(10), default="INR", nullable=False)
    subtotal = Column(Integer, nullable=False)  # Rupees
    shipping_fee = Column(Integer, default=0, nullable=False)  # Rupees
    discount_amount = Column(Integer, default=0, nullable=False)  # Rupees
    tax_amount = Column(Integer, default=0, nullable=False)  # Rupees
    total_amount = Column(Integer, nullable=False)  # Rupees

    notes = Column(Text, nullable=True)
    tracking_number = Column(String(100), nullable=True)
    courier_name = Column(String(100), nullable=True)
    estimated_delivery = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan", order_by="OrderItem.id")
    status_history = relationship(
        "OrderStatusHistory",
        back_populates="order",
        cascade="all, delete-orphan",
        order_by="OrderStatusHistory.id.asc()",
    )
    payments = relationship("Payment", back_populates="order", cascade="all, delete-orphan")
    returns = relationship(
        "ReturnRequest",
        back_populates="order",
        cascade="all, delete-orphan",
        order_by="ReturnRequest.id.desc()",
    )


class OrderItem(Base):
    """Snapshotted line item of an order (Section 21 of Specification)."""

    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(Integer, nullable=True)
    product_variant_id = Column(Integer, nullable=True)

    # Snapshotted fields
    product_name = Column(String(200), nullable=False)
    product_slug = Column(String(200), nullable=True)
    sku = Column(String(100), nullable=False)
    variant_name = Column(String(150), nullable=False)
    product_image = Column(String(500), nullable=True)
    unit_price = Column(Integer, nullable=False)  # Rupees at time of purchase
    quantity = Column(Integer, nullable=False)
    line_total = Column(Integer, nullable=False)  # unit_price * quantity
    personalization_json = Column(JSON().with_variant(JSONB, "postgresql"), default=dict)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    order = relationship("Order", back_populates="items")


class OrderStatusHistory(Base):
    """Audit log for order lifecycle and timeline tracking (Section 20 of Specification)."""

    __tablename__ = "order_status_history"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(50), nullable=False)
    note = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    order = relationship("Order", back_populates="status_history")


class ReturnRequest(Base):
    """Persisted customer return and refund request record."""

    __tablename__ = "return_requests"

    id = Column(Integer, primary_key=True, index=True)
    return_number = Column(String(50), unique=True, index=True, nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    status = Column(String(50), default=ReturnStatus.REQUESTED.value, index=True, nullable=False)
    reason = Column(String(100), nullable=False)
    reason_details = Column(Text, nullable=True)
    items_json = Column(JSON().with_variant(JSONB, "postgresql"), default=list)

    refund_amount = Column(Integer, default=0, nullable=False)  # Rupees
    refund_amount_paise = Column(Integer, default=0, nullable=False)  # Paise
    refund_status = Column(String(50), default=RefundStatus.PENDING.value, index=True, nullable=False)

    admin_notes = Column(Text, nullable=True)
    history_json = Column(JSON().with_variant(JSONB, "postgresql"), default=list)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    order = relationship("Order", back_populates="returns")
    user = relationship("User")
