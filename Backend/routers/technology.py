# routers/technology.py
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict, Any
from uuid import UUID
from deps.auth import get_bearer_token
from lib.supa import supa_for_jwt
from schemas.technology import Technology, TechnologyCreate, TechnologyUpdate

router = APIRouter(tags=["technologies"])

COLUMNS = "id, project_id, name, version"

def _row_to_technology(row: Dict[str, Any]) -> Technology:
    try:
        return Technology.model_validate({
            "id": UUID(str(row["id"])) if row.get("id") is not None else None,
            "project_id": UUID(str(row["project_id"])) if row.get("project_id") is not None else None,
            "name": row.get("name"),
            "version": row.get("version"),
        })
    except Exception as e:
        # Incohérence schéma/données -> 500 explicite
        raise HTTPException(status_code=500, detail=f"Technology: invalid payload from DB ({e})")

def _raise_api_if_error(res, default_status: int = 400, not_found_msg: Optional[str] = None):
    err = getattr(res, "error", None)
    if err:
        status = getattr(err, "status_code", default_status) or default_status
        msg = getattr(err, "message", str(err))
        raise HTTPException(status_code=status, detail=msg)
    if not res.data and not_found_msg:
        raise HTTPException(status_code=404, detail=not_found_msg)

@router.get("/", response_model=List[Technology], response_model_exclude_none=True)
def list_technologies(
    project_id: Optional[UUID] = None,
    token: str | None = Depends(get_bearer_token),
):
    sb = supa_for_jwt(token)  # anon si token None → RLS appliquée
    q = sb.table("technologies").select(COLUMNS)
    if project_id:
        q = q.eq("project_id", str(project_id))
    res = q.execute()
    _raise_api_if_error(res)
    rows = res.data or []
    return [_row_to_technology(r) for r in rows]

@router.get("/project/{project_id}", response_model=List[Technology], response_model_exclude_none=True)
def list_technologies_by_project(
    project_id: UUID,
    token: str | None = Depends(get_bearer_token),
):
    sb = supa_for_jwt(token)
    res = sb.table("technologies").select(COLUMNS).eq("project_id", str(project_id)).execute()
    _raise_api_if_error(res)
    rows = res.data or []
    return [_row_to_technology(r) for r in rows]

@router.post("/", status_code=201, response_model=Technology, response_model_exclude_none=True)
def create_technology(
    payload: TechnologyCreate,
    token: str | None = Depends(get_bearer_token),
):
    if not token:
        # écriture protégée; sinon RLS refusera en 401/403 mais on est explicite
        raise HTTPException(status_code=401, detail="Authentication required")

    sb = supa_for_jwt(token)
    data = payload.model_dump(exclude_none=True)
    if "project_id" in data and data["project_id"] is not None:
        data["project_id"] = str(data["project_id"])

    res = sb.table("technologies").insert(data).select(COLUMNS).single().execute()
    _raise_api_if_error(res, default_status=403, not_found_msg="Erreur lors de la création de la technologie.")
    return _row_to_technology(res.data)

@router.put("/{tech_id}", response_model=Technology, response_model_exclude_none=True)
def update_technology(
    tech_id: UUID,
    payload: TechnologyUpdate,
    token: str | None = Depends(get_bearer_token),
):
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")

    sb = supa_for_jwt(token)
    data = payload.model_dump(exclude_unset=True, exclude_none=True)

    res = (
        sb.table("technologies")
        .update(data)
        .eq("id", str(tech_id))
        .select(COLUMNS)
        .single()
        .execute()
    )
    _raise_api_if_error(res, default_status=403, not_found_msg="Technologie introuvable.")
    return _row_to_technology(res.data)

@router.delete("/{tech_id}", response_model=Technology, response_model_exclude_none=True)
def delete_technology(
    tech_id: UUID,
    token: str | None = Depends(get_bearer_token),
):
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")

    sb = supa_for_jwt(token)
    res = (
        sb.table("technologies")
        .delete()
        .eq("id", str(tech_id))
        .select(COLUMNS)
        .single()
        .execute()
    )
    _raise_api_if_error(res, default_status=403, not_found_msg="Technologie introuvable.")
    return _row_to_technology(res.data)
