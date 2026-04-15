import type { RAGResponse } from "@/lib/types";
import ChunkCard from "./ChunkCard";
import { ScrollArea } from "@/components/ui/scroll-area";
import { FileText, List, Code } from "lucide-react";
import { useState } from "react";
import { submitChunkFeedback } from "@/lib/api";

interface RetrievalPanelProps {
  data: RAGResponse | null;
  query: string;
}

function SectionLabel({ icon: Icon, children }: { icon: React.ElementType; children: React.ReactNode }) {
  return (
    <div className="flex items-center gap-1.5 mb-2.5">
      <Icon className="h-3.5 w-3.5 text-muted-foreground" />
      <h3 className="text-[11px] font-semibold uppercase tracking-widest text-muted-foreground">
        {children}
      </h3>
    </div>
  );
}

export default function RetrievalPanel({ data, query }: RetrievalPanelProps) {
  const [feedbackByChunk, setFeedbackByChunk] = useState<Record<string, "up" | "down" | null>>({});
  const [pendingChunkId, setPendingChunkId] = useState<string | null>(null);

  if (!data) {
    return (
      <div className="flex flex-col h-full bg-card items-center justify-center">
        <p className="text-xs text-muted-foreground opacity-50">
          No retrieval data yet
        </p>
      </div>
    );
  }

  const handleChunkFeedback = async (
    chunkId: string,
    helpful: boolean
  ) => {
    if (!query) return;
    try {
      setPendingChunkId(chunkId);
      await submitChunkFeedback({
        query,
        chunk_ids: [chunkId],
        helpful,
      });
      setFeedbackByChunk((prev) => ({
        ...prev,
        [chunkId]: helpful ? "up" : "down",
      }));
    } catch {
      // Feedback failure should not block browsing inspector data
    } finally {
      setPendingChunkId(null);
    }
  };

  return (
    <div className="flex flex-col h-full bg-card">
      <div className="px-5 py-3 border-b">
        <span className="text-[11px] font-semibold uppercase tracking-widest text-muted-foreground">
          Retrieval Inspector
        </span>
      </div>

      <ScrollArea className="flex-1 min-h-0">
        <div className="px-5 py-4 space-y-6">
          {/* Retrieved Chunks */}
          <section>
            <SectionLabel icon={FileText}>
              Retrieved Chunks · {data.chunks.length}
            </SectionLabel>
            <div className="space-y-2">
              {data.chunks.map((chunk) => (
                <ChunkCard
                  key={chunk.id}
                  chunk={chunk}
                  onFeedback={(selectedChunk, helpful) =>
                    handleChunkFeedback(selectedChunk.id, helpful)
                  }
                  feedbackState={feedbackByChunk[chunk.id] ?? null}
                  disabled={pendingChunkId === chunk.id || !query}
                />
              ))}
            </div>
          </section>

          {/* Final Prompt */}
          <section>
            <SectionLabel icon={Code}>Final Prompt Sent to LLM</SectionLabel>
            <pre className="text-[11px] leading-relaxed bg-muted/50 rounded border p-3 overflow-x-auto whitespace-pre-wrap text-foreground/80 font-mono">
              {data.finalPrompt}
            </pre>
          </section>

          {/* System Logs */}
          <section>
            <SectionLabel icon={List}>Pipeline Logs</SectionLabel>
            <div className="space-y-px rounded border overflow-hidden">
              {data.logs.map((log, i) => (
                <div
                  key={i}
                  className="flex items-start gap-3 text-[11px] bg-muted/30 px-3 py-2 border-b last:border-b-0"
                >
                  <span className="font-mono text-primary font-medium shrink-0 w-[140px]">
                    {log.step}
                  </span>
                  <span className="text-muted-foreground">{log.detail}</span>
                </div>
              ))}
            </div>
          </section>
        </div>
      </ScrollArea>
    </div>
  );
}
