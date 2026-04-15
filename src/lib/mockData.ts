/**
 * Mock data used when USE_MOCK is true in the API service.
 * This file is only imported by api.ts — never by components directly.
 */

import type { RetrievedChunk, PipelineLog, RAGResponse } from "./types";

const MOCK_CHUNKS: RetrievedChunk[] = [
  {
    id: "chunk-1",
    source: "Ghana_Election_Result.csv",
    text: "In the 2020 presidential election, the NPP candidate received 6,730,413 votes (51.30%) while the NDC candidate received 6,214,889 votes (47.36%) across all 275 constituencies.",
    similarityScore: 0.94,
    rank: 1,
  },
  {
    id: "chunk-2",
    source: "2025-Budget-Statement.pdf",
    text: "The total government expenditure for 2025 is projected at GH¢244.4 billion, representing 26.2% of GDP. Revenue and Grants are projected at GH¢192.8 billion.",
    similarityScore: 0.87,
    rank: 2,
  },
  {
    id: "chunk-3",
    source: "2025-Budget-Statement.pdf",
    text: "The education sector has been allocated GH¢28.3 billion, reflecting the government's commitment to human capital development and access to quality education at all levels.",
    similarityScore: 0.76,
    rank: 3,
  },
  {
    id: "chunk-4",
    source: "Ghana_Election_Result.csv",
    text: "The Ashanti Region recorded the highest voter turnout at 82.3%, with 3,421,209 valid votes cast. The Greater Accra Region followed with 2,891,044 valid votes.",
    similarityScore: 0.61,
    rank: 4,
  },
];

const MOCK_FINAL_PROMPT = `You are an AI assistant for Academic City. Use ONLY the provided context to answer the user's question. If the context does not contain enough information, say so.

### Context:
[Chunk 1 - Ghana_Election_Result.csv (score: 0.94)]:
In the 2020 presidential election, the NPP candidate received 6,730,413 votes...

[Chunk 2 - 2025-Budget-Statement.pdf (score: 0.87)]:
The total government expenditure for 2025 is projected at GH¢244.4 billion...

### User Question:
What was the total government expenditure for 2025 and how did the 2020 election results compare?

### Instructions:
- Answer based only on the context above.
- Cite sources when possible.
- If unsure, state that the information is not available in the provided documents.`;

function generateLogs(query: string): PipelineLog[] {
  const now = new Date();
  return [
    { step: "query_received", timestamp: now.toISOString(), detail: `Query: "${query}"` },
    { step: "retrieval_started", timestamp: new Date(now.getTime() + 120).toISOString(), detail: "Searching vector store (FAISS)" },
    { step: "chunks_ranked", timestamp: new Date(now.getTime() + 450).toISOString(), detail: "4 chunks retrieved, ranked by cosine similarity" },
    { step: "context_selected", timestamp: new Date(now.getTime() + 520).toISOString(), detail: "Top 2 chunks selected (score > 0.80)" },
    { step: "prompt_constructed", timestamp: new Date(now.getTime() + 560).toISOString(), detail: "Final prompt assembled with context injection" },
    { step: "response_generated", timestamp: new Date(now.getTime() + 1800).toISOString(), detail: "LLM response received (1.24s)" },
  ];
}

export function getMockChatResponse(query: string): RAGResponse {
  return {
    answer: `Based on the retrieved documents:\n\n**Government Expenditure (2025):** The total government expenditure for 2025 is projected at GH¢244.4 billion, representing 26.2% of GDP. Revenue and Grants are projected at GH¢192.8 billion.\n\n**2020 Election Results:** The NPP candidate received 6,730,413 votes (51.30%) while the NDC candidate received 6,214,889 votes (47.36%). The Ashanti Region had the highest voter turnout at 82.3%.\n\n*Sources: 2025-Budget-Statement.pdf, Ghana_Election_Result.csv*`,
    chunks: MOCK_CHUNKS,
    finalPrompt: MOCK_FINAL_PROMPT,
    logs: generateLogs(query),
  };
}
