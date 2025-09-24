import Card from "@/components/Card";
import { apiTechnologies, type Technology } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function TechnologiesPage() {
  let techs: Technology[] = [];
  let error: string | null = null;

  try {
    techs = await apiTechnologies.list();
  } catch (e) {
    error = e instanceof Error ? e.message : "Erreur inconnue";
  }

  return (
    <main className="max-w-4xl mx-auto px-4 py-10">
      <h1 className="text-3xl font-bold mb-6">Technologies</h1>

      {error && (
        <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          Impossible de charger les technologies. {error}
        </div>
      )}

      <div className="grid gap-4">
        {techs.map(t => (
          <Card
            key={t.id}
            title={t.name || "—"}
            subtitle={t.version ? `Version ${t.version}` : undefined}
          />
        ))}

        {!error && techs.length === 0 && (
          <div className="text-gray-600">Aucune technologie pour l’instant.</div>
        )}
      </div>
    </main>
  );
}
