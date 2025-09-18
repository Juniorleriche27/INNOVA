from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict  # 👈 v2

class DomainBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    image_url: Optional[str] = None

class DomainCreate(DomainBase):
    pass

class Domain(DomainBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)  # 👈 v2

class DomainUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
