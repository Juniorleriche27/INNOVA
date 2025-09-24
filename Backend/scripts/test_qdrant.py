import os
from qdrant_client import QdrantClient

# Lit les variables d'env (tu les as déjà définies)
URL = os.getenv("QDRANT_URL")
KEY = os.getenv("QDRANT_API_KEY")

if not URL or not KEY:
    raise SystemExit("❌ QDRANT_URL / QDRANT_API_KEY manquants dans l'environnement")

c = QdrantClient(
    url=URL,
    api_key=KEY,
    prefer_grpc=False,  # HTTP-only (réseaux stricts/Windows OK)
    timeout=30.0
)

# vecteur factice de dimension 384
vec = [0.0] * 384

# ✅ query_points: on passe le vecteur directement à 'query'
res = c.query_points(
    collection_name="chatlaya_docs",
    query=vec,
    with_payload=True,
    with_vectors=False,
    limit=3
)

print(res.points)
