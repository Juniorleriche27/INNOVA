from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID

class Contributor(BaseModel):
    id: UUID
    project_id: UUID
    user_id: Optional[UUID] = None
    name: Optional[str] = None
    role: Optional[str] = None
    email: Optional[EmailStr] = None
    github: Optional[str] = None

class ContributorCreate(BaseModel):
    project_id: UUID
    user_id: Optional[UUID] = None
    name: Optional[str] = None
    role: Optional[str] = None
    email: Optional[EmailStr] = None
    github: Optional[str] = None

class ContributorUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    email: Optional[EmailStr] = None
    github: Optional[str] = None
