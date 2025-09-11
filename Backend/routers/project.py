# routers/project.py
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from uuid import UUID

from schemas.project import Project, ProjectCreate, ProjectUpdate
from lib.supa import supa_for_jwt, sb_anon
from deps.auth import get_bearer_token
from postgrest import APIError

router = APIRouter(tags=["projects"])


# ✅ Create project (auth requis)
@router.post("/", status_code=201, response_model=Project, response_model_exclude_none=True)
def create_project(
    project: ProjectCreate,
    token: str | None = Depends(get_bearer_token),
):
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")

    sb = supa_for_jwt(token)

    # Pydantic v2 → model_dump; exclude_none pour ne pas envoyer de NULL inutiles
    data = project.model_dump(exclude_none=True)

    # Supabase/Postgres attend une string pour uuid si fourni via JSON
    if "domain_id" in data and data["domain_id"] is not None:
        data["domain_id"] = str(data["domain_id"])

    # Debug temporaire (à retirer en prod)
    print("DEBUG /projects POST payload →", data)

    try:
        res = sb.table("projects").insert(data).execute()
        if not res.data:
            # Généralement RLS / policy non concordante
            raise HTTPException(status_code=403, detail="Insert refused (RLS/Policy).")
        return res.data[0]
    except APIError as e:
        # Renvoyer le message PostgREST lisible côté client
        msg = getattr(e, "message", str(e))
        raise HTTPException(status_code=403, detail=f"Supabase: {msg}")


# ✅ List all projects (lecture publique via anon possible)
@router.get("/", response_model=List[Project], response_model_exclude_none=True)
def get_projects():
    res = sb_anon.table("projects").select("*").execute()
    return res.data or []


# ✅ Get one project (lecture publique via anon possible)
@router.get("/{project_id}", response_model=Project, response_model_exclude_none=True)
def get_project(project_id: UUID):
    res = sb_anon.table("projects").select("*").eq("id", str(project_id)).single().execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Projet introuvable.")
    return res.data


# ✅ Update project (auth requis)
@router.put("/{project_id}", response_model=Project, response_model_exclude_none=True)
def update_project(
    project_id: UUID,
    update: ProjectUpdate,
    token: str | None = Depends(get_bearer_token),
):
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")

    sb = supa_for_jwt(token)

    # Pydantic v2 → model_dump; exclude_unset pour n'envoyer que les champs fournis
    payload = update.model_dump(exclude_none=True, exclude_unset=True)

    if "domain_id" in payload and payload["domain_id"] is not None:
        payload["domain_id"] = str(payload["domain_id"])

    # Debug temporaire (à retirer en prod)
    print("DEBUG /projects PUT payload →", payload)

    try:
        res = sb.table("projects").update(payload).eq("id", str(project_id)).execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="Projet introuvable.")
        return res.data[0]
    except APIError as e:
        msg = getattr(e, "message", str(e))
        raise HTTPException(status_code=403, detail=f"Supabase: {msg}")


# ✅ Delete project (auth requis)
@router.delete("/{project_id}", response_model=Project, response_model_exclude_none=True)
def delete_project(
    project_id: UUID,
    token: str | None = Depends(get_bearer_token),
):
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")

    sb = supa_for_jwt(token)

    try:
        res = sb.table("projects").delete().eq("id", str(project_id)).execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="Projet introuvable.")
        return res.data[0]
    except APIError as e:
        msg = getattr(e, "message", str(e))
        raise HTTPException(status_code=403, detail=f"Supabase: {msg}")
