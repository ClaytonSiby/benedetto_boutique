from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime


class FavoriteBase(BaseModel):
    product_id: UUID


class FavoriteCreate(FavoriteBase):
    pass


class FavoriteResponse(FavoriteBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    created_at: datetime


class FavoriteWithProduct(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    product_id: UUID
    created_at: datetime
    product: dict  # Will contain product details
