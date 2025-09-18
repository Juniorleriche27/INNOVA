from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from uuid import UUID
from schemas.project import Project, ProjectCreate, ProjectUpdate
from lib.supa import supa_for_jwt, sb_anon
from deps.auth import get_bearer_token
from postgrest import APIError  # 👈

router = APIRouter(tags=["projects"])

PROJECT_COLUMNS = (
    "id, name, slug, title, description, domain_id, repo_url, live_url, logo_url, "
    "status, created_at, created_by"
)

def _exec(q, default_status: int = 400, not_found_msg: Optional[str] = None):
    try:
        res = q.execute()
    except APIError as e:
        msg = getattr(e, "message", str(e))
        code = getattr(e, "code", default_status) or default_status
        raise HTTPException(status_code=code, detail=msg)
    if not res.data and not_found_msg:
        raise HTTPException(status_code=404, detail=not_found_msg)
    return res

@router.post("/", status_code=201, response_model=Project, response_model_exclude_none=True)
def create_project(project: ProjectCreate, token: str | None = Depends(get_bearer_token)):
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")
    sb = supa_for_jwt(token)
    data = project.model_dump(exclude_none=True)
    if data.get("domain_id") is not None:
        data["domain_id"] = str(data["domain_id"])
    row = _exec(sb.table("projects").insert(data).select(PROJECT_COLUMNS).single(),
                403, "Insert refused (RLS/Policy).").data
    return row

@router.get("/", response_model=List[Project], response_model_exclude_none=True)
def list_projects(token: str | None = Depends(get_bearer_token)):
    sb = supa_for_jwt(token) if token else sb_anon
    return _exec(sb.table("projects").select(PROJECT_COLUMNS)).data or []

@router.get("/{project_id}", response_model=Project, response_model_exclude_none=True)
def get_project(project_id: UUID, token: str | None = Depends(get_bearer_token)):
    sb = supa_for_jwt(token) if token else sb_anon
    return _exec(sb.table("projects").select(PROJECT_COLUMNS).eq("id", str(project_id)).single(),
                 not_found_msg="Projet introuvable.").data

@router.put("/{project_id}", response_model=Project, response_model_exclude_none=True)
def update_project(project_id: UUID, update: ProjectUpdate, token: str | None = Depends(get_bearer_token)):
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")
    sb = supa_for_jwt(token)
    payload = update.model_dump(exclude_none=True, exclude_unset=True)
    if payload.get("domain_id") is not None:
        payload["domain_id"] = str(payload["domain_id"])
    return _exec(sb.table("projects").update(payload).eq("id", str(project_id))
                    .select(PROJECT_COLUMNS).single(),
                 403, "Projet introuvable.").data

@router.delete("/{project_id}", response_model=Project, response_model_exclude_none=True)
def delete_project(project_id: UUID, token: str | None = Depends(get_bearer_token)):
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")
    sb = supa_for_jwt(token)
    return _exec(sb.table("projects").delete().eq("id", str(project_id))
                    .select(PROJECT_COLUMNS).single(),
                 403, "Projet introuvable.").data
