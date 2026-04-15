from __future__ import annotations

import re


WHITESPACE_RE = re.compile(r"\s+")


def normalize_whitespace(text: str) -> str:
    return WHITESPACE_RE.sub(" ", text).strip()


def sliding_window_chunk(
    text: str,
    *,
    chunk_size: int,
    chunk_overlap: int,
) -> list[str]:
    cleaned = normalize_whitespace(text)
    if not cleaned:
        return []

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")
    if chunk_overlap < 0:
        raise ValueError("chunk_overlap cannot be negative")
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    chunks: list[str] = []
    start = 0
    step = chunk_size - chunk_overlap

    while start < len(cleaned):
        end = min(start + chunk_size, len(cleaned))
        candidate = cleaned[start:end].strip()
        if candidate:
            chunks.append(candidate)
        if end >= len(cleaned):
            break
        start += step

    return chunks
