from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID


class ContactMessageCreate(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    subject: str
    message: str


class ContactMessageResponse(BaseModel):
    id: UUID
    name: str
    email: str
    phone: Optional[str]
    subject: str
    message: str
    is_read: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class NewsletterSubscriberCreate(BaseModel):
    email: EmailStr


class NewsletterSubscriberResponse(BaseModel):
    id: UUID
    email: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
