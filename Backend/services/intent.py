# services/intent.py
from dataclasses import dataclass

@dataclass
class IntentResult:
    intent: str           # "summarize" | "translate" | "qa" | "gen_long" | ...
    complexity: int       # 1..5
    domain_hint: str|None # ex: "finance_public", "uemoa", etc.

def detect_intent(prompt: str) -> IntentResult:
    p = (prompt or "").strip().lower()

    # Règles simples (extensibles)
    if len(p) < 180 and any(k in p for k in ["résume", "résumé", "resume", "summary", "synthèse", "synthese"]):
        return IntentResult("summarize", 2, None)

    if any(k in p for k in ["tradu", "translate", "traduis", "en français", "in english"]):
        return IntentResult("translate", 1, None)

    if any(k in p for k in ["loi", "code général", "directive uemoa", "taux tva", "budget", "marchés publics", "douane"]):
        return IntentResult("qa", 3, "finance_public")

    # Longueur → complexité
    complexity = 5 if len(p) > 1200 else (4 if len(p) > 600 else 3)
    return IntentResult("gen_long", complexity, None)
