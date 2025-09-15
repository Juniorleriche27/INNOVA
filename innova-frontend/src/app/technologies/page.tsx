// src/app/technologies/page.tsx
import { apiTechnologies } from "@/lib/api";
import Card from "@/components/Card";

export const dynamic = "force-dynamic";

export default async function TechnologiesPage() {
  const techs = await apiTechnologies.list();
  return (
    <main className="max-w-4xl mx-auto px-4 py-10">
      <h1 className="text-3xl font-bold mb-6">Technologies</h1>
      <div className="grid gap-4">
        {techs.map(t => (
          <Card
            key={t.id}
            title={t.name || "—"}
            subtitle={t.version ? `Version ${t.version}` : undefined}
          />
        ))}
        {techs.length === 0 && (
          <div className="text-gray-600">Aucune technologie pour l’instant.</div>
        )}
      </div>
    </main>
  );
}
