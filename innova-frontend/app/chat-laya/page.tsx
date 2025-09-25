// innova-frontend/app/chat-laya/page.tsx
"use client";

import { useEffect, useMemo, useRef, useState } from "react";

/** Base API */
const API =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/+$/, "") || "http://127.0.0.1:8000";

/** Types basiques */
type Hit = {
  id: string;
  score: number;
  payload: {
    text?: string;
    title?: string;
    source?: string;
    url?: string;
    type?: string;
    [k: string]: unknown;
  } | null;
};

type ChatTurn = { role: "user" | "assistant"; text: string; sources?: Hit[] };

/** Petit util */
const escapeRe = (s: string) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

/** Page */
export default function ChatLayaPage() {
  /** Onglets */
  const [tab, setTab] = useState<"search" | "chat">("search");

  /** Recherche */
  const [q, setQ] = useState("");
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [hits, setHits] = useState<Hit[]>([]);
  const [ran, setRan] = useState(false);
  const [elapsed, setElapsed] = useState<number | null>(null);

  /** Filtres */
  const [filterSource, setFilterSource] = useState<string>("all");
  const [filterType, setFilterType] = useState<string>("all");

  /** Chat */
  const [turns, setTurns] = useState<ChatTurn[]>([]);
  const [prompt, setPrompt] = useState("");
  const [thinking, setThinking] = useState(false);

  /** Upload */
  const [uploading, setUploading] = useState(false);
  const [uploadErr, setUploadErr] = useState<string | null>(null);

  /** UI refs */
  const inputRef = useRef<HTMLInputElement | null>(null);
  const scrollRef = useRef<HTMLDivElement | null>(null);

  /** Dark mode toggle */
  const [dark, setDark] = useState<boolean>(() =>
    typeof window === "undefined"
      ? false
      : localStorage.getItem("innova.theme") === "dark" ||
        (matchMedia?.("(prefers-color-scheme: dark)").matches ?? false)
  );
  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
    localStorage.setItem("innova.theme", dark ? "dark" : "light");
  }, [dark]);

  /** Historique */
  useEffect(() => {
    // restaurer historique
    try {
      const storedQ = localStorage.getItem("innova.rag.lastQ");
      if (storedQ) setQ(storedQ);
      const storedTurns = localStorage.getItem("innova.chat.turns");
      if (storedTurns) setTurns(JSON.parse(storedTurns));
    } catch {}
  }, []);
  useEffect(() => {
    try {
      localStorage.setItem("innova.chat.turns", JSON.stringify(turns.slice(-50)));
    } catch {}
  }, [turns]);
  useEffect(() => {
    try {
      if (q) localStorage.setItem("innova.rag.lastQ", q);
    } catch {}
  }, [q]);

  /** Raccourcis clavier */
  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setTab("search");
        inputRef.current?.focus();
      }
      if (e.key === "Escape" && q) setQ("");
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [q]);

  /** Auto-scroll chat */
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
    }
  }, [turns, thinking]);

  /** Actions : Recherche */
  async function runSearch(query: string) {
    const t0 = performance.now();
    setLoading(true);
    setErr(null);
    setHits([]);
    setRan(true);
    setElapsed(null);
    try {
      const res = await fetch(
        `${API}/chatlaya/search?query=${encodeURIComponent(query)}&limit=12`,
        { cache: "no-store" }
      );
      if (!res.ok) throw new Error(await res.text());
      const data = (await res.json()) as { hits?: Hit[] };
      setHits(data?.hits ?? []);
    } catch (e: any) {
      setErr(e?.message || "Erreur inconnue");
    } finally {
      setLoading(false);
      setElapsed(performance.now() - t0);
    }
  }
  function onSubmitSearch(e: React.FormEvent) {
    e.preventDefault();
    if (q.trim()) runSearch(q.trim());
  }

  /** Actions : Chat (simple non-stream, compatible backend typique) */
  async function runChatAsk(text: string) {
    const user: ChatTurn = { role: "user", text };
    setTurns((t) => [...t, user]);
    setThinking(true);
    try {
      const res = await fetch(`${API}/chatlaya/ask`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ question: text }),
      });
      if (!res.ok) throw new Error(await res.text());
      const data = (await res.json()) as { answer: string; sources?: Hit[] };
      const assistant: ChatTurn = { role: "assistant", text: data.answer, sources: data.sources };
      setTurns((t) => [...t, assistant]);
    } catch (e: any) {
      const assistant: ChatTurn = {
        role: "assistant",
        text: `❌ Erreur: ${e?.message || "inconnue"}`,
      };
      setTurns((t) => [...t, assistant]);
    } finally {
      setThinking(false);
    }
  }
  function onSubmitChat(e: React.FormEvent) {
    e.preventDefault();
    const p = prompt.trim();
    if (!p) return;
    setPrompt("");
    runChatAsk(p);
  }

  /** Upload (ingest) */
  async function onFiles(files: FileList | null) {
    if (!files || files.length === 0) return;
    setUploadErr(null);
    setUploading(true);
    try {
      const fd = new FormData();
      Array.from(files).forEach((f) => fd.append("file", f));
      const res = await fetch(`${API}/ingest`, { method: "POST", body: fd });
      if (!res.ok) throw new Error(await res.text());
      // Optionnel: toast OK
    } catch (e: any) {
      setUploadErr(e?.message || "Upload échoué");
    } finally {
      setUploading(false);
    }
  }

  /** Dérivés : facettes */
  const sources = useMemo(() => {
    const set = new Set<string>();
    hits.forEach((h) => h.payload?.source && set.add(String(h.payload.source)));
    return ["all", ...Array.from(set)];
  }, [hits]);
  const types = useMemo(() => {
    const set = new Set<string>();
    hits.forEach((h) => h.payload?.type && set.add(String(h.payload.type)));
    return ["all", ...Array.from(set)];
  }, [hits]);

  const filtered = hits.filter((h) => {
    const okS = filterSource === "all" || String(h.payload?.source) === filterSource;
    const okT = filterType === "all" || String(h.payload?.type) === filterType;
    return okS && okT;
  });

  return (
    <main className="mx-auto w-full max-w-6xl px-4 py-8">
      {/* Header + actions */}
      <div className="mb-6 flex items-center justify-between gap-3">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Chat-LAYA</h1>
          <p className="text-gray-600 dark:text-gray-300">RAG & Chat sur vos documents.</p>
        </div>
        <div className="flex items-center gap-2">
          {/* Dark mode */}
          <button
            onClick={() => setDark((v) => !v)}
            className="rounded border px-3 py-2 text-sm hover:bg-gray-50 dark:hover:bg-gray-800"
            title="Basculer thème"
          >
            {dark ? "🌙" : "☀️"}
          </button>

          {/* Upload bouton */}
          <label className="cursor-pointer rounded bg-emerald-600 text-white px-3 py-2 text-sm hover:bg-emerald-700">
            {uploading ? "Ingestion…" : "Uploader des docs"}
            <input
              type="file"
              multiple
              className="hidden"
              onChange={(e) => onFiles(e.target.files)}
            />
          </label>
        </div>
      </div>

      {/* Onglets */}
      <div className="mb-4 inline-flex rounded border bg-white dark:bg-gray-900">
        <button
          onClick={() => setTab("search")}
          className={`px-4 py-2 text-sm rounded-l ${tab === "search" ? "bg-blue-600 text-white" : "hover:bg-gray-50 dark:hover:bg-gray-800"}`}
        >
          🔎 Recherche
        </button>
        <button
          onClick={() => setTab("chat")}
          className={`px-4 py-2 text-sm rounded-r border-l ${tab === "chat" ? "bg-blue-600 text-white" : "hover:bg-gray-50 dark:hover:bg-gray-800"}`}
        >
          💬 Chat
        </button>
      </div>

      {/* Zone d’upload drag-drop */}
      <DropZone onFiles={onFiles} disabled={uploading} />

      {uploadErr && (
        <div className="mt-2 rounded border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-700">
          {uploadErr}
        </div>
      )}

      {tab === "search" ? (
        <section className="mt-6">
          {/* Barre de recherche */}
          <form onSubmit={onSubmitSearch} className="mb-4" role="search">
            <div className="flex items-center gap-2">
              <div className="relative flex-1">
                <span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">🔎</span>
                <input
                  ref={inputRef}
                  value={q}
                  onChange={(e) => setQ(e.target.value)}
                  placeholder="Pose ta question… (Ctrl/Cmd+K)"
                  className="w-full rounded border px-9 py-2 text-[15px] focus:outline-none focus:ring-2 focus:ring-blue-500"
                  aria-label="Saisir la requête"
                />
                {q && (
                  <button
                    type="button"
                    onClick={() => setQ("")}
                    className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                    aria-label="Effacer"
                    title="Effacer (Esc)"
                  >
                    ✕
                  </button>
                )}
              </div>
              <button
                type="submit"
                className="rounded bg-blue-600 text-white px-4 py-2 hover:bg-blue-700 disabled:opacity-50"
                disabled={!q.trim() || loading}
              >
                {loading ? "Recherche…" : "Rechercher"}
              </button>
            </div>
          </form>

          {/* Filtres */}
          {ran && (
            <div className="mb-3 flex flex-wrap items-center gap-2 text-sm">
              <span className="text-gray-500">Filtres :</span>
              <select
                value={filterSource}
                onChange={(e) => setFilterSource(e.target.value)}
                className="rounded border px-2 py-1 bg-white dark:bg-gray-900"
                aria-label="Filtrer par source"
              >
                {sources.map((s) => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </select>
              <select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                className="rounded border px-2 py-1 bg-white dark:bg-gray-900"
                aria-label="Filtrer par type"
              >
                {types.map((t) => (
                  <option key={t} value={t}>{t}</option>
                ))}
              </select>

              <div className="ml-auto text-xs text-gray-500">
                {elapsed != null && <>⏱ {Math.round(elapsed)}ms · </>}
                📄 {filtered.length} / {hits.length}
              </div>
            </div>
          )}

          {/* Erreur */}
          {err && (
            <div className="mb-3 rounded border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-700">
              {err}
            </div>
          )}

          {/* Loading */}
          {loading && <SkeletonList count={4} />}

          {/* Vide */}
          {!loading && !err && hits.length === 0 && ran && (
            <div className="rounded border bg-white dark:bg-gray-900 px-4 py-10 text-center text-gray-600">
              <div className="text-4xl mb-2">🗂️</div>
              Aucun résultat. Essaie de préciser la question ou d’uploader des documents.
            </div>
          )}

          {/* Résultats */}
          {!loading && !err && filtered.length > 0 && (
            <ResultsList hits={filtered} query={q} />
          )}
        </section>
      ) : (
        <section className="mt-4">
          {/* Historique chat */}
          <div
            ref={scrollRef}
            className="mb-3 max-h-[55vh] overflow-auto rounded border bg-white dark:bg-gray-900 p-4"
          >
            {turns.length === 0 && !thinking && (
              <div className="text-center text-gray-600">Commence une conversation avec tes documents.</div>
            )}
            {turns.map((t, i) => (
              <Bubble key={i} role={t.role} text={t.text} sources={t.sources} />
            ))}
            {thinking && <Bubble role="assistant" text="… réflexion en cours" thinking />}
          </div>

          {/* Entrée chat */}
          <form onSubmit={onSubmitChat} className="flex items-start gap-2">
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Demande quelque chose… Shift+Enter = retour à la ligne"
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  onSubmitChat(e);
                }
              }}
              rows={3}
              className="flex-1 rounded border px-3 py-2 text-[15px] focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              type="submit"
              className="rounded bg-blue-600 text-white px-4 py-2 hover:bg-blue-700 disabled:opacity-50"
              disabled={!prompt.trim() || thinking}
            >
              Envoyer
            </button>
          </form>
        </section>
      )}
    </main>
  );
}

