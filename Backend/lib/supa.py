import os
from typing import Optional, Dict
from postgrest import SyncPostgrestClient

# ---- Config ----
SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
SUPABASE_REST_URL = os.getenv("SUPABASE_REST_URL") or (SUPABASE_URL + "/rest/v1")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")

DEFAULT_HEADERS: Dict[str, str] = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "apikey": SUPABASE_ANON_KEY or "",
}

def _client_with_headers(headers: Dict[str, str]) -> SyncPostgrestClient:
    # IMPORTANT: ne pas passer 'http_client' (incompatible avec postgrest>=0.19)
    return SyncPostgrestClient(
        SUPABASE_REST_URL,
        schema="public",
        headers=headers,
        timeout=120,
        verify=True,
        proxy=None,
    )

# Client public (anon)
sb_anon = _client_with_headers({
    **DEFAULT_HEADERS,
    "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
})

def supa_for_jwt(jwt: Optional[str]) -> SyncPostgrestClient:
    """
    Retourne un client PostgREST avec:
      - JWT utilisateur si fourni (Authorization: Bearer <jwt>)
      - Sinon client anonyme (RLS public)
    """
    if jwt:
        return _client_with_headers({
            **DEFAULT_HEADERS,
            "Authorization": f"Bearer {jwt}",
        })
    return sb_anon
