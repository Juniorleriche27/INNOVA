import type { NextConfig } from "next";

const isProd = process.env.NODE_ENV === "production";

// Optionnel : si tu veux proxifier ton API Render via /api/*
// (ex: /api/projects -> https://innova-1-v3ab.onrender.com/projects)
// Mets à jour cette variable si ton URL change.
const API_BASE = (process.env.NEXT_PUBLIC_API_URL || "").replace(/\/+$/, "");

const nextConfig: NextConfig = {
  // Qualité & DX
  reactStrictMode: true,
  poweredByHeader: false,

  // Lint/TS : on tolère les erreurs en prod pour ne pas bloquer les builds.
  // (Quand tout sera propre, remets ces deux flags à false.)
  eslint: { ignoreDuringBuilds: isProd },
  typescript: { ignoreBuildErrors: isProd },

  // Optimisations Next 15
  experimental: {
    typedRoutes: true,
    optimizePackageImports: ["react", "react-dom"],
  },

  // Sécurité HTTP de base
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          { key: "X-Frame-Options", value: "SAMEORIGIN" },
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "Referrer-Policy", value: "no-referrer" },
          // Ajuste selon besoins (ex: autoriser geolocation si nécessaire)
          {
            key: "Permissions-Policy",
            value:
              "camera=(), microphone=(), geolocation=(), interest-cohort=()",
          },
        ],
      },
    ];
  },

  // (Optionnel) Proxy vers ton backend pour éviter les CORS côté navigateur.
  // Si tu l'actives côté front, tu peux appeler fetch('/api/...') au lieu
  // d'utiliser directement NEXT_PUBLIC_API_URL dans le code.
  async rewrites() {
    if (!API_BASE) return [];
    return [
      {
        source: "/api/:path*",
        destination: `${API_BASE}/:path*`,
      },
    ];
  },

  // Images externes (à compléter si tu charges des images distantes)
  images: {
    remotePatterns: [
      // exemple :
      // { protocol: "https", hostname: "innova-1-v3ab.onrender.com" },
      // { protocol: "https", hostname: "*.vercel.app" },
    ],
  },
};

export default nextConfig;
