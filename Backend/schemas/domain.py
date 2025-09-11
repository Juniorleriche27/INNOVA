from typing import Optional
from uuid import UUID
from pydantic import BaseModel

class DomainBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    image_url: Optional[str] = None

class DomainCreate(DomainBase):
    pass

class Domain(DomainBase):
    id: UUID

    class Config:
        from_attributes = True

class DomainUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
