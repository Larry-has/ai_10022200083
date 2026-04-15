from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

try:
    from .pipeline import get_pipeline
    from .schemas import (
        ChatRequest,
        FeedbackRequest,
        FeedbackResponse,
        PipelineLog,
        RAGResponse,
    )
except ImportError:  # pragma: no cover
    from pipeline import get_pipeline
    from schemas import (
        ChatRequest,
        FeedbackRequest,
        FeedbackResponse,
        PipelineLog,
        RAGResponse,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_pipeline().initialize()
    yield


app = FastAPI(
    title="Academic City Custom RAG Backend",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/chat", response_model=RAGResponse)
async def chat(request: ChatRequest) -> RAGResponse:
    try:
        return get_pipeline().chat(request.query.strip())
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - defensive API guard
        raise HTTPException(status_code=500, detail=f"Unexpected backend error: {exc}") from exc


@app.get("/api/logs", response_model=list[PipelineLog])
async def logs() -> list[PipelineLog]:
    return get_pipeline().get_recent_logs()


@app.post("/api/feedback", response_model=FeedbackResponse)
async def feedback(request: FeedbackRequest) -> FeedbackResponse:
    try:
        return get_pipeline().submit_feedback(request)
    except Exception as exc:  # pragma: no cover - defensive API guard
        raise HTTPException(status_code=500, detail=f"Unexpected backend error: {exc}") from exc
