from fastapi import APIRouter, HTTPException
from supabase import create_client
from schemas.domain import Domain, DomainCreate, DomainUpdate
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_ANON_KEY")
supabase = create_client(url, key)

router = APIRouter(tags=["Domains"])

@router.get("/", response_model=List[Domain])
def read_domains():
    res = supabase.table("domains").select("*").execute()
    return res.data

@router.get("/{domain_id}", response_model=Domain)
def read_domain(domain_id: str):
    res = supabase.table("domains").select("*").eq("id", domain_id).single().execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Domain not found")
    return res.data

@router.post("/", response_model=Domain)
def create_new_domain(domain: DomainCreate):
    res = supabase.table("domains").insert(domain.dict()).execute()
    return res.data[0]

@router.put("/{domain_id}", response_model=Domain)
def update_existing_domain(domain_id: str, updates: DomainUpdate):
    res = supabase.table("domains").update(updates.dict(exclude_unset=True)).eq("id", domain_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Domain not found")
    return res.data[0]

@router.delete("/{domain_id}", response_model=Domain)
def delete_existing_domain(domain_id: str):
    res = supabase.table("domains").delete().eq("id", domain_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Domain not found")
    return res.data[0]
