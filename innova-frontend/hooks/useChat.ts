"use client";
import { useState } from "react";
import { sendChat, ChatMessage } from "@/lib/api-client/chat";

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function ask(text: string) {
    setError(null);

    // construire le prochain message utilisateur
    const next: ChatMessage[] = [...messages, { role: "user", content: text } as ChatMessage];
    setMessages(next);
    setLoading(true);

    try {
      const res = await sendChat({ messages: next });

      // ajouter la réponse assistant
      setMessages([
        ...next,
        { role: "assistant", content: res.answer } as ChatMessage,
      ]);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Erreur inconnue");
    } finally {
      setLoading(false);
    }
  }

  return { messages, ask, loading, error };
}
