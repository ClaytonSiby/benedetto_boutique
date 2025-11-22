from pydantic import BaseModel, ConfigDict
from uuid import UUID
from typing import Optional


class AddressBase(BaseModel):
    type: str
    street: str
    city: str
    state: str
    country: str
    postal_code: str
    postal_code_alt: Optional[str] = None


class AddressCreate(AddressBase):
    pass


class AddressUpdate(BaseModel):
    type: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    postal_code_alt: Optional[str] = None


class AddressResponse(AddressBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
