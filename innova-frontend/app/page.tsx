// innova-frontend/app/page.tsx
import Link from "next/link";
import type { Route } from "next";

export default function HomePage() {
  return (
    <main className="px-6 py-8">
      {/* HERO */}
      <section className="max-w-5xl">
        <p className="text-sm text-gray-500">Bienvenue 👋</p>
        <h1 className="mt-1 text-2xl font-semibold tracking-tight">
          Votre espace de pilotage projets & IA
        </h1>
        <p className="mt-2 max-w-2xl text-gray-600">
          Centralisez vos projets, explorez vos documents avec Chat-LAYA (RAG) et suivez vos indicateurs.
        </p>

        <div className="mt-5 flex flex-wrap gap-3">
          <Link
            href="/chat-laya"
            className="inline-flex items-center rounded bg-green-600 px-4 py-2 text-white text-sm font-medium hover:bg-green-700"
          >
            Essayer Chat-LAYA
          </Link>
          <Link
            href="/projects"
            className="inline-flex items-center rounded border px-4 py-2 text-sm font-medium hover:bg-gray-50"
          >
            Voir les projets
          </Link>
        </div>
      </section>

      {/* ACCÈS RAPIDE */}
      <section className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <Card
          title="Projets"
          desc="Créez, organisez et suivez l’avancement de vos projets."
          href="/projects"
          cta="Ouvrir projets"
        />
        <Card
          title="Chat-LAYA"
          desc="Posez des questions et obtenez des réponses sourcées depuis vos documents."
          href="/chat-laya"
          cta="Lancer Chat-LAYA"
          tone="primary"
        />
        <Card
          title="Analytics"
          desc="Suivez les usages, la satisfaction et la qualité des réponses."
          href="/analytics"
          cta="Voir le tableau de bord"
          muted
        />
      </section>

      {/* ASTUCES */}
      <section className="mt-8">
        <div className="rounded border bg-white px-4 py-3 text-sm text-gray-700">
          <ul className="list-disc pl-5 space-y-1">
            <li>
              Astuce : utilisez <kbd className="rounded border px-1">Ctrl</kbd>/<kbd className="rounded border px-1">Cmd</kbd>+
              <kbd className="rounded border px-1">K</kbd> pour focaliser la recherche dans Chat-LAYA.
            </li>
            <li>
              Vous pouvez ingérer des fichiers directement dans la page{" "}
              <Link className="underline" href="/chat-laya">Chat-LAYA</Link> (glisser-déposer).
            </li>
          </ul>
        </div>
      </section>
    </main>
  );
}

function Card({
  title,
  desc,
  href,
  cta,
  tone,
  muted,
}: {
  title: string;
  desc: string;
  href: Route;   // ← typedRoutes friendly
  cta: string;
  tone?: "primary";
  muted?: boolean;
}) {
  return (
    <div
      className={[
        "rounded border bg-white p-4 shadow-sm transition hover:shadow",
        muted ? "opacity-90" : "",
      ].join(" ")}
    >
      <h3 className="text-base font-semibold">{title}</h3>
      <p className="mt-1 text-sm text-gray-600">{desc}</p>
      <div className="mt-3">
        <Link
          href={href}
          className={[
            "inline-flex items-center rounded px-3 py-2 text-sm font-medium",
            tone === "primary"
              ? "bg-blue-600 text-white hover:bg-blue-700"
              : "border hover:bg-gray-50",
          ].join(" ")}
        >
          {cta}
        </Link>
      </div>
    </div>
  );
}
