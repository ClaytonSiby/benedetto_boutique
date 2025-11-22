from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional


class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    parent_id: Optional[UUID] = None
    is_active: bool = True


class CategoryCreate(CategoryBase):
    slug: str


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    parent_id: Optional[UUID] = None
    is_active: Optional[bool] = None
    slug: Optional[str] = None


class CategoryResponse(CategoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    slug: str
    created_at: datetime
    updated_at: datetime
