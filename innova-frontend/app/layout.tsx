// innova-frontend/app/layout.tsx
import "./globals.css";
import type { Metadata } from "next";
import type { ReactNode } from "react";

import Headbar from "@/components/layout/headbar";
import Sidebar from "@/components/layout/sidebar";
import Footer from "@/components/layout/footer";

export const metadata: Metadata = {
  title: "INNOVA+",
  description: "Plateforme INNOVA+",
};

export default function RootLayout(props: { children: ReactNode }) {
  const { children } = props;
  return (
    <html lang="fr">
      <body className="min-h-screen bg-white text-gray-900">
        {/* Header */}
        <Headbar />

        {/* Main: sidebar + content */}
        <div className="flex">
          <aside className="hidden md:block w-64 border-r min-h-[calc(100vh-3rem)]">
            <Sidebar />
          </aside>
          <main className="flex-1 min-w-0">{children}</main>
        </div>

        {/* Footer */}
        <Footer />
      </body>
    </html>
  );
}
