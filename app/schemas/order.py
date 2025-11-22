from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from app.models.order import OrderStatus


class OrderItemBase(BaseModel):
    product_id: UUID
    quantity: int = Field(ge=1)
    price: Decimal = Field(ge=0, decimal_places=2)


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemResponse(OrderItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    order_id: UUID
    subtotal: Decimal


class OrderBase(BaseModel):
    shipping_address_id: Optional[UUID] = None
    billing_address_id: Optional[UUID] = None


class OrderCreate(OrderBase):
    items: List[OrderItemCreate]


class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    shipping_address_id: Optional[UUID] = None
    billing_address_id: Optional[UUID] = None


class OrderResponse(OrderBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: Optional[UUID]
    order_number: str
    status: OrderStatus
    subtotal: Decimal
    tax: Decimal
    shipping_cost: Decimal
    total: Decimal
    created_at: datetime
    updated_at: datetime
    order_items: List[OrderItemResponse] = []
