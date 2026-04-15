from __future__ import annotations

import json
import pickle
from typing import Optional

import faiss
import numpy as np
from huggingface_hub import InferenceClient
from scipy import sparse
from sklearn.feature_extraction.text import TfidfVectorizer

try:
    from .config import (
        EMBEDDINGS_PATH,
        FAISS_INDEX_PATH,
        MANIFEST_PATH,
        TFIDF_MATRIX_PATH,
        TFIDF_VECTORIZER_PATH,
        Settings,
    )
    from .schemas import ChunkRecord, IndexManifest
except ImportError:  # pragma: no cover
    from config import (
        EMBEDDINGS_PATH,
        FAISS_INDEX_PATH,
        MANIFEST_PATH,
        TFIDF_MATRIX_PATH,
        TFIDF_VECTORIZER_PATH,
        Settings,
    )
    from schemas import ChunkRecord, IndexManifest


class EmbeddingStore:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._client: Optional[InferenceClient] = None

    @property
    def client(self) -> InferenceClient:
        if self._client is None:
            if not self.settings.huggingface_api_key:
                raise RuntimeError(
                    "HF_TOKEN (or HUGGINGFACEHUB_API_TOKEN) is required for embedding generation."
                )
            self._client = InferenceClient(api_key=self.settings.huggingface_api_key)
        return self._client

    def _normalize(self, vectors: np.ndarray) -> np.ndarray:
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return (vectors / norms).astype("float32")

    def embed_texts(self, texts: list[str]) -> np.ndarray:
        vectors: list[np.ndarray] = []
        for text in texts:
            embedding = self.client.feature_extraction(
                text=text,
                model=self.settings.embedding_model_name,
            )
            vectors.append(np.asarray(embedding, dtype="float32"))
        stacked = np.vstack(vectors)
        return self._normalize(stacked)

    def embed_query(self, query: str) -> np.ndarray:
        vector = self.embed_texts([query])[0]
        return vector.reshape(1, -1)


def build_tfidf_matrix(chunks: list[ChunkRecord]) -> tuple[TfidfVectorizer, sparse.csr_matrix]:
    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform(chunk.text for chunk in chunks)
    return vectorizer, matrix


def build_faiss_index(embeddings: np.ndarray) -> faiss.IndexFlatIP:
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)
    return index


def save_index_artifacts(
    *,
    settings: Settings,
    chunks: list[ChunkRecord],
    embeddings: np.ndarray,
    faiss_index: faiss.IndexFlatIP,
    tfidf_vectorizer: TfidfVectorizer,
    tfidf_matrix: sparse.csr_matrix,
) -> None:
    np.save(EMBEDDINGS_PATH, embeddings)
    faiss.write_index(faiss_index, str(FAISS_INDEX_PATH))
    sparse.save_npz(TFIDF_MATRIX_PATH, tfidf_matrix)

    with TFIDF_VECTORIZER_PATH.open("wb") as handle:
        pickle.dump(tfidf_vectorizer, handle)

    manifest = IndexManifest(
        embedding_model_name=settings.embedding_model_name,
        chunk_count=len(chunks),
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )
    MANIFEST_PATH.write_text(manifest.model_dump_json(indent=2), encoding="utf-8")


def load_index_artifacts() -> tuple[np.ndarray, faiss.IndexFlatIP, TfidfVectorizer, sparse.csr_matrix]:
    embeddings = np.load(EMBEDDINGS_PATH)
    faiss_index = faiss.read_index(str(FAISS_INDEX_PATH))
    tfidf_matrix = sparse.load_npz(TFIDF_MATRIX_PATH)

    with TFIDF_VECTORIZER_PATH.open("rb") as handle:
        tfidf_vectorizer = pickle.load(handle)

    return embeddings, faiss_index, tfidf_vectorizer, tfidf_matrix


def load_manifest() -> IndexManifest:
    return IndexManifest.model_validate(json.loads(MANIFEST_PATH.read_text(encoding="utf-8")))
