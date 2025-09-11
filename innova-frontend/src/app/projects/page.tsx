// src/app/projects/page.tsx
import Link from "next/link";

type Project = {
  id: string;
  name: string;
  slug: string;
  title?: string | null;
  description?: string | null;
  repo_url?: string | null;
  live_url?: string | null;
  logo_url?: string | null;
  status?: "draft" | "published" | "archived" | string | null;
  created_at?: string | null;
};

async function getProjects(): Promise<Project[]> {
  const base = process.env.NEXT_PUBLIC_API_URL;
  if (!base) throw new Error("NEXT_PUBLIC_API_URL manquant.");
  const res = await fetch(`${base}/projects`, {
    // évite cache build
    cache: "no-store",
    headers: { "Content-Type": "application/json" },
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Échec API /projects (${res.status}): ${text}`);
  }
  return (await res.json()) as Project[];
}

export default async function ProjectsPage() {
  const projects = await getProjects();

  return (
    <main className="mx-auto max-w-4xl p-6">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Projets</h1>
        <Link
          href="/projects/new"
          className="rounded-lg bg-black px-4 py-2 text-white hover:opacity-90"
        >
          Nouveau projet
        </Link>
      </div>

      {projects.length === 0 ? (
        <p className="text-sm text-gray-600">Aucun projet pour le moment.</p>
      ) : (
        <ul className="space-y-3">
          {projects.map((p) => (
            <li
              key={p.id}
              className="rounded-xl border p-4 hover:bg-gray-50 transition"
            >
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-lg font-medium">
                    {p.title ?? p.name}
                    <span className="ml-2 text-gray-500">({p.slug})</span>
                  </h2>
                  {p.description ? (
                    <p className="text-sm text-gray-600">{p.description}</p>
                  ) : null}
                </div>
                <div className="flex gap-3">
                  {p.live_url ? (
                    <a
                      className="text-sm underline"
                      href={p.live_url}
                      target="_blank"
                      rel="noreferrer"
                    >
                      Live
                    </a>
                  ) : null}
                  {p.repo_url ? (
                    <a
                      className="text-sm underline"
                      href={p.repo_url}
                      target="_blank"
                      rel="noreferrer"
                    >
                      Repo
                    </a>
                  ) : null}
                </div>
              </div>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}
