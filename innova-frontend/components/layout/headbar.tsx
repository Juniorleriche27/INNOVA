"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useRef, useState } from "react";

function NavLink({ href, children }: { href: string; children: React.ReactNode }) {
  const pathname = usePathname();
  const active = pathname === href;
  return (
    <Link
      href={href}
      className={`no-underline px-2 py-1 rounded text-[13px] font-medium leading-none outline-none
      ${active ? "text-blue-700 bg-blue-50" : "text-gray-700 hover:text-blue-600"}
      focus-visible:ring-2 focus-visible:ring-blue-500`}
    >
      {children}
    </Link>
  );
}

export default function Headbar() {
  const [authOpen, setAuthOpen] = useState(false);
  const [moreOpen, setMoreOpen] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const authRef = useRef<HTMLDivElement>(null);
  const moreRef = useRef<HTMLDivElement>(null);

  // Fermer les menus si clic extérieur
  useEffect(() => {
    function onClick(e: MouseEvent) {
      if (!authRef.current?.contains(e.target as Node)) setAuthOpen(false);
      if (!moreRef.current?.contains(e.target as Node)) setMoreOpen(false);
    }
    window.addEventListener("click", onClick);
    return () => window.removeEventListener("click", onClick);
  }, []);

  // Ombre sticky quand on scrolle
  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 2);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <header
      className={`sticky top-0 z-40 bg-white/95 backdrop-blur border-b transition-shadow ${
        scrolled ? "shadow-[0_1px_8px_rgba(0,0,0,0.08)]" : "shadow-none"
      }`}
    >
      <div className="px-3 sm:px-4 lg:px-6 h-12 flex items-center justify-between gap-3">
        {/* gauche : burger (mobile) + nav compacte */}
        <div className="flex items-center gap-2 min-w-0">
          <button
            onClick={() => setMobileOpen(v => !v)}
            className="lg:hidden inline-flex items-center justify-center w-9 h-9 rounded border text-gray-600 hover:bg-gray-50 focus-visible:ring-2 focus-visible:ring-blue-500"
            aria-label="Menu"
            aria-expanded={mobileOpen}
          >
            ☰
          </button>

          <nav className="hidden lg:flex items-center gap-1.5 whitespace-nowrap">
            <NavLink href="/">Accueil</NavLink>
            <NavLink href="/about">À propos</NavLink>
            <NavLink href="/contact">Contact</NavLink>
            <NavLink href="/chat-laya">Chat-LAYA</NavLink>

            {/* Liens secondaires dans “Plus” */}
            <div className="relative" ref={moreRef}>
              <button
                onClick={(e) => { e.stopPropagation(); setMoreOpen(v => !v); }}
                className="px-2 py-1 rounded text-[13px] font-medium text-gray-700 hover:text-blue-600 focus-visible:ring-2 focus-visible:ring-blue-500"
                aria-haspopup="menu"
                aria-expanded={moreOpen}
              >
                Plus ▾
              </button>
              {moreOpen && (
                <div role="menu" className="absolute left-0 mt-2 w-52 rounded border bg-white shadow p-1">
                  <Link href="/community" className="block px-3 py-2 rounded hover:bg-gray-50 no-underline text-[13px]" role="menuitem">Communauté</Link>
                  <Link href="/marketplace" className="block px-3 py-2 rounded hover:bg-gray-50 no-underline text-[13px]" role="menuitem">Marketplace</Link>
                  <Link href="/blog" className="block px-3 py-2 rounded hover:bg-gray-50 no-underline text-[13px]" role="menuitem">Blog</Link>
                  <Link href="/docs" className="block px-3 py-2 rounded hover:bg-gray-50 no-underline text-[13px]" role="menuitem">Docs</Link>
                  <Link href="/pricing" className="block px-3 py-2 rounded hover:bg-gray-50 no-underline text-[13px]" role="menuitem">Tarifs</Link>
                  <Link href="/help" className="block px-3 py-2 rounded hover:bg-gray-50 no-underline text-[13px]" role="menuitem">Aide</Link>
                </div>
              )}
            </div>
          </nav>
        </div>

        {/* droite : recherche compacte + nouveau + compte */}
        <div className="flex items-center gap-2">
          <input
            type="search"
            placeholder="Rechercher…"
            className="hidden sm:block w-56 md:w-64 border rounded px-3 py-2 text-[13px] focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <Link
            href="/projects/new"
            className="hidden md:inline-flex items-center rounded bg-blue-600 text-white text-[13px] font-medium px-3 py-2 hover:bg-blue-700 focus-visible:ring-2 focus-visible:ring-blue-500"
          >
            + Nouveau projet
          </Link>

          <div className="relative" ref={authRef}>
            <button
              onClick={(e) => { e.stopPropagation(); setAuthOpen(v => !v); }}
              className="inline-flex items-center gap-1.5 px-3 py-2 rounded border text-[13px] hover:bg-gray-50 focus-visible:ring-2 focus-visible:ring-blue-500"
              aria-haspopup="menu"
              aria-expanded={authOpen}
            >
              Compte ▾
            </button>
            {authOpen && (
              <div role="menu" className="absolute right-0 mt-2 w-56 rounded border bg-white shadow p-1">
                <Link href="/signup" className="block px-3 py-2 rounded hover:bg-gray-50 no-underline text-[13px]" role="menuitem">Inscription</Link>
                <Link href="/login" className="block px-3 py-2 rounded hover:bg-gray-50 no-underline text-[13px]" role="menuitem">Connexion</Link>
                <div className="my-1 border-t" />
                <Link href="/account/recover" className="block px-3 py-2 rounded hover:bg-gray-50 no-underline text-[13px] text-gray-600" role="menuitem">Mot de passe oublié</Link>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* menu mobile */}
      {mobileOpen && (
        <nav className="lg:hidden border-t px-3 py-3 space-y-1 bg-white">
          <Link href="/" className="block px-2 py-2 rounded hover:bg-gray-50 no-underline">Accueil</Link>
          <Link href="/about" className="block px-2 py-2 rounded hover:bg-gray-50 no-underline">À propos</Link>
          <Link href="/contact" className="block px-2 py-2 rounded hover:bg-gray-50 no-underline">Contact</Link>
          <Link href="/chat-laya" className="block px-2 py-2 rounded hover:bg-gray-50 no-underline">Chat-LAYA</Link>
          <Link href="/community" className="block px-2 py-2 rounded hover:bg-gray-50 no-underline">Communauté</Link>
          <Link href="/marketplace" className="block px-2 py-2 rounded hover:bg-gray-50 no-underline">Marketplace</Link>
          <Link href="/blog" className="block px-2 py-2 rounded hover:bg-gray-50 no-underline">Blog</Link>
          <Link href="/docs" className="block px-2 py-2 rounded hover:bg-gray-50 no-underline">Docs</Link>
          <Link href="/pricing" className="block px-2 py-2 rounded hover:bg-gray-50 no-underline">Tarifs</Link>
          <Link href="/help" className="block px-2 py-2 rounded hover:bg-gray-50 no-underline">Aide</Link>
          <div className="mt-2 border-t pt-2">
            <Link href="/signup" className="block px-2 py-2 rounded bg-blue-600 text-white text-center no-underline">
              Inscription
            </Link>
            <Link href="/login" className="block px-2 py-2 mt-1 rounded border text-center no-underline">
              Connexion
            </Link>
          </div>
        </nav>
      )}
    </header>
  );
}
