from fastapi.testclient import TestClient

from backend.api import app
from backend.schemas import FeedbackResponse, PipelineLog, RAGResponse, RetrievedChunk


class StubPipeline:
    def initialize(self) -> None:
        return None

    def chat(self, query: str) -> RAGResponse:
        return RAGResponse(
            answer=f"Echo: {query}",
            chunks=[
                RetrievedChunk(
                    id="chunk-1",
                    source="source.pdf",
                    text="chunk text",
                    similarityScore=0.91,
                    rank=1,
                )
            ],
            finalPrompt="prompt",
            logs=[
                PipelineLog(
                    step="query_received",
                    timestamp="2026-04-15T00:00:00+00:00",
                    detail='Query="hello"',
                )
            ],
        )

    def get_recent_logs(self) -> list[PipelineLog]:
        return [
            PipelineLog(
                step="query_received",
                timestamp="2026-04-15T00:00:00+00:00",
                detail='Query="hello"',
            )
        ]

    def submit_feedback(self, _payload) -> FeedbackResponse:
        return FeedbackResponse(status="ok", recorded=2)


def test_chat_endpoint_returns_frontend_contract(monkeypatch):
    monkeypatch.setattr("backend.api.get_pipeline", lambda: StubPipeline())

    with TestClient(app) as client:
        response = client.post("/api/chat", json={"query": "hello"})

    assert response.status_code == 200
    body = response.json()
    assert body["answer"] == "Echo: hello"
    assert body["chunks"][0]["similarityScore"] == 0.91
    assert body["finalPrompt"] == "prompt"
    assert body["logs"][0]["step"] == "query_received"


def test_logs_endpoint_returns_pipeline_logs(monkeypatch):
    monkeypatch.setattr("backend.api.get_pipeline", lambda: StubPipeline())

    with TestClient(app) as client:
        response = client.get("/api/logs")

    assert response.status_code == 200
    assert response.json()[0]["step"] == "query_received"


def test_feedback_endpoint_records_feedback(monkeypatch):
    monkeypatch.setattr("backend.api.get_pipeline", lambda: StubPipeline())

    with TestClient(app) as client:
        response = client.post(
            "/api/feedback",
            json={
                "query": "What did Mahama score in Ahafo?",
                "chunk_ids": ["c1", "c2"],
                "helpful": True,
                "notes": "Good chunks",
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["recorded"] == 2
