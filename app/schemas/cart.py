from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from decimal import Decimal

from app.schemas.product import ProductResponse


class CartItemBase(BaseModel):
    product_id: UUID
    quantity: int = Field(ge=1)


class CartItemCreate(CartItemBase):
    pass


class CartItemUpdate(BaseModel):
    quantity: int = Field(ge=1)


class CartItemResponse(CartItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    cart_id: UUID
    price: Decimal
    created_at: datetime
    updated_at: datetime
    product: Optional[ProductResponse] = None  # Will contain product details


class CartResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    session_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    cart_items: List[CartItemResponse] = []
