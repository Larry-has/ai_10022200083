from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


load_dotenv()


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
STORE_DIR = BASE_DIR / "store"

CHUNKS_PATH = PROCESSED_DATA_DIR / "chunks.jsonl"
FAISS_INDEX_PATH = STORE_DIR / "faiss.index"
EMBEDDINGS_PATH = STORE_DIR / "chunk_embeddings.npy"
TFIDF_MATRIX_PATH = STORE_DIR / "tfidf_matrix.npz"
TFIDF_VECTORIZER_PATH = STORE_DIR / "tfidf_vectorizer.pkl"
MANIFEST_PATH = STORE_DIR / "manifest.json"
FEEDBACK_LOG_PATH = STORE_DIR / "feedback.jsonl"

DEFAULT_CSV_FILE = "Ghana_Election_Result.csv"
DEFAULT_PDF_FILE = "2025-Budget-Statement-and-Economic-Policy_v4.pdf"


def _int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    return int(value)


def _float_env(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default
    return float(value)


@dataclass(frozen=True)
class Settings:
    csv_filename: str = field(default_factory=lambda: os.getenv("RAG_CSV_FILENAME", DEFAULT_CSV_FILE))
    pdf_filename: str = field(default_factory=lambda: os.getenv("RAG_PDF_FILENAME", DEFAULT_PDF_FILE))
    chunk_size: int = field(default_factory=lambda: _int_env("RAG_CHUNK_SIZE", 800))
    chunk_overlap: int = field(default_factory=lambda: _int_env("RAG_CHUNK_OVERLAP", 120))
    top_k: int = field(default_factory=lambda: _int_env("RAG_TOP_K", 5))
    dense_weight: float = field(default_factory=lambda: _float_env("RAG_DENSE_WEIGHT", 0.7))
    sparse_weight: float = field(default_factory=lambda: _float_env("RAG_SPARSE_WEIGHT", 0.3))
    dense_candidates: int = field(default_factory=lambda: _int_env("RAG_DENSE_CANDIDATES", 16))
    sparse_candidates: int = field(default_factory=lambda: _int_env("RAG_SPARSE_CANDIDATES", 16))
    min_dense_similarity: float = field(default_factory=lambda: _float_env("RAG_MIN_DENSE_SIMILARITY", 0.2))
    max_context_chars: int = field(default_factory=lambda: _int_env("RAG_MAX_CONTEXT_CHARS", 3600))
    prompt_mode: str = field(default_factory=lambda: os.getenv("RAG_PROMPT_MODE", "grounded_v2"))
    feedback_boost_scale: float = field(default_factory=lambda: _float_env("RAG_FEEDBACK_BOOST_SCALE", 0.15))
    embedding_model_name: str = field(
        default_factory=lambda: os.getenv(
            "RAG_EMBEDDING_MODEL",
            "sentence-transformers/all-MiniLM-L6-v2",
        )
    )
    huggingface_model: str = field(
        default_factory=lambda: os.getenv("HUGGINGFACE_MODEL", "meta-llama/Llama-3.1-8B-Instruct")
    )
    huggingface_api_key: Optional[str] = field(
        default_factory=lambda: (
            os.getenv("HF_TOKEN")
            or os.getenv("HUGGINGFACEHUB_API_TOKEN")
            or os.getenv("HUGGINGFACE_API_KEY")
        )
    )
    request_log_limit: int = field(default_factory=lambda: _int_env("RAG_REQUEST_LOG_LIMIT", 50))

    @property
    def csv_path(self) -> Path:
        return RAW_DATA_DIR / self.csv_filename

    @property
    def pdf_path(self) -> Path:
        return RAW_DATA_DIR / self.pdf_filename


def get_settings() -> Settings:
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    STORE_DIR.mkdir(parents=True, exist_ok=True)
    return Settings()
