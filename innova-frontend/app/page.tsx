// innova-frontend/app/page.tsx
import Link from "next/link";

function BlackButton({
  href,
  children,
  className = "",
}: { href: string; children: React.ReactNode; className?: string }) {
  return (
    <Link
      href={href}
      className={[
        "inline-flex items-center justify-center rounded-full",
        "bg-black text-white px-5 py-2.5",
        "transition-transform will-change-transform hover:scale-[1.05]",
        "shadow-sm hover:shadow",
        "no-underline select-none",
        className,
      ].join(" ")}
    >
      {children}
    </Link>
  );
}

function Card({
  title,
  desc,
  emoji,
}: { title: string; desc: string; emoji: string }) {
  return (
    <div className="rounded-2xl bg-white shadow-sm border p-5 transition hover:shadow-md">
      <div className="text-2xl">{emoji}</div>
      <h3 className="mt-2 font-semibold">{title}</h3>
      <p className="mt-1 text-sm text-gray-600">{desc}</p>
    </div>
  );
}

export default function HomePage() {
  return (
    <main className="px-6 py-8">
      {/* Bloc d’accueil : une seule ligne centrée */}
      <div className="mx-auto max-w-5xl">
        <div className="grid grid-cols-3 items-center gap-4">
          <div className="flex justify-start">
            <BlackButton href="/chat-laya">Essayer Chat-LAYA</BlackButton>
          </div>

          <div className="flex items-center justify-center">
            <div className="text-2xl sm:text-3xl font-bold">Bienvenue 👋</div>
          </div>

          <div className="flex justify-end">
            <BlackButton href="/projects">Voir les projets</BlackButton>
          </div>
        </div>

        {/* Titre principal */}
        <h2 className="mt-10 text-center text-xl sm:text-2xl font-semibold">
          Votre espace de travail
        </h2>

        {/* 3 cards alignées */}
        <div className="mt-6 grid grid-cols-1 sm:grid-cols-3 gap-4">
          <Card
            emoji="📂"
            title="Projets"
            desc="Créez, organisez et suivez vos projets."
          />
          <Card
            emoji="💬"
            title="Chat-LAYA"
            desc="Posez des questions et obtenez des réponses sourcées."
          />
          <Card
            emoji="📊"
            title="Analytics"
            desc="Mesurez l’usage, la qualité et la satisfaction."
          />
        </div>
      </div>
    </main>
  );
}
