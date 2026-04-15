from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class ChunkRecord(BaseModel):
    id: str
    source: str
    text: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class RetrievedChunk(BaseModel):
    id: str
    source: str
    text: str
    similarityScore: float
    rank: int


class PipelineLog(BaseModel):
    step: str
    timestamp: str
    detail: Optional[str] = None


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=5000)


class RAGResponse(BaseModel):
    answer: str
    chunks: list[RetrievedChunk]
    finalPrompt: str
    logs: list[PipelineLog]


class RetrievalCandidate(BaseModel):
    chunk: ChunkRecord
    dense_score: float
    sparse_score: float
    feedback_score: float = 0.0
    fused_score: float


class IndexManifest(BaseModel):
    embedding_model_name: str
    chunk_count: int
    chunk_size: int
    chunk_overlap: int


class FeedbackRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=5000)
    chunk_ids: list[str] = Field(..., min_length=1)
    helpful: bool
    notes: Optional[str] = Field(default=None, max_length=1000)


class FeedbackResponse(BaseModel):
    status: str
    recorded: int
