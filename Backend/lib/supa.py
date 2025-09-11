# lib/supa.py
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_ANON_KEY = os.environ["SUPABASE_ANON_KEY"]

# Client anonyme (pour les routes publiques seulement)
sb_anon = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

def supa_for_jwt(jwt: str | None):
    """
    Retourne un client Supabase qui enverra le JWT utilisateur
    dans les requêtes PostgREST (RLS côté DB verra l'utilisateur).
    """
    if not jwt:
        return sb_anon
    client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    # IMPORTANT: on authentifie le transport PostgREST avec le JWT
    client.postgrest.auth(jwt)
    return client
