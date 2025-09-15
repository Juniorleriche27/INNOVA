from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from uuid import UUID
from deps.auth import get_bearer_token
from lib.supa import supa_for_jwt
from schemas.technology import Technology, TechnologyCreate, TechnologyUpdate

router = APIRouter(tags=["technologies"])

# ✅ Liste globale (optionnellement filtrée par project_id via query ?project_id=...)
@router.get("/", response_model=List[Technology], response_model_exclude_none=True)
def list_all_techs(
    project_id: Optional[UUID] = None,
    token: str | None = Depends(get_bearer_token),
):
    try:
        sb = supa_for_jwt(token)
        query = sb.table("technologies").select("*")
        if project_id:
            query = query.eq("project_id", str(project_id))
        res = query.execute()
        return res.data or []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la lecture des technologies: {e}")

# Liste des technologies d’un projet (via path param)
@router.get("/project/{project_id}", response_model=List[Technology], response_model_exclude_none=True)
def list_techs_by_project(project_id: UUID, token: str | None = Depends(get_bearer_token)):
    try:
        sb = supa_for_jwt(token)
        res = sb.table("technologies").select("*").eq("project_id", str(project_id)).execute()
        return res.data or []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la lecture des technologies du projet: {e}")

@router.post("/", status_code=201, response_model=Technology, response_model_exclude_none=True)
def create_tech(payload: TechnologyCreate, token: str | None = Depends(get_bearer_token)):
    sb = supa_for_jwt(token)
    data = payload.dict(exclude_none=True)
    data["project_id"] = str(data["project_id"])
    res = sb.table("technologies").insert(data).execute()
    if not res.data:
        raise HTTPException(status_code=500, detail="Erreur lors de la création de la techno.")
    return res.data[0]

@router.put("/{tech_id}", response_model=Technology, response_model_exclude_none=True)
def update_tech(tech_id: UUID, payload: TechnologyUpdate, token: str | None = Depends(get_bearer_token)):
    sb = supa_for_jwt(token)
    data = payload.dict(exclude_unset=True, exclude_none=True)
    res = sb.table("technologies").update(data).eq("id", str(tech_id)).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Technologie introuvable.")
    return res.data[0]

@router.delete("/{tech_id}", response_model=Technology, response_model_exclude_none=True)
def delete_tech(tech_id: UUID, token: str | None = Depends(get_bearer_token)):
    sb = supa_for_jwt(token)
    res = sb.table("technologies").delete().eq("id", str(tech_id)).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Technologie introuvable.")
    return res.data[0]
