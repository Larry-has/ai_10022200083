import faiss
import numpy as np
from scipy import sparse
from sklearn.feature_extraction.text import TfidfVectorizer

from backend.config import get_settings
from backend.retrieval import HybridRetriever
from backend.schemas import ChunkRecord


def test_hybrid_retrieval_returns_ranked_chunks():
    settings = get_settings()
    chunks = [
        ChunkRecord(
            id="c1",
            source="election.csv",
            text="Candidate Nana Akufo Addo won votes in Ahafo Region",
            metadata={},
        ),
        ChunkRecord(
            id="c2",
            source="budget.pdf",
            text="Government expenditure for 2025 is projected in the budget statement",
            metadata={},
        ),
    ]

    embeddings = np.array(
        [
            [1.0, 0.0],
            [0.0, 1.0],
        ],
        dtype="float32",
    )
    faiss.normalize_L2(embeddings)
    index = faiss.IndexFlatIP(2)
    index.add(embeddings)

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(chunk.text for chunk in chunks)

    def embed_query(query: str) -> np.ndarray:
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
    )

    result = retriever.retrieve("Akufo Addo votes", top_k=2)

    assert result.retrieved_chunks
    assert result.retrieved_chunks[0].id == "c1"
    assert result.retrieved_chunks[0].rank == 1