/** ======= Composants ======= */

function DropZone({ onFiles, disabled }: { onFiles: (f: FileList | null) => void; disabled?: boolean }) {
  const [over, setOver] = useState(false);
  return (
    <div
      onDragOver={(e) => { e.preventDefault(); setOver(true); }}
      onDragLeave={() => setOver(false)}
      onDrop={(e) => {
        e.preventDefault();
        setOver(false);
        if (!disabled) onFiles(e.dataTransfer.files);
      }}
      className={`rounded border px-4 py-4 text-sm ${over ? "bg-blue-50 border-blue-300" : "bg-white dark:bg-gray-900"}`}
      aria-label="Zone d'import de documents (glisser-déposer)"
    >
      <b>Importer des documents</b> — Glisse tes fichiers ici ou utilise le bouton “Uploader des docs”.
    </div>
  );
}

function SkeletonList({ count = 4 }: { count?: number }) {
  return (
    <div className="space-y-3" aria-live="polite">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="animate-pulse rounded border bg-white dark:bg-gray-900 px-4 py-4">
          <div className="h-4 w-40 bg-gray-200 dark:bg-gray-800 rounded" />
          <div className="mt-2 h-3 w-[90%] bg-gray-200 dark:bg-gray-800 rounded" />
          <div className="mt-1 h-3 w-[75%] bg-gray-200 dark:bg-gray-800 rounded" />
          <div className="mt-3 h-2 w-[30%] bg-gray-200 dark:bg-gray-800 rounded" />
        </div>
      ))}
    </div>
  );
}

