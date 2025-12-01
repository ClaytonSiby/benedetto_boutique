from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional
from uuid import UUID
import re


class BlogPostBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    excerpt: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)
    featured_image: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[str] = None
    is_published: bool = False

    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()


class BlogPostCreate(BlogPostBase):
    pass


class BlogPostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    excerpt: Optional[str] = Field(None, min_length=1)
    content: Optional[str] = Field(None, min_length=1)
    featured_image: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[str] = None
    is_published: Optional[bool] = None


class BlogPostResponse(BlogPostBase):
    id: int
    slug: str
    author_id: UUID
    published_at: Optional[datetime] = None
    views_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BlogPostListResponse(BaseModel):
    id: int
    title: str
    slug: str
    excerpt: str
    featured_image: Optional[str] = None
    category: Optional[str] = None
    author_id: UUID
    is_published: bool
    published_at: Optional[datetime] = None
    views_count: int
    created_at: datetime

    class Config:
        from_attributes = True
