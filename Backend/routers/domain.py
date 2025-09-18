# routers/domain.py
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from uuid import UUID

from schemas.domain import Domain, DomainCreate, DomainUpdate
from lib.supa import supa_for_jwt, sb_anon
from deps.auth import get_bearer_token

router = APIRouter(tags=["domains"])

@router.get("/", response_model=List[Domain], response_model_exclude_none=True)
def list_domains():
    res = sb_anon.table("domains").select("*").execute()
    return res.data or []

@router.get("/{domain_id}", response_model=Domain, response_model_exclude_none=True)
def get_domain(domain_id: UUID):
    res = sb_anon.table("domains").select("*").eq("id", str(domain_id)).single().execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Domain not found")
    return res.data

@router.post("/", status_code=201, response_model=Domain, response_model_exclude_none=True)
def create_domain(payload: DomainCreate, token: str | None = Depends(get_bearer_token)):
    sb = supa_for_jwt(token)
    data = payload.model_dump(exclude_none=True)
    res = sb.table("domains").insert(data).select("*").single().execute()
    if not res.data:
        raise HTTPException(status_code=500, detail="Create failed")
    return res.data

@router.put("/{domain_id}", response_model=Domain, response_model_exclude_none=True)
def update_domain(domain_id: UUID, payload: DomainUpdate, token: str | None = Depends(get_bearer_token)):
    sb = supa_for_jwt(token)
    data = payload.model_dump(exclude_none=True, exclude_unset=True)
    res = sb.table("domains").update(data).eq("id", str(domain_id)).select("*").single().execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Domain not found")
    return res.data

@router.delete("/{domain_id}", response_model=Domain, response_model_exclude_none=True)
def delete_domain(domain_id: UUID, token: str | None = Depends(get_bearer_token)):
    sb = supa_for_jwt(token)
    res = sb.table("domains").delete().eq("id", str(domain_id)).select("*").single().execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Domain not found")
    return res.data
