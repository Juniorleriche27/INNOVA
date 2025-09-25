# routers/chatlaya.py (extrait pertinent)
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Optional
from services.intent import detect_intent
from services.router_ai import choose_and_complete
from services import rag_service as rag   # <-- fixed import
import os

router = APIRouter(tags=["chatlaya"])

class AskBody(BaseModel):
    question: str
    temperature: Optional[float] = None   # override optionnel
    max_tokens: Optional[int] = None      # override optionnel
    provider: Optional[str] = None        # "mistral" | "cohere" (optionnel)

@router.post("/ask")
def ask(body: AskBody):
    q = (body.question or "").strip()
    if not q:
        raise HTTPException(400, "question vide")

    cached = rag.cache_get(q)
    if cached:
        answer, sources = cached
        return {"answer": answer, "sources": sources, "cached": True}

    hits = rag.search(q, limit=8)
    context = ""
    top = [h for h in hits if h.get("score", 0) > 0.35][:5]
    if top:
        context = "\n\n".join((h.get("payload", {}) or {}).get("text", "") for h in top)

    intent = detect_intent(q)
    prompt = f"""Tu es Chat-LAYA. Réponds de façon concise et factuelle.
[QUESTION] {q}
[CONTEXTE] {context if context else "N/A"}
Si le contexte est insuffisant, dis-le clairement et propose une piste.
"""
    result = choose_and_complete(
        intent,
        prompt,
        override_temperature=body.temperature,
        override_max_tokens=body.max_tokens,
        force_provider=body.provider
    )
    answer = result.get("text", "(pas de texte)")
    sources = top

    try:
        rag.cache_put(q, answer, sources)
    except Exception:
        pass

    return {"answer": answer, "sources": sources, "provider": result.get("provider"), "model": result.get("model")}
