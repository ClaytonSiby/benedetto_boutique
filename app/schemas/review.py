from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional


class ReviewBase(BaseModel):
    product_id: UUID
    rating: int = Field(ge=1, le=5)
    title: Optional[str] = None
    comment: Optional[str] = None


class ReviewCreate(ReviewBase):
    order_id: Optional[UUID] = None


class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    title: Optional[str] = None
    comment: Optional[str] = None


class ReviewResponse(ReviewBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    order_id: Optional[UUID]
    is_verified: bool
    created_at: datetime
