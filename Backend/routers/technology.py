# routers/technology.py
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict, Any
from uuid import UUID
from deps.auth import get_bearer_token
from lib.supa import supa_for_jwt
from schemas.technology import Technology, TechnologyCreate, TechnologyUpdate
from postgrest import APIError  # 👈 important

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
        raise HTTPException(status_code=500, detail=f"Technology: invalid payload from DB ({e})")

def _exec(q, not_found_msg: Optional[str] = None):
    try:
        res = q.execute()
    except APIError as e:
        msg = getattr(e, "message", str(e))
        code = getattr(e, "code", 400) or 400
        raise HTTPException(status_code=code, detail=msg)
    if not res.data and not_found_msg:
        raise HTTPException(status_code=404, detail=not_found_msg)
    return res

@router.get("/", response_model=List[Technology], response_model_exclude_none=True)
def list_technologies(project_id: Optional[UUID] = None, token: str | None = Depends(get_bearer_token)):
    sb = supa_for_jwt(token)
    q = sb.table("technologies").select(COLUMNS)
    if project_id:
        q = q.eq("project_id", str(project_id))
    rows = _exec(q).data or []
    return [_row_to_technology(r) for r in rows]

@router.get("/project/{project_id}", response_model=List[Technology], response_model_exclude_none=True)
def list_technologies_by_project(project_id: UUID, token: str | None = Depends(get_bearer_token)):
    sb = supa_for_jwt(token)
    rows = _exec(sb.table("technologies").select(COLUMNS).eq("project_id", str(project_id))).data or []
    return [_row_to_technology(r) for r in rows]

@router.post("/", status_code=201, response_model=Technology, response_model_exclude_none=True)
def create_technology(payload: TechnologyCreate, token: str | None = Depends(get_bearer_token)):
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")
    sb = supa_for_jwt(token)
    data = payload.model_dump(exclude_none=True)
    if data.get("project_id") is not None:
        data["project_id"] = str(data["project_id"])
    row = _exec(sb.table("technologies").insert(data).select(COLUMNS).single(),
                "Erreur lors de la création de la technologie.").data
    return _row_to_technology(row)

@router.put("/{tech_id}", response_model=Technology, response_model_exclude_none=True)
def update_technology(tech_id: UUID, payload: TechnologyUpdate, token: str | None = Depends(get_bearer_token)):
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")
    sb = supa_for_jwt(token)
    data = payload.model_dump(exclude_unset=True, exclude_none=True)
    row = _exec(sb.table("technologies").update(data).eq("id", str(tech_id)).select(COLUMNS).single(),
                "Technologie introuvable.").data
    return _row_to_technology(row)

@router.delete("/{tech_id}", response_model=Technology, response_model_exclude_none=True)
def delete_technology(tech_id: UUID, token: str | None = Depends(get_bearer_token)):
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")
    sb = supa_for_jwt(token)
    row = _exec(sb.table("technologies").delete().eq("id", str(tech_id)).select(COLUMNS).single(),
                "Technologie introuvable.").data
    return _row_to_technology(row)
