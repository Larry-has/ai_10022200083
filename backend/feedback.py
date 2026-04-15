from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


TOKEN_RE = re.compile(r"[a-zA-Z0-9]+")


@dataclass
class FeedbackEntry:
    timestamp: str
    query: str
    chunk_id: str
    helpful: bool
    notes: str | None = None


def _tokenize(text: str) -> set[str]:
    return {token.lower() for token in TOKEN_RE.findall(text) if len(token) > 2}


def _jaccard_similarity(left: str, right: str) -> float:
    left_tokens = _tokenize(left)
    right_tokens = _tokenize(right)
    if not left_tokens or not right_tokens:
        return 0.0
    intersection = len(left_tokens & right_tokens)
    union = len(left_tokens | right_tokens)
    return intersection / union if union else 0.0


class FeedbackStore:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.touch()

    def add_feedback(
        self,
        *,
        query: str,
        chunk_ids: list[str],
        helpful: bool,
        notes: str | None = None,
    ) -> int:
        timestamp = datetime.now(timezone.utc).isoformat()
        count = 0
        with self.path.open("a", encoding="utf-8") as handle:
            for chunk_id in chunk_ids:
                entry = FeedbackEntry(
                    timestamp=timestamp,
                    query=query,
                    chunk_id=chunk_id,
                    helpful=helpful,
                    notes=notes,
                )
                handle.write(json.dumps(entry.__dict__, ensure_ascii=False) + "\n")
                count += 1
        return count

    def _load_entries(self) -> list[FeedbackEntry]:
        entries: list[FeedbackEntry] = []
        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                data = json.loads(line)
                entries.append(
                    FeedbackEntry(
                        timestamp=data["timestamp"],
                        query=data["query"],
                        chunk_id=data["chunk_id"],
                        helpful=bool(data["helpful"]),
                        notes=data.get("notes"),
                    )
                )
        return entries

    def score_boosts(
        self,
        *,
        query: str,
        candidate_chunk_ids: set[str],
        scale: float,
    ) -> dict[str, float]:
        boosts: dict[str, float] = {}
        for entry in self._load_entries():
            if entry.chunk_id not in candidate_chunk_ids:
                continue
            similarity = _jaccard_similarity(query, entry.query)
            if similarity <= 0:
                continue
            direction = 1.0 if entry.helpful else -1.0
            boosts[entry.chunk_id] = boosts.get(entry.chunk_id, 0.0) + (direction * similarity * scale)

        for chunk_id, score in list(boosts.items()):
            boosts[chunk_id] = max(min(score, scale), -scale)
        return boosts
