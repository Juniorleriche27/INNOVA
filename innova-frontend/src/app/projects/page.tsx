"use client";
import { useEffect, useState } from "react";

interface Project {
  id: string;
  name: string;
  slug: string;
  description?: string;
  status?: string;
  repo_url?: string;
  live_url?: string;
}

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchProjects() {
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/projects/`);
        if (!res.ok) throw new Error("Erreur API " + res.status);
        const data = await res.json();
        setProjects(data);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    fetchProjects();
  }, []);

  if (loading) return <p>Chargement...</p>;
  if (error) return <p className="text-red-600">Erreur: {error}</p>;

  return (
    <section className="space-y-4">
      <h1 className="text-xl font-semibold">Liste des projets</h1>
      {projects.length === 0 ? (
        <p>Aucun projet trouvé.</p>
      ) : (
        <ul className="grid gap-4 md:grid-cols-2">
          {projects.map((p) => (
            <li
              key={p.id}
              className="border rounded-lg p-4 shadow hover:shadow-md transition"
            >
              <h2 className="text-lg font-bold">{p.name}</h2>
              <p className="text-gray-600 text-sm">{p.description}</p>
              <div className="mt-2 flex gap-4 text-sm">
                {p.repo_url && (
                  <a
                    href={p.repo_url}
                    target="_blank"
                    className="text-blue-600 hover:underline"
                  >
                    Code source
                  </a>
                )}
                {p.live_url && (
                  <a
                    href={p.live_url}
                    target="_blank"
                    className="text-green-600 hover:underline"
                  >
                    Démo en ligne
                  </a>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
