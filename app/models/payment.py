from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum

from app.db.session import Base


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class Payment(Base):
    __tablename__ = "payment"

    id = Column(UUID(as_uuid=True), primary_key=True,
                default=uuid.uuid4, index=True)
    order_id = Column(UUID(as_uuid=True), ForeignKey(
        "order.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    payment_method = Column(String, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String, default="USD", nullable=False)
    status = Column(SQLEnum(PaymentStatus),
                    default=PaymentStatus.PENDING, nullable=False, index=True)
    transaction_id = Column(String, unique=True, nullable=True, index=True)
    # Store provider-specific data
    provider_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    order = relationship("Order", back_populates="payment")

    def __repr__(self):
        return f"<Payment order_id={self.order_id} status={self.status}>"
