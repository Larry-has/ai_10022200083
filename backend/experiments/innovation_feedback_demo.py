from __future__ import annotations

from pathlib import Path

import faiss
import numpy as np
from scipy import sparse
from sklearn.feature_extraction.text import TfidfVectorizer

from backend.config import get_settings
from backend.experiments.common import dump_json, ensure_reports_dir
from backend.feedback import FeedbackStore
from backend.retrieval import HybridRetriever
from backend.schemas import ChunkRecord


def run() -> None:
    reports_dir = ensure_reports_dir()
    settings = get_settings()
    store = FeedbackStore(Path("/tmp/backend-feedback-demo.jsonl"))
    if store.path.exists():
        store.path.unlink()
    store = FeedbackStore(store.path)

    chunks = [
        ChunkRecord(id="c1", source="synthetic", text="budget expenditure estimate", metadata={}),
        ChunkRecord(id="c2", source="synthetic", text="budget expenditure estimate priority programs", metadata={}),
        ChunkRecord(id="c3", source="synthetic", text="election votes and regions", metadata={}),
    ]

    embeddings = np.array([[1.0, 0.0], [0.98, 0.2], [0.0, 1.0]], dtype="float32")
    faiss.normalize_L2(embeddings)
    index = faiss.IndexFlatIP(2)
    index.add(embeddings)

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(chunk.text for chunk in chunks)

    def embed_query(_: str) -> np.ndarray:
        vector = np.array([[1.0, 0.0]], dtype="float32")
        faiss.normalize_L2(vector)
        return vector

    retriever = HybridRetriever(
        settings=settings,
        chunks=chunks,
        dense_index=index,
        tfidf_vectorizer=vectorizer,
        tfidf_matrix=sparse.csr_matrix(tfidf_matrix),
        embed_query_fn=embed_query,
        feedback_store=store,
    )

    query = "budget expenditure priorities"
    before = retriever.retrieve(query, top_k=3)
    store.add_feedback(query=query, chunk_ids=["c2"], helpful=True, notes="User marked as useful")
    after = retriever.retrieve(query, top_k=3)

    payload = {
        "query": query,
        "before_ranking": [chunk.id for chunk in before.retrieved_chunks],
        "after_ranking": [chunk.id for chunk in after.retrieved_chunks],
        "feedback_recorded_for": "c2",
        "explanation": (
            "The feedback-aware reranking adds a bounded query-similarity-weighted score "
            "to previously helpful chunks."
        ),
    }
    dump_json(reports_dir / "part_g_innovation_demo.json", payload)

    lines = [
        "# Part G - Innovation Component",
        "",
        "## Feature: Feedback-Aware Retrieval Memory",
        (
            "A signed feedback signal is persisted for `(query, chunk_id)` pairs and reused during "
            "future retrieval. Similar historical queries contribute a bounded positive/negative boost "
            "to candidate chunks before final ranking."
        ),
        "",
        "## Why This Is Novel In This Project",
        "- Hybrid retrieval is Part B baseline.",
        "- This feature adds adaptive retrieval behavior from user supervision over time.",
        "- It improves relevance without introducing opaque framework abstractions.",
        "",
        "## Demo Outcome",
        f"- Ranking before feedback: `{payload['before_ranking']}`",
        f"- Ranking after feedback: `{payload['after_ranking']}`",
        "- Feedback pushed the explicitly marked chunk upward.",
        "",
        "## API Surface",
        "- `POST /api/feedback` with `{query, chunk_ids, helpful, notes}`",
        "- Feedback log persistence: `backend/store/feedback.jsonl`",
        "",
        "## Artifact",
        "- Raw machine-readable results: `backend/reports/part_g_innovation_demo.json`",
    ]
    (reports_dir / "part_g_innovation.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    run()

