// innova-frontend/components/layout/headbar.tsx
"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useRef, useState } from "react";

const CHAT_URL = process.env.NEXT_PUBLIC_CHATLAYA_URL || "/chat-laya";

function NavLink(props: { href: string; children: React.ReactNode }) {
  const { href, children } = props;
  const pathname = usePathname();
  const active = pathname === href;

  // Avec Next 15 + typedRoutes, Link vérifie que la route existe.
  // Pour éviter les erreurs pendant la mise en place des pages (about, contact, etc.),
  // on neutralise *uniquement ici* le typage du href.
  return (
    <Link
      href={href as unknown as any}
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

  // ✅ refs doivent accepter null en initialisation
  const authRef = useRef<HTMLDivElement | null>(null);
  const moreRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    function onClick(e: MouseEvent) {
      if (!authRef.current?.contains(e.target as Node)) setAuthOpen(false);
      if (!moreRef.current?.contains(e.target as Node)) setMoreOpen(false);
    }
    window.addEventListener("click", onClick);
    return () => window.removeEventListener("click", onClick);
  }, []);

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
        {/* gauche */}
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

            {/* Chat-LAYA : externe si URL absolue, sinon route interne */}
            {CHAT_URL.startsWith("http") ? (
              <a
                href={CHAT_URL}
                className="no-underline px-2 py-1 rounded text-[13px] font-medium text-gray-700 hover:text-blue-600 focus-visible:ring-2 focus-visible:ring-blue-500"
                target="_self"
                rel="noopener noreferrer"
              >
                Chat-LAYA
              </a>
            ) : (
              <NavLink href={CHAT_URL}>Chat-LAYA</NavLink>
            )}

            {/* Plus */}
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
                  <NavLink href="/community">Communauté</NavLink>
                  <NavLink href="/marketplace">Marketplace</NavLink>
                  <NavLink href="/blog">Blog</NavLink>
                  <NavLink href="/docs">Docs</NavLink>
                  <NavLink href="/pricing">Tarifs</NavLink>
                  <NavLink href="/help">Aide</NavLink>
                </div>
              )}
            </div>
          </nav>
        </div>

        {/* droite */}
        <div className="flex items-center gap-2">
          <input
            type="search"
            placeholder="Rechercher…"
            className="hidden sm:block w-56 md:w-64 border rounded px-3 py-2 text-[13px] focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <NavLink href="/projects/new">+ Nouveau projet</NavLink>

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
                <NavLink href="/signup">Inscription</NavLink>
                <NavLink href="/login">Connexion</NavLink>
                <div className="my-1 border-t" />
                <NavLink href="/account/recover">Mot de passe oublié</NavLink>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* mobile */}
      {mobileOpen && (
        <nav className="lg:hidden border-t px-3 py-3 space-y-1 bg-white">
          <NavLink href="/">Accueil</NavLink>
          <NavLink href="/about">À propos</NavLink>
          <NavLink href="/contact">Contact</NavLink>
          {CHAT_URL.startsWith("http") ? (
            <a href={CHAT_URL} className="block px-2 py-2 rounded hover:bg-gray-50 no-underline">Chat-LAYA</a>
          ) : (
            <NavLink href={CHAT_URL}>Chat-LAYA</NavLink>
          )}
          <NavLink href="/community">Communauté</NavLink>
          <NavLink href="/marketplace">Marketplace</NavLink>
          <NavLink href="/blog">Blog</NavLink>
          <NavLink href="/docs">Docs</NavLink>
          <NavLink href="/pricing">Tarifs</NavLink>
          <NavLink href="/help">Aide</NavLink>
          <div className="mt-2 border-t pt-2">
            <NavLink href="/signup">Inscription</NavLink>
            <NavLink href="/login">Connexion</NavLink>
          </div>
        </nav>
      )}
    </header>
  );
}
