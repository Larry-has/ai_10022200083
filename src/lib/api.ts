/**
 * API Service Layer
 * ─────────────────
 * All backend communication is centralized here.
 *
 * To connect your real backend:
 *   1. Set USE_MOCK to false
 *   2. Set API_BASE_URL to your backend URL
 *   3. The fetch calls are already wired — just ensure your API
 *      returns the shapes defined in ./types.ts
 *
 * Endpoints expected:
 *   POST {API_BASE_URL}/chat   → RAGResponse
 *   GET  {API_BASE_URL}/logs   → PipelineLog[]
 */

import type { RAGResponse, PipelineLog } from "./types";
import { getMockChatResponse } from "./mockData";

// ──── Configuration ────────────────────────────────────────────
// Toggle this to false when your backend is ready
const USE_MOCK = (process.env.NEXT_PUBLIC_USE_MOCK ?? "true").toLowerCase() === "true";

// Point this to your backend (e.g. "http://localhost:8000/api")
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "/api";

// Simulated latency for mock mode (ms)
const MOCK_DELAY = 1500;
// ───────────────────────────────────────────────────────────────

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new Error(`API error ${res.status}: ${body || res.statusText}`);
  }

  return res.json();
}

/**
 * Send a user query to the RAG pipeline.
 * Returns the assistant answer, retrieved chunks, final prompt, and logs.
 */
export async function sendChatMessage(query: string): Promise<RAGResponse> {
  if (USE_MOCK) {
    await new Promise((r) => setTimeout(r, MOCK_DELAY));
    return getMockChatResponse(query);
  }

  return request<RAGResponse>("/chat", {
    method: "POST",
    body: JSON.stringify({ query }),
  });
}

/**
 * Fetch pipeline logs (optional standalone endpoint).
 * Use this if your backend exposes logs separately from chat responses.
 */
export async function fetchLogs(): Promise<PipelineLog[]> {
  if (USE_MOCK) {
    return [];
  }

  return request<PipelineLog[]>("/logs");
}
