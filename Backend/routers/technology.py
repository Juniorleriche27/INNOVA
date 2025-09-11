from fastapi import APIRouter, HTTPException, Depends
from typing import List
from uuid import UUID
from deps.auth import get_bearer_token
from lib.supa import supa_for_jwt
from schemas.technology import Technology, TechnologyCreate, TechnologyUpdate

router = APIRouter(tags=["technologies"])

@router.get("/project/{project_id}", response_model=List[Technology], response_model_exclude_none=True)
def list_techs(project_id: UUID, token: str | None = Depends(get_bearer_token)):
    sb = supa_for_jwt(token)
    res = sb.table("technologies").select("*").eq("project_id", str(project_id)).execute()
    return res.data or []

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
