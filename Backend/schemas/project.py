# schemas/project.py
from pydantic import BaseModel, ConfigDict
from typing import Optional, Literal
from uuid import UUID
from datetime import datetime

class ProjectBase(BaseModel):
    title: Optional[str] = None
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    domain_id: Optional[UUID] = None
    repo_url: Optional[str] = None
    live_url: Optional[str] = None
    logo_url: Optional[str] = None
    status: Optional[Literal["draft", "published", "archived"]] = None
    live: Optional[str] = None
    repo: Optional[str] = None

class ProjectCreate(BaseModel):
    # ⬇ OBLIGATOIRES
    name: str
    slug: str
    # ⬇ Optionnels
    title: Optional[str] = None
    description: Optional[str] = None
    domain_id: Optional[UUID] = None
    repo_url: Optional[str] = None
    live_url: Optional[str] = None
    logo_url: Optional[str] = None
    status: Optional[str] = None
    live: Optional[str] = None
    repo: Optional[str] = None
    model_config = ConfigDict(extra="forbid")

class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    domain_id: Optional[UUID] = None
    repo_url: Optional[str] = None
    live_url: Optional[str] = None
    logo_url: Optional[str] = None
    status: Optional[str] = None
    live: Optional[str] = None
    repo: Optional[str] = None
    model_config = ConfigDict(extra="forbid")

class Project(ProjectBase):
    id: UUID
    created_at: datetime
    # dans la réponse, name & slug existent en DB
    name: str
    slug: str
    model_config = ConfigDict(from_attributes=True, extra="ignore")
