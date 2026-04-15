import { useState, useRef, useEffect } from "react";
import { Send, RotateCcw, Loader2 } from "lucide-react";
import ReactMarkdown from "react-markdown";
import { Button } from "@/components/ui/button";
import type { ChatMessage, RAGResponse } from "@/lib/types";
import { sendChatMessage } from "@/lib/api";

interface ChatPanelProps {
  onResponse: (response: RAGResponse) => void;
}

export default function ChatPanel({ onResponse }: ChatPanelProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    const query = input.trim();
    if (!query || loading) return;

    const userMsg: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: query,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const data = await sendChatMessage(query);
      const assistantMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: data.answer,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMsg]);
      onResponse(data);
    } catch {
      const errorMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: "Error: Could not reach the backend. Please try again.",
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-card">
      {/* Panel label */}
      <div className="flex items-center justify-between px-5 py-3 border-b">
        <span className="text-[11px] font-semibold uppercase tracking-widest text-muted-foreground">
          Query Interface
        </span>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setMessages([])}
          disabled={messages.length === 0}
          className="h-7 px-2 text-[11px] text-muted-foreground hover:text-foreground"
        >
          <RotateCcw className="h-3 w-3 mr-1" /> Reset
        </Button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-5 py-4 space-y-4 min-h-0">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center gap-2 opacity-60">
            <p className="text-sm text-muted-foreground max-w-[280px] leading-relaxed">
              Enter a query to search Ghana election results and the 2025 national budget.
            </p>
          </div>
        )}
        {messages.map((msg) => (
          <div key={msg.id} className="space-y-1">
            <span className="text-[10px] font-semibold uppercase tracking-widest text-muted-foreground">
              {msg.role === "user" ? "You" : "Assistant"}
            </span>
            <div
              className={`text-sm leading-relaxed ${
                msg.role === "user"
                  ? "text-foreground"
                  : "text-foreground/90 pl-3 border-l-2 border-primary/30"
              }`}
            >
              {msg.role === "assistant" ? (
                <ReactMarkdown
                  components={{
                    p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                    strong: ({ children }) => <strong className="font-semibold text-foreground">{children}</strong>,
                    em: ({ children }) => <em className="italic text-muted-foreground">{children}</em>,
                  }}
                >
                  {msg.content}
                </ReactMarkdown>
              ) : (
                <span className="whitespace-pre-wrap">{msg.content}</span>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="space-y-1">
            <span className="text-[10px] font-semibold uppercase tracking-widest text-muted-foreground">
              Assistant
            </span>
            <div className="text-sm text-muted-foreground pl-3 border-l-2 border-primary/30 flex items-center gap-2">
              <Loader2 className="h-3.5 w-3.5 animate-spin" />
              Processing pipeline...
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="px-5 py-3 border-t">
        <div className="flex gap-2 items-center">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question..."
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            disabled={loading}
            className="flex-1 h-9 px-3 text-sm bg-muted/50 border rounded-md focus:outline-none focus:ring-1 focus:ring-ring text-foreground placeholder:text-muted-foreground"
          />
          <Button
            onClick={handleSend}
            disabled={loading || !input.trim()}
            size="sm"
            className="h-9 px-3"
          >
            <Send className="h-3.5 w-3.5" />
          </Button>
        </div>
      </div>
    </div>
  );
}
