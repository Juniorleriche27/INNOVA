# Backend/lib/supa.py
from __future__ import annotations

import os
from functools import lru_cache
from typing import Dict, Optional, TypedDict

from postgrest import SyncPostgrestClient


class _SupabaseConfig(TypedDict):
    rest_url: str
    anon_key: str


def _build_config() -> _SupabaseConfig:
    """Charge la configuration Supabase depuis les variables d'environnement."""

    supabase_url = (os.getenv("SUPABASE_URL") or "").rstrip("/")
    rest_url = (os.getenv("SUPABASE_REST_URL") or "").rstrip("/")

    if not rest_url:
        if not supabase_url:
            raise RuntimeError(
                "SUPABASE_URL manquant. Configure SUPABASE_URL ou SUPABASE_REST_URL pour utiliser l'API."
            )
        rest_url = f"{supabase_url}/rest/v1"

    anon_key = (os.getenv("SUPABASE_ANON_KEY") or "").strip()
    if not anon_key:
        raise RuntimeError("SUPABASE_ANON_KEY manquant")

    return {"rest_url": rest_url, "anon_key": anon_key}


@lru_cache()
def _config() -> _SupabaseConfig:
    return _build_config()


def _default_headers() -> Dict[str, str]:
    cfg = _config()
    return {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "apikey": cfg["anon_key"],
    }


def _client_with_headers(headers: Dict[str, str]) -> SyncPostgrestClient:
    """Instancie un client PostgREST avec les en-têtes fournis."""

    cfg = _config()
    # postgrest==0.15.1 -> pas d'arguments verify/proxy/timeout
    return SyncPostgrestClient(
        cfg["rest_url"],
        schema="public",
        headers=headers,
    )


@lru_cache()
def get_sb_anon() -> SyncPostgrestClient:
    """Client Supabase anonyme (Bearer anon key)."""

    headers = {
        **_default_headers(),
        "Authorization": f"Bearer {_config()['anon_key']}",
    }
    return _client_with_headers(headers)


def supa_for_jwt(jwt: Optional[str]) -> SyncPostgrestClient:
    """
    Retourne un client PostgREST:
      - JWT utilisateur si fourni (Authorization: Bearer <jwt>)
      - Sinon client anonyme (RLS public)
    """

    if jwt:
        headers = {
            **_default_headers(),
            "Authorization": f"Bearer {jwt}",
        }
        return _client_with_headers(headers)
    return get_sb_anon()
