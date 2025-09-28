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
const errorMessage = (error: unknown) => {
  if (error instanceof Error) return error.message;
  if (typeof error === "string") return error;
  try {
    return JSON.stringify(error);
  } catch {
    return "Erreur inconnue";
  }
};

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
    } catch (error) {
      setErr(errorMessage(error));
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
        body: JSON.stringify({ question: text, top_k: 8 }),
      });
      if (!res.ok) throw new Error(await res.text());
      const data = (await res.json()) as { answer: string; sources?: Hit[]; rag_error?: string };
      const assistant: ChatTurn = { role: "assistant", text: data.answer, sources: data.sources };
      if (data.rag_error) {
        assistant.text += `\n\n⚠️ Contexte indisponible: ${data.rag_error}`;
      }
      setTurns((t) => [...t, assistant]);
    } catch (error) {
      const assistant: ChatTurn = {
        role: "assistant",
        text: `❌ Erreur: ${errorMessage(error)}`,
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
      const res = await fetch(`${API}/chatlaya/ingest`, { method: "POST", body: fd });
      if (!res.ok) throw new Error(await res.text());
      // Optionnel: toast OK
    } catch (error) {
      setUploadErr(errorMessage(error) || "Upload échoué");
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
    <main className="mx-auto w-full max-w-6xl space-y-8 px-6 py-10">
      {/* Header + actions */}
      <div className="mb-8 flex flex-col gap-6 rounded-3xl bg-white/80 p-8 shadow-xl ring-1 ring-black/5 backdrop-blur md:flex-row md:items-center md:justify-between">
        <div className="space-y-2">
          <span className="inline-flex items-center rounded-full bg-blue-50 px-4 py-1 text-sm font-medium text-blue-600">
            INNOVA · Assistant documentaire
          </span>
          <div>
            <h1 className="text-4xl font-semibold tracking-tight text-gray-900">Chat-LAYA</h1>
            <p className="text-base text-gray-500">Un hub unique pour rechercher, discuter et enrichir vos ressources.</p>
          </div>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          {/* Dark mode */}
          <button
            onClick={() => setDark((v) => !v)}
            className="inline-flex items-center gap-2 rounded-full border border-transparent bg-gray-100 px-4 py-2 text-sm font-medium text-gray-700 transition hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-200 dark:hover:bg-gray-700"
            title="Basculer thème"
          >
            <span className="text-lg">{dark ? "🌙" : "☀️"}</span>
            <span className="hidden sm:inline">Thème</span>
          </button>

          {/* Upload bouton */}
          <label className="inline-flex cursor-pointer items-center gap-2 rounded-full bg-emerald-500 px-5 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-emerald-600 hover:shadow">
            <span>{uploading ? "Ingestion…" : "Ajouter des documents"}</span>
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
      <div className="mb-5 inline-flex rounded-full bg-gray-100 p-1 text-sm font-medium text-gray-500 shadow-inner dark:bg-gray-800 dark:text-gray-300">
        <button
          onClick={() => setTab("search")}
          className={`rounded-full px-5 py-2 transition ${
            tab === "search"
              ? "bg-white text-gray-900 shadow-sm ring-1 ring-black/5"
              : "hover:text-gray-700 dark:hover:text-gray-100"
          }`}
        >
          🔎 Recherche
        </button>
        <button
          onClick={() => setTab("chat")}
          className={`rounded-full px-5 py-2 transition ${
            tab === "chat"
              ? "bg-white text-gray-900 shadow-sm ring-1 ring-black/5"
              : "hover:text-gray-700 dark:hover:text-gray-100"
          }`}
        >
          💬 Chat
        </button>
      </div>

      {/* Zone d’upload drag-drop */}
      <DropZone onFiles={onFiles} disabled={uploading} />

      {uploadErr && (
        <div className="mt-2 rounded-2xl bg-red-50 px-4 py-2 text-sm font-medium text-red-700 shadow-sm">
          {uploadErr}
        </div>
      )}

      {tab === "search" ? (
        <section className="mt-6">
          {/* Barre de recherche */}
          <form onSubmit={onSubmitSearch} className="mb-6" role="search">
            <div className="flex flex-col gap-3 md:flex-row md:items-center">
              <div className="relative flex-1 rounded-full bg-gray-100/80 px-6 py-3 shadow-sm transition focus-within:bg-white focus-within:ring-2 focus-within:ring-blue-500 dark:bg-gray-900/60">
                <span className="pointer-events-none absolute left-6 top-1/2 -translate-y-1/2 text-lg text-gray-400">🔎</span>
                <input
                  ref={inputRef}
                  value={q}
                  onChange={(e) => setQ(e.target.value)}
                  placeholder="Pose ta question… (Ctrl/Cmd+K)"
                  className="w-full border-none bg-transparent pl-10 text-[15px] text-gray-900 outline-none placeholder:text-gray-400 dark:text-gray-100"
                  aria-label="Saisir la requête"
                />
                {q && (
                  <button
                    type="button"
                    onClick={() => setQ("")}
                    className="absolute right-6 top-1/2 -translate-y-1/2 text-gray-400 transition hover:text-gray-600"
                    aria-label="Effacer"
                    title="Effacer (Esc)"
                  >
                    ✕
                  </button>
                )}
              </div>
              <button
                type="submit"
                className="inline-flex items-center justify-center rounded-full bg-blue-600 px-6 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
                disabled={!q.trim() || loading}
              >
                {loading ? "Recherche…" : "Rechercher"}
              </button>
            </div>
          </form>

          {/* Filtres */}
          {ran && (
            <div className="mb-6 flex flex-wrap items-center gap-3 text-sm text-gray-600">
              <span className="font-medium text-gray-500">Filtres :</span>
              <select
                value={filterSource}
                onChange={(e) => setFilterSource(e.target.value)}
                className="rounded-full border-none bg-gray-100 px-4 py-1.5 text-sm text-gray-700 shadow-sm transition focus:outline-none focus:ring-2 focus:ring-blue-400 dark:bg-gray-800 dark:text-gray-200"
                aria-label="Filtrer par source"
              >
                {sources.map((s) => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </select>
              <select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                className="rounded-full border-none bg-gray-100 px-4 py-1.5 text-sm text-gray-700 shadow-sm transition focus:outline-none focus:ring-2 focus:ring-blue-400 dark:bg-gray-800 dark:text-gray-200"
                aria-label="Filtrer par type"
              >
                {types.map((t) => (
                  <option key={t} value={t}>{t}</option>
                ))}
              </select>

              <div className="ml-auto text-xs text-gray-400">
                {elapsed != null && <>⏱ {Math.round(elapsed)}ms · </>}
                📄 {filtered.length} / {hits.length}
              </div>
            </div>
          )}

          {/* Erreur */}
          {err && (
            <div className="mb-3 rounded-2xl bg-red-50 px-4 py-3 text-sm font-medium text-red-700 shadow-sm">
              {err}
            </div>
          )}

          {/* Loading */}
          {loading && <SkeletonList count={4} />}

          {/* Vide */}
          {!loading && !err && hits.length === 0 && ran && (
            <div className="rounded-3xl bg-gray-50 px-4 py-12 text-center text-gray-500 shadow-inner dark:bg-gray-900/40">
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
            className="mb-4 max-h-[55vh] overflow-auto rounded-3xl bg-gray-50 p-6 shadow-inner dark:bg-gray-900/60"
          >
            {turns.length === 0 && !thinking && (
              <div className="text-center text-gray-500">
                Commence une conversation avec tes documents.
              </div>
            )}
            {turns.map((t, i) => (
              <Bubble key={i} role={t.role} text={t.text} sources={t.sources} />
            ))}
            {thinking && <Bubble role="assistant" text="… réflexion en cours" thinking />}
          </div>

          {/* Entrée chat */}
          <form onSubmit={onSubmitChat} className="flex flex-col gap-3 rounded-3xl bg-white/70 p-4 shadow-xl ring-1 ring-black/5 backdrop-blur md:flex-row md:items-end">
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
              className="flex-1 resize-none rounded-2xl border border-transparent bg-gray-50 px-4 py-3 text-[15px] text-gray-900 shadow-inner transition focus:border-blue-200 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-400 dark:bg-gray-900/60 dark:text-gray-100"
            />
            <button
              type="submit"
              className="inline-flex h-12 items-center justify-center rounded-full bg-blue-600 px-6 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
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
      className={`group flex items-center justify-center rounded-3xl border border-dashed px-6 py-6 text-sm transition ${
        over
          ? "border-blue-300 bg-blue-50 text-blue-600"
          : "border-gray-200 bg-gray-50 text-gray-500 hover:border-blue-200 hover:bg-blue-50 hover:text-blue-600 dark:border-gray-700/60 dark:bg-gray-900/40 dark:text-gray-300"
      }`}
      aria-label="Zone d'import de documents (glisser-déposer)"
    >
      <span className="inline-flex items-center gap-3 text-sm font-medium">
        <span className="grid h-10 w-10 place-items-center rounded-full bg-white text-lg shadow-sm ring-1 ring-black/5 dark:bg-gray-900/70">
          📁
        </span>
        Déposez vos fichiers ici
      </span>
    </div>
  );
}

function SkeletonList({ count = 4 }: { count?: number }) {
  return (
    <div className="space-y-3" aria-live="polite">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="animate-pulse rounded-3xl bg-gray-100/80 px-5 py-5 shadow-inner dark:bg-gray-900/40">
          <div className="h-4 w-40 rounded bg-gray-300/70 dark:bg-gray-700" />
          <div className="mt-2 h-3 w-[90%] rounded bg-gray-300/70 dark:bg-gray-700" />
          <div className="mt-1 h-3 w-[75%] rounded bg-gray-300/70 dark:bg-gray-700" />
          <div className="mt-3 h-2 w-[30%] rounded bg-gray-300/70 dark:bg-gray-700" />
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
    <div className="space-y-4" aria-live="polite">
      {hits.map((h) => {
        const text = (h.payload?.text || "") as string;
        const title = (h.payload?.title || "").toString();
        const url = (h.payload?.url || h.payload?.source || "") as string;

        return (
          <article
            key={h.id}
            className="rounded-3xl bg-white px-6 py-6 shadow-lg ring-1 ring-gray-100 transition hover:-translate-y-1 hover:shadow-xl dark:bg-gray-900"
          >
            {/* Titre + actions */}
            <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
              <h3 className="text-lg font-semibold leading-6 text-gray-900 dark:text-gray-100">
                {title || (text ? text.slice(0, 80) + (text.length > 80 ? "…" : "") : "Résultat")}
              </h3>
              <div className="flex items-center gap-2">
                {url && (
                  <a
                    href={url}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1 rounded-full border border-transparent bg-gray-100 px-3 py-1 text-xs font-medium text-gray-600 transition hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-200 dark:hover:bg-gray-700"
                    title="Ouvrir la source"
                  >
                    Ouvrir
                  </a>
                )}
                <button
                  className="inline-flex items-center gap-1 rounded-full border border-transparent bg-gray-100 px-3 py-1 text-xs font-medium text-gray-600 transition hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-200 dark:hover:bg-gray-700"
                  onClick={() => navigator.clipboard.writeText(text || "")}
                  title="Copier le texte"
                >
                  Copier
                </button>
              </div>
            </div>

            {/* Extrait */}
            <p className="mt-3 text-[15px] leading-7 text-gray-700 dark:text-gray-200">
              {highlight(text, terms)}
            </p>

            {/* Métadonnées */}
            <div className="mt-4 flex flex-wrap items-center gap-2 text-xs text-gray-500">
              {h.payload?.source && (
                <span className="inline-flex items-center gap-1 rounded-full bg-blue-50 px-3 py-1 font-medium text-blue-600 dark:bg-blue-500/20 dark:text-blue-100">
                  source: {String(h.payload.source)}
                </span>
              )}
              {h.payload?.type && (
                <span className="inline-flex items-center gap-1 rounded-full bg-emerald-50 px-3 py-1 font-medium text-emerald-600 dark:bg-emerald-500/20 dark:text-emerald-100">
                  type: {String(h.payload.type)}
                </span>
              )}
              <span className="inline-flex items-center gap-2 rounded-full bg-gray-100 px-3 py-1 text-gray-600 dark:bg-gray-800 dark:text-gray-200">
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
    <span className="inline-block h-2 w-24 overflow-hidden rounded-full bg-gray-200 align-middle dark:bg-gray-700">
      <span
        className="block h-full bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-500"
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
        className={`max-w-[80%] rounded-2xl px-4 py-3 text-[15px] leading-6 shadow ${
          role === "user"
            ? "bg-gradient-to-r from-blue-600 to-indigo-600 text-white"
            : "bg-white/80 text-gray-900 backdrop-blur dark:bg-gray-800/80 dark:text-gray-100"
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
