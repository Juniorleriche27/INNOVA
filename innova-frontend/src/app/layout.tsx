import "./globals.css";
import type { Metadata } from "next";
import Sidebar from "./components/Sidebar";
import Headbar from "./components/Headbar";

export const metadata: Metadata = {
  title: "INNOVA+",
  description: "Frontend INNOVA+",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr">
      <body className="font-sans text-gray-900 h-screen w-screen bg-gray-50 overflow-hidden">
        <div className="flex h-full">
          <Sidebar />
          <div className="flex-1 flex flex-col min-w-0">
            <Headbar />
            <main className="flex-1 overflow-y-auto p-6">{children}</main>
          </div>
        </div>
      </body>
    </html>
  );
}
