import Card from "@/components/Card";
import { apiContributors, type Contributor } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function ContributorsPage() {
  let contributors: Contributor[] = [];
  let error: string | null = null;

  try {
    contributors = await apiContributors.list();
  } catch (e) {
    error = e instanceof Error ? e.message : "Erreur inconnue";
  }

  return (
    <main className="max-w-4xl mx-auto px-4 py-10">
      <h1 className="text-3xl font-bold mb-6">Contributeurs</h1>

      {error && (
        <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          Impossible de charger les contributeurs. {error}
        </div>
      )}

      <div className="grid gap-4">
        {contributors.map(c => (
          <Card
            key={c.id}
            title={c.name || c.email || "Anonyme"}
            subtitle={c.role || c.github || c.email || ""}
          />
        ))}

        {!error && contributors.length === 0 && (
          <div className="text-gray-600">Aucun contributeur pour l’instant.</div>
        )}
      </div>
    </main>
  );
}