function ResultsList({ hits, query }: { hits: Hit[]; query: string }) {
  const terms = useMemo(
    () => query.toLowerCase().split(/\s+/).filter(Boolean),
    [query]
  );

  return (
    <div className="space-y-3" aria-live="polite">
      {hits.map((h) => {
        const text = (h.payload?.text || "") as string;
        const title = (h.payload?.title || "").toString();
        const url = (h.payload?.url || h.payload?.source || "") as string;

        return (
          <article key={h.id} className="rounded border bg-white dark:bg-gray-900 px-4 py-4 shadow-sm">
            {/* Titre + actions */}
            <div className="flex items-start justify-between gap-3">
              <h3 className="text-base font-semibold leading-6">
                {title || (text ? text.slice(0, 80) + (text.length > 80 ? "…" : "") : "Résultat")}
              </h3>
              <div className="flex items-center gap-2">
                {url && (
                  <a
                    href={url}
                    target="_blank"
                    rel="noreferrer"
                    className="text-sm rounded border px-2 py-1 hover:bg-gray-50 dark:hover:bg-gray-800"
                    title="Ouvrir la source"
                  >
                    Ouvrir
                  </a>
                )}
                <button
                  className="text-sm rounded border px-2 py-1 hover:bg-gray-50 dark:hover:bg-gray-800"
                  onClick={() => navigator.clipboard.writeText(text || "")}
                  title="Copier le texte"
                >
                  Copier
                </button>
              </div>
            </div>

            {/* Extrait */}
            <p className="mt-1 text-[15px] leading-6 text-gray-800 dark:text-gray-100">
              {highlight(text, terms)}
            </p>

            {/* Métadonnées */}
            <div className="mt-3 flex items-center gap-2 text-xs text-gray-500">
              {h.payload?.source && (
                <span className="inline-flex items-center rounded bg-gray-100 dark:bg-gray-800 px-2 py-0.5">
                  source: {String(h.payload.source)}
                </span>
              )}
              {h.payload?.type && (
                <span className="inline-flex items-center rounded bg-gray-100 dark:bg-gray-800 px-2 py-0.5">
                  type: {String(h.payload.type)}
                </span>
              )}
              <span className="inline-flex items-center gap-2">
                score <ScoreBar score={h.score} /> {h.score.toFixed(3)}
              </span>
            </div>
          </article>
        );
      })}
    </div>
  );
}

