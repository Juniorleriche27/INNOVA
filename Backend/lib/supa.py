# lib/supa.py
import os
from supabase import create_client
from dotenv import load_dotenv

# Charger les variables d'environnement (.env doit contenir SUPABASE_URL et SUPABASE_ANON_KEY)
load_dotenv()
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_ANON_KEY = os.environ["SUPABASE_ANON_KEY"]

# Client anonyme (utilisé pour les routes publiques, rôle anon)
sb_anon = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

def supa_for_jwt(jwt: str | None):
    """
    Retourne un client Supabase configuré avec le JWT utilisateur.
    - Si pas de token, retourne le client anonyme (lecture publique uniquement).
    - Si token fourni, on authentifie le transport PostgREST avec ce JWT.
    """
    if not jwt:
        return sb_anon
    client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    client.postgrest.auth(jwt)
    return client
