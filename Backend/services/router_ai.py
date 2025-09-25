# services/router_ai.py
import os
import time
from typing import Dict, Any, Optional
from .intent import IntentResult

USE_MISTRAL = bool(os.getenv("MISTRAL_API_KEY"))
USE_COHERE  = bool(os.getenv("COHERE_API_KEY"))

# ---- Paramètres par intent (avec fallback .env) ----
def _f(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except Exception:
        return default

def _i(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except Exception:
        return default

PARAMS_BY_INTENT = {
    "translate": {"temperature": _f("TEMP_TRANSLATE", 0.2), "max_tokens": _i("TOKENS_TRANSLATE", 500)},
    "summarize": {"temperature": _f("TEMP_SUMMARIZE", 0.2), "max_tokens": _i("TOKENS_SUMMARIZE", 500)},
    "qa":        {"temperature": _f("TEMP_QA", 0.3),        "max_tokens": _i("TOKENS_QA", 700)},
    "gen_long":  {"temperature": _f("TEMP_GEN_LONG", 0.5),  "max_tokens": _i("TOKENS_GEN_LONG", 1200)},
    "default":   {"temperature": _f("TEMP_DEFAULT", 0.4),   "max_tokens": _i("TOKENS_DEFAULT", 800)},
}

def _params_for(intent_name: str, override_temp: Optional[float], override_max: Optional[int]) -> tuple[float,int]:
    base = PARAMS_BY_INTENT.get(intent_name, PARAMS_BY_INTENT["default"])
    t = override_temp if override_temp is not None else base["temperature"]
    m = override_max  if override_max  is not None else base["max_tokens"]
    return t, m

# ---- Providers ----
def _mistral_complete(prompt: str, temperature: float, max_tokens: int) -> Dict[str, Any]:
    import requests
    model = os.getenv("MISTRAL_MODEL", "mistral-small-latest")
    headers = {"Authorization": f"Bearer {os.getenv('MISTRAL_API_KEY')}"}
    t0 = time.time()
    r = requests.post(
        "https://api.mistral.ai/v1/chat/completions",
        headers=headers,
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens
        },
        timeout=60
    )
    r.raise_for_status()
    data = r.json()
    text = data["choices"][0]["message"]["content"]
    return {"provider": "mistral", "model": model, "text": text, "latency_ms": int((time.time() - t0) * 1000)}

def _cohere_complete(prompt: str, temperature: float, max_tokens: int) -> Dict[str, Any]:
    import cohere
    client = cohere.Client(os.getenv("COHERE_API_KEY"))
    model = os.getenv("COHERE_MODEL", "command-r-plus")
    t0 = time.time()
    resp = client.chat(
        model=model,
        message=prompt,
        temperature=temperature,
        max_tokens=max_tokens
    )
    text = resp.text
    return {"provider": "cohere", "model": model, "text": text, "latency_ms": int((time.time() - t0) * 1000)}

# ---- Sélection + exécution (un seul provider) ----
def choose_and_complete(
    intent: IntentResult,
    prompt: str,
    override_temperature: Optional[float] = None,
    override_max_tokens: Optional[int] = None,
    force_provider: Optional[str] = None  # "mistral" | "cohere"
) -> Dict[str, Any]:

    temperature, max_tokens = _params_for(intent.intent, override_temperature, override_max_tokens)

    # Force provider si demandé
    if force_provider == "mistral" and USE_MISTRAL:
        return _mistral_complete(prompt, temperature, max_tokens)
    if force_provider == "cohere" and USE_COHERE:
        return _cohere_complete(prompt, temperature, max_tokens)

    # Politique par intent (fallback si indispo)
    try:
        if intent.intent in ("translate", "summarize") and USE_MISTRAL:
            return _mistral_complete(prompt, temperature, max_tokens)

        if intent.intent == "qa" and USE_COHERE:
            return _cohere_complete(prompt, temperature, max_tokens)

        if intent.intent == "gen_long" and USE_COHERE:
            return _cohere_complete(prompt, temperature, max_tokens)

        if USE_MISTRAL:
            return _mistral_complete(prompt, temperature, max_tokens)

        if USE_COHERE:
            return _cohere_complete(prompt, temperature, max_tokens)

        return {"provider": "none", "model": "none", "text": "Aucun provider IA configuré.", "latency_ms": 0}
    except Exception as e:
        return {"provider": "error", "model": "-", "text": f"Erreur provider: {e}", "latency_ms": 0}
