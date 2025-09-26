# Backend/lib/supa.py
import os
from typing import Optional, Dict
from postgrest import SyncPostgrestClient

# ---- Config ----
SUPABASE_URL = (os.getenv("SUPABASE_URL", "") or "").rstrip("/")
if not SUPABASE_URL:
    raise RuntimeError("SUPABASE_URL manquant")

SUPABASE_REST_URL = os.getenv("SUPABASE_REST_URL") or (SUPABASE_URL + "/rest/v1")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")
if not SUPABASE_ANON_KEY:
    raise RuntimeError("SUPABASE_ANON_KEY manquant")

DEFAULT_HEADERS: Dict[str, str] = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "apikey": SUPABASE_ANON_KEY,
}

def _client_with_headers(headers: Dict[str, str]) -> SyncPostgrestClient:
    # postgrest==0.15.1 -> pas d'arguments verify/proxy/timeout
    return SyncPostgrestClient(
        SUPABASE_REST_URL,
        schema="public",
        headers=headers,
    )

# Client public (anon)
sb_anon: SyncPostgrestClient = _client_with_headers({
    **DEFAULT_HEADERS,
    "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
})

def supa_for_jwt(jwt: Optional[str]) -> SyncPostgrestClient:
    """
    Retourne un client PostgREST:
      - JWT utilisateur si fourni (Authorization: Bearer <jwt>)
      - Sinon client anonyme (RLS public)
    """
    if jwt:
        return _client_with_headers({
            **DEFAULT_HEADERS,
            "Authorization": f"Bearer {jwt}",
        })
    return sb_anon
