"use client";
import { useState } from "react";

export default function InputBar({ onSend, disabled }: { onSend: (text: string) => void; disabled?: boolean }) {
  const [text, setText] = useState("");
  return (
    <form
      className="flex gap-2"
      onSubmit={(e) => {
        e.preventDefault();
        const t = text.trim();
        if (!t) return;
        onSend(t);
        setText("");
      }}
    >
      <input
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Écris un message..."
        className="flex-1 border rounded px-3 py-2"
      />
      <button
        type="submit"
        disabled={disabled}
        className="rounded bg-blue-600 text-white px-4 py-2 disabled:opacity-50"
      >
        Envoyer
      </button>
    </form>
  );
}
