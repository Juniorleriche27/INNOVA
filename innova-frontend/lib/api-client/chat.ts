import { api } from "./client";

export type ChatMessage = { role: "user" | "assistant" | "system"; content: string };
export type ChatRequest = { messages: ChatMessage[]; top_k?: number; intent?: string | null };
export type ChatResponse = { answer: string; citations: string[] };

export async function sendChat(req: ChatRequest): Promise<ChatResponse> {
  return api<ChatResponse>("/chatlaya/chat", { method: "POST", body: JSON.stringify(req) });
}

export async function sendFeedback(input: { message_id?: number; rating: -1 | 0 | 1; comment?: string }) {
  return api<{ status: "ok" }>("/chatlaya/feedback", { method: "POST", body: JSON.stringify(input) });
}
