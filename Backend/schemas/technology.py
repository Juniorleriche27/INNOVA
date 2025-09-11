from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class Technology(BaseModel):
    id: UUID
    project_id: UUID
    name: Optional[str] = None
    version: Optional[str] = None

class TechnologyCreate(BaseModel):
    project_id: UUID
    name: str
    version: Optional[str] = None

class TechnologyUpdate(BaseModel):
    name: Optional[str] = None
    version: Optional[str] = None
