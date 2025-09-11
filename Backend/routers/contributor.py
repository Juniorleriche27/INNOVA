from fastapi import APIRouter, HTTPException, Depends
from typing import List
from uuid import UUID
from deps.auth import get_bearer_token
from lib.supa import supa_for_jwt
from schemas.contributor import Contributor, ContributorCreate, ContributorUpdate

router = APIRouter(tags=["contributors"])

# Liste des contributeurs d’un projet
@router.get("/project/{project_id}", response_model=List[Contributor], response_model_exclude_none=True)
def list_contributors(project_id: UUID, token: str | None = Depends(get_bearer_token)):
    sb = supa_for_jwt(token)
    res = sb.table("contributors").select("*").eq("project_id", str(project_id)).execute()
    return res.data or []

# Créer un contributor (liaison user_id <-> project_id)
@router.post("/", status_code=201, response_model=Contributor, response_model_exclude_none=True)
def create_contributor(payload: ContributorCreate, token: str | None = Depends(get_bearer_token)):
    sb = supa_for_jwt(token)
    data = payload.dict(exclude_none=True)
    data["project_id"] = str(data["project_id"])
    data["user_id"] = str(data["user_id"])
    res = sb.table("contributors").insert(data).execute()
    if not res.data:
        raise HTTPException(status_code=500, detail="Erreur lors de la création du contributor.")
    return res.data[0]

# Mettre à jour un contributor
@router.put("/{contributor_id}", response_model=Contributor, response_model_exclude_none=True)
def update_contributor(contributor_id: UUID, payload: ContributorUpdate, token: str | None = Depends(get_bearer_token)):
    sb = supa_for_jwt(token)
    data = payload.dict(exclude_unset=True, exclude_none=True)
    res = sb.table("contributors").update(data).eq("id", str(contributor_id)).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Contributor introuvable.")
    return res.data[0]

# Supprimer un contributor
@router.delete("/{contributor_id}", response_model=Contributor, response_model_exclude_none=True)
def delete_contributor(contributor_id: UUID, token: str | None = Depends(get_bearer_token)):
    sb = supa_for_jwt(token)
    res = sb.table("contributors").delete().eq("id", str(contributor_id)).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Contributor introuvable.")
    return res.data[0]
