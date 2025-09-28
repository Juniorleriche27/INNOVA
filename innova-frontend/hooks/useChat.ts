"use client";
import { useState } from "react";
import { sendChat, ChatMessage, ChatSource } from "@/lib/api-client/chat";

type Message = ChatMessage & { sources?: ChatSource[] | undefined };

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function ask(rawText: string) {
    const text = rawText.trim();
    if (!text) return;

    setError(null);
    const userMessage: Message = { role: "user", content: text };
    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);

    try {
      const res = await sendChat({ question: text });
      const assistantMessage: Message = {
        role: "assistant",
        content: res.answer,
        sources: res.sources,
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Erreur inconnue");
    } finally {
      setLoading(false);
    }
  }

  return { messages, ask, loading, error };
}
