from fastapi import Header
from typing import Optional

def get_bearer_token(
    authorization: Optional[str] = Header(default=None, convert_underscores=False)
) -> Optional[str]:
    """
    Récupère le token Bearer depuis le header Authorization.
    Exemple: Authorization: Bearer <jwt>
    """
    if not authorization:
        return None
    parts = authorization.split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]
    return None
