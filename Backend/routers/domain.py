from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from uuid import UUID

from schemas.domain import Domain, DomainCreate, DomainUpdate
from lib.supa import supa_for_jwt, get_sb_anon
from deps.auth import get_bearer_token

router = APIRouter(tags=["domains"])

COLUMNS = "id, name, slug, description, image_url"

def _raise(res, not_found: Optional[str] = None):
    err = getattr(res, "error", None)
    if err:
        code = getattr(err, "status_code", 400) or 400
        msg = getattr(err, "message", str(err))
        raise HTTPException(status_code=code, detail=msg)
    if not res.data and not_found:
        raise HTTPException(status_code=404, detail=not_found)

@router.get("/", response_model=List[Domain])
def read_domains():
    res = get_sb_anon().from_("domains").select(COLUMNS).execute()
    _raise(res)
    return res.data or []

@router.get("/{domain_id}", response_model=Domain)
def read_domain(domain_id: UUID):
    res = get_sb_anon().from_("domains").select(COLUMNS).eq("id", str(domain_id)).single().execute()
    _raise(res, "Domain not found")
    return res.data

@router.post("/", response_model=Domain)
def create_new_domain(
    payload: DomainCreate,
    token: str | None = Depends(get_bearer_token),
):
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")
    sb = supa_for_jwt(token)
    res = sb.from_("domains").insert(payload.model_dump(exclude_none=True)).select(COLUMNS).single().execute()
    _raise(res, "Create failed")
    return res.data

@router.put("/{domain_id}", response_model=Domain)
def update_existing_domain(
    domain_id: UUID,
    updates: DomainUpdate,
    token: str | None = Depends(get_bearer_token),
):
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")
    sb = supa_for_jwt(token)
    res = (
        sb.from_("domains")
        .update(updates.model_dump(exclude_unset=True, exclude_none=True))
        .eq("id", str(domain_id))
        .select(COLUMNS).single().execute()
    )
    _raise(res, "Domain not found")
    return res.data

@router.delete("/{domain_id}", response_model=Domain)
def delete_existing_domain(
    domain_id: UUID,
    token: str | None = Depends(get_bearer_token),
):
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")
    sb = supa_for_jwt(token)
    res = sb.from_("domains").delete().eq("id", str(domain_id)).select(COLUMNS).single().execute()
    _raise(res, "Domain not found")
    return res.data
