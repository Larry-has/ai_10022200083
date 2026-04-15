from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import faiss
import numpy as np
from scipy import sparse
from sklearn.feature_extraction.text import TfidfVectorizer

try:
    from .config import Settings
    from .feedback import FeedbackStore
    from .schemas import ChunkRecord, RetrievalCandidate, RetrievedChunk
except ImportError:  # pragma: no cover
    from config import Settings
    from feedback import FeedbackStore
    from schemas import ChunkRecord, RetrievalCandidate, RetrievedChunk


@dataclass
class RetrievalResult:
    retrieved_chunks: list[RetrievedChunk]
    candidates: list[RetrievalCandidate]


def _normalize_score_map(score_map: dict[str, float]) -> dict[str, float]:
    if not score_map:
        return {}

    values = list(score_map.values())
    max_value = max(values)
    min_value = min(values)
    if max_value == min_value:
        return {key: 1.0 for key in score_map}

    return {
        key: (value - min_value) / (max_value - min_value)
        for key, value in score_map.items()
    }


class HybridRetriever:
    def __init__(
        self,
        *,
        settings: Settings,
        chunks: list[ChunkRecord],
        dense_index: faiss.IndexFlatIP,
        tfidf_vectorizer: TfidfVectorizer,
        tfidf_matrix: sparse.csr_matrix,
        embed_query_fn,
        feedback_store: Optional[FeedbackStore] = None,
    ) -> None:
        self.settings = settings
        self.chunks = chunks
        self.chunk_lookup = {chunk.id: chunk for chunk in chunks}
        self.dense_index = dense_index
        self.tfidf_vectorizer = tfidf_vectorizer
        self.tfidf_matrix = tfidf_matrix
        self.embed_query_fn = embed_query_fn
        self.feedback_store = feedback_store

    def retrieve(self, query: str, *, top_k: Optional[int] = None) -> RetrievalResult:
        limit = top_k or self.settings.top_k
        dense_scores, dense_indices = self._dense_search(query)
        sparse_scores, sparse_indices = self._sparse_search(query)

        dense_map = {
            self.chunks[index].id: float(score)
            for score, index in zip(dense_scores, dense_indices)
            if index != -1
        }
        sparse_map = {
            self.chunks[index].id: float(score)
            for score, index in zip(sparse_scores, sparse_indices)
            if index != -1
        }

        normalized_dense = _normalize_score_map(dense_map)
        normalized_sparse = _normalize_score_map(sparse_map)

        candidate_ids = set(dense_map) | set(sparse_map)
        feedback_boosts = self._feedback_boosts(query, candidate_ids)
        fused_candidates: list[RetrievalCandidate] = []

        for chunk_id in candidate_ids:
            chunk = self.chunk_lookup[chunk_id]
            dense_score = dense_map.get(chunk_id, 0.0)
            sparse_score = sparse_map.get(chunk_id, 0.0)
            feedback_score = feedback_boosts.get(chunk_id, 0.0)
            fused_score = (
                self.settings.dense_weight * normalized_dense.get(chunk_id, 0.0)
                + self.settings.sparse_weight * normalized_sparse.get(chunk_id, 0.0)
                + feedback_score
            )
            fused_candidates.append(
                RetrievalCandidate(
                    chunk=chunk,
                    dense_score=dense_score,
                    sparse_score=sparse_score,
                    feedback_score=feedback_score,
                    fused_score=fused_score,
                )
            )

        fused_candidates.sort(
            key=lambda item: (item.fused_score, item.dense_score, item.sparse_score, item.chunk.id),
            reverse=True,
        )

        filtered_candidates = [
            candidate
            for candidate in fused_candidates
            if candidate.dense_score >= self.settings.min_dense_similarity
        ]

        retrieved_chunks = [
            RetrievedChunk(
                id=candidate.chunk.id,
                source=candidate.chunk.source,
                text=candidate.chunk.text,
                similarityScore=round(candidate.dense_score, 4),
                rank=index + 1,
            )
            for index, candidate in enumerate(filtered_candidates[:limit])
        ]

        return RetrievalResult(
            retrieved_chunks=retrieved_chunks,
            candidates=filtered_candidates[:limit],
        )

    def _dense_search(self, query: str) -> tuple[np.ndarray, np.ndarray]:
        vector = self.embed_query_fn(query)
        scores, indices = self.dense_index.search(vector, self.settings.dense_candidates)
        return scores[0], indices[0]

    def _sparse_search(self, query: str) -> tuple[np.ndarray, np.ndarray]:
        query_vector = self.tfidf_vectorizer.transform([query])
        scores = (query_vector @ self.tfidf_matrix.T).toarray()[0]
        if not scores.size:
            return np.array([], dtype=float), np.array([], dtype=int)

        top_count = min(self.settings.sparse_candidates, scores.shape[0])
        top_indices = np.argpartition(scores, -top_count)[-top_count:]
        sorted_indices = top_indices[np.argsort(scores[top_indices])[::-1]]
        return scores[sorted_indices], sorted_indices

    def _feedback_boosts(self, query: str, candidate_ids: set[str]) -> dict[str, float]:
        if self.feedback_store is None:
            return {}
        return self.feedback_store.score_boosts(
            query=query,
            candidate_chunk_ids=candidate_ids,
            scale=self.settings.feedback_boost_scale,
        )
