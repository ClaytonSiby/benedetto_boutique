from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime, date
from typing import Optional


class ProfileBase(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    avatar_url: Optional[str] = None
    date_of_birth: Optional[date] = None


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(ProfileBase):
    pass


class ProfileResponse(ProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
