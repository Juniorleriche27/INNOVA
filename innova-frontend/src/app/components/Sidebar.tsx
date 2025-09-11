"use client";
import Link from "next/link";

export default function Sidebar() {
  return (
    <aside className="h-full w-64 bg-gray-900 text-white flex flex-col">
      <div className="px-6 py-4 text-xl font-bold tracking-wide">INNOVA+</div>

      <nav className="flex-1 px-3 space-y-1 text-sm">
        <Link
          href="/projects"
          className="block px-3 py-2 rounded hover:bg-gray-800 no-underline"
        >
          Projets
        </Link>
        <Link
          href="/projects/new"
          className="block px-6 py-2 rounded hover:bg-gray-800 no-underline text-gray-300"
        >
          + Nouveau
        </Link>
        <Link
          href="/domains"
          className="block px-3 py-2 rounded hover:bg-gray-800 no-underline"
        >
          Domaines
        </Link>
        <Link
          href="/contributors"
          className="block px-3 py-2 rounded hover:bg-gray-800 no-underline"
        >
          Contributeurs
        </Link>
        <Link
          href="/technologies"
          className="block px-3 py-2 rounded hover:bg-gray-800 no-underline"
        >
          Technologies
        </Link>
      </nav>

      <div className="px-6 py-4 text-[11px] text-gray-400 border-t border-white/10">
        v1.0.0
      </div>
    </aside>
  );
}
