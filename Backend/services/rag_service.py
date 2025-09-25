# services/rag.py
import hashlib
import json
import os
import re
from typing import List, Tuple, Optional

import psycopg2
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

EMB_DIM = int(os.getenv("EMBED_DIM", os.getenv("EMB_DIM", "384")))  # compat .env
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "innova_docs")
DATABASE_URL = os.getenv("DATABASE_URL")

def normalize_q(q: str) -> str:
    s = (q or "").strip().lower()
    s = re.sub(r"[^\w\s]", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s

def q_hash(q: str) -> str:
    return hashlib.sha256(normalize_q(q).encode("utf-8")).hexdigest()

def pg_conn():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL manquant")
    return psycopg2.connect(DATABASE_URL)

def cache_get(question: str) -> Optional[Tuple[str, list]]:
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
    with pg_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            insert into answers_cache(q_hash, question_norm, answer, sources)
            values(%s,%s,%s,%s)
            on conflict (q_hash) do nothing
            """,
            (q_hash(question), normalize_q(question), answer, json.dumps(sources)),
        )

def _ensure_collection(client: QdrantClient):
    # Crée la collection si elle n'existe pas
    collections = client.get_collections().collections
    names = {c.name for c in collections}
    if QDRANT_COLLECTION not in names:
        client.recreate_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=VectorParams(size=EMB_DIM, distance=Distance.COSINE),
        )

def embed(texts: List[str]) -> List[List[float]]:
    # sentence-transformers (CPU ok)
    from sentence_transformers import SentenceTransformer
    model_name = os.getenv("EMB_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    model = SentenceTransformer(model_name)
    return model.encode(texts, normalize_embeddings=True).tolist()

def search(query: str, limit: int = 8):
    client = QdrantClient(url=QDRANT_URL)
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
    client = QdrantClient(url=QDRANT_URL)
    _ensure_collection(client)
    vecs = embed(chunks)
    points = [
        PointStruct(id=None, vector=v, payload={"text": c, "source": source, "type": "doc"})
        for v, c in zip(vecs, chunks)
    ]
    client.upsert(collection_name=QDRANT_COLLECTION, points=points)
    return len(points)
