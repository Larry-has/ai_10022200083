from __future__ import annotations

try:
    from .config import Settings
    from .schemas import RetrievedChunk
except ImportError:  # pragma: no cover
    from config import Settings
    from schemas import RetrievedChunk


def select_context(
    chunks: list[RetrievedChunk],
    *,
    max_context_chars: int,
) -> tuple[list[RetrievedChunk], str]:
    selected: list[RetrievedChunk] = []
    remaining_budget = max_context_chars

    for chunk in chunks:
        block = (
            f"[Rank {chunk.rank} | Source: {chunk.source} | Score: {chunk.similarityScore:.4f}]\n"
            f"{chunk.text}\n"
        )
        if selected and len(block) > remaining_budget:
            break
        if not selected and len(block) > max_context_chars:
            truncated_text = chunk.text[: max_context_chars - 120].rstrip()
            block = (
                f"[Rank {chunk.rank} | Source: {chunk.source} | Score: {chunk.similarityScore:.4f}]\n"
                f"{truncated_text}\n"
            )
        selected.append(chunk)
        remaining_budget -= len(block)

    context_blocks = [
        (
            f"[Context {chunk.rank}] Source={chunk.source}; Similarity={chunk.similarityScore:.4f}\n"
            f"{chunk.text}"
        )
        for chunk in selected
    ]
    context = "\n\n".join(context_blocks)
    return selected, context


def _baseline_prompt(query: str, context: str) -> str:
    return (
        "Answer the user question using the retrieved context.\n\n"
        f"Question:\n{query}\n\n"
        f"Context:\n{context if context else 'No context.'}\n\n"
        "Provide a concise answer."
    )


def _grounded_v2_prompt(query: str, context: str) -> str:
    return (
        "You are an academic RAG assistant for a university AI project.\n"
        "Use ONLY the provided context to answer the user's question.\n"
        "If the context is insufficient, say that the answer is not supported by the retrieved documents.\n"
        "Do not invent facts, values, sources, or citations.\n"
        "When you answer, cite the supporting source names in plain text.\n\n"
        f"User Question:\n{query}\n\n"
        f"Retrieved Context:\n{context if context else 'No relevant context was selected.'}\n\n"
        "Answer Requirements:\n"
        "1. Answer only from the context.\n"
        "2. If evidence is incomplete, state the limitation clearly.\n"
        "3. Keep the answer concise but specific.\n"
        "4. Cite evidence using explicit source names only, for example [Source: Ghana_Election_Result.csv].\n"
        "5. Do not use placeholder citations like [Context 1] or [Context 2].\n"
    )


def _skeptical_v3_prompt(query: str, context: str) -> str:
    return (
        "You are a strict evidence-based assistant.\n"
        "You must only use statements that appear in the context blocks.\n"
        "For each claim, include a source tag in square brackets using the source filename.\n"
        "If evidence is missing, reply with exactly: 'Insufficient evidence in provided documents.'\n\n"
        f"Question:\n{query}\n\n"
        f"Context Blocks:\n{context if context else 'No relevant context was selected.'}\n\n"
        "Return a short answer with explicit source tags.\n"
        "Do not use placeholder citations like [Context 1] or [Context 2]."
    )


def build_prompt(
    *,
    query: str,
    chunks: list[RetrievedChunk],
    settings: Settings,
    prompt_mode: str | None = None,
) -> tuple[str, list[RetrievedChunk]]:
    selected_chunks, context = select_context(
        chunks,
        max_context_chars=settings.max_context_chars,
    )
    mode = (prompt_mode or settings.prompt_mode).strip().lower()
    prompt_builders = {
        "baseline_v1": _baseline_prompt,
        "grounded_v2": _grounded_v2_prompt,
        "skeptical_v3": _skeptical_v3_prompt,
    }
    prompt = prompt_builders.get(mode, _grounded_v2_prompt)(query, context)
    return prompt, selected_chunks
