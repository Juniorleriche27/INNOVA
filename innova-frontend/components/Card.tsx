// components/Card.tsx
import React from "react";

type CardProps = {
  title: React.ReactNode;
  subtitle?: React.ReactNode;
  right?: React.ReactNode;
  href?: string;
  desc?: React.ReactNode;   // description optionnelle
  cta?: React.ReactNode;    // call-to-action optionnel
  muted?: boolean;          // style atténué optionnel
  tone?: "primary" | "secondary"; // tone optionnel
};

export default function Card({
  title,
  subtitle,
  right,
  href,
  desc,
  cta,
  muted,
  tone,
}: CardProps) {
  const content = (
    <div
      className={`w-full rounded-2xl border px-5 py-4 shadow-sm transition ${
        muted
          ? "bg-gray-100 border-gray-100"
          : "bg-white border-gray-200 hover:border-gray-300"
      } ${tone === "primary" ? "border-blue-500" : ""}`}
    >
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="text-lg font-semibold">{title}</div>
          {subtitle ? <div className="text-sm text-gray-600 mt-1">{subtitle}</div> : null}
          {desc ? <div className="text-sm text-gray-500 mt-1">{desc}</div> : null}
        </div>
        <div className="text-right">
          {right ? <div className="text-sm text-blue-600">{right}</div> : null}
          {cta ? <div className="text-sm text-blue-500 mt-1">{cta}</div> : null}
        </div>
      </div>
    </div>
  );

  return href ? (
    <a href={href} className="block">
      {content}
    </a>
  ) : (
    content
  );
}
