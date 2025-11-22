from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional


class InventoryBase(BaseModel):
    quantity: int = Field(ge=0)
    reserved: int = Field(ge=0, default=0)
    available: int = Field(ge=0, default=0)


class InventoryCreate(InventoryBase):
    product_id: UUID


class InventoryUpdate(BaseModel):
    quantity: Optional[int] = Field(None, ge=0)
    reserved: Optional[int] = Field(None, ge=0)
    available: Optional[int] = Field(None, ge=0)


class InventoryResponse(InventoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    product_id: UUID
    updated_at: datetime
