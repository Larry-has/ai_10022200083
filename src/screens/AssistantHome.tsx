import { useState } from "react";
import type { RAGResponse } from "@/lib/types";
import ChatPanel from "@/components/ChatPanel";
import RetrievalPanel from "@/components/RetrievalPanel";
import ThemeToggle from "@/components/ThemeToggle";
import { Database } from "lucide-react";

export default function AssistantHome() {
  const [lastResponse, setLastResponse] = useState<RAGResponse | null>(null);
  const [lastQuery, setLastQuery] = useState("");

  return (
    <div className="flex flex-col h-screen">
      <header className="border-b px-6 py-4 flex items-center justify-between shrink-0 bg-card">
        <div className="flex items-center gap-3">
          <div className="h-8 w-8 rounded bg-primary flex items-center justify-center">
            <Database className="h-4 w-4 text-primary-foreground" />
          </div>
          <div>
            <h1 className="text-base font-semibold tracking-tight text-foreground leading-none mb-0.5">
              Academic City RAG Assistant
            </h1>
            <p className="text-[11px] text-muted-foreground tracking-wide uppercase">
              Election &amp; Budget Document Analysis · Retrieval-Augmented Generation
            </p>
          </div>
        </div>
        <ThemeToggle />
      </header>

      <main className="flex-1 min-h-0 flex flex-col lg:flex-row">
        <div className="flex-1 min-h-[50vh] lg:min-h-0 lg:border-r">
          <ChatPanel
            onResponse={(response, query) => {
              setLastResponse(response);
              setLastQuery(query);
            }}
          />
        </div>
        <div className="flex-1 min-h-[50vh] lg:min-h-0 lg:w-[440px] lg:flex-none">
          <RetrievalPanel data={lastResponse} query={lastQuery} />
        </div>
      </main>
    </div>
  );
}
