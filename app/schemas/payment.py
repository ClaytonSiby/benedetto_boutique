from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional, Dict, Any
from decimal import Decimal
from app.models.payment import PaymentStatus


class PaymentBase(BaseModel):
    payment_method: str
    amount: Decimal = Field(ge=0, decimal_places=2)
    currency: str = "USD"


class PaymentCreate(PaymentBase):
    order_id: UUID
    transaction_id: Optional[str] = None
    provider_data: Optional[Dict[str, Any]] = None


class PaymentUpdate(BaseModel):
    status: Optional[PaymentStatus] = None
    transaction_id: Optional[str] = None
    provider_data: Optional[Dict[str, Any]] = None


class PaymentResponse(PaymentBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    order_id: UUID
    status: PaymentStatus
    transaction_id: Optional[str]
    provider_data: Optional[Dict[str, Any]]
    created_at: datetime
