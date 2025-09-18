from pydantic import BaseModel, ConfigDict
from typing import Optional, Literal
from uuid import UUID
from datetime import datetime

AllowedStatus = Literal["draft", "published", "archived"]

class ProjectBase(BaseModel):
    title: Optional[str] = None
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    domain_id: Optional[UUID] = None
    repo_url: Optional[str] = None
    live_url: Optional[str] = None
    logo_url: Optional[str] = None
    status: Optional[AllowedStatus] = None  # 👈 uniforme
    # Ces deux champs n'existent pas en DB. Si tu les gardes côté front, OK,
    # mais le backend les ignorera (extra="ignore" dans Project).
    live: Optional[str] = None
    repo: Optional[str] = None

class ProjectCreate(BaseModel):
    name: str
    slug: str
    title: Optional[str] = None
    description: Optional[str] = None
    domain_id: Optional[UUID] = None
    repo_url: Optional[str] = None
    live_url: Optional[str] = None
    logo_url: Optional[str] = None
    status: Optional[AllowedStatus] = None  # 👈 uniforme
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
    status: Optional[AllowedStatus] = None  # 👈 uniforme
    live: Optional[str] = None
    repo: Optional[str] = None
    model_config = ConfigDict(extra="forbid")

class Project(ProjectBase):
    id: UUID
    created_at: datetime
    created_by: Optional[UUID] = None   # 👈 optionnel (colonne nullable)
    name: str
    slug: str
    model_config = ConfigDict(from_attributes=True, extra="ignore")
