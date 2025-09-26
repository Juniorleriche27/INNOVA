// innova-frontend/components/layout/sidebar.tsx
"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";

type Item = { href: string; label: string; icon: string; exact?: boolean };

const NAV: Item[] = [
  { href: "/projects", label: "Projets", icon: "📂" },
  { href: "/domains", label: "Domaines", icon: "🌍" },
  { href: "/contributors", label: "Contributeurs", icon: "👥" },
  { href: "/technologies", label: "Technologies", icon: "⚙️" },
];

export default function Sidebar() {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside
      className={[
        "h-full border-r bg-white",
        "transition-[width] duration-200 ease-out",
        collapsed ? "w-16" : "w-64",
      ].join(" ")}
    >
      {/* Top */}
      <div className="flex items-center justify-between px-4 py-4">
        {!collapsed ? (
          <div className="text-lg font-bold tracking-wide text-gray-900">
            INNOVA+
          </div>
        ) : (
          <div className="text-base font-bold text-gray-900">I+</div>
        )}
        <button
          onClick={() => setCollapsed((v) => !v)}
          className="rounded border px-2 py-1 text-xs text-gray-700 hover:bg-gray-50"
          aria-label="Rétracter la sidebar"
          title={collapsed ? "Déplier" : "Rétracter"}
        >
          {collapsed ? "»" : "«"}
        </button>
      </div>

      {/* Nav */}
      <nav className="px-2 pb-2">
        {NAV.map((it) => {
          const active = it.exact ? pathname === it.href : pathname.startsWith(it.href);
          return (
            <Link
              key={it.href}
              href={it.href}
              className={[
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm no-underline",
                active
                  ? "bg-gray-100 text-gray-900"
                  : "text-gray-700 hover:bg-gray-100",
              ].join(" ")}
              aria-current={active ? "page" : undefined}
            >
              <span className="text-lg">{it.icon}</span>
              {!collapsed && <span className="truncate">{it.label}</span>}
            </Link>
          );
        })}

        {/* + Nouveau (contexte projets) */}
        <Link
          href="/projects/new"
          className={[
            "mt-1 ml-9 block rounded-lg px-3 py-1.5 text-xs no-underline",
            "text-gray-600 hover:bg-gray-100",
            collapsed ? "hidden" : "",
          ].join(" ")}
        >
          + Nouveau
        </Link>
      </nav>

      {/* Footer */}
      <div className="mt-auto px-4 py-3 text-[11px] text-gray-500 border-t">
        {!collapsed ? "v1.0.0" : "v1"}
      </div>
    </aside>
  );
}
