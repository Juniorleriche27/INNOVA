import { api } from "./client";

export type ChatMessage = { role: "user" | "assistant" | "system"; content: string };

export type ChatRequest = {
  question: string;
  temperature?: number;
  max_tokens?: number;
  top_k?: number;
  provider?: "cohere";
};

export type ChatSource = {
  id: string;
  score?: number;
  payload?: Record<string, unknown> | null;
};

export type ChatTokenUsage = {
  input_tokens?: number | null;
  output_tokens?: number | null;
  total_tokens?: number | null;
};

export type ChatResponse = {
  answer: string;
  provider: string;
  model: string;
  latency_ms?: number;
  tokens?: ChatTokenUsage | null;
  sources?: ChatSource[];
  rag_error?: string;
};

export async function sendChat(req: ChatRequest): Promise<ChatResponse> {
  return api<ChatResponse>("/chatlaya/ask", { method: "POST", body: JSON.stringify(req) });
}
