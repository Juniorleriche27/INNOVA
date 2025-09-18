# deps/auth.py
from fastapi import Header
from typing import Optional

def get_bearer_token(
    authorization: Optional[str] = Header(default=None, convert_underscores=False)
) -> Optional[str]:
    """
    Extrait le token Bearer depuis l'en-tête HTTP Authorization.
    Exemple attendu :
        Authorization: Bearer <token>
    Retourne:
        - le token (str) si trouvé,
        - None si absent ou mal formé.
    """
    if not authorization:
        return None

    parts = authorization.strip().split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]

    # Optionnel: tu pourrais logger ici si besoin
    return None
