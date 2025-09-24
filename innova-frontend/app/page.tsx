// innova-frontend/app/page.tsx
export default function HomePage() {
  return (
    <main className="p-6">
      <h1 className="text-2xl font-bold">INNOVA+</h1>
      <p className="mt-2 text-gray-600">Bienvenue sur la plateforme.</p>

      {/* ✅ Fonctionnalité ajoutée : liens rapides */}
      <div className="mt-6 space-x-4">
        <a
          href="/projects"
          className="inline-block rounded bg-blue-600 text-white px-4 py-2 hover:bg-blue-700"
        >
          Voir les projets
        </a>
        <a
          href="/chat-laya"
          className="inline-block rounded bg-green-600 text-white px-4 py-2 hover:bg-green-700"
        >
          Essayer Chat-LAYA
        </a>
      </div>
    </main>
  );
}
