// src/app/domains/page.tsx
import { apiDomains } from "@/lib/api";
import Card from "@/components/Card";

export const dynamic = "force-dynamic";

export default async function DomainsPage() {
  const domains = await apiDomains.list();
  return (
    <main className="max-w-4xl mx-auto px-4 py-10">
      <h1 className="text-3xl font-bold mb-6">Domaines</h1>
      <div className="grid gap-4">
        {domains.map(d => (
          <Card
            key={d.id}
            title={d.name}
            subtitle={d.description || d.slug}
            right={<span>Voir</span>}
            href={`#`}
          />
        ))}
        {domains.length === 0 && (
          <div className="text-gray-600">Aucun domaine pour l’instant.</div>
        )}
      </div>
    </main>
  );
}
