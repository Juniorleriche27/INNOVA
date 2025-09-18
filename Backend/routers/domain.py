# routers/domain.py
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from uuid import UUID

from schemas.domain import Domain, DomainCreate, DomainUpdate
from lib.supa import supa_for_jwt, sb_anon
from deps.auth import get_bearer_token

router = APIRouter(tags=["domains"])

DOMAIN_COLUMNS = "id, name, slug, description, image_url"

def _raise_api_if_error(res, default_status: int = 400, not_found_msg: Optional[str] = None):
    err = getattr(res, "error", None)
    if err:
        status = getattr(err, "status_code", default_status) or default_status
        msg = getattr(err, "message", str(err))
        raise HTTPException(status_code=status, detail=msg)
    if not res.data and not_found_msg:
        raise HTTPException(status_code=404, detail=not_found_msg)

# ✅ List domains (lecture publique via anon OK)
@router.get("/", response_model=List[Domain], response_model_exclude_none=True)
def list_domains(token: str | None = Depends(get_bearer_token)):
    sb = supa_for_jwt(token) if token else sb_anon
    res = sb.table("domains").select(DOMAIN_COLUMNS).execute()
    _raise_api_if_error(res)
    return res.data or []

# ✅ Get one domain (lecture publique via anon OK)
@router.get("/{domain_id}", response_model=Domain, response_model_exclude_none=True)
def get_domain(domain_id: UUID, token: str | None = Depends(get_bearer_token)):
    sb = supa_for_jwt(token) if token else sb_anon
    res = sb.table("domains").select(DOMAIN_COLUMNS).eq("id", str(domain_id)).single().execute()
    _raise_api_if_error(res, not_found_msg="Domain not found")
    return res.data

# ✅ Create domain (écriture: à faire côté serveur avec token utilisateur OU service role selon tes policies)
@router.post("/", status_code=201, response_model=Domain, response_model_exclude_none=True)
def create_domain(payload: DomainCreate, token: str | None = Depends(get_bearer_token)):
    if not token:
        # protège des inserts anonymes (sinon RLS refusera de toute façon)
        raise HTTPException(status_code=401, detail="Authentication required")
    sb = supa_for_jwt(token)
    data = payload.model_dump(exclude_none=True)
    res = sb.table("domains").insert(data).select(DOMAIN_COLUMNS).single().execute()
    _raise_api_if_error(res, default_status=403, not_found_msg="Insert refused (RLS/Policy).")
    return res.data

# ✅ Update domain
@router.put("/{domain_id}", response_model=Domain, response_model_exclude_none=True)
def update_domain(domain_id: UUID, updates: DomainUpdate, token: str | None = Depends(get_bearer_token)):
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")
    sb = supa_for_jwt(token)
    payload = updates.model_dump(exclude_unset=True, exclude_none=True)
    res = (
        sb.table("domains")
        .update(payload)
        .eq("id", str(domain_id))
        .select(DOMAIN_COLUMNS)
        .single()
        .execute()
    )
    _raise_api_if_error(res, default_status=403, not_found_msg="Domain not found")
    return res.data

# ✅ Delete domain
@router.delete("/{domain_id}", response_model=Domain, response_model_exclude_none=True)
def delete_domain(domain_id: UUID, token: str | None = Depends(get_bearer_token)):
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")
    sb = supa_for_jwt(token)
    res = (
        sb.table("domains")
        .delete()
        .eq("id", str(domain_id))
        .select(DOMAIN_COLUMNS)
        .single()
        .execute()
    )
    _raise_api_if_error(res, default_status=403, not_found_msg="Domain not found")
    return res.data
