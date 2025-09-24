"""
RAG service pour Chat-LAYA (Qdrant Cloud)
- Connexion client
- Création collection si absente
- Ingestion (fichier -> chunks -> embeddings -> upsert)
- Recherche contextuelle (query_points)
- Helpers: upsert_texts, delete_by_doc_id

Compat Windows: pas de multiprocessing implicite.
"""

import os
from typing import Tuple, List, Iterable, Optional
from qdrant_client import QdrantClient, models
from qdrant_client.models import Distance, VectorParams, Filter, FieldCondition, MatchValue
from sentence_transformers import SentenceTransformer

# -------------------- Config --------------------
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION = "chatlaya_docs"

EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # 384 dims
VECTOR_SIZE = 384

# Client Qdrant (HTTP; prefer_grpc=False = compat réseaux stricts/Windows)
client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
    prefer_grpc=False,
    timeout=30.0,
)

# Modèle d'embedding
model = SentenceTransformer(EMBEDDING_MODEL)

# Crée la collection si elle n’existe pas
if not client.collection_exists(COLLECTION):
    client.create_collection(
        collection_name=COLLECTION,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
    )

# -------------------- Utils --------------------
def _chunk_text(text: str, size: int = 800) -> List[str]:
    return [text[i:i+size] for i in range(0, len(text), size)] if text else []


def upsert_texts(texts: Iterable[str], doc_id: Optional[str] = None) -> int:
    """
    Upsert d'une liste de passages (déjà découpés) avec embeddings.
    doc_id: identifiant logique de la source (permettra delete ciblé)
    Retourne le nombre de points insérés.
    """
    texts = [t for t in texts if t and t.strip()]
    if not texts:
        return 0

    vectors = model.encode(texts, normalize_embeddings=True).tolist()
    payloads = [{"text": t, **({"doc_id": doc_id} if doc_id else {})} for t in texts]

    points = []
    for v, p in zip(vectors, payloads):
        points.append(models.PointStruct(id=models.Uuid(uuid=None), vector=v, payload=p))  # id auto

    client.upsert(collection_name=COLLECTION, points=points)
    return len(points)


def delete_by_doc_id(doc_id: str) -> int:
    """
    Supprime tous les points dont payload.doc_id == doc_id.
    Retourne un indicatif (Qdrant ne renvoie pas le count exact).
    """
    if not doc_id:
        return 0

    cond = FieldCondition(key="doc_id", match=MatchValue(value=doc_id))
    client.delete(
        collection_name=COLLECTION,
        points_selector=models.FilterSelector(filter=Filter(must=[cond])),
    )
    return 1


# -------------------- API utilisée par les routers --------------------
def ingest_file(file) -> tuple[bool, str]:
    """
    Lit un fichier uploadé, découpe, embed, upsert dans Qdrant.
    """
    try:
        raw = file.file.read()
        text = raw.decode("utf-8", errors="ignore") if isinstance(raw, bytes) else str(raw)
        chunks = _chunk_text(text, 800)
        if not chunks:
            return False, "⚠️ Fichier vide ou non lisible"

        inserted = upsert_texts(chunks)
        return True, f"✅ {inserted} passages indexés"
    except Exception as e:
        return False, f"❌ Erreur ingestion: {e}"


def search_context(query: str, top_k: int = 4) -> Tuple[List[str], List[str]]:
    """
    Recherche contextuelle avec query_points.
    Retourne (passages, sources_ids)
    """
    if not query or not query.strip():
        return [], []

    try:
        vec = model.encode([query], normalize_embeddings=True)[0].tolist()

        # ✅ ici on passe le vecteur directement au param 'query'
        resp = client.query_points(
            collection_name=COLLECTION,
            query=vec,
            with_payload=True,
            with_vectors=False,
            limit=top_k
        )

        hits = resp.points
        passages = [h.payload.get("text", "") for h in hits]
        sources = [str(h.id) for h in hits]
        return passages, sources
    except Exception as e:
        print(f"❌ Erreur search_context/query_points: {e}")
        return [], []
