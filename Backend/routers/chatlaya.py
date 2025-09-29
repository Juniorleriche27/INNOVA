from __future__ import annotations

import os
import re
from typing import List, Optional

from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from pydantic import BaseModel, field_validator

from services.intent import detect_intent
from services.router_ai import choose_and_complete

try:  # pragma: no cover - dépendances optionnelles
    from services import rag_service
except Exception as exc:  # pragma: no cover - pas de RAG configuré
    rag_service = None  # type: ignore[assignment]
    _rag_import_error: Optional[Exception] = exc
else:  # pragma: no cover - dépendances présentes
    _rag_import_error = None


router = APIRouter(tags=["chatlaya"])

_DEFAULT_PROMPT = (
    "Tu es Chat-LAYA, l'assistant IA de la plateforme INNOVA+. "
    "Réponds en français, de façon structurée et concise. "
    "Si le contexte ne contient pas l'information demandée, indique-le clairement."
)
MAX_TOP_K = 12


class AskBody(BaseModel):
    question: str
    temperature: float | None = None
    max_tokens: int | None = None
    top_k: int | None = None
    # Gardé pour compat, mais seul "cohere" est accepté
    provider: str | None = None

    @field_validator("question")
    @classmethod
    def not_empty(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("question vide")
        return value.strip()

    @field_validator("top_k")
    @classmethod
    def validate_top_k(cls, value: Optional[int]) -> Optional[int]:
        if value is None:
            return None
        if value < 0:
            raise ValueError("top_k doit être positif")
        return value


@router.post("/ask")
def ask(body: AskBody):
    provider = (body.provider or "cohere").lower()
    if provider != "cohere":
        raise HTTPException(status_code=400, detail=f"Seul 'cohere' est supporté (reçu: {body.provider!r})")

    question = body.question.strip()
    top_k = body.top_k if body.top_k is not None else 4
    top_k = max(0, min(int(top_k), MAX_TOP_K))

    sources: List[dict] = []
    rag_error: Optional[str] = None
    if top_k > 0:
        if rag_service is None:
            if _rag_import_error:
                rag_error = f"Service RAG indisponible: {_rag_import_error}"
            else:
                rag_error = "Service RAG non configuré"
        else:
            try:
                sources = rag_service.search(question, limit=top_k)
            except Exception as exc:  # pragma: no cover - dépendances externes
                rag_error = str(exc)
                sources = []

    context_parts = []
    for hit in sources[:top_k]:
        payload = hit.get("payload") or {}
        snippet = str(payload.get("text") or "").strip()
        if not snippet:
            continue
        meta = payload.get("title") or payload.get("source")
        if meta:
            context_parts.append(f"Source: {meta}\n{snippet}")
        else:
            context_parts.append(snippet)
    context = "\n\n".join(context_parts).strip()

    system_prompt = os.getenv("CHATLAYA_PROMPT", _DEFAULT_PROMPT)
    prompt_sections = [system_prompt]
    if context:
        prompt_sections.append("Contexte documentaire:\n" + context)
    prompt_sections.append(f"Question:\n{question}")
    prompt_sections.append("Réponse détaillée:")
    prompt = "\n\n".join(prompt_sections)

    intent = detect_intent(question)
    completion = choose_and_complete(
        intent,
        prompt,
        override_temperature=body.temperature,
        override_max_tokens=body.max_tokens,
        force_provider="cohere",
        force_model=os.getenv("COHERE_MODEL", "command-r"),
    )

    provider_name = completion.get("provider") or "cohere"
    answer_text = (completion.get("text") or "").strip() or "(réponse vide)"

    if provider_name in {"error", "none"}:
        raise HTTPException(status_code=502, detail=answer_text)

    response = {
        "answer": answer_text,
        "provider": provider_name,
        "model": completion.get("model") or os.getenv("COHERE_MODEL", "command-r"),
        "latency_ms": completion.get("latency_ms"),
        "tokens": completion.get("tokens"),
        "sources": sources,
    }
    if rag_error:
        response["rag_error"] = rag_error
    return response


@router.get("/search")
def search(query: str = Query(..., min_length=1), limit: int = Query(8, ge=1, le=MAX_TOP_K)):
    q = query.strip()
    if not q:
        raise HTTPException(status_code=400, detail="Paramètre 'query' obligatoire")

    if rag_service is None:
        raise HTTPException(status_code=503, detail="Service RAG non disponible")

    try:
        hits = rag_service.search(q, limit=limit)
    except Exception as exc:  # pragma: no cover - dépendances externes
        raise HTTPException(status_code=502, detail=f"Recherche indisponible: {exc}")

    return {"query": q, "hits": hits}


@router.post("/ingest")
async def ingest(files: List[UploadFile] = File(..., alias="file")):
    if rag_service is None:
        raise HTTPException(status_code=503, detail="Service RAG non disponible")

    if not files:
        raise HTTPException(status_code=400, detail="Aucun fichier reçu")

    total_chunks = 0
    errors: List[dict[str, str]] = []

    for upload in files:
        try:
            raw = await upload.read()
            if not raw:
                continue

            text = _decode_bytes(raw)
            if text is None:
                errors.append({
                    "filename": upload.filename or "(sans nom)",
                    "error": "Encodage de fichier non supporté",
                })
                continue

            chunks = _chunk_text(text)
            if not chunks:
                continue

            try:
                total_chunks += rag_service.upsert_chunks(chunks, source=upload.filename or "document")
            except Exception as exc:  # pragma: no cover - dépendances externes
                errors.append({
                    "filename": upload.filename or "(sans nom)",
                    "error": str(exc),
                })
        finally:
            await upload.close()

    return {"status": "ok", "chunks": total_chunks, "errors": errors}


def _decode_bytes(raw: bytes) -> Optional[str]:
    for encoding in ("utf-8", "utf-16", "latin-1"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return None


def _chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> List[str]:
    clean = re.sub(r"\s+", " ", text).strip()
    if not clean:
        return []

    chunks: List[str] = []
    start = 0
    length = len(clean)
    while start < length:
        end = min(length, start + chunk_size)
        chunk = clean[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= length:
            break
        start = max(end - overlap, start + 1)
    return chunks
