// src/app/projects/new/page.tsx
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

type CreateProjectPayload = {
  name: string;
  slug: string;
  title?: string | null;
  description?: string | null;
  repo_url?: string | null;
  live_url?: string | null;
  logo_url?: string | null;
  status?: string | null;
};

export default function NewProjectPage() {
  const router = useRouter();
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const form = new FormData(e.currentTarget);
      const payload: CreateProjectPayload = {
        name: String(form.get("name") ?? "").trim(),
        slug: String(form.get("slug") ?? "").trim(),
        title: (String(form.get("title") ?? "").trim() || null) as string | null,
        description: (String(form.get("description") ?? "").trim() ||
          null) as string | null,
        repo_url: (String(form.get("repo_url") ?? "").trim() ||
          null) as string | null,
        live_url: (String(form.get("live_url") ?? "").trim() ||
          null) as string | null,
        logo_url: (String(form.get("logo_url") ?? "").trim() ||
          null) as string | null,
        status: (String(form.get("status") ?? "").trim() ||
          null) as string | null,
      };

      if (!payload.name || !payload.slug) {
        setError("Veuillez fournir au minimum 'name' et 'slug'.");
        setLoading(false);
        return;
      }

      const base = process.env.NEXT_PUBLIC_API_URL;
      if (!base) throw new Error("NEXT_PUBLIC_API_URL manquant.");

      const res = await fetch(`${base}/projects/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(`Échec API (${res.status}): ${text}`);
      }

      await res.json();

      // Redirection après création : vers la liste ou un détail si dispo
      router.push("/projects");
      // Optionnel : refresh de la route
      router.refresh();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto max-w-2xl p-6">
      <h1 className="mb-4 text-2xl font-semibold">Nouveau projet</h1>

      {error ? (
        <div className="mb-4 rounded-lg border border-red-300 bg-red-50 p-3 text-sm text-red-700">
          {error}
        </div>
      ) : null}

      <form onSubmit={onSubmit} className="space-y-4">
        <div>
          <label htmlFor="name" className="block text-sm font-medium">
            Nom *
          </label>
          <input
            id="name"
            name="name"
            type="text"
            required
            className="mt-1 w-full rounded-lg border p-2"
            placeholder="ex: Innova Frontend"
          />
        </div>

        <div>
          <label htmlFor="slug" className="block text-sm font-medium">
            Slug *
          </label>
          <input
            id="slug"
            name="slug"
            type="text"
            required
            className="mt-1 w-full rounded-lg border p-2"
            placeholder="ex: innova-frontend"
          />
        </div>

        <div>
          <label htmlFor="title" className="block text-sm font-medium">
            Titre (optionnel)
          </label>
          <input
            id="title"
            name="title"
            type="text"
            className="mt-1 w-full rounded-lg border p-2"
          />
        </div>

        <div>
          <label htmlFor="description" className="block text-sm font-medium">
            Description (optionnel)
          </label>
          <textarea
            id="description"
            name="description"
            className="mt-1 w-full rounded-lg border p-2"
            rows={4}
          />
        </div>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <div>
            <label htmlFor="repo_url" className="block text-sm font-medium">
              Repo URL
            </label>
            <input
              id="repo_url"
              name="repo_url"
              type="url"
              className="mt-1 w-full rounded-lg border p-2"
              placeholder="https://github.com/..."
            />
          </div>
          <div>
            <label htmlFor="live_url" className="block text-sm font-medium">
              Live URL
            </label>
            <input
              id="live_url"
              name="live_url"
              type="url"
              className="mt-1 w-full rounded-lg border p-2"
              placeholder="https://..."
            />
          </div>
          <div>
            <label htmlFor="logo_url" className="block text-sm font-medium">
              Logo URL
            </label>
            <input
              id="logo_url"
              name="logo_url"
              type="url"
              className="mt-1 w-full rounded-lg border p-2"
              placeholder="https://..."
            />
          </div>
          <div>
            <label htmlFor="status" className="block text-sm font-medium">
              Statut
            </label>
            <input
              id="status"
              name="status"
              type="text"
              className="mt-1 w-full rounded-lg border p-2"
              placeholder="draft | published | archived"
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="rounded-lg bg-black px-4 py-2 text-white hover:opacity-90 disabled:opacity-60"
        >
          {loading ? "Création..." : "Créer le projet"}
        </button>
      </form>
    </main>
  );
}
