from __future__ import annotations

import json
import re
from collections import deque
from datetime import datetime, timezone
from threading import Lock
from typing import Optional

from huggingface_hub import InferenceClient

try:
    from .config import FEEDBACK_LOG_PATH, get_settings
    from .embeddings import (
        EmbeddingStore,
        build_faiss_index,
        build_tfidf_matrix,
        load_index_artifacts,
        load_manifest,
        save_index_artifacts,
    )
    from .feedback import FeedbackStore
    from .ingestion import ingest_documents, load_chunks
    from .schemas import FeedbackRequest, FeedbackResponse, PipelineLog, RAGResponse, RetrievedChunk
    from .prompt import build_prompt
    from .retrieval import HybridRetriever
except ImportError:  # pragma: no cover
    from config import FEEDBACK_LOG_PATH, get_settings
    from embeddings import (
        EmbeddingStore,
        build_faiss_index,
        build_tfidf_matrix,
        load_index_artifacts,
        load_manifest,
        save_index_artifacts,
    )
    from feedback import FeedbackStore
    from ingestion import ingest_documents, load_chunks
    from schemas import FeedbackRequest, FeedbackResponse, PipelineLog, RAGResponse, RetrievedChunk
    from prompt import build_prompt
    from retrieval import HybridRetriever


CONTEXT_CITATION_PATTERN = re.compile(
    r"(?i)(\[\s*context\s*(\d+)\s*\]|\(\s*context\s*(\d+)\s*\))"
)


def _normalize_context_citations(answer: str, selected_chunks: list[RetrievedChunk]) -> str:
    rank_to_source = {chunk.rank: chunk.source for chunk in selected_chunks}

    def _replace(match: re.Match[str]) -> str:
        rank_text = match.group(2) or match.group(3)
        if rank_text is None:
            return match.group(0)
        rank = int(rank_text)
        source = rank_to_source.get(rank)
        if source is None:
            return match.group(0)
        return f"[Source: {source}]"

    normalized = CONTEXT_CITATION_PATTERN.sub(_replace, answer)
    return normalized