function highlight(text: string, terms: string[]) {
  if (!text || terms.length === 0) return text;
  const regex = new RegExp(`(${terms.map(escapeRe).join("|")})`, "gi");
  const parts = text.split(regex);
  return parts.map((part, i) =>
    terms.some((t) => t && part.toLowerCase() === t.toLowerCase()) ? (
      <mark key={i} className="bg-yellow-200 rounded px-0.5">{part}</mark>
    ) : (
      <span key={i}>{part}</span>
    )
  );
}

function ScoreBar({ score }: { score: number }) {
  const pct = Math.max(0, Math.min(1, score)) * 100;
  return (
    <span className="inline-block h-2 w-24 rounded bg-gray-200 dark:bg-gray-800 align-middle overflow-hidden">
      <span
        className="block h-full bg-blue-600"
        style={{ width: `${pct}%` }}
        aria-hidden="true"
      />
    </span>
  );
}

function Bubble({
  role,
  text,
  thinking,
  sources,
}: {
  role: "user" | "assistant";
  text: string;
  thinking?: boolean;
  sources?: Hit[];
}) {
  return (
    <div className={`mb-3 flex ${role === "user" ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[80%] rounded px-3 py-2 text-[15px] leading-6 ${
          role === "user"
            ? "bg-blue-600 text-white"
            : "bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100"
        }`}
      >
        {thinking ? (
          <span className="inline-flex items-center gap-2">
            <span className="relative inline-flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-gray-400 opacity-75" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-gray-500" />
            </span>
            {text}
          </span>
        ) : (
          text
        )}
        {sources && sources.length > 0 && (
          <div className={`mt-2 text-xs ${role === "user" ? "opacity-90" : "text-gray-600 dark:text-gray-300"}`}>
            Sources :
            <ul className="mt-1 list-disc pl-5">
              {sources.slice(0, 5).map((s) => (
                <li key={s.id}>
                  {s.payload?.title || s.payload?.source || "source"}{" "}
                  {s.payload?.url && (
                    <a className="underline" href={String(s.payload.url)} target="_blank" rel="noreferrer">
                      ouvrir
                    </a>
                  )}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
