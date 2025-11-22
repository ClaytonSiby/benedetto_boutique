from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from decimal import Decimal


class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: Decimal = Field(ge=0, decimal_places=2)
    sale_price: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    sku: str
    category_id: Optional[UUID] = None
    images: Optional[List[str]] = None
    is_active: bool = True


class ProductCreate(ProductBase):
    slug: str


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    sale_price: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    sku: Optional[str] = None
    category_id: Optional[UUID] = None
    images: Optional[List[str]] = None
    is_active: Optional[bool] = None
    slug: Optional[str] = None


class ProductResponse(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    slug: str
    created_at: datetime
    updated_at: datetime
