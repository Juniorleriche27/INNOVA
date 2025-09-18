import os
from dotenv import load_dotenv
from postgrest import SyncPostgrestClient

load_dotenv()

SUPABASE_URL = os.environ["SUPABASE_URL"].rstrip("/")
SUPABASE_ANON_KEY = os.environ["SUPABASE_ANON_KEY"]
REST_URL = f"{SUPABASE_URL}/rest/v1"

def _headers_for_token(token: str | None):
    bearer = token if token else SUPABASE_ANON_KEY
    return {
        "apikey": SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {bearer}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

class _PgWrapper:
    def __init__(self, token: str | None):
        self._client = SyncPostgrestClient(
            REST_URL,
            headers=_headers_for_token(token),
            schema="public",
            timeout=120,
            verify=True,
            proxy=None,
        )

    def table(self, name: str):
        return self._client.from_(name)

    def from_(self, name: str):
        return self._client.from_(name)

sb_anon = _PgWrapper(token=None)

def supa_for_jwt(jwt: str | None):
    return _PgWrapper(token=jwt)
