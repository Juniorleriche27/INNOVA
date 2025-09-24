"""
Choix du moteur IA (OpenAI, Ollama, DeepL…)
Ici on met un vrai appel à OpenAI en exemple.
"""
import os
from openai import OpenAI
from typing import List, Optional
from schemas.chat_schema import ChatMessage

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

def chat_completion(messages: List[ChatMessage], context: Optional[str] = None) -> str:
    if not client:
        return "⚠️ OpenAI non configuré"

    chat_history = [{"role": m.role, "content": m.content} for m in messages]

    if context:
        chat_history.insert(0, {"role": "system", "content": f"Contexte:\n{context}"})

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=chat_history,
        temperature=0.5,
        max_tokens=500,
    )

    return resp.choices[0].message.content.strip()
