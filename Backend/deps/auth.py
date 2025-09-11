from fastapi import Header

def get_bearer_token(authorization: str | None = Header(default=None, convert_underscores=False)):
    """
    Récupère le token Bearer depuis le header Authorization
    Exemple attendu :
    Authorization: Bearer <token>
    """
    if not authorization:
        return None
    parts = authorization.split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]
    return None
