# routers/project.py
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from uuid import UUID

from schemas.project import Project, ProjectCreate, ProjectUpdate
from lib.supa import supa_for_jwt, sb_anon
from deps.auth import get_bearer_token
from postgrest import APIError

router = APIRouter(tags=["projects"])

# Par défaut on retourne toutes les colonnes (compatibles avec Project)
PROJECT_COLUMNS = (
    "id, name, slug, title, description, domain_id, repo_url, live_url, logo_url, "
    "status, created_at, created_by"
)

def _raise_api_if_error(res, default_status: int = 400, not_found_msg: Optional[str] = None):
    err = getattr(res, "error", None)
    if err:
        # PostgREST renseigne souvent status_code/message
        status = getattr(err, "status_code", default_status) or default_status
        msg = getattr(err, "message", str(err))
        raise HTTPException(status_code=status, detail=msg)
    if not res.data and not_found_msg:
        raise HTTPException(status_code=404, detail=not_found_msg)

# ✅ Create project (auth requis)
@router.post("/", status_code=201, response_model=Project, response_model_exclude_none=True)
def create_project(
    project: ProjectCreate,
    token: str | None = Depends(get_bearer_token),
):
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")

    sb = supa_for_jwt(token)
    data = project.model_dump(exclude_none=True)

    # Cast UUID -> str pour PostgREST
    if "domain_id" in data and data["domain_id"] is not None:
        data["domain_id"] = str(data["domain_id"])

    try:
        # .select(...).single() pour récupérer la ligne insérée (avec trigger created_by)
        res = sb.table("projects").insert(data).select(PROJECT_COLUMNS).single().execute()
        _raise_api_if_error(res, default_status=403, not_found_msg="Insert refused (RLS/Policy).")
        return res.data
    except APIError as e:
        msg = getattr(e, "message", str(e))
        raise HTTPException(status_code=403, detail=f"Supabase: {msg}")

# ✅ List projects
# - sans token: anon → ne verra que les 'published' (RLS)
# - avec token: authenticated → verra ses propres projets + published
@router.get("/", response_model=List[Project], response_model_exclude_none=True)
def list_projects(token: str | None = Depends(get_bearer_token)):
    sb = supa_for_jwt(token) if token else sb_anon
    res = sb.table("projects").select(PROJECT_COLUMNS).execute()
    _raise_api_if_error(res)
    return res.data or []

# ✅ Get one project (lecture publique possible si 'published', sinon owner via token)
@router.get("/{project_id}", response_model=Project, response_model_exclude_none=True)
def get_project(project_id: UUID, token: str | None = Depends(get_bearer_token)):
    sb = supa_for_jwt(token) if token else sb_anon
    res = sb.table("projects").select(PROJECT_COLUMNS).eq("id", str(project_id)).single().execute()
    _raise_api_if_error(res, not_found_msg="Projet introuvable.")
    return res.data

# ✅ Update project (auth requis, owner-only via RLS)
@router.put("/{project_id}", response_model=Project, response_model_exclude_none=True)
def update_project(
    project_id: UUID,
    update: ProjectUpdate,
    token: str | None = Depends(get_bearer_token),
):
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")

    sb = supa_for_jwt(token)
    payload = update.model_dump(exclude_none=True, exclude_unset=True)

    if "domain_id" in payload and payload["domain_id"] is not None:
        payload["domain_id"] = str(payload["domain_id"])

    try:
        res = (
            sb.table("projects")
            .update(payload)
            .eq("id", str(project_id))
            .select(PROJECT_COLUMNS)
            .single()
            .execute()
        )
        _raise_api_if_error(res, default_status=403, not_found_msg="Projet introuvable.")
        return res.data
    except APIError as e:
        msg = getattr(e, "message", str(e))
        raise HTTPException(status_code=403, detail=f"Supabase: {msg}")

# ✅ Delete project (auth requis, owner-only via RLS)
@router.delete("/{project_id}", response_model=Project, response_model_exclude_none=True)
def delete_project(
    project_id: UUID,
    token: str | None = Depends(get_bearer_token),
):
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")

    sb = supa_for_jwt(token)
    try:
        res = (
            sb.table("projects")
            .delete()
            .eq("id", str(project_id))
            .select(PROJECT_COLUMNS)
            .single()
            .execute()
        )
        _raise_api_if_error(res, default_status=403, not_found_msg="Projet introuvable.")
        return res.data
    except APIError as e:
        msg = getattr(e, "message", str(e))
        raise HTTPException(status_code=403, detail=f"Supabase: {msg}")
