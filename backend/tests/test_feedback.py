from pathlib import Path

from backend.feedback import FeedbackStore


def test_feedback_store_records_and_scores(tmp_path: Path):
    store = FeedbackStore(tmp_path / "feedback.jsonl")
    store.add_feedback(
        query="What is expenditure in the 2025 budget?",
        chunk_ids=["chunk-budget"],
        helpful=True,
        notes=None,
    )
    store.add_feedback(
        query="What is expenditure in the 2025 budget?",
        chunk_ids=["chunk-election"],
        helpful=False,
        notes=None,
    )

    boosts = store.score_boosts(
        query="Tell me expenditure in the budget",
        candidate_chunk_ids={"chunk-budget", "chunk-election"},
        scale=0.2,
    )

    assert boosts["chunk-budget"] > 0
    assert boosts["chunk-election"] < 0
