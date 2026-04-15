import type { RetrievedChunk } from "@/lib/types";

function ScoreBar({ score }: { score: number }) {
  const pct = Math.round(score * 100);
  const barColor =
    score >= 0.8
      ? "bg-score-good"
      : score >= 0.6
        ? "bg-score-mid"
        : "bg-score-low";
  const textColor =
    score >= 0.8
      ? "text-score-good"
      : score >= 0.6
        ? "text-score-mid"
        : "text-score-low";

  return (
    <div className="flex items-center gap-2">
      <div className="w-16 h-1 rounded-full bg-muted overflow-hidden">
        <div className={`h-full rounded-full ${barColor}`} style={{ width: `${pct}%` }} />
      </div>
      <span className={`text-[11px] font-mono font-semibold tabular-nums ${textColor}`}>
        {pct}%
      </span>
    </div>
  );
}

export default function ChunkCard({ chunk }: { chunk: RetrievedChunk }) {
  return (
    <div className="rounded border bg-muted/20 overflow-hidden">
      {/* Meta row */}
      <div className="flex items-center justify-between px-3 py-2 bg-muted/40 border-b">
        <div className="flex items-center gap-2.5">
          <span className="inline-flex items-center justify-center h-5 w-5 rounded text-[10px] font-bold font-mono bg-primary text-primary-foreground leading-none">
            {chunk.rank}
          </span>
          <span className="text-[12px] font-semibold text-foreground tracking-tight">
            {chunk.source}
          </span>
        </div>
        <ScoreBar score={chunk.similarityScore} />
      </div>
      {/* Chunk text */}
      <p className="px-3 py-2.5 text-[12px] text-foreground/75 leading-[1.65] m-0">
        {chunk.text}
      </p>
    </div>
  );
}
