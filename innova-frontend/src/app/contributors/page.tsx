// src/app/contributors/page.tsx
import { apiContributors } from "@/lib/api";
import Card from "@/components/Card";

export const dynamic = "force-dynamic";

export default async function ContributorsPage() {
  const contributors = await apiContributors.list();
  return (
    <main className="max-w-4xl mx-auto px-4 py-10">
      <h1 className="text-3xl font-bold mb-6">Contributeurs</h1>
      <div className="grid gap-4">
        {contributors.map(c => (
          <Card
            key={c.id}
            title={c.name || c.email || "Anonyme"}
            subtitle={c.role || c.github || c.email || ""}
          />
        ))}
        {contributors.length === 0 && (
          <div className="text-gray-600">Aucun contributeur pour l’instant.</div>
        )}
      </div>
    </main>
  );
}
