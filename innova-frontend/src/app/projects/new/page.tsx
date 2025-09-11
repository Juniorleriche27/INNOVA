"use client";
import { useRouter } from "next/navigation";
import { useState } from "react";

const API =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/+$/, "") ||
  "http://127.0.0.1:8000";

export default function NewProjectPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError]   = useState<string | null>(null);

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError(null);
    setLoading(true);

    const form = new FormData(e.currentTarget);
    const payload = {
      name: String(form.get("name") || "").trim(),
      slug: String(form.get("slug") || "").trim(),
      title: String(form.get("title") || "").trim() || null,
      description: String(form.get("description") || "").trim() || null,
      repo_url: String(form.get("repo_url") || "").trim() || null,
      live_url: String(form.get("live_url") || "").trim() || null,
      logo_url: String(form.get("logo_url") || "").trim() || null,
      status: String(form.get("status") || "").trim() || null,
    };

    if (!payload.name || !payload.slug) {
      setError("Les champs *name* et *slug* sont obligatoires.");
      setLoading(false);
      return;
    }

    try {
      const token = localStorage.getItem("token");
      const res = await fetch(`${API}/projects/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const txt = await res.text();
        throw new Error(`Erreur API ${res.status} - ${txt}`);
      }

      router.push("/projects");
      router.refresh();
    } catch (err: any) {
      setError(err.message ?? "Erreur inconnue");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="space-y-6 max-w-2xl">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">Nouveau projet</h1>
        <a
          href="/projects"
          className="rounded-lg border px-3 py-2 text-sm"
        >
          Retour à la liste
        </a>
      </div>

      {error && <p className="text-red-600">{error}</p>}

      <form onSubmit={onSubmit} className="space-y-4">
        <div className="grid gap-4 md:grid-cols-2">
          <div>
            <label htmlFor="name" className="block text-sm font-medium">Name *</label>
            <input id="name" name="name" className="mt-1 w-full border rounded-lg px-3 py-2" required />
          </div>
          <div>
            <label htmlFor="slug" className="block text-sm font-medium">Slug *</label>
            <input id="slug" name="slug" className="mt-1 w-full border rounded-lg px-3 py-2" required />
          </div>
          <div>
            <label htmlFor="title" className="block text-sm font-medium">Title</label>
            <input id="title" name="title" className="mt-1 w-full border rounded-lg px-3 py-2" />
          </div>
          <div>
            <label htmlFor="status" className="block text-sm font-medium">Status</label>
            <select id="status" name="status" className="mt-1 w-full border rounded-lg px-3 py-2">
              <option value="">(aucun)</option>
              <option value="draft">draft</option>
              <option value="published">published</option>
              <option value="archived">archived</option>
            </select>
          </div>
        </div>

        <div>
          <label htmlFor="description" className="block text-sm font-medium">Description</label>
          <textarea id="description" name="description" rows={4} className="mt-1 w-full border rounded-lg px-3 py-2" />
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <div>
            <label htmlFor="repo_url" className="block text-sm font-medium">Repo URL</label>
            <input id="repo_url" name="repo_url" className="mt-1 w-full border rounded-lg px-3 py-2" />
          </div>
          <div>
            <label htmlFor="live_url" className="block text-sm font-medium">Live URL</label>
            <input id="live_url" name="live_url" className="mt-1 w-full border rounded-lg px-3 py-2" />
          </div>
          <div className="md:col-span-2">
            <label htmlFor="logo_url" className="block text-sm font-medium">Logo URL</label>
            <input id="logo_url" name="logo_url" className="mt-1 w-full border rounded-lg px-3 py-2" />
          </div>
        </div>

        <div className="flex gap-3">
          <button
            type="submit"
            disabled={loading}
            className="rounded-lg bg-blue-600 text-white px-4 py-2 disabled:opacity-60"
          >
            {loading ? "Envoi..." : "Créer"}
          </button>
          <button
            type="button"
            onClick={() => router.back()}
            className="rounded-lg border px-4 py-2"
          >
            Annuler
          </button>
        </div>
      </form>
    </section>
  );
}
