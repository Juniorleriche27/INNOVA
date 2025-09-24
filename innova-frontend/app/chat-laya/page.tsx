"use client";

import React, { useEffect, useState } from "react";

/** Message échangé avec le backend */
type Msg = { role: "user" | "assistant"; content: string };

/** URL de l’API (Render) lue depuis l’env publique Next */
const API_URL: string | undefined = process.env.NEXT_PUBLIC_API_URL;

export default function ChatLayaPage() {
  const [messages, setMessages] = useState<Msg[]>([
    { role: "assistant", content: "Bienvenue sur Chat-LAYA 👋" },
  ]);
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Petit check pour aider au debug (n'affecte pas le build)
  useEffect(() => {
    if (!API_URL) {
      console.warn(
        "NEXT_PUBLIC_API_URL est manquante. Configure-la dans Vercel → Project → Environment Variables."
      );
    }
  }, []);

  async function sendMessage() {
    if (!text.trim()) return;
    setError(null);

    const next: Msg[] = [...messages, { role: "user", content: text }];
    setMessages(next);
    setText("");
    setLoading(true);

    try {
      if (!API_URL) throw new Error("NEXT_PUBLIC_API_URL non définie");

      const res = await fetch(`${API_URL}/chatlaya/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: next }),
      });

      if (!res.ok) {
        const body = await res.text();
        throw new Error(`HTTP ${res.status} – ${body}`);
      }

      const data: unknown = await res.json();
      const answer =
        (data as { answer?: string })?.answer ??
        (data as { message?: string })?.message ??
        "Réponse reçue.";

      setMessages([...next, { role: "assistant", content: String(answer) }]);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Erreur inconnue");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="max-w-3xl mx-auto px-4 py-8 space-y-6">
      <h1 className="text-2xl font-bold">💬 Chat-LAYA</h1>

      {error && (
        <div className="text-sm text-red-600" role="alert">
          {error}
        </div>
      )}

      <div className="space-y-3">
        {messages.map((m, i) => (
          <div
            key={i}
            className={`rounded-lg p-3 ${
              m.role === "user"
                ? "bg-gray-100 text-gray-800"
                : "bg-blue-50 text-blue-900"
            }`}
          >
            <span className="font-medium mr-2">
              {m.role === "user" ? "Vous" : "LAYA"}:
            </span>
            {m.content}
          </div>
        ))}
      </div>

      <div className="flex gap-2">
        <input
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Votre message…"
          className="flex-1 border rounded-lg px-3 py-2"
          disabled={loading}
        />
        <button
          onClick={sendMessage}
          disabled={loading}
          className="px-4 py-2 rounded-lg bg-black text-white disabled:opacity-50"
        >
          {loading ? "Envoi…" : "Envoyer"}
        </button>
      </div>
    </main>
  );
}
