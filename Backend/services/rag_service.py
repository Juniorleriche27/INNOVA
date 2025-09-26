# services/rag.py
import hashlib
import json
import os
import re
from typing import List, Tuple, Optional

import psycopg  # psycopg v3
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct  # API "models"
# Si tu utilises qdrant_client>=1.7 avec http.models, remplace la ligne ci-dessus par:
# from qdrant_client.http import models as qm

# ---------------------------
# Configuration (ENV)
# ---------------------------
EMB_DIM = int(os.getenv("EMBED_DIM", os.getenv("EMB_DIM", "384")))  # compat .env
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")  # optionnel
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "innova_docs")
DATABASE_URL = os.getenv("DATABASE_URL")
EMB_MODEL_NAME = os.getenv("EMB_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# ---------------------------
# Singletons légers
# ---------------------------
_SENTS_MODEL = None  # cache du modèle d'embedding
_QDRANT_CLIENT = None  # cache du client Qdrant


def _qdrant() -> QdrantClient:
    global _QDRANT_CLIENT
    if _QDRANT_CLIENT is None:
        _QDRANT_CLIENT = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    return _QDRANT_CLIENT


def _encoder():
    """Lazy-load du modèle sentence-transformers."""
    global _SENTS_MODEL
    if _SENTS_MODEL is None:
        from sentence_transformers import SentenceTransformer
        _SENTS_MODEL = SentenceTransformer(EMB_MODEL_NAME)
    return _SENTS_MODEL


# ---------------------------
# Utils normalisation / hash
# ---------------------------
def normalize_q(q: str) -> str:
    s = (q or "").strip().lower()
    s = re.sub(r"[^\w\s]", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s


def q_hash(q: str) -> str:
    return hashlib.sha256(normalize_q(q).encode("utf-8")).hexdigest()


# ---------------------------
# Postgres cache (facultatif)
# ---------------------------
def pg_conn():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL manquant")
    return psycopg.connect(DATABASE_URL)


def cache_get(question: str) -> Optional[Tuple[str, list]]:
    """Retourne (answer, sources) si présent dans answers_cache, sinon None."""
    with pg_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "select answer, coalesce(sources,'[]'::jsonb) from answers_cache where q_hash=%s",
            (q_hash(question),),
        )
        row = cur.fetchone()
        if row:
            return row[0], row[1]
    return None


def cache_put(question: str, answer: str, sources: list):
    """Insère en cache, ignore si collision (q_hash PK/unique)."""
    with pg_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            insert into answers_cache(q_hash, question_norm, answer, sources)
            values(%s,%s,%s,%s)
            on conflict (q_hash) do nothing
            """,
            (q_hash(question), normalize_q(question), answer, json.dumps(sources)),
        )


# ---------------------------
# Qdrant helpers
# ---------------------------
def _ensure_collection(client: QdrantClient):
    """Crée la collection si absente."""
    cols = client.get_collections().collections
    names = {c.name for c in cols}
    if QDRANT_COLLECTION not in names:
        client.recreate_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=VectorParams(size=EMB_DIM, distance=Distance.COSINE),
        )


def embed(texts: List[str]) -> List[List[float]]:
    """
    Renvoie les embeddings normalisés (cosine ready).
    Utilise un modèle CPU-friendly par défaut (all-MiniLM-L6-v2, dim=384).
    """
    model = _encoder()
    # normalize_embeddings=True renvoie déjà des vecteurs L2-normalisés
    return model.encode(texts, normalize_embeddings=True).tolist()


# ---------------------------
# Recherche & Ingestion
# ---------------------------
def search(query: str, limit: int = 8):
    """
    Recherche sémantique simple dans Qdrant.
    Retourne une liste de hits: [{id, score, payload}, ...]
    """
    client = _qdrant()
    _ensure_collection(client)

    vec = embed([query])[0]
    res = client.search(collection_name=QDRANT_COLLECTION, query_vector=vec, limit=limit)
    hits = [
        {
            "id": str(p.id),
            "score": float(p.score),
            "payload": p.payload or {}
        }
        for p in res
    ]
    return hits


def upsert_chunks(chunks: List[str], source: str):
    """
    Upsert d'une liste de morceaux de texte avec leur source dans Qdrant.
    Retourne le nombre de points écrits.
    """
    if not chunks:
        return 0

    client = _qdrant()
    _ensure_collection(client)

    vecs = embed(chunks)
    points = [
        PointStruct(
            id=None,  # laisse Qdrant générer
            vector=v,
            payload={"text": c, "source": source, "type": "doc"},
        )
        for v, c in zip(vecs, chunks)
    ]
    # wait=True pour s'assurer que l'indexation est terminée avant de répondre
    client.upsert(collection_name=QDRANT_COLLECTION, points=points, wait=True)
    return len(points)
