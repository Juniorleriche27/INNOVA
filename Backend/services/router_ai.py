# services/router_ai.py
import os
import time
from typing import Dict, Any, Optional
from .intent import IntentResult

# On ne retient que Cohere. La présence d'une clé Mistral n'influence plus le choix.
USE_COHERE = bool(os.getenv("COHERE_API_KEY"))

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

def _params_for(intent_name: str, override_temp: Optional[float], override_max: Optional[int]) -> tuple[float, int]:
    base = PARAMS_BY_INTENT.get(intent_name, PARAMS_BY_INTENT["default"])
    t = override_temp if override_temp is not None else base["temperature"]
    m = override_max  if override_max  is not None else base["max_tokens"]
    return t, m

# ---- Cohere ----
def _cohere_complete(prompt: str, temperature: float, max_tokens: int, model_name: Optional[str] = None) -> Dict[str, Any]:
    import cohere
    api_key = os.getenv("COHERE_API_KEY")
    if not api_key:
        # On renvoie une erreur contrôlée (le caller peut la formater)
        return {"provider": "error", "model": "-", "text": "COHERE_API_KEY manquante", "latency_ms": 0}

    model = model_name or os.getenv("COHERE_MODEL", "command-r")
    t0 = time.time()
    try:
        client = cohere.Client(api_key)
        # Le SDK Cohere accepte soit `message=str`, soit `messages=[...]` selon version.
        # Ici on utilise `message=` pour rester compatible avec le code existant.
        resp = client.chat(
            model=model,
            message=prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )
        text = (getattr(resp, "text", "") or "").strip() or "(réponse vide)"
        return {
            "provider": "cohere",
            "model": model,
            "text": text,
            "latency_ms": int((time.time() - t0) * 1000)
        }
    except Exception as e:
        return {"provider": "error", "model": model, "text": f"Erreur Cohere: {e}", "latency_ms": 0}

# ---- Sélection + exécution (Cohere-only) ----
def choose_and_complete(
    intent: IntentResult,
    prompt: str,
    override_temperature: Optional[float] = None,
    override_max_tokens: Optional[int] = None,
    force_provider: Optional[str] = None,
    **kwargs: Any,  # <--- on avale tout (ex: force_model) pour éviter "unexpected keyword argument"
) -> Dict[str, Any]:
    """
    Routeur de complétion Cohere-only.
    - Ignore force_provider (on force Cohere).
    - Supporte un "force_model" éventuel via kwargs sans planter.
    """
    temperature, max_tokens = _params_for(intent.intent, override_temperature, override_max_tokens)

    # Support optionnel d’un modèle imposé depuis l’UI sans crasher si absent
    model_name = None
    try:
        model_name = kwargs.get("force_model") or os.getenv("COHERE_MODEL", "command-r")
    except Exception:
        model_name = os.getenv("COHERE_MODEL", "command-r")

    # Toujours Cohere
    if not USE_COHERE:
        return {"provider": "none", "model": "none", "text": "Aucun provider IA configuré (Cohere manquant).", "latency_ms": 0}

    return _cohere_complete(prompt, temperature, max_tokens, model_name=model_name)
