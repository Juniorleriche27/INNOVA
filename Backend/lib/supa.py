# lib/supa.py
import os
from dotenv import load_dotenv
from postgrest import SyncPostgrestClient

load_dotenv()

SUPABASE_URL = os.environ["SUPABASE_URL"].rstrip("/")
SUPABASE_ANON_KEY = os.environ["SUPABASE_ANON_KEY"]

REST_URL = f"{SUPABASE_URL}/rest/v1"

def _headers_for_token(token: str | None):
    # Authorization: Bearer <jwt> (user) ou Bearer <anon_key> (anon)
    bearer = token if token else SUPABASE_ANON_KEY
    return {
        "apikey": SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {bearer}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

class _PgWrapper:
    """
    Petit wrapper pour retrouver l'API .table("...") de supabase-py,
    en la redirigeant vers .from_(...) du client PostgREST.
    """
    def __init__(self, token: str | None):
        self._client = SyncPostgrestClient(
            REST_URL,
            headers=_headers_for_token(token),
            schema="public",            # adapte si tu utilises un autre schéma
            timeout=120,                # idem pour timeout
            verify=True,                # TLS verify
            proxy=None,                 # pas de proxy
        )

    def table(self, name: str):
        return self._client.from_(name)

    # expose aussi .from_ si besoin direct
    def from_(self, name: str):
        return self._client.from_(name)

# Client anonyme (lecture publique)
sb_anon = _PgWrapper(token=None)

def supa_for_jwt(jwt: str | None):
    """
    Retourne un client PostgREST authentifié avec le JWT utilisateur s'il est fourni,
    sinon un client anonyme.
    """
    return _PgWrapper(token=jwt)
