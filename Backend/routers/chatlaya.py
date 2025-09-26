# Backend/routers/chatlaya.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator
import os
import logging

from services.router_ai import choose_and_complete

router = APIRouter()
logger = logging.getLogger(__name__)

class AskBody(BaseModel):
    question: str
    temperature: float | None = None
    max_tokens: int | None = None
    provider: str | None = None  # "mistral" | "cohere"

    @field_validator("question")
    @classmethod
    def not_empty(cls, v: str):
        if not v or not v.strip():
            raise ValueError("question vide")
        return v.strip()

@router.post("/ask")
def ask(body: AskBody):
    # Defaults
    provider = (body.provider or "mistral").lower()
    temperature = body.temperature if body.temperature is not None else 0.3
    max_tokens = body.max_tokens if body.max_tokens is not None else 300

    # Vérification des clés / modèles
    if provider == "mistral":
        if not os.getenv("MISTRAL_API_KEY"):
            raise HTTPException(500, "MISTRAL_API_KEY manquante sur le backend")
        model = os.getenv("MISTRAL_MODEL", "mistral-small-latest")
    elif provider == "cohere":
        if not os.getenv("COHERE_API_KEY"):
            raise HTTPException(500, "COHERE_API_KEY manquante sur le backend")
        model = os.getenv("COHERE_MODEL", "command-r-plus")
    else:
        raise HTTPException(400, f"Provider non supporté: {provider}")

    prompt = f"Réponds brièvement et clairement.\nQuestion: {body.question}"

    try:
        result = choose_and_complete(
            intent="qa",
            prompt=prompt,
            override_temperature=temperature,
            override_max_tokens=max_tokens,
            force_provider=provider,
            force_model=model,
        )
    except Exception as e:
        logger.exception("Erreur Chat-LAYA")
        raise HTTPException(502, f"Echec provider {provider}: {e}")

    return {
        "answer": result.get("text", "").strip() or "(réponse vide)",
        "provider": result.get("provider", provider),
        "model": result.get("model", model),
        "tokens": result.get("usage"),
    }
