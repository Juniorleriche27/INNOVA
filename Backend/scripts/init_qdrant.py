# scripts/init_qdrant.py
from __future__ import annotations
import os, time, uuid
from typing import Iterable, List
from qdrant_client import QdrantClient, models

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION = "chatlaya_docs"          # adapte si besoin
VECTOR_SIZE = 384                     # adapte à ton modèle d’embedding
DISTANCE = models.Distance.COSINE

def log(msg: str) -> None:
    print(time.strftime("[%H:%M:%S]"), msg, flush=True)

def seed_points(n: int = 5) -> Iterable[models.PointStruct]:
    # ⚠️ démo : remplace par tes vrais embeddings
    import numpy as np
    for i in range(n):
        vec = np.random.rand(VECTOR_SIZE).astype("float32").tolist()
        yield models.PointStruct(
            id=str(uuid.uuid4()),
            vector=vec,
            payload={"doc_id": f"seed-{i}", "text": f"chunk {i}"}
        )

def ensure_collection(client: QdrantClient) -> None:
    try:
        client.get_collection(COLLECTION)
        log("✅ Collection déjà existante")
    except Exception:
        log("⚠️ Collection absente → création…")
        client.recreate_collection(
            collection_name=COLLECTION,
            vectors_config=models.VectorParams(size=VECTOR_SIZE, distance=DISTANCE),
        )
        log("✅ Collection créée")

def upsert_in_batches(client: QdrantClient, points: List[models.PointStruct], batch_size: int = 128) -> None:
    total = len(points)
    if not total:
        log("ℹ️ Aucun point à uploader (seed vide).")
        return
    for i in range(0, total, batch_size):
        batch = points[i:i+batch_size]
        log(f"→ upsert batch {i//batch_size+1}/{(total-1)//batch_size+1} ({len(batch)} points)")
        client.upsert(collection_name=COLLECTION, points=batch, wait=True)
    log("✅ Upsert terminé")

def main() -> None:
    log(f"🔗 QDRANT_URL = {QDRANT_URL}")
    client = QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
        prefer_grpc=False,  # plus robuste sur Windows
        timeout=30.0,       # augmente si réseau lent (ex: 60.0)
        https=True,
    )
    log("ping collections…")
    _ = client.get_collections()
    ensure_collection(client)
    pts = list(seed_points(n=5))  # remplace par ton pipeline réel
    upsert_in_batches(client, pts, batch_size=64)

if __name__ == "__main__":
    main()
