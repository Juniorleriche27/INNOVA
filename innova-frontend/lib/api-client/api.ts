// src/lib/api.ts
export const API_BASE = (process.env.NEXT_PUBLIC_API_URL || "").replace(/\/+$/, "");

async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    // listes = pas de cache, détail = force revalidate si tu veux
    cache: "no-store",
    headers: { "Content-Type": "application/json", ...(init?.headers || {}) },
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`API ${res.status}: ${text || res.statusText}`);
  }
  return res.json() as Promise<T>;
}

/** Types partagés */
export type UUID = string;

export type Project = {
  id: UUID; name: string; slug: string;
  title?: string | null;
  description?: string | null;
  domain_id?: UUID | null;
  repo_url?: string | null;
  live_url?: string | null;
  logo_url?: string | null;
  status?: "draft" | "published" | "archived" | null;
  live?: string | null;
  repo?: string | null;
};

export type Domain = {
  id: UUID;
  name: string;
  slug: string;
  description?: string | null;
  image_url?: string | null;
};

export type Contributor = {
  id: UUID;
  project_id: UUID;
  user_id: UUID;
  name?: string | null;
  role?: string | null;
  email?: string | null;
  github?: string | null;
};

export type Technology = {
  id: UUID;
  project_id: UUID;
  name?: string | null;
  version?: string | null;
};

/** Endpoints */
export const apiProjects = {
  list: () => api<Project[]>("/projects"),
};

export const apiDomains = {
  list: () => api<Domain[]>("/domains"),
};

export const apiContributors = {
  list: () => api<Contributor[]>("/contributors"),
};

export const apiTechnologies = {
  list: () => api<Technology[]>("/technologies"),
};
