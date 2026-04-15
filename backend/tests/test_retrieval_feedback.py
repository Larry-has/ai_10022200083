import faiss
import numpy as np
from scipy import sparse
from sklearn.feature_extraction.text import TfidfVectorizer

from backend.config import get_settings
from backend.retrieval import HybridRetriever
from backend.schemas import ChunkRecord


class StubFeedbackStore:
    def score_boosts(self, *, query: str, candidate_chunk_ids: set[str], scale: float) -> dict[str, float]:
        del query, scale
        boosts = {}
        if "c2" in candidate_chunk_ids:
            boosts["c2"] = 1.0
        return boosts


def test_feedback_boost_can_reorder_results():
    settings = get_settings()
    chunks = [
        ChunkRecord(id="c1", source="a", text="alpha budget spending", metadata={}),
        ChunkRecord(id="c2", source="b", text="beta budget spending", metadata={}),
    ]

    embeddings = np.array([[1.0, 0.0], [0.98, 0.2]], dtype="float32")
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
        feedback_store=StubFeedbackStore(),
    )

    result = retriever.retrieve("budget", top_k=2)
    assert result.retrieved_chunks[0].id == "c2"
