"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import type { Route } from "next";
import type { ReactNode } from "react";
import clsx from "clsx";

type NavItemProps = {
  href: Route;
  children: ReactNode;
  className?: string;
  exact?: boolean; // si true, active seulement quand le path == href
};

function NavItem({ href, children, className, exact = false }: NavItemProps) {
  const pathname = usePathname();
  const isActive = exact ? pathname === href : pathname.startsWith(href);

  return (
    <Link
      href={href}
      className={clsx(
        "block rounded px-3 py-2 no-underline outline-none transition",
        isActive
          ? "bg-gray-800 text-white"
          : "text-gray-300 hover:bg-gray-800 hover:text-white focus:bg-gray-800 focus:text-white",
        className
      )}
      aria-current={isActive ? "page" : undefined}
    >
      {children}
    </Link>
  );
}

export default function Sidebar() {
  const pathname = usePathname();
  const inProjects = pathname.startsWith("/projects");

  return (
    <aside className="h-full w-64 bg-gray-900 text-white flex flex-col">
      {/* Header */}
      <div className="px-6 py-4 text-xl font-bold tracking-wide">INNOVA+</div>

      {/* Nav */}
      <nav className="flex-1 px-3 space-y-1 text-sm">
        <NavItem href="/projects">Projets</NavItem>

        <NavItem
          href="/projects/new"
          exact
          className={clsx("ml-3 text-xs", inProjects ? "opacity-100" : "opacity-70")}
        >
          + Nouveau
        </NavItem>

        <NavItem href="/domains">Domaines</NavItem>
        <NavItem href="/contributors">Contributeurs</NavItem>
        <NavItem href="/technologies">Technologies</NavItem>
      </nav>

      {/* Footer */}
      <div className="px-6 py-4 text-[11px] text-gray-400 border-t border-white/10">
        v1.0.0
      </div>
    </aside>
  );
}