class RAGPipeline:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.embedding_store = EmbeddingStore(self.settings)
        self.feedback_store = FeedbackStore(FEEDBACK_LOG_PATH)
        self.recent_logs: deque[list[PipelineLog]] = deque(
            maxlen=self.settings.request_log_limit
        )
        self._retriever: Optional[HybridRetriever] = None
        self._chunks = []
        self._lock = Lock()

    def initialize(self) -> None:
        with self._lock:
            if self._retriever is not None:
                return

            if self._artifacts_exist():
                manifest = load_manifest()
                if (
                    manifest.embedding_model_name != self.settings.embedding_model_name
                    or manifest.chunk_size != self.settings.chunk_size
                    or manifest.chunk_overlap != self.settings.chunk_overlap
                ):
                    self._build_artifacts()
                else:
                    self._load_artifacts()
            else:
                self._build_artifacts()

    def _artifacts_exist(self) -> bool:
        required_paths = [
            self.settings.csv_path,
            self.settings.pdf_path,
        ]
        for path in required_paths:
            if not path.exists():
                raise FileNotFoundError(f"Required data file is missing: {path}")

        try:
            from .config import (
                CHUNKS_PATH,
                EMBEDDINGS_PATH,
                FAISS_INDEX_PATH,
                MANIFEST_PATH,
                TFIDF_MATRIX_PATH,
                TFIDF_VECTORIZER_PATH,
            )
        except ImportError:  # pragma: no cover
            from config import (
                CHUNKS_PATH,
                EMBEDDINGS_PATH,
                FAISS_INDEX_PATH,
                MANIFEST_PATH,
                TFIDF_MATRIX_PATH,
                TFIDF_VECTORIZER_PATH,
            )

        return all(
            path.exists()
            for path in [
                CHUNKS_PATH,
                EMBEDDINGS_PATH,
                FAISS_INDEX_PATH,
                TFIDF_MATRIX_PATH,
                TFIDF_VECTORIZER_PATH,
                MANIFEST_PATH,
            ]
        )

    def _build_artifacts(self) -> None:
        self._chunks = ingest_documents(self.settings)
        embeddings = self.embedding_store.embed_texts([chunk.text for chunk in self._chunks])
        tfidf_vectorizer, tfidf_matrix = build_tfidf_matrix(self._chunks)
        dense_index = build_faiss_index(embeddings)
        save_index_artifacts(
            settings=self.settings,
            chunks=self._chunks,
            embeddings=embeddings,
            faiss_index=dense_index,
            tfidf_vectorizer=tfidf_vectorizer,
            tfidf_matrix=tfidf_matrix,
        )
        self._retriever = HybridRetriever(
            settings=self.settings,
            chunks=self._chunks,
            dense_index=dense_index,
            tfidf_vectorizer=tfidf_vectorizer,
            tfidf_matrix=tfidf_matrix,
            embed_query_fn=self.embedding_store.embed_query,
            feedback_store=self.feedback_store,
        )

    def _load_artifacts(self) -> None:
        self._chunks = load_chunks()
        _, dense_index, tfidf_vectorizer, tfidf_matrix = load_index_artifacts()
        self._retriever = HybridRetriever(
            settings=self.settings,
            chunks=self._chunks,
            dense_index=dense_index,
            tfidf_vectorizer=tfidf_vectorizer,
            tfidf_matrix=tfidf_matrix,
            embed_query_fn=self.embedding_store.embed_query,
            feedback_store=self.feedback_store,
        )

    def chat(self, query: str) -> RAGResponse:
        self.initialize()
        assert self._retriever is not None

        logs: list[PipelineLog] = []
        self._log(logs, "query_received", f'Query="{query}"')

        retrieval = self._retriever.retrieve(query, top_k=self.settings.top_k)
        retrieved_chunks = retrieval.retrieved_chunks

        self._log(
            logs,
            "retrieval_completed",
            json.dumps(
                [
                    {
                        "rank": item.rank,
                        "source": item.source,
                        "score": item.similarityScore,
                    }
                    for item in retrieved_chunks
                ]
            ),
        )
        self._log(
            logs,
            "retrieval_scores",
            json.dumps(
                [
                    {
                        "chunk_id": candidate.chunk.id,
                        "dense": round(candidate.dense_score, 4),
                        "sparse": round(candidate.sparse_score, 4),
                        "feedback": round(candidate.feedback_score, 4),
                        "fused": round(candidate.fused_score, 4),
                    }
                    for candidate in retrieval.candidates
                ]
            ),
        )

        if not retrieved_chunks:
            final_prompt = (
                "No prompt was sent to the LLM because retrieval confidence was below the "
                "configured dense similarity threshold."
            )
            self._log(
                logs,
                "retrieval_fallback",
                (
                    "No chunks satisfied the dense similarity threshold; returning fallback "
                    "response without LLM generation."
                ),
            )
            response = RAGResponse(
                answer=(
                    "I could not find sufficiently relevant evidence in the ingested election "
                    "results and 2025 budget documents to answer that confidently."
                ),
                chunks=[],
                finalPrompt=final_prompt,
                logs=logs,
            )
            self.recent_logs.append(response.logs)
            return response

        prompt, selected_chunks = build_prompt(
            query=query,
            chunks=retrieved_chunks,
            settings=self.settings,
        )
        self._log(
            logs,
            "context_selected",
            json.dumps(
                [
                    {
                        "rank": chunk.rank,
                        "source": chunk.source,
                        "score": chunk.similarityScore,
                    }
                    for chunk in selected_chunks
                ]
            ),
        )
        self._log(
            logs,
            "prompt_constructed",
            f"Prompt stored in finalPrompt field ({len(prompt)} chars)",
        )

        answer = self._generate_response(
            prompt,
            system_message=(
                "You are a careful retrieval-augmented assistant. "
                "You must answer using only the supplied context."
            ),
        )
        normalized_answer = _normalize_context_citations(answer, selected_chunks)
        if normalized_answer != answer:
            self._log(logs, "citation_normalized", "Converted [Context n] style citations to [Source: ...].")
            answer = normalized_answer
        self._log(logs, "response_generated", "Hugging Face response generated successfully")

        response = RAGResponse(
            answer=answer,
            chunks=retrieved_chunks,
            finalPrompt=prompt,
            logs=logs,
        )
        self.recent_logs.append(response.logs)
        return response

    def answer_from_prompt(self, prompt: str) -> str:
        return self._generate_response(
            prompt,
            system_message=(
                "You are a careful retrieval-augmented assistant. "
                "You must answer using only the supplied context."
            ),
        )

    def pure_llm_answer(self, query: str) -> str:
        prompt = (
            "Answer the question directly using your general knowledge. "
            "Do not ask for extra context.\n\n"
            f"Question: {query}"
        )
        return self._generate_response(
            prompt,
            system_message="You are a general assistant. Answer clearly and directly.",
        )

    def get_recent_logs(self) -> list[PipelineLog]:
        flattened: list[PipelineLog] = []
        for request_logs in self.recent_logs:
            flattened.extend(request_logs)
        return flattened

    def submit_feedback(self, payload: FeedbackRequest) -> FeedbackResponse:
        self.initialize()
        recorded = self.feedback_store.add_feedback(
            query=payload.query.strip(),
            chunk_ids=payload.chunk_ids,
            helpful=payload.helpful,
            notes=payload.notes,
        )
        return FeedbackResponse(status="ok", recorded=recorded)

    def _generate_response(self, prompt: str, *, system_message: str) -> str:
        if not self.settings.huggingface_api_key:
            raise RuntimeError(
                "HF_TOKEN (or HUGGINGFACEHUB_API_TOKEN) is required for response generation. "
                "Set it before calling /api/chat."
            )

        client = InferenceClient(api_key=self.settings.huggingface_api_key)
        completion = client.chat_completion(
            model=self.settings.huggingface_model,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": system_message,
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=500,
        )
        return completion.choices[0].message.content or ""

    def _log(self, logs: list[PipelineLog], step: str, detail: str) -> None:
        logs.append(
            PipelineLog(
                step=step,
                timestamp=datetime.now(timezone.utc).isoformat(),
                detail=detail,
            )
        )


_PIPELINE: Optional[RAGPipeline] = None


def get_pipeline() -> RAGPipeline:
    global _PIPELINE
    if _PIPELINE is None:
        _PIPELINE = RAGPipeline()
    return _PIPELINE
