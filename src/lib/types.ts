/**
 * Shared types for the RAG chatbot.
 * These match the expected shape of your backend API responses.
 */

export interface RetrievedChunk {
  id: string;
  source: string;
  text: string;
  similarityScore: number;
  rank: number;
}

export interface PipelineLog {
  step: string;
  timestamp: string;
  detail?: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
}

export interface RAGResponse {
  answer: string;
  chunks: RetrievedChunk[];
  finalPrompt: string;
  logs: PipelineLog[];
}
