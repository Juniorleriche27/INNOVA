"use client";

import { useState } from "react";

const API =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/+$/, "") || "http://127.0.0.1:8000";

type Hit = {
  id: string;
  score: number;
  payload: { text?: string; source?: string; [k: string]: unknown } | null;
};

export default function ChatLayaPage() {
  const [q, setQ] = useState("");
  const [hits, setHits] = useState<Hit[]>([]);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  async function onSearch(e: React.FormEvent) {
    e.preventDefault();
    if (!q.trim()) return;
    setLoading(true);
    setErr(null);
    setHits([]);
    try {
      const res = await fetch(
        `${API}/chatlaya/search?query=${encodeURIComponent(q)}&limit=5`,
        { cache: "no-store" }
      );
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setHits((data?.hits || []) as Hit[]);
    } catch (e: any) {
      setErr(e?.message || "Erreur inconnue");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="max-w-3xl mx-auto px-4 py-10">
      <h1 className="text-3xl font-bold mb-2">Chat-LAYA (RAG)</h1>
      <p className="text-gray-600 mb-6">
        Recherche sémantique sur les documents ingérés.
      </p>

      <form onSubmit={onSearch} className="flex gap-2 mb-6">
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Pose ta question…"
          className="flex-1 border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          type="submit"
          className="rounded bg-blue-600 text-white px-4 py-2 hover:bg-blue-700 disabled:opacity-50"
          disabled={loading}
        >
          {loading ? "Recherche…" : "Rechercher"}
        </button>
      </form>

      {err && (
        <div className="mb-4 rounded border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {err}
        </div>
      )}

      <div className="space-y-3">
        {hits.map((h) => (
          <div
            key={h.id}
            className="rounded border px-4 py-3 bg-white shadow-sm"
          >
            <div className="text-sm text-gray-500">score: {h.score.toFixed(4)}</div>
            <div className="font-medium">{h.payload?.text || "—"}</div>
            {h.payload?.source && (
              <div className="text-xs text-gray-500 mt-1">
                source: {String(h.payload.source)}
              </div>
            )}
          </div>
        ))}
        {!loading && !err && hits.length === 0 && (
          <div className="text-gray-600">Aucun résultat pour l’instant.</div>
        )}
      </div>
    </main>
  );
}
