// src/components/Card.tsx
import React from "react";

type CardProps = {
  title: React.ReactNode;
  subtitle?: React.ReactNode;
  right?: React.ReactNode;
  href?: string;
};

export default function Card({ title, subtitle, right, href }: CardProps) {
  const content = (
    <div className="w-full rounded-2xl border border-gray-200 hover:border-gray-300 bg-white px-5 py-4 shadow-sm transition">
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="text-lg font-semibold">{title}</div>
          {subtitle ? <div className="text-sm text-gray-600 mt-1">{subtitle}</div> : null}
        </div>
        {right ? <div className="text-sm text-blue-600">{right}</div> : null}
      </div>
    </div>
  );
  return href ? <a href={href} className="block">{content}</a> : content;
}
