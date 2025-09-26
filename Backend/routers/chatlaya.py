# Backend/routers/chatlaya.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator
import os
import cohere

router = APIRouter(tags=["chatlaya"])

class AskBody(BaseModel):
    question: str
    temperature: float | None = None
    max_tokens: int | None = None
    # Gardé pour compat, mais seul "cohere" est accepté
    provider: str | None = None

    @field_validator("question")
    @classmethod
    def not_empty(cls, v: str):
        if not v or not v.strip():
            raise ValueError("question vide")
        return v.strip()

@router.post("/ask")
def ask(body: AskBody):
    api_key = os.getenv("COHERE_API_KEY")
    if not api_key:
        raise HTTPException(500, "COHERE_API_KEY manquante sur le backend")

    model = os.getenv("COHERE_MODEL", "command-r")
    temperature = 0.3 if body.temperature is None else float(body.temperature)
    max_tokens = 300 if body.max_tokens is None else int(body.max_tokens)

    # Refuse tout autre provider
    if body.provider and body.provider.lower() != "cohere":
        raise HTTPException(400, f"Seul 'cohere' est supporté (reçu: {body.provider!r})")

    try:
        co = cohere.Client(api_key=api_key)
        # IMPORTANT : Cohere attend 'message=' (string), pas 'messages='
        resp = co.chat(
            model=model,
            message=body.question,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        text = (getattr(resp, "text", "") or "").strip() or "(réponse vide)"

        usage = None
        try:
            m = getattr(resp, "meta", None)
            if m and getattr(m, "tokens", None):
                usage = {
                    "input_tokens": getattr(m.tokens, "input_tokens", None),
                    "output_tokens": getattr(m.tokens, "output_tokens", None),
                    "total_tokens": getattr(m.tokens, "total_tokens", None),
                }
        except Exception:
            usage = None

    except Exception as e:
        # renvoie une 502 pour que le front affiche l'erreur proprement
        raise HTTPException(502, f"Echec Cohere: {e}")

    return {
        "answer": text,
        "provider": "cohere",
        "model": model,
        "tokens": usage,
    }
