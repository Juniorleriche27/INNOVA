from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict, Any
from uuid import UUID
from deps.auth import get_bearer_token
from lib.supa import supa_for_jwt
from schemas.contributor import Contributor, ContributorCreate, ContributorUpdate
from postgrest import APIError  # << pour capter les erreurs PostgREST

router = APIRouter(tags=["contributors"])

COLUMNS = "id, project_id, user_id, name, role, email, github"

def _row_to_contributor(row: Dict[str, Any]) -> Contributor:
    try:
        return Contributor.model_validate({
            "id": UUID(str(row["id"])) if row.get("id") is not None else None,
            "project_id": UUID(str(row["project_id"])) if row.get("project_id") is not None else None,
            "user_id": UUID(str(row["user_id"])) if row.get("user_id") is not None else None,
            "name": row.get("name"),
            "role": row.get("role"),
            "email": row.get("email"),
            "github": row.get("github"),
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Contributor: invalid payload from DB ({e})")

def _exec(q, not_found_msg: Optional[str] = None):
    """Exécute une requête PostgREST en capturant APIError et not_found."""
    try:
        res = q.execute()
    except APIError as e:
        # e.message / e.code disponibles selon la version
        msg = getattr(e, "message", str(e))
        code = getattr(e, "code", 400) or 400
        raise HTTPException(status_code=code, detail=msg)
    if not res.data and not_found_msg:
        raise HTTPException(status_code=404, detail=not_found_msg)
    return res

@router.get("/", response_model=List[Contributor], response_model_exclude_none=True)
def list_contributors(
    project_id: Optional[UUID] = None,
    token: str | None = Depends(get_bearer_token),
):
    sb = supa_for_jwt(token)
    q = sb.table("contributors").select(COLUMNS)
    if project_id:
        q = q.eq("project_id", str(project_id))
    rows = _exec(q).data or []
    return [_row_to_contributor(r) for r in rows]

@router.get("/project/{project_id}", response_model=List[Contributor], response_model_exclude_none=True)
def list_contributors_by_project(
    project_id: UUID,
    token: str | None = Depends(get_bearer_token),
):
    sb = supa_for_jwt(token)
    rows = _exec(
        sb.table("contributors").select(COLUMNS).eq("project_id", str(project_id))
    ).data or []
    return [_row_to_contributor(r) for r in rows]

@router.post("/", status_code=201, response_model=Contributor, response_model_exclude_none=True)
def create_contributor(payload: ContributorCreate, token: str | None = Depends(get_bearer_token)):
    sb = supa_for_jwt(token)
    data = payload.model_dump(exclude_none=True)
    if data.get("project_id") is not None:
        data["project_id"] = str(data["project_id"])
    if data.get("user_id") is not None:
        data["user_id"] = str(data["user_id"])

    row = _exec(
        sb.table("contributors").insert(data).select(COLUMNS).single(),
        "Erreur lors de la création du contributor."
    ).data
    return _row_to_contributor(row)

@router.put("/{contributor_id}", response_model=Contributor, response_model_exclude_none=True)
def update_contributor(contributor_id: UUID, payload: ContributorUpdate, token: str | None = Depends(get_bearer_token)):
    sb = supa_for_jwt(token)
    data = payload.model_dump(exclude_unset=True, exclude_none=True)
    row = _exec(
        sb.table("contributors").update(data).eq("id", str(contributor_id)).select(COLUMNS).single(),
        "Contributor introuvable."
    ).data
    return _row_to_contributor(row)

@router.delete("/{contributor_id}", response_model=Contributor, response_model_exclude_none=True)
def delete_contributor(contributor_id: UUID, token: str | None = Depends(get_bearer_token)):
    sb = supa_for_jwt(token)
    row = _exec(
        sb.table("contributors").delete().eq("id", str(contributor_id)).select(COLUMNS).single(),
        "Contributor introuvable."
    ).data
    return _row_to_contributor(row)
