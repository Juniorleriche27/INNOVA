// innova-frontend/lib/api.ts

// ⚠️ Base URL du BACKEND (Render). À définir dans Vercel : NEXT_PUBLIC_CHATLAYA_URL
// Exemple: https://innova-1-v3ab.onrender.com
const API =
  (process.env.NEXT_PUBLIC_CHATLAYA_URL || "").replace(/\/+$/, "") ||
  "https://innova-1-v3ab.onrender.com";

async function json<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(text || `HTTP ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export type Domain = {
  id: string;
  name: string;
  slug: string;
  description?: string | null;
  image_url?: string | null;
};

export type Contributor = {
  id: string;
  project_id: string;
  user_id?: string | null;
  name?: string | null;
  role?: string | null;
  email?: string | null;
  github?: string | null;
};

export type Technology = {
  id: string;
  project_id: string;
  name?: string | null;
  version?: string | null;
};

export const apiDomains = {
  async list(): Promise<Domain[]> {
    const res = await fetch(`${API}/domains`, { cache: "no-store" });
    return json<Domain[]>(res);
  },
};

export const apiContributors = {
  async list(): Promise<Contributor[]> {
    const res = await fetch(`${API}/contributors`, { cache: "no-store" });
    return json<Contributor[]>(res);
  },
};

export const apiTechnologies = {
  async list(): Promise<Technology[]> {
    const res = await fetch(`${API}/technologies`, { cache: "no-store" });
    return json<Technology[]>(res);
  },
};
